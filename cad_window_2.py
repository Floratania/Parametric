import os
import sys
import math
import copy
import json

import ezdxf
import ezdxf.bbox as dxf_bbox
from ezdxf.math import Matrix44
from ezdxf.addons.importer import Importer 

from PySide6.QtWidgets import (
    QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView, 
    QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem, QInputDialog, QFileDialog,
    QGridLayout
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


# --- МОДУЛЬ ПАРАМЕТРИЧНОГО РУХУ ---
class ParametricEngine:
    @staticmethod
    def get_transform(delta_w, delta_h, group):
        # Визначаємо, яка дельта (ΔW чи ΔH) керує локальними вісями X та Y
        val_x = delta_w if "W" in group.get("link_x", "W") else delta_h
        val_y = delta_h if "H" in group.get("link_y", "H") else delta_w

        # Розраховуємо ЛОКАЛЬНЕ зміщення та ріст
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

        self.zones_undo_stack = []
        self.zones_redo_stack = []

        self.coord_tooltip_item = None
        self.coord_snap_marker = None

        self.load_doc_safely()
        self.load_project_config()
        
        self.history = HistoryManager(self.dxf_path)
        self.history.save_state()
        self.save_zones_history_state()

        self.init_ui()
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

    def load_project_config(self):
        # Динамічно формуємо ім'я JSON-файлу на основі імені поточного DXF
        base_path = os.path.splitext(self.dxf_path)[0]
        config_path = f"{base_path}_config.json"
        
        self.parametric_groups.clear()
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for g in data:
                        g["handles"] = set(g.get("handles", []))
                        
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

    def save_project_config(self):
        # Динамічно формуємо ім'я JSON-файлу на основі імені поточного DXF
        base_path = os.path.splitext(self.dxf_path)[0]
        config_path = f"{base_path}_config.json"
        
        data = []
        for g in self.parametric_groups:
            g_data = g.copy()
            g_data["handles"] = list(g["handles"])
            data.append(g_data)
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

        transform_group = QGroupBox("🔄 Трансформація виділених елементів (DXF)")
        transform_group.setStyleSheet("QGroupBox { border: 1px solid #d32f2f; }")
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
        self.btn_mirror_h = QPushButton("Дзеркало ↔ (Гориз)")
        self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
        mirror_btn_layout.addWidget(self.btn_mirror_h)

        self.btn_mirror_v = QPushButton("Дзеркало ↕ (Верт)")
        self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
        mirror_btn_layout.addWidget(self.btn_mirror_v)
        transform_box.addLayout(mirror_btn_layout)

        transform_group.setLayout(transform_box)
        control_panel_layout.addWidget(transform_group)

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
        self.btn_apply_auto_scale.clicked.connect(self.process_parametric_percentage_scale)
        auto_scale_box.addWidget(self.btn_apply_auto_scale)

        auto_scale_group.setLayout(auto_scale_box)
        control_panel_layout.addWidget(auto_scale_group)

        history_group = QGroupBox("Конструкторська історія")
        history_box = QHBoxLayout()
        self.btn_undo = QPushButton("Скасувати")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_redo = QPushButton("Повторити")
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
                
                self.load_project_config()
                
                self.history = HistoryManager(self.dxf_path)
                self.history.save_state()
                self.save_zones_history_state()
                self.save_original_geometries()
                
                self.scan_project_folder_for_dxf()
                self.update_viewer()
                self.load_entities_into_list()
                self.load_groups_into_list()
                self.update_history_buttons_state()
                
            except Exception as e:
                print(f"Помилка при відкритті файлу: {e}")

    def transform_selected_entities(self, mode):
        if not self.selected_handles: return
        selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
        if not selected_entities: return

        cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
        cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

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
                m1 = Matrix44.translate(-cx, -cy, 0)
                m2 = Matrix44.scale(-1, 1, 1)
                m3 = Matrix44.translate(cx, cy, 0)
                m = m1 @ m2 @ m3
            elif mode == "MIRROR_V":
                m1 = Matrix44.translate(-cx, -cy, 0)
                m2 = Matrix44.scale(1, -1, 1)
                m3 = Matrix44.translate(cx, cy, 0)
                m = m1 @ m2 @ m3
            else: 
                continue
            entity.transform(m)

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
        self.update_viewer()
        self.load_entities_into_list()

    def snap_to_zero(self):
        min_x, min_y = float('inf'), float('inf')
        for orig in self.original_geometries.values():
            if orig["type"] in ("CIRCLE", "ARC"):
                min_x = min(min_x, orig["center"][0] - orig["radius"])
                min_y = min(min_y, orig["center"][1] - orig["radius"])
            elif orig["type"] == "LINE":
                min_x = min(min_x, orig["start"][0], orig["end"][0])
                min_y = min(min_y, orig["start"][1], orig["end"][1])
                
        if min_x == float('inf') or min_y == float('inf'):
            return 
            
        shift_x = -min_x
        shift_y = -min_y
        
        for orig in self.original_geometries.values():
            if orig["type"] == "LINE":
                sz = orig["start"][2] if len(orig["start"]) > 2 else 0
                ez = orig["end"][2] if len(orig["end"]) > 2 else 0
                orig["start"] = (orig["start"][0] + shift_x, orig["start"][1] + shift_y, sz)
                orig["end"] = (orig["end"][0] + shift_x, orig["end"][1] + shift_y, ez)
            elif orig["type"] in ("CIRCLE", "ARC"):
                cz = orig["center"][2] if len(orig["center"]) > 2 else 0
                orig["center"] = (orig["center"][0] + shift_x, orig["center"][1] + shift_y, cz)

        self.push_to_history()
        self.process_parametric_percentage_scale()

    def delete_entities_from_dxf(self):
        if not self.selected_handles:
            return

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
            
        name, ok = QInputDialog.getText(self, "Нова група", "Введіть назву групи:")
        if not ok or not name.strip():
            name = f"Група {len(self.parametric_groups) + 1}"

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
        self.parametric_groups.append(new_group)
        self.clear_selection()
        self.push_to_history()
        self.save_project_config()
        self.load_groups_into_list()
        self.update_viewer()

    def disband_parametric_group(self):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
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
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["k_w"] = parse_factor(text)
        self.save_project_config()

    def on_combo_k_h_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["k_h"] = parse_factor(text)
        self.save_project_config()

    def on_combo_growth_p_w_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_p_w"] = parse_factor(text)
        self.save_project_config()

    def on_combo_growth_p_h_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_p_h"] = parse_factor(text)
        self.save_project_config()

    def on_link_x_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["link_x"] = text
        self.save_project_config()

    def on_link_y_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["link_y"] = text
        self.save_project_config()

    def on_growth_dir_x_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_dir_x"] = text
        self.save_project_config()

    def on_growth_dir_y_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["growth_dir_y"] = text
        self.save_project_config()

    def process_parametric_percentage_scale(self):
        try:
            cur_w = float(self.input_current_width.text().strip())
            target_w = float(self.input_target_width.text().strip())
            cur_h = float(self.input_current_height.text().strip())
            target_h = float(self.input_target_height.text().strip())
        except ValueError:
            return

        delta_w = target_w - cur_w
        delta_h = target_h - cur_h

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

        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔW={delta_w:+.1f} мм | ΔH={delta_h:+.1f} мм</font>")
        self.doc.saveas(self.dxf_path)
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

    def save_zones_history_state(self):
        state_snapshot = {
            "parametric_groups": copy.deepcopy(self.parametric_groups)
        }
        self.zones_undo_stack.append(state_snapshot)
        if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

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

    def set_interface_theme(self, theme_name):
        if theme_name == "Темна":
            self.setStyleSheet("QMainWindow { background-color: #1e1e1e; padding: 10 px;} QWidget { color: #d4d4d4; font-size: 12px; padding: 12 px;} QScrollArea { border: none; background-color: #252526; } QGroupBox { font-weight: bold; color: #007acc; border: 1px solid #3c3c3c; border-radius: 6px; margin-top: 15px; } QPushButton { background-color: #333333; border: 1px solid #454545; color: #ffffff; padding: 6px; border-radius: 4px; } QPushButton:hover { background-color: #454545; border-color: #007acc; } QLineEdit { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #ffffff; padding: 4px; } QListWidget { background-color: #1e1e1e; color: #d4d4d4; } QComboBox { background-color: #1e1e1e; color: #ffffff; border: 1px solid #3c3c3c; padding: 2px; }")
        else:
            self.setStyleSheet("QMainWindow { background-color: #f3f3f3; } QWidget { color: #242424; font-size: 12px; } QScrollArea { border: none; background-color: #ffffff; } QGroupBox { font-weight: bold; color: #005fb8; border: 1px solid #d2d2d2; border-radius: 6px; margin-top: 15px; } QPushButton { background-color: #fbfbfb; border: 1px solid #cccccc; color: #242424; padding: 6px; border-radius: 4px; } QPushButton:hover { background-color: #f5f5f5; border-color: #005fb8; } QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; padding: 4px; } QListWidget { background-color: #ffffff; color: #242424; } QComboBox { background-color: #ffffff; color: #000000; border: 1px solid #cccccc; padding: 2px; }")

    def on_scene_item_clicked(self, handle):
        modifiers = QGuiApplication.keyboardModifiers()
        if (modifiers & Qt.ControlModifier):
            if handle in self.selected_handles: self.selected_handles.remove(handle)
            else: self.selected_handles.add(handle)
        else: self.selected_handles = {handle}
        self.sync_list_from_handles()
        self.update_viewer()

    def update_history_buttons_state(self):
        self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
        self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

    def reload_after_history_change(self):
        self.is_loading_history = True
        self.doc = ezdxf.readfile(self.dxf_path)
        self.save_original_geometries()
        self.process_parametric_percentage_scale()
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
        self.history = HistoryManager(self.dxf_path)
        self.history.save_state()
        self.zones_undo_stack.clear()
        self.zones_redo_stack.clear()
        self.save_zones_history_state()
        self.save_original_geometries()
        self.update_viewer()
        self.load_entities_into_list()
        self.load_groups_into_list()
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

            if pyqt_item:
                pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
                pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
                
                if hndl in self.selected_handles:
                    pen_style = QPen(QColor(0, 120, 255), 2.5) 
                else:
                    in_group = False
                    for group in self.parametric_groups:
                        if hndl in group["handles"]:
                            pen_style = QPen(QColor(103, 58, 183), 2) 
                            in_group = True
                            break
                    if not in_group: pen_style = QPen(base_line_color, 1.5)
                
                pyqt_item.setPen(pen_style)
                pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
                self.scene.addItem(pyqt_item)
                self.overlay_items[hndl] = pyqt_item

        self.view.setSceneRect(self.scene.itemsBoundingRect())


if __name__ == "__main__":
    import PySide6.QtWidgets as qtw
    app = qtw.QApplication(sys.argv)
    window = MiniCAD()
    window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
    window.show()
    sys.exit(app.exec())