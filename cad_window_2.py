import os
import sys
import math
import copy
import json
import csv
import re
import zipfile
import xml.etree.ElementTree as ET

import ezdxf
import ezdxf.bbox as dxf_bbox
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Matrix44
from ezdxf.addons.importer import Importer 

from PySide6.QtWidgets import (
    QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView, 
    QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem, QInputDialog, QFileDialog,
    QGridLayout, QGraphicsTextItem, QGraphicsSimpleTextItem, QGraphicsItem
)
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath, QPainter, QGuiApplication


try:
    from graphics_items import SelectableCircle, SelectableLine, SelectableArc
    from graphics_view import AdvancedGraphicsView
    from history_manager import HistoryManager
except ImportError:
    AdvancedGraphicsView = QGraphicsView
    class HistoryManager:
        def __init__(self, p): self.p = p; self.undo_stack=[1]; self.redo_stack=[]
        def save_state(self): pass
        def clear_redo(self): pass
        def undo(self): return True
        def redo(self): return True


def patch_ezdxf_entities():
    from ezdxf.entities import Line, Circle, Arc
    
    Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
    Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
    Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
    Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

    Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
    Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
    Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
    Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

    Arc.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
    Arc.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
    Arc.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
    Arc.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

patch_ezdxf_entities()

# --- ГІБРИДНИЙ ПАРСЕР ЗНАЧЕНЬ ---
def parse_factor(text):
    text = str(text).strip().upper()
    
  
    if '(' in text:
        text = text.split('(')[0].strip()
        
    if not text:
        return 0.0

    if text.endswith("%"):
        try: return float(text[:-1].replace(',', '.')) / 100.0
        except: return 0.0

    if text.startswith("Δ/") or text.startswith("D/"):
        try:
            div = float(text[2:].replace(',', '.'))
            return 0.0 if div == 0 else 1.0 / div
        except: return 0.0

    if "/" in text: # наприклад 1/3
        try:
            parts = text.split("/")
            return float(parts[0]) / float(parts[1])
        except: return 0.0

    try:
        val = float(text.replace(',', '.'))
        if val > 1.0: # Якщо користувач просто написав 50, вважаємо це 50%
            return val / 100.0
        return val
    except:
        return 0.0

def format_factor(val):
    """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
    if abs(val - 0.0) < 0.001: return "0% (Фіксовано / Край)"
    if abs(val - 0.333) < 0.01: return "33.3% (1/3)"
    if abs(val - 0.5) < 0.001: return "50% (Центр / Δ/2)"
    if abs(val - 0.667) < 0.01: return "66.7% (2/3)"
    if abs(val - 1.0) < 0.001: return "100% (Протилежний край / Δ/1)"
    return f"{val*100:g}%"


class DraggableDoorTextItem(QGraphicsTextItem):
    def __init__(self, text, owner):
        super().__init__(text)
        self.owner = owner
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.owner.on_door_text_item_moved(self)


class DraggableDoorTextBoxItem(QGraphicsRectItem):
    def __init__(self, x, y, width, height, owner, handle=None):
        super().__init__(x, y, width, height)
        self.owner = owner
        self.handle = handle
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if self.handle:
            self.owner.selected_handles = {self.handle}
            self.owner.sync_list_from_handles()
        self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.owner.on_door_text_box_moved(self)


# --- МОДУЛЬ ПАРАМЕТРИЧНОГО РУХУ ---
class ParametricEngine:
    @staticmethod
    def get_transform(delta_w, delta_h, group):
        val_x = delta_w if "W" in group.get("link_x", "W") else delta_h
        val_y = delta_h if "H" in group.get("link_y", "H") else delta_w

        shift_x = val_x * group.get("k_w", 0.0)
        growth_x = val_x * group.get("growth_p_w", 0.0)
        
        shift_y = val_y * group.get("k_h", 0.0)
        growth_y = val_y * group.get("growth_p_h", 0.0)
            
        return (shift_x, shift_y, 0), (growth_x, growth_y, 0)


class MiniCAD(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAD Двері: Топологічний Параметризатор")
        self.setGeometry(100, 100, 1600, 950)

        self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
        self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
        self.current_theme = "Темна"

        self.selected_handles = set()
        self.overlay_items = {}
        self.original_geometries = {}
        self.is_loading_history = False

        self.parametric_groups = [] 
        self.project_meta = {
            "source_width": None,
            "source_height": None,
            "target_width": None,
            "target_height": None,
            "keep_blocks": [],
            "delete_blocks": [],
            "door_opening": "left",
            "door_text": {
                "enabled": False,
                "text": "",
                "x": 0.0,
                "y": 0.0,
                "height": 30.0,
                "width_factor": 120.0,
                "rotation": 0.0,
                "font": "STANDARD",
                "handle": None
            }
        }
        self.block_keep_state = {}

        self.zones_undo_stack = []
        self.zones_redo_stack = []
        self.global_recalc_undo_stack = []
        self.global_recalc_redo_stack = []

        self.coord_tooltip_item = None
        self.coord_snap_marker = None

        self.load_doc_safely()
        self.load_project_config()
        
        self.history = HistoryManager(self.dxf_path)
        self.history.save_state()
        self.save_zones_history_state()

        self.init_ui()
        self.update_dimension_inputs_from_meta()
        self.set_interface_theme(self.current_theme)
        self.save_original_geometries()
        self.update_viewer()
        self.load_entities_into_list()
        self.load_groups_into_list()
        self.scan_project_folder_for_dxf()

    def load_doc_safely(self):
        if os.path.exists(self.dxf_path):
            try:
                self.doc = ezdxf.readfile(self.dxf_path)
            except Exception as e:
                print(f"Помилка читання файлу: {e}")
                self.doc = ezdxf.new()
                self.doc.saveas(self.dxf_path)
        else:
            dxf_files = [f for f in os.listdir(self.project_dir) if f.lower().endswith('.dxf')]
            if dxf_files:
                self.dxf_path = os.path.join(self.project_dir, dxf_files[0])
                self.doc = ezdxf.readfile(self.dxf_path)
            else:
                self.doc = ezdxf.new()
                self.doc.saveas(self.dxf_path)

    def get_project_config_path(self):
        base_path = os.path.splitext(self.dxf_path)[0]
        return f"{base_path}_config.json"

    def default_project_meta(self):
        return {
            "source_width": None,
            "source_height": None,
            "target_width": None,
            "target_height": None,
            "keep_blocks": [],
            "delete_blocks": [],
            "door_opening": "left",
            "door_text": self.default_text_settings()
        }

    def default_text_settings(self):
        return {
            "enabled": False,
            "text": "",
            "x": 0.0,
            "y": 0.0,
            "height": 30.0,
            "width_factor": 120.0,
            "rotation": 0.0,
            "font": "STANDARD",
            "handle": None
        }

    def get_group_key(self, group):
        if not group.get("uid"):
            handles_key = ",".join(sorted(str(h) for h in group.get("handles", [])))
            group["uid"] = f"{group.get('name', 'group')}|{handles_key}"
        return group["uid"]

    def load_project_config(self):
        # Динамічно формуємо ім'я JSON-файлу на основі імені поточного DXF
        config_path = self.get_project_config_path()
        
        self.parametric_groups.clear()
        self.project_meta = self.default_project_meta()
        self.block_keep_state = {}
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    if isinstance(raw_data, dict):
                        self.project_meta.update(raw_data.get("meta", {}))
                        text_settings = self.default_text_settings()
                        text_settings.update(self.project_meta.get("door_text", {}))
                        self.project_meta["door_text"] = text_settings
                        data = raw_data.get("groups", [])
                    else:
                        data = raw_data
                    for g in data:
                        g["handles"] = set(g.get("handles", []))
                        self.get_group_key(g)
                        
                        # Міграція зі старих версій
                        if "k_x" in g:
                            g["k_w"] = g.pop("k_x")
                            g["k_h"] = g.pop("k_y")
                            g["growth_p_w"] = g.pop("growth_p_x")
                            g["growth_p_h"] = g.pop("growth_p_y")
                        else:
                            g["k_w"] = g.get("k_w", 0.0)
                            g["k_h"] = g.get("k_h", 0.0)
                            g["growth_p_w"] = g.get("growth_p_w", 0.0)
                            g["growth_p_h"] = g.get("growth_p_h", 0.0)

                        old_link_x = g.get("link_x", "W")
                        old_link_y = g.get("link_y", "H")
                        g["link_x"] = "X = W" if "W" in old_link_x or "Ширин" in old_link_x else "X = H"
                        g["link_y"] = "Y = H" if "H" in old_link_y or "Висот" in old_link_y else "Y = W"
                        
                        # Міграція старого напрямку на розділені осі X та Y
                        if "growth_direction" in g:
                            old_dir = g.pop("growth_direction")
                            g["growth_dir_x"] = "Вправо" if "Вправо" in old_dir else ("Вліво" if "Вліво" in old_dir else "Центр")
                            g["growth_dir_y"] = "Вгору" if "Вгору" in old_dir else ("Вниз" if "Вниз" in old_dir else "Центр")
                        else:
                            g["growth_dir_x"] = g.get("growth_dir_x", "Центр")
                            g["growth_dir_y"] = g.get("growth_dir_y", "Центр")

                    self.parametric_groups = data
            except Exception as e:
                print(f"Помилка завантаження конфігурації JSON: {e}")

        keep_names = self.project_meta.get("keep_blocks", [])
        delete_names = self.project_meta.get("delete_blocks", [])
        for group in self.parametric_groups:
            name = group.get("name", "")
            key = self.get_group_key(group)
            if keep_names:
                self.block_keep_state[key] = key in keep_names or name in keep_names
            elif delete_names:
                self.block_keep_state[key] = not (key in delete_names or name in delete_names)
            else:
                self.block_keep_state[key] = True

    def save_project_config(self):
        # Динамічно формуємо ім'я JSON-файлу на основі імені поточного DXF
        config_path = self.get_project_config_path()
        
        groups_data = []
        for g in self.parametric_groups:
            self.get_group_key(g)
            g_data = g.copy()
            g_data["handles"] = list(g["handles"])
            groups_data.append(g_data)
        self.project_meta["keep_blocks"] = [
            name for name, keep in self.block_keep_state.items() if keep
        ]
        self.project_meta["delete_blocks"] = [
            name for name, keep in self.block_keep_state.items() if not keep
        ]
        data = {"meta": self.project_meta, "groups": groups_data}
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Помилка збереження конфігурації JSON: {e}")

    def init_ui(self):
        main_widget = QWidget()
        self.central_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        folder_explorer_widget = QWidget()
        folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
        folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
        lbl_explorer_title = QLabel("📁 <b>Провідник DXF:</b>")
        lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
        folder_explorer_layout.addWidget(lbl_explorer_title)

        self.btn_open_file = QPushButton("📂 Відкрити файл...")
        self.btn_open_file.setStyleSheet("background-color: #37474f; color: white; font-weight: bold; padding: 4px;")
        self.btn_open_file.clicked.connect(self.open_dxf_from_dialog)
        folder_explorer_layout.addWidget(self.btn_open_file)
        
        self.file_explorer_list = QListWidget()
        self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
        folder_explorer_layout.addWidget(self.file_explorer_list)
        self.central_layout.addWidget(folder_explorer_widget, stretch=1)

        self.scene = QGraphicsScene()
        self.view = AdvancedGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMouseTracking(True)  
        self.scene.mouseMoveEvent = self.on_scene_mouse_move
        self.central_layout.addWidget(self.view, stretch=4)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        control_panel = QWidget()
        control_panel_layout = QVBoxLayout(control_panel)
        control_panel_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_area.setWidget(control_panel)
        self.central_layout.addWidget(self.scroll_area, stretch=4)

        inspector_group = QGroupBox("🔍 Інженерні режими полотна")
        inspector_box = QVBoxLayout()
        self.chk_enable_inspector = QCheckBox("🛰️ Ввімкнути інтерактивний трекер точок")
        self.chk_enable_inspector.setStyleSheet("color: #ff9800; font-weight: bold;")
        self.chk_enable_inspector.clicked.connect(self.toggle_inspector_mode)
        inspector_box.addWidget(self.chk_enable_inspector)
        
        self.btn_snap_zero = QPushButton("↙️ Притиснути фігуру до (0, 0)")
        self.btn_snap_zero.setStyleSheet("background-color: #00897b; color: white; font-weight: bold; padding: 6px;")
        self.btn_snap_zero.clicked.connect(self.snap_to_zero)
        inspector_box.addWidget(self.btn_snap_zero)
        
        inspector_group.setLayout(inspector_box)
        control_panel_layout.addWidget(inspector_group)

        self.transform_group = QGroupBox("🔄 Трансформація виділених елементів (DXF)")
        self.transform_group.setStyleSheet("QGroupBox { border: 1px solid #d32f2f; }")
        transform_box = QVBoxLayout()
        
        rot_btn_layout = QHBoxLayout()
        self.btn_rot_90 = QPushButton("90°")
        self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
        rot_btn_layout.addWidget(self.btn_rot_90)
        
        self.btn_rot_180 = QPushButton("180°")
        self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
        rot_btn_layout.addWidget(self.btn_rot_180)
        
        self.btn_rot_270 = QPushButton("270°")
        self.btn_rot_270.clicked.connect(lambda: self.transform_selected_entities("ROT270"))
        rot_btn_layout.addWidget(self.btn_rot_270)
        transform_box.addLayout(rot_btn_layout)

        mirror_btn_layout = QHBoxLayout()
        self.btn_mirror_h = QPushButton("Дзеркало ↔ Ліво/право")
        self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
        mirror_btn_layout.addWidget(self.btn_mirror_h)

        self.btn_mirror_v = QPushButton("Дзеркало ↕ Верх/низ")
        self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
        mirror_btn_layout.addWidget(self.btn_mirror_v)
        transform_box.addLayout(mirror_btn_layout)

        self.transform_group.setLayout(transform_box)
        control_panel_layout.addWidget(self.transform_group)

        auto_scale_group = QGroupBox("🚀 Параметрична трансформація розмірів")
        auto_scale_box = QVBoxLayout()

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Ширина X:"))
        self.input_current_width = QLineEdit("1000")
        width_layout.addWidget(self.input_current_width)
        width_layout.addWidget(QLabel("➡️ Нова:"))
        self.input_target_width = QLineEdit("1050")
        width_layout.addWidget(self.input_target_width)
        auto_scale_box.addLayout(width_layout)

        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Висота Y:"))
        self.input_current_height = QLineEdit("2000")
        height_layout.addWidget(self.input_current_height)
        height_layout.addWidget(QLabel("➡️ Нова:"))
        self.input_target_height = QLineEdit("2080")
        height_layout.addWidget(self.input_target_height)
        auto_scale_box.addLayout(height_layout)

        self.lbl_status_calc = QLabel("Задайте нові розміри конструкції для автоматичного морфінгу.")
        self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
        auto_scale_box.addWidget(self.lbl_status_calc)

        self.btn_apply_auto_scale = QPushButton("⚡ Запустити глобальний перерахунок")
        self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
        self.btn_apply_auto_scale.clicked.connect(lambda: self.process_parametric_percentage_scale())
        auto_scale_box.addWidget(self.btn_apply_auto_scale)

        preview_buttons = QHBoxLayout()
        self.btn_preview_scale = QPushButton("Перегляд")
        self.btn_preview_scale.clicked.connect(self.preview_parametric_scale)
        preview_buttons.addWidget(self.btn_preview_scale)

        self.btn_restore_current = QPushButton("Повернути базу")
        self.btn_restore_current.clicked.connect(self.restore_current_dxf_from_disk)
        preview_buttons.addWidget(self.btn_restore_current)
        auto_scale_box.addLayout(preview_buttons)

        workflow_buttons = QHBoxLayout()
        self.btn_remember_source_size = QPushButton("Запам'ятати початкові")
        self.btn_remember_source_size.clicked.connect(self.remember_source_dimensions)
        workflow_buttons.addWidget(self.btn_remember_source_size)

        self.btn_import_params = QPushButton("Excel/CSV параметри")
        self.btn_import_params.clicked.connect(self.import_parameters_from_table)
        workflow_buttons.addWidget(self.btn_import_params)

        self.btn_order_wizard = QPushButton("Нове замовлення")
        self.btn_order_wizard.clicked.connect(self.quick_order_wizard)
        workflow_buttons.addWidget(self.btn_order_wizard)
        auto_scale_box.addLayout(workflow_buttons)

        self.btn_export_new_dxf = QPushButton("Створити новий DXF")
        self.btn_export_new_dxf.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;")
        self.btn_export_new_dxf.clicked.connect(self.export_new_dxf_with_dimensions)
        auto_scale_box.addWidget(self.btn_export_new_dxf)

        self.btn_batch_export = QPushButton("Пакет з Excel/CSV")
        self.btn_batch_export.clicked.connect(self.batch_export_from_table)
        auto_scale_box.addWidget(self.btn_batch_export)

        self.btn_find_min_size = QPushButton("Мінімум без накладання")
        self.btn_find_min_size.clicked.connect(self.find_minimum_safe_size)
        auto_scale_box.addWidget(self.btn_find_min_size)

        auto_scale_group.setLayout(auto_scale_box)
        control_panel_layout.addWidget(auto_scale_group)

        opening_group = QGroupBox("Відкривання")
        opening_box = QHBoxLayout()
        self.combo_door_opening = QComboBox()
        self.combo_door_opening.addItems(["Ліве", "Праве"])
        self.combo_door_opening.currentTextChanged.connect(self.on_door_opening_changed)
        opening_box.addWidget(self.combo_door_opening)
        self.btn_mirror_opening = QPushButton("Змінити L/R")
        self.btn_mirror_opening.clicked.connect(self.mirror_door_opening)
        opening_box.addWidget(self.btn_mirror_opening)
        opening_group.setLayout(opening_box)
        control_panel_layout.addWidget(opening_group)

        text_group = QGroupBox("Текст на дверях")
        text_box = QGridLayout()
        self.check_door_text_enabled = QCheckBox("Додати текст")
        self.check_door_text_enabled.stateChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.check_door_text_enabled, 0, 0, 1, 2)

        text_box.addWidget(QLabel("Текст:"), 1, 0)
        self.input_door_text = QLineEdit()
        self.input_door_text.textChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.input_door_text, 1, 1, 1, 3)

        text_box.addWidget(QLabel("X:"), 2, 0)
        self.input_text_x = QLineEdit("0")
        self.input_text_x.textChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.input_text_x, 2, 1)

        text_box.addWidget(QLabel("Y:"), 2, 2)
        self.input_text_y = QLineEdit("0")
        self.input_text_y.textChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.input_text_y, 2, 3)

        text_box.addWidget(QLabel("Висота:"), 3, 0)
        self.input_text_height = QLineEdit("30")
        self.input_text_height.textChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.input_text_height, 3, 1)

        text_box.addWidget(QLabel("Ширина рамки:"), 3, 2)
        self.input_text_width_factor = QLineEdit("120")
        self.input_text_width_factor.textChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.input_text_width_factor, 3, 3)

        text_box.addWidget(QLabel("Поворот:"), 4, 0)
        self.input_text_rotation = QLineEdit("0")
        self.input_text_rotation.textChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.input_text_rotation, 4, 1)

        text_box.addWidget(QLabel("Шрифт:"), 4, 2)
        self.combo_text_font = QComboBox()
        self.combo_text_font.setEditable(True)
        self.combo_text_font.addItems([
            "STANDARD", "Arial", "Arial Narrow", "Arial Black",
            "Calibri", "Calibri Light", "Cambria", "Candara",
            "Century Gothic", "Consolas", "Courier New",
            "Georgia", "Impact", "Segoe UI", "Tahoma",
            "Times New Roman", "Trebuchet MS", "Verdana",
            "Simplex", "Romans", "Isocp"
        ])
        self.combo_text_font.currentTextChanged.connect(self.on_text_settings_changed)
        text_box.addWidget(self.combo_text_font, 4, 3)

        self.btn_place_door_text = QPushButton("Показати/поставити блок")
        self.btn_place_door_text.clicked.connect(self.place_empty_door_text_block)
        text_box.addWidget(self.btn_place_door_text, 5, 0, 1, 4)

        self.btn_apply_door_text = QPushButton("Оновити текст")
        self.btn_apply_door_text.clicked.connect(self.apply_door_text_from_ui)
        text_box.addWidget(self.btn_apply_door_text, 6, 0, 1, 4)

        self.btn_remove_door_text = QPushButton("Прибрати текстовий блок")
        self.btn_remove_door_text.clicked.connect(self.remove_door_text_block)
        text_box.addWidget(self.btn_remove_door_text, 7, 0, 1, 4)

        align_text_buttons = QHBoxLayout()
        self.btn_align_text_width = QPushButton("Вирівняти по ширині")
        self.btn_align_text_width.clicked.connect(lambda: self.align_text_box_to_door("width"))
        align_text_buttons.addWidget(self.btn_align_text_width)
        self.btn_align_text_height = QPushButton("Вирівняти по висоті")
        self.btn_align_text_height.clicked.connect(lambda: self.align_text_box_to_door("height"))
        align_text_buttons.addWidget(self.btn_align_text_height)
        text_box.addLayout(align_text_buttons, 8, 0, 1, 4)
        text_group.setLayout(text_box)
        control_panel_layout.addWidget(text_group)
        self.sync_text_inputs_from_meta()
        self.sync_opening_inputs_from_meta()

        history_group = QGroupBox("Конструкторська історія")
        history_box = QHBoxLayout()
        self.btn_undo = QPushButton("Назад")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_redo = QPushButton("Вперед")
        self.btn_redo.clicked.connect(self.redo)
        history_box.addWidget(self.btn_undo)
        history_box.addWidget(self.btn_redo)
        history_group.setLayout(history_box)
        control_panel_layout.addWidget(history_group)

        group_constructor_group = QGroupBox("🛠️ Параметричні групи топології")
        group_box = QVBoxLayout()

        self.btn_create_group = QPushButton("🧩 Створити параметричну групу")
        self.btn_create_group.setStyleSheet("background-color: #673ab7; color: white; font-weight: bold;")
        self.btn_create_group.clicked.connect(self.create_parametric_group)
        group_box.addWidget(self.btn_create_group)

        self.btn_delete_from_dxf = QPushButton("🗑️ Видалити об'єкти з креслення (DXF)")
        self.btn_delete_from_dxf.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        self.btn_delete_from_dxf.clicked.connect(self.delete_entities_from_dxf)
        group_box.addWidget(self.btn_delete_from_dxf)

        self.btn_remove_selected = QPushButton("✂️ Виключити виділене з групи")
        self.btn_remove_selected.clicked.connect(self.remove_selected_from_group)
        group_box.addWidget(self.btn_remove_selected)

        self.btn_disband_group = QPushButton("💥 Розформувати вибрану групу")
        self.btn_disband_group.clicked.connect(self.disband_parametric_group)
        group_box.addWidget(self.btn_disband_group)

        group_box.addWidget(QLabel("<b>Параметричні групи деталей:</b>"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setFixedHeight(100)
        self.group_list_widget.itemSelectionChanged.connect(self.on_group_selection_changed)
        group_box.addWidget(self.group_list_widget)

        group_box.addWidget(QLabel("<b>Блоки для нового DXF (галочка = лишити):</b>"))
        self.block_filter_list = QListWidget()
        self.block_filter_list.setFixedHeight(95)
        self.block_filter_list.itemChanged.connect(self.on_block_keep_state_changed)
        group_box.addWidget(self.block_filter_list)

        # --- ГІБРИДНА СІТКА НАЛАШТУВАНЬ ГРУПИ (РОЗДІЛЕНІ ОСІ X та Y) ---
        group_box.addWidget(QLabel("<b>⚙️ Параметри трансформації:</b>"))
        
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(5)

        preset_items = [
            "0% (Фіксовано / Край)",
            "33.3% (1/3)",
            "50% (Центр / Δ/2)",
            "66.7% (2/3)",
            "100% (Протилежний край / Δ/1)",
            "✏️ Ввести вручну (напр. 15%)"
        ]

        # Рядок 1: Вісь X
        self.combo_link_x = QComboBox()
        self.combo_link_x.addItems(["X = W", "X = H"])
        grid.addWidget(self.combo_link_x, 0, 0)

        grid.addWidget(QLabel("Зсув:"), 0, 1)
        self.combo_k_w = QComboBox()
        self.combo_k_w.setEditable(True)
        self.combo_k_w.addItems(preset_items)
        grid.addWidget(self.combo_k_w, 0, 2)

        grid.addWidget(QLabel("Ріст:"), 0, 3)
        self.combo_growth_p_w = QComboBox()
        self.combo_growth_p_w.setEditable(True)
        self.combo_growth_p_w.addItems(preset_items)
        grid.addWidget(self.combo_growth_p_w, 0, 4)

        self.combo_growth_dir_x = QComboBox()
        self.combo_growth_dir_x.addItems(["Вправо", "Вліво", "Центр"])
        grid.addWidget(self.combo_growth_dir_x, 0, 5)

        # Рядок 2: Вісь Y
        self.combo_link_y = QComboBox()
        self.combo_link_y.addItems(["Y = H", "Y = W"])
        grid.addWidget(self.combo_link_y, 1, 0)

        grid.addWidget(QLabel("Зсув:"), 1, 1)
        self.combo_k_h = QComboBox()
        self.combo_k_h.setEditable(True)
        self.combo_k_h.addItems(preset_items)
        grid.addWidget(self.combo_k_h, 1, 2)

        grid.addWidget(QLabel("Ріст:"), 1, 3)
        self.combo_growth_p_h = QComboBox()
        self.combo_growth_p_h.setEditable(True)
        self.combo_growth_p_h.addItems(preset_items)
        grid.addWidget(self.combo_growth_p_h, 1, 4)

        self.combo_growth_dir_y = QComboBox()
        self.combo_growth_dir_y.addItems(["Вгору", "Вниз", "Центр"])
        grid.addWidget(self.combo_growth_dir_y, 1, 5)

        group_box.addLayout(grid)

        rule_layout = QHBoxLayout()
        self.combo_rule_library = QComboBox()
        self.combo_rule_library.addItems(list(self.typical_rule_library().keys()))
        rule_layout.addWidget(self.combo_rule_library)
        self.btn_apply_rule = QPushButton("Застосувати правило")
        self.btn_apply_rule.clicked.connect(self.apply_selected_rule_to_group)
        rule_layout.addWidget(self.btn_apply_rule)
        group_box.addLayout(rule_layout)

        # Підключення сигналів сітки
        self.combo_link_x.currentTextChanged.connect(self.on_link_x_changed)
        self.combo_link_y.currentTextChanged.connect(self.on_link_y_changed)
        
        self.combo_k_w.currentTextChanged.connect(self.on_combo_k_w_changed)
        self.combo_k_h.currentTextChanged.connect(self.on_combo_k_h_changed)
        self.combo_growth_p_w.currentTextChanged.connect(self.on_combo_growth_p_w_changed)
        self.combo_growth_p_h.currentTextChanged.connect(self.on_combo_growth_p_h_changed)
        
        self.combo_growth_dir_x.currentTextChanged.connect(self.on_growth_dir_x_changed)
        self.combo_growth_dir_y.currentTextChanged.connect(self.on_growth_dir_y_changed)
        # -------------------------------------------------------------

        group_constructor_group.setLayout(group_box)
        control_panel_layout.addWidget(group_constructor_group)

        control_panel_layout.addWidget(QLabel("<b>Повний список ліній/отворів у файлі:</b>"))
        self.entity_list = QListWidget()
        self.entity_list.setFixedHeight(120)
        self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        control_panel_layout.addWidget(self.entity_list)

        theme_group = QGroupBox("🎨 Інтерфейс")
        theme_box = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темна", "Світла"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_box.addWidget(self.theme_combo)
        theme_group.setLayout(theme_box)
        control_panel_layout.addWidget(theme_group)

        control_panel_layout.addStretch()
        self.update_history_buttons_state()

    def typical_rule_library(self):
        return {
            "Фіксовано": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Рухається вправо": {
                "k_w": 1.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Рухається вгору": {
                "k_w": 0.0, "k_h": 1.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Центрувати по ширині": {
                "k_w": 0.5, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Центрувати по висоті": {
                "k_w": 0.0, "k_h": 0.5,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Розтягнути вправо": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 1.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Розтягнути вгору": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 1.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Правий край + ріст вгору": {
                "k_w": 1.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 1.0,
                "growth_dir_x": "Центр", "growth_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Верхній край + ріст вправо": {
                "k_w": 0.0, "k_h": 1.0,
                "growth_p_w": 1.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Центр",
                "link_x": "X = W", "link_y": "Y = H"
            }
        }

    def apply_rule_to_group(self, group, rule_name):
        rule = self.typical_rule_library().get(rule_name)
        if not rule:
            return
        group.update(rule)

    def apply_selected_rule_to_group(self):
        selected = self.group_list_widget.selectedItems()
        if not selected:
            return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.apply_rule_to_group(self.parametric_groups[idx], self.combo_rule_library.currentText())
        self.save_project_config()
        self.on_group_selection_changed()
        self.update_viewer()

    def parse_numeric_text(self, value):
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        text = text.replace(",", ".")
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        return float(match.group(0)) if match else None

    def format_dimension_value(self, value):
        if value is None:
            return ""
        value = float(value)
        return str(int(value)) if abs(value - int(value)) < 0.001 else f"{value:.2f}".rstrip("0").rstrip(".")

    def get_dxf_bounds_dimensions(self):
        min_x, max_x = float("inf"), float("-inf")
        min_y, max_y = float("inf"), float("-inf")
        for entity in self.doc.modelspace():
            tp = entity.dxftype()
            if tp in ("CIRCLE", "ARC"):
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                min_x = min(min_x, cx - r)
                max_x = max(max_x, cx + r)
                min_y = min(min_y, cy - r)
                max_y = max(max_y, cy + r)
            elif tp == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                min_x = min(min_x, x1, x2)
                max_x = max(max_x, x1, x2)
                min_y = min(min_y, y1, y2)
                max_y = max(max_y, y1, y2)
        if min_x == float("inf") or min_y == float("inf"):
            return None, None
        return max_x - min_x, max_y - min_y

    def update_dimension_inputs_from_meta(self):
        source_w = self.project_meta.get("source_width")
        source_h = self.project_meta.get("source_height")
        if source_w is None or source_h is None:
            source_w, source_h = self.get_dxf_bounds_dimensions()
            self.project_meta["source_width"] = source_w
            self.project_meta["source_height"] = source_h

        target_w = self.project_meta.get("target_width", source_w)
        target_h = self.project_meta.get("target_height", source_h)

        self.input_current_width.setText(self.format_dimension_value(source_w))
        self.input_current_height.setText(self.format_dimension_value(source_h))
        self.input_target_width.setText(self.format_dimension_value(target_w))
        self.input_target_height.setText(self.format_dimension_value(target_h))
        self.sync_text_inputs_from_meta()
        self.sync_opening_inputs_from_meta()

    def remember_source_dimensions(self):
        source_w = self.parse_numeric_text(self.input_current_width.text())
        source_h = self.parse_numeric_text(self.input_current_height.text())
        if source_w is None or source_h is None:
            source_w, source_h = self.get_dxf_bounds_dimensions()
        self.project_meta["source_width"] = source_w
        self.project_meta["source_height"] = source_h
        self.project_meta["target_width"] = self.parse_numeric_text(self.input_target_width.text())
        self.project_meta["target_height"] = self.parse_numeric_text(self.input_target_height.text())
        self.save_project_config()
        self.update_dimension_inputs_from_meta()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Початкові розміри збережено.</font>")

    def load_block_filter_list(self):
        if not hasattr(self, "block_filter_list"):
            return
        self.block_filter_list.blockSignals(True)
        self.block_filter_list.clear()
        valid_names = set()
        for group in self.parametric_groups:
            name = group.get("name", "")
            key = self.get_group_key(group)
            valid_names.add(key)
            keep = self.block_keep_state.get(key, True)
            self.block_keep_state[key] = keep
            item = QListWidgetItem(f"{name} ({len(group['handles'])} об.)")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if keep else Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.block_filter_list.addItem(item)
        for key in list(self.block_keep_state):
            if key not in valid_names:
                del self.block_keep_state[key]
        self.block_filter_list.blockSignals(False)

    def on_block_keep_state_changed(self, item):
        self.record_action_snapshot()
        key = item.data(Qt.ItemDataRole.UserRole)
        self.block_keep_state[key] = item.checkState() == Qt.CheckState.Checked
        self.save_project_config()

    def get_text_settings(self):
        settings = self.default_text_settings()
        settings.update(self.project_meta.get("door_text", {}))
        self.project_meta["door_text"] = settings
        if settings["enabled"] and hasattr(self, "check_door_text_enabled"):
            self.check_door_text_enabled.blockSignals(True)
            self.check_door_text_enabled.setChecked(True)
            self.check_door_text_enabled.blockSignals(False)
        return settings

    def text_box_width(self, settings):
        return max(float(settings.get("width_factor", 120.0)), 1.0)

    def text_box_height(self, settings):
        return max(float(settings.get("height", 30.0)), 1.0)

    def text_display_value(self, text):
        return str(text).strip()

    def add_centered_text_preview(self, parent_item, text, box_w, box_h, font_name):
        if not text:
            return
        text_item = QGraphicsSimpleTextItem(text, parent_item)
        font = text_item.font()
        if font_name and font_name.upper() != "STANDARD":
            font.setFamily(font_name)
        font.setPointSizeF(100.0)
        text_item.setFont(font)
        text_item.setBrush(QBrush(QColor(255, 255, 255)))
        text_item.setZValue(10)
        text_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        br = text_item.boundingRect()
        if br.width() <= 0 or br.height() <= 0:
            return
        scale = min((box_w * 0.9) / br.width(), (box_h * 0.75) / br.height())
        scale = max(min(scale, 10.0), 0.01)
        text_item.setScale(scale)
        text_item.setPos(
            (box_w - br.width() * scale) * 0.5,
            (box_h - br.height() * scale) * 0.5
        )

    def sync_text_inputs_from_meta(self):
        if not hasattr(self, "input_door_text"):
            return
        settings = self.get_text_settings()
        widgets = [
            self.check_door_text_enabled,
            self.input_door_text,
            self.input_text_x,
            self.input_text_y,
            self.input_text_height,
            self.input_text_width_factor,
            self.input_text_rotation,
            self.combo_text_font
        ]
        for widget in widgets:
            widget.blockSignals(True)
        self.check_door_text_enabled.setChecked(bool(settings.get("enabled")))
        self.input_door_text.setText(str(settings.get("text", "")))
        self.input_text_x.setText(self.format_dimension_value(settings.get("x", 0.0)))
        self.input_text_y.setText(self.format_dimension_value(settings.get("y", 0.0)))
        self.input_text_height.setText(self.format_dimension_value(settings.get("height", 30.0)))
        self.input_text_width_factor.setText(self.format_dimension_value(settings.get("width_factor", 120.0)))
        self.input_text_rotation.setText(self.format_dimension_value(settings.get("rotation", 0.0)))
        self.combo_text_font.setCurrentText(str(settings.get("font", "STANDARD")))
        for widget in widgets:
            widget.blockSignals(False)

    def collect_text_settings_from_inputs(self):
        if not hasattr(self, "input_door_text"):
            return self.get_text_settings()
        settings = self.get_text_settings()
        settings["text"] = self.input_door_text.text()
        settings["enabled"] = self.check_door_text_enabled.isChecked()
        for key, widget, fallback in (
            ("x", self.input_text_x, 0.0),
            ("y", self.input_text_y, 0.0),
            ("height", self.input_text_height, 30.0),
            ("width_factor", self.input_text_width_factor, 120.0),
            ("rotation", self.input_text_rotation, 0.0),
        ):
            value = self.parse_numeric_text(widget.text())
            settings[key] = fallback if value is None else value
        settings["font"] = self.combo_text_font.currentText().strip() or "STANDARD"
        self.project_meta["door_text"] = settings
        return settings

    def on_text_settings_changed(self, *args):
        self.collect_text_settings_from_inputs()
        self.save_project_config()

    def apply_door_text_from_ui(self):
        self.record_action_snapshot()
        settings = self.collect_text_settings_from_inputs()
        settings["enabled"] = True
        self.project_meta["door_text"] = settings
        self.check_door_text_enabled.blockSignals(True)
        self.check_door_text_enabled.setChecked(True)
        self.check_door_text_enabled.blockSignals(False)
        self.apply_door_text_to_doc()
        self.doc.saveas(self.dxf_path)
        self.save_project_config()
        self.save_original_geometries()
        self.load_entities_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Текст оновлено на DXF.</font>")

    def remove_door_text_block(self):
        self.record_action_snapshot()
        settings = self.get_text_settings()
        handle = settings.get("handle")
        if handle:
            self.selected_handles.discard(handle)
            for group in self.parametric_groups:
                group["handles"].discard(handle)
            self.parametric_groups = [g for g in self.parametric_groups if g.get("handles")]
        self.remove_managed_text_entity(self.doc, settings)
        settings.update({
            "enabled": False,
            "text": "",
            "handle": None
        })
        self.project_meta["door_text"] = settings
        self.check_door_text_enabled.blockSignals(True)
        self.check_door_text_enabled.setChecked(False)
        self.check_door_text_enabled.blockSignals(False)
        self.input_door_text.setText("")
        self.doc.saveas(self.dxf_path)
        self.save_original_geometries()
        self.save_project_config()
        self.load_entities_into_list()
        self.load_groups_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Текстовий блок прибрано.</font>")

    def get_non_text_dxf_bounds(self):
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")
        for entity in self.doc.modelspace():
            tp = entity.dxftype()
            if tp == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                min_x = min(min_x, x1, x2)
                max_x = max(max_x, x1, x2)
                min_y = min(min_y, y1, y2)
                max_y = max(max_y, y1, y2)
            elif tp in ("CIRCLE", "ARC"):
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                min_x = min(min_x, cx - r)
                max_x = max(max_x, cx + r)
                min_y = min(min_y, cy - r)
                max_y = max(max_y, cy + r)
        if min_x == float("inf"):
            return None, None, None, None
        return min_x, min_y, max_x, max_y

    def align_text_box_to_door(self, dimension):
        min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
        if min_x is None:
            self.lbl_status_calc.setText("<font color='red'>Не знайдено геометрію дверей для вирівнювання.</font>")
            return
        self.record_action_snapshot()
        settings = self.collect_text_settings_from_inputs()
        settings["enabled"] = True
        if dimension == "width":
            box_w = self.text_box_width(settings)
            settings["x"] = min_x + ((max_x - min_x) - box_w) * 0.5
            message = "Текстову рамку виставлено по центру ширини полотна."
        else:
            box_h = self.text_box_height(settings)
            settings["y"] = min_y + ((max_y - min_y) - box_h) * 0.5
            message = "Текстову рамку виставлено по центру висоти полотна."
        self.project_meta["door_text"] = settings
        self.apply_door_text_to_doc()
        self.doc.saveas(self.dxf_path)
        self.save_original_geometries()
        self.save_project_config()
        self.sync_text_inputs_from_meta()
        self.load_entities_into_list()
        self.sync_list_from_handles()
        self.update_viewer()
        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>{message}</font>")

    def place_empty_door_text_block(self):
        self.record_action_snapshot()
        settings = self.collect_text_settings_from_inputs()
        settings["enabled"] = True
        if not str(settings.get("text", "")).strip():
            settings["text"] = ""
        if settings.get("x", 0.0) == 0.0 and settings.get("y", 0.0) == 0.0:
            min_x, min_y, max_x, max_y = self.get_dxf_bounds()
            if min_x is not None:
                settings["x"] = min_x + (max_x - min_x) * 0.5
                settings["y"] = min_y + (max_y - min_y) * 0.5
        self.project_meta["door_text"] = settings
        self.sync_text_inputs_from_meta()
        entity = self.apply_door_text_to_doc()
        if entity is not None:
            self.selected_handles = {entity.dxf.handle}
        self.doc.saveas(self.dxf_path)
        self.save_original_geometries()
        self.load_entities_into_list()
        self.sync_list_from_handles()
        self.save_project_config()
        self.update_viewer()
        self.lbl_status_calc.setText("<font color='#4fc3f7'>Текстовий блок можна перетягнути мишкою.</font>")

    def on_door_text_item_moved(self, item):
        self.record_action_snapshot()
        settings = self.get_text_settings()
        settings["x"] = float(item.pos().x())
        settings["y"] = float(-item.pos().y() - float(settings.get("height", 30.0)))
        settings["enabled"] = True
        self.project_meta["door_text"] = settings
        handle = settings.get("handle")
        if handle and handle in self.doc.entitydb:
            self.doc.entitydb[handle].dxf.insert = (settings["x"], settings["y"], 0.0)
            self.doc.saveas(self.dxf_path)
            self.selected_handles = {handle}
        self.sync_text_inputs_from_meta()
        self.save_project_config()
        self.load_entities_into_list()
        self.sync_list_from_handles()

    def on_door_text_box_moved(self, item):
        self.record_action_snapshot()
        settings = self.get_text_settings()
        settings["x"] = float(item.pos().x() + item.rect().x())
        settings["y"] = float(-(item.pos().y() + item.rect().y() + item.rect().height()))
        settings["enabled"] = True
        self.project_meta["door_text"] = settings
        self.apply_door_text_to_doc()
        self.doc.saveas(self.dxf_path)
        handle = settings.get("handle")
        if handle:
            self.selected_handles = {handle}
        self.sync_text_inputs_from_meta()
        self.save_project_config()
        self.load_entities_into_list()
        self.sync_list_from_handles()
        self.update_viewer()

    def sync_opening_inputs_from_meta(self):
        if not hasattr(self, "combo_door_opening"):
            return
        opening = self.project_meta.get("door_opening", "left")
        self.combo_door_opening.blockSignals(True)
        self.combo_door_opening.setCurrentText("Праве" if opening == "right" else "Ліве")
        self.combo_door_opening.blockSignals(False)

    def on_door_opening_changed(self, text):
        self.record_action_snapshot()
        self.project_meta["door_opening"] = "right" if "Прав" in text else "left"
        self.save_project_config()

    def get_dxf_bounds(self, doc=None):
        doc = doc or self.doc
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")
        for entity in doc.modelspace():
            tp = entity.dxftype()
            if tp in ("CIRCLE", "ARC"):
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                min_x = min(min_x, cx - r)
                max_x = max(max_x, cx + r)
                min_y = min(min_y, cy - r)
                max_y = max(max_y, cy + r)
            elif tp == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                min_x = min(min_x, x1, x2)
                max_x = max(max_x, x1, x2)
                min_y = min(min_y, y1, y2)
                max_y = max(max_y, y1, y2)
            elif tp == "TEXT":
                settings = self.get_text_settings()
                if settings.get("handle") == entity.dxf.handle:
                    x = float(settings.get("x", 0.0))
                    y = float(settings.get("y", 0.0))
                    w = self.text_box_width(settings)
                    h = self.text_box_height(settings)
                else:
                    x, y, _ = entity.dxf.insert
                    h = float(entity.dxf.height)
                    w = max(len(str(entity.dxf.text).strip()), 1) * h * 0.6 * float(getattr(entity.dxf, "width", 1.0))
                min_x = min(min_x, x)
                max_x = max(max_x, x + w)
                min_y = min(min_y, y)
                max_y = max(max_y, y + h)
        if min_x == float("inf"):
            return None, None, None, None
        return min_x, min_y, max_x, max_y

    def entity_bbox(self, entity):
        tp = entity.dxftype()
        if tp in ("CIRCLE", "ARC"):
            cx, cy, _ = entity.dxf.center
            r = entity.dxf.radius
            return (cx - r, cy - r, cx + r, cy + r)
        if tp == "LINE":
            x1, y1, _ = entity.dxf.start
            x2, y2, _ = entity.dxf.end
            return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        if tp == "TEXT":
            settings = self.get_text_settings()
            if settings.get("handle") == entity.dxf.handle:
                x = float(settings.get("x", 0.0))
                y = float(settings.get("y", 0.0))
                w = self.text_box_width(settings)
                h = self.text_box_height(settings)
            else:
                x, y, _ = entity.dxf.insert
                h = float(entity.dxf.height)
                w = max(len(str(entity.dxf.text).strip()), 1) * h * 0.6 * float(getattr(entity.dxf, "width", 1.0))
            return (x, y, x + w, y + h)
        return None

    def transform_managed_text_settings(self, mode, cx, cy):
        settings = self.get_text_settings()
        handle = settings.get("handle")
        if not handle or handle not in self.selected_handles:
            return
        box_w = self.text_box_width(settings)
        box_h = self.text_box_height(settings)
        center_x = float(settings.get("x", 0.0)) + box_w * 0.5
        center_y = float(settings.get("y", 0.0)) + box_h * 0.5
        dx = center_x - cx
        dy = center_y - cy
        rotation = float(settings.get("rotation", 0.0))

        if mode == "ROT90":
            center_x, center_y = cx - dy, cy + dx
            rotation += 90.0
        elif mode == "ROT180":
            center_x, center_y = cx - dx, cy - dy
            rotation += 180.0
        elif mode == "ROT270":
            center_x, center_y = cx + dy, cy - dx
            rotation += 270.0
        elif mode == "MIRROR_H":
            center_x = 2 * cx - center_x
            rotation = 180.0 - rotation
        elif mode == "MIRROR_V":
            center_y = 2 * cy - center_y
            rotation = -rotation
        else:
            return

        settings["x"] = center_x - box_w * 0.5
        settings["y"] = center_y - box_h * 0.5
        settings["rotation"] = rotation % 360.0
        self.project_meta["door_text"] = settings
        self.apply_door_text_to_doc()

    def mirror_entity_horizontally(self, entity, axis_x):
        tp = entity.dxftype()
        if tp == "LINE":
            sx, sy, sz = entity.dxf.start
            ex, ey, ez = entity.dxf.end
            entity.dxf.start = (2 * axis_x - sx, sy, sz)
            entity.dxf.end = (2 * axis_x - ex, ey, ez)
        elif tp in ("CIRCLE", "ARC"):
            cx, cy, cz = entity.dxf.center
            entity.dxf.center = (2 * axis_x - cx, cy, cz)
            if tp == "ARC":
                old_start = float(entity.dxf.start_angle)
                old_end = float(entity.dxf.end_angle)
                entity.dxf.start_angle = (180.0 - old_end) % 360.0
                entity.dxf.end_angle = (180.0 - old_start) % 360.0
        elif tp == "TEXT":
            x, y, z = entity.dxf.insert
            entity.dxf.insert = (2 * axis_x - x, y, z)
            entity.dxf.rotation = (180.0 - float(getattr(entity.dxf, "rotation", 0.0))) % 360.0

    def mirror_entity_vertically(self, entity, axis_y):
        tp = entity.dxftype()
        if tp == "LINE":
            sx, sy, sz = entity.dxf.start
            ex, ey, ez = entity.dxf.end
            entity.dxf.start = (sx, 2 * axis_y - sy, sz)
            entity.dxf.end = (ex, 2 * axis_y - ey, ez)
        elif tp in ("CIRCLE", "ARC"):
            cx, cy, cz = entity.dxf.center
            entity.dxf.center = (cx, 2 * axis_y - cy, cz)
            if tp == "ARC":
                old_start = float(entity.dxf.start_angle)
                old_end = float(entity.dxf.end_angle)
                entity.dxf.start_angle = (-old_end) % 360.0
                entity.dxf.end_angle = (-old_start) % 360.0
        elif tp == "TEXT":
            x, y, z = entity.dxf.insert
            entity.dxf.insert = (x, 2 * axis_y - y, z)
            entity.dxf.rotation = (-float(getattr(entity.dxf, "rotation", 0.0))) % 360.0

    def mirror_door_opening(self):
        min_x, min_y, max_x, max_y = self.get_dxf_bounds()
        if min_x is None:
            return
        self.record_action_snapshot()
        axis_x = (min_x + max_x) * 0.5
        for entity in self.doc.modelspace():
            tp = entity.dxftype()
            if tp == "LINE":
                sx, sy, sz = entity.dxf.start
                ex, ey, ez = entity.dxf.end
                entity.dxf.start = (2 * axis_x - sx, sy, sz)
                entity.dxf.end = (2 * axis_x - ex, ey, ez)
            elif tp in ("CIRCLE", "ARC"):
                cx, cy, cz = entity.dxf.center
                entity.dxf.center = (2 * axis_x - cx, cy, cz)
                if tp == "ARC":
                    old_start = float(entity.dxf.start_angle)
                    old_end = float(entity.dxf.end_angle)
                    entity.dxf.start_angle = (180.0 - old_end) % 360.0
                    entity.dxf.end_angle = (180.0 - old_start) % 360.0
            elif tp == "TEXT":
                x, y, z = entity.dxf.insert
                entity.dxf.insert = (2 * axis_x - x, y, z)
                entity.dxf.rotation = (180.0 - float(getattr(entity.dxf, "rotation", 0.0))) % 360.0
        settings = self.get_text_settings()
        settings["x"] = 2 * axis_x - (float(settings.get("x", 0.0)) + self.text_box_width(settings))
        settings["rotation"] = (180.0 - float(settings.get("rotation", 0.0))) % 360.0
        self.project_meta["door_text"] = settings
        self.apply_door_text_to_doc()
        self.project_meta["door_opening"] = "right" if self.project_meta.get("door_opening") != "right" else "left"
        self.doc.saveas(self.dxf_path)
        self.save_original_geometries()
        self.save_project_config()
        self.sync_opening_inputs_from_meta()
        self.sync_text_inputs_from_meta()
        self.load_entities_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Відкривання дзеркально змінено.</font>")

    def group_original_bbox(self, group):
        min_x, min_y = float("inf"), float("inf")
        max_x, max_y = float("-inf"), float("-inf")
        for handle in group.get("handles", set()):
            orig = self.original_geometries.get(handle)
            if not orig:
                continue
            if orig["type"] in ("CIRCLE", "ARC"):
                cx, cy, _ = orig["center"]
                r = orig["radius"]
                min_x = min(min_x, cx - r)
                max_x = max(max_x, cx + r)
                min_y = min(min_y, cy - r)
                max_y = max(max_y, cy + r)
            elif orig["type"] == "LINE":
                sx, sy, _ = orig["start"]
                ex, ey, _ = orig["end"]
                min_x = min(min_x, sx, ex)
                max_x = max(max_x, sx, ex)
                min_y = min(min_y, sy, ey)
                max_y = max(max_y, sy, ey)
            elif orig["type"] == "TEXT":
                x, y, _ = orig["insert"]
                h = float(orig["height"])
                w = max(len(str(orig.get("text", "")).strip()), 1) * h * 0.6 * float(orig.get("width", 1.0))
                min_x = min(min_x, x)
                max_x = max(max_x, x + w)
                min_y = min(min_y, y)
                max_y = max(max_y, y + h)
        if min_x == float("inf"):
            return None
        return (min_x, min_y, max_x, max_y)

    def simulated_group_bbox(self, group, cur_w, cur_h, target_w, target_h):
        bbox = self.group_original_bbox(group)
        if not bbox:
            return None
        min_x, min_y, max_x, max_y = bbox
        delta_w = target_w - cur_w
        delta_h = target_h - cur_h
        shift_v, growth_v = ParametricEngine.get_transform(delta_w, delta_h, group)
        min_x += shift_v[0]
        max_x += shift_v[0]
        min_y += shift_v[1]
        max_y += shift_v[1]

        if group.get("growth_dir_x", "Центр") == "Вправо":
            max_x += growth_v[0]
        elif group.get("growth_dir_x", "Центр") == "Вліво":
            min_x -= growth_v[0]
        else:
            min_x -= growth_v[0] * 0.5
            max_x += growth_v[0] * 0.5

        if group.get("growth_dir_y", "Центр") == "Вгору":
            max_y += growth_v[1]
        elif group.get("growth_dir_y", "Центр") == "Вниз":
            min_y -= growth_v[1]
        else:
            min_y -= growth_v[1] * 0.5
            max_y += growth_v[1] * 0.5

        return (min(min_x, max_x), min(min_y, max_y), max(min_x, max_x), max(min_y, max_y))

    def bboxes_overlap(self, a, b, gap=0.5):
        return not (
            a[2] <= b[0] + gap or
            b[2] <= a[0] + gap or
            a[3] <= b[1] + gap or
            b[3] <= a[1] + gap
        )

    def has_new_group_overlap(self, cur_w, cur_h, target_w, target_h):
        groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
        if len(groups) < 2:
            return False
        original_bboxes = [self.group_original_bbox(g) for g in groups]
        simulated_bboxes = [self.simulated_group_bbox(g, cur_w, cur_h, target_w, target_h) for g in groups]
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                if self.bboxes_overlap(original_bboxes[i], original_bboxes[j]):
                    continue
                if simulated_bboxes[i] and simulated_bboxes[j] and self.bboxes_overlap(simulated_bboxes[i], simulated_bboxes[j]):
                    return True
        return False

    def find_min_safe_axis(self, cur_w, cur_h, axis):
        if axis == "width":
            if not self.has_new_group_overlap(cur_w, cur_h, 1.0, cur_h):
                return 1.0
            low, high = 1.0, cur_w
            for _ in range(32):
                mid = (low + high) * 0.5
                if self.has_new_group_overlap(cur_w, cur_h, mid, cur_h):
                    low = mid
                else:
                    high = mid
            return high
        if not self.has_new_group_overlap(cur_w, cur_h, cur_w, 1.0):
            return 1.0
        low, high = 1.0, cur_h
        for _ in range(32):
            mid = (low + high) * 0.5
            if self.has_new_group_overlap(cur_w, cur_h, cur_w, mid):
                low = mid
            else:
                high = mid
        return high

    def find_minimum_safe_size(self):
        try:
            cur_w = float(self.input_current_width.text().strip())
            cur_h = float(self.input_current_height.text().strip())
        except ValueError:
            self.lbl_status_calc.setText("<font color='red'>Спочатку задайте початкову ширину і висоту.</font>")
            return
        if len(self.parametric_groups) < 2:
            self.lbl_status_calc.setText("<font color='red'>Потрібно мінімум дві параметричні групи для перевірки накладання.</font>")
            return
        min_w = self.find_min_safe_axis(cur_w, cur_h, "width")
        min_h = self.find_min_safe_axis(cur_w, cur_h, "height")
        self.lbl_status_calc.setText(
            f"<font color='#4fc3f7'>Мінімум без нового накладання: W≈{min_w:.1f} мм, H≈{min_h:.1f} мм</font>"
        )

    def get_text_style_name(self, doc, font_name):
        font = (font_name or "STANDARD").strip()
        if font.upper() == "STANDARD":
            return "STANDARD"
        style_name = "TXT_" + re.sub(r"[^0-9A-Za-z_]+", "_", font.upper()).strip("_")
        font_files = {
            "ARIAL": "arial.ttf",
            "ARIAL NARROW": "arialn.ttf",
            "SIMPLEX": "simplex.shx"
        }
        if style_name not in doc.styles:
            doc.styles.new(style_name, dxfattribs={"font": font_files.get(font.upper(), font)})
        return style_name

    def remove_managed_text_entity(self, doc=None, settings=None):
        doc = doc or self.doc
        settings = settings or self.get_text_settings()
        handle = settings.get("handle")
        if handle and handle in doc.entitydb:
            try:
                doc.modelspace().delete_entity(doc.entitydb[handle])
            except Exception:
                pass
        settings["handle"] = None

    def apply_door_text_to_doc(self, doc=None):
        doc = doc or self.doc
        settings = self.get_text_settings()
        if not settings.get("enabled"):
            self.remove_managed_text_entity(doc, settings)
            return None
        text = self.text_display_value(settings.get("text", ""))
        dxf_text = text if text else " "
        style_name = self.get_text_style_name(doc, settings.get("font", "STANDARD"))
        handle = settings.get("handle")
        entity = doc.entitydb[handle] if handle and handle in doc.entitydb else None
        if entity is None or entity.dxftype() != "TEXT":
            entity = doc.modelspace().add_text(dxf_text)
            settings["handle"] = entity.dxf.handle
        box_x = float(settings.get("x", 0.0))
        box_y = float(settings.get("y", 0.0))
        box_w = self.text_box_width(settings)
        box_h = self.text_box_height(settings)
        text_h = max(box_h * 0.55, 0.1)
        center_x = box_x + box_w * 0.5
        center_y = box_y + box_h * 0.5
        entity.dxf.text = dxf_text
        entity.dxf.height = text_h
        entity.dxf.style = style_name
        entity.dxf.width = 1.0
        entity.set_placement((center_x, center_y, 0.0), align=TextEntityAlignment.MIDDLE_CENTER)
        entity.dxf.rotation = float(settings.get("rotation", 0.0))
        self.project_meta["door_text"] = settings
        return entity

    def normalize_key(self, value):
        text = str(value).strip().lower()
        replacements = {
            "ширина": "target_width",
            "width": "target_width",
            "w": "target_width",
            "нова ширина": "target_width",
            "target_width": "target_width",
            "висота": "target_height",
            "height": "target_height",
            "h": "target_height",
            "нова висота": "target_height",
            "target_height": "target_height",
            "поточна ширина": "source_width",
            "source_width": "source_width",
            "current_width": "source_width",
            "початкова ширина": "source_width",
            "поточна висота": "source_height",
            "source_height": "source_height",
            "current_height": "source_height",
            "початкова висота": "source_height",
            "лишити": "keep_blocks",
            "keep": "keep_blocks",
            "keep_blocks": "keep_blocks",
            "видалити": "delete_blocks",
            "delete": "delete_blocks",
            "delete_blocks": "delete_blocks",
            "текст": "text",
            "text": "text",
            "door_text": "text",
            "текст x": "text_x",
            "text_x": "text_x",
            "x_text": "text_x",
            "текст y": "text_y",
            "text_y": "text_y",
            "y_text": "text_y",
            "розмір шрифту": "font_size",
            "висота тексту": "font_size",
            "font_size": "font_size",
            "text_height": "font_size",
            "шрифт": "font",
            "font": "font",
            "ширина тексту": "text_width",
            "text_width": "text_width",
            "width_factor": "text_width",
            "поворот тексту": "text_rotation",
            "text_rotation": "text_rotation",
            "rotation": "text_rotation",
        }
        return replacements.get(text, text)

    def read_csv_rows(self, path):
        for encoding in ("utf-8-sig", "cp1251", "utf-8"):
            try:
                with open(path, newline="", encoding=encoding) as f:
                    return [row for row in csv.reader(f) if any(str(c).strip() for c in row)]
            except UnicodeDecodeError:
                continue
        return []

    def read_xlsx_rows(self, path):
        ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with zipfile.ZipFile(path) as zf:
            shared = []
            if "xl/sharedStrings.xml" in zf.namelist():
                root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
                for si in root.findall("a:si", ns):
                    shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
            sheet_name = "xl/worksheets/sheet1.xml"
            root = ET.fromstring(zf.read(sheet_name))
            rows = []
            for row in root.findall(".//a:row", ns):
                values = []
                for cell in row.findall("a:c", ns):
                    raw = cell.find("a:v", ns)
                    text = raw.text if raw is not None else ""
                    if cell.attrib.get("t") == "s" and text:
                        text = shared[int(text)]
                    values.append(text)
                if any(str(v).strip() for v in values):
                    rows.append(values)
            return rows

    def import_parameters_from_table(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть Excel/CSV з параметрами",
            self.project_dir,
            "Tables (*.xlsx *.csv);;All Files (*)"
        )
        if not path:
            return
        try:
            rows = self.read_xlsx_rows(path) if path.lower().endswith(".xlsx") else self.read_csv_rows(path)
            params = self.extract_table_parameters(rows)
            self.record_action_snapshot()
            self.apply_imported_parameters(params)
            self.apply_door_text_to_doc()
            self.doc.saveas(self.dxf_path)
            self.save_project_config()
            self.save_original_geometries()
            self.update_dimension_inputs_from_meta()
            self.sync_text_inputs_from_meta()
            self.load_entities_into_list()
            self.update_viewer()
            self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Параметри імпортовано: {os.path.basename(path)}</font>")
        except Exception as e:
            self.lbl_status_calc.setText(f"<font color='red'>Помилка імпорту: {e}</font>")

    def quick_order_wizard(self):
        default_text = f"{self.input_target_width.text()}x{self.input_target_height.text()}"
        text, ok = QInputDialog.getText(
            self,
            "Нове замовлення",
            "Введіть новий розмір W x H:",
            text=default_text
        )
        if not ok:
            return
        nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[,.]\d+)?", text)]
        if len(nums) < 2:
            self.lbl_status_calc.setText("<font color='red'>Введіть два числа: ширина і висота.</font>")
            return
        if not self.input_current_width.text().strip() or not self.input_current_height.text().strip():
            self.update_dimension_inputs_from_meta()
        self.input_target_width.setText(self.format_dimension_value(nums[0]))
        self.input_target_height.setText(self.format_dimension_value(nums[1]))
        self.export_new_dxf_with_dimensions()

    def extract_table_parameters(self, rows):
        params = {}
        if not rows:
            return params

        headers = [self.normalize_key(c) for c in rows[0]]
        if "target_width" in headers or "target_height" in headers:
            for row in rows[1:]:
                for idx, key in enumerate(headers):
                    if idx >= len(row):
                        continue
                    value = row[idx]
                    if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
                        num = self.parse_numeric_text(value)
                        if num is not None:
                            params[key] = num
                    elif key in ("text", "font"):
                        params[key] = str(value).strip()
                    elif key in ("keep_blocks", "delete_blocks"):
                        params.setdefault(key, []).extend(self.split_block_names(value))
            return params

        for row in rows:
            if len(row) < 2:
                continue
            key = self.normalize_key(row[0])
            value = row[1]
            if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
                num = self.parse_numeric_text(value)
                if num is not None:
                    params[key] = num
            elif key in ("text", "font"):
                params[key] = str(value).strip()
            elif key in ("keep_blocks", "delete_blocks"):
                params[key] = self.split_block_names(value)
        return params

    def split_block_names(self, value):
        if value is None:
            return []
        return [part.strip() for part in re.split(r"[,;\n]+", str(value)) if part.strip()]

    def apply_imported_parameters(self, params):
        for key in ("source_width", "source_height", "target_width", "target_height"):
            if key in params:
                self.project_meta[key] = params[key]
        text_settings = self.get_text_settings()
        text_key_map = {
            "text": "text",
            "text_x": "x",
            "text_y": "y",
            "font_size": "height",
            "text_width": "width_factor",
            "text_rotation": "rotation",
            "font": "font"
        }
        for source_key, target_key in text_key_map.items():
            if source_key in params:
                text_settings[target_key] = params[source_key]
        if "text" in params and str(params["text"]).strip():
            text_settings["enabled"] = True
            if "text_x" not in params and "text_y" not in params:
                self.lbl_status_calc.setText("<font color='#4fc3f7'>Текст підставлено в попередньо задану рамку.</font>")
        self.project_meta["door_text"] = text_settings
        if "keep_blocks" in params and params["keep_blocks"]:
            keep_set = set(params["keep_blocks"])
            for group in self.parametric_groups:
                name = group.get("name", "")
                key = self.get_group_key(group)
                self.block_keep_state[key] = key in keep_set or name in keep_set
        if "delete_blocks" in params and params["delete_blocks"]:
            delete_set = set(params["delete_blocks"])
            for group in self.parametric_groups:
                name = group.get("name", "")
                key = self.get_group_key(group)
                if key in delete_set or name in delete_set:
                    self.block_keep_state[key] = False
        self.update_dimension_inputs_from_meta()
        self.sync_text_inputs_from_meta()
        self.load_block_filter_list()
        self.save_project_config()

    def sanitize_filename_part(self, value):
        text = self.format_dimension_value(value)
        return re.sub(r"[^0-9A-Za-zА-Яа-я_\-.]+", "_", text)

    def build_export_path(self, target_w, target_h):
        base_name = os.path.splitext(os.path.basename(self.dxf_path))[0]
        base_name = re.sub(r"(?<!\d)\d{3,5}_\d{3,5}(?!\d)", "", base_name).strip("_- ")
        width_part = self.sanitize_filename_part(target_w)
        height_part = self.sanitize_filename_part(target_h)
        name = f"{base_name}_{width_part}_{height_part}.DXF"
        path = os.path.join(self.project_dir, name)
        counter = 2
        while os.path.exists(path):
            name = f"{base_name}_{width_part}_{height_part}_{counter}.DXF"
            path = os.path.join(self.project_dir, name)
            counter += 1
        return path

    def preview_parametric_scale(self):
        self.record_action_snapshot()
        self.process_parametric_percentage_scale(save_result=False, record_history=False)
        self.lbl_status_calc.setText("<font color='#4fc3f7'>Перегляд застосовано тільки на екрані. Файл ще не збережено.</font>")

    def restore_current_dxf_from_disk(self):
        if not os.path.exists(self.dxf_path):
            return
        self.record_action_snapshot()
        self.doc = ezdxf.readfile(self.dxf_path)
        self.save_original_geometries()
        self.update_dimension_inputs_from_meta()
        self.update_viewer()
        self.load_entities_into_list()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Повернуто стан з відкритого DXF.</font>")

    def export_new_dxf_with_dimensions(self):
        self.collect_text_settings_from_inputs()
        original_bytes = None
        if os.path.exists(self.dxf_path):
            with open(self.dxf_path, "rb") as f:
                original_bytes = f.read()
        original_meta = copy.deepcopy(self.project_meta)
        original_groups = copy.deepcopy(self.parametric_groups)
        original_keep_state = copy.deepcopy(self.block_keep_state)

        self.project_meta["source_width"] = self.parse_numeric_text(self.input_current_width.text())
        self.project_meta["source_height"] = self.parse_numeric_text(self.input_current_height.text())
        self.project_meta["target_width"] = self.parse_numeric_text(self.input_target_width.text())
        self.project_meta["target_height"] = self.parse_numeric_text(self.input_target_height.text())
        self.is_loading_history = True
        self.process_parametric_percentage_scale(save_result=True, record_history=False)
        self.is_loading_history = False

        target_w = self.project_meta.get("target_width")
        target_h = self.project_meta.get("target_height")
        export_path = self.build_export_path(target_w, target_h)

        export_doc = copy.deepcopy(self.doc)
        export_msp = export_doc.modelspace()
        delete_handles = set()
        for group in self.parametric_groups:
            key = self.get_group_key(group)
            if not self.block_keep_state.get(key, True):
                delete_handles.update(group.get("handles", set()))
        for hndl in list(delete_handles):
            if hndl in export_doc.entitydb:
                export_msp.delete_entity(export_doc.entitydb[hndl])

        export_doc.saveas(export_path)
        if original_bytes is not None:
            with open(self.dxf_path, "wb") as f:
                f.write(original_bytes)
            self.doc = ezdxf.readfile(self.dxf_path)
        self.project_meta = original_meta
        self.parametric_groups = original_groups
        self.block_keep_state = original_keep_state
        self.save_original_geometries()
        self.save_project_config()
        self.scan_project_folder_for_dxf()
        self.update_dimension_inputs_from_meta()
        self.load_groups_into_list()
        self.load_entities_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Створено: {os.path.basename(export_path)}</font>")

    def batch_export_from_table(self):
        self.collect_text_settings_from_inputs()
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть Excel/CSV для пакетного створення DXF",
            self.project_dir,
            "Tables (*.xlsx *.csv);;All Files (*)"
        )
        if not path:
            return

        original_bytes = None
        if os.path.exists(self.dxf_path):
            with open(self.dxf_path, "rb") as f:
                original_bytes = f.read()
        original_meta = copy.deepcopy(self.project_meta)
        original_groups = copy.deepcopy(self.parametric_groups)
        original_keep_state = copy.deepcopy(self.block_keep_state)

        try:
            rows = self.read_xlsx_rows(path) if path.lower().endswith(".xlsx") else self.read_csv_rows(path)
            jobs = self.extract_batch_jobs(rows)
            created = []
            for job in jobs:
                self.project_meta = copy.deepcopy(original_meta)
                self.parametric_groups = copy.deepcopy(original_groups)
                self.block_keep_state = copy.deepcopy(original_keep_state)
                self.apply_imported_parameters(job)
                self.is_loading_history = True
                self.process_parametric_percentage_scale(save_result=True, record_history=False)
                self.is_loading_history = False

                target_w = self.project_meta.get("target_width")
                target_h = self.project_meta.get("target_height")
                export_path = self.build_export_path(target_w, target_h)
                export_doc = copy.deepcopy(self.doc)
                export_msp = export_doc.modelspace()
                delete_handles = self.get_export_delete_handles()
                for hndl in delete_handles:
                    if hndl in export_doc.entitydb:
                        export_msp.delete_entity(export_doc.entitydb[hndl])
                export_doc.saveas(export_path)
                created.append(os.path.basename(export_path))

                if original_bytes is not None:
                    with open(self.dxf_path, "wb") as f:
                        f.write(original_bytes)
                    self.doc = ezdxf.readfile(self.dxf_path)
                    self.save_original_geometries()

            self.project_meta = original_meta
            self.parametric_groups = original_groups
            self.block_keep_state = original_keep_state
            self.save_project_config()
            self.scan_project_folder_for_dxf()
            self.update_dimension_inputs_from_meta()
            self.load_groups_into_list()
            self.load_entities_into_list()
            self.update_viewer()
            self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Пакет створено: {len(created)} DXF</font>")
        except Exception as e:
            self.lbl_status_calc.setText(f"<font color='red'>Помилка пакета: {e}</font>")
            if original_bytes is not None:
                with open(self.dxf_path, "wb") as f:
                    f.write(original_bytes)
                self.doc = ezdxf.readfile(self.dxf_path)
                self.save_original_geometries()

    def extract_batch_jobs(self, rows):
        if not rows:
            return []
        headers = [self.normalize_key(c) for c in rows[0]]
        jobs = []
        for row in rows[1:]:
            params = {}
            for idx, key in enumerate(headers):
                if idx >= len(row):
                    continue
                value = row[idx]
                if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
                    num = self.parse_numeric_text(value)
                    if num is not None:
                        params[key] = num
                elif key in ("text", "font"):
                    text_value = str(value).strip()
                    if text_value:
                        params[key] = text_value
                elif key in ("keep_blocks", "delete_blocks"):
                    names = self.split_block_names(value)
                    if names:
                        params.setdefault(key, []).extend(names)
            if params:
                jobs.append(params)
        if not jobs:
            single = self.extract_table_parameters(rows)
            if single:
                jobs.append(single)
        return jobs

    def get_export_delete_handles(self):
        delete_handles = set()
        for group in self.parametric_groups:
            key = self.get_group_key(group)
            if not self.block_keep_state.get(key, True):
                delete_handles.update(group.get("handles", set()))
        return delete_handles

    def open_dxf_from_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Виберіть DXF файл",
            self.project_dir,
            "DXF Files (*.dxf);;All Files (*)"
        )
        
        if file_path:
            try:
                self.project_dir = os.path.dirname(os.path.abspath(file_path))
                self.dxf_path = os.path.abspath(file_path)
                
                self.doc = ezdxf.readfile(self.dxf_path)
                
                self.selected_handles.clear()
                self.parametric_groups.clear()
                self.zones_undo_stack.clear()
                self.zones_redo_stack.clear()
                self.global_recalc_undo_stack.clear()
                self.global_recalc_redo_stack.clear()
                
                self.load_project_config()
                self.update_dimension_inputs_from_meta()
                
                self.history = HistoryManager(self.dxf_path)
                self.history.save_state()
                self.save_zones_history_state()
                self.save_original_geometries()
                
                self.scan_project_folder_for_dxf()
                self.update_viewer()
                self.load_entities_into_list()
                self.load_groups_into_list()
                self.load_block_filter_list()
                self.update_history_buttons_state()
                
            except Exception as e:
                print(f"Помилка при відкритті файлу: {e}")

    def transform_selected_entities(self, mode):
        if not self.selected_handles: return
        selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
        if not selected_entities: return
        self.record_action_snapshot()

        bboxes = [self.entity_bbox(e) for e in selected_entities]
        bboxes = [b for b in bboxes if b]
        if not bboxes:
            return
        min_x = min(b[0] for b in bboxes)
        min_y = min(b[1] for b in bboxes)
        max_x = max(b[2] for b in bboxes)
        max_y = max(b[3] for b in bboxes)
        cx = (min_x + max_x) * 0.5
        cy = (min_y + max_y) * 0.5

        for entity in selected_entities:
            if mode == "ROT90":
                m1 = Matrix44.translate(-cx, -cy, 0)
                m2 = Matrix44.z_rotate(math.radians(90))
                m3 = Matrix44.translate(cx, cy, 0)
                m = m1 @ m2 @ m3
            elif mode == "ROT180":
                m1 = Matrix44.translate(-cx, -cy, 0)
                m2 = Matrix44.z_rotate(math.radians(180))
                m3 = Matrix44.translate(cx, cy, 0)
                m = m1 @ m2 @ m3
            elif mode == "ROT270":
                m1 = Matrix44.translate(-cx, -cy, 0)
                m2 = Matrix44.z_rotate(math.radians(270))
                m3 = Matrix44.translate(cx, cy, 0)
                m = m1 @ m2 @ m3
            elif mode == "MIRROR_H":
                self.mirror_entity_horizontally(entity, cx)
                continue
            elif mode == "MIRROR_V":
                self.mirror_entity_vertically(entity, cy)
                continue
            else: 
                continue
            entity.transform(m)

        self.transform_managed_text_settings(mode, cx, cy)

        # --- РОЗУМНЕ ОНОВЛЕННЯ ПАРАМЕТРІВ ГРУПИ ПРИ ТРАНСФОРМАЦІЇ ---
        for group in self.parametric_groups:
            if not group["handles"].isdisjoint(self.selected_handles):
                # Зберігаємо старі значення
                old_kw = group.get("k_w", 0.0)
                old_kh = group.get("k_h", 0.0)
                old_gpw = group.get("growth_p_w", 0.0)
                old_gph = group.get("growth_p_h", 0.0)
                
                old_link_x = group.get("link_x", "X = W")
                old_link_y = group.get("link_y", "Y = H")
                
                old_dir_x = group.get("growth_dir_x", "Центр")
                old_dir_y = group.get("growth_dir_y", "Центр")

                if mode == "ROT90":
                    group["k_w"], group["k_h"] = old_kh, old_kw
                    group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
                    group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
                    group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
                    # Переклад напрямку (Поворот проти годинникової)
                    map_x_to_y = {"Вправо": "Вгору", "Вліво": "Вниз", "Центр": "Центр"}
                    map_y_to_x = {"Вгору": "Вліво", "Вниз": "Вправо", "Центр": "Центр"}
                    group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
                    group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")

                elif mode == "ROT270":
                    group["k_w"], group["k_h"] = old_kh, old_kw
                    group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
                    group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
                    group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
                    # Переклад напрямку (Поворот за годинниковою)
                    map_x_to_y = {"Вправо": "Вниз", "Вліво": "Вгору", "Центр": "Центр"}
                    map_y_to_x = {"Вгору": "Вправо", "Вниз": "Вліво", "Центр": "Центр"}
                    group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
                    group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")

                elif mode == "ROT180":
                    map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
                    map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
                    group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
                    group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")

                elif mode == "MIRROR_H": # Дзеркало по горизонталі (міняється тільки X)
                    map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
                    group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")

                elif mode == "MIRROR_V": # Дзеркало по вертикалі (міняється тільки Y)
                    map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
                    group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
                    
        self.doc.saveas(self.dxf_path)
        self.save_project_config()
        self.save_original_geometries() 
        self.push_to_history()
        
        self.on_group_selection_changed() # <- Тут інтерфейс підтягне нові слова "Вгору", "Вниз" тощо
        self.sync_text_inputs_from_meta()
        self.update_viewer()
        self.load_entities_into_list()

    def snap_to_zero(self):
        min_x, min_y, max_x, max_y = self.get_dxf_bounds()
        if min_x is None or min_y is None:
            return
        self.record_action_snapshot()
        shift_x = -min_x
        shift_y = -min_y

        matrix = Matrix44.translate(shift_x, shift_y, 0)
        for entity in self.doc.modelspace():
            try:
                entity.transform(matrix)
            except Exception:
                tp = entity.dxftype()
                if tp == "TEXT":
                    x, y, z = entity.dxf.insert
                    entity.dxf.insert = (x + shift_x, y + shift_y, z)

        settings = self.get_text_settings()
        settings["x"] = float(settings.get("x", 0.0)) + shift_x
        settings["y"] = float(settings.get("y", 0.0)) + shift_y
        self.project_meta["door_text"] = settings

        self.doc.saveas(self.dxf_path)
        self.save_original_geometries()
        self.save_project_config()
        self.push_to_history()
        self.sync_text_inputs_from_meta()
        self.load_entities_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Фігуру притиснуто до (0,0).</font>")

    def delete_entities_from_dxf(self):
        if not self.selected_handles:
            return
        self.record_action_snapshot()

        msp = self.doc.modelspace()
        handles_to_delete = list(self.selected_handles)

        for hndl in handles_to_delete:
            if hndl in self.doc.entitydb:
                entity = self.doc.entitydb[hndl]
                msp.delete_entity(entity)
            
            if hndl in self.original_geometries:
                del self.original_geometries[hndl]

            for group in self.parametric_groups:
                if hndl in group["handles"]:
                    group["handles"].remove(hndl)

        self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]
        self.selected_handles.clear()
        
        self.doc.saveas(self.dxf_path)
        self.save_project_config()
        self.push_to_history()
        
        self.load_entities_into_list()
        self.load_groups_into_list()
        self.update_viewer()

    def toggle_inspector_mode(self, checked):
        if not checked:
            if self.coord_tooltip_item and self.coord_tooltip_item in self.scene.items():
                self.scene.removeItem(self.coord_tooltip_item)
            if self.coord_snap_marker and self.coord_snap_marker in self.scene.items():
                self.scene.removeItem(self.coord_snap_marker)
            self.coord_tooltip_item = None
            self.coord_snap_marker = None
        self.update_viewer()

    def on_scene_mouse_move(self, event):
        QGraphicsScene.mouseMoveEvent(self.scene, event)
        if not self.chk_enable_inspector.isChecked():
            return

        pos = event.scenePos()
        cursor_x, cursor_y = pos.x(), -pos.y()

        closest_pt = None
        min_dist = float('inf')

        for entity in self.doc.modelspace():
            if entity.dxftype() == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                
                d1 = math.hypot(cursor_x - x1, cursor_y - y1)
                d2 = math.hypot(cursor_x - x2, cursor_y - y2)

                if d1 < min_dist:
                    min_dist = d1
                    closest_pt = (x1, y1, "START")
                if d2 < min_dist:
                    min_dist = d2
                    closest_pt = (x2, y2, "END")

        if closest_pt and min_dist < 40.0:
            snap_x, snap_y, pt_type = closest_pt
            if not self.coord_snap_marker:
                self.coord_snap_marker = self.scene.addEllipse(-4, -4, 8, 8, QPen(QColor("#ff9800"), 1.5), QBrush(QColor(255, 152, 0, 150)))
                self.coord_tooltip_item = self.scene.addText("")
                self.coord_tooltip_item.setDefaultTextColor(QColor("#ff9800"))
            
            self.coord_snap_marker.setPos(snap_x, -snap_y)
            self.coord_tooltip_item.setPos(snap_x + 10, -snap_y - 25)
            self.coord_tooltip_item.setPlainText(f"Вузол {pt_type}\nX: {snap_x:.1f}\nY: {snap_y:.1f}")
        else:
            if self.coord_tooltip_item:
                self.coord_tooltip_item.setPlainText("")
            if self.coord_snap_marker:
                self.coord_snap_marker.setPos(-99999, -99999)
        
        self.view.viewport().update()

    def create_parametric_group(self):
        if len(self.selected_handles) < 1:
            return  

        name, ok = QInputDialog.getText(
            self,
            "Нова група",
            "Введіть назву групи:"
        )
        if not ok or not name.strip():
            name = f"Група {len(self.parametric_groups) + 1}"
        self.record_action_snapshot()

        for group in self.parametric_groups:
            group["handles"].difference_update(self.selected_handles)
        self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]

        new_group = {
            "name": name.strip(),
            "handles": set(self.selected_handles),
            "k_w": 0.0, 
            "k_h": 0.0,
            "growth_p_w": 0.0, 
            "growth_p_h": 0.0,
            "growth_dir_x": "Центр",
            "growth_dir_y": "Центр",
            "link_x": "X = W",
            "link_y": "Y = H"
        }
        self.get_group_key(new_group)
        self.parametric_groups.append(new_group)
        self.block_keep_state[new_group["uid"]] = True
        self.clear_selection()
        self.push_to_history()
        self.save_project_config()
        self.load_groups_into_list()
        self.update_viewer()

    def disband_parametric_group(self):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        del self.parametric_groups[idx]
        self.clear_selection()
        self.push_to_history()
        self.save_project_config()
        self.load_groups_into_list()
        self.update_viewer()

    def remove_selected_from_group(self):
        selected_group_item = self.group_list_widget.currentItem()
        if not selected_group_item or not self.selected_handles: return
        self.record_action_snapshot()
        
        idx = selected_group_item.data(Qt.ItemDataRole.UserRole)
        group = self.parametric_groups[idx]
        
        group["handles"] -= self.selected_handles
        if not group["handles"]:
            del self.parametric_groups[idx]
            
        self.clear_selection()
        self.push_to_history()
        self.save_project_config()
        self.load_groups_into_list()
        self.update_viewer()

    def load_groups_into_list(self):
        self.group_list_widget.blockSignals(True)
        self.group_list_widget.clear()
        for idx, group in enumerate(self.parametric_groups):
            name = group.get("name", f"Гр №{idx+1}")
            text = f"🧩 {name} ({len(group['handles'])} об.)"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.group_list_widget.addItem(item)
        self.group_list_widget.blockSignals(False)
        self.load_block_filter_list()

    def on_group_selection_changed(self):
        selected = self.group_list_widget.selectedItems()
        widgets_to_toggle = [
            self.combo_k_w, self.combo_k_h, self.combo_growth_p_w, 
            self.combo_growth_p_h, self.combo_growth_dir_x, self.combo_growth_dir_y, 
            self.combo_link_x, self.combo_link_y
        ]
        
        if not selected:
            for widget in widgets_to_toggle: widget.setEnabled(False)
            return
        
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        group = self.parametric_groups[idx]

        for widget in widgets_to_toggle:
            widget.blockSignals(True)
            widget.setEnabled(True)
        
        self.combo_k_w.setCurrentText(format_factor(group.get("k_w", 0.0)))
        self.combo_k_h.setCurrentText(format_factor(group.get("k_h", 0.0)))
        self.combo_growth_p_w.setCurrentText(format_factor(group.get("growth_p_w", 0.0)))
        self.combo_growth_p_h.setCurrentText(format_factor(group.get("growth_p_h", 0.0)))
        
        self.combo_growth_dir_x.setCurrentText(group.get("growth_dir_x", "Центр"))
        self.combo_growth_dir_y.setCurrentText(group.get("growth_dir_y", "Центр"))
        
        link_x_val = group.get("link_x", "X = W")
        self.combo_link_x.setCurrentText("X = W" if "W" in link_x_val else "X = H")
        link_y_val = group.get("link_y", "Y = H")
        self.combo_link_y.setCurrentText("Y = W" if "W" in link_y_val else "Y = H")

        for widget in widgets_to_toggle:
            widget.blockSignals(False)

        self.selected_handles = set(group["handles"])
        self.sync_list_from_handles()
        self.update_viewer()

    def on_combo_k_w_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["k_w"] = parse_factor(text)
        self.save_project_config()

    def on_combo_k_h_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["k_h"] = parse_factor(text)
        self.save_project_config()

    def on_combo_growth_p_w_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_p_w"] = parse_factor(text)
        self.save_project_config()

    def on_combo_growth_p_h_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_p_h"] = parse_factor(text)
        self.save_project_config()

    def on_link_x_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["link_x"] = text
        self.save_project_config()

    def on_link_y_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["link_y"] = text
        self.save_project_config()

    def on_growth_dir_x_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_dir_x"] = text
        self.save_project_config()

    def on_growth_dir_y_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_dir_y"] = text
        self.save_project_config()

    def process_parametric_percentage_scale(self, save_result=True, record_history=True):
        try:
            cur_w = float(self.input_current_width.text().strip())
            target_w = float(self.input_target_width.text().strip())
            cur_h = float(self.input_current_height.text().strip())
            target_h = float(self.input_target_height.text().strip())
        except ValueError:
            return

        self.collect_text_settings_from_inputs()
        should_record = save_result and record_history and not self.is_loading_history
        if should_record:
            before_snapshot = self.capture_full_state_snapshot()
            self.history.save_state()
            self.history.clear_redo()
            self.save_zones_history_state()
            self.zones_redo_stack.clear()
            self.global_recalc_undo_stack.append(before_snapshot)
            self.global_recalc_redo_stack.clear()
            if len(self.global_recalc_undo_stack) > 30:
                self.global_recalc_undo_stack.pop(0)

        delta_w = target_w - cur_w
        delta_h = target_h - cur_h
        self.project_meta["source_width"] = cur_w
        self.project_meta["source_height"] = cur_h
        self.project_meta["target_width"] = target_w
        self.project_meta["target_height"] = target_h

        for hndl, orig in self.original_geometries.items():
            if hndl not in self.doc.entitydb: continue
            entity = self.doc.entitydb[hndl]

            associated_group = None
            for group in self.parametric_groups:
                if hndl in group["handles"]:
                    associated_group = group
                    break

            if associated_group is None:
                if orig["type"] == "LINE":
                    entity.dxf.start = orig["start"]
                    entity.dxf.end = orig["end"]
                elif orig["type"] in ("CIRCLE", "ARC"):
                    entity.dxf.center = orig["center"]
                    entity.dxf.radius = orig["radius"]
                elif orig["type"] == "TEXT":
                    entity.dxf.insert = orig["insert"]
                    entity.dxf.height = orig["height"]
                    entity.dxf.width = orig["width"]
                    entity.dxf.rotation = orig["rotation"]
                continue

            shift_v, growth_v = ParametricEngine.get_transform(delta_w, delta_h, associated_group)
            
            growth_dir_x = associated_group.get("growth_dir_x", "Центр")
            growth_dir_y = associated_group.get("growth_dir_y", "Центр")

            if orig["type"] == "LINE":
                sx, sy, sz = orig["start"]
                ex, ey, ez = orig["end"]

                dsx, dsy = shift_v[0], shift_v[1]
                dex, dey = shift_v[0], shift_v[1]

                # --- ЛОГІКА ПО X (ШИРИНА) ---
                if sx < ex: left_p, right_p = "S", "E"
                elif sx > ex: left_p, right_p = "E", "S"
                else: left_p, right_p = "BOTH", "BOTH"

                if growth_dir_x == "Вправо":
                    if right_p in ("S", "BOTH"): dsx += growth_v[0]
                    if right_p in ("E", "BOTH"): dex += growth_v[0]
                elif growth_dir_x == "Вліво":
                    if left_p in ("S", "BOTH"): dsx -= growth_v[0]
                    if left_p in ("E", "BOTH"): dex -= growth_v[0]
                else: # Центр
                    if left_p == "S": dsx -= growth_v[0] * 0.5
                    if right_p == "S": dsx += growth_v[0] * 0.5
                    if left_p == "E": dex -= growth_v[0] * 0.5
                    if right_p == "E": dex += growth_v[0] * 0.5

                # --- ЛОГІКА ПО Y (ВИСОТА) ---
                if sy < ey: bottom_p, top_p = "S", "E"
                elif sy > ey: bottom_p, top_p = "E", "S"
                else: bottom_p, top_p = "BOTH", "BOTH"

                if growth_dir_y == "Вгору":
                    if top_p in ("S", "BOTH"): dsy += growth_v[1]
                    if top_p in ("E", "BOTH"): dey += growth_v[1]
                elif growth_dir_y == "Вниз":
                    if bottom_p in ("S", "BOTH"): dsy -= growth_v[1]
                    if bottom_p in ("E", "BOTH"): dey -= growth_v[1]
                else: # Центр
                    if bottom_p == "S": dsy -= growth_v[1] * 0.5
                    if top_p == "S": dsy += growth_v[1] * 0.5
                    if bottom_p == "E": dey -= growth_v[1] * 0.5
                    if top_p == "E": dey += growth_v[1] * 0.5

                entity.dxf.start = (sx + dsx, sy + dsy, sz)
                entity.dxf.end = (ex + dex, ey + dey, ez)

            elif orig["type"] in ("CIRCLE", "ARC"):
                cx, cy, cz = orig["center"]
                r = orig["radius"]

                entity.dxf.center = (cx + shift_v[0], cy + shift_v[1], cz)

                new_r = r
                if growth_v[0] != 0.0 or growth_v[1] != 0.0:
                    scale_factor = 1.0 + ((abs(growth_v[0]) + abs(growth_v[1])) / (cur_w + cur_h))
                    new_r = r * scale_factor

                entity.dxf.radius = new_r

            elif orig["type"] == "TEXT":
                x, y, z = orig["insert"]
                new_x = x + shift_v[0]
                new_y = y + shift_v[1]
                new_height = max(float(orig["height"]) + growth_v[1], 0.1)
                new_width = max(float(orig["width"]), 0.01)
                if growth_v[0] != 0.0:
                    new_width = max(float(orig["width"]) + growth_v[0], 0.01)
                entity.dxf.insert = (new_x, new_y, z)
                entity.dxf.height = new_height
                entity.dxf.width = new_width

                settings = self.get_text_settings()
                if settings.get("handle") == hndl:
                    settings["x"] = new_x
                    settings["y"] = new_y
                    settings["height"] = new_height
                    settings["width_factor"] = new_width
                    self.project_meta["door_text"] = settings

        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔW={delta_w:+.1f} мм | ΔH={delta_h:+.1f} мм</font>")
        self.apply_door_text_to_doc()
        if save_result:
            self.doc.saveas(self.dxf_path)
        self.save_project_config()
        if should_record:
            self.history.save_state()
            self.save_zones_history_state()
            self.global_recalc_redo_stack.clear()
            self.update_history_buttons_state()
        self.update_viewer()

    def save_original_geometries(self):
        self.original_geometries.clear()
        for entity in self.doc.modelspace():
            hndl = entity.dxf.handle
            tp = entity.dxftype()
            if tp == "CIRCLE":
                self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
            elif tp == "LINE":
                self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}
            elif tp == "ARC":
                self.original_geometries[hndl] = {"type": "ARC", "center": entity.dxf.center, "radius": entity.dxf.radius, "start_angle": entity.dxf.start_angle, "end_angle": entity.dxf.end_angle}
            elif tp == "TEXT":
                settings = self.get_text_settings()
                if settings.get("handle") == hndl:
                    insert = (
                        float(settings.get("x", 0.0)),
                        float(settings.get("y", 0.0)),
                        0.0
                    )
                    height = self.text_box_height(settings)
                    width = self.text_box_width(settings)
                    text_value = settings.get("text", "")
                else:
                    insert = entity.dxf.insert
                    height = float(entity.dxf.height)
                    width = float(getattr(entity.dxf, "width", 1.0))
                    text_value = entity.dxf.text
                self.original_geometries[hndl] = {
                    "type": "TEXT",
                    "insert": insert,
                    "height": height,
                    "width": width,
                    "rotation": float(getattr(entity.dxf, "rotation", 0.0)),
                    "text": text_value
                }

    def save_zones_history_state(self):
        state_snapshot = {
            "parametric_groups": copy.deepcopy(self.parametric_groups),
            "project_meta": copy.deepcopy(self.project_meta),
            "block_keep_state": copy.deepcopy(self.block_keep_state)
        }
        self.zones_undo_stack.append(state_snapshot)
        if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

    def capture_full_state_snapshot(self):
        return {
            "doc": copy.deepcopy(self.doc),
            "parametric_groups": copy.deepcopy(self.parametric_groups),
            "project_meta": copy.deepcopy(self.project_meta),
            "block_keep_state": copy.deepcopy(self.block_keep_state)
        }

    def record_action_snapshot(self):
        if self.is_loading_history:
            return
        self.global_recalc_undo_stack.append(self.capture_full_state_snapshot())
        if len(self.global_recalc_undo_stack) > 50:
            self.global_recalc_undo_stack.pop(0)
        self.global_recalc_redo_stack.clear()
        self.update_history_buttons_state()

    def restore_full_state_snapshot(self, snapshot):
        self.doc = copy.deepcopy(snapshot["doc"])
        self.parametric_groups = copy.deepcopy(snapshot["parametric_groups"])
        self.project_meta = copy.deepcopy(snapshot["project_meta"])
        self.block_keep_state = copy.deepcopy(snapshot["block_keep_state"])
        self.doc.saveas(self.dxf_path)
        self.save_project_config()
        self.save_original_geometries()
        self.update_dimension_inputs_from_meta()
        self.load_groups_into_list()
        self.load_entities_into_list()
        self.update_viewer()
        self.update_history_buttons_state()

    def push_to_history(self):
        self.history.save_state()
        self.history.clear_redo()
        self.save_zones_history_state()
        self.zones_redo_stack.clear()
        self.update_history_buttons_state()

    def undo(self):
        if self.history.undo() and len(self.zones_undo_stack) > 1:
            current_snapshot = self.zones_undo_stack.pop()
            self.zones_redo_stack.append(current_snapshot)
            previous_snapshot = self.zones_undo_stack[-1]
            
            restored_groups = copy.deepcopy(previous_snapshot["parametric_groups"])
            
            for rest_g in restored_groups:
                for cur_g in self.parametric_groups:
                    if rest_g["name"] == cur_g["name"]:
                        rest_g["k_w"] = cur_g.get("k_w", 0.0)
                        rest_g["k_h"] = cur_g.get("k_h", 0.0)
                        rest_g["growth_p_w"] = cur_g.get("growth_p_w", 0.0)
                        rest_g["growth_p_h"] = cur_g.get("growth_p_h", 0.0)
                        rest_g["growth_dir_x"] = cur_g.get("growth_dir_x", "Центр")
                        rest_g["growth_dir_y"] = cur_g.get("growth_dir_y", "Центр")
                        rest_g["link_x"] = cur_g.get("link_x", "X = W")
                        rest_g["link_y"] = cur_g.get("link_y", "Y = H")
                        break

            self.parametric_groups = restored_groups
            self.save_project_config()
            self.reload_after_history_change()

    def redo(self):
        if self.history.redo() and self.zones_redo_stack:
            next_snapshot = self.zones_redo_stack.pop()
            self.zones_undo_stack.append(next_snapshot)
            
            restored_groups = copy.deepcopy(next_snapshot["parametric_groups"])
            
            for rest_g in restored_groups:
                for cur_g in self.parametric_groups:
                    if rest_g["name"] == cur_g["name"]:
                        rest_g["k_w"] = cur_g.get("k_w", 0.0)
                        rest_g["k_h"] = cur_g.get("k_h", 0.0)
                        rest_g["growth_p_w"] = cur_g.get("growth_p_w", 0.0)
                        rest_g["growth_p_h"] = cur_g.get("growth_p_h", 0.0)
                        rest_g["growth_dir_x"] = cur_g.get("growth_dir_x", "Центр")
                        rest_g["growth_dir_y"] = cur_g.get("growth_dir_y", "Центр")
                        rest_g["link_x"] = cur_g.get("link_x", "X = W")
                        rest_g["link_y"] = cur_g.get("link_y", "Y = H")
                        break

            self.parametric_groups = restored_groups
            self.save_project_config()
            self.reload_after_history_change()

    def restore_state_snapshot(self, snapshot):
        self.parametric_groups = copy.deepcopy(snapshot["parametric_groups"])
        self.project_meta = copy.deepcopy(snapshot.get("project_meta", self.project_meta))
        self.block_keep_state = copy.deepcopy(snapshot.get("block_keep_state", self.block_keep_state))
        self.save_project_config()
        self.reload_after_history_change()

    def undo(self):
        if self.global_recalc_undo_stack:
            self.global_recalc_redo_stack.append(self.capture_full_state_snapshot())
            snapshot = self.global_recalc_undo_stack.pop()
            self.restore_full_state_snapshot(snapshot)
            return
        if self.history.undo() and len(self.zones_undo_stack) > 1:
            current_snapshot = self.zones_undo_stack.pop()
            self.zones_redo_stack.append(current_snapshot)
            self.restore_state_snapshot(self.zones_undo_stack[-1])

    def redo(self):
        if self.global_recalc_redo_stack:
            self.global_recalc_undo_stack.append(self.capture_full_state_snapshot())
            snapshot = self.global_recalc_redo_stack.pop()
            self.restore_full_state_snapshot(snapshot)
            return
        if self.history.redo() and self.zones_redo_stack:
            next_snapshot = self.zones_redo_stack.pop()
            self.zones_undo_stack.append(next_snapshot)
            self.restore_state_snapshot(next_snapshot)

    def set_interface_theme(self, theme_name):
        is_dark = theme_name == "Темна"
        if is_dark:
            self.setStyleSheet("""
                QMainWindow { background-color: #1e1e1e; }
                QWidget { color: #d4d4d4; font-size: 12px; }
                QScrollArea { border: none; background-color: #252526; }
                QGroupBox {
                    font-weight: bold; color: #4fc3f7; border: 1px solid #3c3c3c;
                    border-radius: 6px; margin-top: 15px; padding-top: 10px;
                }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
                QPushButton {
                    background-color: #333333; border: 1px solid #454545; color: #ffffff;
                    padding: 6px; border-radius: 4px;
                }
                QPushButton:hover { background-color: #454545; border-color: #007acc; }
                QPushButton:disabled { color: #777777; background-color: #252525; }
                QLineEdit, QComboBox {
                    background-color: #1e1e1e; border: 1px solid #3c3c3c;
                    color: #ffffff; padding: 4px; border-radius: 3px;
                }
                QListWidget {
                    background-color: #1e1e1e; color: #d4d4d4;
                    border: 1px solid #3c3c3c; border-radius: 4px;
                }
                QListWidget::item:selected { background-color: #0e639c; color: #ffffff; }
                QCheckBox { spacing: 6px; }
                QScrollBar:vertical { background: #252526; width: 12px; }
                QScrollBar::handle:vertical { background: #555555; border-radius: 5px; min-height: 24px; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #eef2f7; }
                QWidget { color: #1f2933; font-size: 12px; }
                QScrollArea { border: none; background-color: #f7f9fc; }
                QGroupBox {
                    background-color: #ffffff; font-weight: bold; color: #0b5cad;
                    border: 1px solid #cfd7e3; border-radius: 6px;
                    margin-top: 15px; padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin; left: 10px; padding: 0 4px;
                    background-color: #ffffff;
                }
                QPushButton {
                    background-color: #ffffff; border: 1px solid #b8c4d4; color: #1f2933;
                    padding: 6px; border-radius: 4px;
                }
                QPushButton:hover { background-color: #edf5ff; border-color: #0b5cad; }
                QPushButton:pressed { background-color: #dbeafe; }
                QPushButton:disabled { color: #9aa6b2; background-color: #edf0f4; }
                QLineEdit, QComboBox {
                    background-color: #ffffff; border: 1px solid #b8c4d4;
                    color: #111827; padding: 4px; border-radius: 3px;
                    selection-background-color: #bfdbfe;
                }
                QListWidget {
                    background-color: #ffffff; color: #1f2933;
                    border: 1px solid #cfd7e3; border-radius: 4px;
                    alternate-background-color: #f6f8fb;
                }
                QListWidget::item:selected { background-color: #dbeafe; color: #111827; }
                QCheckBox { spacing: 6px; }
                QCheckBox::indicator:checked { background-color: #0b5cad; border: 1px solid #0b5cad; }
                QScrollBar:vertical { background: #f1f5f9; width: 12px; }
                QScrollBar::handle:vertical { background: #b8c4d4; border-radius: 5px; min-height: 24px; }
            """)
        self.apply_theme_widget_overrides(is_dark)

    def apply_theme_widget_overrides(self, is_dark):
        styles = {
            "btn_open_file": (
                "background-color: #37474f; color: white; font-weight: bold; padding: 4px;",
                "background-color: #e8f1fb; color: #123f68; border: 1px solid #9cb7d5; font-weight: bold; padding: 4px;"
            ),
            "chk_enable_inspector": (
                "color: #ff9800; font-weight: bold;",
                "color: #9a5b00; font-weight: bold;"
            ),
            "btn_snap_zero": (
                "background-color: #00897b; color: white; font-weight: bold; padding: 6px;",
                "background-color: #e0f2f1; color: #005f56; border: 1px solid #7bbdb5; font-weight: bold; padding: 6px;"
            ),
            "transform_group": (
                "QGroupBox { border: 1px solid #d32f2f; }",
                "QGroupBox { background-color: #fff7f7; border: 1px solid #e2a8a8; color: #8a1f1f; }"
            ),
            "lbl_status_calc": (
                "color: #4fc3f7; font-size: 11px;",
                "color: #0b5cad; font-size: 11px;"
            ),
            "btn_apply_auto_scale": (
                "background-color: #007acc; color: white; font-weight: bold; padding: 6px;",
                "background-color: #0b5cad; color: white; border: 1px solid #084b8d; font-weight: bold; padding: 6px;"
            ),
            "btn_export_new_dxf": (
                "background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;",
                "background-color: #2e7d32; color: white; border: 1px solid #1f5d23; font-weight: bold; padding: 6px;"
            ),
            "btn_create_group": (
                "background-color: #673ab7; color: white; font-weight: bold;",
                "background-color: #ede7f6; color: #4527a0; border: 1px solid #b39ddb; font-weight: bold;"
            ),
            "btn_delete_from_dxf": (
                "background-color: #d32f2f; color: white; font-weight: bold;",
                "background-color: #fde8e8; color: #9b1c1c; border: 1px solid #f3aaaa; font-weight: bold;"
            ),
        }
        for attr_name, (dark_style, light_style) in styles.items():
            widget = getattr(self, attr_name, None)
            if widget is not None:
                widget.setStyleSheet(dark_style if is_dark else light_style)

    def on_scene_item_clicked(self, handle):
        modifiers = QGuiApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier):
            if handle in self.selected_handles: self.selected_handles.remove(handle)
            else: self.selected_handles.add(handle)
        else: self.selected_handles = {handle}
        self.sync_list_from_handles()
        self.update_viewer()

    def update_history_buttons_state(self):
        can_undo_history = len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1
        can_redo_history = len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0
        self.btn_undo.setEnabled(bool(self.global_recalc_undo_stack) or can_undo_history)
        self.btn_redo.setEnabled(bool(self.global_recalc_redo_stack) or can_redo_history)

    def reload_after_history_change(self):
        self.is_loading_history = True
        self.doc = ezdxf.readfile(self.dxf_path)
        self.save_original_geometries()
        self.update_dimension_inputs_from_meta()
        self.load_groups_into_list()
        self.load_entities_into_list()
        self.update_history_buttons_state()
        self.is_loading_history = False

    def scan_project_folder_for_dxf(self):
        self.file_explorer_list.blockSignals(True)
        self.file_explorer_list.clear()
        try:
            files = os.listdir(self.project_dir)
            dxf_files = [f for f in files if f.lower().endswith('.dxf')]
            for file_name in dxf_files:
                item = QListWidgetItem(f"📄 {file_name}")
                item.setData(Qt.ItemDataRole.UserRole, file_name)
                self.file_explorer_list.addItem(item)
                if file_name.lower() == os.path.basename(self.dxf_path).lower():
                    self.file_explorer_list.setCurrentItem(item)
        except Exception as e:
            print(f"Помилка провідника: {e}")
        self.file_explorer_list.blockSignals(False)

    def on_dxf_selection_changed_in_explorer(self):
        selected_items = self.file_explorer_list.selectedItems()
        if not selected_items: return
        self.selected_handles.clear()
        self.parametric_groups.clear()
        base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.dxf_path = os.path.join(self.project_dir, base_file_name)
        self.doc = ezdxf.readfile(self.dxf_path)

        if len(selected_items) > 1:
            for item in selected_items[1:]:
                addon_file_name = item.data(Qt.ItemDataRole.UserRole)
                addon_path = os.path.join(self.project_dir, addon_file_name)
                if os.path.exists(addon_path):
                    try:
                        addon_doc = ezdxf.readfile(addon_path)
                        importer = Importer(addon_doc, self.doc)
                        importer.import_modelspace()
                        importer.finalize()
                    except Exception as e: print(f"Помилка злиття: {e}")

        self.load_project_config()
        self.update_dimension_inputs_from_meta()
        self.history = HistoryManager(self.dxf_path)
        self.history.save_state()
        self.zones_undo_stack.clear()
        self.zones_redo_stack.clear()
        self.global_recalc_undo_stack.clear()
        self.global_recalc_redo_stack.clear()
        self.save_zones_history_state()
        self.save_original_geometries()
        self.update_viewer()
        self.load_entities_into_list()
        self.load_groups_into_list()
        self.load_block_filter_list()
        self.update_history_buttons_state()

    def process_manual_rubber_band(self, rect):
        modifiers = QGuiApplication.keyboardModifiers()
        if not (modifiers & Qt.ControlModifier):
            self.selected_handles.clear()
        path = QPainterPath()
        path.addRect(rect)
        for item in self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape):
            hndl = item.data(Qt.ItemDataRole.UserRole)
            if hndl: self.selected_handles.add(hndl)
        self.sync_list_from_handles()
        self.update_viewer()

    def sync_list_from_handles(self):
        self.entity_list.blockSignals(True)
        self.entity_list.clearSelection()
        for i in range(self.entity_list.count()):
            item = self.entity_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
        self.entity_list.blockSignals(False)

    def on_list_selection_changed(self):
        self.selected_handles.clear()
        for item in self.entity_list.selectedItems():
            self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
        self.update_viewer()

    def clear_selection(self):
        self.selected_handles.clear()
        self.update_viewer()
        self.entity_list.blockSignals(True)
        self.entity_list.clearSelection()
        self.entity_list.blockSignals(False)

    def on_theme_changed(self, theme_name):
        self.current_theme = theme_name
        self.set_interface_theme(theme_name)
        self.update_viewer()

    def load_entities_into_list(self):
        self.entity_list.blockSignals(True)
        self.entity_list.clear()
        seen = set()
        for entity in self.doc.modelspace():
            tp = entity.dxftype()
            hndl = entity.dxf.handle
            if tp == "CIRCLE":
                cx, cy, _ = entity.dxf.center
                if (round(cx, 1), round(cy, 1)) in seen: continue
                seen.add((round(cx, 1), round(cy, 1)))
                text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
            elif tp == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                if (round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)) in seen: continue
                seen.add((round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)))
                text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм. Початок: ({x1:.1f}, {y1:.1f}), Кінець: ({x2:.1f}, {y2:.1f})"
            elif tp == "ARC":
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                if (round(cx, 1), round(cy, 1), round(r, 1)) in seen: continue
                seen.add((round(cx, 1), round(cy, 1), round(r, 1)))
                text = f"🌙 Дуга (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}, R:{r:.1f}"
            elif tp == "TEXT":
                x, y, _ = entity.dxf.insert
                label = entity.dxf.text.strip() or "[рамка тексту]"
                text = f"Текст (ID: {hndl}) \"{label}\" X:{x:.1f}, Y:{y:.1f}, H:{entity.dxf.height:.1f}"
            else: continue
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, hndl)
            self.entity_list.addItem(item)
        self.entity_list.blockSignals(False)

    def update_viewer(self):
        items_to_remove = [item for item in self.scene.items() if item != self.coord_tooltip_item and item != self.coord_snap_marker]
        for item in items_to_remove:
            self.scene.removeItem(item)
            
        self.overlay_items.clear()

        if self.current_theme == "Темна":
            self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
            base_line_color = QColor(220, 220, 220)
        else:
            self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
            base_line_color = QColor(80, 80, 80)

        self.scene.addLine(-150, 0, 150, 0, QPen(QColor(33, 150, 243), 2))
        self.scene.addLine(0, 150, 0, -150, QPen(QColor(76, 175, 80), 2))

        for idx, group in enumerate(self.parametric_groups):
            g_min_x, g_max_x, g_min_y, g_max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
            for hndl in group["handles"]:
                if hndl not in self.doc.entitydb: continue
                e = self.doc.entitydb[hndl]
                if e.dxftype() in ("CIRCLE", "ARC"):
                    g_min_x = min(g_min_x, e.dxf.center[0] - e.dxf.radius)
                    g_max_x = max(g_max_x, e.dxf.center[0] + e.dxf.radius)
                    g_min_y = min(g_min_y, e.dxf.center[1] - e.dxf.radius)
                    g_max_y = max(g_max_y, e.dxf.center[1] + e.dxf.radius)
                elif e.dxftype() == "LINE":
                    g_min_x = min(g_min_x, e.dxf.start[0], e.dxf.end[0])
                    g_max_x = max(g_max_x, e.dxf.start[0], e.dxf.end[0])
                    g_min_y = min(g_min_y, e.dxf.start[1], e.dxf.end[1])
                    g_max_y = max(g_max_y, e.dxf.start[1], e.dxf.end[1])

            if g_min_x != float('inf'):
                rect_item = QGraphicsRectItem(g_min_x - 4, -(g_max_y + 4), (g_max_x - g_min_x) + 8, (g_max_y - g_min_y) + 8)
                rect_item.setBrush(QBrush(QColor(103, 58, 183, 20)))
                rect_item.setPen(QPen(QColor(103, 58, 183, 150), 1, Qt.PenStyle.DashLine))
                self.scene.addItem(rect_item)

        seen_circles, seen_lines, seen_arcs = set(), set(), set()

        for entity in self.doc.modelspace():
            hndl = entity.dxf.handle
            tp = entity.dxftype()
            pyqt_item = None
            
            if tp == "CIRCLE":
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                if (round(cx, 2), round(cy, 2)) in seen_circles: continue
                seen_circles.add((round(cx, 2), round(cy, 2)))
                pyqt_item = SelectableCircle(
                    cx - r,
                    -cy - r,
                    r * 2,
                    r * 2,
                    entity
                )
            elif tp == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
                seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                pyqt_item = SelectableLine(
                    x1, -y1,
                    x2, -y2,
                    entity
                )

            elif tp == "ARC":
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                sa = entity.dxf.start_angle
                ea = entity.dxf.end_angle
                if (round(cx, 2), round(cy, 2), round(sa, 2)) in seen_arcs: continue
                seen_arcs.add((round(cx, 2), round(cy, 2), round(sa, 2)))
                pyqt_item = SelectableArc(
                    QPointF(cx, -cy),
                    r,
                    sa,
                    ea,
                    entity
                )

            elif tp == "TEXT":
                settings = self.get_text_settings()
                display_text = self.text_display_value(settings.get("text", entity.dxf.text))
                if settings.get("handle") == hndl:
                    box_x = float(settings.get("x", 0.0))
                    box_y = float(settings.get("y", 0.0))
                    box_w = self.text_box_width(settings)
                    box_h = self.text_box_height(settings)
                    pyqt_item = DraggableDoorTextBoxItem(
                        0,
                        0,
                        box_w,
                        box_h,
                        self,
                        hndl
                    )
                    pyqt_item.setPos(box_x, -box_y - box_h)
                    pyqt_item.setBrush(QBrush(QColor(0, 120, 255, 55)))
                    pyqt_item.setPen(QPen(QColor(0, 120, 255), 1.5, Qt.PenStyle.DashLine))
                    pyqt_item.setTransformOriginPoint(box_w * 0.5, box_h * 0.5)
                    pyqt_item.setRotation(-float(settings.get("rotation", 0.0)))
                    self.scene.addItem(pyqt_item)
                    self.add_centered_text_preview(
                        pyqt_item,
                        display_text,
                        box_w,
                        box_h,
                        str(settings.get("font", "STANDARD"))
                    )
                else:
                    x, y, _ = entity.dxf.insert
                    display_text = entity.dxf.text.strip()
                    pyqt_item = self.scene.addText(display_text)
                    pyqt_item.setDefaultTextColor(QColor(0, 120, 255) if hndl in self.selected_handles else base_line_color)
                    font = pyqt_item.font()
                    font.setPointSizeF(max(float(entity.dxf.height), 1.0))
                    pyqt_item.setFont(font)
                    pyqt_item.setPos(x, -y - float(entity.dxf.height))
                    pyqt_item.setRotation(-float(getattr(entity.dxf, "rotation", 0.0)))
                    pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
                    pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
                pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
                self.overlay_items[hndl] = pyqt_item
                continue

            if pyqt_item:
                pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
                pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
                
                if hndl in self.selected_handles:
                    pen_style = QPen(QColor(0, 120, 255), 2.5) 
                else:
                    in_group = False
                    for group in self.parametric_groups:
                        if hndl in group["handles"]:
                            group_key = self.get_group_key(group)
                            if self.block_keep_state.get(group_key, True):
                                pen_style = QPen(QColor(76, 175, 80), 2)
                            else:
                                pen_style = QPen(QColor(211, 47, 47), 2)
                            in_group = True
                            break
                    if not in_group: pen_style = QPen(base_line_color, 1.5)
                
                pyqt_item.setPen(pen_style)
                pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
                self.scene.addItem(pyqt_item)
                self.overlay_items[hndl] = pyqt_item

        settings = self.get_text_settings()
        if settings.get("enabled") and not settings.get("handle"):
            box_x = float(settings.get("x", 0.0))
            box_y = float(settings.get("y", 0.0))
            box_w = self.text_box_width(settings)
            box_h = self.text_box_height(settings)
            box_item = DraggableDoorTextBoxItem(0, 0, box_w, box_h, self)
            box_item.setPos(box_x, -box_y - box_h)
            box_item.setBrush(QBrush(QColor(0, 120, 255, 55)))
            box_item.setPen(QPen(QColor(0, 120, 255), 1.5, Qt.PenStyle.DashLine))
            box_item.setTransformOriginPoint(box_w * 0.5, box_h * 0.5)
            box_item.setRotation(-float(settings.get("rotation", 0.0)))
            self.scene.addItem(box_item)
            display_text = self.text_display_value(settings.get("text", ""))
            self.add_centered_text_preview(
                box_item,
                display_text,
                box_w,
                box_h,
                str(settings.get("font", "STANDARD"))
            )

        self.view.setSceneRect(self.scene.itemsBoundingRect())


if __name__ == "__main__":
    import PySide6.QtWidgets as qtw
    app = qtw.QApplication(sys.argv)
    window = MiniCAD()
    window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
    window.show()
    sys.exit(app.exec())
