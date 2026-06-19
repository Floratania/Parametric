# # import os
# # import sys
# # import math
# # import copy
# # import json
# # import csv
# # import re
# # import zipfile
# # import xml.etree.ElementTree as ET
# # from PySide6.QtGui import QShortcut, QKeySequence
# # from parametric_db_new import LoginDialog, ParametricDb
# # import table_io

# # import ezdxf
# # import ezdxf.bbox as dxf_bbox
# # from ezdxf.enums import TextEntityAlignment
# # from ezdxf.math import Matrix44
# # from ezdxf.addons.importer import Importer 

# # from PySide6.QtWidgets import (
# #     QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# #     QListWidget, QListWidgetItem, QPushButton, QCheckBox,
# #     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView, 
# #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem, QInputDialog, QFileDialog, QMessageBox,
# #     QGridLayout, QGraphicsTextItem, QGraphicsSimpleTextItem, QGraphicsItem, QTabWidget, QSizePolicy
# # )
# # from PySide6.QtCore import QPointF, Qt
# # from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath, QPainter, QGuiApplication


# # try:
# #     from graphics_items import SelectableCircle, SelectableLine, SelectableArc
# #     from graphics_view import AdvancedGraphicsView
# #     from history_manager import HistoryManager
# # except ImportError:
# #     AdvancedGraphicsView = QGraphicsView
# #     class HistoryManager:
# #         def __init__(self, p): self.p = p; self.undo_stack=[1]; self.redo_stack=[]
# #         def save_state(self): pass
# #         def clear_redo(self): pass
# #         def undo(self): return True
# #         def redo(self): return True


# # def patch_ezdxf_entities():
# #     from ezdxf.entities import Line, Circle, Arc
    
# #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# #     Arc.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# #     Arc.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# #     Arc.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# #     Arc.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # patch_ezdxf_entities()


# # def parse_factor(text):
# #     text = str(text).strip().upper()
    
  
# #     if '(' in text:
# #         text = text.split('(')[0].strip()
        
# #     if not text:
# #         return 0.0

# #     if text.endswith("%"):
# #         try: return float(text[:-1].replace(',', '.')) / 100.0
# #         except: return 0.0

# #     if text.startswith("Δ/") or text.startswith("D/"):
# #         try:
# #             div = float(text[2:].replace(',', '.'))
# #             return 0.0 if div == 0 else 1.0 / div
# #         except: return 0.0

# #     if "/" in text: 
# #         try:
# #             parts = text.split("/")
# #             return float(parts[0]) / float(parts[1])
# #         except: return 0.0

# #     try:
# #         val = float(text.replace(',', '.'))
# #         if val > 1.0: 
# #             return val / 100.0
# #         return val
# #     except:
# #         return 0.0

# # def format_factor(val):
# #     """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
# #     if abs(val - 0.0) < 0.001: return "0% (Фіксовано)"
# #     if abs(val - 0.25) < 0.001: return "25% (Δ/4)"
# #     if abs(val - 0.333) < 0.01: return "33.3% (Δ/3)"
# #     if abs(val - 0.5) < 0.001: return "50% (Δ/2)"
# #     if abs(val - 0.667) < 0.01: return "66.7% (2Δ/3)"
# #     if abs(val - 0.75) < 0.01: return "75% (3Δ/4)"
# #     if abs(val - 1.0) < 0.001: return "100% (Δ)"
# #     return f"{val*100:g}%"


# # class DraggableDoorTextItem(QGraphicsTextItem):
# #     def __init__(self, text, owner):
# #         super().__init__(text)
# #         self.owner = owner
# #         self.setFlags(
# #             QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
# #             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
# #         )

# #     def mouseReleaseEvent(self, event):
# #         super().mouseReleaseEvent(event)
# #         self.owner.on_door_text_item_moved(self)


# # class DraggableDxfTextItem(QGraphicsTextItem):
# #     def __init__(self, text, owner, handle, entity_type="TEXT"):
# #         super().__init__(text)
# #         self.owner = owner
# #         self.handle = handle
# #         self.entity_type = entity_type
# #         self.setFlags(
# #             QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
# #             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
# #         )
# #         self.setCursor(Qt.CursorShape.OpenHandCursor)

# #     def mousePressEvent(self, event):
# #         if self.handle:
# #             self.owner.selected_handles = {self.handle}
# #             self.owner.sync_list_from_handles()
# #         self.setCursor(Qt.CursorShape.ClosedHandCursor)
# #         super().mousePressEvent(event)

# #     def mouseReleaseEvent(self, event):
# #         super().mouseReleaseEvent(event)
# #         self.setCursor(Qt.CursorShape.OpenHandCursor)
# #         self.owner.on_existing_dxf_text_moved(self)


# # class DraggableDoorTextBoxItem(QGraphicsRectItem):
# #     def __init__(self, x, y, width, height, owner, handle=None):
# #         super().__init__(x, y, width, height)
# #         self.owner = owner
# #         self.handle = handle
# #         self.setFlags(
# #             QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
# #             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
# #         )
# #         self.setCursor(Qt.CursorShape.OpenHandCursor)

# #     def mousePressEvent(self, event):
# #         if self.handle:
# #             self.owner.selected_handles = {self.handle}
# #             self.owner.sync_list_from_handles()
# #         self.setCursor(Qt.CursorShape.ClosedHandCursor)
# #         super().mousePressEvent(event)

# #     def mouseReleaseEvent(self, event):
# #         super().mouseReleaseEvent(event)
# #         self.setCursor(Qt.CursorShape.OpenHandCursor)
# #         self.owner.on_door_text_box_moved(self)


# # # --- МОДУЛЬ ПАРАМЕТРИЧНОГО РУХУ ---
# # class ParametricEngine:
# #     @staticmethod
# #     def signed_shift(value, direction, positive_name, negative_name):
# #         """Повертає зсув з урахуванням напрямку.

# #         Раніше зсув завжди додавався як +X/+Y. Через це після ROT180 або дзеркала
# #         група могла рости в правильний бік, але вся база групи все одно їхала вправо/вгору.
# #         """
# #         direction = str(direction or positive_name)
# #         if direction == negative_name:
# #             return -value
# #         return value

# #     @staticmethod
# #     def get_transform(delta_w, delta_h, group):
# #         val_x = delta_w if "W" in group.get("link_x", "W") else delta_h
# #         val_y = delta_h if "H" in group.get("link_y", "H") else delta_w

# #         raw_shift_x = val_x * group.get("k_w", 0.0)
# #         raw_shift_y = val_y * group.get("k_h", 0.0)

# #         shift_x = ParametricEngine.signed_shift(
# #             raw_shift_x,
# #             group.get("shift_dir_x", "Вправо"),
# #             "Вправо",
# #             "Вліво"
# #         )
# #         shift_y = ParametricEngine.signed_shift(
# #             raw_shift_y,
# #             group.get("shift_dir_y", "Вгору"),
# #             "Вгору",
# #             "Вниз"
# #         )

# #         growth_x = val_x * group.get("growth_p_w", 0.0)
# #         growth_y = val_y * group.get("growth_p_h", 0.0)

# #         return (shift_x, shift_y, 0), (growth_x, growth_y, 0)


# # class MiniCAD(QMainWindow):
# #     def __init__(self):
# #         super().__init__()

# #         self.setWindowTitle("Параметризатор")
# #         self.setGeometry(100, 100, 1600, 950)

# #         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
# #         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
# #         self.debug_output = False
# #         self.db = ParametricDb()
# #         self.current_user = None
# #         self.current_theme = "Темна"
# #         self.current_project_file_id = None
# #         self.current_door_model_id = None

# #         self.selected_handles = set()
# #         self.overlay_items = {}
# #         self.original_geometries = {}
# #         self.is_loading_history = False

# #         self.parametric_groups = [] 
# #         self.folder_meta = self.default_folder_meta()
# #         self.project_meta = {
# #             "source_width": None,
# #             "source_height": None,
# #             "target_width": None,
# #             "target_height": None,
# #             "keep_blocks": [],
# #             "delete_blocks": [],
# #             "door_opening": "left",
# #             "source_door_opening": "left",
# #             "target_door_opening": "left",
# #             "growth_axis": "both",
# #             "axis_link_mode": "normal",
# #             "door_text": {
# #                 "enabled": False,
# #                 "text": "",
# #                 "x": 0.0,
# #                 "y": 0.0,
# #                 "height": 30.0,
# #                 "width_factor": 120.0,
# #                 "rotation": 0.0,
# #                 "font": "STANDARD",
# #                 "handle": None
# #             }
# #         }
# #         self.block_keep_state = {}

# #         self.zones_undo_stack = []
# #         self.zones_redo_stack = []
# #         self.global_recalc_undo_stack = []
# #         self.global_recalc_redo_stack = []

# #         self.coord_tooltip_item = None
# #         self.coord_snap_marker = None

# #         self.load_doc_safely()
# #         self.load_project_config()
        
# #         self.history = HistoryManager(self.dxf_path)
# #         self.history.save_state()
# #         self.save_zones_history_state()

# #         self.init_ui()
# #         if not self.authenticate_user():
# #             sys.exit(0)
# #         self.setup_shortcuts()
# #         self.update_dimension_inputs_from_meta()
# #         self.set_interface_theme(self.current_theme)
# #         self.save_original_geometries()
# #         self.update_viewer()
# #         self.load_entities_into_list()
# #         self.load_groups_into_list()
# #         self.scan_project_folder_for_dxf()

# #     def load_doc_safely(self):
# #         if os.path.exists(self.dxf_path):
# #             try:
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #             except Exception as e:
# #                 print(f"Помилка читання файлу: {e}")
# #                 self.doc = ezdxf.new()
# #                 self.doc.saveas(self.dxf_path)
# #         else:
# #             dxf_files = [f for f in os.listdir(self.project_dir) if f.lower().endswith('.dxf')]
# #             if dxf_files:
# #                 self.dxf_path = os.path.join(self.project_dir, dxf_files[0])
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #             else:
# #                 self.doc = ezdxf.new()
# #                 self.doc.saveas(self.dxf_path)

# #     def get_project_config_path(self):
# #         base_path = os.path.splitext(self.dxf_path)[0]
# #         return f"{base_path}_config.json"

# #     def get_folder_config_path(self):
# #         return os.path.join(self.project_dir, "_folder_params.json")

# #     def default_folder_meta(self):
# #         return {
# #             "source_width": None,
# #             "source_height": None,
# #             "target_width": None,
# #             "target_height": None,
# #             "source_door_opening": None
# #         }

# #     def load_folder_config(self):
# #         """JSON папки більше не є джерелом правди. Залишено як no-op для сумісності."""
# #         self.folder_meta = self.default_folder_meta()

# #     def save_folder_config(self):
# #         """Не пишемо _folder_params.json. Дані зберігаються в MSSQL."""
# #         return

# #     def apply_folder_dimensions_to_meta(self):
# #         for key in ("source_width", "source_height", "target_width", "target_height"):
# #             value = self.folder_meta.get(key)
# #             if value is not None:
# #                 self.project_meta[key] = value
# #         if self.folder_meta.get("source_door_opening"):
# #             self.project_meta["source_door_opening"] = self.folder_meta["source_door_opening"]

# #     def update_folder_dimensions_from_meta(self):
# #         changed = False
# #         for key in ("source_width", "source_height", "target_width", "target_height"):
# #             value = self.project_meta.get(key)
# #             if value is not None and self.folder_meta.get(key) != value:
# #                 self.folder_meta[key] = value
# #                 changed = True
# #         opening = self.project_meta.get("source_door_opening")
# #         if opening and self.folder_meta.get("source_door_opening") != opening:
# #             self.folder_meta["source_door_opening"] = opening
# #             changed = True
# #         if changed:
# #             self.save_folder_config()

# #     def default_project_meta(self):
# #         return {
# #             "source_width": None,
# #             "source_height": None,
# #             "target_width": None,
# #             "target_height": None,
# #             "keep_blocks": [],
# #             "delete_blocks": [],
# #             "door_opening": "left",
# #             "source_door_opening": "left",
# #             "target_door_opening": "left",
# #             "growth_axis": "both",
# #             "axis_link_mode": "normal",
# #             "door_text": self.default_text_settings()
# #         }

# #     def default_text_settings(self):
# #         return {
# #             "enabled": False,
# #             "text": "",
# #             "x": 0.0,
# #             "y": 0.0,
# #             "height": 30.0,
# #             "width_factor": 120.0,
# #             "rotation": 0.0,
# #             "font": "STANDARD",
# #             "handle": None
# #         }

# #     def get_group_key(self, group):
# #         if not group.get("uid"):
# #             handles_key = ",".join(sorted(str(h) for h in group.get("handles", [])))
# #             group["uid"] = f"{group.get('name', 'group')}|{handles_key}"
# #         return group["uid"]

# #     def authenticate_user(self):
 
# #         if hasattr(self.db, "_check_connection"):
# #             self.db._check_connection()

       
# #         if not self.db.available:
# #             message = (
# #                 "⚠️ <font color='#ff9800'><b>Увага: Немає зв'язку з SQL-сервером!</b></font><br><br>"
# #                 f"Помилка: {self.db.last_error}<br><br>"
# #                 "Введіть логін/пароль для спроби локального входу або перевірте підключення."
# #             )
# #         else:
# #             message = "Вхід"

      
# #         while True:
# #             dialog = LoginDialog(self, message)
# #             if dialog.exec() != LoginDialog.DialogCode.Accepted:
               
# #                 return False
            
# #             username, password = dialog.credentials()
            
        
# #             if not self.db.available:
# #                 QMessageBox.critical(
# #                     self, 
# #                     "Помилка підключення", 
# #                     f"Неможливо авторизуватись, оскільки SQL-сервер недоступний.\n\nДеталі помилки:\n{self.db.last_error}"
# #                 )
# #                 continue

# #             try:
# #                 user = self.db.authenticate(username, password)
# #             except Exception as exc:
# #                 QMessageBox.warning(self, "База даних", f"Помилка авторизації:\n{exc}")
# #                 return False

# #             if user:
# #                 self.current_user = user
# #                 self.setWindowTitle(f"{self.windowTitle()} | {user.get('username')}")
# #                 if hasattr(self, "lbl_status_calc"):
# #                     self.lbl_status_calc.setText(
# #                         f"<font color='#a5d6a7'>БД підключена. Користувач: {user.get('username')}</font>"
# #                     )
# #                 self.save_current_project_to_db("Opened")
# #                 self.register_current_folder_model(show_errors=False)
# #                 self.update_file_status_panel()
# #                 return True
                
# #             QMessageBox.warning(self, "Авторизація", "Невірний логін або пароль.")


# #     def current_user_id(self):
# #         if not self.current_user:
# #             return None
# #         return self.current_user.get("id")

# #     def save_current_project_to_db(self, status="ConfigSaved"):
# #         if not getattr(self, "db", None) or not self.current_user_id():
# #             return

# #         project_file_id = self.db.save_project_snapshot(
# #             self.project_dir,
# #             self.dxf_path,
# #             self.project_meta,
# #             self.parametric_groups,
# #             self.block_keep_state,
# #             self.current_user_id(),
# #             status,
# #             getattr(self, "current_project_file_id", None),
# #             getattr(self, "current_door_model_id", None),
# #         )

# #         if project_file_id:
# #             self.current_project_file_id = project_file_id
# #             loaded = self.db.load_project_config(
# #                 dxf_path=self.dxf_path,
# #                 project_file_id=project_file_id,
# #                 door_model_id=getattr(self, "current_door_model_id", None),
# #             )
# #             if loaded and loaded.get("door_model_id"):
# #                 self.current_door_model_id = loaded.get("door_model_id")
# #             self.register_current_folder_model(show_errors=False)
# #             if hasattr(self, "lbl_status_calc"):
# #                 self.lbl_status_calc.setText("<font color='#a5d6a7'>Проєкт/модель збережено в MSSQL.</font>")
# #         elif hasattr(self, "lbl_status_calc"):
# #             self.lbl_status_calc.setText(
# #                 f"<font color='#ff9800'>БД не прийняла запис: {self.db.last_error}</font>"
# #             )

# #     def register_current_folder_model(self, show_errors=True):
# #         """One folder = one DoorModel. Register all DXF files in this folder under the same model."""
# #         if not getattr(self, "db", None) or not self.current_user_id():
# #             return None
# #         door_model_id = self.db.register_folder_dxf_files(
# #             self.project_dir,
# #             self.project_meta,
# #             self.current_user_id(),
# #             getattr(self, "current_door_model_id", None),
# #         )
# #         if door_model_id:
# #             self.current_door_model_id = door_model_id
# #             return door_model_id
# #         if show_errors and hasattr(self, "lbl_status_calc"):
# #             self.lbl_status_calc.setText(f"<font color='#ff9800'>Не вдалося зареєструвати папку як модель: {self.db.last_error}</font>")
# #         return None

# #     def save_export_to_db(self, export_path, status="Exported"):
# #         if not getattr(self, "db", None) or not self.current_user_id():
# #             return
# #         if not getattr(self, "current_project_file_id", None):
# #             self.save_current_project_to_db("BeforeExport")
# #         if not getattr(self, "current_project_file_id", None):
# #             return

# #         self.db.save_export_file(
# #             self.current_project_file_id,
# #             export_path,
# #             self.project_meta.get("target_width"),
# #             self.project_meta.get("target_height"),
# #             self.export_target_opening(),
# #             self.current_user_id(),
# #             getattr(self, "current_door_model_id", None),
# #         )

# #     def select_all_entities(self):
# #         self.selected_handles.clear()

# #         for i in range(self.entity_list.count()):
# #             item = self.entity_list.item(i)
# #             handle = item.data(Qt.UserRole)

# #             if handle is None:
# #                 continue

# #             self.selected_handles.add(str(handle))
# #             item.setSelected(True)

# #         self.update_viewer()
# #         # self.sync_entity_list_selection()


# #     def clear_selection(self):
# #         self.selected_handles.clear()
# #         self.entity_list.clearSelection()
# #         self.group_list_widget.clearSelection()
# #         self.update_viewer()


# #     def zoom_extents(self):
# #         self.view.fitInView(
# #             self.scene.itemsBoundingRect(),
# #             Qt.KeepAspectRatio
# #         )

# #     def load_project_config(self):
# #         """Основне завантаження з MSSQL. JSON читається тільки як fallback для міграції старих файлів."""
# #         self.parametric_groups.clear()
# #         self.project_meta = self.default_project_meta()
# #         self.block_keep_state = {}

# #         loaded = None
# #         if getattr(self, "db", None) and getattr(self.db, "available", False):
# #             loaded = self.db.load_project_config(
# #                 dxf_path=self.dxf_path,
# #                 project_file_id=getattr(self, "current_project_file_id", None),
# #                 door_model_id=getattr(self, "current_door_model_id", None),
# #             )

# #         if loaded:
# #             self.current_project_file_id = loaded.get("project_file_id")
# #             if loaded.get("door_model_id"):
# #                 self.current_door_model_id = loaded.get("door_model_id")
# #             self.project_meta.update(loaded.get("meta") or {})
# #             text_settings = self.default_text_settings()
# #             text_settings.update(self.project_meta.get("door_text") or {})
# #             self.project_meta["door_text"] = text_settings
# #             self.parametric_groups = loaded.get("groups") or []
# #             self.block_keep_state = loaded.get("block_keep_state") or {}
# #         else:
# #             # Тільки для першого перенесення зі старого JSON у БД.
# #             config_path = self.get_project_config_path()
# #             if os.path.exists(config_path):
# #                 try:
# #                     with open(config_path, "r", encoding="utf-8") as f:
# #                         raw_data = json.load(f)
# #                     if isinstance(raw_data, dict):
# #                         self.project_meta.update(raw_data.get("meta", {}))
# #                         text_settings = self.default_text_settings()
# #                         text_settings.update(self.project_meta.get("door_text", {}))
# #                         self.project_meta["door_text"] = text_settings
# #                         self.parametric_groups = raw_data.get("groups", [])
# #                     else:
# #                         self.parametric_groups = raw_data
# #                 except Exception as e:
# #                     print(f"Помилка міграційного читання JSON: {e}")

# #         for g in self.parametric_groups:
# #             g["handles"] = set(g.get("handles", []))
# #             self.get_group_key(g)

# #             if "k_x" in g:
# #                 g["k_w"] = g.pop("k_x")
# #                 g["k_h"] = g.pop("k_y")
# #                 g["growth_p_w"] = g.pop("growth_p_x")
# #                 g["growth_p_h"] = g.pop("growth_p_y")
# #             else:
# #                 g["k_w"] = g.get("k_w", 0.0)
# #                 g["k_h"] = g.get("k_h", 0.0)
# #                 g["growth_p_w"] = g.get("growth_p_w", 0.0)
# #                 g["growth_p_h"] = g.get("growth_p_h", 0.0)

# #             old_link_x = g.get("link_x", "W")
# #             old_link_y = g.get("link_y", "H")
# #             g["link_x"] = "X = W" if "W" in old_link_x or "Ширин" in old_link_x else "X = H"
# #             g["link_y"] = "Y = H" if "H" in old_link_y or "Висот" in old_link_y else "Y = W"

# #             if "growth_direction" in g:
# #                 old_dir = g.pop("growth_direction")
# #                 g["growth_dir_x"] = "Вправо" if "Вправо" in old_dir else ("Вліво" if "Вліво" in old_dir else "Центр")
# #                 g["growth_dir_y"] = "Вгору" if "Вгору" in old_dir else ("Вниз" if "Вниз" in old_dir else "Центр")
# #             else:
# #                 g["growth_dir_x"] = g.get("growth_dir_x", "Центр")
# #                 g["growth_dir_y"] = g.get("growth_dir_y", "Центр")

# #             g["shift_dir_x"] = g.get("shift_dir_x", "Вправо")
# #             g["shift_dir_y"] = g.get("shift_dir_y", "Вгору")
# #             g["role_y"] = g.get("role_y", "manual")
# #             g["auto_rule"] = bool(g.get("auto_rule", False))
# #             g["touch_y_enabled"] = bool(g.get("touch_y_enabled", False))
# #             g["touch_to_uid"] = g.get("touch_to_uid")
# #             g["touch_gap_y"] = float(g.get("touch_gap_y", 0.0) or 0.0)
# #             if "resizes" not in g:
# #                 g["resizes"] = (
# #                     abs(float(g.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
# #                     abs(float(g.get("growth_p_h", 0.0) or 0.0)) > 0.000001
# #                 )

# #             key = self.get_group_key(g)
# #             if key not in self.block_keep_state:
# #                 self.block_keep_state[key] = True
# #             self.apply_growth_axis_to_group(g)

# #         self.apply_axis_link_mode_to_groups()

# #     def save_project_config(self):
# #         """Замість JSON пишемо конфігурацію в MSSQL."""
# #         self.project_meta["keep_blocks"] = [name for name, keep in self.block_keep_state.items() if keep]
# #         self.project_meta["delete_blocks"] = [name for name, keep in self.block_keep_state.items() if not keep]
# #         self.save_current_project_to_db("ConfigSaved")

# #     def export_config_to_json_backup(self):
# #         """Ручний backup/export JSON. Це не основне збереження."""
# #         groups_data = []
# #         for g in self.parametric_groups:
# #             self.get_group_key(g)
# #             g_data = g.copy()
# #             g_data["handles"] = list(g.get("handles", []))
# #             groups_data.append(g_data)

# #         data = {"meta": self.project_meta, "groups": groups_data}

# #         file_path, _ = QFileDialog.getSaveFileName(
# #             self,
# #             "Експорт конфігурації JSON",
# #             os.path.splitext(self.dxf_path)[0] + "_backup.json",
# #             "JSON Files (*.json)"
# #         )
# #         if file_path:
# #             with open(file_path, "w", encoding="utf-8") as f:
# #                 json.dump(data, f, indent=4, ensure_ascii=False, default=list)

# #         if getattr(self, "current_project_file_id", None) and self.current_user_id():
# #             self.db.export_project_json_backup(
# #                 self.current_project_file_id,
# #                 data,
# #                 self.current_user_id(),
# #                 "ManualExport",
# #             )

# #     def init_ui(self):
# #         main_widget = QWidget()
# #         self.central_layout = QHBoxLayout(main_widget)
# #         self.setCentralWidget(main_widget)

# #         folder_explorer_widget = QWidget()
# #         folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
# #         folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
# #         lbl_explorer_title = QLabel("📁 <b>Провідник DXF:</b>")
# #         lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
# #         folder_explorer_layout.addWidget(lbl_explorer_title)

# #         self.btn_open_file = QPushButton("📂 Відкрити файл...")
# #         self.btn_open_file.setStyleSheet("background-color: #37474f; color: white; font-weight: bold; padding: 4px;")
# #         self.btn_open_file.clicked.connect(self.open_dxf_from_dialog)
# #         folder_explorer_layout.addWidget(self.btn_open_file)

# #         self.btn_export_json_backup = QPushButton("💾 Експорт JSON backup")
# #         self.btn_export_json_backup.setStyleSheet("background-color: #455a64; color: white; font-weight: bold; padding: 4px;")
# #         self.btn_export_json_backup.clicked.connect(self.export_config_to_json_backup)
# #         folder_explorer_layout.addWidget(self.btn_export_json_backup)
        
# #         self.file_explorer_list = QListWidget()
# #         self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# #         self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
# #         folder_explorer_layout.addWidget(self.file_explorer_list)
# #         self.central_layout.addWidget(folder_explorer_widget, stretch=1)

# #         self.scene = QGraphicsScene()
# #         self.view = AdvancedGraphicsView(self.scene, self)
# #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# #         self.view.setMouseTracking(True)  
# #         self.scene.mouseMoveEvent = self.on_scene_mouse_move
# #         self.central_layout.addWidget(self.view, stretch=5)
# #         self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 

# #         self.scroll_area = QScrollArea()
# #         self.scroll_area.setWidgetResizable(True) 
# #         self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
# #         control_panel = QWidget()
# #         control_panel_layout = QVBoxLayout(control_panel)
# #         control_panel_layout.setContentsMargins(5, 5, 5, 5)
# #         self.scroll_area.setWidget(control_panel)
# #         self.central_layout.addWidget(self.scroll_area, stretch=4)

# #         self.file_status_group = QGroupBox("Стан файлу")
# #         file_status_box = QGridLayout()
# #         file_status_box.setSpacing(4) 
# #         file_status_box.setContentsMargins(6, 12, 6, 6)

# #         self.lbl_file_status_source = QLabel("")
# #         self.lbl_file_status_target = QLabel("")
# #         self.lbl_file_status_opening = QLabel("")
# #         self.lbl_file_status_axis = QLabel("")
# #         self.lbl_file_status_db = QLabel("")

# #         file_status_box.addWidget(self.lbl_file_status_source, 0, 0)
# #         file_status_box.addWidget(self.lbl_file_status_target, 0, 1)
# #         file_status_box.addWidget(self.lbl_file_status_opening, 1, 0)
# #         file_status_box.addWidget(self.lbl_file_status_axis, 1, 1)
# #         file_status_box.addWidget(self.lbl_file_status_db, 2, 0, 1, 2)

# #         file_status_box.addWidget(QLabel("Осі файлу:"), 3, 0)

# #         axis_box = QHBoxLayout()

# #         self.combo_link_x = QComboBox()
# #         self.combo_link_x.addItems(["X = W", "X = H"])
# #         self.combo_link_x.setEnabled(True)
# #         self.combo_link_x.setToolTip("Глобальна прив'язка осей для всього файлу")
# #         axis_box.addWidget(self.combo_link_x)

# #         self.combo_link_y = QComboBox()
# #         self.combo_link_y.addItems(["Y = H", "Y = W"])
# #         self.combo_link_y.setEnabled(False)
# #         self.combo_link_y.setToolTip("Глобальна прив'язка осей для всього файлу")
# #         axis_box.addWidget(self.combo_link_y)

# #         file_status_box.addLayout(axis_box, 3, 1)

# #         self.file_status_group.setLayout(file_status_box)
# #         control_panel_layout.addWidget(self.file_status_group)

# #         self.side_tabs = QTabWidget()
# #         self.side_tabs.setDocumentMode(True)
# #         self.side_tabs.setUsesScrollButtons(True)
# #         self.tab_file = QWidget()
# #         self.tab_sizes = QWidget()
# #         self.tab_groups = QWidget()
# #         self.tab_text = QWidget()
# #         self.tab_more = QWidget()
# #         self.tab_file_layout = QVBoxLayout(self.tab_file)
# #         self.tab_sizes_layout = QVBoxLayout(self.tab_sizes)
# #         self.tab_groups_layout = QVBoxLayout(self.tab_groups)
# #         self.tab_text_layout = QVBoxLayout(self.tab_text)
# #         self.tab_more_layout = QVBoxLayout(self.tab_more)
# #         for layout in (
# #             self.tab_file_layout,
# #             self.tab_sizes_layout,
# #             self.tab_groups_layout,
# #             self.tab_text_layout,
# #             self.tab_more_layout,
# #         ):
# #             layout.setContentsMargins(3, 3, 3, 3)
# #             layout.setSpacing(4)
# #         self.side_tabs.addTab(self.tab_file, "Файл")
# #         self.side_tabs.addTab(self.tab_sizes, "Розміри")
# #         self.side_tabs.addTab(self.tab_groups, "Групи")
# #         self.side_tabs.addTab(self.tab_text, "Текст")
# #         self.side_tabs.addTab(self.tab_more, "Інше")
# #         control_panel_layout.addWidget(self.side_tabs)

# #         inspector_group = QGroupBox("")
# #         inspector_box = QVBoxLayout()
# #         self.chk_enable_inspector = QCheckBox(" Ввімкнути інтерактивний трекер точок")
# #         self.chk_enable_inspector.setStyleSheet("color: #ff9800; font-weight: bold;")
# #         self.chk_enable_inspector.clicked.connect(self.toggle_inspector_mode)
# #         inspector_box.addWidget(self.chk_enable_inspector)
        
# #         self.btn_snap_zero = QPushButton("↙️ Притиснути фігуру до (0, 0)")
# #         self.btn_snap_zero.setStyleSheet("background-color: #00897b; color: white; font-weight: bold; padding: 6px;")
# #         self.btn_snap_zero.clicked.connect(self.snap_to_zero)
# #         inspector_box.addWidget(self.btn_snap_zero)
        
# #         inspector_group.setLayout(inspector_box)
# #         self.tab_more_layout.addWidget(inspector_group)

# #         self.transform_group = QGroupBox("🔄 Трансформація виділених елементів (DXF)")
# #         self.transform_group.setStyleSheet("QGroupBox { border: 1px solid #d32f2f; }")
# #         transform_box = QVBoxLayout()
        
# #         rot_btn_layout = QHBoxLayout()
# #         self.btn_rot_90 = QPushButton("90°")
# #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# #         rot_btn_layout.addWidget(self.btn_rot_90)
        
# #         self.btn_rot_180 = QPushButton("180°")
# #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# #         rot_btn_layout.addWidget(self.btn_rot_180)
        
# #         self.btn_rot_270 = QPushButton("270°")
# #         self.btn_rot_270.clicked.connect(lambda: self.transform_selected_entities("ROT270"))
# #         rot_btn_layout.addWidget(self.btn_rot_270)
# #         transform_box.addLayout(rot_btn_layout)

# #         mirror_btn_layout = QHBoxLayout()
# #         self.btn_mirror_h = QPushButton("Дзеркало ↔ Ліво/право")
# #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# #         mirror_btn_layout.addWidget(self.btn_mirror_h)

# #         self.btn_mirror_v = QPushButton("Дзеркало ↕ Верх/низ")
# #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
# #         mirror_btn_layout.addWidget(self.btn_mirror_v)
# #         transform_box.addLayout(mirror_btn_layout)

# #         self.transform_group.setLayout(transform_box)
# #         self.tab_file_layout.addWidget(self.transform_group)

# #         auto_scale_group = QGroupBox(" Параметрична трансформація розмірів")
# #         auto_scale_box = QVBoxLayout()

# #         width_layout = QHBoxLayout()
# #         width_layout.addWidget(QLabel("Ширина:"))
# #         self.input_current_width = QLineEdit("1000")
# #         width_layout.addWidget(self.input_current_width)
# #         width_layout.addWidget(QLabel("➡️ Нова:"))
# #         self.input_target_width = QLineEdit("1050")
# #         width_layout.addWidget(self.input_target_width)
# #         auto_scale_box.addLayout(width_layout)

# #         height_layout = QHBoxLayout()
# #         height_layout.addWidget(QLabel("Висота:"))
# #         self.input_current_height = QLineEdit("2000")
# #         height_layout.addWidget(self.input_current_height)
# #         height_layout.addWidget(QLabel("➡️ Нова:"))
# #         self.input_target_height = QLineEdit("2080")
# #         height_layout.addWidget(self.input_target_height)
# #         auto_scale_box.addLayout(height_layout)

# #         self.lbl_status_calc = QLabel("Задайте нові розміри конструкції для автоматичного морфінгу.")
# #         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
# #         auto_scale_box.addWidget(self.lbl_status_calc)

# #         self.btn_apply_auto_scale = QPushButton(" Запустити глобальний перерахунок")
# #         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
# #         self.btn_apply_auto_scale.clicked.connect(lambda: self.process_parametric_percentage_scale())
# #         auto_scale_box.addWidget(self.btn_apply_auto_scale)

# #         preview_buttons = QHBoxLayout()
# #         self.btn_preview_scale = QPushButton("Перегляд")
# #         self.btn_preview_scale.clicked.connect(self.preview_parametric_scale)
# #         preview_buttons.addWidget(self.btn_preview_scale)

# #         self.btn_restore_current = QPushButton("Повернути базу")
# #         self.btn_restore_current.clicked.connect(self.restore_current_dxf_from_disk)
# #         preview_buttons.addWidget(self.btn_restore_current)
# #         auto_scale_box.addLayout(preview_buttons)

# #         workflow_buttons = QHBoxLayout()
# #         self.btn_remember_source_size = QPushButton("Запам'ятати початкові")
# #         self.btn_remember_source_size.clicked.connect(self.remember_source_dimensions)
# #         workflow_buttons.addWidget(self.btn_remember_source_size)

# #         self.btn_import_params = QPushButton("Excel/CSV параметри")
# #         self.btn_import_params.clicked.connect(self.import_parameters_from_table)
# #         workflow_buttons.addWidget(self.btn_import_params)

# #         self.btn_order_wizard = QPushButton("Нове замовлення")
# #         self.btn_order_wizard.clicked.connect(self.quick_order_wizard)
# #         workflow_buttons.addWidget(self.btn_order_wizard)
# #         auto_scale_box.addLayout(workflow_buttons)

# #         self.btn_export_new_dxf = QPushButton("Створити новий DXF")
# #         self.btn_export_new_dxf.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;")
# #         self.btn_export_new_dxf.clicked.connect(self.export_new_dxf_with_dimensions)
# #         auto_scale_box.addWidget(self.btn_export_new_dxf)

# #         self.btn_batch_export = QPushButton("Пакет з Excel/CSV")
# #         self.btn_batch_export.clicked.connect(self.batch_export_from_table)
# #         auto_scale_box.addWidget(self.btn_batch_export)

# #         # self.btn_find_min_size = QPushButton("Мінімум без накладання")
# #         # self.btn_find_min_size.clicked.connect(self.find_minimum_safe_size)
# #         # auto_scale_box.addWidget(self.btn_find_min_size)

# #         auto_scale_group.setLayout(auto_scale_box)
# #         self.tab_sizes_layout.addWidget(auto_scale_group)

# #         opening_group = QGroupBox("Відкривання")
# #         opening_box = QHBoxLayout()
# #         opening_box.addWidget(QLabel("Початкове:"))
# #         self.combo_source_door_opening = QComboBox()
# #         self.combo_source_door_opening.addItems(["Ліве", "Праве"])
# #         self.combo_source_door_opening.currentTextChanged.connect(self.on_source_door_opening_changed)
# #         opening_box.addWidget(self.combo_source_door_opening)
# #         opening_box.addWidget(QLabel("Отримати:"))
# #         self.combo_door_opening = QComboBox()
# #         self.combo_door_opening.addItems(["Ліве", "Праве"])
# #         self.combo_door_opening.currentTextChanged.connect(self.on_door_opening_changed)
# #         opening_box.addWidget(self.combo_door_opening)
# #         self.btn_mirror_opening = QPushButton("Змінити L/R")
# #         self.btn_mirror_opening.clicked.connect(self.mirror_door_opening)
# #         opening_box.addWidget(self.btn_mirror_opening)
# #         opening_group.setLayout(opening_box)
# #         self.tab_sizes_layout.addWidget(opening_group)

# #         text_group = QGroupBox("Текст на дверях")
# #         text_box = QGridLayout()
# #         self.check_door_text_enabled = QCheckBox("Додати текст")
# #         self.check_door_text_enabled.stateChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.check_door_text_enabled, 0, 0, 1, 2)

# #         text_box.addWidget(QLabel("Текст:"), 1, 0)
# #         self.input_door_text = QLineEdit()
# #         self.input_door_text.textChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.input_door_text, 1, 1, 1, 3)

# #         text_box.addWidget(QLabel("X:"), 2, 0)
# #         self.input_text_x = QLineEdit("0")
# #         self.input_text_x.textChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.input_text_x, 2, 1)

# #         text_box.addWidget(QLabel("Y:"), 2, 2)
# #         self.input_text_y = QLineEdit("0")
# #         self.input_text_y.textChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.input_text_y, 2, 3)

# #         text_box.addWidget(QLabel("Висота:"), 3, 0)
# #         self.input_text_height = QLineEdit("30")
# #         self.input_text_height.textChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.input_text_height, 3, 1)

# #         text_box.addWidget(QLabel("Ширина рамки:"), 3, 2)
# #         self.input_text_width_factor = QLineEdit("120")
# #         self.input_text_width_factor.textChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.input_text_width_factor, 3, 3)

# #         text_box.addWidget(QLabel("Поворот:"), 4, 0)
# #         self.input_text_rotation = QLineEdit("0")
# #         self.input_text_rotation.textChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.input_text_rotation, 4, 1)

# #         text_box.addWidget(QLabel("Шрифт:"), 4, 2)
# #         self.combo_text_font = QComboBox()
# #         self.combo_text_font.setEditable(True)
# #         self.combo_text_font.addItems([
# #             "STANDARD", "Arial", "Arial Narrow", "Arial Black",
# #             "Calibri", "Calibri Light", "Cambria", "Candara",
# #             "Century Gothic", "Consolas", "Courier New",
# #             "Georgia", "Impact", "Segoe UI", "Tahoma",
# #             "Times New Roman", "Trebuchet MS", "Verdana",
# #             "Simplex", "Romans", "Isocp"
# #         ])
# #         self.combo_text_font.currentTextChanged.connect(self.on_text_settings_changed)
# #         text_box.addWidget(self.combo_text_font, 4, 3)

# #         self.btn_place_door_text = QPushButton("Показати/поставити блок")
# #         self.btn_place_door_text.clicked.connect(self.place_empty_door_text_block)
# #         text_box.addWidget(self.btn_place_door_text, 5, 0, 1, 4)

# #         self.btn_apply_door_text = QPushButton("Оновити текст")
# #         self.btn_apply_door_text.clicked.connect(self.apply_door_text_from_ui)
# #         text_box.addWidget(self.btn_apply_door_text, 6, 0, 1, 4)

# #         self.btn_remove_door_text = QPushButton("Прибрати текстовий блок")
# #         self.btn_remove_door_text.clicked.connect(self.remove_door_text_block)
# #         text_box.addWidget(self.btn_remove_door_text, 7, 0, 1, 4)

# #         align_text_buttons = QHBoxLayout()
# #         self.btn_align_text_width = QPushButton("Вирівняти по ширині")
# #         self.btn_align_text_width.clicked.connect(lambda: self.align_text_box_to_door("width"))
# #         align_text_buttons.addWidget(self.btn_align_text_width)
# #         self.btn_align_text_height = QPushButton("Вирівняти по висоті")
# #         self.btn_align_text_height.clicked.connect(lambda: self.align_text_box_to_door("height"))
# #         align_text_buttons.addWidget(self.btn_align_text_height)
# #         text_box.addLayout(align_text_buttons, 8, 0, 1, 4)
# #         text_group.setLayout(text_box)
# #         self.text_group = text_group
# #         self.text_box_layout = text_box
# #         text_group.setCheckable(True)
# #         text_group.toggled.connect(self.set_text_panel_expanded)
# #         text_settings = self.project_meta.get("door_text", {})
# #         text_open = bool(
# #             text_settings.get("enabled") or
# #             str(text_settings.get("text", "")).strip() or
# #             text_settings.get("handle")
# #         )
# #         text_group.setChecked(text_open)
# #         self.set_text_panel_expanded(text_open)
# #         self.tab_text_layout.addWidget(text_group)
# #         self.sync_text_inputs_from_meta()
# #         self.sync_opening_inputs_from_meta()

# #         history_group = QGroupBox("Конструкторська історія")
# #         history_box = QHBoxLayout()
# #         self.btn_undo = QPushButton("Назад")
# #         self.btn_undo.clicked.connect(self.undo)
# #         self.btn_redo = QPushButton("Вперед")
# #         self.btn_redo.clicked.connect(self.redo)
# #         history_box.addWidget(self.btn_undo)
# #         history_box.addWidget(self.btn_redo)
# #         history_group.setLayout(history_box)
# #         self.tab_file_layout.addWidget(history_group)

# #         group_constructor_group = QGroupBox(" Параметричні групи топології")
# #         group_box = QVBoxLayout()

# #         self.btn_create_group = QPushButton(" Створити параметричну групу")
# #         self.btn_create_group.setStyleSheet("background-color: #673ab7; color: white; font-weight: bold;")
# #         self.btn_create_group.clicked.connect(self.create_parametric_group)
# #         group_box.addWidget(self.btn_create_group)

# #         self.btn_auto_group_entities = QPushButton("Автогрупувати")
# #         self.btn_auto_group_entities.setStyleSheet("background-color: #455a64; color: white; font-weight: bold;")
# #         self.btn_auto_group_entities.clicked.connect(self.auto_group_entities)
# #         self.btn_auto_group_entities.hide()

# #         self.btn_delete_from_dxf = QPushButton(" Видалити об'єкти з креслення (DXF)")
# #         self.btn_delete_from_dxf.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
# #         self.btn_delete_from_dxf.clicked.connect(self.delete_entities_from_dxf)
# #         group_box.addWidget(self.btn_delete_from_dxf)

# #         self.btn_remove_selected = QPushButton(" Виключити виділене з групи")
# #         self.btn_remove_selected.clicked.connect(self.remove_selected_from_group)
# #         group_box.addWidget(self.btn_remove_selected)

# #         self.btn_disband_group = QPushButton("Розформувати вибрану групу")
# #         self.btn_disband_group.clicked.connect(self.disband_parametric_group)
# #         group_box.addWidget(self.btn_disband_group)

# #         group_box.addWidget(QLabel("<b>Параметричні групи деталей:</b>"))
# #         self.group_list_widget = QListWidget()
# #         self.group_list_widget.setFixedHeight(76)
# #         self.group_list_widget.itemSelectionChanged.connect(self.on_group_selection_changed)
# #         group_box.addWidget(self.group_list_widget)

# #         group_box.addWidget(QLabel("<b>Блоки для нового DXF (галочка = лишити):</b>"))
# #         self.block_filter_list = QListWidget()
# #         self.block_filter_list.setFixedHeight(70)
# #         self.block_filter_list.itemChanged.connect(self.on_block_keep_state_changed)
# #         group_box.addWidget(self.block_filter_list)

   
# #         group_box.addWidget(QLabel("<b> Параметри трансформації:</b>"))
        
# #         growth_axis_layout = QHBoxLayout()
# #         growth_axis_layout.addWidget(QLabel("Режим файлу:"))
# #         self.combo_group_growth_axis = QComboBox()
# #         self.combo_group_growth_axis.addItems(["Ширина + висота", "Тільки ширина", "Тільки висота", "Не росте"])
# #         self.combo_group_growth_axis.currentTextChanged.connect(self.on_group_growth_axis_changed)
# #         growth_axis_layout.addWidget(self.combo_group_growth_axis)
# #         group_box.addLayout(growth_axis_layout)

# #         self.chk_group_resizes = QCheckBox("Група змінює розмір")
# #         self.chk_group_resizes.stateChanged.connect(self.on_group_resizes_changed)
# #         group_box.addWidget(self.chk_group_resizes)

# #         grid = QGridLayout()
# #         self.param_transform_grid = grid
# #         grid.setContentsMargins(0, 0, 0, 0)
# #         grid.setHorizontalSpacing(4)
# #         grid.setVerticalSpacing(3)

# #         preset_items = [
# #             "0% (Фіксовано)",
# #             "25% (1/4)",
# #             "33.3% (1/3)",
# #             "50% (Центр / Δ/2)",
# #             "66.7% (2/3)",
# #             "75% (1/4)",
# #             "100% (Δ/1)",
# #             "Ввести вручну"
# #         ]

# #         self.combo_k_w = QComboBox()
# #         self.combo_k_w.setEditable(True)
# #         self.combo_k_w.addItems(preset_items)

# #         self.combo_shift_dir_x = QComboBox()
# #         self.combo_shift_dir_x.addItems(["Вправо", "Вліво"])

# #         self.combo_growth_p_w = QComboBox()
# #         self.combo_growth_p_w.setEditable(True)
# #         self.combo_growth_p_w.addItems(preset_items)

# #         self.combo_growth_dir_x = QComboBox()
# #         self.combo_growth_dir_x.addItems(["Вправо", "Вліво", "Центр"])

# #         self.combo_k_h = QComboBox()
# #         self.combo_k_h.setEditable(True)
# #         self.combo_k_h.addItems(preset_items)

# #         self.combo_shift_dir_y = QComboBox()
# #         self.combo_shift_dir_y.addItems(["Вгору", "Вниз"])

# #         self.combo_growth_p_h = QComboBox()
# #         self.combo_growth_p_h.setEditable(True)
# #         self.combo_growth_p_h.addItems(preset_items)

# #         self.combo_growth_dir_y = QComboBox()
# #         self.combo_growth_dir_y.addItems(["Вгору", "Вниз", "Центр"])

# #         grid.addWidget(QLabel("X зсув"), 0, 0)
# #         grid.addWidget(self.combo_k_w, 0, 1)
# #         grid.addWidget(self.combo_shift_dir_x, 0, 2)

# #         grid.addWidget(QLabel("X ріст"), 1, 0)
# #         grid.addWidget(self.combo_growth_p_w, 1, 1)
# #         grid.addWidget(self.combo_growth_dir_x, 1, 2)

# #         grid.addWidget(QLabel("Y зсув"), 2, 0)
# #         grid.addWidget(self.combo_k_h, 2, 1)
# #         grid.addWidget(self.combo_shift_dir_y, 2, 2)

# #         grid.addWidget(QLabel("Y ріст"), 3, 0)
# #         grid.addWidget(self.combo_growth_p_h, 3, 1)
# #         grid.addWidget(self.combo_growth_dir_y, 3, 2)

# #         grid.setColumnStretch(0, 0)
# #         grid.setColumnStretch(1, 1)
# #         grid.setColumnStretch(2, 0)

# #         group_box.addLayout(grid)

# #         rule_layout = QHBoxLayout()
# #         self.combo_rule_library = QComboBox()
# #         self.combo_rule_library.addItems(list(self.typical_rule_library().keys()))
# #         rule_layout.addWidget(self.combo_rule_library)
# #         self.btn_apply_rule = QPushButton("Застосувати правило")
# #         self.btn_apply_rule.clicked.connect(self.apply_selected_rule_to_group)
# #         rule_layout.addWidget(self.btn_apply_rule)
# #         group_box.addLayout(rule_layout)

# #         topology_layout = QHBoxLayout()
# #         # self.btn_auto_rules_y = QPushButton("Авто правила Y")
# #         # self.btn_auto_rules_y.setStyleSheet("background-color: #455a64; color: white; font-weight: bold;")
# #         # self.btn_auto_rules_y.clicked.connect(self.auto_apply_vertical_topology_rules)
# #         # topology_layout.addWidget(self.btn_auto_rules_y)

# #         # self.btn_touch_rules_y = QPushButton("Зберігати дотик Y")
# #         # self.btn_touch_rules_y.setStyleSheet("background-color: #00695c; color: white; font-weight: bold;")
# #         # self.btn_touch_rules_y.clicked.connect(self.auto_detect_vertical_touch_constraints)
# #         # topology_layout.addWidget(self.btn_touch_rules_y)

# #         self.btn_auto_chain_growth_y = QPushButton("Авто сума росту Y")
# #         self.btn_auto_chain_growth_y.setStyleSheet("background-color: #1565c0; color: white; font-weight: bold;")
# #         self.btn_auto_chain_growth_y.clicked.connect(self.auto_chain_growth_y)
# #         self.btn_auto_chain_growth_y.hide()

# #         self.btn_auto_chain_growth_x = QPushButton("Авто сума росту X")
# #         self.btn_auto_chain_growth_x.setStyleSheet("background-color: #6a1b9a; color: white; font-weight: bold;")
# #         self.btn_auto_chain_growth_x.clicked.connect(self.auto_chain_growth_x)
# #         self.btn_auto_chain_growth_x.hide()

# #         self.btn_auto_layout_all = QPushButton("Авторозставити все")
# #         self.btn_auto_layout_all.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
# #         self.btn_auto_layout_all.clicked.connect(self.auto_layout_all_groups)
# #         self.btn_auto_layout_all.hide()

# #         # self.btn_auto_mirror_x = QPushButton("Дзеркальні сторони X")
# #         # self.btn_auto_mirror_x.setStyleSheet("background-color: #8d6e63; color: white; font-weight: bold;")
# #         # self.btn_auto_mirror_x.clicked.connect(self.confirm_and_apply_mirror_x_rules)
# #         # topology_layout.addWidget(self.btn_auto_mirror_x)
# #         group_box.addLayout(topology_layout)

# #         # Підключення сигналів сітки

        
# #         self.combo_k_w.currentTextChanged.connect(self.on_combo_k_w_changed)
# #         self.combo_k_h.currentTextChanged.connect(self.on_combo_k_h_changed)
# #         self.combo_growth_p_w.currentTextChanged.connect(self.on_combo_growth_p_w_changed)
# #         self.combo_growth_p_h.currentTextChanged.connect(self.on_combo_growth_p_h_changed)
        
# #         self.combo_growth_dir_x.currentTextChanged.connect(self.on_growth_dir_x_changed)
# #         self.combo_growth_dir_y.currentTextChanged.connect(self.on_growth_dir_y_changed)
# #         self.combo_shift_dir_x.currentTextChanged.connect(self.on_shift_dir_x_changed)
# #         self.combo_shift_dir_y.currentTextChanged.connect(self.on_shift_dir_y_changed)


# #         self.combo_link_x.currentTextChanged.connect(self.on_link_x_changed)
# #         self.combo_link_y.currentTextChanged.connect(self.on_link_y_changed)
# #         # -------------------------------------------------------------

# #         group_constructor_group.setLayout(group_box)
# #         self.tab_groups_layout.addWidget(group_constructor_group)

# #         self.tab_groups_layout.addWidget(QLabel("<b>Повний список ліній/отворів у файлі:</b>"))
# #         self.entity_list = QListWidget()
# #         self.entity_list.setFixedHeight(86)
# #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# #         self.tab_groups_layout.addWidget(self.entity_list)

# #         theme_group = QGroupBox(" Інтерфейс")
# #         theme_box = QHBoxLayout()
# #         self.theme_combo = QComboBox()
# #         self.theme_combo.addItems(["Темна", "Світла"])
# #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# #         theme_box.addWidget(self.theme_combo)
# #         theme_group.setLayout(theme_box)
# #         self.tab_more_layout.addWidget(theme_group)

# #         self.tab_file_layout.addStretch()
# #         self.tab_sizes_layout.addStretch()
# #         self.tab_groups_layout.addStretch()
# #         self.tab_text_layout.addStretch()
# #         self.tab_more_layout.addStretch()
# #         control_panel_layout.addStretch()
# #         self.apply_compact_right_panel_style()
# #         self.update_history_buttons_state()



# #     def apply_compact_right_panel_style(self):
# #         """Компактний режим правої панелі: максимум 300 px і без горизонтального роз'їзду."""
# #         if hasattr(self, "scroll_area"):
# #             self.scroll_area.setFixedWidth(400)
# #             self.scroll_area.setMinimumWidth(400)
# #             self.scroll_area.setMaximumWidth(400)

# #         widgets = []
# #         if hasattr(self, "scroll_area") and self.scroll_area.widget():
# #             widgets = self.scroll_area.widget().findChildren(QWidget)

# #         for widget in widgets:
# #             if isinstance(widget, QLabel):
# #                 widget.setWordWrap(True)
# #                 widget.setMaximumWidth(370)
# #             elif isinstance(widget, QPushButton):
# #                 widget.setMinimumHeight(24)
# #                 widget.setMaximumHeight(30)
# #                 widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
# #             elif isinstance(widget, (QLineEdit, QComboBox)):
# #                 widget.setMinimumHeight(22)
# #                 widget.setMaximumHeight(26)
# #                 widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
# #             elif isinstance(widget, QListWidget):
# #                 widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

# #         for group in self.findChildren(QGroupBox):
# #             group.setMaximumWidth(386)

# #         self.setStyleSheet(self.styleSheet() + """
# #         QScrollArea { border: 0px; }
# #         QTabWidget::pane { border: 1px solid #444; padding: 2px; }
# #         QTabBar::tab { padding: 3px 5px; min-width: 42px; font-size: 10px; }
# #         QGroupBox {
# #             margin-top: 8px;
# #             padding-top: 8px;
# #             font-size: 10px;
# #         }
# #         QLabel { font-size: 10px; }
# #         QPushButton {
# #             font-size: 10px;
# #             padding: 3px 4px;
# #             text-align: center;
# #         }
# #         QLineEdit, QComboBox {
# #             font-size: 10px;
# #             padding: 1px 3px;
# #         }
# #         QListWidget {
# #             font-size: 10px;
# #         }
# #         QCheckBox {
# #             font-size: 10px;
# #             spacing: 3px;
# #         }
# #         """)

# #     def setup_shortcuts(self):

# #         # ---------- Файл ----------
# #         QShortcut(QKeySequence("Ctrl+O"), self, self.open_dxf_from_dialog)
# #         QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.doc.saveas(self.dxf_path))

# #         # ---------- Історія ----------
# #         QShortcut(QKeySequence("Ctrl+Z"), self, self.undo)
# #         QShortcut(QKeySequence("Ctrl+Y"), self, self.redo)

# #         # Альтернативний redo як в AutoCAD
# #         QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.redo)

# #         # ---------- Виділення ----------
# #         QShortcut(QKeySequence("Ctrl+A"), self, self.select_all_entities)

# #         # Зняти виділення
# #         QShortcut(QKeySequence("Escape"), self, self.clear_selection)

# #         # ---------- Видалення ----------
# #         QShortcut(QKeySequence("Delete"), self, self.delete_entities_from_dxf)

# #         # ---------- Перегляд ----------
# #         QShortcut(QKeySequence("F"), self, self.zoom_extents)      # Fit All
# #         QShortcut(QKeySequence("Home"), self, self.zoom_extents)

# #         # ---------- Перетворення ----------
# #         QShortcut(QKeySequence("Ctrl+R"), self,
# #                 lambda: self.transform_selected_entities("ROT90"))

# #         QShortcut(QKeySequence("Ctrl+Shift+R"), self,
# #                 lambda: self.transform_selected_entities("ROT180"))

# #         QShortcut(QKeySequence("Ctrl+M"), self,
# #                 lambda: self.transform_selected_entities("MIRROR_H"))

# #         # ---------- Групи ----------
# #         QShortcut(QKeySequence("Ctrl+G"), self, self.create_parametric_group)

# #         QShortcut(QKeySequence("Ctrl+Shift+G"), self,
# #                 self.disband_parametric_group)

# #         # ---------- Перерахунок ----------
# #         QShortcut(QKeySequence("F5"), self,
# #                 self.process_parametric_percentage_scale)

# #         QShortcut(QKeySequence("F6"), self,
# #                 self.preview_parametric_scale)

# #         # ---------- Експорт ----------
# #         QShortcut(QKeySequence("Ctrl+E"), self,
# #                 self.export_new_dxf_with_dimensions)

# #     def typical_rule_library(self):
# #         return {
            
# #             "Фіксовано": {
# #                 "k_w": 0.0, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Рухається вправо": {
# #                 "k_w": 1.0, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Рухається вліво": {
# #                 "k_w": 1.0, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Рухається вгору": {
# #                 "k_w": 0.0, "k_h": 1.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Центрувати по ширині": {
# #                 "k_w": 0.5, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Центрувати по висоті": {
# #                 "k_w": 0.0, "k_h": 0.5,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
            
# #             "Правий край + ріст вгору": {
# #                 "k_w": 1.0, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 1.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Верхній край + ріст вправо": {
# #                 "k_w": 0.0, "k_h": 1.0,
# #                 "growth_p_w": 1.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },

# #             # "Лівий край + ріст вправо": {
# #             #     "k_w": 0.0, "k_h": 0.0,
# #             #     "growth_p_w": 1.0, "growth_p_h": 0.0,
# #             #     "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #             #     "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
# #             #     "link_x": "X = W", "link_y": "Y = H"
# #             # },

# #             # "Правий край + ріст вліво": {
# #             #     "k_w": 1.0, "k_h": 0.0,
# #             #     "growth_p_w": 1.0, "growth_p_h": 0.0,
# #             #     "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
# #             #     "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #             #     "link_x": "X = W", "link_y": "Y = H"
# #             # },

# #             # "Нижній край + ріст вгору": {
# #             #     "k_w": 0.0, "k_h": 0.0,
# #             #     "growth_p_w": 0.0, "growth_p_h": 1.0,
# #             #     "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #             #     "shift_dir_x": "Вправо", "shift_dir_y": "Вниз",
# #             #     "link_x": "X = W", "link_y": "Y = H"
# #             # },

# #             # "Верхній край + ріст вниз": {
# #             #     "k_w": 0.0, "k_h": 1.0,
# #             #     "growth_p_w": 0.0, "growth_p_h": 1.0,
# #             #     "growth_dir_x": "Вправо", "growth_dir_y": "Вниз",
# #             #     "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #             #     "link_x": "X = W", "link_y": "Y = H"
# #             # },

# #             "1/3 ширини": {
# #                 "k_w": 0.3333, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },

# #             "2/3 ширини": {
# #                 "k_w": 0.6667, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
            
# #             "Розтягнути вправо": {
# #                 "k_w": 0.0, "k_h": 0.0,
# #                 "growth_p_w": 1.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },
# #             "Розтягнути вгору": {
# #                 "k_w": 0.0, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 1.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },

# #             "Розтягнути вліво": {
# #                 "k_w": 0.0, "k_h": 0.0,
# #                 "growth_p_w": 1.0, "growth_p_h": 0.0,
# #                 "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
# #                 "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             },

# #             "Розтягнути вниз": {
# #                 "k_w": 0.0, "k_h": 0.0,
# #                 "growth_p_w": 0.0, "growth_p_h": 1.0,
# #                 "growth_dir_x": "Вправо", "growth_dir_y": "Вниз",
# #                 "shift_dir_x": "Вправо", "shift_dir_y": "Вниз",
# #                 "link_x": "X = W", "link_y": "Y = H"
# #             }
# #         }

# #     def apply_rule_to_group(self, group, rule_name):
# #         rule = self.typical_rule_library().get(rule_name)
# #         if not rule:
# #             return
# #         group.update(rule)

# #     def apply_selected_rule_to_group(self):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected:
# #             return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.apply_rule_to_group(self.parametric_groups[idx], self.combo_rule_library.currentText())
# #         self.save_project_config()
# #         self.on_group_selection_changed()
# #         self.update_viewer()

# #     def parse_numeric_text(self, value):
# #         if value is None:
# #             return None
# #         text = str(value).strip()
# #         if not text:
# #             return None
# #         text = text.replace(",", ".")
# #         match = re.search(r"-?\d+(?:\.\d+)?", text)
# #         return float(match.group(0)) if match else None

# #     def format_dimension_value(self, value):
# #         if value is None:
# #             return ""
# #         value = float(value)
# #         return str(int(value)) if abs(value - int(value)) < 0.001 else f"{value:.2f}".rstrip("0").rstrip(".")

# #     def get_dxf_bounds_dimensions(self):
# #         min_x, max_x = float("inf"), float("-inf")
# #         min_y, max_y = float("inf"), float("-inf")
# #         for entity in self.doc.modelspace():
# #             tp = entity.dxftype()
# #             if tp in ("CIRCLE", "ARC"):
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 min_x = min(min_x, cx - r)
# #                 max_x = max(max_x, cx + r)
# #                 min_y = min(min_y, cy - r)
# #                 max_y = max(max_y, cy + r)
# #             elif tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 min_x = min(min_x, x1, x2)
# #                 max_x = max(max_x, x1, x2)
# #                 min_y = min(min_y, y1, y2)
# #                 max_y = max(max_y, y1, y2)
# #         if min_x == float("inf") or min_y == float("inf"):
# #             return None, None
# #         return max_x - min_x, max_y - min_y

# #     def update_dimension_inputs_from_meta(self):
# #         self.apply_folder_dimensions_to_meta()
# #         source_w = self.project_meta.get("source_width")
# #         source_h = self.project_meta.get("source_height")
# #         if source_w is None or source_h is None:
# #             source_w, source_h = self.get_dxf_bounds_dimensions()
# #             self.project_meta["source_width"] = source_w
# #             self.project_meta["source_height"] = source_h
# #             self.update_folder_dimensions_from_meta()

# #         target_w = self.project_meta.get("target_width", source_w)
# #         target_h = self.project_meta.get("target_height", source_h)
# #         self.project_meta["target_width"] = target_w
# #         self.project_meta["target_height"] = target_h
# #         self.update_folder_dimensions_from_meta()

# #         self.input_current_width.setText(self.format_dimension_value(source_w))
# #         self.input_current_height.setText(self.format_dimension_value(source_h))
# #         self.input_target_width.setText(self.format_dimension_value(target_w))
# #         self.input_target_height.setText(self.format_dimension_value(target_h))
# #         self.sync_text_inputs_from_meta()
# #         self.sync_opening_inputs_from_meta()
# #         self.sync_file_growth_axis_combo()
# #         self.update_file_status_panel()

# #     def update_file_status_panel(self):
# #         if not hasattr(self, "lbl_file_status_source"):
# #             return
# #         source_w = self.format_dimension_value(self.project_meta.get("source_width"))
# #         source_h = self.format_dimension_value(self.project_meta.get("source_height"))
# #         target_w = self.format_dimension_value(self.project_meta.get("target_width"))
# #         target_h = self.format_dimension_value(self.project_meta.get("target_height"))
# #         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
# #         target_opening = self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)
# #         opening_names = {"left": "Ліве", "right": "Праве"}
# #         link_x, link_y = self.link_pair_for_mode() if hasattr(self, "link_pair_for_mode") else ("X = W", "Y = H")
# #         db_state = "online" if getattr(getattr(self, "db", None), "available", False) else "offline"
# #         user = self.current_user.get("username") if getattr(self, "current_user", None) else "-"
# #         self.lbl_file_status_source.setText(f"Початковий: {source_w} x {source_h}")
# #         self.lbl_file_status_target.setText(f"Цільовий: {target_w} x {target_h}")
# #         self.lbl_file_status_opening.setText(
# #             f"Відкривання: {opening_names.get(source_opening, source_opening)} -> {opening_names.get(target_opening, target_opening)}"
# #         )
# #         self.lbl_file_status_axis.setText(f"Осі: {link_x}, {link_y}")
# #         model_id = getattr(self, "current_door_model_id", None) or "-"
# #         file_id = getattr(self, "current_project_file_id", None) or "-"
# #         self.lbl_file_status_db.setText(f"БД: {db_state} | користувач: {user} | модель: {model_id} | файл: {file_id}")

# #     def prompt_source_dimensions_on_open(self):

# #         # 1. Спочатку пробуємо завантажити модель з БД
# #         if getattr(self, "current_door_model_id", None):

# #             model_data = self.db.load_door_model(self.current_door_model_id)

# #             if model_data:

# #                 meta = model_data.get("meta", {})

# #                 source_w = meta.get("source_width")
# #                 source_h = meta.get("source_height")
# #                 opening = meta.get("source_door_opening")

# #                 if source_w and source_h:

# #                     self.project_meta["source_width"] = source_w
# #                     self.project_meta["source_height"] = source_h

# #                     self.project_meta["target_width"] = source_w
# #                     self.project_meta["target_height"] = source_h

# #                     self.project_meta["source_door_opening"] = opening or "left"
# #                     self.project_meta["target_door_opening"] = opening or "left"
# #                     self.project_meta["door_opening"] = opening or "left"

# #                     return False

# #         # 2. Якщо DoorModel ще не знайдений — шукаємо по папці
# #         model_id = self.db.find_door_model_by_folder(self.project_dir)

# #         if model_id:

# #             self.current_door_model_id = model_id

# #             model_data = self.db.load_door_model(model_id)

# #             if model_data:

# #                 meta = model_data.get("meta", {})

# #                 self.project_meta["source_width"] = meta.get("source_width")
# #                 self.project_meta["source_height"] = meta.get("source_height")

# #                 self.project_meta["target_width"] = meta.get("source_width")
# #                 self.project_meta["target_height"] = meta.get("source_height")

# #                 opening = meta.get("source_door_opening") or "left"

# #                 self.project_meta["source_door_opening"] = opening
# #                 self.project_meta["target_door_opening"] = opening
# #                 self.project_meta["door_opening"] = opening

# #                 return False

# #     # 3. Тільки якщо в БД нічого немає — показуємо діалог
# #         if self.folder_meta.get("source_width") is not None and self.folder_meta.get("source_height") is not None:
# #             self.apply_folder_dimensions_to_meta()
# #             if not self.folder_meta.get("source_door_opening"):
# #                 opening_text, opening_ok = QInputDialog.getItem(
# #                     self,
# #                     "Початкове відкривання",
# #                     "Яке відкривання у файлах цієї папки?",
# #                     ["Ліве", "Праве"],
# #                     0,
# #                     False
# #                 )
# #                 opening = "right" if opening_ok and "Прав" in opening_text else "left"
# #                 self.project_meta["source_door_opening"] = opening
# #                 self.project_meta["target_door_opening"] = opening
# #                 self.project_meta["door_opening"] = opening
# #                 self.folder_meta["source_door_opening"] = opening
# #                 self.save_folder_config()
# #                 self.save_project_config()
# #             return False
# #         guessed_w, guessed_h = self.get_dxf_bounds_dimensions()
# #         source_w = self.folder_meta.get("source_width") or self.project_meta.get("source_width") or guessed_w
# #         source_h = self.folder_meta.get("source_height") or self.project_meta.get("source_height") or guessed_h
# #         target_w = self.folder_meta.get("target_width") or self.project_meta.get("target_width")
# #         target_h = self.folder_meta.get("target_height") or self.project_meta.get("target_height")

# #         default_text = ""
# #         if source_w is not None and source_h is not None:
# #             default_text = f"{self.format_dimension_value(source_w)} x {self.format_dimension_value(source_h)}"

# #         text, ok = QInputDialog.getText(
# #             self,
# #             "Початковий розмір",
# #             "Введіть початкову ширину і висоту (W x H):",
# #             text=default_text
# #         )
# #         if not ok:
# #             return False

# #         values = [
# #             float(value.replace(",", "."))
# #             for value in re.findall(r"-?\d+(?:[,.]\d+)?", text)
# #         ]
# #         if len(values) < 2:
# #             QMessageBox.warning(
# #                 self,
# #                 "Початковий розмір",
# #                 "Введіть два числа, наприклад: 860 x 2040"
# #             )
# #             return False

# #         source_w, source_h = values[0], values[1]
# #         self.project_meta["source_width"] = source_w
# #         self.project_meta["source_height"] = source_h
# #         self.folder_meta["source_width"] = source_w
# #         self.folder_meta["source_height"] = source_h

# #         if not self.folder_meta.get("source_door_opening"):
# #             opening_text, opening_ok = QInputDialog.getItem(
# #                 self,
# #                 "Початкове відкривання",
# #                 "Яке відкривання у файлах цієї папки?",
# #                 ["Ліве", "Праве"],
# #                 0,
# #                 False
# #             )
# #             opening = "right" if opening_ok and "Прав" in opening_text else "left"
# #             self.project_meta["source_door_opening"] = opening
# #             self.project_meta["target_door_opening"] = opening
# #             self.project_meta["door_opening"] = opening
# #             self.folder_meta["source_door_opening"] = opening

# #         if target_w is None:
# #             target_w = source_w
# #         if target_h is None:
# #             target_h = source_h
# #         self.project_meta["target_width"] = target_w
# #         self.project_meta["target_height"] = target_h
# #         self.folder_meta["target_width"] = target_w
# #         self.folder_meta["target_height"] = target_h

# #         self.save_folder_config()
# #         self.save_project_config()
# #         return True

# #     def remember_source_dimensions(self):
# #         source_w = self.parse_numeric_text(self.input_current_width.text())
# #         source_h = self.parse_numeric_text(self.input_current_height.text())
# #         if source_w is None or source_h is None:
# #             source_w, source_h = self.get_dxf_bounds_dimensions()
# #         self.project_meta["source_width"] = source_w
# #         self.project_meta["source_height"] = source_h
# #         self.project_meta["target_width"] = self.parse_numeric_text(self.input_target_width.text())
# #         self.project_meta["target_height"] = self.parse_numeric_text(self.input_target_height.text())
# #         self.update_folder_dimensions_from_meta()
# #         self.save_project_config()
# #         self.update_dimension_inputs_from_meta()
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Початкові розміри збережено.</font>")

# #     def load_block_filter_list(self):
# #         if not hasattr(self, "block_filter_list"):
# #             return
# #         self.block_filter_list.blockSignals(True)
# #         self.block_filter_list.clear()
# #         valid_names = set()
# #         for group in self.parametric_groups:
# #             name = group.get("name", "")
# #             key = self.get_group_key(group)
# #             valid_names.add(key)
# #             keep = self.block_keep_state.get(key, True)
# #             self.block_keep_state[key] = keep
# #             item = QListWidgetItem(f"{name} ({len(group['handles'])} об.)")
# #             item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
# #             item.setCheckState(Qt.CheckState.Checked if keep else Qt.CheckState.Unchecked)
# #             item.setData(Qt.ItemDataRole.UserRole, key)
# #             self.block_filter_list.addItem(item)
# #         for key in list(self.block_keep_state):
# #             if key not in valid_names:
# #                 del self.block_keep_state[key]
# #         self.block_filter_list.blockSignals(False)

# #     def on_block_keep_state_changed(self, item):
# #         self.record_action_snapshot()
# #         key = item.data(Qt.ItemDataRole.UserRole)
# #         self.block_keep_state[key] = item.checkState() == Qt.CheckState.Checked
# #         self.save_project_config()

# #     def set_text_panel_expanded(self, expanded):
# #         layout = getattr(self, "text_box_layout", None)
# #         if not layout:
# #             return
# #         for index in range(layout.count()):
# #             item = layout.itemAt(index)
# #             widget = item.widget()
# #             child_layout = item.layout()
# #             if widget:
# #                 widget.setVisible(expanded)
# #             elif child_layout:
# #                 for child_index in range(child_layout.count()):
# #                     child_item = child_layout.itemAt(child_index)
# #                     child_widget = child_item.widget()
# #                     if child_widget:
# #                         child_widget.setVisible(expanded)

# #     def get_text_settings(self):
# #         settings = self.default_text_settings()
# #         settings.update(self.project_meta.get("door_text", {}))
# #         self.project_meta["door_text"] = settings
# #         if settings["enabled"] and hasattr(self, "check_door_text_enabled"):
# #             self.check_door_text_enabled.blockSignals(True)
# #             self.check_door_text_enabled.setChecked(True)
# #             self.check_door_text_enabled.blockSignals(False)
# #         return settings

# #     def text_box_width(self, settings):
# #         return max(float(settings.get("width_factor", 120.0)), 1.0)

# #     def text_box_height(self, settings):
# #         return max(float(settings.get("height", 30.0)), 1.0)

# #     def text_display_value(self, text):
# #         return str(text).strip()

# #     def add_centered_text_preview(self, parent_item, text, box_w, box_h, font_name):
# #         if not text:
# #             return
# #         text_item = QGraphicsSimpleTextItem(text, parent_item)
# #         font = text_item.font()
# #         if font_name and font_name.upper() != "STANDARD":
# #             font.setFamily(font_name)
# #         font.setPointSizeF(100.0)
# #         text_item.setFont(font)
# #         text_item.setBrush(QBrush(QColor(255, 255, 255)))
# #         text_item.setZValue(10)
# #         text_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
# #         br = text_item.boundingRect()
# #         if br.width() <= 0 or br.height() <= 0:
# #             return
# #         scale = min((box_w * 0.9) / br.width(), (box_h * 0.75) / br.height())
# #         scale = max(min(scale, 10.0), 0.01)
# #         text_item.setScale(scale)
# #         text_item.setPos(
# #             (box_w - br.width() * scale) * 0.5,
# #             (box_h - br.height() * scale) * 0.5
# #         )

# #     def sync_text_inputs_from_meta(self):
# #         if not hasattr(self, "input_door_text"):
# #             return
# #         settings = self.get_text_settings()
# #         widgets = [
# #             self.check_door_text_enabled,
# #             self.input_door_text,
# #             self.input_text_x,
# #             self.input_text_y,
# #             self.input_text_height,
# #             self.input_text_width_factor,
# #             self.input_text_rotation,
# #             self.combo_text_font
# #         ]
# #         for widget in widgets:
# #             widget.blockSignals(True)
# #         self.check_door_text_enabled.setChecked(bool(settings.get("enabled")))
# #         self.input_door_text.setText(str(settings.get("text", "")))
# #         self.input_text_x.setText(self.format_dimension_value(settings.get("x", 0.0)))
# #         self.input_text_y.setText(self.format_dimension_value(settings.get("y", 0.0)))
# #         self.input_text_height.setText(self.format_dimension_value(settings.get("height", 30.0)))
# #         self.input_text_width_factor.setText(self.format_dimension_value(settings.get("width_factor", 120.0)))
# #         self.input_text_rotation.setText(self.format_dimension_value(settings.get("rotation", 0.0)))
# #         self.combo_text_font.setCurrentText(str(settings.get("font", "STANDARD")))
# #         for widget in widgets:
# #             widget.blockSignals(False)
# #         if hasattr(self, "text_group"):
# #             should_open = bool(
# #                 settings.get("enabled") or
# #                 str(settings.get("text", "")).strip() or
# #                 settings.get("handle")
# #             )
# #             self.text_group.setChecked(should_open)
# #             self.set_text_panel_expanded(should_open)

# #     def collect_text_settings_from_inputs(self):
# #         if not hasattr(self, "input_door_text"):
# #             return self.get_text_settings()
# #         settings = self.get_text_settings()
# #         settings["text"] = self.input_door_text.text()
# #         settings["enabled"] = self.check_door_text_enabled.isChecked()
# #         for key, widget, fallback in (
# #             ("x", self.input_text_x, 0.0),
# #             ("y", self.input_text_y, 0.0),
# #             ("height", self.input_text_height, 30.0),
# #             ("width_factor", self.input_text_width_factor, 120.0),
# #             ("rotation", self.input_text_rotation, 0.0),
# #         ):
# #             value = self.parse_numeric_text(widget.text())
# #             settings[key] = fallback if value is None else value
# #         settings["font"] = self.combo_text_font.currentText().strip() or "STANDARD"
# #         self.project_meta["door_text"] = settings
# #         return settings

# #     def on_text_settings_changed(self, *args):
# #         self.collect_text_settings_from_inputs()
# #         self.save_project_config()

# #     def apply_door_text_from_ui(self):
# #         self.record_action_snapshot()
# #         settings = self.collect_text_settings_from_inputs()
# #         settings["enabled"] = True
# #         self.project_meta["door_text"] = settings
# #         self.check_door_text_enabled.blockSignals(True)
# #         self.check_door_text_enabled.setChecked(True)
# #         self.check_door_text_enabled.blockSignals(False)
# #         self.apply_door_text_to_doc()
# #         self.doc.saveas(self.dxf_path)
# #         self.save_project_config()
# #         self.save_original_geometries()
# #         self.load_entities_into_list()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Текст оновлено на DXF.</font>")

# #     def remove_door_text_block(self):
# #         self.record_action_snapshot()
# #         settings = self.get_text_settings()
# #         handle = settings.get("handle")
# #         if handle:
# #             self.selected_handles.discard(handle)
# #             for group in self.parametric_groups:
# #                 group["handles"].discard(handle)
# #             self.parametric_groups = [g for g in self.parametric_groups if g.get("handles")]
# #         self.remove_managed_text_entity(self.doc, settings)
# #         settings.update({
# #             "enabled": False,
# #             "text": "",
# #             "handle": None
# #         })
# #         self.project_meta["door_text"] = settings
# #         self.check_door_text_enabled.blockSignals(True)
# #         self.check_door_text_enabled.setChecked(False)
# #         self.check_door_text_enabled.blockSignals(False)
# #         self.input_door_text.setText("")
# #         self.doc.saveas(self.dxf_path)
# #         self.save_original_geometries()
# #         self.save_project_config()
# #         self.load_entities_into_list()
# #         self.load_groups_into_list()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Текстовий блок прибрано.</font>")

# #     def get_non_text_dxf_bounds(self):
# #         min_x, min_y = float("inf"), float("inf")
# #         max_x, max_y = float("-inf"), float("-inf")
# #         for entity in self.doc.modelspace():
# #             tp = entity.dxftype()
# #             if tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 min_x = min(min_x, x1, x2)
# #                 max_x = max(max_x, x1, x2)
# #                 min_y = min(min_y, y1, y2)
# #                 max_y = max(max_y, y1, y2)
# #             elif tp in ("CIRCLE", "ARC"):
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 min_x = min(min_x, cx - r)
# #                 max_x = max(max_x, cx + r)
# #                 min_y = min(min_y, cy - r)
# #                 max_y = max(max_y, cy + r)
# #         if min_x == float("inf"):
# #             return None, None, None, None
# #         return min_x, min_y, max_x, max_y

# #     def align_text_box_to_door(self, dimension):
# #         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
# #         if min_x is None:
# #             self.lbl_status_calc.setText("<font color='red'>Не знайдено геометрію дверей для вирівнювання.</font>")
# #             return
# #         self.record_action_snapshot()
# #         settings = self.collect_text_settings_from_inputs()
# #         settings["enabled"] = True
# #         if dimension == "width":
# #             box_w = self.text_box_width(settings)
# #             settings["x"] = min_x + ((max_x - min_x) - box_w) * 0.5
# #             message = "Текстову рамку виставлено по центру ширини полотна."
# #         else:
# #             box_h = self.text_box_height(settings)
# #             settings["y"] = min_y + ((max_y - min_y) - box_h) * 0.5
# #             message = "Текстову рамку виставлено по центру висоти полотна."
# #         self.project_meta["door_text"] = settings
# #         self.apply_door_text_to_doc()
# #         self.doc.saveas(self.dxf_path)
# #         self.save_original_geometries()
# #         self.save_project_config()
# #         self.sync_text_inputs_from_meta()
# #         self.load_entities_into_list()
# #         self.sync_list_from_handles()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>{message}</font>")

# #     def place_empty_door_text_block(self):
# #         self.record_action_snapshot()
# #         settings = self.collect_text_settings_from_inputs()
# #         settings["enabled"] = True
# #         if not str(settings.get("text", "")).strip():
# #             settings["text"] = ""
# #         if settings.get("x", 0.0) == 0.0 and settings.get("y", 0.0) == 0.0:
# #             min_x, min_y, max_x, max_y = self.get_dxf_bounds()
# #             if min_x is not None:
# #                 settings["x"] = min_x + (max_x - min_x) * 0.5
# #                 settings["y"] = min_y + (max_y - min_y) * 0.5
# #         self.project_meta["door_text"] = settings
# #         self.sync_text_inputs_from_meta()
# #         entity = self.apply_door_text_to_doc()
# #         if entity is not None:
# #             self.selected_handles = {entity.dxf.handle}
# #         self.doc.saveas(self.dxf_path)
# #         self.save_original_geometries()
# #         self.load_entities_into_list()
# #         self.sync_list_from_handles()
# #         self.save_project_config()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText("<font color='#4fc3f7'>Текстовий блок можна перетягнути мишкою.</font>")

# #     def on_door_text_item_moved(self, item):
# #         self.record_action_snapshot()
# #         settings = self.get_text_settings()
# #         settings["x"] = float(item.pos().x())
# #         settings["y"] = float(-item.pos().y() - float(settings.get("height", 30.0)))
# #         settings["enabled"] = True
# #         self.project_meta["door_text"] = settings
# #         handle = settings.get("handle")
# #         if handle and handle in self.doc.entitydb:
# #             self.doc.entitydb[handle].dxf.insert = (settings["x"], settings["y"], 0.0)
# #             self.doc.saveas(self.dxf_path)
# #             self.selected_handles = {handle}
# #         self.sync_text_inputs_from_meta()
# #         self.save_project_config()
# #         self.load_entities_into_list()
# #         self.sync_list_from_handles()

# #     def on_door_text_box_moved(self, item):
# #         self.record_action_snapshot()
# #         settings = self.get_text_settings()
# #         settings["x"] = float(item.pos().x() + item.rect().x())
# #         settings["y"] = float(-(item.pos().y() + item.rect().y() + item.rect().height()))
# #         settings["enabled"] = True
# #         self.project_meta["door_text"] = settings
# #         self.apply_door_text_to_doc()
# #         self.doc.saveas(self.dxf_path)
# #         handle = settings.get("handle")
# #         if handle:
# #             self.selected_handles = {handle}
# #         self.sync_text_inputs_from_meta()
# #         self.save_project_config()
# #         self.load_entities_into_list()
# #         self.sync_list_from_handles()
# #         self.update_viewer()

# #     def sync_opening_inputs_from_meta(self):
# #         if not hasattr(self, "combo_door_opening"):
# #             return
# #         opening = self.project_meta.get("door_opening", "left")
# #         self.combo_door_opening.blockSignals(True)
# #         self.combo_door_opening.setCurrentText("Праве" if opening == "right" else "Ліве")
# #         self.combo_door_opening.blockSignals(False)

# #     def on_door_opening_changed(self, text):
# #         self.record_action_snapshot()
# #         self.project_meta["door_opening"] = "right" if "Прав" in text else "left"
# #         self.save_project_config()

# #     def sync_opening_inputs_from_meta(self):
# #         if not hasattr(self, "combo_door_opening"):
# #             return
# #         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
# #         target_opening = self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)
# #         if hasattr(self, "combo_source_door_opening"):
# #             self.combo_source_door_opening.blockSignals(True)
# #             self.combo_source_door_opening.setCurrentText("Праве" if source_opening == "right" else "Ліве")
# #             self.combo_source_door_opening.blockSignals(False)
# #         self.combo_door_opening.blockSignals(True)
# #         self.combo_door_opening.setCurrentText("Праве" if target_opening == "right" else "Ліве")
# #         self.combo_door_opening.blockSignals(False)

# #     def on_source_door_opening_changed(self, text):
# #         self.record_action_snapshot()
# #         self.project_meta["source_door_opening"] = "right" if "Прав" in text else "left"
# #         self.folder_meta["source_door_opening"] = self.project_meta["source_door_opening"]
# #         self.save_folder_config()
# #         self.save_project_config()
# #         self.update_file_status_panel()

# #     def on_door_opening_changed(self, text):
# #         self.record_action_snapshot()
# #         self.project_meta["target_door_opening"] = "right" if "Прав" in text else "left"
# #         self.project_meta["door_opening"] = self.project_meta["target_door_opening"]
# #         self.save_project_config()
# #         self.update_file_status_panel()

# #     def get_dxf_bounds(self, doc=None):
# #         doc = doc or self.doc
# #         min_x, min_y = float("inf"), float("inf")
# #         max_x, max_y = float("-inf"), float("-inf")
# #         for entity in doc.modelspace():
# #             tp = entity.dxftype()
# #             if tp in ("CIRCLE", "ARC"):
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 min_x = min(min_x, cx - r)
# #                 max_x = max(max_x, cx + r)
# #                 min_y = min(min_y, cy - r)
# #                 max_y = max(max_y, cy + r)
# #             elif tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 min_x = min(min_x, x1, x2)
# #                 max_x = max(max_x, x1, x2)
# #                 min_y = min(min_y, y1, y2)
# #                 max_y = max(max_y, y1, y2)
# #             elif tp == "TEXT":
# #                 settings = self.get_text_settings()
# #                 if settings.get("handle") == entity.dxf.handle:
# #                     x = float(settings.get("x", 0.0))
# #                     y = float(settings.get("y", 0.0))
# #                     w = self.text_box_width(settings)
# #                     h = self.text_box_height(settings)
# #                 else:
# #                     x, y, _ = entity.dxf.insert
# #                     h = float(entity.dxf.height)
# #                     w = max(len(str(entity.dxf.text).strip()), 1) * h * 0.6 * float(getattr(entity.dxf, "width", 1.0))
# #                 min_x = min(min_x, x)
# #                 max_x = max(max_x, x + w)
# #                 min_y = min(min_y, y)
# #                 max_y = max(max_y, y + h)
# #         if min_x == float("inf"):
# #             return None, None, None, None
# #         return min_x, min_y, max_x, max_y

# #     def entity_bbox(self, entity):
# #         tp = entity.dxftype()
# #         if tp in ("CIRCLE", "ARC"):
# #             cx, cy, _ = entity.dxf.center
# #             r = entity.dxf.radius
# #             return (cx - r, cy - r, cx + r, cy + r)
# #         if tp == "LINE":
# #             x1, y1, _ = entity.dxf.start
# #             x2, y2, _ = entity.dxf.end
# #             return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
# #         if tp in ("TEXT", "MTEXT"):
# #             settings = self.get_text_settings()
# #             if settings.get("handle") == entity.dxf.handle:
# #                 x = float(settings.get("x", 0.0))
# #                 y = float(settings.get("y", 0.0))
# #                 w = self.text_box_width(settings)
# #                 h = self.text_box_height(settings)
# #             else:
# #                 x, y, _ = entity.dxf.insert
# #                 h = float(entity.dxf.height)
# #                 w = max(len(str(entity.dxf.text).strip()), 1) * h * 0.6 * float(getattr(entity.dxf, "width", 1.0))
# #             return (x, y, x + w, y + h)
# #         return None

# #     def transform_managed_text_settings(self, mode, cx, cy):
# #         settings = self.get_text_settings()
# #         handle = settings.get("handle")
# #         if not handle or handle not in self.selected_handles:
# #             return
# #         box_w = self.text_box_width(settings)
# #         box_h = self.text_box_height(settings)
# #         center_x = float(settings.get("x", 0.0)) + box_w * 0.5
# #         center_y = float(settings.get("y", 0.0)) + box_h * 0.5
# #         dx = center_x - cx
# #         dy = center_y - cy
# #         rotation = float(settings.get("rotation", 0.0))

# #         if mode == "ROT90":
# #             center_x, center_y = cx - dy, cy + dx
# #             rotation += 90.0
# #         elif mode == "ROT180":
# #             center_x, center_y = cx - dx, cy - dy
# #             rotation += 180.0
# #         elif mode == "ROT270":
# #             center_x, center_y = cx + dy, cy - dx
# #             rotation += 270.0
# #         elif mode == "MIRROR_H":
# #             center_x = 2 * cx - center_x
# #             rotation = 180.0 - rotation
# #         elif mode == "MIRROR_V":
# #             center_y = 2 * cy - center_y
# #             rotation = -rotation
# #         else:
# #             return

# #         settings["x"] = center_x - box_w * 0.5
# #         settings["y"] = center_y - box_h * 0.5
# #         settings["rotation"] = rotation % 360.0
# #         self.project_meta["door_text"] = settings
# #         self.apply_door_text_to_doc()

# #     def mirror_entity_horizontally(self, entity, axis_x):
# #         tp = entity.dxftype()
# #         if tp == "LINE":
# #             sx, sy, sz = entity.dxf.start
# #             ex, ey, ez = entity.dxf.end
# #             entity.dxf.start = (2 * axis_x - sx, sy, sz)
# #             entity.dxf.end = (2 * axis_x - ex, ey, ez)
# #         elif tp in ("CIRCLE", "ARC"):
# #             cx, cy, cz = entity.dxf.center
# #             entity.dxf.center = (2 * axis_x - cx, cy, cz)
# #             if tp == "ARC":
# #                 old_start = float(entity.dxf.start_angle)
# #                 old_end = float(entity.dxf.end_angle)
# #                 entity.dxf.start_angle = (180.0 - old_end) % 360.0
# #                 entity.dxf.end_angle = (180.0 - old_start) % 360.0
# #         elif tp == "TEXT":
# #             x, y, z = entity.dxf.insert
# #             entity.dxf.insert = (2 * axis_x - x, y, z)
# #             entity.dxf.rotation = (180.0 - float(getattr(entity.dxf, "rotation", 0.0))) % 360.0

# #     def mirror_entity_vertically(self, entity, axis_y):
# #         tp = entity.dxftype()
# #         if tp == "LINE":
# #             sx, sy, sz = entity.dxf.start
# #             ex, ey, ez = entity.dxf.end
# #             entity.dxf.start = (sx, 2 * axis_y - sy, sz)
# #             entity.dxf.end = (ex, 2 * axis_y - ey, ez)
# #         elif tp in ("CIRCLE", "ARC"):
# #             cx, cy, cz = entity.dxf.center
# #             entity.dxf.center = (cx, 2 * axis_y - cy, cz)
# #             if tp == "ARC":
# #                 old_start = float(entity.dxf.start_angle)
# #                 old_end = float(entity.dxf.end_angle)
# #                 entity.dxf.start_angle = (-old_end) % 360.0
# #                 entity.dxf.end_angle = (-old_start) % 360.0
# #         elif tp == "TEXT":
# #             x, y, z = entity.dxf.insert
# #             entity.dxf.insert = (x, 2 * axis_y - y, z)
# #             entity.dxf.rotation = (-float(getattr(entity.dxf, "rotation", 0.0))) % 360.0


# #     def flip_x_direction(self, direction):
# #         if direction == "Вправо":
# #             return "Вліво"
# #         if direction == "Вліво":
# #             return "Вправо"
# #         return direction
    
# #     def flip_y_direction(self, direction):
# #         if direction == "Вгору":
# #             return "Вниз"
# #         if direction == "Вниз":
# #             return "Вгору"
# #         return direction

# #     def mirror_door_opening(self):
# #         min_x, min_y, max_x, max_y = self.get_dxf_bounds()
# #         if min_x is None:
# #             return

# #         self.record_action_snapshot()

# #         link_x, link_y = self.link_pair_for_mode()
# #         mirror_by_y = link_y == "Y = W"

# #         axis_x = (min_x + max_x) * 0.5
# #         axis_y = (min_y + max_y) * 0.5

# #         for entity in self.doc.modelspace():
# #             tp = entity.dxftype()

# #             if tp == "LINE":
# #                 sx, sy, sz = entity.dxf.start
# #                 ex, ey, ez = entity.dxf.end

# #                 if mirror_by_y:
# #                     entity.dxf.start = (sx, 2 * axis_y - sy, sz)
# #                     entity.dxf.end = (ex, 2 * axis_y - ey, ez)
# #                 else:
# #                     entity.dxf.start = (2 * axis_x - sx, sy, sz)
# #                     entity.dxf.end = (2 * axis_x - ex, ey, ez)

# #             elif tp in ("CIRCLE", "ARC"):
# #                 cx, cy, cz = entity.dxf.center

# #                 if mirror_by_y:
# #                     entity.dxf.center = (cx, 2 * axis_y - cy, cz)

# #                     if tp == "ARC":
# #                         old_start = float(entity.dxf.start_angle)
# #                         old_end = float(entity.dxf.end_angle)
# #                         entity.dxf.start_angle = (-old_end) % 360.0
# #                         entity.dxf.end_angle = (-old_start) % 360.0

# #                 else:
# #                     entity.dxf.center = (2 * axis_x - cx, cy, cz)

# #                     if tp == "ARC":
# #                         old_start = float(entity.dxf.start_angle)
# #                         old_end = float(entity.dxf.end_angle)
# #                         entity.dxf.start_angle = (180.0 - old_end) % 360.0
# #                         entity.dxf.end_angle = (180.0 - old_start) % 360.0

# #             elif tp == "TEXT":
# #                 x, y, z = entity.dxf.insert

# #                 if mirror_by_y:
# #                     entity.dxf.insert = (x, 2 * axis_y - y, z)
# #                 else:
# #                     entity.dxf.insert = (2 * axis_x - x, y, z)

# #                 entity.dxf.rotation = float(getattr(entity.dxf, "rotation", 0.0))

# #         settings = self.get_text_settings()

# #         if mirror_by_y:
# #             settings["y"] = 2 * axis_y - float(settings.get("y", 0.0))
# #         else:
# #             settings["x"] = 2 * axis_x - (
# #                 float(settings.get("x", 0.0)) + self.text_box_width(settings)
# #             )

# #         self.project_meta["door_text"] = settings
# #         self.apply_door_text_to_doc()

# #         for group in self.parametric_groups:
# #             if mirror_by_y:
# #                 group["growth_dir_y"] = self.flip_y_direction(
# #                     group.get("growth_dir_y", "Вгору")
# #                 )
# #                 group["shift_dir_y"] = self.flip_y_direction(
# #                     group.get("shift_dir_y", "Вгору")
# #                 )
# #             else:
# #                 group["growth_dir_x"] = self.flip_x_direction(
# #                     group.get("growth_dir_x", "Вправо")
# #                 )
# #                 group["shift_dir_x"] = self.flip_x_direction(
# #                     group.get("shift_dir_x", "Вправо")
# #                 )

# #         self.project_meta["door_opening"] = (
# #             "right" if self.project_meta.get("door_opening") != "right" else "left"
# #         )
# #         self.project_meta["target_door_opening"] = self.project_meta["door_opening"]

# #         self.doc.saveas(self.dxf_path)
# #         self.save_original_geometries()
# #         self.apply_axis_link_mode_to_groups()
# #         self.save_project_config()
# #         self.sync_opening_inputs_from_meta()
# #         self.sync_text_inputs_from_meta()
# #         self.sync_link_combos_from_file_mode()
# #         self.load_entities_into_list()
# #         self.update_viewer()
# #         self.update_file_status_panel()

# #         self.lbl_status_calc.setText(
# #             "<font color='#a5d6a7'>Відкривання дзеркально змінено.</font>"
# #         )

# #     def group_original_bbox(self, group):
# #         min_x, min_y = float("inf"), float("inf")
# #         max_x, max_y = float("-inf"), float("-inf")
# #         for handle in group.get("handles", set()):
# #             orig = self.original_geometries.get(handle)
# #             if not orig:
# #                 continue
# #             if orig["type"] in ("CIRCLE", "ARC"):
# #                 cx, cy, _ = orig["center"]
# #                 r = orig["radius"]
# #                 min_x = min(min_x, cx - r)
# #                 max_x = max(max_x, cx + r)
# #                 min_y = min(min_y, cy - r)
# #                 max_y = max(max_y, cy + r)
# #             elif orig["type"] == "LINE":
# #                 sx, sy, _ = orig["start"]
# #                 ex, ey, _ = orig["end"]
# #                 min_x = min(min_x, sx, ex)
# #                 max_x = max(max_x, sx, ex)
# #                 min_y = min(min_y, sy, ey)
# #                 max_y = max(max_y, sy, ey)
# #             elif orig["type"] == "TEXT":
# #                 x, y, _ = orig["insert"]
# #                 h = float(orig["height"])
# #                 w = max(len(str(orig.get("text", "")).strip()), 1) * h * 0.6 * float(orig.get("width", 1.0))
# #                 min_x = min(min_x, x)
# #                 max_x = max(max_x, x + w)
# #                 min_y = min(min_y, y)
# #                 max_y = max(max_y, y + h)
# #         if min_x == float("inf"):
# #             return None
# #         return (min_x, min_y, max_x, max_y)

# #     def simulated_group_bbox(self, group, cur_w, cur_h, target_w, target_h):
# #         bbox = self.group_original_bbox(group)
# #         if not bbox:
# #             return None
# #         min_x, min_y, max_x, max_y = bbox
# #         delta_w = target_w - cur_w
# #         delta_h = target_h - cur_h
# #         shift_v, growth_v = ParametricEngine.get_transform(delta_w, delta_h, group)
# #         min_x += shift_v[0]
# #         max_x += shift_v[0]
# #         min_y += shift_v[1]
# #         max_y += shift_v[1]

# #         if group.get("growth_dir_x", "Центр") == "Вправо":
# #             max_x += growth_v[0]
# #         elif group.get("growth_dir_x", "Центр") == "Вліво":
# #             min_x -= growth_v[0]
# #         else:
# #             min_x -= growth_v[0] * 0.5
# #             max_x += growth_v[0] * 0.5

# #         if group.get("growth_dir_y", "Центр") == "Вгору":
# #             max_y += growth_v[1]
# #         elif group.get("growth_dir_y", "Центр") == "Вниз":
# #             min_y -= growth_v[1]
# #         else:
# #             min_y -= growth_v[1] * 0.5
# #             max_y += growth_v[1] * 0.5

# #         return (min(min_x, max_x), min(min_y, max_y), max(min_x, max_x), max(min_y, max_y))

# #     def bboxes_overlap(self, a, b, gap=0.5):
# #         return not (
# #             a[2] <= b[0] + gap or
# #             b[2] <= a[0] + gap or
# #             a[3] <= b[1] + gap or
# #             b[3] <= a[1] + gap
# #         )

# #     def has_new_group_overlap(self, cur_w, cur_h, target_w, target_h):
# #         groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
# #         if len(groups) < 2:
# #             return False
# #         original_bboxes = [self.group_original_bbox(g) for g in groups]
# #         simulated_bboxes = [self.simulated_group_bbox(g, cur_w, cur_h, target_w, target_h) for g in groups]
# #         for i in range(len(groups)):
# #             for j in range(i + 1, len(groups)):
# #                 if self.bboxes_overlap(original_bboxes[i], original_bboxes[j]):
# #                     continue
# #                 if simulated_bboxes[i] and simulated_bboxes[j] and self.bboxes_overlap(simulated_bboxes[i], simulated_bboxes[j]):
# #                     return True
# #         return False

# #     def find_min_safe_axis(self, cur_w, cur_h, axis):
# #         if axis == "width":
# #             if not self.has_new_group_overlap(cur_w, cur_h, 1.0, cur_h):
# #                 return 1.0
# #             low, high = 1.0, cur_w
# #             for _ in range(32):
# #                 mid = (low + high) * 0.5
# #                 if self.has_new_group_overlap(cur_w, cur_h, mid, cur_h):
# #                     low = mid
# #                 else:
# #                     high = mid
# #             return high
# #         if not self.has_new_group_overlap(cur_w, cur_h, cur_w, 1.0):
# #             return 1.0
# #         low, high = 1.0, cur_h
# #         for _ in range(32):
# #             mid = (low + high) * 0.5
# #             if self.has_new_group_overlap(cur_w, cur_h, cur_w, mid):
# #                 low = mid
# #             else:
# #                 high = mid
# #         return high

# #     def find_minimum_safe_size(self):
# #         try:
# #             cur_w = float(self.input_current_width.text().strip())
# #             cur_h = float(self.input_current_height.text().strip())
# #         except ValueError:
# #             self.lbl_status_calc.setText("<font color='red'>Спочатку задайте початкову ширину і висоту.</font>")
# #             return
# #         if len(self.parametric_groups) < 2:
# #             self.lbl_status_calc.setText("<font color='red'>Потрібно мінімум дві параметричні групи для перевірки накладання.</font>")
# #             return
# #         min_w = self.find_min_safe_axis(cur_w, cur_h, "width")
# #         min_h = self.find_min_safe_axis(cur_w, cur_h, "height")
# #         self.lbl_status_calc.setText(
# #             f"<font color='#4fc3f7'>Мінімум без нового накладання: W≈{min_w:.1f} мм, H≈{min_h:.1f} мм</font>"
# #         )

# #     def validate_target_size_or_warn(self, cur_w, cur_h, target_w, target_h):
# #         if len(self.parametric_groups) < 2:
# #             return True
# #         if not self.has_new_group_overlap(cur_w, cur_h, target_w, target_h):
# #             return True
# #         min_w = self.find_min_safe_axis(cur_w, cur_h, "width")
# #         min_h = self.find_min_safe_axis(cur_w, cur_h, "height")
# #         self.lbl_status_calc.setText(
# #             "<font color='red'>Заданий розмір дає накладання блоків. "
# #             f"Безпечний мінімум: W≈{min_w:.1f} мм, H≈{min_h:.1f} мм.</font>"
# #         )
# #         return False

# #     def get_text_style_name(self, doc, font_name):
# #         font = (font_name or "STANDARD").strip()
# #         if font.upper() == "STANDARD":
# #             return "STANDARD"
# #         style_name = "TXT_" + re.sub(r"[^0-9A-Za-z_]+", "_", font.upper()).strip("_")
# #         font_files = {
# #             "ARIAL": "arial.ttf",
# #             "ARIAL NARROW": "arialn.ttf",
# #             "SIMPLEX": "simplex.shx"
# #         }
# #         if style_name not in doc.styles:
# #             doc.styles.new(style_name, dxfattribs={"font": font_files.get(font.upper(), font)})
# #         return style_name

# #     def remove_managed_text_entity(self, doc=None, settings=None):
# #         doc = doc or self.doc
# #         settings = settings or self.get_text_settings()
# #         handle = settings.get("handle")
# #         if handle and handle in doc.entitydb:
# #             try:
# #                 doc.modelspace().delete_entity(doc.entitydb[handle])
# #             except Exception:
# #                 pass
# #         settings["handle"] = None

# #     def apply_door_text_to_doc(self, doc=None):
# #         doc = doc or self.doc
# #         settings = self.get_text_settings()
# #         if not settings.get("enabled"):
# #             self.remove_managed_text_entity(doc, settings)
# #             return None
# #         text = self.text_display_value(settings.get("text", ""))
# #         dxf_text = text if text else " "
# #         style_name = self.get_text_style_name(doc, settings.get("font", "STANDARD"))
# #         handle = settings.get("handle")
# #         entity = doc.entitydb[handle] if handle and handle in doc.entitydb else None
# #         if entity is None or entity.dxftype() != "TEXT":
# #             entity = doc.modelspace().add_text(dxf_text)
# #             settings["handle"] = entity.dxf.handle
# #         box_x = float(settings.get("x", 0.0))
# #         box_y = float(settings.get("y", 0.0))
# #         box_w = self.text_box_width(settings)
# #         box_h = self.text_box_height(settings)
# #         text_h = max(box_h * 0.55, 0.1)
# #         center_x = box_x + box_w * 0.5
# #         center_y = box_y + box_h * 0.5
# #         entity.dxf.text = dxf_text
# #         entity.dxf.height = text_h
# #         entity.dxf.style = style_name
# #         entity.dxf.width = 1.0
# #         entity.set_placement((center_x, center_y, 0.0), align=TextEntityAlignment.MIDDLE_CENTER)
# #         entity.dxf.rotation = float(settings.get("rotation", 0.0))
# #         self.project_meta["door_text"] = settings
# #         return entity

# #     def normalize_key(self, value):
# #         text = str(value).strip().lower()
# #         replacements = {
# #             "ширина": "target_width",
# #             "width": "target_width",
# #             "w": "target_width",
# #             "нова ширина": "target_width",
# #             "target_width": "target_width",
# #             "висота": "target_height",
# #             "height": "target_height",
# #             "h": "target_height",
# #             "нова висота": "target_height",
# #             "target_height": "target_height",
# #             "поточна ширина": "source_width",
# #             "source_width": "source_width",
# #             "current_width": "source_width",
# #             "початкова ширина": "source_width",
# #             "поточна висота": "source_height",
# #             "source_height": "source_height",
# #             "current_height": "source_height",
# #             "початкова висота": "source_height",
# #             "лишити": "keep_blocks",
# #             "keep": "keep_blocks",
# #             "keep_blocks": "keep_blocks",
# #             "видалити": "delete_blocks",
# #             "delete": "delete_blocks",
# #             "delete_blocks": "delete_blocks",
# #             "текст": "text",
# #             "text": "text",
# #             "door_text": "text",
# #             "текст x": "text_x",
# #             "text_x": "text_x",
# #             "x_text": "text_x",
# #             "текст y": "text_y",
# #             "text_y": "text_y",
# #             "y_text": "text_y",
# #             "розмір шрифту": "font_size",
# #             "висота тексту": "font_size",
# #             "font_size": "font_size",
# #             "text_height": "font_size",
# #             "шрифт": "font",
# #             "font": "font",
# #             "ширина тексту": "text_width",
# #             "text_width": "text_width",
# #             "width_factor": "text_width",
# #             "поворот тексту": "text_rotation",
# #             "text_rotation": "text_rotation",
# #             "rotation": "text_rotation",
# #         }
# #         return replacements.get(text, text)

# #     def read_csv_rows(self, path):
# #         for encoding in ("utf-8-sig", "cp1251", "utf-8"):
# #             try:
# #                 with open(path, newline="", encoding=encoding) as f:
# #                     return [row for row in csv.reader(f) if any(str(c).strip() for c in row)]
# #             except UnicodeDecodeError:
# #                 continue
# #         return []

# #     def read_xlsx_rows(self, path):
# #         ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
# #         with zipfile.ZipFile(path) as zf:
# #             shared = []
# #             if "xl/sharedStrings.xml" in zf.namelist():
# #                 root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
# #                 for si in root.findall("a:si", ns):
# #                     shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
# #             sheet_name = "xl/worksheets/sheet1.xml"
# #             root = ET.fromstring(zf.read(sheet_name))
# #             rows = []
# #             for row in root.findall(".//a:row", ns):
# #                 values = []
# #                 for cell in row.findall("a:c", ns):
# #                     raw = cell.find("a:v", ns)
# #                     text = raw.text if raw is not None else ""
# #                     if cell.attrib.get("t") == "s" and text:
# #                         text = shared[int(text)]
# #                     values.append(text)
# #                 if any(str(v).strip() for v in values):
# #                     rows.append(values)
# #             return rows

# #     def import_parameters_from_table(self):
# #         path, _ = QFileDialog.getOpenFileName(
# #             self,
# #             "Виберіть Excel/CSV з параметрами",
# #             self.project_dir,
# #             "Tables (*.xlsx *.csv);;All Files (*)"
# #         )
# #         if not path:
# #             return
# #         try:
# #             rows = self.read_xlsx_rows(path) if path.lower().endswith(".xlsx") else self.read_csv_rows(path)
# #             params = self.extract_table_parameters(rows)
# #             self.record_action_snapshot()
# #             self.apply_imported_parameters(params)
# #             self.apply_door_text_to_doc()
# #             self.doc.saveas(self.dxf_path)
# #             self.save_project_config()
# #             self.save_original_geometries()
# #             self.update_dimension_inputs_from_meta()
# #             self.sync_text_inputs_from_meta()
# #             self.load_entities_into_list()
# #             self.update_viewer()
# #             self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Параметри імпортовано: {os.path.basename(path)}</font>")
# #         except Exception as e:
# #             self.lbl_status_calc.setText(f"<font color='red'>Помилка імпорту: {e}</font>")

# #     def quick_order_wizard(self):
# #         default_text = f"{self.input_target_width.text()}x{self.input_target_height.text()}"
# #         text, ok = QInputDialog.getText(
# #             self,
# #             "Нове замовлення",
# #             "Введіть новий розмір W x H:",
# #             text=default_text
# #         )
# #         if not ok:
# #             return
# #         nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[,.]\d+)?", text)]
# #         if len(nums) < 2:
# #             self.lbl_status_calc.setText("<font color='red'>Введіть два числа: ширина і висота.</font>")
# #             return
# #         if not self.input_current_width.text().strip() or not self.input_current_height.text().strip():
# #             self.update_dimension_inputs_from_meta()
# #         self.input_target_width.setText(self.format_dimension_value(nums[0]))
# #         self.input_target_height.setText(self.format_dimension_value(nums[1]))
# #         self.export_model_dxf_with_dimensions()

# #     def extract_table_parameters(self, rows):
# #         params = {}
# #         if not rows:
# #             return params

# #         headers = [self.normalize_key(c) for c in rows[0]]
# #         if "target_width" in headers or "target_height" in headers:
# #             for row in rows[1:]:
# #                 for idx, key in enumerate(headers):
# #                     if idx >= len(row):
# #                         continue
# #                     value = row[idx]
# #                     if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
# #                         num = self.parse_numeric_text(value)
# #                         if num is not None:
# #                             params[key] = num
# #                     elif key in ("text", "font"):
# #                         params[key] = str(value).strip()
# #                     elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
# #                         opening = self.parse_door_opening_value(value)
# #                         if opening:
# #                             params[key] = opening
# #                     elif key in ("keep_blocks", "delete_blocks"):
# #                         params.setdefault(key, []).extend(self.split_block_names(value))
# #             return params

# #         for row in rows:
# #             if len(row) < 2:
# #                 continue
# #             key = self.normalize_key(row[0])
# #             value = row[1]
# #             if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
# #                 num = self.parse_numeric_text(value)
# #                 if num is not None:
# #                     params[key] = num
# #             elif key in ("text", "font"):
# #                 params[key] = str(value).strip()
# #             elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
# #                 opening = self.parse_door_opening_value(value)
# #                 if opening:
# #                     params[key] = opening
# #             elif key in ("keep_blocks", "delete_blocks"):
# #                 params[key] = self.split_block_names(value)
# #         return params

# #     def split_block_names(self, value):
# #         if value is None:
# #             return []
# #         return [part.strip() for part in re.split(r"[,;\n]+", str(value)) if part.strip()]

# #     def apply_imported_parameters(self, params, refresh_ui=True, save_config=True):
# #         for key in ("source_width", "source_height", "target_width", "target_height"):
# #             if key in params:
# #                 self.project_meta[key] = params[key]
# #         source_opening = params.get("source_door_opening", params.get("source_opening"))
# #         target_opening = params.get("target_door_opening", params.get("target_opening", params.get("door_opening")))
# #         if source_opening:
# #             self.project_meta["source_door_opening"] = source_opening
# #         if target_opening:
# #             self.project_meta["target_door_opening"] = target_opening
# #             self.project_meta["door_opening"] = target_opening
# #         if save_config:
# #             self.update_folder_dimensions_from_meta()
# #         text_settings = self.get_text_settings()
# #         text_key_map = {
# #             "text": "text",
# #             "text_x": "x",
# #             "text_y": "y",
# #             "font_size": "height",
# #             "text_width": "width_factor",
# #             "text_rotation": "rotation",
# #             "font": "font"
# #         }
# #         for source_key, target_key in text_key_map.items():
# #             if source_key in params:
# #                 text_settings[target_key] = params[source_key]
# #         if "text" in params and str(params["text"]).strip():
# #             text_settings["enabled"] = True
# #             if "text_x" not in params and "text_y" not in params:
# #                 self.lbl_status_calc.setText("<font color='#4fc3f7'>Текст підставлено в попередньо задану рамку.</font>")
# #         self.project_meta["door_text"] = text_settings
# #         if "keep_blocks" in params and params["keep_blocks"]:
# #             keep_set = set(params["keep_blocks"])
# #             for group in self.parametric_groups:
# #                 name = group.get("name", "")
# #                 key = self.get_group_key(group)
# #                 self.block_keep_state[key] = key in keep_set or name in keep_set
# #         if "delete_blocks" in params and params["delete_blocks"]:
# #             delete_set = set(params["delete_blocks"])
# #             for group in self.parametric_groups:
# #                 name = group.get("name", "")
# #                 key = self.get_group_key(group)
# #                 if key in delete_set or name in delete_set:
# #                     self.block_keep_state[key] = False
# #         if refresh_ui:
# #             self.update_dimension_inputs_from_meta()
# #             self.sync_opening_inputs_from_meta()
# #             self.sync_text_inputs_from_meta()
# #             self.load_block_filter_list()
# #         if save_config:
# #             self.save_project_config()

# #     def sanitize_filename_part(self, value):
# #         text = self.format_dimension_value(value)
# #         return re.sub(r"[^0-9A-Za-zА-Яа-я_\-.]+", "_", text)

# #     def parse_door_opening_value(self, value):
# #         text = str(value or "").strip().lower()
# #         if not text:
# #             return None
# #         if text in ("right", "r", "prave") or "прав" in text or "right" in text:
# #             return "right"
# #         if text in ("left", "l", "live") or "лів" in text or "лев" in text or "left" in text:
# #             return "left"
# #         return None

# #     def get_export_output_dir(self, target_w, target_h):
# #         width_part = self.sanitize_filename_part(target_w)
# #         height_part = self.sanitize_filename_part(target_h)
# #         folder_name = f"generated_{width_part}_{height_part}"
# #         output_dir = os.path.join(self.project_dir, folder_name)
# #         os.makedirs(output_dir, exist_ok=True)
# #         return output_dir

# #     def build_export_path(self, target_w, target_h):
# #         base_name = os.path.splitext(os.path.basename(self.dxf_path))[0]
# #         base_name = re.sub(r"(?<!\d)\d{3,5}_\d{3,5}(?!\d)", "", base_name).strip("_- ")
# #         width_part = self.sanitize_filename_part(target_w)
# #         height_part = self.sanitize_filename_part(target_h)
# #         name = f"{base_name}_{width_part}_{height_part}.DXF"
# #         output_dir = self.get_export_output_dir(target_w, target_h)
# #         path = os.path.join(output_dir, name)
# #         counter = 2
# #         while os.path.exists(path):
# #             name = f"{base_name}_{width_part}_{height_part}_{counter}.DXF"
# #             path = os.path.join(output_dir, name)
# #             counter += 1
# #         return path

# #     def export_target_opening(self):
# #         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
# #         return self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)

# #     def export_needs_opening_mirror(self):
# #         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
# #         return source_opening != self.export_target_opening()

# #     def apply_opening_to_export_doc(self, export_doc):
# #         if not self.export_needs_opening_mirror():
# #             return
# #         min_x, _min_y, max_x, _max_y = self.get_dxf_bounds(export_doc)
# #         if min_x is None:
# #             return
# #         axis_x = (min_x + max_x) * 0.5
# #         for entity in export_doc.modelspace():
# #             self.mirror_entity_horizontally(entity, axis_x)

# #     def save_generated_folder_config(self, output_dir, target_w, target_h, target_opening):
# #         folder_meta = self.default_folder_meta()
# #         folder_meta.update({
# #             "source_width": target_w,
# #             "source_height": target_h,
# #             "target_width": target_w,
# #             "target_height": target_h,
# #             "source_door_opening": target_opening
# #         })
# #         try:
# #             with open(os.path.join(output_dir, "_folder_params.json"), "w", encoding="utf-8") as f:
# #                 json.dump(folder_meta, f, indent=4, ensure_ascii=False)
# #         except Exception as e:
# #             print(f"Generated folder config save error: {e}")

# #     def save_generated_project_config(self, export_path, target_w, target_h):
# #         target_opening = self.export_target_opening()
# #         generated_meta = copy.deepcopy(self.project_meta)
# #         generated_meta.update({
# #             "source_width": target_w,
# #             "source_height": target_h,
# #             "target_width": target_w,
# #             "target_height": target_h,
# #             "source_door_opening": target_opening,
# #             "target_door_opening": target_opening,
# #             "door_opening": target_opening
# #         })
# #         generated_meta["keep_blocks"] = [
# #             key for key, keep in self.block_keep_state.items() if keep
# #         ]
# #         generated_meta["delete_blocks"] = [
# #             key for key, keep in self.block_keep_state.items() if not keep
# #         ]
# #         groups_data = []
# #         for group in self.parametric_groups:
# #             self.get_group_key(group)
# #             group_data = group.copy()
# #             group_data["handles"] = list(group.get("handles", []))
# #             groups_data.append(group_data)
# #         config_path = f"{os.path.splitext(export_path)[0]}_config.json"
# #         try:
# #             with open(config_path, "w", encoding="utf-8") as f:
# #                 json.dump({"meta": generated_meta, "groups": groups_data}, f, indent=4, ensure_ascii=False)
# #             self.save_generated_folder_config(os.path.dirname(export_path), target_w, target_h, target_opening)
# #         except Exception as e:
# #             print(f"Generated project config save error: {e}")

# #     def is_generated_dimension_dxf(self, file_name):
# #         base_name = os.path.splitext(file_name)[0]
# #         return re.search(r"_\d{2,5}_\d{2,5}(?:_\d+)?$", base_name) is not None

# #     def get_folder_source_dxf_files(self):
# #         try:
# #             files = os.listdir(self.project_dir)
# #         except Exception:
# #             return []
# #         return sorted(
# #             file_name for file_name in files
# #             if file_name.lower().endswith(".dxf")
# #             and not self.is_generated_dimension_dxf(file_name)
# #         )

# #     def preview_parametric_scale(self):
# #         self.record_action_snapshot()
# #         if self.debug_output:
# #             print("\n" + "=" * 90)
# #             print("[PREVIEW DEBUG] START PREVIEW")
# #             print("[PREVIEW DEBUG] Перегляд рахує не від файлу на диску, а від self.original_geometries")
# #             print(f"[PREVIEW DEBUG] base handles={len(self.original_geometries)}")
# #             print(f"[PREVIEW DEBUG] source W/H={self.project_meta.get('source_width')} / {self.project_meta.get('source_height')}")
# #             print(f"[PREVIEW DEBUG] target W/H={self.input_target_width.text()} / {self.input_target_height.text()}")
# #             print("=" * 90)
# #         if self.process_parametric_percentage_scale(save_result=False, record_history=False):
# #             self.lbl_status_calc.setText("<font color='#4fc3f7'>Перегляд застосовано тільки на екрані. Файл ще не збережено.</font>")

# #     def restore_current_dxf_from_disk(self):
# #         if not os.path.exists(self.dxf_path):
# #             return
# #         self.record_action_snapshot()
# #         self.doc = ezdxf.readfile(self.dxf_path)
# #         self.save_original_geometries()
# #         self.update_dimension_inputs_from_meta()
# #         self.update_viewer()
# #         self.load_entities_into_list()
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Повернуто стан з відкритого DXF.</font>")

# #     def export_new_dxf_with_dimensions(self):
# #         self.collect_text_settings_from_inputs()
# #         original_dxf_path = self.dxf_path
# #         original_bytes = None
# #         if os.path.exists(self.dxf_path):
# #             with open(self.dxf_path, "rb") as f:
# #                 original_bytes = f.read()
# #         original_meta = copy.deepcopy(self.project_meta)
# #         original_groups = copy.deepcopy(self.parametric_groups)
# #         original_keep_state = copy.deepcopy(self.block_keep_state)

# #         self.project_meta["source_width"] = self.parse_numeric_text(self.input_current_width.text())
# #         self.project_meta["source_height"] = self.parse_numeric_text(self.input_current_height.text())
# #         self.project_meta["target_width"] = self.parse_numeric_text(self.input_target_width.text())
# #         self.project_meta["target_height"] = self.parse_numeric_text(self.input_target_height.text())
# #         self.update_folder_dimensions_from_meta()
# #         self.is_loading_history = True
# #         self.suppress_project_config_save = True
# #         try:
# #             ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
# #         finally:
# #             self.suppress_project_config_save = False
# #             self.is_loading_history = False
# #         if not ok_to_export:
# #             if original_bytes is not None:
# #                 with open(self.dxf_path, "wb") as f:
# #                     f.write(original_bytes)
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #                 self.save_original_geometries()
# #             self.project_meta = original_meta
# #             self.parametric_groups = original_groups
# #             self.block_keep_state = original_keep_state
# #             self.update_dimension_inputs_from_meta()
# #             self.load_groups_into_list()
# #             self.load_entities_into_list()
# #             self.update_viewer()
# #             return

# #         target_w = self.project_meta.get("target_width")
# #         target_h = self.project_meta.get("target_height")
# #         export_path = self.build_export_path(target_w, target_h)

# #         export_doc = copy.deepcopy(self.doc)
# #         export_msp = export_doc.modelspace()
# #         delete_handles = set()
# #         for group in self.parametric_groups:
# #             key = self.get_group_key(group)
# #             if not self.block_keep_state.get(key, True):
# #                 delete_handles.update(group.get("handles", set()))
# #         for hndl in list(delete_handles):
# #             if hndl in export_doc.entitydb:
# #                 export_msp.delete_entity(export_doc.entitydb[hndl])

# #         self.apply_opening_to_export_doc(export_doc)
# #         export_doc.saveas(export_path)
# #         self.save_generated_project_config(export_path, target_w, target_h)
# #         self.save_export_to_db(export_path)
# #         if original_bytes is not None:
# #             with open(self.dxf_path, "wb") as f:
# #                 f.write(original_bytes)
# #             self.doc = ezdxf.readfile(self.dxf_path)
# #         self.project_meta = original_meta
# #         self.parametric_groups = original_groups
# #         self.block_keep_state = original_keep_state
# #         self.save_original_geometries()
# #         self.save_project_config()
# #         self.scan_project_folder_for_dxf()
# #         self.update_dimension_inputs_from_meta()
# #         self.load_groups_into_list()
# #         self.load_entities_into_list()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Створено: {os.path.basename(export_path)}</font>")

# #     def export_model_dxf_with_dimensions(self):
# #         """Export all source DXF files from the current folder/model with the same target size."""
# #         self.collect_text_settings_from_inputs()
# #         self.register_current_folder_model(show_errors=False)

# #         original_dxf_path = self.dxf_path
# #         original_project_file_id = getattr(self, "current_project_file_id", None)
# #         original_door_model_id = getattr(self, "current_door_model_id", None)
# #         original_meta = copy.deepcopy(self.project_meta)
# #         original_groups = copy.deepcopy(self.parametric_groups)
# #         original_keep_state = copy.deepcopy(self.block_keep_state)
# #         original_bytes = None
# #         if os.path.exists(original_dxf_path):
# #             with open(original_dxf_path, "rb") as f:
# #                 original_bytes = f.read()

# #         source_files = self.get_folder_source_dxf_files()
# #         if not source_files:
# #             source_files = [os.path.basename(self.dxf_path)]

# #         target_w = self.parse_numeric_text(self.input_target_width.text())
# #         target_h = self.parse_numeric_text(self.input_target_height.text())
# #         source_w = self.parse_numeric_text(self.input_current_width.text())
# #         source_h = self.parse_numeric_text(self.input_current_height.text())
# #         if target_w is None or target_h is None or source_w is None or source_h is None:
# #             self.lbl_status_calc.setText("<font color='red'>Вкажіть початкові та цільові W/H.</font>")
# #             return

# #         created = []
# #         skipped = 0
# #         try:
# #             for source_file in source_files:
# #                 source_path = os.path.join(self.project_dir, source_file)
# #                 if not os.path.exists(source_path):
# #                     continue
# #                 with open(source_path, "rb") as f:
# #                     source_bytes = f.read()

# #                 self.dxf_path = source_path
# #                 self.current_project_file_id = None
# #                 self.current_door_model_id = original_door_model_id
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #                 self.load_project_config()
# #                 self.save_original_geometries()

# #                 self.project_meta["source_width"] = source_w
# #                 self.project_meta["source_height"] = source_h
# #                 self.project_meta["target_width"] = target_w
# #                 self.project_meta["target_height"] = target_h

# #                 self.is_loading_history = True
# #                 self.suppress_project_config_save = True
# #                 try:
# #                     ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
# #                 finally:
# #                     self.suppress_project_config_save = False
# #                     self.is_loading_history = False

# #                 if not ok_to_export:
# #                     skipped += 1
# #                     with open(source_path, "wb") as f:
# #                         f.write(source_bytes)
# #                     self.doc = ezdxf.readfile(self.dxf_path)
# #                     self.save_original_geometries()
# #                     continue

# #                 export_path = self.build_export_path(target_w, target_h)
# #                 export_doc = copy.deepcopy(self.doc)
# #                 export_msp = export_doc.modelspace()
# #                 for hndl in self.get_export_delete_handles():
# #                     if hndl in export_doc.entitydb:
# #                         export_msp.delete_entity(export_doc.entitydb[hndl])

# #                 self.apply_opening_to_export_doc(export_doc)
# #                 export_doc.saveas(export_path)
# #                 self.save_generated_project_config(export_path, target_w, target_h)
# #                 self.save_export_to_db(export_path)
# #                 created.append(os.path.basename(export_path))

# #                 with open(source_path, "wb") as f:
# #                     f.write(source_bytes)
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #                 self.save_original_geometries()

# #             self.dxf_path = original_dxf_path
# #             self.current_project_file_id = original_project_file_id
# #             self.current_door_model_id = original_door_model_id
# #             if os.path.exists(self.dxf_path):
# #                 if original_bytes is not None:
# #                     with open(self.dxf_path, "wb") as f:
# #                         f.write(original_bytes)
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #             self.project_meta = original_meta
# #             self.parametric_groups = original_groups
# #             self.block_keep_state = original_keep_state
# #             self.save_original_geometries()
# #             self.save_project_config()
# #             self.scan_project_folder_for_dxf()
# #             self.update_dimension_inputs_from_meta()
# #             self.load_groups_into_list()
# #             self.load_entities_into_list()
# #             self.update_viewer()
# #             if skipped:
# #                 self.lbl_status_calc.setText(f"<font color='#ff9800'>Комплект створено: {len(created)} DXF, пропущено: {skipped}</font>")
# #             else:
# #                 self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Комплект створено: {len(created)} DXF</font>")
# #         except Exception as e:
# #             self.dxf_path = original_dxf_path
# #             self.current_project_file_id = original_project_file_id
# #             self.current_door_model_id = original_door_model_id
# #             if original_bytes is not None and os.path.exists(self.dxf_path):
# #                 with open(self.dxf_path, "wb") as f:
# #                     f.write(original_bytes)
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #                 self.save_original_geometries()
# #             self.project_meta = original_meta
# #             self.parametric_groups = original_groups
# #             self.block_keep_state = original_keep_state
# #             self.lbl_status_calc.setText(f"<font color='red'>Помилка експорту комплекту: {e}</font>")

# #     def batch_export_from_table(self):
# #         self.collect_text_settings_from_inputs()
# #         path, _ = QFileDialog.getOpenFileName(
# #             self,
# #             "Виберіть Excel/CSV для пакетного створення DXF",
# #             self.project_dir,
# #             "Tables (*.xlsx *.csv);;All Files (*)"
# #         )
# #         if not path:
# #             return

# #         original_dxf_path = self.dxf_path
# #         original_bytes = None
# #         if os.path.exists(self.dxf_path):
# #             with open(self.dxf_path, "rb") as f:
# #                 original_bytes = f.read()
# #         original_meta = copy.deepcopy(self.project_meta)
# #         original_groups = copy.deepcopy(self.parametric_groups)
# #         original_keep_state = copy.deepcopy(self.block_keep_state)

# #         try:
# #             rows = self.read_xlsx_rows(path) if path.lower().endswith(".xlsx") else self.read_csv_rows(path)
# #             jobs = self.extract_batch_jobs(rows)
# #             source_files = self.get_folder_source_dxf_files()
# #             if not source_files:
# #                 source_files = [os.path.basename(self.dxf_path)]
# #             created = []
# #             skipped = 0
# #             for job in jobs:
# #                 for source_file in source_files:
# #                     source_path = os.path.join(self.project_dir, source_file)
# #                     if not os.path.exists(source_path):
# #                         continue
# #                     with open(source_path, "rb") as f:
# #                         source_bytes = f.read()

# #                     self.dxf_path = source_path
# #                     self.current_project_file_id = None
# #                     self.doc = ezdxf.readfile(self.dxf_path)
# #                     self.load_project_config()
# #                     self.save_original_geometries()
# #                     self.apply_imported_parameters(job, refresh_ui=False, save_config=False)
# #                     self.is_loading_history = True
# #                     self.suppress_project_config_save = True
# #                     try:
# #                         ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
# #                     finally:
# #                         self.suppress_project_config_save = False
# #                         self.is_loading_history = False
# #                     if not ok_to_export:
# #                         skipped += 1
# #                         with open(source_path, "wb") as f:
# #                             f.write(source_bytes)
# #                         self.doc = ezdxf.readfile(self.dxf_path)
# #                         self.save_original_geometries()
# #                         continue

# #                     target_w = self.project_meta.get("target_width")
# #                     target_h = self.project_meta.get("target_height")
# #                     export_path = self.build_export_path(target_w, target_h)
# #                     export_doc = copy.deepcopy(self.doc)
# #                     export_msp = export_doc.modelspace()
# #                     delete_handles = self.get_export_delete_handles()
# #                     for hndl in delete_handles:
# #                         if hndl in export_doc.entitydb:
# #                             export_msp.delete_entity(export_doc.entitydb[hndl])
# #                     self.apply_opening_to_export_doc(export_doc)
# #                     export_doc.saveas(export_path)
# #                     self.save_generated_project_config(export_path, target_w, target_h)
# #                     self.save_export_to_db(export_path)
# #                     created.append(os.path.basename(export_path))

# #                     with open(source_path, "wb") as f:
# #                         f.write(source_bytes)
# #                     self.doc = ezdxf.readfile(self.dxf_path)
# #                     self.save_original_geometries()

# #             self.dxf_path = original_dxf_path
# #             if os.path.exists(self.dxf_path):
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #             self.project_meta = original_meta
# #             self.parametric_groups = original_groups
# #             self.block_keep_state = original_keep_state
# #             self.save_project_config()
# #             self.scan_project_folder_for_dxf()
# #             self.update_dimension_inputs_from_meta()
# #             self.load_groups_into_list()
# #             self.load_entities_into_list()
# #             self.update_viewer()
# #             if skipped:
# #                 self.lbl_status_calc.setText(
# #                     f"<font color='#ff9800'>Пакет створено: {len(created)} DXF, пропущено через накладання: {skipped}</font>"
# #                 )
# #             else:
# #                 self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Пакет створено: {len(created)} DXF</font>")
# #         except Exception as e:
# #             self.lbl_status_calc.setText(f"<font color='red'>Помилка пакета: {e}</font>")
# #             self.dxf_path = original_dxf_path
# #             if original_bytes is not None:
# #                 with open(self.dxf_path, "wb") as f:
# #                     f.write(original_bytes)
# #                 self.doc = ezdxf.readfile(self.dxf_path)
# #                 self.save_original_geometries()

# #     def extract_batch_jobs(self, rows):
# #         if not rows:
# #             return []
# #         headers = [self.normalize_key(c) for c in rows[0]]
# #         jobs = []
# #         for row in rows[1:]:
# #             params = {}
# #             for idx, key in enumerate(headers):
# #                 if idx >= len(row):
# #                     continue
# #                 value = row[idx]
# #                 if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
# #                     num = self.parse_numeric_text(value)
# #                     if num is not None:
# #                         params[key] = num
# #                 elif key in ("text", "font"):
# #                     text_value = str(value).strip()
# #                     if text_value:
# #                         params[key] = text_value
# #                 elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
# #                     opening = self.parse_door_opening_value(value)
# #                     if opening:
# #                         params[key] = opening
# #                 elif key in ("keep_blocks", "delete_blocks"):
# #                     names = self.split_block_names(value)
# #                     if names:
# #                         params.setdefault(key, []).extend(names)
# #             if params:
# #                 jobs.append(params)
# #         if not jobs:
# #             single = self.extract_table_parameters(rows)
# #             if single:
# #                 jobs.append(single)
# #         return jobs

# #     def normalize_key(self, value):
# #         return table_io.normalize_key(value)

# #     def read_csv_rows(self, path):
# #         return table_io.read_csv_rows(path)

# #     def read_xlsx_rows(self, path):
# #         return table_io.read_xlsx_rows(path)

# #     def extract_table_parameters(self, rows):
# #         return table_io.extract_table_parameters(rows, self.parse_numeric_text)

# #     def split_block_names(self, value):
# #         return table_io.split_block_names(value)

# #     def parse_door_opening_value(self, value):
# #         return table_io.parse_door_opening_value(value)

# #     def extract_batch_jobs(self, rows):
# #         return table_io.extract_batch_jobs(rows, self.parse_numeric_text)

# #     def get_export_delete_handles(self):
# #         delete_handles = set()
# #         for group in self.parametric_groups:
# #             key = self.get_group_key(group)
# #             if not self.block_keep_state.get(key, True):
# #                 delete_handles.update(group.get("handles", set()))
# #         return delete_handles

# #     def open_dxf_from_dialog(self):
# #         file_path, _ = QFileDialog.getOpenFileName(
# #             self,
# #             "Виберіть DXF файл",
# #             self.project_dir,
# #             "DXF Files (*.dxf);;All Files (*)"
# #         )
        
# #         if file_path:
# #             try:
# #                 old_project_dir = getattr(self, "project_dir", None)
# #                 new_project_dir = os.path.dirname(os.path.abspath(file_path))
# #                 if old_project_dir and os.path.abspath(old_project_dir) != os.path.abspath(new_project_dir):
# #                     self.current_project_file_id = None
# #                     self.current_door_model_id = None
# #                 else:
# #                     self.current_project_file_id = None
# #                 self.project_dir = new_project_dir
# #                 self.dxf_path = os.path.abspath(file_path)
                
# #                 self.doc = ezdxf.readfile(self.dxf_path)
                
# #                 self.selected_handles.clear()
# #                 self.parametric_groups.clear()
# #                 self.zones_undo_stack.clear()
# #                 self.zones_redo_stack.clear()
# #                 self.global_recalc_undo_stack.clear()
# #                 self.global_recalc_redo_stack.clear()
                
# #                 self.load_folder_config()
# #                 self.load_project_config()
# #                 self.prompt_source_dimensions_on_open()
# #                 self.register_current_folder_model(show_errors=False)
# #                 self.update_dimension_inputs_from_meta()
                
# #                 self.history = HistoryManager(self.dxf_path)
# #                 self.history.save_state()
# #                 self.save_zones_history_state()
# #                 self.save_original_geometries()
                
# #                 self.scan_project_folder_for_dxf()
# #                 self.update_viewer()
# #                 self.load_entities_into_list()
# #                 self.load_groups_into_list()
# #                 self.load_block_filter_list()
# #                 self.update_history_buttons_state()
                
# #             except Exception as e:
# #                 print(f"Помилка при відкритті файлу: {e}")

# #     def transform_selected_entities(self, mode):
# #         if not self.selected_handles: return
# #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# #         if not selected_entities: return
# #         self.record_action_snapshot()

# #         bboxes = [self.entity_bbox(e) for e in selected_entities]
# #         bboxes = [b for b in bboxes if b]
# #         if not bboxes:
# #             return
# #         min_x = min(b[0] for b in bboxes)
# #         min_y = min(b[1] for b in bboxes)
# #         max_x = max(b[2] for b in bboxes)
# #         max_y = max(b[3] for b in bboxes)
# #         cx = (min_x + max_x) * 0.5
# #         cy = (min_y + max_y) * 0.5

# #         for entity in selected_entities:
# #             if mode == "ROT90":
# #                 m1 = Matrix44.translate(-cx, -cy, 0)
# #                 m2 = Matrix44.z_rotate(math.radians(90))
# #                 m3 = Matrix44.translate(cx, cy, 0)
# #                 m = m1 @ m2 @ m3
# #             elif mode == "ROT180":
# #                 m1 = Matrix44.translate(-cx, -cy, 0)
# #                 m2 = Matrix44.z_rotate(math.radians(180))
# #                 m3 = Matrix44.translate(cx, cy, 0)
# #                 m = m1 @ m2 @ m3
# #             elif mode == "ROT270":
# #                 m1 = Matrix44.translate(-cx, -cy, 0)
# #                 m2 = Matrix44.z_rotate(math.radians(270))
# #                 m3 = Matrix44.translate(cx, cy, 0)
# #                 m = m1 @ m2 @ m3
# #             elif mode == "MIRROR_H":
# #                 self.mirror_entity_horizontally(entity, cx)
# #                 continue
# #             elif mode == "MIRROR_V":
# #                 self.mirror_entity_vertically(entity, cy)
# #                 continue
# #             else: 
# #                 continue
# #             entity.transform(m)

# #         self.transform_managed_text_settings(mode, cx, cy)

# #         for group in self.parametric_groups:
# #             if not group["handles"].isdisjoint(self.selected_handles):
           
# #                 old_kw = group.get("k_w", 0.0)
# #                 old_kh = group.get("k_h", 0.0)
# #                 old_gpw = group.get("growth_p_w", 0.0)
# #                 old_gph = group.get("growth_p_h", 0.0)
                
# #                 old_link_x = group.get("link_x", "X = W")
# #                 old_link_y = group.get("link_y", "Y = H")
                
# #                 old_dir_x = group.get("growth_dir_x", "Вправо")
# #                 old_dir_y = group.get("growth_dir_y", "Вгору")
# #                 old_shift_dir_x = group.get("shift_dir_x", "Вправо")
# #                 old_shift_dir_y = group.get("shift_dir_y", "Вгору")

# #                 if mode == "ROT90":
# #                     group["k_w"], group["k_h"] = old_kh, old_kw
# #                     group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
# #                     group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
# #                     group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
            
# #                     map_x_to_y = {"Вправо": "Вгору", "Вліво": "Вниз", "Центр": "Центр"}
# #                     map_y_to_x = {"Вгору": "Вліво", "Вниз": "Вправо", "Центр": "Центр"}
# #                     group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
# #                     group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")
# #                     group["shift_dir_x"] = map_y_to_x.get(old_shift_dir_y, "Вправо")
# #                     group["shift_dir_y"] = map_x_to_y.get(old_shift_dir_x, "Вгору")

# #                 elif mode == "ROT270":
# #                     group["k_w"], group["k_h"] = old_kh, old_kw
# #                     group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
# #                     group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
# #                     group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
           
# #                     map_x_to_y = {"Вправо": "Вниз", "Вліво": "Вгору", "Центр": "Центр"}
# #                     map_y_to_x = {"Вгору": "Вправо", "Вниз": "Вліво", "Центр": "Центр"}
# #                     group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
# #                     group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")
# #                     group["shift_dir_x"] = map_y_to_x.get(old_shift_dir_y, "Вправо")
# #                     group["shift_dir_y"] = map_x_to_y.get(old_shift_dir_x, "Вгору")

# #                 elif mode == "ROT180":
# #                     map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
# #                     map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
# #                     group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
# #                     group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
# #                     group["shift_dir_x"] = map_x.get(old_shift_dir_x, "Вправо")
# #                     group["shift_dir_y"] = map_y.get(old_shift_dir_y, "Вгору")

# #                 elif mode == "MIRROR_H": 
# #                     map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
# #                     group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
# #                     group["shift_dir_x"] = map_x.get(old_shift_dir_x, "Вправо")

# #                 elif mode == "MIRROR_V": 
# #                     map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
# #                     group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
# #                     group["shift_dir_y"] = map_y.get(old_shift_dir_y, "Вгору")
                    
# #         self.update_growth_axis_after_transform(mode)
# #         self.swap_axis_link_mode_for_quarter_turn(mode)
# #         self.doc.saveas(self.dxf_path)

# #         self.commit_current_geometry_as_parametric_base(
# #             reason=f"TRANSFORM {mode}",
# #             update_source_dimensions=False,
# #             preserve_target_dimensions=True,
# #         )

# #         self.save_project_config()
# #         self.push_to_history()
        
# #         self.on_group_selection_changed() 
# #         self.sync_text_inputs_from_meta()
# #         self.update_viewer()
# #         self.load_entities_into_list()

# #     def snap_to_zero(self):
# #         min_x, min_y, max_x, max_y = self.get_dxf_bounds()
# #         if min_x is None or min_y is None:
# #             return
# #         self.record_action_snapshot()
# #         shift_x = -min_x
# #         shift_y = -min_y

# #         matrix = Matrix44.translate(shift_x, shift_y, 0)
# #         for entity in self.doc.modelspace():
# #             try:
# #                 entity.transform(matrix)
# #             except Exception:
# #                 tp = entity.dxftype()
# #                 if tp == "TEXT":
# #                     x, y, z = entity.dxf.insert
# #                     entity.dxf.insert = (x + shift_x, y + shift_y, z)

# #         settings = self.get_text_settings()
# #         settings["x"] = float(settings.get("x", 0.0)) + shift_x
# #         settings["y"] = float(settings.get("y", 0.0)) + shift_y
# #         self.project_meta["door_text"] = settings

# #         self.doc.saveas(self.dxf_path)
# #         self.save_original_geometries()
# #         self.save_project_config()
# #         self.push_to_history()
# #         self.sync_text_inputs_from_meta()
# #         self.load_entities_into_list()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Фігуру притиснуто до (0,0).</font>")

# #     def delete_entities_from_dxf(self):
# #         if not self.selected_handles:
# #             return
# #         self.record_action_snapshot()

# #         msp = self.doc.modelspace()
# #         handles_to_delete = list(self.selected_handles)

# #         for hndl in handles_to_delete:
# #             if hndl in self.doc.entitydb:
# #                 entity = self.doc.entitydb[hndl]
# #                 msp.delete_entity(entity)
            
# #             if hndl in self.original_geometries:
# #                 del self.original_geometries[hndl]

# #             for group in self.parametric_groups:
# #                 if hndl in group["handles"]:
# #                     group["handles"].remove(hndl)

# #         self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]
# #         self.selected_handles.clear()
        
# #         self.doc.saveas(self.dxf_path)
# #         self.save_project_config()
# #         self.push_to_history()
        
# #         self.load_entities_into_list()
# #         self.load_groups_into_list()
# #         self.update_viewer()

# #     def toggle_inspector_mode(self, checked):
# #         if not checked:
# #             if self.coord_tooltip_item and self.coord_tooltip_item in self.scene.items():
# #                 self.scene.removeItem(self.coord_tooltip_item)
# #             if self.coord_snap_marker and self.coord_snap_marker in self.scene.items():
# #                 self.scene.removeItem(self.coord_snap_marker)
# #             self.coord_tooltip_item = None
# #             self.coord_snap_marker = None
# #         self.update_viewer()

# #     def on_scene_mouse_move(self, event):
# #         QGraphicsScene.mouseMoveEvent(self.scene, event)
# #         if not self.chk_enable_inspector.isChecked():
# #             return

# #         pos = event.scenePos()
# #         cursor_x, cursor_y = pos.x(), -pos.y()

# #         closest_pt = None
# #         min_dist = float('inf')

# #         for entity in self.doc.modelspace():
# #             if entity.dxftype() == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
                
# #                 d1 = math.hypot(cursor_x - x1, cursor_y - y1)
# #                 d2 = math.hypot(cursor_x - x2, cursor_y - y2)

# #                 if d1 < min_dist:
# #                     min_dist = d1
# #                     closest_pt = (x1, y1, "START")
# #                 if d2 < min_dist:
# #                     min_dist = d2
# #                     closest_pt = (x2, y2, "END")

# #         if closest_pt and min_dist < 40.0:
# #             snap_x, snap_y, pt_type = closest_pt
# #             if not self.coord_snap_marker:
# #                 self.coord_snap_marker = self.scene.addEllipse(-4, -4, 8, 8, QPen(QColor("#ff9800"), 1.5), QBrush(QColor(255, 152, 0, 150)))
# #                 self.coord_tooltip_item = self.scene.addText("")
# #                 self.coord_tooltip_item.setDefaultTextColor(QColor("#ff9800"))
            
# #             self.coord_snap_marker.setPos(snap_x, -snap_y)
# #             self.coord_tooltip_item.setPos(snap_x + 10, -snap_y - 25)
# #             self.coord_tooltip_item.setPlainText(f"Вузол {pt_type}\nX: {snap_x:.1f}\nY: {snap_y:.1f}")
# #         else:
# #             if self.coord_tooltip_item:
# #                 self.coord_tooltip_item.setPlainText("")
# #             if self.coord_snap_marker:
# #                 self.coord_snap_marker.setPos(-99999, -99999)
        
# #         self.view.viewport().update()

# #     def guess_growth_axis_for_bbox(self, bbox):
# #         bounds = self.get_non_text_dxf_bounds()
# #         if bounds[0] is None or not bbox:
# #             return "both"
# #         ratio_x = self.auto_layout_dimension_ratio(bbox, bounds, "x")
# #         ratio_y = self.auto_layout_dimension_ratio(bbox, bounds, "y")
# #         grows_x = ratio_x >= 0.55
# #         grows_y = ratio_y >= 0.55
# #         if grows_x and grows_y:
# #             return "both"
# #         if grows_x:
# #             return "width"
# #         if grows_y:
# #             return "height"
# #         return "fixed"

# #     def make_parametric_group_data(self, name, handles, growth_axis="both", auto_grouped=False):
# #         group = {
# #             "name": name,
# #             "handles": set(handles),
# #             "k_w": 0.0,
# #             "k_h": 0.0,
# #             "growth_p_w": 0.0,
# #             "growth_p_h": 0.0,
# #             "growth_dir_x": "Центр",
# #             "growth_dir_y": "Центр",
# #             "shift_dir_x": "Вправо",
# #             "shift_dir_y": "Вгору",
# #             "link_x": "X = W",
# #             "link_y": "Y = H",
# #             "growth_axis": growth_axis,
# #             "resizes": False,
# #             "role_y": "manual",
# #             "auto_rule": False,
# #             "auto_grouped": auto_grouped,
# #             "touch_y_enabled": False,
# #             "touch_to_uid": None,
# #             "touch_gap_y": 0.0
# #         }
# #         self.get_group_key(group)
# #         self.apply_growth_axis_to_group(group)
# #         return group

# #     def union_bboxes(self, bboxes):
# #         valid = [bbox for bbox in bboxes if bbox]
# #         if not valid:
# #             return None
# #         return (
# #             min(b[0] for b in valid),
# #             min(b[1] for b in valid),
# #             max(b[2] for b in valid),
# #             max(b[3] for b in valid),
# #         )

# #     def bboxes_near(self, a, b, tolerance):
# #         return not (
# #             a[2] < b[0] - tolerance or
# #             b[2] < a[0] - tolerance or
# #             a[3] < b[1] - tolerance or
# #             b[3] < a[1] - tolerance
# #         )

# #     def collect_autogroup_entries(self):
# #         entries = []
# #         for entity in self.doc.modelspace():
# #             bbox = self.entity_bbox(entity)
# #             if not bbox:
# #                 continue
# #             handle = entity.dxf.handle
# #             layer = str(getattr(entity.dxf, "layer", "") or "0")
# #             entries.append({
# #                 "handle": handle,
# #                 "bbox": bbox,
# #                 "layer": layer,
# #                 "type": entity.dxftype(),
# #             })
# #         return entries

# #     def build_layer_autogroups(self, entries):
# #         layer_map = {}
# #         for entry in entries:
# #             layer_map.setdefault(entry["layer"], []).append(entry)
# #         useful_layers = {
# #             layer: items for layer, items in layer_map.items()
# #             if len(items) > 1 and layer.strip() and layer.strip() != "0"
# #         }
# #         if len(useful_layers) < 2:
# #             return []
# #         groups = []
# #         for layer, items in sorted(useful_layers.items()):
# #             handles = [item["handle"] for item in items]
# #             bbox = self.union_bboxes([item["bbox"] for item in items])
# #             groups.append((f"Шар {layer}", handles, bbox))
# #         return groups

# #     def build_proximity_autogroups(self, entries, tolerance=3.0):
# #         n = len(entries)
# #         visited = set()
# #         groups = []
# #         for start in range(n):
# #             if start in visited:
# #                 continue
# #             stack = [start]
# #             visited.add(start)
# #             component = []
# #             while stack:
# #                 idx = stack.pop()
# #                 component.append(entries[idx])
# #                 bbox = entries[idx]["bbox"]
# #                 for other in range(n):
# #                     if other in visited:
# #                         continue
# #                     if self.bboxes_near(bbox, entries[other]["bbox"], tolerance):
# #                         visited.add(other)
# #                         stack.append(other)
# #             groups.append(component)
# #         result = []
# #         for i, component in enumerate(groups, start=1):
# #             handles = [item["handle"] for item in component]
# #             bbox = self.union_bboxes([item["bbox"] for item in component])
# #             result.append((f"Деталь {i}", handles, bbox))
# #         return result

# #     def auto_group_entities(self):
# #         entries = self.collect_autogroup_entries()
# #         if not entries:
# #             self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автогрупування.</font>")
# #             return
# #         if self.parametric_groups:
# #             answer = QMessageBox.question(
# #                 self,
# #                 "Автогрупувати",
# #                 "Поточні параметричні групи буде замінено. Продовжити?",
# #                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
# #                 QMessageBox.StandardButton.No,
# #             )
# #             if answer != QMessageBox.StandardButton.Yes:
# #                 return

# #         auto_groups = self.build_layer_autogroups(entries)
# #         method = "layers"
# #         if not auto_groups:
# #             auto_groups = self.build_proximity_autogroups(entries)
# #             method = "proximity"

# #         auto_groups = [
# #             (name, handles, bbox)
# #             for name, handles, bbox in auto_groups
# #             if handles and bbox
# #         ]
# #         if not auto_groups:
# #             self.lbl_status_calc.setText("<font color='red'>Не вдалося сформувати групи автоматично.</font>")
# #             return

# #         self.record_action_snapshot()
# #         self.parametric_groups = []
# #         self.block_keep_state = {}
# #         file_axis = self.project_meta.get("growth_axis", "both")
# #         for name, handles, bbox in auto_groups:
# #             group = self.make_parametric_group_data(name, handles, file_axis, auto_grouped=True)
# #             self.parametric_groups.append(group)
# #             self.block_keep_state[group["uid"]] = True

# #         self.clear_selection()
# #         self.push_to_history()
# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText(
# #             f"<font color='#a5d6a7'>Автогрупування: створено {len(self.parametric_groups)} груп ({method}).</font>"
# #         )

# #     def create_parametric_group(self):
# #         if len(self.selected_handles) < 1:
# #             return  

# #         name, ok = QInputDialog.getText(
# #             self,
# #             "Нова група",
# #             "Введіть назву групи:"
# #         )
# #         if not ok or not name.strip():
# #             name = f"Група {len(self.parametric_groups) + 1}"
# #         self.record_action_snapshot()

# #         for group in self.parametric_groups:
# #             group["handles"].difference_update(self.selected_handles)
# #         self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]

# #         new_group = {
# #             "name": name.strip(),
# #             "handles": set(self.selected_handles),
# #             "k_w": 0.0, 
# #             "k_h": 0.0,
# #             "growth_p_w": 0.0, 
# #             "growth_p_h": 0.0,
# #             "growth_dir_x": "Центр",
# #             "growth_dir_y": "Центр",
# #             "shift_dir_x": "Вправо",
# #             "shift_dir_y": "Вгору",
# #             "link_x": "X = W",
# #             "link_y": "Y = H",
# #             "growth_axis": "both",
# #             "resizes": False,
# #             "role_y": "manual",
# #             "auto_rule": False,
# #             "touch_y_enabled": False,
# #             "touch_to_uid": None,
# #             "touch_gap_y": 0.0
# #         }
# #         self.get_group_key(new_group)
# #         self.parametric_groups.append(new_group)
# #         self.block_keep_state[new_group["uid"]] = True
# #         self.clear_selection()
# #         self.push_to_history()
# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.update_viewer()

# #     def disband_parametric_group(self):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         del self.parametric_groups[idx]
# #         self.clear_selection()
# #         self.push_to_history()
# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.update_viewer()

# #     def remove_selected_from_group(self):
# #         selected_group_item = self.group_list_widget.currentItem()
# #         if not selected_group_item or not self.selected_handles: return
# #         self.record_action_snapshot()
        
# #         idx = selected_group_item.data(Qt.ItemDataRole.UserRole)
# #         group = self.parametric_groups[idx]
        
# #         group["handles"] -= self.selected_handles
# #         if not group["handles"]:
# #             del self.parametric_groups[idx]
            
# #         self.clear_selection()
# #         self.push_to_history()
# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.update_viewer()

# #     def load_groups_into_list(self):
# #         self.group_list_widget.blockSignals(True)
# #         self.group_list_widget.clear()
# #         for idx, group in enumerate(self.parametric_groups):
# #             name = group.get("name", f"Гр №{idx+1}")
# #             role = group.get("role_y", "manual")
# #             auto_mark = "⚙️" if group.get("auto_rule") else "✍️"
# #             touch_mark = "🔗" if group.get("touch_y_enabled") else ""
# #             axis_mark = {
# #                 "both": "WH",
# #                 "width": "W",
# #                 "height": "H",
# #                 "fixed": "fix",
# #             }.get(self.project_meta.get("growth_axis", "both"), "WH")
# #             text = f"🧩 {auto_mark}{touch_mark} {name} ({len(group['handles'])} об.) {axis_mark} Y:{role}"
# #             key = self.get_group_key(group)
# #             keep_mark = "keep" if self.block_keep_state.get(key, True) else "del"
# #             size_mark = "size" if self.group_resizes(group) else "move"
# #             link_x, link_y = self.link_pair_for_mode()
# #             text = f"{auto_mark}{touch_mark} {name} [{axis_mark} {size_mark} {keep_mark} {link_x}/{link_y}] ({len(group['handles'])} об.) Y:{role}"
# #             item = QListWidgetItem(text)
# #             item.setToolTip(text)
# #             item.setData(Qt.ItemDataRole.UserRole, idx)
# #             self.group_list_widget.addItem(item)
# #         self.group_list_widget.blockSignals(False)
# #         self.load_block_filter_list()

# #     def on_group_selection_changed(self):
# #         selected = self.group_list_widget.selectedItems()
# #         widgets_to_toggle = [
# #             self.combo_k_w, self.combo_k_h, self.combo_growth_p_w, 
# #             self.combo_growth_p_h, self.combo_growth_dir_x, self.combo_growth_dir_y,
# #             self.combo_shift_dir_x, self.combo_shift_dir_y,
# #             self.chk_group_resizes
# #         ]
        
# #         if not selected:
# #             for widget in widgets_to_toggle: widget.setEnabled(False)
# #             self.chk_group_resizes.blockSignals(True)
# #             self.chk_group_resizes.setChecked(False)
# #             self.chk_group_resizes.blockSignals(False)
# #             self.apply_group_controls_visibility(None)
# #             return
        
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         group = self.parametric_groups[idx]

# #         for widget in widgets_to_toggle:
# #             widget.blockSignals(True)
# #             widget.setEnabled(True)
        
# #         self.combo_k_w.setCurrentText(format_factor(group.get("k_w", 0.0)))
# #         self.combo_k_h.setCurrentText(format_factor(group.get("k_h", 0.0)))
# #         self.combo_growth_p_w.setCurrentText(format_factor(group.get("growth_p_w", 0.0)))
# #         self.combo_growth_p_h.setCurrentText(format_factor(group.get("growth_p_h", 0.0)))
# #         self.chk_group_resizes.setChecked(self.group_resizes(group))
        
# #         self.combo_growth_dir_x.setCurrentText(group.get("growth_dir_x", "Вправо"))
# #         self.combo_growth_dir_y.setCurrentText(group.get("growth_dir_y", "Вгору"))
# #         self.combo_shift_dir_x.setCurrentText(group.get("shift_dir_x", "Вправо"))
# #         self.combo_shift_dir_y.setCurrentText(group.get("shift_dir_y", "Вгору"))
        
# #         self.apply_axis_link_mode_to_groups()
# #         self.sync_link_combos_from_file_mode()

# #         for widget in widgets_to_toggle:
# #             widget.blockSignals(False)

# #         self.apply_group_controls_visibility(group)
# #         self.selected_handles = set(group["handles"])
# #         self.sync_list_from_handles()
# #         self.update_viewer()

# #     def growth_axis_to_label(self, axis):
# #         return {
# #             "both": "Ширина + висота",
# #             "width": "Тільки ширина",
# #             "height": "Тільки висота",
# #             "fixed": "Не росте",
# #         }.get(axis, "Ширина + висота")

# #     def growth_axis_from_label(self, label):
# #         text = str(label)
# #         if "Тільки ширина" in text:
# #             return "width"
# #         if "Тільки висота" in text:
# #             return "height"
# #         if "Не росте" in text:
# #             return "fixed"
# #         return "both"

# #     def swap_growth_axis_for_quarter_turn(self, axis):
# #         if axis == "width":
# #             return "height"
# #         if axis == "height":
# #             return "width"
# #         return axis

# #     def update_growth_axis_after_transform(self, mode):
# #         if mode not in ("ROT90", "ROT270"):
# #             return
# #         self.project_meta["growth_axis"] = self.swap_growth_axis_for_quarter_turn(
# #             self.project_meta.get("growth_axis", "both")
# #         )
# #         for group in self.parametric_groups:
# #             if "growth_axis" in group:
# #                 group["growth_axis"] = self.swap_growth_axis_for_quarter_turn(
# #                     group.get("growth_axis", "both")
# #                 )
# #         self.sync_file_growth_axis_combo()

# #     def link_pair_for_mode(self, mode=None):
# #         mode = mode or self.project_meta.get("axis_link_mode", "normal")
# #         if mode == "rotated":
# #             return "X = H", "Y = W"
# #         return "X = W", "Y = H"

# #     def axis_link_mode_from_pair(self, link_x=None, link_y=None):
# #         link_x = link_x or ""
# #         link_y = link_y or ""
# #         if "H" in link_x or "W" in link_y:
# #             return "rotated"
# #         return "normal"

# #     def apply_axis_link_mode_to_groups(self):
# #         link_x, link_y = self.link_pair_for_mode()
# #         for group in self.parametric_groups:
# #             group["link_x"] = link_x
# #             group["link_y"] = link_y

# #     def sync_link_combos_from_file_mode(self):
# #         if not hasattr(self, "combo_link_x") or not hasattr(self, "combo_link_y"):
# #             return
# #         link_x, link_y = self.link_pair_for_mode()
# #         self.combo_link_x.blockSignals(True)
# #         self.combo_link_y.blockSignals(True)
# #         self.combo_link_x.setCurrentText(link_x)
# #         self.combo_link_y.setCurrentText(link_y)
# #         self.combo_link_x.blockSignals(False)
# #         self.combo_link_y.blockSignals(False)
# #         self.update_file_status_panel()

# #     def swap_axis_link_mode_for_quarter_turn(self, mode):
# #         if mode not in ("ROT90", "ROT270"):
# #             return
# #         current = self.project_meta.get("axis_link_mode", "normal")
# #         self.project_meta["axis_link_mode"] = "rotated" if current == "normal" else "normal"
# #         self.apply_axis_link_mode_to_groups()
# #         self.sync_link_combos_from_file_mode()

# #     def set_param_grid_row_visible(self, row, visible):
# #         grid = getattr(self, "param_transform_grid", None)
# #         if not grid:
# #             return
# #         for col in range(grid.columnCount()):
# #             item = grid.itemAtPosition(row, col)
# #             if item and item.widget():
# #                 item.widget().setVisible(visible)

# #     def apply_growth_axis_ui(self, axis):
# #         self.set_param_grid_row_visible(0, axis in ("both", "width"))
# #         self.set_param_grid_row_visible(1, axis in ("both", "height"))

# #     def set_param_grid_cells_visible(self, row, columns, visible):
# #         grid = getattr(self, "param_transform_grid", None)
# #         if not grid:
# #             return
# #         for col in columns:
# #             item = grid.itemAtPosition(row, col)
# #             if item and item.widget():
# #                 item.widget().setVisible(visible)

# #     def group_resizes(self, group):
# #         if not group:
# #             return False
# #         if "resizes" in group:
# #             return bool(group.get("resizes"))
# #         return (
# #             abs(float(group.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
# #             abs(float(group.get("growth_p_h", 0.0) or 0.0)) > 0.000001
# #         )

# #     def apply_group_controls_visibility(self, group):
# #         axis = self.project_meta.get("growth_axis", "both")
# #         self.apply_growth_axis_ui(axis)
# #         show_growth = self.group_resizes(group)
# #         show_x = axis in ("both", "width")
# #         show_y = axis in ("both", "height")
# #         self.set_param_grid_cells_visible(0, (4, 5, 6), show_growth and show_x)
# #         self.set_param_grid_cells_visible(1, (4, 5, 6), show_growth and show_y)

# #     def apply_growth_axis_to_group(self, group):
# #         axis = self.project_meta.get("growth_axis", "both")
# #         if not self.group_resizes(group):
# #             group["growth_p_w"] = 0.0
# #             group["growth_p_h"] = 0.0
# #             group["growth_dir_x"] = "Центр"
# #             group["growth_dir_y"] = "Центр"
# #             return
# #         if axis in ("height", "fixed"):
# #             group["growth_p_w"] = 0.0
# #             group["growth_dir_x"] = "Центр"
# #         if axis in ("width", "fixed"):
# #             group["growth_p_h"] = 0.0
# #             group["growth_dir_y"] = "Центр"

# #     def sync_file_growth_axis_combo(self):
# #         if not hasattr(self, "combo_group_growth_axis"):
# #             return
# #         self.combo_group_growth_axis.blockSignals(True)
# #         self.combo_group_growth_axis.setCurrentText(
# #             self.growth_axis_to_label(self.project_meta.get("growth_axis", "both"))
# #         )
# #         self.combo_group_growth_axis.blockSignals(False)
# #         current = self.group_list_widget.currentItem() if hasattr(self, "group_list_widget") else None
# #         group = self.parametric_groups[current.data(Qt.ItemDataRole.UserRole)] if current else None
# #         self.apply_group_controls_visibility(group)
# #         self.update_file_status_panel()

# #     def on_group_growth_axis_changed(self, text):
# #         self.record_action_snapshot()
# #         self.project_meta["growth_axis"] = self.growth_axis_from_label(text)
# #         for group in self.parametric_groups:
# #             self.apply_growth_axis_to_group(group)
# #         current = self.group_list_widget.currentItem()
# #         group = self.parametric_groups[current.data(Qt.ItemDataRole.UserRole)] if current else None
# #         self.apply_group_controls_visibility(group)
# #         self.save_project_config()
# #         self.on_group_selection_changed()

# #     def on_group_resizes_changed(self, state):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected:
# #             return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         group = self.parametric_groups[idx]
# #         group["resizes"] = state == Qt.CheckState.Checked.value
# #         self.apply_growth_axis_to_group(group)
# #         self.apply_group_controls_visibility(group)
# #         self.save_project_config()
# #         self.on_group_selection_changed()

# #     def on_combo_k_w_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["k_w"] = parse_factor(text)
# #         self.save_project_config()

# #     def on_combo_k_h_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["k_h"] = parse_factor(text)
# #         self.save_project_config()

# #     def on_combo_growth_p_w_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["growth_p_w"] = parse_factor(text)
# #         self.save_project_config()

# #     def on_combo_growth_p_h_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["growth_p_h"] = parse_factor(text)
# #         self.save_project_config()

# #     def on_link_x_changed(self, text):
# #         self.record_action_snapshot()
# #         self.project_meta["axis_link_mode"] = self.axis_link_mode_from_pair(link_x=text)
# #         self.apply_axis_link_mode_to_groups()
# #         self.sync_link_combos_from_file_mode()
# #         self.save_project_config()

# #     def on_link_y_changed(self, text):
# #         self.record_action_snapshot()
# #         self.project_meta["axis_link_mode"] = self.axis_link_mode_from_pair(link_y=text)
# #         self.apply_axis_link_mode_to_groups()
# #         self.sync_link_combos_from_file_mode()
# #         self.save_project_config()

# #     def on_growth_dir_x_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["growth_dir_x"] = text
# #         self.save_project_config()

# #     def on_growth_dir_y_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["growth_dir_y"] = text
# #         self.save_project_config()

# #     def on_shift_dir_x_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["shift_dir_x"] = text
# #         self.save_project_config()

# #     def on_shift_dir_y_changed(self, text):
# #         selected = self.group_list_widget.selectedItems()
# #         if not selected: return
# #         self.record_action_snapshot()
# #         idx = selected[0].data(Qt.ItemDataRole.UserRole)
# #         self.parametric_groups[idx]["shift_dir_y"] = text
# #         self.save_project_config()



# #     def group_center_y(self, group):
# #         bbox = self.group_original_bbox(group)
# #         if not bbox:
# #             return 0.0
# #         return (bbox[1] + bbox[3]) * 0.5

# #     def group_center_x(self, group):
# #         bbox = self.group_original_bbox(group)
# #         if not bbox:
# #             return 0.0
# #         return (bbox[0] + bbox[2]) * 0.5

# #     def ensure_topology_fields(self, group):
# #         self.get_group_key(group)
# #         group.setdefault("role_y", "manual")
# #         group.setdefault("auto_rule", False)
# #         group.setdefault("touch_y_enabled", False)
# #         group.setdefault("touch_to_uid", None)
# #         group.setdefault("touch_gap_y", 0.0)
# #         group.setdefault("growth_axis", "both")
# #         group.setdefault("resizes", (
# #             abs(float(group.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
# #             abs(float(group.get("growth_p_h", 0.0) or 0.0)) > 0.000001
# #         ))
# #         group.setdefault("auto_chain_x", False)
# #         group.setdefault("chain_shift_x", 0.0)
# #         group.setdefault("chain_growth_own_x", 0.0)
# #         group.setdefault("chain_growth_after_x", 0.0)

# #     def groups_overlap_by_x(self, bbox_a, bbox_b, tolerance=2.0):
# #         if not bbox_a or not bbox_b:
# #             return False
# #         return not (bbox_a[2] < bbox_b[0] - tolerance or bbox_b[2] < bbox_a[0] - tolerance)

# #     def auto_apply_vertical_topology_rules(self):
# #         """
# #         AUTO RULES Y / Авто правила Y.

# #         Що робить:
# #         1) бере всі параметричні групи, у яких є bbox;
# #         2) рахує центр групи по Y;
# #         3) знаходить найнижчий і найвищий центр;
# #         4) перетворює позицію групи у коефіцієнт k_h:
# #            - низ  => k_h = 0.0
# #            - верх => k_h = 1.0
# #            - середина => пропорційно, часто 0.5
# #         5) записує це в JSON як auto_rule=True, role_y=bottom/middle/top.

# #         ВАЖЛИВО:
# #         ця кнопка НЕ рахує суму ростів. Для суми ростів є кнопка "Авто сума росту Y".
# #         """
# #         valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
# #         if not valid_groups:
# #             self.lbl_status_calc.setText("<font color='red'>Немає груп з геометрією для автоаналізу Y.</font>")
# #             self.topology_debug_print("AUTO RULES Y: немає груп з bbox")
# #             return

# #         self.record_action_snapshot()

# #         rows = []
# #         rows.append("AUTO RULES Y / Авто правила Y")
# #         rows.append("Сенс: програма сама визначає низ/середину/верх і ставить k_h.")
# #         rows.append("Формула: k_h = (centerY - minCenterY) / (maxCenterY - minCenterY)")
# #         rows.append("Потім: близько до низу => 0; близько до верху => 1; близько до центру => 0.5")
# #         rows.append("")

# #         centers = [self.group_center_y(g) for g in valid_groups]
# #         min_c, max_c = min(centers), max(centers)
# #         span = max(max_c - min_c, 0.0001)
# #         rows.append(f"minCenterY={min_c:.3f}; maxCenterY={max_c:.3f}; span={span:.3f}")
# #         rows.append("")

# #         sorted_groups = sorted(valid_groups, key=self.group_center_y)
# #         rows.append("Групи знизу вгору:")
# #         for i, group in enumerate(sorted_groups, start=1):
# #             bbox = self.group_original_bbox(group)
# #             uid = self.get_group_key(group)
# #             cy = self.group_center_y(group)
# #             rows.append(
# #                 f"  #{i}: name={group.get('name')} uid={uid} "
# #                 f"bbox=(minY={bbox[1]:.3f}, maxY={bbox[3]:.3f}) centerY={cy:.3f}"
# #             )
# #         rows.append("")
# #         rows.append("Рішення по кожній групі:")

# #         for group in sorted_groups:
# #             self.ensure_topology_fields(group)
# #             uid = self.get_group_key(group)
# #             bbox = self.group_original_bbox(group)
# #             cy = self.group_center_y(group)
# #             raw_k = (cy - min_c) / span
# #             k = raw_k
# #             reason = "пропорційне положення між низом і верхом"

# #             if k < 0.15:
# #                 role = "bottom"
# #                 k = 0.0
# #                 reason = "центр близько до нижнього краю => фіксуємо як НИЗ"
# #             elif k > 0.85:
# #                 role = "top"
# #                 k = 1.0
# #                 reason = "центр близько до верхнього краю => фіксуємо як ВЕРХ"
# #             else:
# #                 role = "middle"
# #                 if abs(k - 0.5) < 0.18:
# #                     k = 0.5
# #                     reason = "центр близько до середини => ставимо 50%"

# #             old_k_h = float(group.get("k_h", 0.0) or 0.0)
# #             old_growth = float(group.get("growth_p_h", 0.0) or 0.0)
# #             old_dir = group.get("growth_dir_y", "Центр")

# #             group.update({
# #                 "k_h": round(float(k), 4),
# #                 "growth_p_h": 0.0,
# #                 "growth_dir_y": "Центр",
# #                 "link_y": "Y = H",
# #                 "role_y": role,
# #                 "auto_rule": True,
# #             })

# #             rows.append(
# #                 f"  group={group.get('name')} uid={uid}: "
# #                 f"centerY={cy:.3f}; raw_k={raw_k:.6f}; "
# #                 f"old_k_h={old_k_h:.6f} -> new_k_h={k:.6f} ({k*100:.2f}%); "
# #                 f"old_growth_p_h={old_growth:.6f} -> new_growth_p_h=0; "
# #                 f"old_dir={old_dir} -> new_dir=Центр; role_y={role}; reason={reason}"
# #             )

# #         rows.append("")
# #         rows.append("РЕЗУЛЬТАТ: Авто правила Y тільки розставляють позиційний зсув k_h: низ=0%, середина≈50%, верх=100%.")
# #         rows.append("Якщо треба логіка 50% + 5% = 55%, натискай 'Авто сума росту Y'.")
# #         self.topology_debug_print("AUTO RULES Y / Авто правила Y", rows)

# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.on_group_selection_changed()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Авто правила Y застосовано. Деталі дивись у консолі: [TOPOLOGY DEBUG] AUTO RULES Y.</font>")

# #     def topology_debug_print(self, title, rows=None):
# #         """Єдиний формат логів у консоль для топологічних розрахунків."""
# #         print("\n" + "=" * 90)
# #         print(f"[TOPOLOGY DEBUG] {title}")
# #         print("=" * 90)
# #         if rows:
# #             for row in rows:
# #                 print(row)
# #         print("=" * 90 + "\n")

# #     def auto_layout_dimension_ratio(self, bbox, bounds, axis):
# #         min_x, min_y, max_x, max_y = bounds
# #         if axis == "x":
# #             total = max(max_x - min_x, 0.0001)
# #             return max((bbox[2] - bbox[0]) / total, 0.0)
# #         total = max(max_y - min_y, 0.0001)
# #         return max((bbox[3] - bbox[1]) / total, 0.0)
    

# #     def format_factor(val):
# #         """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
# #         if abs(val - 0.0) < 0.001: return "0% (Фіксовано)"
# #         if abs(val - 0.25) < 0.001: return "25% (1/4)"
# #         if abs(val - 0.333) < 0.01: return "33.3% (Δ/3)"
# #         if abs(val - 0.5) < 0.001: return "50% (Δ/2)"
# #         if abs(val - 0.667) < 0.01: return "66.7% (Δ/3)"
# #         if abs(val - 0.75) < 0.01: return  "75% (1/4)"
# #         if abs(val - 1.0) < 0.001: return "100% (Δ)"
# #         return f"{val*100:g}%"
    


# #     def seed_auto_layout_growth(self):
# #         bounds = self.get_non_text_dxf_bounds()
# #         min_x, min_y, max_x, max_y = bounds
# #         if min_x is None:
# #             return []

# #         width = max(max_x - min_x, 0.0001)
# #         height = max(max_y - min_y, 0.0001)
# #         edge_tol_x = max(width * 0.025, 2.0)
# #         edge_tol_y = max(height * 0.025, 2.0)
# #         rows = [
# #             "AUTO LAYOUT SEED / start growth detection",
# #             f"bounds: minX={min_x:.3f}, maxX={max_x:.3f}, minY={min_y:.3f}, maxY={max_y:.3f}",
# #         ]

# #         for group in self.parametric_groups:
# #             bbox = self.group_original_bbox(group)
# #             if not bbox:
# #                 continue
# #             self.ensure_topology_fields(group)
# #             bx1, by1, bx2, by2 = bbox
# #             ratio_x = self.auto_layout_dimension_ratio(bbox, bounds, "x")
# #             ratio_y = self.auto_layout_dimension_ratio(bbox, bounds, "y")

# #             axis = self.project_meta.get("growth_axis", "both")
# #             if axis == "width":
# #                 grow_x, grow_y = True, False
# #             elif axis == "height":
# #                 grow_x, grow_y = False, True
# #             elif axis == "fixed":
# #                 grow_x, grow_y = False, False
# #             else:
# #                 grow_x = ratio_x >= 0.55
# #                 grow_y = ratio_y >= 0.55
# #             group["link_x"] = "X = W"
# #             group["link_y"] = "Y = H"
# #             group["shift_dir_x"] = "Вправо"
# #             group["shift_dir_y"] = "Вгору"
# #             group["growth_p_w"] = 1.0 if grow_x else 0.0
# #             group["growth_p_h"] = 1.0 if grow_y else 0.0

# #             if grow_x:
# #                 if abs(bx1 - min_x) <= edge_tol_x:
# #                     group["growth_dir_x"] = "Вправо"
# #                 elif abs(bx2 - max_x) <= edge_tol_x:
# #                     group["growth_dir_x"] = "Вліво"
# #                 else:
# #                     group["growth_dir_x"] = "Центр"
# #             else:
# #                 group["growth_dir_x"] = "Центр"

# #             if grow_y:
# #                 if abs(by1 - min_y) <= edge_tol_y:
# #                     group["growth_dir_y"] = "Вгору"
# #                 elif abs(by2 - max_y) <= edge_tol_y:
# #                     group["growth_dir_y"] = "Вниз"
# #                 else:
# #                     group["growth_dir_y"] = "Центр"
# #             else:
# #                 group["growth_dir_y"] = "Центр"

# #             group["auto_layout"] = True
# #             group["auto_layout_ratio_x"] = round(float(ratio_x), 6)
# #             group["auto_layout_ratio_y"] = round(float(ratio_y), 6)
# #             rows.append(
# #                 f"{group.get('name')} uid={self.get_group_key(group)}: "
# #                 f"ratioX={ratio_x:.3f}, ratioY={ratio_y:.3f}, "
# #                 f"growthX={group['growth_p_w']:.1f} dirX={group['growth_dir_x']}, "
# #                 f"growthY={group['growth_p_h']:.1f} dirY={group['growth_dir_y']}"
# #             )
# #         return rows

# #     def finish_auto_layout_position_rules(self):
# #         bounds = self.get_non_text_dxf_bounds()
# #         min_x, min_y, max_x, max_y = bounds
# #         if min_x is None:
# #             return []

# #         width = max(max_x - min_x, 0.0001)
# #         height = max(max_y - min_y, 0.0001)
# #         edge_tol_x = max(width * 0.025, 2.0)
# #         edge_tol_y = max(height * 0.025, 2.0)
# #         rows = ["AUTO LAYOUT FINISH / position shifts for fixed groups"]

# #         for group in self.parametric_groups:
# #             bbox = self.group_original_bbox(group)
# #             if not bbox:
# #                 continue
# #             bx1, by1, bx2, by2 = bbox
# #             cx = (bx1 + bx2) * 0.5
# #             cy = (by1 + by2) * 0.5

# #             if abs(float(group.get("growth_p_w", 0.0) or 0.0)) <= 0.000001:
# #                 if abs(bx1 - min_x) <= edge_tol_x:
# #                     k_w = 0.0
# #                     reason_x = "left edge"
# #                 elif abs(bx2 - max_x) <= edge_tol_x:
# #                     k_w = 1.0
# #                     reason_x = "right edge"
# #                 else:
# #                     k_w = (cx - min_x) / width
# #                     reason_x = "relative center X"
# #                 group["k_w"] = round(float(max(0.0, min(1.0, k_w))), 6)
# #                 group["link_x"] = "X = W"
# #                 group["shift_dir_x"] = "Вправо"
# #                 rows.append(f"{group.get('name')}: k_w={group['k_w']:.6f} ({reason_x})")

# #             if abs(float(group.get("growth_p_h", 0.0) or 0.0)) <= 0.000001:
# #                 if abs(by1 - min_y) <= edge_tol_y:
# #                     k_h = 0.0
# #                     reason_y = "bottom edge"
# #                 elif abs(by2 - max_y) <= edge_tol_y:
# #                     k_h = 1.0
# #                     reason_y = "top edge"
# #                 else:
# #                     k_h = (cy - min_y) / height
# #                     reason_y = "relative center Y"
# #                 group["k_h"] = round(float(max(0.0, min(1.0, k_h))), 6)
# #                 group["link_y"] = "Y = H"
# #                 group["shift_dir_y"] = "Вгору"
# #                 rows.append(f"{group.get('name')}: k_h={group['k_h']:.6f} ({reason_y})")

# #         return rows

# #     def auto_layout_all_groups(self):
# #         valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
# #         if not valid_groups:
# #             self.lbl_status_calc.setText("<font color='red'>Немає параметричних груп з геометрією для авторозстановки.</font>")
# #             return

# #         self.record_action_snapshot()
# #         rows = ["AUTHOROZSTAVYTY ALL / Авторозставити все"]
# #         rows.extend(self.seed_auto_layout_growth())

# #         self.suppress_auto_chain_snapshot = True
# #         try:
# #             self.auto_chain_growth_x()
# #             self.auto_chain_growth_y()
# #         finally:
# #             self.suppress_auto_chain_snapshot = False

# #         rows.extend(self.finish_auto_layout_position_rules())
# #         rows.append("Done: old k/growth coefficients are filled automatically; manual controls remain available.")

# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.on_group_selection_changed()
# #         self.update_viewer()
# #         self.topology_debug_print("AUTHOROZSTAVYTY ALL / Авторозставити все", rows)
# #         self.lbl_status_calc.setText("<font color='#a5d6a7'>Авторозставлення виконано: ріст і зсуви заповнені автоматично.</font>")

# #     def auto_chain_growth_y(self):
# #         """
# #         AUTO CHAIN Y / Авто сума росту Y, але НЕ одним загальним списком.

# #         ВАЖЛИВО:
# #         - ліва вертикальна сторона рахується окремо;
# #         - права вертикальна сторона рахується окремо;
# #         - центр рахується від середнього/узгодженого результату лівої і правої сторони;
# #         - групи, які лежать на одному Y-рівні, НЕ складаються одна з одною як 50%+50%.
# #           Для одного рівня береться максимальний ріст рівня, бо це одна і та сама висотна зона.

# #         Це виправляє ситуацію з логу:
# #             1 росте 50%
# #             рп1 росте 50%
# #         Вони не мають давати 100%, якщо це ліва/права сторона одного рівня.
# #         """
# #         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
# #         if min_x is None:
# #             self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автоматичної суми росту Y.</font>")
# #             self.topology_debug_print("AUTO CHAIN Y SIDES: немає геометрії")
# #             return

# #         axis_x = (min_x + max_x) * 0.5
# #         width = max_x - min_x
# #         height = max_y - min_y
# #         center_tolerance_x = max(width * 0.015, 2.0)
# #         level_tolerance_y = max(height * 0.003, 0.5)
# #         balance_tolerance = 0.0005  # 0.05%

# #         left_items = []
# #         right_items = []
# #         center_items = []

# #         for group in self.parametric_groups:
# #             bbox = self.group_original_bbox(group)
# #             if not bbox:
# #                 continue
# #             self.ensure_topology_fields(group)
# #             uid = self.get_group_key(group)
# #             bx1, by1, bx2, by2 = bbox
# #             center_x = (bx1 + bx2) * 0.5
# #             center_y = (by1 + by2) * 0.5
# #             growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))

# #             item = {
# #                 "group": group,
# #                 "uid": uid,
# #                 "name": group.get("name", ""),
# #                 "bbox": bbox,
# #                 "min_x": bx1,
# #                 "max_x": bx2,
# #                 "min_y": by1,
# #                 "max_y": by2,
# #                 "center_x": center_x,
# #                 "center_y": center_y,
# #                 "growth": growth,
# #             }

# #             # Якщо користувач уже вручну задав side_x у JSON — поважаємо це.
# #             explicit_side = str(group.get("side_x", "")).strip().lower()
# #             if explicit_side in ("left", "right", "center"):
# #                 side = explicit_side
# #             elif center_x < axis_x - center_tolerance_x:
# #                 side = "left"
# #             elif center_x > axis_x + center_tolerance_x:
# #                 side = "right"
# #             else:
# #                 side = "center"

# #             item["side"] = side
# #             if side == "left":
# #                 left_items.append(item)
# #             elif side == "right":
# #                 right_items.append(item)
# #             else:
# #                 center_items.append(item)

# #         if not left_items and not right_items and not center_items:
# #             self.lbl_status_calc.setText("<font color='red'>Немає груп для автоматичної суми росту Y.</font>")
# #             self.topology_debug_print("AUTO CHAIN Y SIDES: немає валідних груп")
# #             return

# #         def sort_bottom_up(items):
# #             items.sort(key=lambda item: (item["center_y"], item["min_y"], item["center_x"]))

# #         sort_bottom_up(left_items)
# #         sort_bottom_up(right_items)
# #         sort_bottom_up(center_items)

# #         def make_levels(items):
# #             """Об'єднує групи з майже однаковим center_y в один висотний рівень."""
# #             levels = []
# #             for item in items:
# #                 placed = False
# #                 for level in levels:
# #                     if abs(level["center_y"] - item["center_y"]) <= level_tolerance_y:
# #                         level["items"].append(item)
# #                         # Плавно уточнюємо центр рівня, щоб не залежати від першого елемента.
# #                         level["center_y"] = sum(x["center_y"] for x in level["items"]) / len(level["items"])
# #                         level["min_y"] = min(level["min_y"], item["min_y"])
# #                         level["max_y"] = max(level["max_y"], item["max_y"])
# #                         placed = True
# #                         break
# #                 if not placed:
# #                     levels.append({
# #                         "center_y": item["center_y"],
# #                         "min_y": item["min_y"],
# #                         "max_y": item["max_y"],
# #                         "items": [item],
# #                     })
# #             levels.sort(key=lambda level: (level["center_y"], level["min_y"]))
# #             for level in levels:
# #                 # Рівень — це одна висотна зона. Не складаємо 50%+50% для паралельних деталей одного рівня.
# #                 level["growth"] = max((x["growth"] for x in level["items"]), default=0.0)
# #             return levels

# #         left_levels = make_levels(left_items)
# #         right_levels = make_levels(right_items)
# #         center_levels = make_levels(center_items)

# #         left_sum = sum(level["growth"] for level in left_levels)
# #         right_sum = sum(level["growth"] for level in right_levels)
# #         diff = abs(left_sum - right_sum)

# #         rows = []
# #         rows.append("AUTO CHAIN Y SIDES / Авто сума росту Y по лівій/правій стороні")
# #         rows.append("Тепер це НЕ один список знизу вгору для всіх груп.")
# #         rows.append("Ліва сторона, права сторона і центр розділяються по X.")
# #         rows.append("Групи на одному Y-рівні не додаються одна до одної: для рівня береться MAX growth_p_h.")
# #         rows.append("")
# #         rows.append(f"bounds: minX={min_x:.3f}, maxX={max_x:.3f}, minY={min_y:.3f}, maxY={max_y:.3f}")
# #         rows.append(f"axis_x={axis_x:.3f}, center_tolerance_x={center_tolerance_x:.3f}, level_tolerance_y={level_tolerance_y:.3f}")
# #         rows.append("")

# #         def describe_side(side_name, items, levels):
# #             rows.append(f"{side_name} groups після поділу по X:")
# #             if not items:
# #                 rows.append("  немає")
# #             for i, item in enumerate(items, start=1):
# #                 rows.append(
# #                     f"  {side_name[0]}#{i}: name={item['name']} uid={item['uid']} side={item['side']} "
# #                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}, "
# #                     f"minY={item['min_y']:.3f}, maxY={item['max_y']:.3f}) "
# #                     f"centerX={item['center_x']:.3f}; centerY={item['center_y']:.3f}; "
# #                     f"own_growth_p_h={item['growth']:.6f} ({item['growth']*100:.2f}%)"
# #                 )
# #             rows.append(f"{side_name} Y-рівні:")
# #             if not levels:
# #                 rows.append("  немає")
# #             for j, level in enumerate(levels, start=1):
# #                 names = ", ".join(f"{x['name']}[{x['uid']}]" for x in level["items"])
# #                 item_growths = ", ".join(f"{x['growth']*100:.2f}%" for x in level["items"])
# #                 rows.append(
# #                     f"  level {j}: centerY≈{level['center_y']:.3f}; items={names}; "
# #                     f"item_growths=[{item_growths}]; level_growth=MAX={level['growth']:.6f} ({level['growth']*100:.2f}%)"
# #                 )
# #             rows.append("")

# #         describe_side("LEFT", left_items, left_levels)
# #         describe_side("RIGHT", right_items, right_levels)
# #         describe_side("CENTER", center_items, center_levels)

# #         rows.append(f"SUM LEFT LEVELS  = {left_sum:.6f} ({left_sum*100:.2f}%)")
# #         rows.append(f"SUM RIGHT LEVELS = {right_sum:.6f} ({right_sum*100:.2f}%)")
# #         rows.append(f"DIFF             = {diff:.6f} ({diff*100:.2f}%)")

# #         normalize_to = None
# #         has_both_sides = bool(left_levels) and bool(right_levels)
# #         if has_both_sides and diff > balance_tolerance:
# #             rows.append("")
# #             rows.append("WARNING: ліва і права сторона мають різний сумарний ріст по Y.")
# #             rows.append("Перед записом k_h треба уточнити у конструктора.")
# #             self.topology_debug_print("AUTO CHAIN Y SIDES / ПОТРІБНЕ УТОЧНЕННЯ", rows)

# #             msg = (
# #                 "Сумарний ріст по Y зліва і справа різний.\n\n"
# #                 f"LEFT = {left_sum*100:.2f}%\n"
# #                 f"RIGHT = {right_sum*100:.2f}%\n"
# #                 f"DIFF = {diff*100:.2f}%\n\n"
# #                 "Так — вирівняти до більшої суми пропорційно.\n"
# #                 "Ні — застосувати як є, з різними зсувами.\n"
# #                 "Cancel — нічого не змінювати."
# #             )
# #             answer = QMessageBox.question(
# #                 self,
# #                 "Y-сторони мають різний сумарний ріст",
# #                 msg,
# #                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
# #                 QMessageBox.StandardButton.Cancel,
# #             )

# #             if answer == QMessageBox.StandardButton.Cancel:
# #                 rows.append("КОНСТРУКТОР СКАСУВАВ: правила Y не застосовано.")
# #                 self.topology_debug_print("AUTO CHAIN Y SIDES / Скасовано", rows)
# #                 self.lbl_status_calc.setText("<font color='#ffcc80'>Авто сума Y скасована: сторони мали різний сумарний ріст.</font>")
# #                 return

# #             if answer == QMessageBox.StandardButton.Yes:
# #                 normalize_to = max(left_sum, right_sum)
# #                 rows.append("")
# #                 rows.append(f"КОНСТРУКТОР ОБРАВ ВИРІВНЯТИ: target_sum={normalize_to:.6f} ({normalize_to*100:.2f}%)")
# #             else:
# #                 rows.append("")
# #                 rows.append("КОНСТРУКТОР ОБРАВ ЗАСТОСУВАТИ ЯК Є: ліва/права сторона можуть мати різні k_h.")
# #         elif has_both_sides:
# #             rows.append("OK: сумарний ріст лівої і правої сторони по Y однаковий у межах допуску.")
# #         else:
# #             rows.append("INFO: знайдена тільки одна сторона або тільки центр; порівнювати LEFT/RIGHT немає з чим.")

# #         if not getattr(self, "suppress_auto_chain_snapshot", False):
# #             self.record_action_snapshot()

# #         def scale_levels(levels, current_sum, target_sum, side_name):
# #             if target_sum is None or abs(current_sum - target_sum) <= balance_tolerance:
# #                 return
# #             if current_sum <= 0.000001:
# #                 rows.append(
# #                     f"NORMALIZE {side_name}: поточна сума 0%, неможливо пропорційно масштабувати. "
# #                     f"Задай growth_p_h хоча б для одного рівня цієї сторони вручну."
# #                 )
# #                 return
# #             factor = target_sum / current_sum
# #             rows.append(
# #                 f"NORMALIZE {side_name}: current_sum={current_sum:.6f} -> target_sum={target_sum:.6f}; factor={factor:.6f}"
# #             )
# #             for level in levels:
# #                 old_level_growth = level["growth"]
# #                 new_level_growth = old_level_growth * factor
# #                 level["growth"] = new_level_growth
# #                 rows.append(
# #                     f"  {side_name} level centerY≈{level['center_y']:.3f}: "
# #                     f"level_growth {old_level_growth:.6f} -> {new_level_growth:.6f} "
# #                     f"({old_level_growth*100:.2f}% -> {new_level_growth*100:.2f}%)"
# #                 )
# #                 # Масштабуємо тільки ті групи рівня, які реально мали ріст.
# #                 for item in level["items"]:
# #                     g = item["group"]
# #                     old = abs(float(g.get("growth_p_h", 0.0) or 0.0))
# #                     if old > 0.000001:
# #                         new_val = old * factor
# #                         g["growth_p_h"] = round(float(new_val), 6)
# #                         item["growth"] = new_val
# #                         rows.append(
# #                             f"    {side_name} {g.get('name')} uid={item['uid']}: growth_p_h {old:.6f} -> {new_val:.6f} "
# #                             f"({old*100:.2f}% -> {new_val*100:.2f}%)"
# #                         )

# #         if normalize_to is not None:
# #             scale_levels(left_levels, left_sum, normalize_to, "LEFT")
# #             scale_levels(right_levels, right_sum, normalize_to, "RIGHT")
# #             left_sum = sum(level["growth"] for level in left_levels)
# #             right_sum = sum(level["growth"] for level in right_levels)
# #             diff = abs(left_sum - right_sum)
# #             rows.append("")
# #             rows.append("Після вирівнювання:")
# #             rows.append(f"SUM LEFT LEVELS  = {left_sum:.6f} ({left_sum*100:.2f}%)")
# #             rows.append(f"SUM RIGHT LEVELS = {right_sum:.6f} ({right_sum*100:.2f}%)")
# #             rows.append(f"DIFF             = {diff:.6f} ({diff*100:.2f}%)")

# #         def apply_levels(levels, side_name):
# #             cumulative = 0.0
# #             rows.append("")
# #             rows.append(f"Застосування {side_name} Y-chain:")
# #             for level_index, level in enumerate(levels, start=1):
# #                 before = cumulative
# #                 level_growth = float(level.get("growth", 0.0) or 0.0)
# #                 rows.append(
# #                     f"  {side_name} level {level_index}: centerY≈{level['center_y']:.3f}; "
# #                     f"sum_below={before:.6f} ({before*100:.2f}%); "
# #                     f"level_growth={level_growth:.6f} ({level_growth*100:.2f}%)"
# #                 )
# #                 for item in level["items"]:
# #                     group = item["group"]
# #                     uid = item["uid"]
# #                     old_k = float(group.get("k_h", 0.0) or 0.0)
# #                     old_growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))

# #                     group["k_h"] = round(float(before), 6)
# #                     group["growth_p_h"] = round(float(old_growth), 6)
# #                     if old_growth > 0.000001:
# #                         group["growth_dir_y"] = "Вгору"
# #                     group["link_y"] = "Y = H"
# #                     group["side_y_chain"] = side_name.lower()
# #                     group["auto_chain_y"] = True
# #                     group["auto_chain_y_mode"] = "side_levels"
# #                     group["chain_shift_y"] = round(float(before), 6)
# #                     group["chain_growth_own_y"] = round(float(old_growth), 6)
# #                     group["chain_level_growth_y"] = round(float(level_growth), 6)
# #                     group["chain_growth_after_y"] = round(float(before + level_growth), 6)

# #                     rows.append(
# #                         f"    {side_name} {group.get('name')} uid={uid}: "
# #                         f"old_k_h={old_k:.6f} -> new_k_h={before:.6f} ({before*100:.2f}%); "
# #                         f"own_growth_p_h={old_growth:.6f} ({old_growth*100:.2f}%); "
# #                         f"level_growth_used={level_growth:.6f} ({level_growth*100:.2f}%); "
# #                         f"dir={group.get('growth_dir_y')}"
# #                     )
# #                 cumulative += level_growth
# #             rows.append(f"  {side_name} final cumulative={cumulative:.6f} ({cumulative*100:.2f}%)")
# #             return cumulative

# #         final_left = apply_levels(left_levels, "LEFT") if left_levels else 0.0
# #         final_right = apply_levels(right_levels, "RIGHT") if right_levels else 0.0

# #         # Центр не складається сам із собою. Для центральних груп беремо shift на їхньому Y-рівні
# #         # як середнє між лівою і правою стороною для такого самого рівня.
# #         def shift_at_y(levels, y):
# #             cumulative = 0.0
# #             for level in levels:
# #                 if level["center_y"] < y - level_tolerance_y:
# #                     cumulative += float(level.get("growth", 0.0) or 0.0)
# #             return cumulative

# #         rows.append("")
# #         rows.append("Застосування CENTER Y-chain:")
# #         if center_levels:
# #             for level in center_levels:
# #                 center_y = level["center_y"]
# #                 left_shift = shift_at_y(left_levels, center_y) if left_levels else None
# #                 right_shift = shift_at_y(right_levels, center_y) if right_levels else None
# #                 if left_shift is not None and right_shift is not None:
# #                     center_shift = (left_shift + right_shift) * 0.5
# #                     reason = f"average(left_shift={left_shift:.6f}, right_shift={right_shift:.6f})"
# #                 elif left_shift is not None:
# #                     center_shift = left_shift
# #                     reason = f"left_shift={left_shift:.6f}"
# #                 elif right_shift is not None:
# #                     center_shift = right_shift
# #                     reason = f"right_shift={right_shift:.6f}"
# #                 else:
# #                     center_shift = 0.0
# #                     reason = "no side levels"

# #                 level_growth = float(level.get("growth", 0.0) or 0.0)
# #                 for item in level["items"]:
# #                     group = item["group"]
# #                     uid = item["uid"]
# #                     old_k = float(group.get("k_h", 0.0) or 0.0)
# #                     old_growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))
# #                     group["k_h"] = round(float(center_shift), 6)
# #                     group["growth_p_h"] = round(float(old_growth), 6)
# #                     if old_growth > 0.000001:
# #                         group["growth_dir_y"] = "Вгору"
# #                     group["link_y"] = "Y = H"
# #                     group["side_y_chain"] = "center"
# #                     group["auto_chain_y"] = True
# #                     group["auto_chain_y_mode"] = "side_levels_center"
# #                     group["chain_shift_y"] = round(float(center_shift), 6)
# #                     group["chain_growth_own_y"] = round(float(old_growth), 6)
# #                     group["chain_level_growth_y"] = round(float(level_growth), 6)
# #                     rows.append(
# #                         f"  CENTER {group.get('name')} uid={uid}: old_k_h={old_k:.6f} -> new_k_h={center_shift:.6f} "
# #                         f"({center_shift*100:.2f}%); own_growth={old_growth:.6f}; reason={reason}"
# #                     )
# #         else:
# #             rows.append("  немає")

# #         rows.append("")
# #         rows.append("ФІНАЛ Y:")
# #         rows.append(f"  LEFT total  = {final_left:.6f} ({final_left*100:.2f}%)")
# #         rows.append(f"  RIGHT total = {final_right:.6f} ({final_right*100:.2f}%)")
# #         rows.append(f"  DIFF        = {abs(final_left-final_right):.6f} ({abs(final_left-final_right)*100:.2f}%)")
# #         rows.append("  Тепер 1 і рп1 не складаються у 100%, якщо вони є лівою/правою стороною одного рівня.")

# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.on_group_selection_changed()
# #         self.update_viewer()
# #         self.topology_debug_print("AUTO CHAIN Y SIDES / Авто сума росту Y по сторонах", rows)

# #         if has_both_sides and abs(final_left - final_right) <= balance_tolerance:
# #             self.lbl_status_calc.setText(
# #                 f"<font color='#a5d6a7'>Авто сума Y по сторонах застосована. LEFT≈RIGHT={final_left*100:.1f}%.</font>"
# #             )
# #         else:
# #             self.lbl_status_calc.setText(
# #                 f"<font color='#ffcc80'>Авто сума Y застосована: LEFT={final_left*100:.1f}%, RIGHT={final_right*100:.1f}%.</font>"
# #             )

# #     def auto_chain_growth_x(self):
# #         """
# #         AUTO CHAIN X / Авто сума росту X, але правильно для дверей/вікон:

# #         ВАЖЛИВО:
# #         - ліва сторона рахується окремо: від лівого краю до центру;
# #         - права сторона рахується окремо: від правого краю до центру;
# #         - сумарний growth_p_w лівої сторони порівнюється із сумарним growth_p_w правої сторони;
# #         - якщо суми різні, програма питає конструктора, що робити.

# #         Для лівої сторони:
# #             k_w = сума ростів лівіше
# #             growth_dir_x = Вправо

# #         Для правої сторони:
# #             k_w = 1 - сума ростів правіше
# #             growth_dir_x = Вліво

# #         Приклад:
# #             LEFT:  10% + 15% = 25%
# #             RIGHT: 5% + 20%  = 25%
# #             => OK, сторони збалансовані.

# #             LEFT:  25%
# #             RIGHT: 30%
# #             => WARNING, треба уточнення конструктора.
# #         """
# #         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
# #         if min_x is None:
# #             self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автоматичної суми росту X.</font>")
# #             self.topology_debug_print("AUTO CHAIN X SIDES: немає геометрії")
# #             return

# #         axis_x = (min_x + max_x) * 0.5
# #         width = max_x - min_x
# #         center_tolerance = max(width * 0.015, 2.0)

# #         left_items = []
# #         right_items = []
# #         center_items = []

# #         for group in self.parametric_groups:
# #             bbox = self.group_original_bbox(group)
# #             if not bbox:
# #                 continue
# #             self.ensure_topology_fields(group)
# #             uid = self.get_group_key(group)
# #             bx1, by1, bx2, by2 = bbox
# #             center_x = (bx1 + bx2) * 0.5

# #             item = {
# #                 "group": group,
# #                 "uid": uid,
# #                 "name": group.get("name", ""),
# #                 "bbox": bbox,
# #                 "min_x": bx1,
# #                 "max_x": bx2,
# #                 "center_x": center_x,
# #                 "growth": abs(float(group.get("growth_p_w", 0.0) or 0.0)),
# #             }

# #             if center_x < axis_x - center_tolerance:
# #                 item["side"] = "left"
# #                 left_items.append(item)
# #             elif center_x > axis_x + center_tolerance:
# #                 item["side"] = "right"
# #                 right_items.append(item)
# #             else:
# #                 item["side"] = "center"
# #                 center_items.append(item)

# #         if not left_items and not right_items:
# #             self.lbl_status_calc.setText("<font color='red'>Не знайдено лівих/правих груп для X-логіки.</font>")
# #             self.topology_debug_print("AUTO CHAIN X SIDES: немає лівих/правих груп")
# #             return

# #         left_items.sort(key=lambda item: (item["center_x"], item["min_x"]))
# #         # Права сторона рахується від правого краю до центру.
# #         right_items.sort(key=lambda item: (-item["center_x"], -item["max_x"]))
# #         center_items.sort(key=lambda item: (item["center_x"], item["min_x"]))

# #         left_sum = sum(item["growth"] for item in left_items)
# #         right_sum = sum(item["growth"] for item in right_items)
# #         diff = abs(left_sum - right_sum)
# #         balance_tolerance = 0.0005  # 0.05%

# #         rows = []
# #         rows.append("AUTO CHAIN X SIDES / Авто сума росту X по сторонах")
# #         rows.append("НЕ один загальний ланцюг зліва направо, а два незалежні ланцюги:")
# #         rows.append("  LEFT:  лівий край -> центр, growth_dir_x=Вправо")
# #         rows.append("  RIGHT: правий край -> центр, growth_dir_x=Вліво")
# #         rows.append("Після цього програма порівнює сумарний % росту LEFT і RIGHT.")
# #         rows.append("")
# #         rows.append(f"bounds_x: minX={min_x:.3f}, maxX={max_x:.3f}, width={width:.3f}")
# #         rows.append(f"axis_x={axis_x:.3f}, center_tolerance={center_tolerance:.3f}")
# #         rows.append("")

# #         rows.append("LEFT groups, від лівого краю до центру:")
# #         if left_items:
# #             for i, item in enumerate(left_items, start=1):
# #                 rows.append(
# #                     f"  L#{i}: name={item['name']} uid={item['uid']} "
# #                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
# #                     f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
# #                 )
# #         else:
# #             rows.append("  немає")

# #         rows.append("")
# #         rows.append("RIGHT groups, від правого краю до центру:")
# #         if right_items:
# #             for i, item in enumerate(right_items, start=1):
# #                 rows.append(
# #                     f"  R#{i}: name={item['name']} uid={item['uid']} "
# #                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
# #                     f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
# #                 )
# #         else:
# #             rows.append("  немає")

# #         rows.append("")
# #         rows.append("CENTER groups, біля центру, не беруть участь у сумі сторін:")
# #         if center_items:
# #             for i, item in enumerate(center_items, start=1):
# #                 rows.append(
# #                     f"  C#{i}: name={item['name']} uid={item['uid']} "
# #                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
# #                     f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
# #                 )
# #         else:
# #             rows.append("  немає")

# #         rows.append("")
# #         rows.append(f"SUM LEFT  = {left_sum:.6f} ({left_sum*100:.2f}%)")
# #         rows.append(f"SUM RIGHT = {right_sum:.6f} ({right_sum*100:.2f}%)")
# #         rows.append(f"DIFF      = {diff:.6f} ({diff*100:.2f}%)")

# #         # Якщо суми не рівні, перед застосуванням питаємо конструктора.
# #         normalize_to = None
# #         if diff > balance_tolerance:
# #             rows.append("")
# #             rows.append("WARNING: Сумарний ріст лівої і правої сторони НЕ однаковий.")
# #             rows.append("Програма має уточнити у конструктора перед записом k_w.")
# #             self.topology_debug_print("AUTO CHAIN X SIDES / ПОТРІБНЕ УТОЧНЕННЯ", rows)

# #             msg = (
# #                 "Сумарний ріст лівої і правої сторони різний.\n\n"
# #                 f"LEFT = {left_sum*100:.2f}%\n"
# #                 f"RIGHT = {right_sum*100:.2f}%\n"
# #                 f"DIFF = {diff*100:.2f}%\n\n"
# #                 "Так — вирівняти до більшої суми пропорційно.\n"
# #                 "Ні — застосувати як є, з різними зсувами.\n"
# #                 "Cancel — нічого не змінювати."
# #             )
# #             answer = QMessageBox.question(
# #                 self,
# #                 "X-сторони мають різний сумарний ріст",
# #                 msg,
# #                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
# #                 QMessageBox.StandardButton.Cancel,
# #             )

# #             if answer == QMessageBox.StandardButton.Cancel:
# #                 rows.append("КОНСТРУКТОР СКАСУВАВ: правила X не застосовано.")
# #                 self.topology_debug_print("AUTO CHAIN X SIDES / Скасовано", rows)
# #                 self.lbl_status_calc.setText("<font color='#ffcc80'>Авто сума X скасована: сторони мали різний сумарний ріст.</font>")
# #                 return

# #             if answer == QMessageBox.StandardButton.Yes:
# #                 normalize_to = max(left_sum, right_sum)
# #                 rows.append("")
# #                 rows.append(f"КОНСТРУКТОР ОБРАВ ВИРІВНЯТИ: target_sum={normalize_to:.6f} ({normalize_to*100:.2f}%)")
# #             else:
# #                 rows.append("")
# #                 rows.append("КОНСТРУКТОР ОБРАВ ЗАСТОСУВАТИ ЯК Є: ліві і праві зсуви можуть відрізнятися.")
# #         else:
# #             rows.append("OK: Сумарний ріст лівої і правої сторони однаковий у межах допуску.")

# #         if not getattr(self, "suppress_auto_chain_snapshot", False):
# #             self.record_action_snapshot()

# #         def scale_side(items, current_sum, target_sum, side_name):
# #             if target_sum is None or abs(current_sum - target_sum) <= balance_tolerance:
# #                 return
# #             if current_sum <= 0.000001:
# #                 rows.append(
# #                     f"NORMALIZE {side_name}: поточна сума 0%, неможливо пропорційно масштабувати. "
# #                     f"Задай growth_p_w хоча б для однієї групи цієї сторони вручну."
# #                 )
# #                 return
# #             factor = target_sum / current_sum
# #             rows.append(
# #                 f"NORMALIZE {side_name}: current_sum={current_sum:.6f} -> target_sum={target_sum:.6f}; "
# #                 f"factor={factor:.6f}"
# #             )
# #             for item in items:
# #                 g = item["group"]
# #                 old = abs(float(g.get("growth_p_w", 0.0) or 0.0))
# #                 new_val = old * factor
# #                 g["growth_p_w"] = round(float(new_val), 6)
# #                 item["growth"] = new_val
# #                 rows.append(
# #                     f"  {side_name} {g.get('name')} uid={item['uid']}: growth_p_w {old:.6f} -> {new_val:.6f} "
# #                     f"({old*100:.2f}% -> {new_val*100:.2f}%)"
# #                 )

# #         if normalize_to is not None:
# #             scale_side(left_items, left_sum, normalize_to, "LEFT")
# #             scale_side(right_items, right_sum, normalize_to, "RIGHT")
# #             left_sum = sum(item["growth"] for item in left_items)
# #             right_sum = sum(item["growth"] for item in right_items)
# #             diff = abs(left_sum - right_sum)
# #             rows.append("")
# #             rows.append("Після вирівнювання:")
# #             rows.append(f"SUM LEFT  = {left_sum:.6f} ({left_sum*100:.2f}%)")
# #             rows.append(f"SUM RIGHT = {right_sum:.6f} ({right_sum*100:.2f}%)")
# #             rows.append(f"DIFF      = {diff:.6f} ({diff*100:.2f}%)")

# #         rows.append("")
# #         rows.append("Застосування LEFT chain:")
# #         cumulative_left = 0.0
# #         for item in left_items:
# #             group = item["group"]
# #             uid = item["uid"]
# #             old_k = float(group.get("k_w", 0.0) or 0.0)
# #             own_growth = abs(float(group.get("growth_p_w", 0.0) or 0.0))
# #             new_k = cumulative_left

# #             group["k_w"] = round(float(new_k), 6)
# #             group["growth_p_w"] = round(float(own_growth), 6)
# #             group["growth_dir_x"] = "Вправо" if own_growth > 0.000001 else group.get("growth_dir_x", "Центр")
# #             group["link_x"] = "X = W"
# #             group["side_x"] = "left"
# #             group["auto_chain_x"] = True
# #             group["auto_chain_x_mode"] = "side_sum"
# #             group["chain_shift_x"] = round(float(new_k), 6)
# #             group["chain_growth_own_x"] = round(float(own_growth), 6)

# #             before = cumulative_left
# #             cumulative_left += own_growth
# #             group["chain_growth_after_x"] = round(float(cumulative_left), 6)
# #             group["side_sum_x"] = round(float(left_sum), 6)

# #             rows.append(
# #                 f"  LEFT {group.get('name')} uid={uid}: "
# #                 f"old_k_w={old_k:.6f} -> new_k_w=sum_from_left={new_k:.6f} ({new_k*100:.2f}%); "
# #                 f"own_growth={own_growth:.6f} ({own_growth*100:.2f}%); "
# #                 f"sum_before={before:.6f}; sum_after={cumulative_left:.6f}; dir={group.get('growth_dir_x')}"
# #             )

# #         rows.append("")
# #         rows.append("Застосування RIGHT chain:")
# #         cumulative_right = 0.0
# #         for item in right_items:
# #             group = item["group"]
# #             uid = item["uid"]
# #             old_k = float(group.get("k_w", 0.0) or 0.0)
# #             own_growth = abs(float(group.get("growth_p_w", 0.0) or 0.0))
# #             # Права сторона прив'язана до правого краю.
# #             # Найправіша група має k_w=1.0, а кожен внутрішній ріст справа зменшує k_w для наступних до центру.
# #             new_k = 1.0 - cumulative_right

# #             group["k_w"] = round(float(new_k), 6)
# #             group["growth_p_w"] = round(float(own_growth), 6)
# #             group["growth_dir_x"] = "Вліво" if own_growth > 0.000001 else group.get("growth_dir_x", "Центр")
# #             group["link_x"] = "X = W"
# #             group["side_x"] = "right"
# #             group["auto_chain_x"] = True
# #             group["auto_chain_x_mode"] = "side_sum"
# #             group["chain_shift_x"] = round(float(new_k), 6)
# #             group["chain_growth_own_x"] = round(float(own_growth), 6)

# #             before = cumulative_right
# #             cumulative_right += own_growth
# #             group["chain_growth_after_x"] = round(float(cumulative_right), 6)
# #             group["side_sum_x"] = round(float(right_sum), 6)

# #             rows.append(
# #                 f"  RIGHT {group.get('name')} uid={uid}: "
# #                 f"old_k_w={old_k:.6f} -> new_k_w=1-sum_from_right={new_k:.6f} ({new_k*100:.2f}%); "
# #                 f"own_growth={own_growth:.6f} ({own_growth*100:.2f}%); "
# #                 f"sum_before={before:.6f}; sum_after={cumulative_right:.6f}; dir={group.get('growth_dir_x')}"
# #             )

# #         rows.append("")
# #         rows.append("CENTER groups:")
# #         center_k = left_sum if diff <= balance_tolerance or normalize_to is not None else (left_sum + (1.0 - right_sum)) * 0.5
# #         for item in center_items:
# #             group = item["group"]
# #             old_k = float(group.get("k_w", 0.0) or 0.0)
# #             group["k_w"] = round(float(center_k), 6)
# #             group["link_x"] = "X = W"
# #             group["side_x"] = "center"
# #             group["auto_chain_x"] = True
# #             group["auto_chain_x_mode"] = "side_sum_center"
# #             group["chain_shift_x"] = round(float(center_k), 6)
# #             group["side_sum_left_x"] = round(float(left_sum), 6)
# #             group["side_sum_right_x"] = round(float(right_sum), 6)
# #             rows.append(
# #                 f"  CENTER {group.get('name')} uid={item['uid']}: old_k_w={old_k:.6f} -> new_k_w={center_k:.6f} "
# #                 f"({center_k*100:.2f}%). Це центральна зона між лівою і правою сторонами."
# #             )

# #         rows.append("")
# #         rows.append("ФІНАЛ:")
# #         rows.append(f"  LEFT total  = {left_sum:.6f} ({left_sum*100:.2f}%)")
# #         rows.append(f"  RIGHT total = {right_sum:.6f} ({right_sum*100:.2f}%)")
# #         rows.append(f"  DIFF        = {abs(left_sum-right_sum):.6f} ({abs(left_sum-right_sum)*100:.2f}%)")
# #         rows.append("  Ліві/праві групи можуть мати різні k_w, але сумарний % росту сторін контролюється.")

# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.on_group_selection_changed()
# #         self.update_viewer()
# #         self.topology_debug_print("AUTO CHAIN X SIDES / Авто сума росту X по сторонах", rows)

# #         if abs(left_sum - right_sum) <= balance_tolerance:
# #             self.lbl_status_calc.setText(
# #                 f"<font color='#a5d6a7'>Авто сума X по сторонах застосована. LEFT=RIGHT={left_sum*100:.1f}%.</font>"
# #             )
# #         else:
# #             self.lbl_status_calc.setText(
# #                 f"<font color='#ffcc80'>Авто сума X застосована з різними сторонами: LEFT={left_sum*100:.1f}%, RIGHT={right_sum*100:.1f}%.</font>"
# #             )

# #     def auto_detect_vertical_touch_constraints(self, tolerance=3.0):
# #         """
# #         TOUCH Y / Зберігати дотик Y.

# #         Що робить:
# #         1) очищає старі touch-зв'язки;
# #         2) сортує групи знизу вгору;
# #         3) для кожної нижньої групи шукає найближчу верхню групу;
# #         4) перевіряє, чи вони перетинаються по X, тобто реально стоять одна над одною;
# #         5) рахує gap = upper.minY - lower.maxY;
# #         6) якщо gap від 0 до tolerance, записує:
# #            lower.touch_y_enabled = True
# #            lower.touch_to_uid = upper.uid
# #            lower.touch_gap_y = gap

# #         Під час глобального перерахунку calculate_touch_extra_y_shifts() тримає цей gap.
# #         """
# #         valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
# #         if len(valid_groups) < 2:
# #             self.lbl_status_calc.setText("<font color='red'>Потрібно мінімум дві групи для пошуку дотику.</font>")
# #             self.topology_debug_print("TOUCH Y: потрібно мінімум дві групи")
# #             return

# #         self.record_action_snapshot()
# #         rows = []
# #         rows.append("TOUCH Y / Зберігати дотик Y")
# #         rows.append(f"tolerance={tolerance:.3f} мм")
# #         rows.append("Сенс: якщо нижня група торкається верхньої або має малий зазор, програма запам'ятовує цей зазор.")
# #         rows.append("Потім при перерахунку верхня група додатково зсувається, щоб gap залишився такий самий.")
# #         rows.append("")

# #         for group in valid_groups:
# #             self.ensure_topology_fields(group)
# #             uid = self.get_group_key(group)
# #             old_enabled = group.get("touch_y_enabled")
# #             old_to = group.get("touch_to_uid")
# #             old_gap = group.get("touch_gap_y")
# #             group["touch_y_enabled"] = False
# #             group["touch_to_uid"] = None
# #             group["touch_gap_y"] = 0.0
# #             rows.append(f"Очистка старого touch: group={group.get('name')} uid={uid}; old_enabled={old_enabled}; old_to={old_to}; old_gap={old_gap}")

# #         sorted_groups = sorted(valid_groups, key=self.group_center_y)
# #         rows.append("")
# #         rows.append("Групи знизу вгору:")
# #         for i, group in enumerate(sorted_groups, start=1):
# #             bbox = self.group_original_bbox(group)
# #             rows.append(
# #                 f"  #{i}: name={group.get('name')} uid={self.get_group_key(group)} "
# #                 f"bbox=(minX={bbox[0]:.3f}, minY={bbox[1]:.3f}, maxX={bbox[2]:.3f}, maxY={bbox[3]:.3f})"
# #             )

# #         constraints_count = 0
# #         rows.append("")
# #         rows.append("Пошук найближчої верхньої групи для кожної нижньої:")

# #         for lower in sorted_groups:
# #             lower_uid = self.get_group_key(lower)
# #             lower_bbox = self.group_original_bbox(lower)
# #             best_upper = None
# #             best_gap = None

# #             rows.append(f"\nLOWER group={lower.get('name')} uid={lower_uid}; lower_top=maxY={lower_bbox[3]:.3f}")

# #             for upper in sorted_groups:
# #                 if upper is lower:
# #                     continue
# #                 upper_uid = self.get_group_key(upper)
# #                 upper_bbox = self.group_original_bbox(upper)
# #                 overlap_x = self.groups_overlap_by_x(lower_bbox, upper_bbox, tolerance=tolerance)
# #                 gap = upper_bbox[1] - lower_bbox[3]

# #                 if not overlap_x:
# #                     rows.append(
# #                         f"  candidate upper={upper.get('name')} uid={upper_uid}: SKIP, "
# #                         f"немає перетину по X; gap={gap:.3f}"
# #                     )
# #                     continue
# #                 if gap < -tolerance:
# #                     rows.append(
# #                         f"  candidate upper={upper.get('name')} uid={upper_uid}: SKIP, "
# #                         f"накладання по Y більше tolerance; gap={gap:.3f}"
# #                     )
# #                     continue

# #                 rows.append(
# #                     f"  candidate upper={upper.get('name')} uid={upper_uid}: OK candidate, "
# #                     f"overlap_x=True; gap=upper.minY({upper_bbox[1]:.3f}) - lower.maxY({lower_bbox[3]:.3f}) = {gap:.3f}"
# #                 )

# #                 if best_gap is None or gap < best_gap:
# #                     best_gap = gap
# #                     best_upper = upper

# #             if best_upper is not None and best_gap is not None and best_gap <= tolerance:
# #                 upper_uid = self.get_group_key(best_upper)
# #                 lower["touch_y_enabled"] = True
# #                 lower["touch_to_uid"] = upper_uid
# #                 lower["touch_gap_y"] = float(best_gap)
# #                 constraints_count += 1
# #                 rows.append(
# #                     f"  => TOUCH SAVED: lower={lower_uid} -> upper={upper_uid}; "
# #                     f"saved_gap_y={best_gap:.3f} мм"
# #                 )
# #             else:
# #                 rows.append("  => TOUCH NOT SAVED: немає верхньої групи в межах tolerance")

# #         rows.append("")
# #         rows.append(f"РЕЗУЛЬТАТ: знайдено touch-зв'язків Y = {constraints_count}")
# #         rows.append("Під час перерахунку буде лог [TOUCH DEBUG] START TOUCH Y CORRECTION — там видно корекцію у мм.")
# #         self.topology_debug_print("TOUCH Y / Зберігати дотик Y", rows)

# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.update_viewer()
# #         self.lbl_status_calc.setText(
# #             f"<font color='#a5d6a7'>Знайдено вертикальних зв'язків дотику: {constraints_count}. Деталі дивись у консолі: [TOPOLOGY DEBUG] TOUCH Y.</font>"
# #         )

# #     # ============================================================
# #     # РУХОМИЙ ПОЧАТКОВИЙ TEXT / MTEXT
# #     # ============================================================
# #     def on_existing_dxf_text_moved(self, item):
# #         """
# #         Коли користувач перетягнув TEXT/MTEXT, який вже був у початковому DXF,
# #         ми оновлюємо insert у самому DXF і зберігаємо файл.
# #         """
# #         handle = getattr(item, "handle", None)
# #         if not handle or handle not in self.doc.entitydb:
# #             print(f"[TEXT MOVE DEBUG] handle={handle} не знайдено в DXF entitydb")
# #             return

# #         entity = self.doc.entitydb[handle]
# #         tp = entity.dxftype()
# #         pos = item.pos()
# #         old_insert = tuple(entity.dxf.insert) if hasattr(entity.dxf, "insert") else None

# #         # У сцені Y інвертований: CAD y = -scene_y - text_height.
# #         text_height = float(getattr(entity.dxf, "height", 10.0) or 10.0)
# #         new_x = float(pos.x())
# #         new_y = float(-pos.y() - text_height)

# #         if tp in ("TEXT", "MTEXT"):
# #             entity.dxf.insert = (new_x, new_y, 0.0)

# #         self.selected_handles = {handle}
# #         self.doc.saveas(self.dxf_path)
# #         self.save_original_geometries()
# #         self.load_entities_into_list()
# #         self.sync_list_from_handles()
# #         self.save_project_config()

# #         print("\n" + "=" * 90)
# #         print("[TEXT MOVE DEBUG] Початковий текст DXF перетягнуто")
# #         print("=" * 90)
# #         print(f"handle={handle}; type={tp}")
# #         print(f"old_insert={old_insert}")
# #         print(f"scene_pos=(x={pos.x():.3f}, y={pos.y():.3f})")
# #         print(f"new_dxf_insert=(x={new_x:.3f}, y={new_y:.3f}, z=0.000)")
# #         print("Файл DXF збережено.")
# #         print("=" * 90 + "\n")

# #     # ============================================================
# #     # ДЗЕРКАЛЬНІ СТОРОНИ X З ПІДТВЕРДЖЕННЯМ КОНСТРУКТОРА
# #     # ============================================================
# #     def bbox_signature_for_mirror(self, bbox, axis_x):
# #         """
# #         Нормалізований підпис bbox відносно центральної осі.
# #         Для дзеркальних лівої/правої сторін відстані від осі мають збігатися.
# #         """
# #         min_x, min_y, max_x, max_y = bbox
# #         dist_near = min(abs(min_x - axis_x), abs(max_x - axis_x))
# #         dist_far = max(abs(min_x - axis_x), abs(max_x - axis_x))
# #         return (round(dist_near, 1), round(dist_far, 1), round(min_y, 1), round(max_y, 1))

# #     def find_mirror_x_group_pairs(self, tolerance=2.0):
# #         """
# #         Шукає пари груп, які виглядають як дзеркальні ліва/права сторона.
# #         Порівнюємо bbox відносно центральної осі конструкції.
# #         """
# #         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
# #         if min_x is None:
# #             return None, []

# #         axis_x = (min_x + max_x) * 0.5
# #         valid = []
# #         for group in self.parametric_groups:
# #             bbox = self.group_original_bbox(group)
# #             if not bbox:
# #                 continue
# #             self.ensure_topology_fields(group)
# #             uid = self.get_group_key(group)
# #             cx = (bbox[0] + bbox[2]) * 0.5
# #             side = "left" if cx < axis_x - tolerance else ("right" if cx > axis_x + tolerance else "center")
# #             valid.append({"group": group, "uid": uid, "bbox": bbox, "cx": cx, "side": side})

# #         left = [x for x in valid if x["side"] == "left"]
# #         right = [x for x in valid if x["side"] == "right"]
# #         pairs = []
# #         used_right = set()

# #         for l in left:
# #             l_sig = self.bbox_signature_for_mirror(l["bbox"], axis_x)
# #             best = None
# #             best_score = None
# #             for r in right:
# #                 if r["uid"] in used_right:
# #                     continue
# #                 r_sig = self.bbox_signature_for_mirror(r["bbox"], axis_x)
# #                 score = sum(abs(a - b) for a, b in zip(l_sig, r_sig))
# #                 if best is None or score < best_score:
# #                     best = r
# #                     best_score = score
# #             if best is not None and best_score is not None and best_score <= tolerance * 4:
# #                 pairs.append((l, best, best_score))
# #                 used_right.add(best["uid"])

# #         return axis_x, pairs

# #     def proposed_mirror_growth_value(self, left_group, right_group):
# #         """
# #         Якщо на одній стороні вже заданий ріст, копіюємо його на другу.
# #         Якщо на обох різний — беремо середнє і показуємо це в діалозі.
# #         """
# #         gl = abs(float(left_group.get("growth_p_w", 0.0) or 0.0))
# #         gr = abs(float(right_group.get("growth_p_w", 0.0) or 0.0))
# #         if gl > 0 and gr == 0:
# #             return gl, "взято ріст лівої сторони"
# #         if gr > 0 and gl == 0:
# #             return gr, "взято ріст правої сторони"
# #         if gl > 0 and gr > 0 and abs(gl - gr) > 0.000001:
# #             return (gl + gr) * 0.5, "обидві сторони мали різний ріст, взято середнє"
# #         return max(gl, gr), "обидві сторони вже однакові або ріст 0%"

# #     def confirm_and_apply_mirror_x_rules(self):
# #         """
# #         Перевіряє, чи ліва і права сторони дзеркальні.
# #         Якщо так — показує конструктору список знайдених пар і тільки після підтвердження
# #         прописує однаковий growth_p_w для обох сторін.
# #         """
# #         axis_x, pairs = self.find_mirror_x_group_pairs(tolerance=2.0)
# #         rows = []
# #         rows.append("MIRROR X / Дзеркальні сторони X")
# #         rows.append("Сенс: якщо ліва і права сторони однакові дзеркально, їм треба дати однаковий % розтягування.")
# #         rows.append("Перед записом правил програма питає підтвердження конструктора.")
# #         rows.append("")
# #         rows.append(f"axis_x={axis_x if axis_x is not None else 'None'}")
# #         rows.append(f"found_pairs={len(pairs)}")

# #         if axis_x is None or not pairs:
# #             self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows + ["РЕЗУЛЬТАТ: дзеркальних пар не знайдено."])
# #             self.lbl_status_calc.setText("<font color='red'>Дзеркальних ліво/право груп не знайдено.</font>")
# #             return

# #         message_lines = [
# #             "Знайдено дзеркальні ліво/право пари.",
# #             "Прописати їм однаковий відсоток розтягування по X?",
# #             "",
# #         ]

# #         proposals = []
# #         for i, (l, r, score) in enumerate(pairs, start=1):
# #             gval, reason = self.proposed_mirror_growth_value(l["group"], r["group"])
# #             proposals.append((l, r, gval, reason, score))
# #             line = (
# #                 f"{i}) {l['group'].get('name')} ↔ {r['group'].get('name')}: "
# #                 f"growth_p_w = {gval*100:.2f}% ({reason})"
# #             )
# #             message_lines.append(line)
# #             rows.append(
# #                 f"pair#{i}: left={l['group'].get('name')} uid={l['uid']} bbox={tuple(round(v,3) for v in l['bbox'])}; "
# #                 f"right={r['group'].get('name')} uid={r['uid']} bbox={tuple(round(v,3) for v in r['bbox'])}; "
# #                 f"score={score:.3f}; proposed_growth={gval:.6f}; reason={reason}"
# #             )

# #         answer = QMessageBox.question(
# #             self,
# #             "Підтвердити дзеркальні правила X",
# #             "\n".join(message_lines),
# #             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
# #             QMessageBox.StandardButton.No,
# #         )

# #         if answer != QMessageBox.StandardButton.Yes:
# #             rows.append("КОНСТРУКТОР ВІДХИЛИВ: правила не записано.")
# #             self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows)
# #             self.lbl_status_calc.setText("<font color='#ffcc80'>Дзеркальні правила X не застосовано.</font>")
# #             return

# #         self.record_action_snapshot()
# #         rows.append("")
# #         rows.append("КОНСТРУКТОР ПІДТВЕРДИВ: записуємо однакове розтягування.")

# #         for l, r, gval, reason, score in proposals:
# #             lg = l["group"]
# #             rg = r["group"]
# #             old_l = float(lg.get("growth_p_w", 0.0) or 0.0)
# #             old_r = float(rg.get("growth_p_w", 0.0) or 0.0)

# #             lg["growth_p_w"] = round(float(gval), 6)
# #             rg["growth_p_w"] = round(float(gval), 6)
# #             lg["growth_dir_x"] = "Вліво"
# #             rg["growth_dir_x"] = "Вправо"
# #             lg["link_x"] = "X = W"
# #             rg["link_x"] = "X = W"
# #             lg["auto_mirror_x"] = True
# #             rg["auto_mirror_x"] = True
# #             lg["mirror_pair_uid"] = r["uid"]
# #             rg["mirror_pair_uid"] = l["uid"]

# #             rows.append(
# #                 f"APPLY: {lg.get('name')} old_growth={old_l:.6f} -> {gval:.6f}, dir=Вліво; "
# #                 f"{rg.get('name')} old_growth={old_r:.6f} -> {gval:.6f}, dir=Вправо"
# #             )

# #         self.save_project_config()
# #         self.load_groups_into_list()
# #         self.on_group_selection_changed()
# #         self.update_viewer()
# #         self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows)
# #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Дзеркальні правила X застосовано для пар: {len(proposals)}.</font>")

# #     def calculate_touch_extra_y_shifts(self, cur_w, cur_h, target_w, target_h):
# #         """
# #         Повертає додатковий Y-зсув для груп, щоб зберегти початковий вертикальний дотик/зазор.
# #         Формат: {uid: extra_shift_y}.
# #         """
# #         uid_to_group = {}
# #         uid_to_bbox = {}
# #         extra = {}

# #         for group in self.parametric_groups:
# #             if not self.group_original_bbox(group):
# #                 continue
# #             uid = self.get_group_key(group)
# #             uid_to_group[uid] = group
# #             bbox = self.simulated_group_bbox(group, cur_w, cur_h, target_w, target_h)
# #             if bbox:
# #                 uid_to_bbox[uid] = list(bbox)
# #                 extra[uid] = 0.0

# #         if len(uid_to_bbox) < 2:
# #             if self.debug_output:
# #                 print("[TOUCH DEBUG] Not enough groups for touch correction")
# #             return extra

# #         if self.debug_output:
# #             print("\n" + "=" * 90)
# #             print("[TOUCH DEBUG] START TOUCH Y CORRECTION")
# #             for _uid, _bbox in uid_to_bbox.items():
# #                 _g = uid_to_group[_uid]
# #                 print(f"[TOUCH DEBUG] before uid={_uid}; name={_g.get('name')}; bbox={tuple(round(v,3) for v in _bbox)}; enabled={_g.get('touch_y_enabled')}; to={_g.get('touch_to_uid')}; gap={_g.get('touch_gap_y')}")

# #         # Проходимо знизу вгору, щоб верхні деталі піднімались/опускались разом з тими, до кого вони прив'язані.
# #         sorted_groups = sorted(uid_to_group.values(), key=self.group_center_y)
# #         for _ in range(max(1, len(sorted_groups))):
# #             changed = False
# #             for lower in sorted_groups:
# #                 if not lower.get("touch_y_enabled"):
# #                     continue
# #                 lower_uid = self.get_group_key(lower)
# #                 upper_uid = lower.get("touch_to_uid")
# #                 if lower_uid not in uid_to_bbox or upper_uid not in uid_to_bbox:
# #                     continue

# #                 lower_bbox = uid_to_bbox[lower_uid]
# #                 upper_bbox = uid_to_bbox[upper_uid]
# #                 wanted_gap = float(lower.get("touch_gap_y", 0.0) or 0.0)
# #                 wanted_upper_min_y = lower_bbox[3] + wanted_gap
# #                 correction = wanted_upper_min_y - upper_bbox[1]

# #                 if abs(correction) > 0.001:
# #                     if self.debug_output:
# #                         print(
# #                             f"[TOUCH DEBUG] lower={lower_uid} -> upper={upper_uid}; "
# #                             f"wanted_gap={wanted_gap:.3f}; lower_top={lower_bbox[3]:.3f}; "
# #                             f"upper_min_before={upper_bbox[1]:.3f}; correction={correction:.3f}"
# #                         )
# #                     uid_to_bbox[upper_uid][1] += correction
# #                     uid_to_bbox[upper_uid][3] += correction
# #                     extra[upper_uid] = extra.get(upper_uid, 0.0) + correction
# #                     changed = True
# #             if not changed:
# #                 break

# #         if self.debug_output:
# #             print(f"[TOUCH DEBUG] extra result={extra}")
# #             print("=" * 90 + "\n")
# #         return extra

# #     def process_parametric_percentage_scale(self, save_result=True, record_history=True):
# #         try:
# #             cur_w = float(self.input_current_width.text().strip())
# #             target_w = float(self.input_target_width.text().strip())
# #             cur_h = float(self.input_current_height.text().strip())
# #             target_h = float(self.input_target_height.text().strip())
# #         except ValueError:
# #             return False

# #         self.collect_text_settings_from_inputs()
# #         if not self.validate_target_size_or_warn(cur_w, cur_h, target_w, target_h):
# #             return False

# #         should_record = save_result and record_history and not self.is_loading_history
# #         if should_record:
# #             before_snapshot = self.capture_full_state_snapshot()
# #             self.history.save_state()
# #             self.history.clear_redo()
# #             self.save_zones_history_state()
# #             self.zones_redo_stack.clear()
# #             self.global_recalc_undo_stack.append(before_snapshot)
# #             self.global_recalc_redo_stack.clear()
# #             if len(self.global_recalc_undo_stack) > 30:
# #                 self.global_recalc_undo_stack.pop(0)

# #         delta_w = target_w - cur_w
# #         delta_h = target_h - cur_h
# #         if self.debug_output:
# #             print("\n" + "=" * 90)
# #             print("[RECALC DEBUG] START GLOBAL PARAMETRIC RECALC")
# #             print(f"[RECALC DEBUG] cur_w={cur_w}, target_w={target_w}, delta_w={delta_w}")
# #             print(f"[RECALC DEBUG] cur_h={cur_h}, target_h={target_h}, delta_h={delta_h}")
# #             print("[RECALC DEBUG] Groups:")
# #             for _g in self.parametric_groups:
# #                 _uid = self.get_group_key(_g)
# #                 print(
# #                     f"  uid={_uid}; name={_g.get('name')}; "
# #                     f"k_w={_g.get('k_w')}; growth_p_w={_g.get('growth_p_w')}; dir_x={_g.get('growth_dir_x')}; link_x={_g.get('link_x')}; "
# #                     f"k_h={_g.get('k_h')}; growth_p_h={_g.get('growth_p_h')}; dir_y={_g.get('growth_dir_y')}; link_y={_g.get('link_y')}; "
# #                     f"auto_chain_y={_g.get('auto_chain_y')}; chain_shift_y={_g.get('chain_shift_y')}; chain_growth_after_y={_g.get('chain_growth_after_y')}"
# #                 )
# #         touch_extra_y = self.calculate_touch_extra_y_shifts(cur_w, cur_h, target_w, target_h)
# #         if self.debug_output:
# #             print(f"[RECALC DEBUG] touch_extra_y={touch_extra_y}")
# #         self.project_meta["source_width"] = cur_w
# #         self.project_meta["source_height"] = cur_h
# #         self.project_meta["target_width"] = target_w
# #         self.project_meta["target_height"] = target_h

# #         for hndl, orig in self.original_geometries.items():
# #             if hndl not in self.doc.entitydb: continue
# #             entity = self.doc.entitydb[hndl]

# #             associated_group = None
# #             for group in self.parametric_groups:
# #                 if hndl in group["handles"]:
# #                     associated_group = group
# #                     break

# #             if associated_group is None:
# #                 if orig["type"] == "LINE":
# #                     entity.dxf.start = orig["start"]
# #                     entity.dxf.end = orig["end"]
# #                 elif orig["type"] in ("CIRCLE", "ARC"):
# #                     entity.dxf.center = orig["center"]
# #                     entity.dxf.radius = orig["radius"]
# #                 elif orig["type"] == "TEXT":
# #                     entity.dxf.insert = orig["insert"]
# #                     entity.dxf.height = orig["height"]
# #                     entity.dxf.width = orig["width"]
# #                     entity.dxf.rotation = orig["rotation"]
# #                 continue

# #             shift_v, growth_v = ParametricEngine.get_transform(delta_w, delta_h, associated_group)
# #             if self.debug_output:
# #                 print(
# #                     f"[RECALC DEBUG] handle={hndl}; type={orig.get('type')}; "
# #                     f"group={associated_group.get('name')} uid={self.get_group_key(associated_group)}; "
# #                     f"base_shift=(x={shift_v[0]:.3f}, y={shift_v[1]:.3f}); "
# #                     f"growth=(x={growth_v[0]:.3f}, y={growth_v[1]:.3f}); "
# #                     f"k_w={associated_group.get('k_w')}; k_h={associated_group.get('k_h')}; "
# #                     f"shift_dir_x={associated_group.get('shift_dir_x')}; shift_dir_y={associated_group.get('shift_dir_y')}; "
# #                     f"growth_p_w={associated_group.get('growth_p_w')}; growth_p_h={associated_group.get('growth_p_h')}"
# #                 )
           
# #             group_uid = self.get_group_key(associated_group)
# #             extra_y = touch_extra_y.get(group_uid, 0.0)
# #             if abs(extra_y) > 0.0001:
# #                 if self.debug_output:
# #                     print(f"[RECALC DEBUG]   touch correction extra_y={extra_y:.3f} applied to group uid={group_uid}")
# #                 shift_v = (shift_v[0], shift_v[1] + extra_y, shift_v[2])
            
# #             growth_dir_x = associated_group.get("growth_dir_x", "Центр")
# #             growth_dir_y = associated_group.get("growth_dir_y", "Центр")

# #             if orig["type"] == "LINE":
# #                 sx, sy, sz = orig["start"]
# #                 ex, ey, ez = orig["end"]

# #                 dsx, dsy = shift_v[0], shift_v[1]
# #                 dex, dey = shift_v[0], shift_v[1]

# #                 # --- ЛОГІКА ПО X (ШИРИНА) ---
# #                 if sx < ex: left_p, right_p = "S", "E"
# #                 elif sx > ex: left_p, right_p = "E", "S"
# #                 else: left_p, right_p = "BOTH", "BOTH"

# #                 if growth_dir_x == "Вправо":
# #                     if right_p in ("S", "BOTH"): dsx += growth_v[0]
# #                     if right_p in ("E", "BOTH"): dex += growth_v[0]
# #                 elif growth_dir_x == "Вліво":
# #                     if left_p in ("S", "BOTH"): dsx -= growth_v[0]
# #                     if left_p in ("E", "BOTH"): dex -= growth_v[0]
# #                 else: # Центр
# #                     if left_p == "S": dsx -= growth_v[0] * 0.5
# #                     if right_p == "S": dsx += growth_v[0] * 0.5
# #                     if left_p == "E": dex -= growth_v[0] * 0.5
# #                     if right_p == "E": dex += growth_v[0] * 0.5

# #                 # --- ЛОГІКА ПО Y (ВИСОТА) ---
# #                 if sy < ey: bottom_p, top_p = "S", "E"
# #                 elif sy > ey: bottom_p, top_p = "E", "S"
# #                 else: bottom_p, top_p = "BOTH", "BOTH"

# #                 if growth_dir_y == "Вгору":
# #                     if top_p in ("S", "BOTH"): dsy += growth_v[1]
# #                     if top_p in ("E", "BOTH"): dey += growth_v[1]
# #                 elif growth_dir_y == "Вниз":
# #                     if bottom_p in ("S", "BOTH"): dsy -= growth_v[1]
# #                     if bottom_p in ("E", "BOTH"): dey -= growth_v[1]
# #                 else: # Центр
# #                     if bottom_p == "S": dsy -= growth_v[1] * 0.5
# #                     if top_p == "S": dsy += growth_v[1] * 0.5
# #                     if bottom_p == "E": dey -= growth_v[1] * 0.5
# #                     if top_p == "E": dey += growth_v[1] * 0.5

# #                 entity.dxf.start = (sx + dsx, sy + dsy, sz)
# #                 entity.dxf.end = (ex + dex, ey + dey, ez)

# #             elif orig["type"] in ("CIRCLE", "ARC"):
# #                 cx, cy, cz = orig["center"]
# #                 r = orig["radius"]

# #                 entity.dxf.center = (cx + shift_v[0], cy + shift_v[1], cz)

# #                 new_r = r
# #                 if growth_v[0] != 0.0 or growth_v[1] != 0.0:
# #                     scale_factor = 1.0 + ((abs(growth_v[0]) + abs(growth_v[1])) / (cur_w + cur_h))
# #                     new_r = r * scale_factor

# #                 entity.dxf.radius = new_r

# #             elif orig["type"] == "TEXT":
# #                 x, y, z = orig["insert"]
# #                 new_x = x + shift_v[0]
# #                 new_y = y + shift_v[1]
# #                 new_height = max(float(orig["height"]) + growth_v[1], 0.1)
# #                 new_width = max(float(orig["width"]), 0.01)
# #                 if growth_v[0] != 0.0:
# #                     new_width = max(float(orig["width"]) + growth_v[0], 0.01)
# #                 entity.dxf.insert = (new_x, new_y, z)
# #                 entity.dxf.height = new_height
# #                 entity.dxf.width = new_width

# #                 settings = self.get_text_settings()
# #                 if settings.get("handle") == hndl:
# #                     settings["x"] = new_x
# #                     settings["y"] = new_y
# #                     settings["height"] = new_height
# #                     settings["width_factor"] = new_width
# #                     self.project_meta["door_text"] = settings

# #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔW={delta_w:+.1f} мм | ΔH={delta_h:+.1f} мм</font>")
# #         self.apply_door_text_to_doc()
# #         if save_result:
# #             self.doc.saveas(self.dxf_path)
# #         if not getattr(self, "suppress_project_config_save", False):
# #             self.save_project_config()
# #         if should_record:
# #             self.history.save_state()
# #             self.save_zones_history_state()
# #             self.global_recalc_redo_stack.clear()
# #             self.update_history_buttons_state()
# #         self.update_viewer()
# #         return True

# #     # def commit_current_geometry_as_parametric_base(self, reason="", update_source_dimensions=True, preserve_target_dimensions=True):
# #     #     """
# #     #     Робить поточну геометрію DXF новою базою для параметричного перерахунку.

# #     #     Навіщо:
# #     #     - preview/process_parametric_percentage_scale() не рахує від поточного DXF напряму;
# #     #     - він бере self.original_geometries як "початкову геометрію";
# #     #     - після ROT/MIRROR потрібно оновити self.original_geometries, інакше "Перегляд"
# #     #       застосує правила до геометрії ДО оберту.
# #     #     """
# #     #     old_source_w = self.project_meta.get("source_width")
# #     #     old_source_h = self.project_meta.get("source_height")
# #     #     old_target_w = self.project_meta.get("target_width")
# #     #     old_target_h = self.project_meta.get("target_height")

# #     #     self.save_original_geometries()

# #     #     if update_source_dimensions:
# #     #         new_w, new_h = self.get_dxf_bounds_dimensions()
# #     #         if new_w is not None and new_h is not None:
# #     #             self.project_meta["source_width"] = new_w
# #     #             self.project_meta["source_height"] = new_h

# #     #             # target_width/target_height не чіпаємо, якщо користувач уже задав новий розмір.
# #     #             # Але якщо target був порожній або дорівнював старому source, синхронізуємо з новою базою,
# #     #             # щоб після оберту поля не залишались у старій орієнтації.
# #     #             if not preserve_target_dimensions:
# #     #                 self.project_meta["target_width"] = new_w
# #     #                 self.project_meta["target_height"] = new_h
# #     #             else:
# #     #                 if old_target_w is None or (old_source_w is not None and abs(float(old_target_w) - float(old_source_w)) < 0.001):
# #     #                     self.project_meta["target_width"] = new_w
# #     #                 if old_target_h is None or (old_source_h is not None and abs(float(old_target_h) - float(old_source_h)) < 0.001):
# #     #                     self.project_meta["target_height"] = new_h

# #     #     print("\n" + "=" * 90)
# #     #     print("[BASE DEBUG] PARAMETRIC BASE UPDATED")
# #     #     print(f"[BASE DEBUG] reason={reason}")
# #     #     print(f"[BASE DEBUG] source before: W={old_source_w}, H={old_source_h}")
# #     #     print(f"[BASE DEBUG] source after : W={self.project_meta.get('source_width')}, H={self.project_meta.get('source_height')}")
# #     #     print(f"[BASE DEBUG] target after : W={self.project_meta.get('target_width')}, H={self.project_meta.get('target_height')}")
# #     #     print(f"[BASE DEBUG] original_geometries handles={len(self.original_geometries)}")
# #     #     print("=" * 90)

# #     #     self.update_dimension_inputs_from_meta()

# #     def commit_current_geometry_as_parametric_base(
# #         self,
# #         reason="",
# #         update_source_dimensions=False,
# #         preserve_target_dimensions=True
# #     ):
# #         """
# #         Робить поточну геометрію DXF новою базою для параметричного перерахунку,
# #         але НЕ міняє значення у полях ширини та висоти.
# #         """

# #         old_source_w = self.project_meta.get("source_width")
# #         old_source_h = self.project_meta.get("source_height")
# #         old_target_w = self.project_meta.get("target_width")
# #         old_target_h = self.project_meta.get("target_height")

# #         self.save_original_geometries()

# #         if self.debug_output:
# #             print("\n" + "=" * 90)
# #             print("[BASE DEBUG] PARAMETRIC BASE UPDATED")
# #             print(f"[BASE DEBUG] reason={reason}")
# #             print(f"[BASE DEBUG] source kept : W={old_source_w}, H={old_source_h}")
# #             print(f"[BASE DEBUG] target kept : W={old_target_w}, H={old_target_h}")
# #             print(f"[BASE DEBUG] original_geometries handles={len(self.original_geometries)}")
# #             print("=" * 90)


# #     def save_original_geometries(self):
# #         self.original_geometries.clear()
# #         for entity in self.doc.modelspace():
# #             hndl = entity.dxf.handle
# #             tp = entity.dxftype()
# #             if tp == "CIRCLE":
# #                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
# #             elif tp == "LINE":
# #                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}
# #             elif tp == "ARC":
# #                 self.original_geometries[hndl] = {"type": "ARC", "center": entity.dxf.center, "radius": entity.dxf.radius, "start_angle": entity.dxf.start_angle, "end_angle": entity.dxf.end_angle}
# #             elif tp == "TEXT":
# #                 settings = self.get_text_settings()
# #                 if settings.get("handle") == hndl:
# #                     insert = (
# #                         float(settings.get("x", 0.0)),
# #                         float(settings.get("y", 0.0)),
# #                         0.0
# #                     )
# #                     height = self.text_box_height(settings)
# #                     width = self.text_box_width(settings)
# #                     text_value = settings.get("text", "")
# #                 else:
# #                     insert = entity.dxf.insert
# #                     height = float(entity.dxf.height)
# #                     width = float(getattr(entity.dxf, "width", 1.0))
# #                     text_value = entity.dxf.text
# #                 self.original_geometries[hndl] = {
# #                     "type": "TEXT",
# #                     "insert": insert,
# #                     "height": height,
# #                     "width": width,
# #                     "rotation": float(getattr(entity.dxf, "rotation", 0.0)),
# #                     "text": text_value
# #                 }

# #     def save_zones_history_state(self):
# #         state_snapshot = {
# #             "parametric_groups": copy.deepcopy(self.parametric_groups),
# #             "project_meta": copy.deepcopy(self.project_meta),
# #             "block_keep_state": copy.deepcopy(self.block_keep_state)
# #         }
# #         self.zones_undo_stack.append(state_snapshot)
# #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# #     def capture_full_state_snapshot(self):
# #         return {
# #             "doc": copy.deepcopy(self.doc),
# #             "parametric_groups": copy.deepcopy(self.parametric_groups),
# #             "project_meta": copy.deepcopy(self.project_meta),
# #             "block_keep_state": copy.deepcopy(self.block_keep_state)
# #         }

# #     def record_action_snapshot(self):
# #         if self.is_loading_history:
# #             return
# #         self.global_recalc_undo_stack.append(self.capture_full_state_snapshot())
# #         if len(self.global_recalc_undo_stack) > 50:
# #             self.global_recalc_undo_stack.pop(0)
# #         self.global_recalc_redo_stack.clear()
# #         self.update_history_buttons_state()

# #     def restore_full_state_snapshot(self, snapshot):
# #         self.doc = copy.deepcopy(snapshot["doc"])
# #         self.parametric_groups = copy.deepcopy(snapshot["parametric_groups"])
# #         self.project_meta = copy.deepcopy(snapshot["project_meta"])
# #         self.block_keep_state = copy.deepcopy(snapshot["block_keep_state"])
# #         self.doc.saveas(self.dxf_path)
# #         self.save_project_config()
# #         self.save_original_geometries()
# #         self.update_dimension_inputs_from_meta()
# #         self.load_groups_into_list()
# #         self.load_entities_into_list()
# #         self.update_viewer()
# #         self.update_history_buttons_state()

# #     def push_to_history(self):
# #         self.history.save_state()
# #         self.history.clear_redo()
# #         self.save_zones_history_state()
# #         self.zones_redo_stack.clear()
# #         self.update_history_buttons_state()

# #     def undo(self):
# #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# #             current_snapshot = self.zones_undo_stack.pop()
# #             self.zones_redo_stack.append(current_snapshot)
# #             previous_snapshot = self.zones_undo_stack[-1]
            
# #             restored_groups = copy.deepcopy(previous_snapshot["parametric_groups"])
            
# #             for rest_g in restored_groups:
# #                 for cur_g in self.parametric_groups:
# #                     if rest_g["name"] == cur_g["name"]:
# #                         rest_g["k_w"] = cur_g.get("k_w", 0.0)
# #                         rest_g["k_h"] = cur_g.get("k_h", 0.0)
# #                         rest_g["growth_p_w"] = cur_g.get("growth_p_w", 0.0)
# #                         rest_g["growth_p_h"] = cur_g.get("growth_p_h", 0.0)
# #                         rest_g["growth_dir_x"] = cur_g.get("growth_dir_x", "Центр")
# #                         rest_g["growth_dir_y"] = cur_g.get("growth_dir_y", "Центр")
# #                         rest_g["shift_dir_x"] = cur_g.get("shift_dir_x", "Вправо")
# #                         rest_g["shift_dir_y"] = cur_g.get("shift_dir_y", "Вгору")
# #                         rest_g["link_x"] = cur_g.get("link_x", "X = W")
# #                         rest_g["link_y"] = cur_g.get("link_y", "Y = H")
# #                         break

# #             self.parametric_groups = restored_groups
# #             self.save_project_config()
# #             self.reload_after_history_change()

# #     def redo(self):
# #         if self.history.redo() and self.zones_redo_stack:
# #             next_snapshot = self.zones_redo_stack.pop()
# #             self.zones_undo_stack.append(next_snapshot)
            
# #             restored_groups = copy.deepcopy(next_snapshot["parametric_groups"])
            
# #             for rest_g in restored_groups:
# #                 for cur_g in self.parametric_groups:
# #                     if rest_g["name"] == cur_g["name"]:
# #                         rest_g["k_w"] = cur_g.get("k_w", 0.0)
# #                         rest_g["k_h"] = cur_g.get("k_h", 0.0)
# #                         rest_g["growth_p_w"] = cur_g.get("growth_p_w", 0.0)
# #                         rest_g["growth_p_h"] = cur_g.get("growth_p_h", 0.0)
# #                         rest_g["growth_dir_x"] = cur_g.get("growth_dir_x", "Центр")
# #                         rest_g["growth_dir_y"] = cur_g.get("growth_dir_y", "Центр")
# #                         rest_g["shift_dir_x"] = cur_g.get("shift_dir_x", "Вправо")
# #                         rest_g["shift_dir_y"] = cur_g.get("shift_dir_y", "Вгору")
# #                         rest_g["link_x"] = cur_g.get("link_x", "X = W")
# #                         rest_g["link_y"] = cur_g.get("link_y", "Y = H")
# #                         break

# #             self.parametric_groups = restored_groups
# #             self.save_project_config()
# #             self.reload_after_history_change()

# #     def restore_state_snapshot(self, snapshot):
# #         self.parametric_groups = copy.deepcopy(snapshot["parametric_groups"])
# #         self.project_meta = copy.deepcopy(snapshot.get("project_meta", self.project_meta))
# #         self.block_keep_state = copy.deepcopy(snapshot.get("block_keep_state", self.block_keep_state))
# #         self.save_project_config()
# #         self.reload_after_history_change()

# #     def undo(self):
# #         if self.global_recalc_undo_stack:
# #             self.global_recalc_redo_stack.append(self.capture_full_state_snapshot())
# #             snapshot = self.global_recalc_undo_stack.pop()
# #             self.restore_full_state_snapshot(snapshot)
# #             return
# #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# #             current_snapshot = self.zones_undo_stack.pop()
# #             self.zones_redo_stack.append(current_snapshot)
# #             self.restore_state_snapshot(self.zones_undo_stack[-1])

# #     def redo(self):
# #         if self.global_recalc_redo_stack:
# #             self.global_recalc_undo_stack.append(self.capture_full_state_snapshot())
# #             snapshot = self.global_recalc_redo_stack.pop()
# #             self.restore_full_state_snapshot(snapshot)
# #             return
# #         if self.history.redo() and self.zones_redo_stack:
# #             next_snapshot = self.zones_redo_stack.pop()
# #             self.zones_undo_stack.append(next_snapshot)
# #             self.restore_state_snapshot(next_snapshot)

# #     def set_interface_theme(self, theme_name):
# #         is_dark = theme_name == "Темна"
# #         if is_dark:
# #             self.setStyleSheet("""
# #                 QMainWindow { background-color: #1e1e1e; }
# #                 QWidget { color: #d4d4d4; font-size: 12px; }
                               
# #                 QTabWidget::pane {
# #                     border: 1px solid #3c3c3c;
# #                     background: #1e1e1e;
# #                     top: -1px; /* Прибирає подвійну рамку на стику */
# #                 }
    
# #                 /* Базовий стиль для всіх вкладок на панелі */
# #                 QTabBar::tab {
# #                     background: #3c3c3c;
# #                     color: #fff;
# #                     padding: 8px 16px;
# #                     font-size: 13px;
# #                     font-weight: 500;
# #                     border: 1px solid #3c3c3c;
# #                     border-bottom: none;
# #                     border-top-left-radius: 4px;
# #                     border-top-right-radius: 4px;
# #                     min-width: 40px;
# #                 }

# #                 /* Стиль вкладки, коли на неї наводять мишкою */
# #                 QTabBar::tab:hover {
# #                     background: #2c3e50;
                    
# #                 }

# #                 /* Стиль строго для АКТИВНОЇ (обраної) вкладки */
# #                QTabBar::tab:selected {
# #                     background: #2c3e50;
# #                     color: #ffffff ;
# #                     font-weight: bold;
# #                     border-bottom: 2px solid #2ecc71; 
# #                 }
# #                 QScrollArea { border: none; background-color: #252526; }
# #                 QGroupBox {
# #                     font-weight: bold; color: #4fc3f7; border: 1px solid #3c3c3c;
# #                     border-radius: 6px; margin-top: 15px; padding-top: 10px;
# #                 }
# #                 QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
# #                 QPushButton {
# #                     background-color: #333333; border: 1px solid #454545; color: #ffffff;
# #                     padding: 6px; border-radius: 4px;
# #                 }
# #                 QPushButton:hover { background-color: #454545; border-color: #007acc; }
# #                 QPushButton:disabled { color: #777777; background-color: #252525; }
# #                 QLineEdit, QComboBox {
# #                     background-color: #1e1e1e; border: 1px solid #3c3c3c;
# #                     color: #ffffff; padding: 4px; border-radius: 3px;
# #                 }
# #                 QListWidget {
# #                     background-color: #1e1e1e; color: #d4d4d4;
# #                     border: 1px solid #3c3c3c; border-radius: 4px;
# #                 }
# #                 QListWidget::item:selected { background-color: #0e639c; color: #ffffff; }
# #                 QCheckBox { spacing: 6px; }
# #                 QScrollBar:vertical { background: #252526; width: 12px; }
# #                 QScrollBar::handle:vertical { background: #555555; border-radius: 5px; min-height: 24px; }
                               
# #                  QGroupBox {
# #                 font-size: 14px;
# #                 font-weight: bold;
# #                 color: #2d3748;
# #                 margin-top: 12px; /* Відступ зверху для заголовка */
# #                 border: 1px solid #cbd5e0;
# #                 border-radius: 6px;
# #                 padding-top: 16px; /* Внутрішній відступ від заголовка до елементів */
# #             }

# #             /* Зсув заголовка з чекбоксом трохи вище та лівіше */
# #             QGroupBox::title {
# #                 subcontrol-origin: margin;
# #                 subcontrol-position: top left;
# #                 left: 10px;
# #                 padding: 0 5px;
# #             }

# #             /* БАЗОВИЙ СТИЛЬ ЧЕКБОКСА всередині GroupBox */
# #             QGroupBox::indicator {
# #                 width: 18px;
# #                 height: 18px;
# #                 border: 2px solid #cbd5e0;
# #                 border-radius: 4px;
# #                 background-color: #ffffff;
# #             }

# #             /* Стан при наведенні курсору */
# #             QGroupBox::indicator:hover {
# #                 border-color: #3182ce;
# #                 background-color: #f7fafc;
# #             }

# #             /* Стан, коли галочка ВСТАНОВЛЕНА (панель відкрита) */
# #             QGroupBox::indicator:checked {
# #                 border-color: #3182ce;
# #                 background-color: #3182ce;
# #                 /* Вбудована SVG-галочка білого кольору */
# #                 image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
# #             }

# #             /* Стан, коли галочка ЗНЯТА (панель згорнута) */
# #             QGroupBox::indicator:unchecked {
# #                 border-color: #cbd5e0;
# #                 background-color: #ffffff;
# #             }
# #             """)
# #         else:
# #             self.setStyleSheet("""
# #                 QMainWindow { background-color: #eef2f7; color: #fff}
# #                 QWidget { background-color: #ffffff; color: #1f2933; font-size: 12px; }
                               
# #                                QTabWidget::pane {
# #                     border: 1px solid #e0e0e0;
# #                     background: #ffffff;
# #                     top: -1px; /* Прибирає подвійну рамку на стику */
# #                 }
    
# #                 /* Базовий стиль для всіх вкладок на панелі */
# #                 QTabBar::tab {
# #                     background: #f8f9fa;
# #                     color: #2c3e50;
# #                      padding: 8px 16px;
# #                     font-size: 13px;
# #                     font-weight: 500;
# #                     border: 1px solid #e0e0e0;
# #                     border-bottom: none;
# #                     border-top-left-radius: 4px;
# #                     border-top-right-radius: 4px;
# #                     min-width: 80px;
# #                 }

# #                 /* Стиль вкладки, коли на неї наводять мишкою */
# #                 QTabBar::tab:hover {
# #                     background: #eef2f7;
# #                     color: #2ecc71; /* Зелений колір тексту при наведенні */
# #                 }

# #                 /* Стиль строго для АКТИВНОЇ (обраної) вкладки */
# #                 QTabBar::tab:selected {
# #                     background: #ffffff;
# #                     color: #2c3e50  ;
# #                     font-weight: bold;
# #                     border-bottom: 2px solid #2ecc71; 
# #                 }
# #                 QScrollArea { border: none; background-color: #f7f9fc; }
# #                 QGroupBox {
# #                     background-color: #ffffff; font-weight: bold; color: #0b5cad;
# #                     border: 1px solid #cfd7e3; border-radius: 6px;
# #                     margin-top: 15px; padding-top: 10px;
# #                 }
# #                 QGroupBox::title {
# #                     subcontrol-origin: margin; left: 10px; padding: 0 4px;
# #                     background-color: #ffffff;
# #                 }
# #                 QPushButton {
# #                     background-color: #ffffff; border: 1px solid #b8c4d4; color: #1f2933;
# #                     padding: 6px; border-radius: 4px;
# #                 }
# #                 QPushButton:hover { background-color: #edf5ff; border-color: #0b5cad; }
# #                 QPushButton:pressed { background-color: #dbeafe; }
# #                 QPushButton:disabled { color: #9aa6b2; background-color: #edf0f4; }
# #                 QLineEdit, QComboBox {
# #                     background-color: #ffffff; border: 1px solid #b8c4d4;
# #                     color: #111827; padding: 4px; border-radius: 3px;
# #                     selection-background-color: #bfdbfe;
# #                 }
# #                 QListWidget {
# #                     background-color: #ffffff; color: #1f2933;
# #                     border: 1px solid #cfd7e3; border-radius: 4px;
# #                     alternate-background-color: #f6f8fb;
# #                 }
# #                 QListWidget::item:selected { background-color: #dbeafe; color: #111827; }
# #                 QCheckBox {  spacing: 6px; }
# #                 QCheckBox::indicator:unchecked {
# #                     background-color: #ffffff;
# #                     border: 1px solid #1e1e1e;
# #                 }
 
# #                 QCheckBox::indicator:checked { background-color: #0b5cad; border: 1px solid #0b5cad; }
# #                 QScrollBar:vertical { background: #f1f5f9; width: 12px; }
# #                 QScrollBar::handle:vertical { background: #b8c4d4; border-radius: 5px; min-height: 24px; }
                               
# #                  QGroupBox {
# #                 font-size: 14px;
# #                 font-weight: bold;
# #                 color: #2d3748;
# #                 margin-top: 12px; /* Відступ зверху для заголовка */
# #                 border: 1px solid #cbd5e0;
# #                 border-radius: 6px;
# #                 padding-top: 16px; /* Внутрішній відступ від заголовка до елементів */
# #             }

# #             /* Зсув заголовка з чекбоксом трохи вище та лівіше */
# #             QGroupBox::title {
# #                 subcontrol-origin: margin;
# #                 subcontrol-position: top left;
# #                 left: 10px;
# #                 padding: 0 5px;
# #             }

# #             /* БАЗОВИЙ СТИЛЬ ЧЕКБОКСА всередині GroupBox */
# #             QGroupBox::indicator {
# #                 width: 18px;
# #                 height: 18px;
# #                 border: 2px solid #cbd5e0;
# #                 border-radius: 4px;
# #                 background-color: #ffffff;
# #             }

# #             /* Стан при наведенні курсору */
# #             QGroupBox::indicator:hover {
# #                 border-color: #3182ce;
# #                 background-color: #f7fafc;
# #             }

# #             /* Стан, коли галочка ВСТАНОВЛЕНА (панель відкрита) */
# #             QGroupBox::indicator:checked {
# #                 border-color: #3182ce;
# #                 background-color: #3182ce;
# #                 /* Вбудована SVG-галочка білого кольору */
# #                 image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
# #             }

# #             /* Стан, коли галочка ЗНЯТА (панель згорнута) */
# #             QGroupBox::indicator:unchecked {
# #                 border-color: #cbd5e0;
# #                 background-color: #ffffff;
# #             }
# #             """)
# #         self.apply_theme_widget_overrides(is_dark)

# #     def apply_theme_widget_overrides(self, is_dark):
# #         styles = {
# #             "btn_open_file": (
# #                 "background-color: #37474f; color: white; font-weight: bold; padding: 4px;",
# #                 "background-color: #e8f1fb; color: #123f68; border: 1px solid #9cb7d5; font-weight: bold; padding: 4px;"
# #             ),
# #             "chk_enable_inspector": (
# #                 "color: #ff9800; font-weight: bold;",
# #                 "color: #9a5b00; font-weight: bold;"
# #             ),
# #             "btn_snap_zero": (
# #                 "background-color: #00897b; color: white; font-weight: bold; padding: 6px;",
# #                 "background-color: #e0f2f1; color: #005f56; border: 1px solid #7bbdb5; font-weight: bold; padding: 6px;"
# #             ),
# #             "transform_group": (
# #                 "QGroupBox { border: 1px solid #d32f2f; }",
# #                 "QGroupBox { background-color: #fff7f7; border: 1px solid #e2a8a8; color: #8a1f1f; }"
# #             ),
# #             "lbl_status_calc": (
# #                 "color: #4fc3f7; font-size: 11px;",
# #                 "color: #0b5cad; font-size: 11px;"
# #             ),
# #             "btn_apply_auto_scale": (
# #                 "background-color: #007acc; color: white; font-weight: bold; padding: 6px;",
# #                 "background-color: #0b5cad; color: white; border: 1px solid #084b8d; font-weight: bold; padding: 6px;"
# #             ),
# #             "btn_export_new_dxf": (
# #                 "background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;",
# #                 "background-color: #2e7d32; color: white; border: 1px solid #1f5d23; font-weight: bold; padding: 6px;"
# #             ),
# #             "btn_create_group": (
# #                 "background-color: #673ab7; color: white; font-weight: bold;",
# #                 "background-color: #ede7f6; color: #4527a0; border: 1px solid #b39ddb; font-weight: bold;"
# #             ),
# #             "btn_delete_from_dxf": (
# #                 "background-color: #d32f2f; color: white; font-weight: bold;",
# #                 "background-color: #fde8e8; color: #9b1c1c; border: 1px solid #f3aaaa; font-weight: bold;"
# #             ),
# #         }
# #         for attr_name, (dark_style, light_style) in styles.items():
# #             widget = getattr(self, attr_name, None)
# #             if widget is not None:
# #                 widget.setStyleSheet(dark_style if is_dark else light_style)

# #     def on_scene_item_clicked(self, handle):
# #         modifiers = QGuiApplication.keyboardModifiers()
# #         if (modifiers & Qt.ControlModifier):
# #             if handle in self.selected_handles: self.selected_handles.remove(handle)
# #             else: self.selected_handles.add(handle)
# #             self.sync_list_from_handles()
# #             self.update_viewer()
# #             return

# #         group_idx = self.group_index_for_handle(handle)
# #         if group_idx is not None:
# #             self.select_group_by_index(group_idx)
# #             return

# #         self.group_list_widget.clearSelection()
# #         self.selected_handles = {handle}
# #         self.sync_list_from_handles()
# #         self.update_viewer()

# #     def group_index_for_handle(self, handle):
# #         handle = str(handle)
# #         for idx, group in enumerate(self.parametric_groups):
# #             if handle in {str(h) for h in group.get("handles", set())}:
# #                 return idx
# #         return None

# #     def select_group_by_index(self, idx):
# #         if idx < 0 or idx >= self.group_list_widget.count():
# #             return
# #         self.group_list_widget.setCurrentRow(idx)
# #         group = self.parametric_groups[idx]
# #         self.selected_handles = set(group.get("handles", set()))
# #         self.sync_list_from_handles()
# #         self.update_viewer()

# #     def update_history_buttons_state(self):
# #         can_undo_history = len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1
# #         can_redo_history = len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0
# #         self.btn_undo.setEnabled(bool(self.global_recalc_undo_stack) or can_undo_history)
# #         self.btn_redo.setEnabled(bool(self.global_recalc_redo_stack) or can_redo_history)

# #     def reload_after_history_change(self):
# #         self.is_loading_history = True
# #         self.doc = ezdxf.readfile(self.dxf_path)
# #         self.save_original_geometries()
# #         self.update_dimension_inputs_from_meta()
# #         self.load_groups_into_list()
# #         self.load_entities_into_list()
# #         self.update_history_buttons_state()
# #         self.is_loading_history = False

# #     def scan_project_folder_for_dxf(self):
# #         self.file_explorer_list.blockSignals(True)
# #         self.file_explorer_list.clear()
# #         try:
# #             files = os.listdir(self.project_dir)
# #             dxf_files = [f for f in files if f.lower().endswith('.dxf')]
# #             for file_name in dxf_files:
# #                 item = QListWidgetItem(f"📄 {file_name}")
# #                 item.setData(Qt.ItemDataRole.UserRole, file_name)
# #                 self.file_explorer_list.addItem(item)
# #                 if file_name.lower() == os.path.basename(self.dxf_path).lower():
# #                     self.file_explorer_list.setCurrentItem(item)
# #         except Exception as e:
# #             print(f"Помилка провідника: {e}")
# #         self.file_explorer_list.blockSignals(False)

# #     def on_dxf_selection_changed_in_explorer(self):
# #         selected_items = self.file_explorer_list.selectedItems()
# #         if not selected_items: return
# #         self.selected_handles.clear()
# #         self.parametric_groups.clear()
# #         base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
# #         self.current_project_file_id = None
# #         self.dxf_path = os.path.join(self.project_dir, base_file_name)
# #         self.doc = ezdxf.readfile(self.dxf_path)

# #         if len(selected_items) > 1:
# #             for item in selected_items[1:]:
# #                 addon_file_name = item.data(Qt.ItemDataRole.UserRole)
# #                 addon_path = os.path.join(self.project_dir, addon_file_name)
# #                 if os.path.exists(addon_path):
# #                     try:
# #                         addon_doc = ezdxf.readfile(addon_path)
# #                         importer = Importer(addon_doc, self.doc)
# #                         importer.import_modelspace()
# #                         importer.finalize()
# #                     except Exception as e: print(f"Помилка злиття: {e}")

# #         self.load_folder_config()
# #         self.load_project_config()
# #         self.prompt_source_dimensions_on_open()
# #         self.register_current_folder_model(show_errors=False)
# #         self.update_dimension_inputs_from_meta()
# #         self.history = HistoryManager(self.dxf_path)
# #         self.history.save_state()
# #         self.zones_undo_stack.clear()
# #         self.zones_redo_stack.clear()
# #         self.global_recalc_undo_stack.clear()
# #         self.global_recalc_redo_stack.clear()
# #         self.save_zones_history_state()
# #         self.save_original_geometries()
# #         self.update_viewer()
# #         self.load_entities_into_list()
# #         self.load_groups_into_list()
# #         self.load_block_filter_list()
# #         self.update_history_buttons_state()

# #     def process_manual_rubber_band(self, rect):
# #         modifiers = QGuiApplication.keyboardModifiers()
# #         if not (modifiers & Qt.ControlModifier):
# #             self.selected_handles.clear()
# #         path = QPainterPath()
# #         path.addRect(rect)
# #         for item in self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape):
# #             hndl = item.data(Qt.ItemDataRole.UserRole)
# #             if hndl: self.selected_handles.add(hndl)
# #         self.sync_list_from_handles()
# #         self.update_viewer()

# #     def sync_list_from_handles(self):
# #         self.entity_list.blockSignals(True)
# #         self.entity_list.clearSelection()
# #         for i in range(self.entity_list.count()):
# #             item = self.entity_list.item(i)
# #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# #         self.entity_list.blockSignals(False)

# #     def on_list_selection_changed(self):
# #         self.selected_handles.clear()
# #         for item in self.entity_list.selectedItems():
# #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# #         self.update_viewer()

# #     def clear_selection(self):
# #         self.selected_handles.clear()
# #         self.update_viewer()
# #         self.entity_list.blockSignals(True)
# #         self.entity_list.clearSelection()
# #         self.entity_list.blockSignals(False)

# #     def on_theme_changed(self, theme_name):
# #         self.current_theme = theme_name
# #         self.set_interface_theme(theme_name)
# #         self.update_viewer()

# #     def load_entities_into_list(self):
# #         self.entity_list.blockSignals(True)
# #         self.entity_list.clear()
# #         seen = set()
# #         for entity in self.doc.modelspace():
# #             tp = entity.dxftype()
# #             hndl = entity.dxf.handle
# #             if tp == "CIRCLE":
# #                 cx, cy, _ = entity.dxf.center
# #                 if (round(cx, 1), round(cy, 1)) in seen: continue
# #                 seen.add((round(cx, 1), round(cy, 1)))
# #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# #             elif tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 if (round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)) in seen: continue
# #                 seen.add((round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)))
# #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм. Початок: ({x1:.1f}, {y1:.1f}), Кінець: ({x2:.1f}, {y2:.1f})"
# #             elif tp == "ARC":
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 sa = float(entity.dxf.start_angle)
# #                 ea = float(entity.dxf.end_angle)

# #                 arc_key = (
# #                     round(cx, 2),
# #                     round(cy, 2),
# #                     round(r, 2),
# #                     round(sa, 2),
# #                     round(ea, 2),
# #                 )

# #                 if arc_key in seen:
# #                     continue

# #                 seen.add(arc_key)

# #                 text = (
# #                     f"🌙 Дуга (ID: {hndl}) "
# #                     f"Центр X:{cx:.1f}, Y:{cy:.1f}, "
# #                     f"R:{r:.1f}, Кути: {sa:.1f}° → {ea:.1f}°"
# #                 )
# #             # elif tp == "ARC":
# #             #     cx, cy, _ = entity.dxf.center
# #             #     r = entity.dxf.radius
# #             #     if (round(cx, 1), round(cy, 1), round(r, 1)) in seen: continue
# #             #     seen.add((round(cx, 1), round(cy, 1), round(r, 1)))
# #             #     text = f"🌙 Дуга (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}, R:{r:.1f}"
# #             elif tp == "TEXT":
# #                 x, y, _ = entity.dxf.insert
# #                 label = entity.dxf.text.strip() or "[рамка тексту]"
# #                 text = f"Текст (ID: {hndl}) \"{label}\" X:{x:.1f}, Y:{y:.1f}, H:{entity.dxf.height:.1f}"
# #             else: continue
# #             item = QListWidgetItem(text)
# #             item.setData(Qt.ItemDataRole.UserRole, str(hndl))
# #             self.entity_list.addItem(item)
# #         self.entity_list.blockSignals(False)

# #     def update_viewer(self):
# #         items_to_remove = [item for item in self.scene.items() if item != self.coord_tooltip_item and item != self.coord_snap_marker]
# #         for item in items_to_remove:
# #             self.scene.removeItem(item)
            
# #         self.overlay_items.clear()

# #         if self.current_theme == "Темна":
# #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# #             base_line_color = QColor(220, 220, 220)
# #         else:
# #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# #             base_line_color = QColor(80, 80, 80)

# #         self.scene.addLine(-150, 0, 150, 0, QPen(QColor(33, 150, 243), 2))
# #         self.scene.addLine(0, 150, 0, -150, QPen(QColor(76, 175, 80), 2))

# #         for idx, group in enumerate(self.parametric_groups):
# #             g_min_x, g_max_x, g_min_y, g_max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
# #             for hndl in group["handles"]:
# #                 if hndl not in self.doc.entitydb: continue
# #                 e = self.doc.entitydb[hndl]
# #                 if e.dxftype() in ("CIRCLE", "ARC"):
# #                     g_min_x = min(g_min_x, e.dxf.center[0] - e.dxf.radius)
# #                     g_max_x = max(g_max_x, e.dxf.center[0] + e.dxf.radius)
# #                     g_min_y = min(g_min_y, e.dxf.center[1] - e.dxf.radius)
# #                     g_max_y = max(g_max_y, e.dxf.center[1] + e.dxf.radius)
# #                 elif e.dxftype() == "LINE":
# #                     g_min_x = min(g_min_x, e.dxf.start[0], e.dxf.end[0])
# #                     g_max_x = max(g_max_x, e.dxf.start[0], e.dxf.end[0])
# #                     g_min_y = min(g_min_y, e.dxf.start[1], e.dxf.end[1])
# #                     g_max_y = max(g_max_y, e.dxf.start[1], e.dxf.end[1])

# #             if g_min_x != float('inf'):
# #                 rect_item = QGraphicsRectItem(g_min_x - 4, -(g_max_y + 4), (g_max_x - g_min_x) + 8, (g_max_y - g_min_y) + 8)
# #                 rect_item.setBrush(QBrush(QColor(103, 58, 183, 20)))
# #                 rect_item.setPen(QPen(QColor(103, 58, 183, 150), 1, Qt.PenStyle.DashLine))
# #                 self.scene.addItem(rect_item)

# #         seen_circles, seen_lines, seen_arcs = set(), set(), set()

# #         for entity in self.doc.modelspace():
# #             hndl = entity.dxf.handle
# #             tp = entity.dxftype()
# #             pyqt_item = None
            
# #             if tp == "CIRCLE":
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# #                 pyqt_item = SelectableCircle(
# #                     cx - r,
# #                     -cy - r,
# #                     r * 2,
# #                     r * 2,
# #                     entity
# #                 )
# #             elif tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# #                 pyqt_item = SelectableLine(
# #                     x1, -y1,
# #                     x2, -y2,
# #                     entity
# #                 )

# #             elif tp == "ARC":
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 sa = entity.dxf.start_angle
# #                 ea = entity.dxf.end_angle
# #                 if (round(cx, 2), round(cy, 2), round(sa, 2)) in seen_arcs: continue
# #                 seen_arcs.add((round(cx, 2), round(cy, 2), round(sa, 2)))
# #                 pyqt_item = SelectableArc(
# #                     QPointF(cx, -cy),
# #                     r,
# #                     sa,
# #                     ea,
# #                     entity
# #                 )

# #             elif tp in ("TEXT", "MTEXT"):
# #                 settings = self.get_text_settings()
# #                 entity_text = getattr(entity.dxf, "text", "") if tp == "TEXT" else getattr(entity, "text", "")
# #                 display_text = self.text_display_value(settings.get("text", entity_text))
# #                 if settings.get("handle") == hndl:
# #                     # Наш керований текстовий блок: лишається рамкою, яку можна рухати.
# #                     box_x = float(settings.get("x", 0.0))
# #                     box_y = float(settings.get("y", 0.0))
# #                     box_w = self.text_box_width(settings)
# #                     box_h = self.text_box_height(settings)
# #                     pyqt_item = DraggableDoorTextBoxItem(
# #                         0,
# #                         0,
# #                         box_w,
# #                         box_h,
# #                         self,
# #                         hndl
# #                     )
# #                     pyqt_item.setPos(box_x, -box_y - box_h)
# #                     pyqt_item.setBrush(QBrush(QColor(0, 120, 255, 55)))
# #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 1.5, Qt.PenStyle.DashLine))
# #                     pyqt_item.setTransformOriginPoint(box_w * 0.5, box_h * 0.5)
# #                     pyqt_item.setRotation(-float(settings.get("rotation", 0.0)))
# #                     self.scene.addItem(pyqt_item)
# #                     self.add_centered_text_preview(
# #                         pyqt_item,
# #                         display_text,
# #                         box_w,
# #                         box_h,
# #                         str(settings.get("font", "STANDARD"))
# #                     )
# #                 else:
 
# #                     x, y, _ = entity.dxf.insert
# #                     if tp == "TEXT":
# #                         display_text = entity.dxf.text.strip() or " "
# #                         text_height = float(entity.dxf.height)
# #                     else:
# #                         display_text = str(getattr(entity, "text", "") or getattr(entity.dxf, "text", "") or " ").strip() or " "
# #                         text_height = float(getattr(entity.dxf, "char_height", 10.0) or getattr(entity.dxf, "height", 10.0) or 10.0)
# #                     pyqt_item = DraggableDxfTextItem(display_text, self, hndl, tp)
# #                     pyqt_item.setDefaultTextColor(QColor(0, 120, 255) if hndl in self.selected_handles else base_line_color)
# #                     font = pyqt_item.font()
# #                     font.setPointSizeF(max(text_height, 1.0))
# #                     pyqt_item.setFont(font)
# #                     pyqt_item.setPos(x, -y - text_height)
# #                     pyqt_item.setRotation(-float(getattr(entity.dxf, "rotation", 0.0)))
# #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# #                 self.overlay_items[hndl] = pyqt_item
# #                 self.scene.addItem(pyqt_item) if pyqt_item.scene() is None else None
# #                 continue

# #             if pyqt_item:
# #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
                
# #                 if hndl in self.selected_handles:
# #                     pen_style = QPen(QColor(0, 120, 255), 2.5) 
# #                 else:
# #                     in_group = False
# #                     for group in self.parametric_groups:
# #                         if hndl in group["handles"]:
# #                             group_key = self.get_group_key(group)
# #                             if self.block_keep_state.get(group_key, True):
# #                                 pen_style = QPen(QColor(76, 175, 80), 2)
# #                             else:
# #                                 pen_style = QPen(QColor(211, 47, 47), 2)
# #                             in_group = True
# #                             break
# #                     if not in_group: pen_style = QPen(base_line_color, 1.5)
                
# #                 pyqt_item.setPen(pen_style)
# #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# #                 self.scene.addItem(pyqt_item)
# #                 self.overlay_items[hndl] = pyqt_item

# #         settings = self.get_text_settings()
# #         if settings.get("enabled") and not settings.get("handle"):
# #             box_x = float(settings.get("x", 0.0))
# #             box_y = float(settings.get("y", 0.0))
# #             box_w = self.text_box_width(settings)
# #             box_h = self.text_box_height(settings)
# #             box_item = DraggableDoorTextBoxItem(0, 0, box_w, box_h, self)
# #             box_item.setPos(box_x, -box_y - box_h)
# #             box_item.setBrush(QBrush(QColor(0, 120, 255, 55)))
# #             box_item.setPen(QPen(QColor(0, 120, 255), 1.5, Qt.PenStyle.DashLine))
# #             box_item.setTransformOriginPoint(box_w * 0.5, box_h * 0.5)
# #             box_item.setRotation(-float(settings.get("rotation", 0.0)))
# #             self.scene.addItem(box_item)
# #             display_text = self.text_display_value(settings.get("text", ""))
# #             self.add_centered_text_preview(
# #                 box_item,
# #                 display_text,
# #                 box_w,
# #                 box_h,
# #                 str(settings.get("font", "STANDARD"))
# #             )

# #         self.view.setSceneRect(self.scene.itemsBoundingRect())


# # if __name__ == "__main__":
# #     import PySide6.QtWidgets as qtw
# #     app = qtw.QApplication(sys.argv)
# #     window = MiniCAD()
# #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
# #     window.show()
# #     sys.exit(app.exec())
# import os
# import sys
# import math
# import copy
# import json
# import csv
# import re
# import zipfile
# import xml.etree.ElementTree as ET
# from PySide6.QtGui import QShortcut, QKeySequence
# from parametric_db_new import LoginDialog, ParametricDb
# import table_io

# import ezdxf
# import ezdxf.bbox as dxf_bbox
# from ezdxf.enums import TextEntityAlignment
# from ezdxf.math import Matrix44
# from ezdxf.addons.importer import Importer 

# from PySide6.QtWidgets import (
#     QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
#     QListWidget, QListWidgetItem, QPushButton, QCheckBox,
#     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView, 
#     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem, QInputDialog, QFileDialog, QMessageBox,
#     QGridLayout, QGraphicsTextItem, QGraphicsSimpleTextItem, QGraphicsItem, QTabWidget, QSizePolicy
# )
# from PySide6.QtCore import QPointF, Qt
# from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath, QPainter, QGuiApplication


# try:
#     from graphics_items import SelectableCircle, SelectableLine, SelectableArc
#     from graphics_view import AdvancedGraphicsView
#     from history_manager import HistoryManager
# except ImportError:
#     AdvancedGraphicsView = QGraphicsView
#     class HistoryManager:
#         def __init__(self, p): self.p = p; self.undo_stack=[1]; self.redo_stack=[]
#         def save_state(self): pass
#         def clear_redo(self): pass
#         def undo(self): return True
#         def redo(self): return True


# def patch_ezdxf_entities():
#     from ezdxf.entities import Line, Circle, Arc
    
#     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
#     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
#     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
#     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

#     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
#     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
#     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
#     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

#     Arc.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
#     Arc.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
#     Arc.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
#     Arc.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# patch_ezdxf_entities()


# def parse_factor(text):
#     text = str(text).strip().upper()
    
  
#     if '(' in text:
#         text = text.split('(')[0].strip()
        
#     if not text:
#         return 0.0

#     if text.endswith("%"):
#         try: return float(text[:-1].replace(',', '.')) / 100.0
#         except: return 0.0

#     if text.startswith("Δ/") or text.startswith("D/"):
#         try:
#             div = float(text[2:].replace(',', '.'))
#             return 0.0 if div == 0 else 1.0 / div
#         except: return 0.0

#     if "/" in text: 
#         try:
#             parts = text.split("/")
#             return float(parts[0]) / float(parts[1])
#         except: return 0.0

#     try:
#         val = float(text.replace(',', '.'))
#         if val > 1.0: 
#             return val / 100.0
#         return val
#     except:
#         return 0.0

# def format_factor(val):
#     """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
#     if abs(val - 0.0) < 0.001: return "0% (Фіксовано)"
#     if abs(val - 0.25) < 0.001: return "25% (Δ/4)"
#     if abs(val - 0.333) < 0.01: return "33.3% (Δ/3)"
#     if abs(val - 0.5) < 0.001: return "50% (Δ/2)"
#     if abs(val - 0.667) < 0.01: return "66.7% (2Δ/3)"
#     if abs(val - 0.75) < 0.01: return "75% (3Δ/4)"
#     if abs(val - 1.0) < 0.001: return "100% (Δ)"
#     return f"{val*100:g}%"


# class DraggableDoorTextItem(QGraphicsTextItem):
#     def __init__(self, text, owner):
#         super().__init__(text)
#         self.owner = owner
#         self.setFlags(
#             QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
#             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
#         )

#     def mouseReleaseEvent(self, event):
#         super().mouseReleaseEvent(event)
#         self.owner.on_door_text_item_moved(self)


# class DraggableDxfTextItem(QGraphicsTextItem):
#     def __init__(self, text, owner, handle, entity_type="TEXT"):
#         super().__init__(text)
#         self.owner = owner
#         self.handle = handle
#         self.entity_type = entity_type
#         self.setFlags(
#             QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
#             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
#         )
#         self.setCursor(Qt.CursorShape.OpenHandCursor)

#     def mousePressEvent(self, event):
#         if self.handle:
#             self.owner.selected_handles = {self.handle}
#             self.owner.sync_list_from_handles()
#         self.setCursor(Qt.CursorShape.ClosedHandCursor)
#         super().mousePressEvent(event)

#     def mouseReleaseEvent(self, event):
#         super().mouseReleaseEvent(event)
#         self.setCursor(Qt.CursorShape.OpenHandCursor)
#         self.owner.on_existing_dxf_text_moved(self)


# class DraggableDoorTextBoxItem(QGraphicsRectItem):
#     def __init__(self, x, y, width, height, owner, handle=None):
#         super().__init__(x, y, width, height)
#         self.owner = owner
#         self.handle = handle
#         self.setFlags(
#             QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
#             QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
#         )
#         self.setCursor(Qt.CursorShape.OpenHandCursor)

#     def mousePressEvent(self, event):
#         if self.handle:
#             self.owner.selected_handles = {self.handle}
#             self.owner.sync_list_from_handles()
#         self.setCursor(Qt.CursorShape.ClosedHandCursor)
#         super().mousePressEvent(event)

#     def mouseReleaseEvent(self, event):
#         super().mouseReleaseEvent(event)
#         self.setCursor(Qt.CursorShape.OpenHandCursor)
#         self.owner.on_door_text_box_moved(self)


# # --- МОДУЛЬ ПАРАМЕТРИЧНОГО РУХУ ---
# class ParametricEngine:
#     @staticmethod
#     def signed_shift(value, direction, positive_name, negative_name):
#         """Повертає зсув з урахуванням напрямку.

#         Раніше зсув завжди додавався як +X/+Y. Через це після ROT180 або дзеркала
#         група могла рости в правильний бік, але вся база групи все одно їхала вправо/вгору.
#         """
#         direction = str(direction or positive_name)
#         if direction == negative_name:
#             return -value
#         return value

#     @staticmethod
#     def get_transform(delta_w, delta_h, group):
#         val_x = delta_w if "W" in group.get("link_x", "W") else delta_h
#         val_y = delta_h if "H" in group.get("link_y", "H") else delta_w

#         raw_shift_x = val_x * group.get("k_w", 0.0)
#         raw_shift_y = val_y * group.get("k_h", 0.0)

#         shift_x = ParametricEngine.signed_shift(
#             raw_shift_x,
#             group.get("shift_dir_x", "Вправо"),
#             "Вправо",
#             "Вліво"
#         )
#         shift_y = ParametricEngine.signed_shift(
#             raw_shift_y,
#             group.get("shift_dir_y", "Вгору"),
#             "Вгору",
#             "Вниз"
#         )

#         growth_x = val_x * group.get("growth_p_w", 0.0)
#         growth_y = val_y * group.get("growth_p_h", 0.0)

#         return (shift_x, shift_y, 0), (growth_x, growth_y, 0)


# class MiniCAD(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Параметризатор")
#         self.setGeometry(100, 100, 1600, 950)

#         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
#         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
#         self.debug_output = False
#         self.db = ParametricDb()
#         self.current_user = None
#         self.current_theme = "Темна"
#         self.current_project_file_id = None
#         self.current_door_model_id = None

#         self.selected_handles = set()
#         self.overlay_items = {}
#         self.original_geometries = {}
#         self.is_loading_history = False

#         self.parametric_groups = [] 
#         self.project_meta = {
#             "source_width": None,
#             "source_height": None,
#             "target_width": None,
#             "target_height": None,
#             "keep_blocks": [],
#             "delete_blocks": [],
#             "door_opening": "left",
#             "source_door_opening": "left",
#             "target_door_opening": "left",
#             "growth_axis": "both",
#             "axis_link_mode": "normal",
#             "door_text": {
#                 "enabled": False,
#                 "text": "",
#                 "x": 0.0,
#                 "y": 0.0,
#                 "height": 30.0,
#                 "width_factor": 120.0,
#                 "rotation": 0.0,
#                 "font": "STANDARD",
#                 "handle": None
#             }
#         }
#         self.block_keep_state = {}

#         self.zones_undo_stack = []
#         self.zones_redo_stack = []
#         self.global_recalc_undo_stack = []
#         self.global_recalc_redo_stack = []

#         self.coord_tooltip_item = None
#         self.coord_snap_marker = None

#         self.load_doc_safely()
#         self.load_project_config()
        
#         self.history = HistoryManager(self.dxf_path)
#         self.history.save_state()
#         self.save_zones_history_state()

#         self.init_ui()
#         if not self.authenticate_user():
#             sys.exit(0)
#         self.setup_shortcuts()
#         self.update_dimension_inputs_from_meta()
#         self.set_interface_theme(self.current_theme)
#         self.save_original_geometries()
#         self.update_viewer()
#         self.load_entities_into_list()
#         self.load_groups_into_list()
#         self.scan_project_folder_for_dxf()

#     def load_doc_safely(self):
#         if os.path.exists(self.dxf_path):
#             try:
#                 self.doc = ezdxf.readfile(self.dxf_path)
#             except Exception as e:
#                 print(f"Помилка читання файлу: {e}")
#                 self.doc = ezdxf.new()
#                 self.doc.saveas(self.dxf_path)
#         else:
#             dxf_files = [f for f in os.listdir(self.project_dir) if f.lower().endswith('.dxf')]
#             if dxf_files:
#                 self.dxf_path = os.path.join(self.project_dir, dxf_files[0])
#                 self.doc = ezdxf.readfile(self.dxf_path)
#             else:
#                 self.doc = ezdxf.new()
#                 self.doc.saveas(self.dxf_path)

#     def default_project_meta(self):
#         return {
#             "source_width": None,
#             "source_height": None,
#             "target_width": None,
#             "target_height": None,
#             "keep_blocks": [],
#             "delete_blocks": [],
#             "door_opening": "left",
#             "source_door_opening": "left",
#             "target_door_opening": "left",
#             "growth_axis": "both",
#             "axis_link_mode": "normal",
#             "door_text": self.default_text_settings()
#         }

#     def default_text_settings(self):
#         return {
#             "enabled": False,
#             "text": "",
#             "x": 0.0,
#             "y": 0.0,
#             "height": 30.0,
#             "width_factor": 120.0,
#             "rotation": 0.0,
#             "font": "STANDARD",
#             "handle": None
#         }

#     def get_group_key(self, group):
#         if not group.get("uid"):
#             handles_key = ",".join(sorted(str(h) for h in group.get("handles", [])))
#             group["uid"] = f"{group.get('name', 'group')}|{handles_key}"
#         return group["uid"]

#     def authenticate_user(self):
 
#         if hasattr(self.db, "_check_connection"):
#             self.db._check_connection()

       
#         if not self.db.available:
#             message = (
#                 "⚠️ <font color='#ff9800'><b>Увага: Немає зв'язку з SQL-сервером!</b></font><br><br>"
#                 f"Помилка: {self.db.last_error}<br><br>"
#                 "Введіть логін/пароль для спроби локального входу або перевірте підключення."
#             )
#         else:
#             message = "Вхід"

      
#         while True:
#             dialog = LoginDialog(self, message)
#             if dialog.exec() != LoginDialog.DialogCode.Accepted:
               
#                 return False
            
#             username, password = dialog.credentials()
            
        
#             if not self.db.available:
#                 QMessageBox.critical(
#                     self, 
#                     "Помилка підключення", 
#                     f"Неможливо авторизуватись, оскільки SQL-сервер недоступний.\n\nДеталі помилки:\n{self.db.last_error}"
#                 )
#                 continue

#             try:
#                 user = self.db.authenticate(username, password)
#             except Exception as exc:
#                 QMessageBox.warning(self, "База даних", f"Помилка авторизації:\n{exc}")
#                 return False

#             if user:
#                 self.current_user = user
#                 self.setWindowTitle(f"{self.windowTitle()} | {user.get('username')}")
#                 if hasattr(self, "lbl_status_calc"):
#                     self.lbl_status_calc.setText(
#                         f"<font color='#a5d6a7'>БД підключена. Користувач: {user.get('username')}</font>"
#                     )
#                 self.save_current_project_to_db("Opened")
#                 self.register_current_folder_model(show_errors=False)
#                 self.update_file_status_panel()
#                 return True
                
#             QMessageBox.warning(self, "Авторизація", "Невірний логін або пароль.")


#     def current_user_id(self):
#         if not self.current_user:
#             return None
#         return self.current_user.get("id")

#     def save_current_project_to_db(self, status="ConfigSaved"):
#         if not getattr(self, "db", None) or not self.current_user_id():
#             return

#         project_file_id = self.db.save_project_snapshot(
#             self.project_dir,
#             self.dxf_path,
#             self.project_meta,
#             self.parametric_groups,
#             self.block_keep_state,
#             self.current_user_id(),
#             status,
#             getattr(self, "current_project_file_id", None),
#             getattr(self, "current_door_model_id", None),
#         )

#         if project_file_id:
#             self.current_project_file_id = project_file_id
#             loaded = self.db.load_project_config(
#                 dxf_path=self.dxf_path,
#                 project_file_id=project_file_id,
#                 door_model_id=getattr(self, "current_door_model_id", None),
#             )
#             if loaded and loaded.get("door_model_id"):
#                 self.current_door_model_id = loaded.get("door_model_id")
#             self.register_current_folder_model(show_errors=False)
#             if hasattr(self, "lbl_status_calc"):
#                 self.lbl_status_calc.setText("<font color='#a5d6a7'>Проєкт/модель збережено в MSSQL.</font>")
#         elif hasattr(self, "lbl_status_calc"):
#             self.lbl_status_calc.setText(
#                 f"<font color='#ff9800'>БД не прийняла запис: {self.db.last_error}</font>"
#             )


#     def register_current_folder_model(self, show_errors=True):
#         """One folder = one DoorModel. Register all DXF files in this folder under the same model."""
#         if not getattr(self, "db", None) or not self.current_user_id():
#             return None

#         try:
#             door_model_id = self.db.register_folder_dxf_files(
#                 self.project_dir,
#                 self.project_meta,
#                 self.current_user_id(),
#                 getattr(self, "current_door_model_id", None),
#             )
#         except TypeError:
#             door_model_id = self.db.register_folder_dxf_files(
#                 self.project_dir,
#                 self.project_meta,
#                 self.current_user_id(),
#             )

#         if door_model_id:
#             self.current_door_model_id = door_model_id
#             return door_model_id

#         if show_errors and hasattr(self, "lbl_status_calc"):
#             self.lbl_status_calc.setText(
#                 f"<font color='#ff9800'>Не вдалося зареєструвати папку як модель: {self.db.last_error}</font>"
#             )
#         return None

#     def save_export_to_db(self, export_path, status="Exported"):
#         if not getattr(self, "db", None) or not self.current_user_id():
#             return
#         if not getattr(self, "current_project_file_id", None):
#             self.save_current_project_to_db("BeforeExport")
#         if not getattr(self, "current_project_file_id", None):
#             return

#         self.db.save_export_file(
#             self.current_project_file_id,
#             export_path,
#             self.project_meta.get("target_width"),
#             self.project_meta.get("target_height"),
#             self.export_target_opening(),
#             self.current_user_id(),
#             getattr(self, "current_door_model_id", None),
#         )

#     def select_all_entities(self):
#         self.selected_handles.clear()

#         for i in range(self.entity_list.count()):
#             item = self.entity_list.item(i)
#             handle = item.data(Qt.UserRole)

#             if handle is None:
#                 continue

#             self.selected_handles.add(str(handle))
#             item.setSelected(True)

#         self.update_viewer()
#         # self.sync_entity_list_selection()


#     def clear_selection(self):
#         self.selected_handles.clear()
#         self.entity_list.clearSelection()
#         self.group_list_widget.clearSelection()
#         self.update_viewer()


#     def zoom_extents(self):
#         self.view.fitInView(
#             self.scene.itemsBoundingRect(),
#             Qt.KeepAspectRatio
#         )


#     def load_project_config(self):
#         """
#         Основне завантаження тільки з MSSQL.

#         1) шукаємо DoorModel по поточній папці;
#         2) шукаємо ProjectFile по DoorModelId + FileName;
#         3) якщо файл ще не має груп, але DoorModel має початкові розміри —
#            підтягуємо W/H/відкривання з DoorModels;
#         4) JSON автоматично не читаємо.
#         """
#         self.parametric_groups.clear()
#         self.project_meta = self.default_project_meta()
#         self.block_keep_state = {}

#         if not getattr(self, "db", None) or not getattr(self.db, "available", False):
#             return

#         try:
#             if not getattr(self, "current_door_model_id", None):
#                 model_id = self.db.find_door_model_by_folder(self.project_dir)
#                 if model_id:
#                     self.current_door_model_id = model_id

#             loaded = None
#             if getattr(self, "current_door_model_id", None):
#                 loaded = self.db.load_project_config(
#                     dxf_path=self.dxf_path,
#                     project_file_id=getattr(self, "current_project_file_id", None),
#                     door_model_id=getattr(self, "current_door_model_id", None),
#                     file_name=os.path.basename(self.dxf_path),
#                 )

#             if not loaded and getattr(self, "current_door_model_id", None):
#                 model_data = self.db.load_door_model(self.current_door_model_id)
#                 if model_data:
#                     meta = model_data.get("meta") or {}
#                     self.project_meta.update(meta)
                    
#                     link_x, link_y = self.link_pair_for_mode(self.project_meta.get("axis_link_mode", "normal"))
#                     self.project_meta["link_x"] = link_x
#                     self.project_meta["link_y"] = link_y
#                     text_settings = self.default_text_settings()
#                     text_settings.update(self.project_meta.get("door_text") or {})
                    
#                     self.project_meta["door_text"] = text_settings
#                     return

#             if not loaded:
#                 return

#             self.current_project_file_id = loaded.get("project_file_id")
#             if loaded.get("door_model_id"):
#                 self.current_door_model_id = loaded.get("door_model_id")

#             self.project_meta.update(loaded.get("meta") or {})
#             link_x, link_y = self.link_pair_for_mode(self.project_meta.get("axis_link_mode", "normal"))
#             self.project_meta["link_x"] = link_x
#             self.project_meta["link_y"] = link_y
#             text_settings = self.default_text_settings()
#             text_settings.update(self.project_meta.get("door_text") or {})
#             self.project_meta["door_text"] = text_settings

#             self.parametric_groups = loaded.get("groups") or []
#             self.block_keep_state = loaded.get("block_keep_state") or {}

#         except Exception as exc:
#             print(f"Помилка завантаження конфігурації з БД: {exc}")

#         for g in self.parametric_groups:
#             g["handles"] = set(g.get("handles", []))
#             self.get_group_key(g)

#             if "k_x" in g:
#                 g["k_w"] = g.pop("k_x")
#                 g["k_h"] = g.pop("k_y")
#                 g["growth_p_w"] = g.pop("growth_p_x")
#                 g["growth_p_h"] = g.pop("growth_p_y")
#             else:
#                 g["k_w"] = g.get("k_w", 0.0)
#                 g["k_h"] = g.get("k_h", 0.0)
#                 g["growth_p_w"] = g.get("growth_p_w", 0.0)
#                 g["growth_p_h"] = g.get("growth_p_h", 0.0)

#             # Прив'язка осей груп береться з AxisLinkMode файлу, а не зі старих значень групи.
#             g["link_x"], g["link_y"] = self.link_pair_for_mode()

#             if "growth_direction" in g:
#                 old_dir = g.pop("growth_direction")
#                 g["growth_dir_x"] = "Вправо" if "Вправо" in old_dir else ("Вліво" if "Вліво" in old_dir else "Центр")
#                 g["growth_dir_y"] = "Вгору" if "Вгору" in old_dir else ("Вниз" if "Вниз" in old_dir else "Центр")
#             else:
#                 g["growth_dir_x"] = g.get("growth_dir_x", "Центр")
#                 g["growth_dir_y"] = g.get("growth_dir_y", "Центр")

#             g["shift_dir_x"] = g.get("shift_dir_x", "Вправо")
#             g["shift_dir_y"] = g.get("shift_dir_y", "Вгору")
#             g["role_y"] = g.get("role_y", "manual")
#             g["auto_rule"] = bool(g.get("auto_rule", False))
#             g["touch_y_enabled"] = bool(g.get("touch_y_enabled", False))
#             g["touch_to_uid"] = g.get("touch_to_uid")
#             g["touch_gap_y"] = float(g.get("touch_gap_y", 0.0) or 0.0)

#             if "resizes" not in g:
#                 g["resizes"] = (
#                     abs(float(g.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
#                     abs(float(g.get("growth_p_h", 0.0) or 0.0)) > 0.000001
#                 )

#             key = self.get_group_key(g)
#             if key not in self.block_keep_state:
#                 self.block_keep_state[key] = True

#             self.apply_growth_axis_to_group(g)

#         self.apply_axis_link_mode_to_groups()

#     def save_project_config(self):
#         """Замість JSON пишемо конфігурацію в MSSQL."""
#         self.project_meta["keep_blocks"] = [name for name, keep in self.block_keep_state.items() if keep]
#         self.project_meta["delete_blocks"] = [name for name, keep in self.block_keep_state.items() if not keep]
#         self.save_current_project_to_db("ConfigSaved")


#     def load_config_from_json_file(self):
#         """
#         Ручне завантаження старої JSON-конфігурації.

#         Це єдине місце, де JSON читається.
#         Після завантаження дані одразу записуються в MSSQL.
#         """
#         file_path, _ = QFileDialog.getOpenFileName(
#             self,
#             "Завантажити налаштування з JSON",
#             self.project_dir,
#             "JSON Files (*.json);;All Files (*)"
#         )
#         if not file_path:
#             return

#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 raw_data = json.load(f)

#             self.parametric_groups.clear()
#             self.block_keep_state = {}

#             if isinstance(raw_data, dict):
#                 self.project_meta.update(raw_data.get("meta", {}))
#                 text_settings = self.default_text_settings()
#                 text_settings.update(self.project_meta.get("door_text") or {})
#                 self.project_meta["door_text"] = text_settings
#                 self.parametric_groups = raw_data.get("groups", [])
#                 self.block_keep_state = raw_data.get("block_keep_state", {}) or {}
#             elif isinstance(raw_data, list):
#                 self.parametric_groups = raw_data
#             else:
#                 QMessageBox.warning(self, "JSON", "Невідомий формат JSON-файлу.")
#                 return

#             for g in self.parametric_groups:
#                 g["handles"] = set(g.get("handles", []))
#                 self.get_group_key(g)

#                 g["k_w"] = g.get("k_w", g.get("k_x", 0.0))
#                 g["k_h"] = g.get("k_h", g.get("k_y", 0.0))
#                 g["growth_p_w"] = g.get("growth_p_w", g.get("growth_p_x", 0.0))
#                 g["growth_p_h"] = g.get("growth_p_h", g.get("growth_p_y", 0.0))

#                 g["growth_dir_x"] = g.get("growth_dir_x", "Центр")
#                 g["growth_dir_y"] = g.get("growth_dir_y", "Центр")
#                 g["shift_dir_x"] = g.get("shift_dir_x", "Вправо")
#                 g["shift_dir_y"] = g.get("shift_dir_y", "Вгору")
#                 g["link_x"] = g.get("link_x", "X = W")
#                 g["link_y"] = g.get("link_y", "Y = H")
#                 g["resizes"] = bool(g.get("resizes", False))

#                 key = self.get_group_key(g)
#                 if key not in self.block_keep_state:
#                     self.block_keep_state[key] = True

#             self.save_project_config()
#             self.update_dimension_inputs_from_meta()
#             self.update_viewer()
#             self.load_groups_into_list()
#             self.load_block_filter_list()
#             self.update_file_status_panel()

#             QMessageBox.information(
#                 self,
#                 "JSON",
#                 "Налаштування завантажено з JSON і збережено в MSSQL."
#             )

#         except Exception as exc:
#             QMessageBox.critical(self, "JSON", f"Не вдалося завантажити JSON:\n{exc}")

#     def init_ui(self):
#         main_widget = QWidget()
#         self.central_layout = QHBoxLayout(main_widget)
#         self.setCentralWidget(main_widget)

#         folder_explorer_widget = QWidget()
#         folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
#         folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
#         lbl_explorer_title = QLabel("📁 <b>Провідник DXF:</b>")
#         lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
#         folder_explorer_layout.addWidget(lbl_explorer_title)

#         self.btn_open_file = QPushButton("📂 Відкрити файл...")
#         self.btn_open_file.setStyleSheet("background-color: #37474f; color: white; font-weight: bold; padding: 4px;")
#         self.btn_open_file.clicked.connect(self.open_dxf_from_dialog)
#         folder_explorer_layout.addWidget(self.btn_open_file)

#         self.btn_load_json_settings = QPushButton("📥 Завантажити налаштування JSON")
#         self.btn_load_json_settings.setStyleSheet("background-color: #455a64; color: white; font-weight: bold; padding: 4px;")
#         self.btn_load_json_settings.clicked.connect(self.load_config_from_json_file)
#         folder_explorer_layout.addWidget(self.btn_load_json_settings)
        
#         self.file_explorer_list = QListWidget()
#         self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#         self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
#         folder_explorer_layout.addWidget(self.file_explorer_list)
#         self.central_layout.addWidget(folder_explorer_widget, stretch=1)

#         self.scene = QGraphicsScene()
#         self.view = AdvancedGraphicsView(self.scene, self)
#         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
#         self.view.setMouseTracking(True)  
#         self.scene.mouseMoveEvent = self.on_scene_mouse_move
#         self.central_layout.addWidget(self.view, stretch=5)
#         self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 

#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True) 
#         self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
#         control_panel = QWidget()
#         control_panel_layout = QVBoxLayout(control_panel)
#         control_panel_layout.setContentsMargins(5, 5, 5, 5)
#         self.scroll_area.setWidget(control_panel)
#         self.central_layout.addWidget(self.scroll_area, stretch=4)

#         self.file_status_group = QGroupBox("Стан файлу")
#         file_status_box = QGridLayout()
#         file_status_box.setSpacing(4) 
#         file_status_box.setContentsMargins(6, 12, 6, 6)

#         self.lbl_file_status_source = QLabel("")
#         self.lbl_file_status_target = QLabel("")
#         self.lbl_file_status_opening = QLabel("")
#         self.lbl_file_status_axis = QLabel("")
#         self.lbl_file_status_db = QLabel("")

#         file_status_box.addWidget(self.lbl_file_status_source, 0, 0)
#         file_status_box.addWidget(self.lbl_file_status_target, 0, 1)
#         file_status_box.addWidget(self.lbl_file_status_opening, 1, 0)
#         file_status_box.addWidget(self.lbl_file_status_axis, 1, 1)
#         file_status_box.addWidget(self.lbl_file_status_db, 2, 0, 1, 2)

#         file_status_box.addWidget(QLabel("Осі файлу:"), 3, 0)

#         axis_box = QHBoxLayout()

#         self.combo_link_x = QComboBox()
#         self.combo_link_x.addItems(["X = W", "X = H"])
#         self.combo_link_x.setEnabled(True)
#         self.combo_link_x.setToolTip("Глобальна прив'язка осей для всього файлу")
#         axis_box.addWidget(self.combo_link_x)

#         self.combo_link_y = QComboBox()
#         self.combo_link_y.addItems(["Y = H", "Y = W"])
#         self.combo_link_y.setEnabled(False)
#         self.combo_link_y.setToolTip("Глобальна прив'язка осей для всього файлу")
#         axis_box.addWidget(self.combo_link_y)

#         file_status_box.addLayout(axis_box, 3, 1)

#         self.file_status_group.setLayout(file_status_box)
#         control_panel_layout.addWidget(self.file_status_group)

#         self.side_tabs = QTabWidget()
#         self.side_tabs.setDocumentMode(True)
#         self.side_tabs.setUsesScrollButtons(True)
#         self.tab_file = QWidget()
#         self.tab_sizes = QWidget()
#         self.tab_groups = QWidget()
#         self.tab_text = QWidget()
#         self.tab_more = QWidget()
#         self.tab_file_layout = QVBoxLayout(self.tab_file)
#         self.tab_sizes_layout = QVBoxLayout(self.tab_sizes)
#         self.tab_groups_layout = QVBoxLayout(self.tab_groups)
#         self.tab_text_layout = QVBoxLayout(self.tab_text)
#         self.tab_more_layout = QVBoxLayout(self.tab_more)
#         for layout in (
#             self.tab_file_layout,
#             self.tab_sizes_layout,
#             self.tab_groups_layout,
#             self.tab_text_layout,
#             self.tab_more_layout,
#         ):
#             layout.setContentsMargins(3, 3, 3, 3)
#             layout.setSpacing(4)
#         self.side_tabs.addTab(self.tab_file, "Файл")
#         self.side_tabs.addTab(self.tab_sizes, "Розміри")
#         self.side_tabs.addTab(self.tab_groups, "Групи")
#         self.side_tabs.addTab(self.tab_text, "Текст")
#         self.side_tabs.addTab(self.tab_more, "Інше")
#         control_panel_layout.addWidget(self.side_tabs)

#         inspector_group = QGroupBox("")
#         inspector_box = QVBoxLayout()
#         self.chk_enable_inspector = QCheckBox(" Ввімкнути інтерактивний трекер точок")
#         self.chk_enable_inspector.setStyleSheet("color: #ff9800; font-weight: bold;")
#         self.chk_enable_inspector.clicked.connect(self.toggle_inspector_mode)
#         inspector_box.addWidget(self.chk_enable_inspector)
        
#         self.btn_snap_zero = QPushButton("↙️ Притиснути фігуру до (0, 0)")
#         self.btn_snap_zero.setStyleSheet("background-color: #00897b; color: white; font-weight: bold; padding: 6px;")
#         self.btn_snap_zero.clicked.connect(self.snap_to_zero)
#         inspector_box.addWidget(self.btn_snap_zero)
        
#         inspector_group.setLayout(inspector_box)
#         self.tab_more_layout.addWidget(inspector_group)

#         self.transform_group = QGroupBox("🔄 Трансформація виділених елементів (DXF)")
#         self.transform_group.setStyleSheet("QGroupBox { border: 1px solid #d32f2f; }")
#         transform_box = QVBoxLayout()
        
#         rot_btn_layout = QHBoxLayout()
#         self.btn_rot_90 = QPushButton("90°")
#         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
#         rot_btn_layout.addWidget(self.btn_rot_90)
        
#         self.btn_rot_180 = QPushButton("180°")
#         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
#         rot_btn_layout.addWidget(self.btn_rot_180)
        
#         self.btn_rot_270 = QPushButton("270°")
#         self.btn_rot_270.clicked.connect(lambda: self.transform_selected_entities("ROT270"))
#         rot_btn_layout.addWidget(self.btn_rot_270)
#         transform_box.addLayout(rot_btn_layout)

#         mirror_btn_layout = QHBoxLayout()
#         self.btn_mirror_h = QPushButton("Дзеркало ↔ Ліво/право")
#         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
#         mirror_btn_layout.addWidget(self.btn_mirror_h)

#         self.btn_mirror_v = QPushButton("Дзеркало ↕ Верх/низ")
#         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
#         mirror_btn_layout.addWidget(self.btn_mirror_v)
#         transform_box.addLayout(mirror_btn_layout)

#         self.transform_group.setLayout(transform_box)
#         self.tab_file_layout.addWidget(self.transform_group)

#         auto_scale_group = QGroupBox(" Параметрична трансформація розмірів")
#         auto_scale_box = QVBoxLayout()

#         width_layout = QHBoxLayout()
#         width_layout.addWidget(QLabel("Ширина:"))
#         self.input_current_width = QLineEdit("1000")
#         width_layout.addWidget(self.input_current_width)
#         width_layout.addWidget(QLabel("➡️ Нова:"))
#         self.input_target_width = QLineEdit("1050")
#         width_layout.addWidget(self.input_target_width)
#         auto_scale_box.addLayout(width_layout)

#         height_layout = QHBoxLayout()
#         height_layout.addWidget(QLabel("Висота:"))
#         self.input_current_height = QLineEdit("2000")
#         height_layout.addWidget(self.input_current_height)
#         height_layout.addWidget(QLabel("➡️ Нова:"))
#         self.input_target_height = QLineEdit("2080")
#         height_layout.addWidget(self.input_target_height)
#         auto_scale_box.addLayout(height_layout)

#         self.lbl_status_calc = QLabel("Задайте нові розміри конструкції для автоматичного морфінгу.")
#         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
#         auto_scale_box.addWidget(self.lbl_status_calc)

#         self.btn_apply_auto_scale = QPushButton(" Запустити глобальний перерахунок")
#         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
#         self.btn_apply_auto_scale.clicked.connect(lambda: self.process_parametric_percentage_scale())
#         auto_scale_box.addWidget(self.btn_apply_auto_scale)

#         preview_buttons = QHBoxLayout()
#         self.btn_preview_scale = QPushButton("Перегляд")
#         self.btn_preview_scale.clicked.connect(self.preview_parametric_scale)
#         preview_buttons.addWidget(self.btn_preview_scale)

#         self.btn_restore_current = QPushButton("Повернути базу")
#         self.btn_restore_current.clicked.connect(self.restore_current_dxf_from_disk)
#         preview_buttons.addWidget(self.btn_restore_current)
#         auto_scale_box.addLayout(preview_buttons)

#         workflow_buttons = QHBoxLayout()
#         self.btn_remember_source_size = QPushButton("Запам'ятати початкові")
#         self.btn_remember_source_size.clicked.connect(self.remember_source_dimensions)
#         workflow_buttons.addWidget(self.btn_remember_source_size)

#         self.btn_import_params = QPushButton("Excel/CSV параметри")
#         self.btn_import_params.clicked.connect(self.import_parameters_from_table)
#         workflow_buttons.addWidget(self.btn_import_params)

#         self.btn_order_wizard = QPushButton("Нове замовлення")
#         self.btn_order_wizard.clicked.connect(self.quick_order_wizard)
#         workflow_buttons.addWidget(self.btn_order_wizard)
#         auto_scale_box.addLayout(workflow_buttons)

#         self.btn_export_new_dxf = QPushButton("Створити новий DXF")
#         self.btn_export_new_dxf.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;")
#         self.btn_export_new_dxf.clicked.connect(self.export_new_dxf_with_dimensions)
#         auto_scale_box.addWidget(self.btn_export_new_dxf)

#         self.btn_batch_export = QPushButton("Пакет з Excel/CSV")
#         self.btn_batch_export.clicked.connect(self.batch_export_from_table)
#         auto_scale_box.addWidget(self.btn_batch_export)

#         # self.btn_find_min_size = QPushButton("Мінімум без накладання")
#         # self.btn_find_min_size.clicked.connect(self.find_minimum_safe_size)
#         # auto_scale_box.addWidget(self.btn_find_min_size)

#         auto_scale_group.setLayout(auto_scale_box)
#         self.tab_sizes_layout.addWidget(auto_scale_group)

#         opening_group = QGroupBox("Відкривання")
#         opening_box = QHBoxLayout()
#         opening_box.addWidget(QLabel("Початкове:"))
#         self.combo_source_door_opening = QComboBox()
#         self.combo_source_door_opening.addItems(["Ліве", "Праве"])
#         self.combo_source_door_opening.currentTextChanged.connect(self.on_source_door_opening_changed)
#         opening_box.addWidget(self.combo_source_door_opening)
#         opening_box.addWidget(QLabel("Отримати:"))
#         self.combo_door_opening = QComboBox()
#         self.combo_door_opening.addItems(["Ліве", "Праве"])
#         self.combo_door_opening.currentTextChanged.connect(self.on_door_opening_changed)
#         opening_box.addWidget(self.combo_door_opening)
#         self.btn_mirror_opening = QPushButton("Змінити L/R")
#         self.btn_mirror_opening.clicked.connect(self.mirror_door_opening)
#         opening_box.addWidget(self.btn_mirror_opening)
#         opening_group.setLayout(opening_box)
#         self.tab_sizes_layout.addWidget(opening_group)

#         text_group = QGroupBox("Текст на дверях")
#         text_box = QGridLayout()
#         self.check_door_text_enabled = QCheckBox("Додати текст")
#         self.check_door_text_enabled.stateChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.check_door_text_enabled, 0, 0, 1, 2)

#         text_box.addWidget(QLabel("Текст:"), 1, 0)
#         self.input_door_text = QLineEdit()
#         self.input_door_text.textChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.input_door_text, 1, 1, 1, 3)

#         text_box.addWidget(QLabel("X:"), 2, 0)
#         self.input_text_x = QLineEdit("0")
#         self.input_text_x.textChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.input_text_x, 2, 1)

#         text_box.addWidget(QLabel("Y:"), 2, 2)
#         self.input_text_y = QLineEdit("0")
#         self.input_text_y.textChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.input_text_y, 2, 3)

#         text_box.addWidget(QLabel("Висота:"), 3, 0)
#         self.input_text_height = QLineEdit("30")
#         self.input_text_height.textChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.input_text_height, 3, 1)

#         text_box.addWidget(QLabel("Ширина рамки:"), 3, 2)
#         self.input_text_width_factor = QLineEdit("120")
#         self.input_text_width_factor.textChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.input_text_width_factor, 3, 3)

#         text_box.addWidget(QLabel("Поворот:"), 4, 0)
#         self.input_text_rotation = QLineEdit("0")
#         self.input_text_rotation.textChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.input_text_rotation, 4, 1)

#         text_box.addWidget(QLabel("Шрифт:"), 4, 2)
#         self.combo_text_font = QComboBox()
#         self.combo_text_font.setEditable(True)
#         self.combo_text_font.addItems([
#             "STANDARD", "Arial", "Arial Narrow", "Arial Black",
#             "Calibri", "Calibri Light", "Cambria", "Candara",
#             "Century Gothic", "Consolas", "Courier New",
#             "Georgia", "Impact", "Segoe UI", "Tahoma",
#             "Times New Roman", "Trebuchet MS", "Verdana",
#             "Simplex", "Romans", "Isocp"
#         ])
#         self.combo_text_font.currentTextChanged.connect(self.on_text_settings_changed)
#         text_box.addWidget(self.combo_text_font, 4, 3)

#         self.btn_place_door_text = QPushButton("Показати/поставити блок")
#         self.btn_place_door_text.clicked.connect(self.place_empty_door_text_block)
#         text_box.addWidget(self.btn_place_door_text, 5, 0, 1, 4)

#         self.btn_apply_door_text = QPushButton("Оновити текст")
#         self.btn_apply_door_text.clicked.connect(self.apply_door_text_from_ui)
#         text_box.addWidget(self.btn_apply_door_text, 6, 0, 1, 4)

#         self.btn_remove_door_text = QPushButton("Прибрати текстовий блок")
#         self.btn_remove_door_text.clicked.connect(self.remove_door_text_block)
#         text_box.addWidget(self.btn_remove_door_text, 7, 0, 1, 4)

#         align_text_buttons = QHBoxLayout()
#         self.btn_align_text_width = QPushButton("Вирівняти по ширині")
#         self.btn_align_text_width.clicked.connect(lambda: self.align_text_box_to_door("width"))
#         align_text_buttons.addWidget(self.btn_align_text_width)
#         self.btn_align_text_height = QPushButton("Вирівняти по висоті")
#         self.btn_align_text_height.clicked.connect(lambda: self.align_text_box_to_door("height"))
#         align_text_buttons.addWidget(self.btn_align_text_height)
#         text_box.addLayout(align_text_buttons, 8, 0, 1, 4)
#         text_group.setLayout(text_box)
#         self.text_group = text_group
#         self.text_box_layout = text_box
#         text_group.setCheckable(True)
#         text_group.toggled.connect(self.set_text_panel_expanded)
#         text_settings = self.project_meta.get("door_text", {})
#         text_open = bool(
#             text_settings.get("enabled") or
#             str(text_settings.get("text", "")).strip() or
#             text_settings.get("handle")
#         )
#         text_group.setChecked(text_open)
#         self.set_text_panel_expanded(text_open)
#         self.tab_text_layout.addWidget(text_group)
#         self.sync_text_inputs_from_meta()
#         self.sync_opening_inputs_from_meta()

#         history_group = QGroupBox("Конструкторська історія")
#         history_box = QHBoxLayout()
#         self.btn_undo = QPushButton("Назад")
#         self.btn_undo.clicked.connect(self.undo)
#         self.btn_redo = QPushButton("Вперед")
#         self.btn_redo.clicked.connect(self.redo)
#         history_box.addWidget(self.btn_undo)
#         history_box.addWidget(self.btn_redo)
#         history_group.setLayout(history_box)
#         self.tab_file_layout.addWidget(history_group)

#         group_constructor_group = QGroupBox(" Параметричні групи топології")
#         group_box = QVBoxLayout()

#         self.btn_create_group = QPushButton(" Створити параметричну групу")
#         self.btn_create_group.setStyleSheet("background-color: #673ab7; color: white; font-weight: bold;")
#         self.btn_create_group.clicked.connect(self.create_parametric_group)
#         group_box.addWidget(self.btn_create_group)

#         self.btn_auto_group_entities = QPushButton("Автогрупувати")
#         self.btn_auto_group_entities.setStyleSheet("background-color: #455a64; color: white; font-weight: bold;")
#         self.btn_auto_group_entities.clicked.connect(self.auto_group_entities)
#         self.btn_auto_group_entities.hide()

#         self.btn_delete_from_dxf = QPushButton(" Видалити об'єкти з креслення (DXF)")
#         self.btn_delete_from_dxf.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
#         self.btn_delete_from_dxf.clicked.connect(self.delete_entities_from_dxf)
#         group_box.addWidget(self.btn_delete_from_dxf)

#         self.btn_remove_selected = QPushButton(" Виключити виділене з групи")
#         self.btn_remove_selected.clicked.connect(self.remove_selected_from_group)
#         group_box.addWidget(self.btn_remove_selected)

#         self.btn_disband_group = QPushButton("Розформувати вибрану групу")
#         self.btn_disband_group.clicked.connect(self.disband_parametric_group)
#         group_box.addWidget(self.btn_disband_group)

#         group_box.addWidget(QLabel("<b>Параметричні групи деталей:</b>"))
#         self.group_list_widget = QListWidget()
#         self.group_list_widget.setFixedHeight(76)
#         self.group_list_widget.itemSelectionChanged.connect(self.on_group_selection_changed)
#         group_box.addWidget(self.group_list_widget)

#         group_box.addWidget(QLabel("<b>Блоки для нового DXF (галочка = лишити):</b>"))
#         self.block_filter_list = QListWidget()
#         self.block_filter_list.setFixedHeight(70)
#         self.block_filter_list.itemChanged.connect(self.on_block_keep_state_changed)
#         group_box.addWidget(self.block_filter_list)

   
#         group_box.addWidget(QLabel("<b> Параметри трансформації:</b>"))
        
#         growth_axis_layout = QHBoxLayout()
#         growth_axis_layout.addWidget(QLabel("Режим файлу:"))
#         self.combo_group_growth_axis = QComboBox()
#         self.combo_group_growth_axis.addItems(["Ширина + висота", "Тільки ширина", "Тільки висота", "Не росте"])
#         self.combo_group_growth_axis.currentTextChanged.connect(self.on_group_growth_axis_changed)
#         growth_axis_layout.addWidget(self.combo_group_growth_axis)
#         group_box.addLayout(growth_axis_layout)

#         self.chk_group_resizes = QCheckBox("Група змінює розмір")
#         self.chk_group_resizes.stateChanged.connect(self.on_group_resizes_changed)
#         group_box.addWidget(self.chk_group_resizes)

#         grid = QGridLayout()
#         self.param_transform_grid = grid
#         grid.setContentsMargins(0, 0, 0, 0)
#         grid.setHorizontalSpacing(4)
#         grid.setVerticalSpacing(3)

#         preset_items = [
#             "0% (Фіксовано)",
#             "25% (1/4)",
#             "33.3% (1/3)",
#             "50% (Центр / Δ/2)",
#             "66.7% (2/3)",
#             "75% (1/4)",
#             "100% (Δ/1)",
#             "Ввести вручну"
#         ]

#         self.combo_k_w = QComboBox()
#         self.combo_k_w.setEditable(True)
#         self.combo_k_w.addItems(preset_items)

#         self.combo_shift_dir_x = QComboBox()
#         self.combo_shift_dir_x.addItems(["Вправо", "Вліво"])

#         self.combo_growth_p_w = QComboBox()
#         self.combo_growth_p_w.setEditable(True)
#         self.combo_growth_p_w.addItems(preset_items)

#         self.combo_growth_dir_x = QComboBox()
#         self.combo_growth_dir_x.addItems(["Вправо", "Вліво", "Центр"])

#         self.combo_k_h = QComboBox()
#         self.combo_k_h.setEditable(True)
#         self.combo_k_h.addItems(preset_items)

#         self.combo_shift_dir_y = QComboBox()
#         self.combo_shift_dir_y.addItems(["Вгору", "Вниз"])

#         self.combo_growth_p_h = QComboBox()
#         self.combo_growth_p_h.setEditable(True)
#         self.combo_growth_p_h.addItems(preset_items)

#         self.combo_growth_dir_y = QComboBox()
#         self.combo_growth_dir_y.addItems(["Вгору", "Вниз", "Центр"])

#         self.lbl_shift_x = QLabel("X зсув")
#         self.lbl_growth_x = QLabel("X ріст")
#         self.lbl_shift_y = QLabel("Y зсув")
#         self.lbl_growth_y = QLabel("Y ріст")

#         grid.addWidget(self.lbl_shift_x, 0, 0)
#         grid.addWidget(self.combo_k_w, 0, 1)
#         grid.addWidget(self.combo_shift_dir_x, 0, 2)

#         grid.addWidget(self.lbl_shift_y, 1, 0)
#         grid.addWidget(self.combo_k_h, 1, 1)
#         grid.addWidget(self.combo_shift_dir_y, 1, 2)

#         grid.addWidget(self.lbl_growth_x, 2, 0)
#         grid.addWidget(self.combo_growth_p_w, 2, 1)
#         grid.addWidget(self.combo_growth_dir_x, 2, 2)

#         grid.addWidget(self.lbl_growth_y, 3, 0)
#         grid.addWidget(self.combo_growth_p_h, 3, 1)
#         grid.addWidget(self.combo_growth_dir_y, 3, 2)

#         grid.setColumnStretch(0, 0)
#         grid.setColumnStretch(1, 1)
#         grid.setColumnStretch(2, 0)

#         group_box.addLayout(grid)

#         rule_layout = QHBoxLayout()
#         self.combo_rule_library = QComboBox()
#         self.combo_rule_library.addItems(list(self.typical_rule_library().keys()))
#         rule_layout.addWidget(self.combo_rule_library)
#         self.btn_apply_rule = QPushButton("Застосувати правило")
#         self.btn_apply_rule.clicked.connect(self.apply_selected_rule_to_group)
#         rule_layout.addWidget(self.btn_apply_rule)
#         group_box.addLayout(rule_layout)

#         topology_layout = QHBoxLayout()
#         # self.btn_auto_rules_y = QPushButton("Авто правила Y")
#         # self.btn_auto_rules_y.setStyleSheet("background-color: #455a64; color: white; font-weight: bold;")
#         # self.btn_auto_rules_y.clicked.connect(self.auto_apply_vertical_topology_rules)
#         # topology_layout.addWidget(self.btn_auto_rules_y)

#         # self.btn_touch_rules_y = QPushButton("Зберігати дотик Y")
#         # self.btn_touch_rules_y.setStyleSheet("background-color: #00695c; color: white; font-weight: bold;")
#         # self.btn_touch_rules_y.clicked.connect(self.auto_detect_vertical_touch_constraints)
#         # topology_layout.addWidget(self.btn_touch_rules_y)

#         self.btn_auto_chain_growth_y = QPushButton("Авто сума росту Y")
#         self.btn_auto_chain_growth_y.setStyleSheet("background-color: #1565c0; color: white; font-weight: bold;")
#         self.btn_auto_chain_growth_y.clicked.connect(self.auto_chain_growth_y)
#         self.btn_auto_chain_growth_y.hide()

#         self.btn_auto_chain_growth_x = QPushButton("Авто сума росту X")
#         self.btn_auto_chain_growth_x.setStyleSheet("background-color: #6a1b9a; color: white; font-weight: bold;")
#         self.btn_auto_chain_growth_x.clicked.connect(self.auto_chain_growth_x)
#         self.btn_auto_chain_growth_x.hide()

#         self.btn_auto_layout_all = QPushButton("Авторозставити все")
#         self.btn_auto_layout_all.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
#         self.btn_auto_layout_all.clicked.connect(self.auto_layout_all_groups)
#         self.btn_auto_layout_all.hide()

#         # self.btn_auto_mirror_x = QPushButton("Дзеркальні сторони X")
#         # self.btn_auto_mirror_x.setStyleSheet("background-color: #8d6e63; color: white; font-weight: bold;")
#         # self.btn_auto_mirror_x.clicked.connect(self.confirm_and_apply_mirror_x_rules)
#         # topology_layout.addWidget(self.btn_auto_mirror_x)
#         group_box.addLayout(topology_layout)

#         # Підключення сигналів сітки

        
#         self.combo_k_w.currentTextChanged.connect(self.on_combo_k_w_changed)
#         self.combo_k_h.currentTextChanged.connect(self.on_combo_k_h_changed)
#         self.combo_growth_p_w.currentTextChanged.connect(self.on_combo_growth_p_w_changed)
#         self.combo_growth_p_h.currentTextChanged.connect(self.on_combo_growth_p_h_changed)
        
#         self.combo_growth_dir_x.currentTextChanged.connect(self.on_growth_dir_x_changed)
#         self.combo_growth_dir_y.currentTextChanged.connect(self.on_growth_dir_y_changed)
#         self.combo_shift_dir_x.currentTextChanged.connect(self.on_shift_dir_x_changed)
#         self.combo_shift_dir_y.currentTextChanged.connect(self.on_shift_dir_y_changed)


#         self.combo_link_x.currentTextChanged.connect(self.on_link_x_changed)
#         self.combo_link_y.currentTextChanged.connect(self.on_link_y_changed)
#         # -------------------------------------------------------------

#         group_constructor_group.setLayout(group_box)
#         self.tab_groups_layout.addWidget(group_constructor_group)

#         self.tab_groups_layout.addWidget(QLabel("<b>Повний список ліній/отворів у файлі:</b>"))
#         self.entity_list = QListWidget()
#         self.entity_list.setFixedHeight(86)
#         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
#         self.tab_groups_layout.addWidget(self.entity_list)

#         theme_group = QGroupBox(" Інтерфейс")
#         theme_box = QHBoxLayout()
#         self.theme_combo = QComboBox()
#         self.theme_combo.addItems(["Темна", "Світла"])
#         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
#         theme_box.addWidget(self.theme_combo)
#         theme_group.setLayout(theme_box)
#         self.tab_more_layout.addWidget(theme_group)

#         self.tab_file_layout.addStretch()
#         self.tab_sizes_layout.addStretch()
#         self.tab_groups_layout.addStretch()
#         self.tab_text_layout.addStretch()
#         self.tab_more_layout.addStretch()
#         control_panel_layout.addStretch()
#         self.apply_compact_right_panel_style()
#         self.apply_group_controls_visibility(None)
#         self.update_history_buttons_state()


#     def update_growth_controls_visibility(self):
#         checked = self.chk_group_resizes.isChecked() if hasattr(self, "chk_group_resizes") else False

#         widgets = [
#             "lbl_growth_x",
#             "combo_growth_p_w",
#             "combo_growth_dir_x",
#             "lbl_growth_y",
#             "combo_growth_p_h",
#             "combo_growth_dir_y",
#         ]

#         for name in widgets:
#             widget = getattr(self, name, None)
#             if widget:
#                 widget.setVisible(checked)



#     def apply_compact_right_panel_style(self):
#         """Компактний режим правої панелі: максимум 300 px і без горизонтального роз'їзду."""
#         if hasattr(self, "scroll_area"):
#             self.scroll_area.setFixedWidth(300)
#             self.scroll_area.setMinimumWidth(300)
#             self.scroll_area.setMaximumWidth(300)

#         widgets = []
#         if hasattr(self, "scroll_area") and self.scroll_area.widget():
#             widgets = self.scroll_area.widget().findChildren(QWidget)

#         for widget in widgets:
#             if isinstance(widget, QLabel):
#                 widget.setWordWrap(True)
#                 widget.setMaximumWidth(286)
#             elif isinstance(widget, QPushButton):
#                 widget.setMinimumHeight(24)
#                 widget.setMaximumHeight(30)
#                 widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
#             elif isinstance(widget, (QLineEdit, QComboBox)):
#                 widget.setMinimumHeight(22)
#                 widget.setMaximumHeight(26)
#                 widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
#             elif isinstance(widget, QListWidget):
#                 widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

#         for group in self.findChildren(QGroupBox):
#             group.setMaximumWidth(286)

#         self.setStyleSheet(self.styleSheet() + """
#         QScrollArea { border: 0px; }
#         QTabWidget::pane { border: 1px solid #444; padding: 2px; }
#         QTabBar::tab { padding: 3px 5px; min-width: 42px; font-size: 10px; }
#         QGroupBox {
#             margin-top: 8px;
#             padding-top: 8px;
#             font-size: 10px;
#         }
#         QLabel { font-size: 10px; }
#         QPushButton {
#             font-size: 10px;
#             padding: 3px 4px;
#             text-align: center;
#         }
#         QLineEdit, QComboBox {
#             font-size: 10px;
#             padding: 1px 3px;
#         }
#         QListWidget {
#             font-size: 10px;
#         }
#         QCheckBox {
#             font-size: 10px;
#             spacing: 3px;
#         }
#         """)

#     def setup_shortcuts(self):

#         # ---------- Файл ----------
#         QShortcut(QKeySequence("Ctrl+O"), self, self.open_dxf_from_dialog)
#         QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.doc.saveas(self.dxf_path))

#         # ---------- Історія ----------
#         QShortcut(QKeySequence("Ctrl+Z"), self, self.undo)
#         QShortcut(QKeySequence("Ctrl+Y"), self, self.redo)

#         # Альтернативний redo як в AutoCAD
#         QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.redo)

#         # ---------- Виділення ----------
#         QShortcut(QKeySequence("Ctrl+A"), self, self.select_all_entities)

#         # Зняти виділення
#         QShortcut(QKeySequence("Escape"), self, self.clear_selection)

#         # ---------- Видалення ----------
#         QShortcut(QKeySequence("Delete"), self, self.delete_entities_from_dxf)

#         # ---------- Перегляд ----------
#         QShortcut(QKeySequence("F"), self, self.zoom_extents)      # Fit All
#         QShortcut(QKeySequence("Home"), self, self.zoom_extents)

#         # ---------- Перетворення ----------
#         QShortcut(QKeySequence("Ctrl+R"), self,
#                 lambda: self.transform_selected_entities("ROT90"))

#         QShortcut(QKeySequence("Ctrl+Shift+R"), self,
#                 lambda: self.transform_selected_entities("ROT180"))

#         QShortcut(QKeySequence("Ctrl+M"), self,
#                 lambda: self.transform_selected_entities("MIRROR_H"))

#         # ---------- Групи ----------
#         QShortcut(QKeySequence("Ctrl+G"), self, self.create_parametric_group)

#         QShortcut(QKeySequence("Ctrl+Shift+G"), self,
#                 self.disband_parametric_group)

#         # ---------- Перерахунок ----------
#         QShortcut(QKeySequence("F5"), self,
#                 self.process_parametric_percentage_scale)

#         QShortcut(QKeySequence("F6"), self,
#                 self.preview_parametric_scale)

#         # ---------- Експорт ----------
#         QShortcut(QKeySequence("Ctrl+E"), self,
#                 self.export_new_dxf_with_dimensions)

#     def typical_rule_library(self):
#         return {
            
#             "Фіксовано": {
#                 "k_w": 0.0, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Рухається вправо": {
#                 "k_w": 1.0, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Рухається вліво": {
#                 "k_w": 1.0, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Рухається вгору": {
#                 "k_w": 0.0, "k_h": 1.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Центрувати по ширині": {
#                 "k_w": 0.5, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Центрувати по висоті": {
#                 "k_w": 0.0, "k_h": 0.5,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
            
#             "Правий край + ріст вгору": {
#                 "k_w": 1.0, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 1.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Верхній край + ріст вправо": {
#                 "k_w": 0.0, "k_h": 1.0,
#                 "growth_p_w": 1.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },

#             # "Лівий край + ріст вправо": {
#             #     "k_w": 0.0, "k_h": 0.0,
#             #     "growth_p_w": 1.0, "growth_p_h": 0.0,
#             #     "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#             #     "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
#             #     "link_x": "X = W", "link_y": "Y = H"
#             # },

#             # "Правий край + ріст вліво": {
#             #     "k_w": 1.0, "k_h": 0.0,
#             #     "growth_p_w": 1.0, "growth_p_h": 0.0,
#             #     "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
#             #     "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#             #     "link_x": "X = W", "link_y": "Y = H"
#             # },

#             # "Нижній край + ріст вгору": {
#             #     "k_w": 0.0, "k_h": 0.0,
#             #     "growth_p_w": 0.0, "growth_p_h": 1.0,
#             #     "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#             #     "shift_dir_x": "Вправо", "shift_dir_y": "Вниз",
#             #     "link_x": "X = W", "link_y": "Y = H"
#             # },

#             # "Верхній край + ріст вниз": {
#             #     "k_w": 0.0, "k_h": 1.0,
#             #     "growth_p_w": 0.0, "growth_p_h": 1.0,
#             #     "growth_dir_x": "Вправо", "growth_dir_y": "Вниз",
#             #     "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#             #     "link_x": "X = W", "link_y": "Y = H"
#             # },

#             "1/3 ширини": {
#                 "k_w": 0.3333, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },

#             "2/3 ширини": {
#                 "k_w": 0.6667, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
            
#             "Розтягнути вправо": {
#                 "k_w": 0.0, "k_h": 0.0,
#                 "growth_p_w": 1.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },
#             "Розтягнути вгору": {
#                 "k_w": 0.0, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 1.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },

#             "Розтягнути вліво": {
#                 "k_w": 0.0, "k_h": 0.0,
#                 "growth_p_w": 1.0, "growth_p_h": 0.0,
#                 "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
#                 "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
#                 "link_x": "X = W", "link_y": "Y = H"
#             },

#             "Розтягнути вниз": {
#                 "k_w": 0.0, "k_h": 0.0,
#                 "growth_p_w": 0.0, "growth_p_h": 1.0,
#                 "growth_dir_x": "Вправо", "growth_dir_y": "Вниз",
#                 "shift_dir_x": "Вправо", "shift_dir_y": "Вниз",
#                 "link_x": "X = W", "link_y": "Y = H"
#             }
#         }

#     def apply_rule_to_group(self, group, rule_name):
#         rule = self.typical_rule_library().get(rule_name)
#         if not rule:
#             return
#         group.update(rule)

#     def apply_selected_rule_to_group(self):
#         selected = self.group_list_widget.selectedItems()
#         if not selected:
#             return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.apply_rule_to_group(self.parametric_groups[idx], self.combo_rule_library.currentText())
#         self.save_project_config()
#         self.on_group_selection_changed()
#         self.update_viewer()

#     def parse_numeric_text(self, value):
#         if value is None:
#             return None
#         text = str(value).strip()
#         if not text:
#             return None
#         text = text.replace(",", ".")
#         match = re.search(r"-?\d+(?:\.\d+)?", text)
#         return float(match.group(0)) if match else None

#     def format_dimension_value(self, value):
#         if value is None:
#             return ""
#         value = float(value)
#         return str(int(value)) if abs(value - int(value)) < 0.001 else f"{value:.2f}".rstrip("0").rstrip(".")

#     def get_dxf_bounds_dimensions(self):
#         min_x, max_x = float("inf"), float("-inf")
#         min_y, max_y = float("inf"), float("-inf")
#         for entity in self.doc.modelspace():
#             tp = entity.dxftype()
#             if tp in ("CIRCLE", "ARC"):
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 min_x = min(min_x, cx - r)
#                 max_x = max(max_x, cx + r)
#                 min_y = min(min_y, cy - r)
#                 max_y = max(max_y, cy + r)
#             elif tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 min_x = min(min_x, x1, x2)
#                 max_x = max(max_x, x1, x2)
#                 min_y = min(min_y, y1, y2)
#                 max_y = max(max_y, y1, y2)
#         if min_x == float("inf") or min_y == float("inf"):
#             return None, None
#         return max_x - min_x, max_y - min_y


#     def update_dimension_inputs_from_meta(self):
#         """
#         Оновлює поля розмірів тільки з project_meta.
#         project_meta наповнюється з MSSQL, не з JSON/_folder_params.
#         """
#         source_w = self.project_meta.get("source_width")
#         source_h = self.project_meta.get("source_height")

#         if source_w is None or source_h is None:
#             source_w, source_h = self.get_dxf_bounds_dimensions()
#             self.project_meta["source_width"] = source_w
#             self.project_meta["source_height"] = source_h

#         target_w = self.project_meta.get("target_width") or source_w
#         target_h = self.project_meta.get("target_height") or source_h

#         self.project_meta["target_width"] = target_w
#         self.project_meta["target_height"] = target_h

#         self.input_current_width.setText(self.format_dimension_value(source_w))
#         self.input_current_height.setText(self.format_dimension_value(source_h))
#         self.input_target_width.setText(self.format_dimension_value(target_w))
#         self.input_target_height.setText(self.format_dimension_value(target_h))

#         self.sync_text_inputs_from_meta()
#         self.sync_opening_inputs_from_meta()
#         self.sync_file_growth_axis_combo()
#         self.update_file_status_panel()

#     def update_file_status_panel(self):
#         if not hasattr(self, "lbl_file_status_source"):
#             return
#         source_w = self.format_dimension_value(self.project_meta.get("source_width"))
#         source_h = self.format_dimension_value(self.project_meta.get("source_height"))
#         target_w = self.format_dimension_value(self.project_meta.get("target_width"))
#         target_h = self.format_dimension_value(self.project_meta.get("target_height"))
#         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
#         target_opening = self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)
#         opening_names = {"left": "Ліве", "right": "Праве"}
#         link_x, link_y = self.link_pair_for_mode() if hasattr(self, "link_pair_for_mode") else ("X = W", "Y = H")
#         db_state = "online" if getattr(getattr(self, "db", None), "available", False) else "offline"
#         user = self.current_user.get("username") if getattr(self, "current_user", None) else "-"
#         self.lbl_file_status_source.setText(f"Початковий: {source_w} x {source_h}")
#         self.lbl_file_status_target.setText(f"Цільовий: {target_w} x {target_h}")
#         self.lbl_file_status_opening.setText(
#             f"Відкривання: {opening_names.get(source_opening, source_opening)} -> {opening_names.get(target_opening, target_opening)}"
#         )
#         self.lbl_file_status_axis.setText(f"Осі: {link_x}, {link_y}")
#         model_id = getattr(self, "current_door_model_id", None) or "-"
#         file_id = getattr(self, "current_project_file_id", None) or "-"
#         self.lbl_file_status_db.setText(f"БД: {db_state} | користувач: {user} | модель: {model_id} | файл: {file_id}")


#     def prompt_source_dimensions_on_open(self):
#         """
#         Початкові розміри і відкривання беруться з DoorModels.

#         Якщо DoorModel для папки вже є в БД — нічого не питаємо.
#         Якщо в БД ще немає початкових розмірів — питаємо один раз і записуємо в DoorModels.
#         JSON тут не використовується.
#         """
#         if getattr(self, "db", None) and getattr(self.db, "available", False):
#             if not getattr(self, "current_door_model_id", None):
#                 model_id = self.db.find_door_model_by_folder(self.project_dir)
#                 if model_id:
#                     self.current_door_model_id = model_id

#             if getattr(self, "current_door_model_id", None):
#                 model_data = self.db.load_door_model(self.current_door_model_id)
#                 if model_data:
#                     meta = model_data.get("meta") or {}
#                     source_w = meta.get("source_width")
#                     source_h = meta.get("source_height")

#                     if source_w is not None and source_h is not None:
#                         opening = meta.get("source_door_opening") or "left"

#                         self.project_meta["source_width"] = source_w
#                         self.project_meta["source_height"] = source_h
#                         self.project_meta["target_width"] = self.project_meta.get("target_width") or source_w
#                         self.project_meta["target_height"] = self.project_meta.get("target_height") or source_h
#                         self.project_meta["source_door_opening"] = opening
#                         self.project_meta["target_door_opening"] = self.project_meta.get("target_door_opening") or opening
#                         self.project_meta["door_opening"] = self.project_meta.get("door_opening") or opening
#                         self.project_meta["growth_axis"] = meta.get("growth_axis") or self.project_meta.get("growth_axis") or "both"
#                         self.project_meta["axis_link_mode"] = meta.get("axis_link_mode") or self.project_meta.get("axis_link_mode") or "normal"
#                         self.project_meta["link_x"] = meta.get("link_x") or self.project_meta.get("link_x") or "X = W"
#                         self.project_meta["link_y"] = meta.get("link_y") or self.project_meta.get("link_y") or "Y = H"

#                         self.update_dimension_inputs_from_meta()
#                         return False

#         guessed_w, guessed_h = self.get_dxf_bounds_dimensions()
#         source_w = self.project_meta.get("source_width") or guessed_w
#         source_h = self.project_meta.get("source_height") or guessed_h

#         default_text = ""
#         if source_w is not None and source_h is not None:
#             default_text = f"{self.format_dimension_value(source_w)} x {self.format_dimension_value(source_h)}"

#         text, ok = QInputDialog.getText(
#             self,
#             "Початковий розмір моделі",
#             "Введіть початкову ширину і висоту для всієї папки (W x H):",
#             text=default_text
#         )
#         if not ok:
#             return False

#         values = [
#             float(value.replace(",", "."))
#             for value in re.findall(r"-?\d+(?:[,.]\d+)?", text)
#         ]

#         if len(values) < 2:
#             QMessageBox.warning(
#                 self,
#                 "Початковий розмір",
#                 "Введіть два числа, наприклад: 860 x 2040"
#             )
#             return False

#         source_w, source_h = values[0], values[1]

#         opening_text, opening_ok = QInputDialog.getItem(
#             self,
#             "Початкове відкривання",
#             "Яке відкривання у файлах цієї папки?",
#             ["Ліве", "Праве"],
#             0,
#             False
#         )

#         opening = "right" if opening_ok and "Прав" in opening_text else "left"

#         self.project_meta["source_width"] = source_w
#         self.project_meta["source_height"] = source_h
#         self.project_meta["target_width"] = source_w
#         self.project_meta["target_height"] = source_h
#         self.project_meta["source_door_opening"] = opening
#         self.project_meta["target_door_opening"] = opening
#         self.project_meta["door_opening"] = opening

#         if getattr(self, "db", None) and getattr(self.db, "available", False) and self.current_user_id():
#             door_model_id = self.db.get_or_create_door_model(
#                 folder_path=self.project_dir,
#                 model_name=os.path.basename(self.project_dir),
#                 source_width=source_w,
#                 source_height=source_h,
#                 source_door_opening=opening,
#                 user_id=self.current_user_id(),
#                 growth_axis=self.project_meta.get("growth_axis", "both"),
#                 axis_link_mode=self.project_meta.get("axis_link_mode", "normal"),
#                 link_x=self.project_meta.get("link_x", "X = W"),
#                 link_y=self.project_meta.get("link_y", "Y = H"),
#             )

#             if door_model_id:
#                 self.current_door_model_id = door_model_id
#                 self.register_current_folder_model(show_errors=False)

#         self.update_dimension_inputs_from_meta()
#         self.save_project_config()
#         return True


#     def remember_source_dimensions(self):
#         source_w = self.parse_numeric_text(self.input_current_width.text())
#         source_h = self.parse_numeric_text(self.input_current_height.text())

#         if source_w is None or source_h is None:
#             source_w, source_h = self.get_dxf_bounds_dimensions()

#         self.project_meta["source_width"] = source_w
#         self.project_meta["source_height"] = source_h

#         target_w = self.parse_numeric_text(self.input_target_width.text())
#         target_h = self.parse_numeric_text(self.input_target_height.text())
#         self.project_meta["target_width"] = target_w if target_w is not None else source_w
#         self.project_meta["target_height"] = target_h if target_h is not None else source_h

#         if getattr(self, "db", None) and getattr(self.db, "available", False) and self.current_user_id():
#             if not getattr(self, "current_door_model_id", None):
#                 self.current_door_model_id = self.db.get_or_create_door_model(
#                     folder_path=self.project_dir,
#                     model_name=os.path.basename(self.project_dir),
#                     source_width=source_w,
#                     source_height=source_h,
#                     source_door_opening=self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening") or "left",
#                     user_id=self.current_user_id(),
#                     growth_axis=self.project_meta.get("growth_axis", "both"),
#                     axis_link_mode=self.project_meta.get("axis_link_mode", "normal"),
#                     link_x=self.project_meta.get("link_x", "X = W"),
#                     link_y=self.project_meta.get("link_y", "Y = H"),
#                 )

#             if getattr(self, "current_door_model_id", None):
#                 self.db.update_door_model_from_meta(
#                     self.current_door_model_id,
#                     self.project_meta,
#                     self.current_user_id(),
#                 )

#         self.save_project_config()
#         self.update_dimension_inputs_from_meta()
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Початкові розміри збережено в БД.</font>")

#     def load_block_filter_list(self):
#         if not hasattr(self, "block_filter_list"):
#             return
#         self.block_filter_list.blockSignals(True)
#         self.block_filter_list.clear()
#         valid_names = set()
#         for group in self.parametric_groups:
#             name = group.get("name", "")
#             key = self.get_group_key(group)
#             valid_names.add(key)
#             keep = self.block_keep_state.get(key, True)
#             self.block_keep_state[key] = keep
#             item = QListWidgetItem(f"{name} ({len(group['handles'])} об.)")
#             item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
#             item.setCheckState(Qt.CheckState.Checked if keep else Qt.CheckState.Unchecked)
#             item.setData(Qt.ItemDataRole.UserRole, key)
#             self.block_filter_list.addItem(item)
#         for key in list(self.block_keep_state):
#             if key not in valid_names:
#                 del self.block_keep_state[key]
#         self.block_filter_list.blockSignals(False)

#     def on_block_keep_state_changed(self, item):
#         self.record_action_snapshot()
#         key = item.data(Qt.ItemDataRole.UserRole)
#         self.block_keep_state[key] = item.checkState() == Qt.CheckState.Checked
#         self.save_project_config()

#     def set_text_panel_expanded(self, expanded):
#         layout = getattr(self, "text_box_layout", None)
#         if not layout:
#             return
#         for index in range(layout.count()):
#             item = layout.itemAt(index)
#             widget = item.widget()
#             child_layout = item.layout()
#             if widget:
#                 widget.setVisible(expanded)
#             elif child_layout:
#                 for child_index in range(child_layout.count()):
#                     child_item = child_layout.itemAt(child_index)
#                     child_widget = child_item.widget()
#                     if child_widget:
#                         child_widget.setVisible(expanded)

#     def get_text_settings(self):
#         settings = self.default_text_settings()
#         settings.update(self.project_meta.get("door_text", {}))
#         self.project_meta["door_text"] = settings
#         if settings["enabled"] and hasattr(self, "check_door_text_enabled"):
#             self.check_door_text_enabled.blockSignals(True)
#             self.check_door_text_enabled.setChecked(True)
#             self.check_door_text_enabled.blockSignals(False)
#         return settings

#     def text_box_width(self, settings):
#         return max(float(settings.get("width_factor", 120.0)), 1.0)

#     def text_box_height(self, settings):
#         return max(float(settings.get("height", 30.0)), 1.0)

#     def text_display_value(self, text):
#         return str(text).strip()

#     def add_centered_text_preview(self, parent_item, text, box_w, box_h, font_name):
#         if not text:
#             return
#         text_item = QGraphicsSimpleTextItem(text, parent_item)
#         font = text_item.font()
#         if font_name and font_name.upper() != "STANDARD":
#             font.setFamily(font_name)
#         font.setPointSizeF(100.0)
#         text_item.setFont(font)
#         text_item.setBrush(QBrush(QColor(255, 255, 255)))
#         text_item.setZValue(10)
#         text_item.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
#         br = text_item.boundingRect()
#         if br.width() <= 0 or br.height() <= 0:
#             return
#         scale = min((box_w * 0.9) / br.width(), (box_h * 0.75) / br.height())
#         scale = max(min(scale, 10.0), 0.01)
#         text_item.setScale(scale)
#         text_item.setPos(
#             (box_w - br.width() * scale) * 0.5,
#             (box_h - br.height() * scale) * 0.5
#         )

#     def sync_text_inputs_from_meta(self):
#         if not hasattr(self, "input_door_text"):
#             return
#         settings = self.get_text_settings()
#         widgets = [
#             self.check_door_text_enabled,
#             self.input_door_text,
#             self.input_text_x,
#             self.input_text_y,
#             self.input_text_height,
#             self.input_text_width_factor,
#             self.input_text_rotation,
#             self.combo_text_font
#         ]
#         for widget in widgets:
#             widget.blockSignals(True)
#         self.check_door_text_enabled.setChecked(bool(settings.get("enabled")))
#         self.input_door_text.setText(str(settings.get("text", "")))
#         self.input_text_x.setText(self.format_dimension_value(settings.get("x", 0.0)))
#         self.input_text_y.setText(self.format_dimension_value(settings.get("y", 0.0)))
#         self.input_text_height.setText(self.format_dimension_value(settings.get("height", 30.0)))
#         self.input_text_width_factor.setText(self.format_dimension_value(settings.get("width_factor", 120.0)))
#         self.input_text_rotation.setText(self.format_dimension_value(settings.get("rotation", 0.0)))
#         self.combo_text_font.setCurrentText(str(settings.get("font", "STANDARD")))
#         for widget in widgets:
#             widget.blockSignals(False)
#         if hasattr(self, "text_group"):
#             should_open = bool(
#                 settings.get("enabled") or
#                 str(settings.get("text", "")).strip() or
#                 settings.get("handle")
#             )
#             self.text_group.setChecked(should_open)
#             self.set_text_panel_expanded(should_open)

#     def collect_text_settings_from_inputs(self):
#         if not hasattr(self, "input_door_text"):
#             return self.get_text_settings()
#         settings = self.get_text_settings()
#         settings["text"] = self.input_door_text.text()
#         settings["enabled"] = self.check_door_text_enabled.isChecked()
#         for key, widget, fallback in (
#             ("x", self.input_text_x, 0.0),
#             ("y", self.input_text_y, 0.0),
#             ("height", self.input_text_height, 30.0),
#             ("width_factor", self.input_text_width_factor, 120.0),
#             ("rotation", self.input_text_rotation, 0.0),
#         ):
#             value = self.parse_numeric_text(widget.text())
#             settings[key] = fallback if value is None else value
#         settings["font"] = self.combo_text_font.currentText().strip() or "STANDARD"
#         self.project_meta["door_text"] = settings
#         return settings

#     def on_text_settings_changed(self, *args):
#         self.collect_text_settings_from_inputs()
#         self.save_project_config()

#     def apply_door_text_from_ui(self):
#         self.record_action_snapshot()
#         settings = self.collect_text_settings_from_inputs()
#         settings["enabled"] = True
#         self.project_meta["door_text"] = settings
#         self.check_door_text_enabled.blockSignals(True)
#         self.check_door_text_enabled.setChecked(True)
#         self.check_door_text_enabled.blockSignals(False)
#         self.apply_door_text_to_doc()
#         self.doc.saveas(self.dxf_path)
#         self.save_project_config()
#         self.save_original_geometries()
#         self.load_entities_into_list()
#         self.update_viewer()
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Текст оновлено на DXF.</font>")

#     def remove_door_text_block(self):
#         self.record_action_snapshot()
#         settings = self.get_text_settings()
#         handle = settings.get("handle")
#         if handle:
#             self.selected_handles.discard(handle)
#             for group in self.parametric_groups:
#                 group["handles"].discard(handle)
#             self.parametric_groups = [g for g in self.parametric_groups if g.get("handles")]
#         self.remove_managed_text_entity(self.doc, settings)
#         settings.update({
#             "enabled": False,
#             "text": "",
#             "handle": None
#         })
#         self.project_meta["door_text"] = settings
#         self.check_door_text_enabled.blockSignals(True)
#         self.check_door_text_enabled.setChecked(False)
#         self.check_door_text_enabled.blockSignals(False)
#         self.input_door_text.setText("")
#         self.doc.saveas(self.dxf_path)
#         self.save_original_geometries()
#         self.save_project_config()
#         self.load_entities_into_list()
#         self.load_groups_into_list()
#         self.update_viewer()
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Текстовий блок прибрано.</font>")

#     def get_non_text_dxf_bounds(self):
#         min_x, min_y = float("inf"), float("inf")
#         max_x, max_y = float("-inf"), float("-inf")
#         for entity in self.doc.modelspace():
#             tp = entity.dxftype()
#             if tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 min_x = min(min_x, x1, x2)
#                 max_x = max(max_x, x1, x2)
#                 min_y = min(min_y, y1, y2)
#                 max_y = max(max_y, y1, y2)
#             elif tp in ("CIRCLE", "ARC"):
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 min_x = min(min_x, cx - r)
#                 max_x = max(max_x, cx + r)
#                 min_y = min(min_y, cy - r)
#                 max_y = max(max_y, cy + r)
#         if min_x == float("inf"):
#             return None, None, None, None
#         return min_x, min_y, max_x, max_y

#     def align_text_box_to_door(self, dimension):
#         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
#         if min_x is None:
#             self.lbl_status_calc.setText("<font color='red'>Не знайдено геометрію дверей для вирівнювання.</font>")
#             return
#         self.record_action_snapshot()
#         settings = self.collect_text_settings_from_inputs()
#         settings["enabled"] = True
#         if dimension == "width":
#             box_w = self.text_box_width(settings)
#             settings["x"] = min_x + ((max_x - min_x) - box_w) * 0.5
#             message = "Текстову рамку виставлено по центру ширини полотна."
#         else:
#             box_h = self.text_box_height(settings)
#             settings["y"] = min_y + ((max_y - min_y) - box_h) * 0.5
#             message = "Текстову рамку виставлено по центру висоти полотна."
#         self.project_meta["door_text"] = settings
#         self.apply_door_text_to_doc()
#         self.doc.saveas(self.dxf_path)
#         self.save_original_geometries()
#         self.save_project_config()
#         self.sync_text_inputs_from_meta()
#         self.load_entities_into_list()
#         self.sync_list_from_handles()
#         self.update_viewer()
#         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>{message}</font>")

#     def place_empty_door_text_block(self):
#         self.record_action_snapshot()
#         settings = self.collect_text_settings_from_inputs()
#         settings["enabled"] = True
#         if not str(settings.get("text", "")).strip():
#             settings["text"] = ""
#         if settings.get("x", 0.0) == 0.0 and settings.get("y", 0.0) == 0.0:
#             min_x, min_y, max_x, max_y = self.get_dxf_bounds()
#             if min_x is not None:
#                 settings["x"] = min_x + (max_x - min_x) * 0.5
#                 settings["y"] = min_y + (max_y - min_y) * 0.5
#         self.project_meta["door_text"] = settings
#         self.sync_text_inputs_from_meta()
#         entity = self.apply_door_text_to_doc()
#         if entity is not None:
#             self.selected_handles = {entity.dxf.handle}
#         self.doc.saveas(self.dxf_path)
#         self.save_original_geometries()
#         self.load_entities_into_list()
#         self.sync_list_from_handles()
#         self.save_project_config()
#         self.update_viewer()
#         self.lbl_status_calc.setText("<font color='#4fc3f7'>Текстовий блок можна перетягнути мишкою.</font>")

#     def on_door_text_item_moved(self, item):
#         self.record_action_snapshot()
#         settings = self.get_text_settings()
#         settings["x"] = float(item.pos().x())
#         settings["y"] = float(-item.pos().y() - float(settings.get("height", 30.0)))
#         settings["enabled"] = True
#         self.project_meta["door_text"] = settings
#         handle = settings.get("handle")
#         if handle and handle in self.doc.entitydb:
#             self.doc.entitydb[handle].dxf.insert = (settings["x"], settings["y"], 0.0)
#             self.doc.saveas(self.dxf_path)
#             self.selected_handles = {handle}
#         self.sync_text_inputs_from_meta()
#         self.save_project_config()
#         self.load_entities_into_list()
#         self.sync_list_from_handles()

#     def on_door_text_box_moved(self, item):
#         self.record_action_snapshot()
#         settings = self.get_text_settings()
#         settings["x"] = float(item.pos().x() + item.rect().x())
#         settings["y"] = float(-(item.pos().y() + item.rect().y() + item.rect().height()))
#         settings["enabled"] = True
#         self.project_meta["door_text"] = settings
#         self.apply_door_text_to_doc()
#         self.doc.saveas(self.dxf_path)
#         handle = settings.get("handle")
#         if handle:
#             self.selected_handles = {handle}
#         self.sync_text_inputs_from_meta()
#         self.save_project_config()
#         self.load_entities_into_list()
#         self.sync_list_from_handles()
#         self.update_viewer()

#     def sync_opening_inputs_from_meta(self):
#         if not hasattr(self, "combo_door_opening"):
#             return
#         opening = self.project_meta.get("door_opening", "left")
#         self.combo_door_opening.blockSignals(True)
#         self.combo_door_opening.setCurrentText("Праве" if opening == "right" else "Ліве")
#         self.combo_door_opening.blockSignals(False)

#     def on_door_opening_changed(self, text):
#         self.record_action_snapshot()
#         self.project_meta["door_opening"] = "right" if "Прав" in text else "left"
#         self.save_project_config()

#     def sync_opening_inputs_from_meta(self):
#         if not hasattr(self, "combo_door_opening"):
#             return
#         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
#         target_opening = self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)
#         if hasattr(self, "combo_source_door_opening"):
#             self.combo_source_door_opening.blockSignals(True)
#             self.combo_source_door_opening.setCurrentText("Праве" if source_opening == "right" else "Ліве")
#             self.combo_source_door_opening.blockSignals(False)
#         self.combo_door_opening.blockSignals(True)
#         self.combo_door_opening.setCurrentText("Праве" if target_opening == "right" else "Ліве")
#         self.combo_door_opening.blockSignals(False)


#     def on_source_door_opening_changed(self, text):
#         self.record_action_snapshot()
#         self.project_meta["source_door_opening"] = "right" if "Прав" in text else "left"
#         if not self.project_meta.get("target_door_opening"):
#             self.project_meta["target_door_opening"] = self.project_meta["source_door_opening"]
#         self.save_project_config()
#         self.update_file_status_panel()

#     def on_door_opening_changed(self, text):
#         self.record_action_snapshot()
#         self.project_meta["target_door_opening"] = "right" if "Прав" in text else "left"
#         self.project_meta["door_opening"] = self.project_meta["target_door_opening"]
#         self.save_project_config()
#         self.update_file_status_panel()

#     def get_dxf_bounds(self, doc=None):
#         doc = doc or self.doc
#         min_x, min_y = float("inf"), float("inf")
#         max_x, max_y = float("-inf"), float("-inf")
#         for entity in doc.modelspace():
#             tp = entity.dxftype()
#             if tp in ("CIRCLE", "ARC"):
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 min_x = min(min_x, cx - r)
#                 max_x = max(max_x, cx + r)
#                 min_y = min(min_y, cy - r)
#                 max_y = max(max_y, cy + r)
#             elif tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 min_x = min(min_x, x1, x2)
#                 max_x = max(max_x, x1, x2)
#                 min_y = min(min_y, y1, y2)
#                 max_y = max(max_y, y1, y2)
#             elif tp == "TEXT":
#                 settings = self.get_text_settings()
#                 if settings.get("handle") == entity.dxf.handle:
#                     x = float(settings.get("x", 0.0))
#                     y = float(settings.get("y", 0.0))
#                     w = self.text_box_width(settings)
#                     h = self.text_box_height(settings)
#                 else:
#                     x, y, _ = entity.dxf.insert
#                     h = float(entity.dxf.height)
#                     w = max(len(str(entity.dxf.text).strip()), 1) * h * 0.6 * float(getattr(entity.dxf, "width", 1.0))
#                 min_x = min(min_x, x)
#                 max_x = max(max_x, x + w)
#                 min_y = min(min_y, y)
#                 max_y = max(max_y, y + h)
#         if min_x == float("inf"):
#             return None, None, None, None
#         return min_x, min_y, max_x, max_y

#     def entity_bbox(self, entity):
#         tp = entity.dxftype()
#         if tp in ("CIRCLE", "ARC"):
#             cx, cy, _ = entity.dxf.center
#             r = entity.dxf.radius
#             return (cx - r, cy - r, cx + r, cy + r)
#         if tp == "LINE":
#             x1, y1, _ = entity.dxf.start
#             x2, y2, _ = entity.dxf.end
#             return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
#         if tp in ("TEXT", "MTEXT"):
#             settings = self.get_text_settings()
#             if settings.get("handle") == entity.dxf.handle:
#                 x = float(settings.get("x", 0.0))
#                 y = float(settings.get("y", 0.0))
#                 w = self.text_box_width(settings)
#                 h = self.text_box_height(settings)
#             else:
#                 x, y, _ = entity.dxf.insert
#                 h = float(entity.dxf.height)
#                 w = max(len(str(entity.dxf.text).strip()), 1) * h * 0.6 * float(getattr(entity.dxf, "width", 1.0))
#             return (x, y, x + w, y + h)
#         return None

#     def transform_managed_text_settings(self, mode, cx, cy):
#         settings = self.get_text_settings()
#         handle = settings.get("handle")
#         if not handle or handle not in self.selected_handles:
#             return
#         box_w = self.text_box_width(settings)
#         box_h = self.text_box_height(settings)
#         center_x = float(settings.get("x", 0.0)) + box_w * 0.5
#         center_y = float(settings.get("y", 0.0)) + box_h * 0.5
#         dx = center_x - cx
#         dy = center_y - cy
#         rotation = float(settings.get("rotation", 0.0))

#         if mode == "ROT90":
#             center_x, center_y = cx - dy, cy + dx
#             rotation += 90.0
#         elif mode == "ROT180":
#             center_x, center_y = cx - dx, cy - dy
#             rotation += 180.0
#         elif mode == "ROT270":
#             center_x, center_y = cx + dy, cy - dx
#             rotation += 270.0
#         elif mode == "MIRROR_H":
#             center_x = 2 * cx - center_x
#             rotation = 180.0 - rotation
#         elif mode == "MIRROR_V":
#             center_y = 2 * cy - center_y
#             rotation = -rotation
#         else:
#             return

#         settings["x"] = center_x - box_w * 0.5
#         settings["y"] = center_y - box_h * 0.5
#         settings["rotation"] = rotation % 360.0
#         self.project_meta["door_text"] = settings
#         self.apply_door_text_to_doc()

#     def mirror_entity_horizontally(self, entity, axis_x):
#         tp = entity.dxftype()
#         if tp == "LINE":
#             sx, sy, sz = entity.dxf.start
#             ex, ey, ez = entity.dxf.end
#             entity.dxf.start = (2 * axis_x - sx, sy, sz)
#             entity.dxf.end = (2 * axis_x - ex, ey, ez)
#         elif tp in ("CIRCLE", "ARC"):
#             cx, cy, cz = entity.dxf.center
#             entity.dxf.center = (2 * axis_x - cx, cy, cz)
#             if tp == "ARC":
#                 old_start = float(entity.dxf.start_angle)
#                 old_end = float(entity.dxf.end_angle)
#                 entity.dxf.start_angle = (180.0 - old_end) % 360.0
#                 entity.dxf.end_angle = (180.0 - old_start) % 360.0
#         elif tp == "TEXT":
#             x, y, z = entity.dxf.insert
#             entity.dxf.insert = (2 * axis_x - x, y, z)
#             entity.dxf.rotation = (180.0 - float(getattr(entity.dxf, "rotation", 0.0))) % 360.0

#     def mirror_entity_vertically(self, entity, axis_y):
#         tp = entity.dxftype()
#         if tp == "LINE":
#             sx, sy, sz = entity.dxf.start
#             ex, ey, ez = entity.dxf.end
#             entity.dxf.start = (sx, 2 * axis_y - sy, sz)
#             entity.dxf.end = (ex, 2 * axis_y - ey, ez)
#         elif tp in ("CIRCLE", "ARC"):
#             cx, cy, cz = entity.dxf.center
#             entity.dxf.center = (cx, 2 * axis_y - cy, cz)
#             if tp == "ARC":
#                 old_start = float(entity.dxf.start_angle)
#                 old_end = float(entity.dxf.end_angle)
#                 entity.dxf.start_angle = (-old_end) % 360.0
#                 entity.dxf.end_angle = (-old_start) % 360.0
#         elif tp == "TEXT":
#             x, y, z = entity.dxf.insert
#             entity.dxf.insert = (x, 2 * axis_y - y, z)
#             entity.dxf.rotation = (-float(getattr(entity.dxf, "rotation", 0.0))) % 360.0


#     def flip_x_direction(self, direction):
#         if direction == "Вправо":
#             return "Вліво"
#         if direction == "Вліво":
#             return "Вправо"
#         return direction
    
#     def flip_y_direction(self, direction):
#         if direction == "Вгору":
#             return "Вниз"
#         if direction == "Вниз":
#             return "Вгору"
#         return direction

#     def mirror_door_opening(self):
#         min_x, min_y, max_x, max_y = self.get_dxf_bounds()
#         if min_x is None:
#             return

#         self.record_action_snapshot()

#         link_x, link_y = self.link_pair_for_mode()
#         mirror_by_y = link_y == "Y = W"

#         axis_x = (min_x + max_x) * 0.5
#         axis_y = (min_y + max_y) * 0.5

#         for entity in self.doc.modelspace():
#             tp = entity.dxftype()

#             if tp == "LINE":
#                 sx, sy, sz = entity.dxf.start
#                 ex, ey, ez = entity.dxf.end

#                 if mirror_by_y:
#                     entity.dxf.start = (sx, 2 * axis_y - sy, sz)
#                     entity.dxf.end = (ex, 2 * axis_y - ey, ez)
#                 else:
#                     entity.dxf.start = (2 * axis_x - sx, sy, sz)
#                     entity.dxf.end = (2 * axis_x - ex, ey, ez)

#             elif tp in ("CIRCLE", "ARC"):
#                 cx, cy, cz = entity.dxf.center

#                 if mirror_by_y:
#                     entity.dxf.center = (cx, 2 * axis_y - cy, cz)

#                     if tp == "ARC":
#                         old_start = float(entity.dxf.start_angle)
#                         old_end = float(entity.dxf.end_angle)
#                         entity.dxf.start_angle = (-old_end) % 360.0
#                         entity.dxf.end_angle = (-old_start) % 360.0

#                 else:
#                     entity.dxf.center = (2 * axis_x - cx, cy, cz)

#                     if tp == "ARC":
#                         old_start = float(entity.dxf.start_angle)
#                         old_end = float(entity.dxf.end_angle)
#                         entity.dxf.start_angle = (180.0 - old_end) % 360.0
#                         entity.dxf.end_angle = (180.0 - old_start) % 360.0

#             elif tp == "TEXT":
#                 x, y, z = entity.dxf.insert

#                 if mirror_by_y:
#                     entity.dxf.insert = (x, 2 * axis_y - y, z)
#                 else:
#                     entity.dxf.insert = (2 * axis_x - x, y, z)

#                 entity.dxf.rotation = float(getattr(entity.dxf, "rotation", 0.0))

#         settings = self.get_text_settings()

#         if mirror_by_y:
#             settings["y"] = 2 * axis_y - float(settings.get("y", 0.0))
#         else:
#             settings["x"] = 2 * axis_x - (
#                 float(settings.get("x", 0.0)) + self.text_box_width(settings)
#             )

#         self.project_meta["door_text"] = settings
#         self.apply_door_text_to_doc()

#         for group in self.parametric_groups:
#             if mirror_by_y:
#                 group["growth_dir_y"] = self.flip_y_direction(
#                     group.get("growth_dir_y", "Вгору")
#                 )
#                 group["shift_dir_y"] = self.flip_y_direction(
#                     group.get("shift_dir_y", "Вгору")
#                 )
#             else:
#                 group["growth_dir_x"] = self.flip_x_direction(
#                     group.get("growth_dir_x", "Вправо")
#                 )
#                 group["shift_dir_x"] = self.flip_x_direction(
#                     group.get("shift_dir_x", "Вправо")
#                 )

#         self.project_meta["door_opening"] = (
#             "right" if self.project_meta.get("door_opening") != "right" else "left"
#         )
#         self.project_meta["target_door_opening"] = self.project_meta["door_opening"]

#         self.doc.saveas(self.dxf_path)
#         self.save_original_geometries()
#         self.apply_axis_link_mode_to_groups()
#         self.save_project_config()
#         self.sync_opening_inputs_from_meta()
#         self.sync_text_inputs_from_meta()
#         self.sync_link_combos_from_file_mode()
#         self.load_entities_into_list()
#         self.update_viewer()
#         self.update_file_status_panel()

#         self.lbl_status_calc.setText(
#             "<font color='#a5d6a7'>Відкривання дзеркально змінено.</font>"
#         )

#     def group_original_bbox(self, group):
#         min_x, min_y = float("inf"), float("inf")
#         max_x, max_y = float("-inf"), float("-inf")
#         for handle in group.get("handles", set()):
#             orig = self.original_geometries.get(handle)
#             if not orig:
#                 continue
#             if orig["type"] in ("CIRCLE", "ARC"):
#                 cx, cy, _ = orig["center"]
#                 r = orig["radius"]
#                 min_x = min(min_x, cx - r)
#                 max_x = max(max_x, cx + r)
#                 min_y = min(min_y, cy - r)
#                 max_y = max(max_y, cy + r)
#             elif orig["type"] == "LINE":
#                 sx, sy, _ = orig["start"]
#                 ex, ey, _ = orig["end"]
#                 min_x = min(min_x, sx, ex)
#                 max_x = max(max_x, sx, ex)
#                 min_y = min(min_y, sy, ey)
#                 max_y = max(max_y, sy, ey)
#             elif orig["type"] == "TEXT":
#                 x, y, _ = orig["insert"]
#                 h = float(orig["height"])
#                 w = max(len(str(orig.get("text", "")).strip()), 1) * h * 0.6 * float(orig.get("width", 1.0))
#                 min_x = min(min_x, x)
#                 max_x = max(max_x, x + w)
#                 min_y = min(min_y, y)
#                 max_y = max(max_y, y + h)
#         if min_x == float("inf"):
#             return None
#         return (min_x, min_y, max_x, max_y)

#     def simulated_group_bbox(self, group, cur_w, cur_h, target_w, target_h):
#         bbox = self.group_original_bbox(group)
#         if not bbox:
#             return None
#         min_x, min_y, max_x, max_y = bbox
#         delta_w = target_w - cur_w
#         delta_h = target_h - cur_h
#         shift_v, growth_v = ParametricEngine.get_transform(delta_w, delta_h, group)
#         min_x += shift_v[0]
#         max_x += shift_v[0]
#         min_y += shift_v[1]
#         max_y += shift_v[1]

#         if group.get("growth_dir_x", "Центр") == "Вправо":
#             max_x += growth_v[0]
#         elif group.get("growth_dir_x", "Центр") == "Вліво":
#             min_x -= growth_v[0]
#         else:
#             min_x -= growth_v[0] * 0.5
#             max_x += growth_v[0] * 0.5

#         if group.get("growth_dir_y", "Центр") == "Вгору":
#             max_y += growth_v[1]
#         elif group.get("growth_dir_y", "Центр") == "Вниз":
#             min_y -= growth_v[1]
#         else:
#             min_y -= growth_v[1] * 0.5
#             max_y += growth_v[1] * 0.5

#         return (min(min_x, max_x), min(min_y, max_y), max(min_x, max_x), max(min_y, max_y))

#     def bboxes_overlap(self, a, b, gap=0.5):
#         return not (
#             a[2] <= b[0] + gap or
#             b[2] <= a[0] + gap or
#             a[3] <= b[1] + gap or
#             b[3] <= a[1] + gap
#         )

#     def has_new_group_overlap(self, cur_w, cur_h, target_w, target_h):
#         groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
#         if len(groups) < 2:
#             return False
#         original_bboxes = [self.group_original_bbox(g) for g in groups]
#         simulated_bboxes = [self.simulated_group_bbox(g, cur_w, cur_h, target_w, target_h) for g in groups]
#         for i in range(len(groups)):
#             for j in range(i + 1, len(groups)):
#                 if self.bboxes_overlap(original_bboxes[i], original_bboxes[j]):
#                     continue
#                 if simulated_bboxes[i] and simulated_bboxes[j] and self.bboxes_overlap(simulated_bboxes[i], simulated_bboxes[j]):
#                     return True
#         return False

#     def find_min_safe_axis(self, cur_w, cur_h, axis):
#         if axis == "width":
#             if not self.has_new_group_overlap(cur_w, cur_h, 1.0, cur_h):
#                 return 1.0
#             low, high = 1.0, cur_w
#             for _ in range(32):
#                 mid = (low + high) * 0.5
#                 if self.has_new_group_overlap(cur_w, cur_h, mid, cur_h):
#                     low = mid
#                 else:
#                     high = mid
#             return high
#         if not self.has_new_group_overlap(cur_w, cur_h, cur_w, 1.0):
#             return 1.0
#         low, high = 1.0, cur_h
#         for _ in range(32):
#             mid = (low + high) * 0.5
#             if self.has_new_group_overlap(cur_w, cur_h, cur_w, mid):
#                 low = mid
#             else:
#                 high = mid
#         return high

#     def find_minimum_safe_size(self):
#         try:
#             cur_w = float(self.input_current_width.text().strip())
#             cur_h = float(self.input_current_height.text().strip())
#         except ValueError:
#             self.lbl_status_calc.setText("<font color='red'>Спочатку задайте початкову ширину і висоту.</font>")
#             return
#         if len(self.parametric_groups) < 2:
#             self.lbl_status_calc.setText("<font color='red'>Потрібно мінімум дві параметричні групи для перевірки накладання.</font>")
#             return
#         min_w = self.find_min_safe_axis(cur_w, cur_h, "width")
#         min_h = self.find_min_safe_axis(cur_w, cur_h, "height")
#         self.lbl_status_calc.setText(
#             f"<font color='#4fc3f7'>Мінімум без нового накладання: W≈{min_w:.1f} мм, H≈{min_h:.1f} мм</font>"
#         )

#     def validate_target_size_or_warn(self, cur_w, cur_h, target_w, target_h):
#         if len(self.parametric_groups) < 2:
#             return True
#         if not self.has_new_group_overlap(cur_w, cur_h, target_w, target_h):
#             return True
#         min_w = self.find_min_safe_axis(cur_w, cur_h, "width")
#         min_h = self.find_min_safe_axis(cur_w, cur_h, "height")
#         self.lbl_status_calc.setText(
#             "<font color='red'>Заданий розмір дає накладання блоків. "
#             f"Безпечний мінімум: W≈{min_w:.1f} мм, H≈{min_h:.1f} мм.</font>"
#         )
#         return False

#     def get_text_style_name(self, doc, font_name):
#         font = (font_name or "STANDARD").strip()
#         if font.upper() == "STANDARD":
#             return "STANDARD"
#         style_name = "TXT_" + re.sub(r"[^0-9A-Za-z_]+", "_", font.upper()).strip("_")
#         font_files = {
#             "ARIAL": "arial.ttf",
#             "ARIAL NARROW": "arialn.ttf",
#             "SIMPLEX": "simplex.shx"
#         }
#         if style_name not in doc.styles:
#             doc.styles.new(style_name, dxfattribs={"font": font_files.get(font.upper(), font)})
#         return style_name

#     def remove_managed_text_entity(self, doc=None, settings=None):
#         doc = doc or self.doc
#         settings = settings or self.get_text_settings()
#         handle = settings.get("handle")
#         if handle and handle in doc.entitydb:
#             try:
#                 doc.modelspace().delete_entity(doc.entitydb[handle])
#             except Exception:
#                 pass
#         settings["handle"] = None

#     def apply_door_text_to_doc(self, doc=None):
#         doc = doc or self.doc
#         settings = self.get_text_settings()
#         if not settings.get("enabled"):
#             self.remove_managed_text_entity(doc, settings)
#             return None
#         text = self.text_display_value(settings.get("text", ""))
#         dxf_text = text if text else " "
#         style_name = self.get_text_style_name(doc, settings.get("font", "STANDARD"))
#         handle = settings.get("handle")
#         entity = doc.entitydb[handle] if handle and handle in doc.entitydb else None
#         if entity is None or entity.dxftype() != "TEXT":
#             entity = doc.modelspace().add_text(dxf_text)
#             settings["handle"] = entity.dxf.handle
#         box_x = float(settings.get("x", 0.0))
#         box_y = float(settings.get("y", 0.0))
#         box_w = self.text_box_width(settings)
#         box_h = self.text_box_height(settings)
#         text_h = max(box_h * 0.55, 0.1)
#         center_x = box_x + box_w * 0.5
#         center_y = box_y + box_h * 0.5
#         entity.dxf.text = dxf_text
#         entity.dxf.height = text_h
#         entity.dxf.style = style_name
#         entity.dxf.width = 1.0
#         entity.set_placement((center_x, center_y, 0.0), align=TextEntityAlignment.MIDDLE_CENTER)
#         entity.dxf.rotation = float(settings.get("rotation", 0.0))
#         self.project_meta["door_text"] = settings
#         return entity

#     def normalize_key(self, value):
#         text = str(value).strip().lower()
#         replacements = {
#             "ширина": "target_width",
#             "width": "target_width",
#             "w": "target_width",
#             "нова ширина": "target_width",
#             "target_width": "target_width",
#             "висота": "target_height",
#             "height": "target_height",
#             "h": "target_height",
#             "нова висота": "target_height",
#             "target_height": "target_height",
#             "поточна ширина": "source_width",
#             "source_width": "source_width",
#             "current_width": "source_width",
#             "початкова ширина": "source_width",
#             "поточна висота": "source_height",
#             "source_height": "source_height",
#             "current_height": "source_height",
#             "початкова висота": "source_height",
#             "лишити": "keep_blocks",
#             "keep": "keep_blocks",
#             "keep_blocks": "keep_blocks",
#             "видалити": "delete_blocks",
#             "delete": "delete_blocks",
#             "delete_blocks": "delete_blocks",
#             "текст": "text",
#             "text": "text",
#             "door_text": "text",
#             "текст x": "text_x",
#             "text_x": "text_x",
#             "x_text": "text_x",
#             "текст y": "text_y",
#             "text_y": "text_y",
#             "y_text": "text_y",
#             "розмір шрифту": "font_size",
#             "висота тексту": "font_size",
#             "font_size": "font_size",
#             "text_height": "font_size",
#             "шрифт": "font",
#             "font": "font",
#             "ширина тексту": "text_width",
#             "text_width": "text_width",
#             "width_factor": "text_width",
#             "поворот тексту": "text_rotation",
#             "text_rotation": "text_rotation",
#             "rotation": "text_rotation",
#         }
#         return replacements.get(text, text)

#     def read_csv_rows(self, path):
#         for encoding in ("utf-8-sig", "cp1251", "utf-8"):
#             try:
#                 with open(path, newline="", encoding=encoding) as f:
#                     return [row for row in csv.reader(f) if any(str(c).strip() for c in row)]
#             except UnicodeDecodeError:
#                 continue
#         return []

#     def read_xlsx_rows(self, path):
#         ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
#         with zipfile.ZipFile(path) as zf:
#             shared = []
#             if "xl/sharedStrings.xml" in zf.namelist():
#                 root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
#                 for si in root.findall("a:si", ns):
#                     shared.append("".join(t.text or "" for t in si.findall(".//a:t", ns)))
#             sheet_name = "xl/worksheets/sheet1.xml"
#             root = ET.fromstring(zf.read(sheet_name))
#             rows = []
#             for row in root.findall(".//a:row", ns):
#                 values = []
#                 for cell in row.findall("a:c", ns):
#                     raw = cell.find("a:v", ns)
#                     text = raw.text if raw is not None else ""
#                     if cell.attrib.get("t") == "s" and text:
#                         text = shared[int(text)]
#                     values.append(text)
#                 if any(str(v).strip() for v in values):
#                     rows.append(values)
#             return rows

#     def import_parameters_from_table(self):
#         path, _ = QFileDialog.getOpenFileName(
#             self,
#             "Виберіть Excel/CSV з параметрами",
#             self.project_dir,
#             "Tables (*.xlsx *.csv);;All Files (*)"
#         )
#         if not path:
#             return
#         try:
#             rows = self.read_xlsx_rows(path) if path.lower().endswith(".xlsx") else self.read_csv_rows(path)
#             params = self.extract_table_parameters(rows)
#             self.record_action_snapshot()
#             self.apply_imported_parameters(params)
#             self.apply_door_text_to_doc()
#             self.doc.saveas(self.dxf_path)
#             self.save_project_config()
#             self.save_original_geometries()
#             self.update_dimension_inputs_from_meta()
#             self.sync_text_inputs_from_meta()
#             self.load_entities_into_list()
#             self.update_viewer()
#             self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Параметри імпортовано: {os.path.basename(path)}</font>")
#         except Exception as e:
#             self.lbl_status_calc.setText(f"<font color='red'>Помилка імпорту: {e}</font>")

#     def quick_order_wizard(self):
#         default_text = f"{self.input_target_width.text()}x{self.input_target_height.text()}"
#         text, ok = QInputDialog.getText(
#             self,
#             "Нове замовлення",
#             "Введіть новий розмір W x H:",
#             text=default_text
#         )
#         if not ok:
#             return
#         nums = [float(x.replace(",", ".")) for x in re.findall(r"\d+(?:[,.]\d+)?", text)]
#         if len(nums) < 2:
#             self.lbl_status_calc.setText("<font color='red'>Введіть два числа: ширина і висота.</font>")
#             return
#         if not self.input_current_width.text().strip() or not self.input_current_height.text().strip():
#             self.update_dimension_inputs_from_meta()
#         self.input_target_width.setText(self.format_dimension_value(nums[0]))
#         self.input_target_height.setText(self.format_dimension_value(nums[1]))
#         self.export_model_dxf_with_dimensions()

#     def extract_table_parameters(self, rows):
#         params = {}
#         if not rows:
#             return params

#         headers = [self.normalize_key(c) for c in rows[0]]
#         if "target_width" in headers or "target_height" in headers:
#             for row in rows[1:]:
#                 for idx, key in enumerate(headers):
#                     if idx >= len(row):
#                         continue
#                     value = row[idx]
#                     if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
#                         num = self.parse_numeric_text(value)
#                         if num is not None:
#                             params[key] = num
#                     elif key in ("text", "font"):
#                         params[key] = str(value).strip()
#                     elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
#                         opening = self.parse_door_opening_value(value)
#                         if opening:
#                             params[key] = opening
#                     elif key in ("keep_blocks", "delete_blocks"):
#                         params.setdefault(key, []).extend(self.split_block_names(value))
#             return params

#         for row in rows:
#             if len(row) < 2:
#                 continue
#             key = self.normalize_key(row[0])
#             value = row[1]
#             if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
#                 num = self.parse_numeric_text(value)
#                 if num is not None:
#                     params[key] = num
#             elif key in ("text", "font"):
#                 params[key] = str(value).strip()
#             elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
#                 opening = self.parse_door_opening_value(value)
#                 if opening:
#                     params[key] = opening
#             elif key in ("keep_blocks", "delete_blocks"):
#                 params[key] = self.split_block_names(value)
#         return params

#     def split_block_names(self, value):
#         if value is None:
#             return []
#         return [part.strip() for part in re.split(r"[,;\n]+", str(value)) if part.strip()]

#     def apply_imported_parameters(self, params, refresh_ui=True, save_config=True):
#         for key in ("source_width", "source_height", "target_width", "target_height"):
#             if key in params:
#                 self.project_meta[key] = params[key]
#         source_opening = params.get("source_door_opening", params.get("source_opening"))
#         target_opening = params.get("target_door_opening", params.get("target_opening", params.get("door_opening")))
#         if source_opening:
#             self.project_meta["source_door_opening"] = source_opening
#         if target_opening:
#             self.project_meta["target_door_opening"] = target_opening
#             self.project_meta["door_opening"] = target_opening
#         text_settings = self.get_text_settings()
#         text_key_map = {
#             "text": "text",
#             "text_x": "x",
#             "text_y": "y",
#             "font_size": "height",
#             "text_width": "width_factor",
#             "text_rotation": "rotation",
#             "font": "font"
#         }
#         for source_key, target_key in text_key_map.items():
#             if source_key in params:
#                 text_settings[target_key] = params[source_key]
#         if "text" in params and str(params["text"]).strip():
#             text_settings["enabled"] = True
#             if "text_x" not in params and "text_y" not in params:
#                 self.lbl_status_calc.setText("<font color='#4fc3f7'>Текст підставлено в попередньо задану рамку.</font>")
#         self.project_meta["door_text"] = text_settings
#         if "keep_blocks" in params and params["keep_blocks"]:
#             keep_set = set(params["keep_blocks"])
#             for group in self.parametric_groups:
#                 name = group.get("name", "")
#                 key = self.get_group_key(group)
#                 self.block_keep_state[key] = key in keep_set or name in keep_set
#         if "delete_blocks" in params and params["delete_blocks"]:
#             delete_set = set(params["delete_blocks"])
#             for group in self.parametric_groups:
#                 name = group.get("name", "")
#                 key = self.get_group_key(group)
#                 if key in delete_set or name in delete_set:
#                     self.block_keep_state[key] = False
#         if refresh_ui:
#             self.update_dimension_inputs_from_meta()
#             self.sync_opening_inputs_from_meta()
#             self.sync_text_inputs_from_meta()
#             self.load_block_filter_list()
#         if save_config:
#             self.save_project_config()

#     def sanitize_filename_part(self, value):
#         text = self.format_dimension_value(value)
#         return re.sub(r"[^0-9A-Za-zА-Яа-я_\-.]+", "_", text)

#     def parse_door_opening_value(self, value):
#         text = str(value or "").strip().lower()
#         if not text:
#             return None
#         if text in ("right", "r", "prave") or "прав" in text or "right" in text:
#             return "right"
#         if text in ("left", "l", "live") or "лів" in text or "лев" in text or "left" in text:
#             return "left"
#         return None

#     def get_export_output_dir(self, target_w, target_h):
#         width_part = self.sanitize_filename_part(target_w)
#         height_part = self.sanitize_filename_part(target_h)
#         folder_name = f"generated_{width_part}_{height_part}"
#         output_dir = os.path.join(self.project_dir, folder_name)
#         os.makedirs(output_dir, exist_ok=True)
#         return output_dir

#     def build_export_path(self, target_w, target_h):
#         base_name = os.path.splitext(os.path.basename(self.dxf_path))[0]
#         base_name = re.sub(r"(?<!\d)\d{3,5}_\d{3,5}(?!\d)", "", base_name).strip("_- ")
#         width_part = self.sanitize_filename_part(target_w)
#         height_part = self.sanitize_filename_part(target_h)
#         name = f"{base_name}_{width_part}_{height_part}.DXF"
#         output_dir = self.get_export_output_dir(target_w, target_h)
#         path = os.path.join(output_dir, name)
#         counter = 2
#         while os.path.exists(path):
#             name = f"{base_name}_{width_part}_{height_part}_{counter}.DXF"
#             path = os.path.join(output_dir, name)
#             counter += 1
#         return path

#     def export_target_opening(self):
#         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
#         return self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)

#     def export_needs_opening_mirror(self):
#         source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
#         return source_opening != self.export_target_opening()

#     def apply_opening_to_export_doc(self, export_doc):
#         if not self.export_needs_opening_mirror():
#             return
#         min_x, _min_y, max_x, _max_y = self.get_dxf_bounds(export_doc)
#         if min_x is None:
#             return
#         axis_x = (min_x + max_x) * 0.5
#         for entity in export_doc.modelspace():
#             self.mirror_entity_horizontally(entity, axis_x)


#     def save_generated_folder_config(self, output_dir, target_w, target_h, target_opening):
#         """
#         _folder_params.json більше не створюємо.
#         Початкові параметри моделі зберігаються в DoorModels.
#         """
#         return

#     def save_generated_project_config(self, export_path, target_w, target_h):
#         """
#         JSON для згенерованого DXF більше не створюємо.
#         Уся історія експорту зберігається в ProjectExports.
#         """
#         return

#     def is_generated_dimension_dxf(self, file_name):
#         base_name = os.path.splitext(file_name)[0]
#         return re.search(r"_\d{2,5}_\d{2,5}(?:_\d+)?$", base_name) is not None

#     def get_folder_source_dxf_files(self):
#         try:
#             files = os.listdir(self.project_dir)
#         except Exception:
#             return []
#         return sorted(
#             file_name for file_name in files
#             if file_name.lower().endswith(".dxf")
#             and not self.is_generated_dimension_dxf(file_name)
#         )

#     def preview_parametric_scale(self):
#         self.record_action_snapshot()
#         if self.debug_output:
#             print("\n" + "=" * 90)
#             print("[PREVIEW DEBUG] START PREVIEW")
#             print("[PREVIEW DEBUG] Перегляд рахує не від файлу на диску, а від self.original_geometries")
#             print(f"[PREVIEW DEBUG] base handles={len(self.original_geometries)}")
#             print(f"[PREVIEW DEBUG] source W/H={self.project_meta.get('source_width')} / {self.project_meta.get('source_height')}")
#             print(f"[PREVIEW DEBUG] target W/H={self.input_target_width.text()} / {self.input_target_height.text()}")
#             print("=" * 90)
#         if self.process_parametric_percentage_scale(save_result=False, record_history=False):
#             self.lbl_status_calc.setText("<font color='#4fc3f7'>Перегляд застосовано тільки на екрані. Файл ще не збережено.</font>")

#     def restore_current_dxf_from_disk(self):
#         if not os.path.exists(self.dxf_path):
#             return
#         self.record_action_snapshot()
#         self.doc = ezdxf.readfile(self.dxf_path)
#         self.save_original_geometries()
#         self.update_dimension_inputs_from_meta()
#         self.update_viewer()
#         self.load_entities_into_list()
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Повернуто стан з відкритого DXF.</font>")

#     def export_new_dxf_with_dimensions(self):
#         self.collect_text_settings_from_inputs()
#         original_dxf_path = self.dxf_path
#         original_bytes = None
#         if os.path.exists(self.dxf_path):
#             with open(self.dxf_path, "rb") as f:
#                 original_bytes = f.read()
#         original_meta = copy.deepcopy(self.project_meta)
#         original_groups = copy.deepcopy(self.parametric_groups)
#         original_keep_state = copy.deepcopy(self.block_keep_state)

#         self.project_meta["source_width"] = self.parse_numeric_text(self.input_current_width.text())
#         self.project_meta["source_height"] = self.parse_numeric_text(self.input_current_height.text())
#         self.project_meta["target_width"] = self.parse_numeric_text(self.input_target_width.text())
#         self.project_meta["target_height"] = self.parse_numeric_text(self.input_target_height.text())
#         self.is_loading_history = True
#         self.suppress_project_config_save = True
#         try:
#             ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
#         finally:
#             self.suppress_project_config_save = False
#             self.is_loading_history = False
#         if not ok_to_export:
#             if original_bytes is not None:
#                 with open(self.dxf_path, "wb") as f:
#                     f.write(original_bytes)
#                 self.doc = ezdxf.readfile(self.dxf_path)
#                 self.save_original_geometries()
#             self.project_meta = original_meta
#             self.parametric_groups = original_groups
#             self.block_keep_state = original_keep_state
#             self.update_dimension_inputs_from_meta()
#             self.load_groups_into_list()
#             self.load_entities_into_list()
#             self.update_viewer()
#             return

#         target_w = self.project_meta.get("target_width")
#         target_h = self.project_meta.get("target_height")
#         export_path = self.build_export_path(target_w, target_h)

#         export_doc = copy.deepcopy(self.doc)
#         export_msp = export_doc.modelspace()
#         delete_handles = set()
#         for group in self.parametric_groups:
#             key = self.get_group_key(group)
#             if not self.block_keep_state.get(key, True):
#                 delete_handles.update(group.get("handles", set()))
#         for hndl in list(delete_handles):
#             if hndl in export_doc.entitydb:
#                 export_msp.delete_entity(export_doc.entitydb[hndl])

#         self.apply_opening_to_export_doc(export_doc)
#         export_doc.saveas(export_path)
#         self.save_generated_project_config(export_path, target_w, target_h)
#         self.save_export_to_db(export_path)
#         if original_bytes is not None:
#             with open(self.dxf_path, "wb") as f:
#                 f.write(original_bytes)
#             self.doc = ezdxf.readfile(self.dxf_path)
#         self.project_meta = original_meta
#         self.parametric_groups = original_groups
#         self.block_keep_state = original_keep_state
#         self.save_original_geometries()
#         self.save_project_config()
#         self.scan_project_folder_for_dxf()
#         self.update_dimension_inputs_from_meta()
#         self.load_groups_into_list()
#         self.load_entities_into_list()
#         self.update_viewer()
#         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Створено: {os.path.basename(export_path)}</font>")

#     def export_model_dxf_with_dimensions(self):
#         """Export all source DXF files from the current folder/model with the same target size."""
#         self.collect_text_settings_from_inputs()
#         self.register_current_folder_model(show_errors=False)

#         original_dxf_path = self.dxf_path
#         original_project_file_id = getattr(self, "current_project_file_id", None)
#         original_door_model_id = getattr(self, "current_door_model_id", None)
#         original_meta = copy.deepcopy(self.project_meta)
#         original_groups = copy.deepcopy(self.parametric_groups)
#         original_keep_state = copy.deepcopy(self.block_keep_state)
#         original_bytes = None
#         if os.path.exists(original_dxf_path):
#             with open(original_dxf_path, "rb") as f:
#                 original_bytes = f.read()

#         source_files = self.get_folder_source_dxf_files()
#         if not source_files:
#             source_files = [os.path.basename(self.dxf_path)]

#         target_w = self.parse_numeric_text(self.input_target_width.text())
#         target_h = self.parse_numeric_text(self.input_target_height.text())
#         source_w = self.parse_numeric_text(self.input_current_width.text())
#         source_h = self.parse_numeric_text(self.input_current_height.text())
#         if target_w is None or target_h is None or source_w is None or source_h is None:
#             self.lbl_status_calc.setText("<font color='red'>Вкажіть початкові та цільові W/H.</font>")
#             return

#         created = []
#         skipped = 0
#         try:
#             for source_file in source_files:
#                 source_path = os.path.join(self.project_dir, source_file)
#                 if not os.path.exists(source_path):
#                     continue
#                 with open(source_path, "rb") as f:
#                     source_bytes = f.read()

#                 self.dxf_path = source_path
#                 self.current_project_file_id = None
#                 self.current_door_model_id = original_door_model_id
#                 self.doc = ezdxf.readfile(self.dxf_path)
#                 self.load_project_config()
#                 self.save_original_geometries()

#                 self.project_meta["source_width"] = source_w
#                 self.project_meta["source_height"] = source_h
#                 self.project_meta["target_width"] = target_w
#                 self.project_meta["target_height"] = target_h

#                 self.is_loading_history = True
#                 self.suppress_project_config_save = True
#                 try:
#                     ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
#                 finally:
#                     self.suppress_project_config_save = False
#                     self.is_loading_history = False

#                 if not ok_to_export:
#                     skipped += 1
#                     with open(source_path, "wb") as f:
#                         f.write(source_bytes)
#                     self.doc = ezdxf.readfile(self.dxf_path)
#                     self.save_original_geometries()
#                     continue

#                 export_path = self.build_export_path(target_w, target_h)
#                 export_doc = copy.deepcopy(self.doc)
#                 export_msp = export_doc.modelspace()
#                 for hndl in self.get_export_delete_handles():
#                     if hndl in export_doc.entitydb:
#                         export_msp.delete_entity(export_doc.entitydb[hndl])

#                 self.apply_opening_to_export_doc(export_doc)
#                 export_doc.saveas(export_path)
#                 self.save_generated_project_config(export_path, target_w, target_h)
#                 self.save_export_to_db(export_path)
#                 created.append(os.path.basename(export_path))

#                 with open(source_path, "wb") as f:
#                     f.write(source_bytes)
#                 self.doc = ezdxf.readfile(self.dxf_path)
#                 self.save_original_geometries()

#             self.dxf_path = original_dxf_path
#             self.current_project_file_id = original_project_file_id
#             self.current_door_model_id = original_door_model_id
#             if os.path.exists(self.dxf_path):
#                 if original_bytes is not None:
#                     with open(self.dxf_path, "wb") as f:
#                         f.write(original_bytes)
#                 self.doc = ezdxf.readfile(self.dxf_path)
#             self.project_meta = original_meta
#             self.parametric_groups = original_groups
#             self.block_keep_state = original_keep_state
#             self.save_original_geometries()
#             self.save_project_config()
#             self.scan_project_folder_for_dxf()
#             self.update_dimension_inputs_from_meta()
#             self.load_groups_into_list()
#             self.load_entities_into_list()
#             self.update_viewer()
#             if skipped:
#                 self.lbl_status_calc.setText(f"<font color='#ff9800'>Комплект створено: {len(created)} DXF, пропущено: {skipped}</font>")
#             else:
#                 self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Комплект створено: {len(created)} DXF</font>")
#         except Exception as e:
#             self.dxf_path = original_dxf_path
#             self.current_project_file_id = original_project_file_id
#             self.current_door_model_id = original_door_model_id
#             if original_bytes is not None and os.path.exists(self.dxf_path):
#                 with open(self.dxf_path, "wb") as f:
#                     f.write(original_bytes)
#                 self.doc = ezdxf.readfile(self.dxf_path)
#                 self.save_original_geometries()
#             self.project_meta = original_meta
#             self.parametric_groups = original_groups
#             self.block_keep_state = original_keep_state
#             self.lbl_status_calc.setText(f"<font color='red'>Помилка експорту комплекту: {e}</font>")

#     def batch_export_from_table(self):
#         self.collect_text_settings_from_inputs()
#         path, _ = QFileDialog.getOpenFileName(
#             self,
#             "Виберіть Excel/CSV для пакетного створення DXF",
#             self.project_dir,
#             "Tables (*.xlsx *.csv);;All Files (*)"
#         )
#         if not path:
#             return

#         original_dxf_path = self.dxf_path
#         original_bytes = None
#         if os.path.exists(self.dxf_path):
#             with open(self.dxf_path, "rb") as f:
#                 original_bytes = f.read()
#         original_meta = copy.deepcopy(self.project_meta)
#         original_groups = copy.deepcopy(self.parametric_groups)
#         original_keep_state = copy.deepcopy(self.block_keep_state)

#         try:
#             rows = self.read_xlsx_rows(path) if path.lower().endswith(".xlsx") else self.read_csv_rows(path)
#             jobs = self.extract_batch_jobs(rows)
#             source_files = self.get_folder_source_dxf_files()
#             if not source_files:
#                 source_files = [os.path.basename(self.dxf_path)]
#             created = []
#             skipped = 0
#             for job in jobs:
#                 for source_file in source_files:
#                     source_path = os.path.join(self.project_dir, source_file)
#                     if not os.path.exists(source_path):
#                         continue
#                     with open(source_path, "rb") as f:
#                         source_bytes = f.read()

#                     self.dxf_path = source_path
#                     self.current_project_file_id = None
#                     self.doc = ezdxf.readfile(self.dxf_path)
#                     self.load_project_config()
#                     self.save_original_geometries()
#                     self.apply_imported_parameters(job, refresh_ui=False, save_config=False)
#                     self.is_loading_history = True
#                     self.suppress_project_config_save = True
#                     try:
#                         ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
#                     finally:
#                         self.suppress_project_config_save = False
#                         self.is_loading_history = False
#                     if not ok_to_export:
#                         skipped += 1
#                         with open(source_path, "wb") as f:
#                             f.write(source_bytes)
#                         self.doc = ezdxf.readfile(self.dxf_path)
#                         self.save_original_geometries()
#                         continue

#                     target_w = self.project_meta.get("target_width")
#                     target_h = self.project_meta.get("target_height")
#                     export_path = self.build_export_path(target_w, target_h)
#                     export_doc = copy.deepcopy(self.doc)
#                     export_msp = export_doc.modelspace()
#                     delete_handles = self.get_export_delete_handles()
#                     for hndl in delete_handles:
#                         if hndl in export_doc.entitydb:
#                             export_msp.delete_entity(export_doc.entitydb[hndl])
#                     self.apply_opening_to_export_doc(export_doc)
#                     export_doc.saveas(export_path)
#                     self.save_generated_project_config(export_path, target_w, target_h)
#                     self.save_export_to_db(export_path)
#                     created.append(os.path.basename(export_path))

#                     with open(source_path, "wb") as f:
#                         f.write(source_bytes)
#                     self.doc = ezdxf.readfile(self.dxf_path)
#                     self.save_original_geometries()

#             self.dxf_path = original_dxf_path
#             if os.path.exists(self.dxf_path):
#                 self.doc = ezdxf.readfile(self.dxf_path)
#             self.project_meta = original_meta
#             self.parametric_groups = original_groups
#             self.block_keep_state = original_keep_state
#             self.save_project_config()
#             self.scan_project_folder_for_dxf()
#             self.update_dimension_inputs_from_meta()
#             self.load_groups_into_list()
#             self.load_entities_into_list()
#             self.update_viewer()
#             if skipped:
#                 self.lbl_status_calc.setText(
#                     f"<font color='#ff9800'>Пакет створено: {len(created)} DXF, пропущено через накладання: {skipped}</font>"
#                 )
#             else:
#                 self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Пакет створено: {len(created)} DXF</font>")
#         except Exception as e:
#             self.lbl_status_calc.setText(f"<font color='red'>Помилка пакета: {e}</font>")
#             self.dxf_path = original_dxf_path
#             if original_bytes is not None:
#                 with open(self.dxf_path, "wb") as f:
#                     f.write(original_bytes)
#                 self.doc = ezdxf.readfile(self.dxf_path)
#                 self.save_original_geometries()

#     def extract_batch_jobs(self, rows):
#         if not rows:
#             return []
#         headers = [self.normalize_key(c) for c in rows[0]]
#         jobs = []
#         for row in rows[1:]:
#             params = {}
#             for idx, key in enumerate(headers):
#                 if idx >= len(row):
#                     continue
#                 value = row[idx]
#                 if key in ("source_width", "source_height", "target_width", "target_height", "text_x", "text_y", "font_size", "text_width", "text_rotation"):
#                     num = self.parse_numeric_text(value)
#                     if num is not None:
#                         params[key] = num
#                 elif key in ("text", "font"):
#                     text_value = str(value).strip()
#                     if text_value:
#                         params[key] = text_value
#                 elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
#                     opening = self.parse_door_opening_value(value)
#                     if opening:
#                         params[key] = opening
#                 elif key in ("keep_blocks", "delete_blocks"):
#                     names = self.split_block_names(value)
#                     if names:
#                         params.setdefault(key, []).extend(names)
#             if params:
#                 jobs.append(params)
#         if not jobs:
#             single = self.extract_table_parameters(rows)
#             if single:
#                 jobs.append(single)
#         return jobs

#     def normalize_key(self, value):
#         return table_io.normalize_key(value)

#     def read_csv_rows(self, path):
#         return table_io.read_csv_rows(path)

#     def read_xlsx_rows(self, path):
#         return table_io.read_xlsx_rows(path)

#     def extract_table_parameters(self, rows):
#         return table_io.extract_table_parameters(rows, self.parse_numeric_text)

#     def split_block_names(self, value):
#         return table_io.split_block_names(value)

#     def parse_door_opening_value(self, value):
#         return table_io.parse_door_opening_value(value)

#     def extract_batch_jobs(self, rows):
#         return table_io.extract_batch_jobs(rows, self.parse_numeric_text)

#     def get_export_delete_handles(self):
#         delete_handles = set()
#         for group in self.parametric_groups:
#             key = self.get_group_key(group)
#             if not self.block_keep_state.get(key, True):
#                 delete_handles.update(group.get("handles", set()))
#         return delete_handles

#     def open_dxf_from_dialog(self):
#         file_path, _ = QFileDialog.getOpenFileName(
#             self,
#             "Виберіть DXF файл",
#             self.project_dir,
#             "DXF Files (*.dxf);;All Files (*)"
#         )
        
#         if file_path:
#             try:
#                 old_project_dir = getattr(self, "project_dir", None)
#                 new_project_dir = os.path.dirname(os.path.abspath(file_path))
#                 if old_project_dir and os.path.abspath(old_project_dir) != os.path.abspath(new_project_dir):
#                     self.current_project_file_id = None
#                     self.current_door_model_id = None
#                 else:
#                     self.current_project_file_id = None
#                 self.project_dir = new_project_dir
#                 self.dxf_path = os.path.abspath(file_path)
                
#                 self.doc = ezdxf.readfile(self.dxf_path)
                
#                 self.selected_handles.clear()
#                 self.parametric_groups.clear()
#                 self.zones_undo_stack.clear()
#                 self.zones_redo_stack.clear()
#                 self.global_recalc_undo_stack.clear()
#                 self.global_recalc_redo_stack.clear()
                
#                 self.load_project_config()
#                 self.prompt_source_dimensions_on_open()
#                 self.register_current_folder_model(show_errors=False)
#                 self.update_dimension_inputs_from_meta()
                
#                 self.history = HistoryManager(self.dxf_path)
#                 self.history.save_state()
#                 self.save_zones_history_state()
#                 self.save_original_geometries()
                
#                 self.scan_project_folder_for_dxf()
#                 self.update_viewer()
#                 self.load_entities_into_list()
#                 self.load_groups_into_list()
#                 self.load_block_filter_list()
#                 self.update_history_buttons_state()
                
#             except Exception as e:
#                 print(f"Помилка при відкритті файлу: {e}")

#     def transform_selected_entities(self, mode):
#         if not self.selected_handles: return
#         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
#         if not selected_entities: return
#         self.record_action_snapshot()

#         bboxes = [self.entity_bbox(e) for e in selected_entities]
#         bboxes = [b for b in bboxes if b]
#         if not bboxes:
#             return
#         min_x = min(b[0] for b in bboxes)
#         min_y = min(b[1] for b in bboxes)
#         max_x = max(b[2] for b in bboxes)
#         max_y = max(b[3] for b in bboxes)
#         cx = (min_x + max_x) * 0.5
#         cy = (min_y + max_y) * 0.5

#         for entity in selected_entities:
#             if mode == "ROT90":
#                 m1 = Matrix44.translate(-cx, -cy, 0)
#                 m2 = Matrix44.z_rotate(math.radians(90))
#                 m3 = Matrix44.translate(cx, cy, 0)
#                 m = m1 @ m2 @ m3
#             elif mode == "ROT180":
#                 m1 = Matrix44.translate(-cx, -cy, 0)
#                 m2 = Matrix44.z_rotate(math.radians(180))
#                 m3 = Matrix44.translate(cx, cy, 0)
#                 m = m1 @ m2 @ m3
#             elif mode == "ROT270":
#                 m1 = Matrix44.translate(-cx, -cy, 0)
#                 m2 = Matrix44.z_rotate(math.radians(270))
#                 m3 = Matrix44.translate(cx, cy, 0)
#                 m = m1 @ m2 @ m3
#             elif mode == "MIRROR_H":
#                 self.mirror_entity_horizontally(entity, cx)
#                 continue
#             elif mode == "MIRROR_V":
#                 self.mirror_entity_vertically(entity, cy)
#                 continue
#             else: 
#                 continue
#             entity.transform(m)

#         self.transform_managed_text_settings(mode, cx, cy)

#         for group in self.parametric_groups:
#             if not group["handles"].isdisjoint(self.selected_handles):
           
#                 old_kw = group.get("k_w", 0.0)
#                 old_kh = group.get("k_h", 0.0)
#                 old_gpw = group.get("growth_p_w", 0.0)
#                 old_gph = group.get("growth_p_h", 0.0)
                
#                 old_link_x = group.get("link_x", "X = W")
#                 old_link_y = group.get("link_y", "Y = H")
                
#                 old_dir_x = group.get("growth_dir_x", "Вправо")
#                 old_dir_y = group.get("growth_dir_y", "Вгору")
#                 old_shift_dir_x = group.get("shift_dir_x", "Вправо")
#                 old_shift_dir_y = group.get("shift_dir_y", "Вгору")

#                 if mode == "ROT90":
#                     group["k_w"], group["k_h"] = old_kh, old_kw
#                     group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
#                     group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
#                     group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
            
#                     map_x_to_y = {"Вправо": "Вгору", "Вліво": "Вниз", "Центр": "Центр"}
#                     map_y_to_x = {"Вгору": "Вліво", "Вниз": "Вправо", "Центр": "Центр"}
#                     group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
#                     group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")
#                     group["shift_dir_x"] = map_y_to_x.get(old_shift_dir_y, "Вправо")
#                     group["shift_dir_y"] = map_x_to_y.get(old_shift_dir_x, "Вгору")

#                 elif mode == "ROT270":
#                     group["k_w"], group["k_h"] = old_kh, old_kw
#                     group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
#                     group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
#                     group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
           
#                     map_x_to_y = {"Вправо": "Вниз", "Вліво": "Вгору", "Центр": "Центр"}
#                     map_y_to_x = {"Вгору": "Вправо", "Вниз": "Вліво", "Центр": "Центр"}
#                     group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
#                     group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")
#                     group["shift_dir_x"] = map_y_to_x.get(old_shift_dir_y, "Вправо")
#                     group["shift_dir_y"] = map_x_to_y.get(old_shift_dir_x, "Вгору")

#                 elif mode == "ROT180":
#                     map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
#                     map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
#                     group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
#                     group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
#                     group["shift_dir_x"] = map_x.get(old_shift_dir_x, "Вправо")
#                     group["shift_dir_y"] = map_y.get(old_shift_dir_y, "Вгору")

#                 elif mode == "MIRROR_H": 
#                     map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
#                     group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
#                     group["shift_dir_x"] = map_x.get(old_shift_dir_x, "Вправо")

#                 elif mode == "MIRROR_V": 
#                     map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
#                     group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
#                     group["shift_dir_y"] = map_y.get(old_shift_dir_y, "Вгору")
                    
#         self.update_growth_axis_after_transform(mode)
#         self.swap_axis_link_mode_for_quarter_turn(mode)
#         self.doc.saveas(self.dxf_path)

#         self.commit_current_geometry_as_parametric_base(
#             reason=f"TRANSFORM {mode}",
#             update_source_dimensions=False,
#             preserve_target_dimensions=True,
#         )

#         self.save_project_config()
#         self.push_to_history()
        
#         self.on_group_selection_changed() 
#         self.sync_text_inputs_from_meta()
#         self.update_viewer()
#         self.load_entities_into_list()

#     def snap_to_zero(self):
#         min_x, min_y, max_x, max_y = self.get_dxf_bounds()
#         if min_x is None or min_y is None:
#             return
#         self.record_action_snapshot()
#         shift_x = -min_x
#         shift_y = -min_y

#         matrix = Matrix44.translate(shift_x, shift_y, 0)
#         for entity in self.doc.modelspace():
#             try:
#                 entity.transform(matrix)
#             except Exception:
#                 tp = entity.dxftype()
#                 if tp == "TEXT":
#                     x, y, z = entity.dxf.insert
#                     entity.dxf.insert = (x + shift_x, y + shift_y, z)

#         settings = self.get_text_settings()
#         settings["x"] = float(settings.get("x", 0.0)) + shift_x
#         settings["y"] = float(settings.get("y", 0.0)) + shift_y
#         self.project_meta["door_text"] = settings

#         self.doc.saveas(self.dxf_path)
#         self.save_original_geometries()
#         self.save_project_config()
#         self.push_to_history()
#         self.sync_text_inputs_from_meta()
#         self.load_entities_into_list()
#         self.update_viewer()
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Фігуру притиснуто до (0,0).</font>")

#     def delete_entities_from_dxf(self):
#         if not self.selected_handles:
#             return
#         self.record_action_snapshot()

#         msp = self.doc.modelspace()
#         handles_to_delete = list(self.selected_handles)

#         for hndl in handles_to_delete:
#             if hndl in self.doc.entitydb:
#                 entity = self.doc.entitydb[hndl]
#                 msp.delete_entity(entity)
            
#             if hndl in self.original_geometries:
#                 del self.original_geometries[hndl]

#             for group in self.parametric_groups:
#                 if hndl in group["handles"]:
#                     group["handles"].remove(hndl)

#         self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]
#         self.selected_handles.clear()
        
#         self.doc.saveas(self.dxf_path)
#         self.save_project_config()
#         self.push_to_history()
        
#         self.load_entities_into_list()
#         self.load_groups_into_list()
#         self.update_viewer()

#     def toggle_inspector_mode(self, checked):
#         if not checked:
#             if self.coord_tooltip_item and self.coord_tooltip_item in self.scene.items():
#                 self.scene.removeItem(self.coord_tooltip_item)
#             if self.coord_snap_marker and self.coord_snap_marker in self.scene.items():
#                 self.scene.removeItem(self.coord_snap_marker)
#             self.coord_tooltip_item = None
#             self.coord_snap_marker = None
#         self.update_viewer()

#     def on_scene_mouse_move(self, event):
#         QGraphicsScene.mouseMoveEvent(self.scene, event)
#         if not self.chk_enable_inspector.isChecked():
#             return

#         pos = event.scenePos()
#         cursor_x, cursor_y = pos.x(), -pos.y()

#         closest_pt = None
#         min_dist = float('inf')

#         for entity in self.doc.modelspace():
#             if entity.dxftype() == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
                
#                 d1 = math.hypot(cursor_x - x1, cursor_y - y1)
#                 d2 = math.hypot(cursor_x - x2, cursor_y - y2)

#                 if d1 < min_dist:
#                     min_dist = d1
#                     closest_pt = (x1, y1, "START")
#                 if d2 < min_dist:
#                     min_dist = d2
#                     closest_pt = (x2, y2, "END")

#         if closest_pt and min_dist < 40.0:
#             snap_x, snap_y, pt_type = closest_pt
#             if not self.coord_snap_marker:
#                 self.coord_snap_marker = self.scene.addEllipse(-4, -4, 8, 8, QPen(QColor("#ff9800"), 1.5), QBrush(QColor(255, 152, 0, 150)))
#                 self.coord_tooltip_item = self.scene.addText("")
#                 self.coord_tooltip_item.setDefaultTextColor(QColor("#ff9800"))
            
#             self.coord_snap_marker.setPos(snap_x, -snap_y)
#             self.coord_tooltip_item.setPos(snap_x + 10, -snap_y - 25)
#             self.coord_tooltip_item.setPlainText(f"Вузол {pt_type}\nX: {snap_x:.1f}\nY: {snap_y:.1f}")
#         else:
#             if self.coord_tooltip_item:
#                 self.coord_tooltip_item.setPlainText("")
#             if self.coord_snap_marker:
#                 self.coord_snap_marker.setPos(-99999, -99999)
        
#         self.view.viewport().update()

#     def guess_growth_axis_for_bbox(self, bbox):
#         bounds = self.get_non_text_dxf_bounds()
#         if bounds[0] is None or not bbox:
#             return "both"
#         ratio_x = self.auto_layout_dimension_ratio(bbox, bounds, "x")
#         ratio_y = self.auto_layout_dimension_ratio(bbox, bounds, "y")
#         grows_x = ratio_x >= 0.55
#         grows_y = ratio_y >= 0.55
#         if grows_x and grows_y:
#             return "both"
#         if grows_x:
#             return "width"
#         if grows_y:
#             return "height"
#         return "fixed"

#     def make_parametric_group_data(self, name, handles, growth_axis="both", auto_grouped=False):
#         group = {
#             "name": name,
#             "handles": set(handles),
#             "k_w": 0.0,
#             "k_h": 0.0,
#             "growth_p_w": 0.0,
#             "growth_p_h": 0.0,
#             "growth_dir_x": "Центр",
#             "growth_dir_y": "Центр",
#             "shift_dir_x": "Вправо",
#             "shift_dir_y": "Вгору",
#             "link_x": "X = W",
#             "link_y": "Y = H",
#             "growth_axis": growth_axis,
#             "resizes": False,
#             "role_y": "manual",
#             "auto_rule": False,
#             "auto_grouped": auto_grouped,
#             "touch_y_enabled": False,
#             "touch_to_uid": None,
#             "touch_gap_y": 0.0
#         }
#         self.get_group_key(group)
#         self.apply_growth_axis_to_group(group)
#         return group

#     def union_bboxes(self, bboxes):
#         valid = [bbox for bbox in bboxes if bbox]
#         if not valid:
#             return None
#         return (
#             min(b[0] for b in valid),
#             min(b[1] for b in valid),
#             max(b[2] for b in valid),
#             max(b[3] for b in valid),
#         )

#     def bboxes_near(self, a, b, tolerance):
#         return not (
#             a[2] < b[0] - tolerance or
#             b[2] < a[0] - tolerance or
#             a[3] < b[1] - tolerance or
#             b[3] < a[1] - tolerance
#         )

#     def collect_autogroup_entries(self):
#         entries = []
#         for entity in self.doc.modelspace():
#             bbox = self.entity_bbox(entity)
#             if not bbox:
#                 continue
#             handle = entity.dxf.handle
#             layer = str(getattr(entity.dxf, "layer", "") or "0")
#             entries.append({
#                 "handle": handle,
#                 "bbox": bbox,
#                 "layer": layer,
#                 "type": entity.dxftype(),
#             })
#         return entries

#     def build_layer_autogroups(self, entries):
#         layer_map = {}
#         for entry in entries:
#             layer_map.setdefault(entry["layer"], []).append(entry)
#         useful_layers = {
#             layer: items for layer, items in layer_map.items()
#             if len(items) > 1 and layer.strip() and layer.strip() != "0"
#         }
#         if len(useful_layers) < 2:
#             return []
#         groups = []
#         for layer, items in sorted(useful_layers.items()):
#             handles = [item["handle"] for item in items]
#             bbox = self.union_bboxes([item["bbox"] for item in items])
#             groups.append((f"Шар {layer}", handles, bbox))
#         return groups

#     def build_proximity_autogroups(self, entries, tolerance=3.0):
#         n = len(entries)
#         visited = set()
#         groups = []
#         for start in range(n):
#             if start in visited:
#                 continue
#             stack = [start]
#             visited.add(start)
#             component = []
#             while stack:
#                 idx = stack.pop()
#                 component.append(entries[idx])
#                 bbox = entries[idx]["bbox"]
#                 for other in range(n):
#                     if other in visited:
#                         continue
#                     if self.bboxes_near(bbox, entries[other]["bbox"], tolerance):
#                         visited.add(other)
#                         stack.append(other)
#             groups.append(component)
#         result = []
#         for i, component in enumerate(groups, start=1):
#             handles = [item["handle"] for item in component]
#             bbox = self.union_bboxes([item["bbox"] for item in component])
#             result.append((f"Деталь {i}", handles, bbox))
#         return result

#     def auto_group_entities(self):
#         entries = self.collect_autogroup_entries()
#         if not entries:
#             self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автогрупування.</font>")
#             return
#         if self.parametric_groups:
#             answer = QMessageBox.question(
#                 self,
#                 "Автогрупувати",
#                 "Поточні параметричні групи буде замінено. Продовжити?",
#                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
#                 QMessageBox.StandardButton.No,
#             )
#             if answer != QMessageBox.StandardButton.Yes:
#                 return

#         auto_groups = self.build_layer_autogroups(entries)
#         method = "layers"
#         if not auto_groups:
#             auto_groups = self.build_proximity_autogroups(entries)
#             method = "proximity"

#         auto_groups = [
#             (name, handles, bbox)
#             for name, handles, bbox in auto_groups
#             if handles and bbox
#         ]
#         if not auto_groups:
#             self.lbl_status_calc.setText("<font color='red'>Не вдалося сформувати групи автоматично.</font>")
#             return

#         self.record_action_snapshot()
#         self.parametric_groups = []
#         self.block_keep_state = {}
#         file_axis = self.project_meta.get("growth_axis", "both")
#         for name, handles, bbox in auto_groups:
#             group = self.make_parametric_group_data(name, handles, file_axis, auto_grouped=True)
#             self.parametric_groups.append(group)
#             self.block_keep_state[group["uid"]] = True

#         self.clear_selection()
#         self.push_to_history()
#         self.save_project_config()
#         self.load_groups_into_list()
#         self.update_viewer()
#         self.lbl_status_calc.setText(
#             f"<font color='#a5d6a7'>Автогрупування: створено {len(self.parametric_groups)} груп ({method}).</font>"
#         )

#     def create_parametric_group(self):
#         if len(self.selected_handles) < 1:
#             return  

#         name, ok = QInputDialog.getText(
#             self,
#             "Нова група",
#             "Введіть назву групи:"
#         )
#         if not ok or not name.strip():
#             name = f"Група {len(self.parametric_groups) + 1}"
#         self.record_action_snapshot()

#         for group in self.parametric_groups:
#             group["handles"].difference_update(self.selected_handles)
#         self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]

#         new_group = {
#             "name": name.strip(),
#             "handles": set(self.selected_handles),
#             "k_w": 0.0, 
#             "k_h": 0.0,
#             "growth_p_w": 0.0, 
#             "growth_p_h": 0.0,
#             "growth_dir_x": "Центр",
#             "growth_dir_y": "Центр",
#             "shift_dir_x": "Вправо",
#             "shift_dir_y": "Вгору",
#             "link_x": "X = W",
#             "link_y": "Y = H",
#             "growth_axis": "both",
#             "resizes": False,
#             "role_y": "manual",
#             "auto_rule": False,
#             "touch_y_enabled": False,
#             "touch_to_uid": None,
#             "touch_gap_y": 0.0
#         }
#         self.get_group_key(new_group)
#         self.parametric_groups.append(new_group)
#         self.block_keep_state[new_group["uid"]] = True
#         self.clear_selection()
#         self.push_to_history()
#         self.save_project_config()
#         self.load_groups_into_list()
#         self.update_viewer()

#     def disband_parametric_group(self):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         del self.parametric_groups[idx]
#         self.clear_selection()
#         self.push_to_history()
#         self.save_project_config()
#         self.load_groups_into_list()
#         self.update_viewer()

#     def remove_selected_from_group(self):
#         selected_group_item = self.group_list_widget.currentItem()
#         if not selected_group_item or not self.selected_handles: return
#         self.record_action_snapshot()
        
#         idx = selected_group_item.data(Qt.ItemDataRole.UserRole)
#         group = self.parametric_groups[idx]
        
#         group["handles"] -= self.selected_handles
#         if not group["handles"]:
#             del self.parametric_groups[idx]
            
#         self.clear_selection()
#         self.push_to_history()
#         self.save_project_config()
#         self.load_groups_into_list()
#         self.update_viewer()

#     def load_groups_into_list(self):
#         self.group_list_widget.blockSignals(True)
#         self.group_list_widget.clear()
#         for idx, group in enumerate(self.parametric_groups):
#             name = group.get("name", f"Гр №{idx+1}")
#             role = group.get("role_y", "manual")
#             auto_mark = "⚙️" if group.get("auto_rule") else "✍️"
#             touch_mark = "🔗" if group.get("touch_y_enabled") else ""
#             axis_mark = {
#                 "both": "WH",
#                 "width": "W",
#                 "height": "H",
#                 "fixed": "fix",
#             }.get(self.project_meta.get("growth_axis", "both"), "WH")
#             text = f"🧩 {auto_mark}{touch_mark} {name} ({len(group['handles'])} об.) {axis_mark} Y:{role}"
#             key = self.get_group_key(group)
#             keep_mark = "keep" if self.block_keep_state.get(key, True) else "del"
#             size_mark = "size" if self.group_resizes(group) else "move"
#             link_x, link_y = self.link_pair_for_mode()
#             text = f"{auto_mark}{touch_mark} {name} [{axis_mark} {size_mark} {keep_mark} {link_x}/{link_y}] ({len(group['handles'])} об.) Y:{role}"
#             item = QListWidgetItem(text)
#             item.setToolTip(text)
#             item.setData(Qt.ItemDataRole.UserRole, idx)
#             self.group_list_widget.addItem(item)
#         self.group_list_widget.blockSignals(False)
#         self.load_block_filter_list()

#     def on_group_selection_changed(self):
#         selected = self.group_list_widget.selectedItems()
#         widgets_to_toggle = [
#             self.combo_k_w, self.combo_k_h, self.combo_growth_p_w, 
#             self.combo_growth_p_h, self.combo_growth_dir_x, self.combo_growth_dir_y,
#             self.combo_shift_dir_x, self.combo_shift_dir_y,
#             self.chk_group_resizes
#         ]
        
#         if not selected:
#             for widget in widgets_to_toggle: widget.setEnabled(False)
#             self.chk_group_resizes.blockSignals(True)
#             self.chk_group_resizes.setChecked(False)
#             self.chk_group_resizes.blockSignals(False)
#             self.apply_group_controls_visibility(None)
#             return
        
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         group = self.parametric_groups[idx]

#         for widget in widgets_to_toggle:
#             widget.blockSignals(True)
#             widget.setEnabled(True)
        
#         self.combo_k_w.setCurrentText(format_factor(group.get("k_w", 0.0)))
#         self.combo_k_h.setCurrentText(format_factor(group.get("k_h", 0.0)))
#         self.combo_growth_p_w.setCurrentText(format_factor(group.get("growth_p_w", 0.0)))
#         self.combo_growth_p_h.setCurrentText(format_factor(group.get("growth_p_h", 0.0)))
#         self.chk_group_resizes.setChecked(self.group_resizes(group))
        
#         self.combo_growth_dir_x.setCurrentText(group.get("growth_dir_x", "Вправо"))
#         self.combo_growth_dir_y.setCurrentText(group.get("growth_dir_y", "Вгору"))
#         self.combo_shift_dir_x.setCurrentText(group.get("shift_dir_x", "Вправо"))
#         self.combo_shift_dir_y.setCurrentText(group.get("shift_dir_y", "Вгору"))
        
#         self.apply_axis_link_mode_to_groups()
#         self.sync_link_combos_from_file_mode()

#         for widget in widgets_to_toggle:
#             widget.blockSignals(False)

#         self.apply_group_controls_visibility(group)
#         self.selected_handles = set(group["handles"])
#         self.sync_list_from_handles()
#         self.update_viewer()

#     def growth_axis_to_label(self, axis):
#         return {
#             "both": "Ширина + висота",
#             "width": "Тільки ширина",
#             "height": "Тільки висота",
#             "fixed": "Не росте",
#         }.get(axis, "Ширина + висота")

#     def growth_axis_from_label(self, label):
#         text = str(label)
#         if "Тільки ширина" in text:
#             return "width"
#         if "Тільки висота" in text:
#             return "height"
#         if "Не росте" in text:
#             return "fixed"
#         return "both"

#     def swap_growth_axis_for_quarter_turn(self, axis):
#         if axis == "width":
#             return "height"
#         if axis == "height":
#             return "width"
#         return axis

#     def update_growth_axis_after_transform(self, mode):
#         if mode not in ("ROT90", "ROT270"):
#             return
#         self.project_meta["growth_axis"] = self.swap_growth_axis_for_quarter_turn(
#             self.project_meta.get("growth_axis", "both")
#         )
#         for group in self.parametric_groups:
#             if "growth_axis" in group:
#                 group["growth_axis"] = self.swap_growth_axis_for_quarter_turn(
#                     group.get("growth_axis", "both")
#                 )
#         self.sync_file_growth_axis_combo()

#     def link_pair_for_mode(self, mode=None):
#         """Повертає пару прив'язок осей із режиму файлу.

#         У БД зберігаємо тільки AxisLinkMode:
#         - normal  => X = W, Y = H
#         - rotated => X = H, Y = W
#         """
#         mode = str(mode or self.project_meta.get("axis_link_mode") or "normal").strip().lower()
#         if mode == "rotated":
#             return "X = H", "Y = W"
#         return "X = W", "Y = H"

#     def axis_mode_from_link_x(self, link_x=None):
#         link_x = link_x or (self.combo_link_x.currentText() if hasattr(self, "combo_link_x") else "X = W")
#         return "rotated" if str(link_x).strip() == "X = H" else "normal"

#     def apply_axis_link_mode_to_groups(self):
#         """Синхронізує глобальну прив'язку осей з усіма групами."""
#         mode = str(self.project_meta.get("axis_link_mode") or "normal").strip().lower()
#         if mode not in ("normal", "rotated"):
#             mode = "normal"
#         self.project_meta["axis_link_mode"] = mode

#         link_x, link_y = self.link_pair_for_mode(mode)
#         self.project_meta["link_x"] = link_x
#         self.project_meta["link_y"] = link_y

#         for group in self.parametric_groups:
#             group["link_x"] = link_x
#             group["link_y"] = link_y

#     def sync_axis_inputs_from_meta(self):
#         """Виставляє combo X/Y за AxisLinkMode, а не навпаки."""
#         mode = str(self.project_meta.get("axis_link_mode") or "normal").strip().lower()
#         if mode not in ("normal", "rotated"):
#             mode = "normal"
#         self.project_meta["axis_link_mode"] = mode

#         link_x, link_y = self.link_pair_for_mode(mode)
#         self.project_meta["link_x"] = link_x
#         self.project_meta["link_y"] = link_y

#         if hasattr(self, "combo_link_x"):
#             self.combo_link_x.blockSignals(True)
#             self.combo_link_x.setCurrentText(link_x)
#             self.combo_link_x.blockSignals(False)

#         if hasattr(self, "combo_link_y"):
#             self.combo_link_y.blockSignals(True)
#             self.combo_link_y.setCurrentText(link_y)
#             self.combo_link_y.blockSignals(False)

#     def swap_axis_link_mode_for_quarter_turn(self, mode):
#         if mode not in ("ROT90", "ROT270"):
#             return
#         current = self.project_meta.get("axis_link_mode", "normal")
#         self.project_meta["axis_link_mode"] = "rotated" if current == "normal" else "normal"
#         self.apply_axis_link_mode_to_groups()
#         self.sync_link_combos_from_file_mode()

#     def set_param_grid_row_visible(self, row, visible):
#         grid = getattr(self, "param_transform_grid", None)
#         if not grid:
#             return
#         for col in range(grid.columnCount()):
#             item = grid.itemAtPosition(row, col)
#             if item and item.widget():
#                 item.widget().setVisible(visible)

#     def apply_growth_axis_ui(self, axis):
#         """Показує тільки ті осі, які дозволені режимом файлу.

#         Компактна сітка параметрів має рядки:
#         0 — X зсув, 1 — X ріст, 2 — Y зсув, 3 — Y ріст.
#         Ріст додатково ховається у apply_group_controls_visibility(),
#         якщо не ввімкнено галочку "Група змінює розмір".
#         """
#         self.set_param_grid_row_visible(0, axis in ("both", "width"))
#         self.set_param_grid_row_visible(2, axis in ("both", "height"))


#     def set_param_grid_cells_visible(self, row, columns, visible):
#         grid = getattr(self, "param_transform_grid", None)
#         if not grid:
#             return
#         for col in columns:
#             item = grid.itemAtPosition(row, col)
#             if item and item.widget():
#                 item.widget().setVisible(visible)

#     def group_resizes(self, group):
#         if not group:
#             return False
#         if "resizes" in group:
#             return bool(group.get("resizes"))
#         return (
#             abs(float(group.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
#             abs(float(group.get("growth_p_h", 0.0) or 0.0)) > 0.000001
#         )

#     def apply_group_controls_visibility(self, group):
#         """Показує поля росту тільки коли ввімкнено 'Група змінює розмір'."""
#         axis = self.project_meta.get("growth_axis", "both")
#         show_growth = self.group_resizes(group)

#         show_x = axis in ("both", "width")
#         show_y = axis in ("both", "height")

#         # Рядки компактної сітки:
#         # 0 — X зсув, 1 — X ріст, 2 — Y зсув, 3 — Y ріст.
#         self.set_param_grid_row_visible(0, show_x)
#         self.set_param_grid_row_visible(2, show_y)
#         self.set_param_grid_row_visible(1, show_x and show_growth)
#         self.set_param_grid_row_visible(3, show_y and show_growth)

#     def apply_growth_axis_to_group(self, group):
#         axis = self.project_meta.get("growth_axis", "both")
#         if not self.group_resizes(group):
#             group["growth_p_w"] = 0.0
#             group["growth_p_h"] = 0.0
#             group["growth_dir_x"] = "Центр"
#             group["growth_dir_y"] = "Центр"
#             return
#         if axis in ("height", "fixed"):
#             group["growth_p_w"] = 0.0
#             group["growth_dir_x"] = "Центр"
#         if axis in ("width", "fixed"):
#             group["growth_p_h"] = 0.0
#             group["growth_dir_y"] = "Центр"

#     def sync_file_growth_axis_combo(self):
#         if not hasattr(self, "combo_group_growth_axis"):
#             return
#         self.combo_group_growth_axis.blockSignals(True)
#         self.combo_group_growth_axis.setCurrentText(
#             self.growth_axis_to_label(self.project_meta.get("growth_axis", "both"))
#         )
#         self.combo_group_growth_axis.blockSignals(False)
#         current = self.group_list_widget.currentItem() if hasattr(self, "group_list_widget") else None
#         group = self.parametric_groups[current.data(Qt.ItemDataRole.UserRole)] if current else None
#         self.apply_group_controls_visibility(group)
#         self.update_file_status_panel()

#     def on_group_growth_axis_changed(self, text):
#         self.record_action_snapshot()
#         self.project_meta["growth_axis"] = self.growth_axis_from_label(text)
#         for group in self.parametric_groups:
#             self.apply_growth_axis_to_group(group)
#         current = self.group_list_widget.currentItem()
#         group = self.parametric_groups[current.data(Qt.ItemDataRole.UserRole)] if current else None
#         self.apply_group_controls_visibility(group)
#         self.save_project_config()
#         self.on_group_selection_changed()

#     def on_group_resizes_changed(self, state):
#         selected = self.group_list_widget.selectedItems()
#         if not selected:
#             self.apply_group_controls_visibility(None)
#             return

#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         if idx is None or idx < 0 or idx >= len(self.parametric_groups):
#             self.apply_group_controls_visibility(None)
#             return

#         group = self.parametric_groups[idx]

#         checked = state == Qt.CheckState.Checked or state == Qt.CheckState.Checked.value or bool(self.chk_group_resizes.isChecked())
#         group["resizes"] = bool(checked)

#         if not checked:
#             group["growth_p_w"] = 0.0
#             group["growth_p_h"] = 0.0
#             group["growth_dir_x"] = "Центр"
#             group["growth_dir_y"] = "Центр"
#         else:
#             # При вмиканні не задаємо ріст автоматично, тільки показуємо поля.
#             group.setdefault("growth_p_w", 0.0)
#             group.setdefault("growth_p_h", 0.0)
#             if group.get("growth_dir_x") in (None, ""):
#                 group["growth_dir_x"] = "Вправо"
#             if group.get("growth_dir_y") in (None, ""):
#                 group["growth_dir_y"] = "Вгору"

#         self.apply_growth_axis_to_group(group)
#         self.apply_group_controls_visibility(group)
#         self.save_project_config()
#         self.on_group_selection_changed()
#         self.update_viewer()

#     def on_combo_k_w_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["k_w"] = parse_factor(text)
#         self.save_project_config()

#     def on_combo_k_h_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["k_h"] = parse_factor(text)
#         self.save_project_config()

#     def on_combo_growth_p_w_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["growth_p_w"] = parse_factor(text)
#         self.save_project_config()

#     def on_combo_growth_p_h_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["growth_p_h"] = parse_factor(text)
#         self.save_project_config()

#     def on_link_x_changed(self, text=None):
#         self.record_action_snapshot()
#         self.project_meta["axis_link_mode"] = self.axis_mode_from_link_x(text)

#         self.apply_axis_link_mode_to_groups()
#         self.sync_axis_inputs_from_meta()
#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_file_status_panel()

#     def on_link_y_changed(self, text=None):
#         self.record_action_snapshot()
#         text = text or (self.combo_link_y.currentText() if hasattr(self, "combo_link_y") else "Y = H")
#         self.project_meta["axis_link_mode"] = "rotated" if str(text).strip() == "Y = W" else "normal"

#         self.apply_axis_link_mode_to_groups()
#         self.sync_axis_inputs_from_meta()
#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_file_status_panel()

#     def on_growth_dir_x_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["growth_dir_x"] = text
#         self.save_project_config()

#     def on_growth_dir_y_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["growth_dir_y"] = text
#         self.save_project_config()

#     def on_shift_dir_x_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["shift_dir_x"] = text
#         self.save_project_config()

#     def on_shift_dir_y_changed(self, text):
#         selected = self.group_list_widget.selectedItems()
#         if not selected: return
#         self.record_action_snapshot()
#         idx = selected[0].data(Qt.ItemDataRole.UserRole)
#         self.parametric_groups[idx]["shift_dir_y"] = text
#         self.save_project_config()



#     def group_center_y(self, group):
#         bbox = self.group_original_bbox(group)
#         if not bbox:
#             return 0.0
#         return (bbox[1] + bbox[3]) * 0.5

#     def group_center_x(self, group):
#         bbox = self.group_original_bbox(group)
#         if not bbox:
#             return 0.0
#         return (bbox[0] + bbox[2]) * 0.5

#     def ensure_topology_fields(self, group):
#         self.get_group_key(group)
#         group.setdefault("role_y", "manual")
#         group.setdefault("auto_rule", False)
#         group.setdefault("touch_y_enabled", False)
#         group.setdefault("touch_to_uid", None)
#         group.setdefault("touch_gap_y", 0.0)
#         group.setdefault("growth_axis", "both")
#         group.setdefault("resizes", (
#             abs(float(group.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
#             abs(float(group.get("growth_p_h", 0.0) or 0.0)) > 0.000001
#         ))
#         group.setdefault("auto_chain_x", False)
#         group.setdefault("chain_shift_x", 0.0)
#         group.setdefault("chain_growth_own_x", 0.0)
#         group.setdefault("chain_growth_after_x", 0.0)

#     def groups_overlap_by_x(self, bbox_a, bbox_b, tolerance=2.0):
#         if not bbox_a or not bbox_b:
#             return False
#         return not (bbox_a[2] < bbox_b[0] - tolerance or bbox_b[2] < bbox_a[0] - tolerance)

#     def auto_apply_vertical_topology_rules(self):
#         """
#         AUTO RULES Y / Авто правила Y.

#         Що робить:
#         1) бере всі параметричні групи, у яких є bbox;
#         2) рахує центр групи по Y;
#         3) знаходить найнижчий і найвищий центр;
#         4) перетворює позицію групи у коефіцієнт k_h:
#            - низ  => k_h = 0.0
#            - верх => k_h = 1.0
#            - середина => пропорційно, часто 0.5
#         5) записує це в JSON як auto_rule=True, role_y=bottom/middle/top.

#         ВАЖЛИВО:
#         ця кнопка НЕ рахує суму ростів. Для суми ростів є кнопка "Авто сума росту Y".
#         """
#         valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
#         if not valid_groups:
#             self.lbl_status_calc.setText("<font color='red'>Немає груп з геометрією для автоаналізу Y.</font>")
#             self.topology_debug_print("AUTO RULES Y: немає груп з bbox")
#             return

#         self.record_action_snapshot()

#         rows = []
#         rows.append("AUTO RULES Y / Авто правила Y")
#         rows.append("Сенс: програма сама визначає низ/середину/верх і ставить k_h.")
#         rows.append("Формула: k_h = (centerY - minCenterY) / (maxCenterY - minCenterY)")
#         rows.append("Потім: близько до низу => 0; близько до верху => 1; близько до центру => 0.5")
#         rows.append("")

#         centers = [self.group_center_y(g) for g in valid_groups]
#         min_c, max_c = min(centers), max(centers)
#         span = max(max_c - min_c, 0.0001)
#         rows.append(f"minCenterY={min_c:.3f}; maxCenterY={max_c:.3f}; span={span:.3f}")
#         rows.append("")

#         sorted_groups = sorted(valid_groups, key=self.group_center_y)
#         rows.append("Групи знизу вгору:")
#         for i, group in enumerate(sorted_groups, start=1):
#             bbox = self.group_original_bbox(group)
#             uid = self.get_group_key(group)
#             cy = self.group_center_y(group)
#             rows.append(
#                 f"  #{i}: name={group.get('name')} uid={uid} "
#                 f"bbox=(minY={bbox[1]:.3f}, maxY={bbox[3]:.3f}) centerY={cy:.3f}"
#             )
#         rows.append("")
#         rows.append("Рішення по кожній групі:")

#         for group in sorted_groups:
#             self.ensure_topology_fields(group)
#             uid = self.get_group_key(group)
#             bbox = self.group_original_bbox(group)
#             cy = self.group_center_y(group)
#             raw_k = (cy - min_c) / span
#             k = raw_k
#             reason = "пропорційне положення між низом і верхом"

#             if k < 0.15:
#                 role = "bottom"
#                 k = 0.0
#                 reason = "центр близько до нижнього краю => фіксуємо як НИЗ"
#             elif k > 0.85:
#                 role = "top"
#                 k = 1.0
#                 reason = "центр близько до верхнього краю => фіксуємо як ВЕРХ"
#             else:
#                 role = "middle"
#                 if abs(k - 0.5) < 0.18:
#                     k = 0.5
#                     reason = "центр близько до середини => ставимо 50%"

#             old_k_h = float(group.get("k_h", 0.0) or 0.0)
#             old_growth = float(group.get("growth_p_h", 0.0) or 0.0)
#             old_dir = group.get("growth_dir_y", "Центр")

#             group.update({
#                 "k_h": round(float(k), 4),
#                 "growth_p_h": 0.0,
#                 "growth_dir_y": "Центр",
#                 "link_y": "Y = H",
#                 "role_y": role,
#                 "auto_rule": True,
#             })

#             rows.append(
#                 f"  group={group.get('name')} uid={uid}: "
#                 f"centerY={cy:.3f}; raw_k={raw_k:.6f}; "
#                 f"old_k_h={old_k_h:.6f} -> new_k_h={k:.6f} ({k*100:.2f}%); "
#                 f"old_growth_p_h={old_growth:.6f} -> new_growth_p_h=0; "
#                 f"old_dir={old_dir} -> new_dir=Центр; role_y={role}; reason={reason}"
#             )

#         rows.append("")
#         rows.append("РЕЗУЛЬТАТ: Авто правила Y тільки розставляють позиційний зсув k_h: низ=0%, середина≈50%, верх=100%.")
#         rows.append("Якщо треба логіка 50% + 5% = 55%, натискай 'Авто сума росту Y'.")
#         self.topology_debug_print("AUTO RULES Y / Авто правила Y", rows)

#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_viewer()
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Авто правила Y застосовано. Деталі дивись у консолі: [TOPOLOGY DEBUG] AUTO RULES Y.</font>")

#     def topology_debug_print(self, title, rows=None):
#         """Єдиний формат логів у консоль для топологічних розрахунків."""
#         print("\n" + "=" * 90)
#         print(f"[TOPOLOGY DEBUG] {title}")
#         print("=" * 90)
#         if rows:
#             for row in rows:
#                 print(row)
#         print("=" * 90 + "\n")

#     def auto_layout_dimension_ratio(self, bbox, bounds, axis):
#         min_x, min_y, max_x, max_y = bounds
#         if axis == "x":
#             total = max(max_x - min_x, 0.0001)
#             return max((bbox[2] - bbox[0]) / total, 0.0)
#         total = max(max_y - min_y, 0.0001)
#         return max((bbox[3] - bbox[1]) / total, 0.0)
    

#     def format_factor(val):
#         """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
#         if abs(val - 0.0) < 0.001: return "0% (Фіксовано)"
#         if abs(val - 0.25) < 0.001: return "25% (1/4)"
#         if abs(val - 0.333) < 0.01: return "33.3% (Δ/3)"
#         if abs(val - 0.5) < 0.001: return "50% (Δ/2)"
#         if abs(val - 0.667) < 0.01: return "66.7% (Δ/3)"
#         if abs(val - 0.75) < 0.01: return  "75% (1/4)"
#         if abs(val - 1.0) < 0.001: return "100% (Δ)"
#         return f"{val*100:g}%"
    


#     def seed_auto_layout_growth(self):
#         bounds = self.get_non_text_dxf_bounds()
#         min_x, min_y, max_x, max_y = bounds
#         if min_x is None:
#             return []

#         width = max(max_x - min_x, 0.0001)
#         height = max(max_y - min_y, 0.0001)
#         edge_tol_x = max(width * 0.025, 2.0)
#         edge_tol_y = max(height * 0.025, 2.0)
#         rows = [
#             "AUTO LAYOUT SEED / start growth detection",
#             f"bounds: minX={min_x:.3f}, maxX={max_x:.3f}, minY={min_y:.3f}, maxY={max_y:.3f}",
#         ]

#         for group in self.parametric_groups:
#             bbox = self.group_original_bbox(group)
#             if not bbox:
#                 continue
#             self.ensure_topology_fields(group)
#             bx1, by1, bx2, by2 = bbox
#             ratio_x = self.auto_layout_dimension_ratio(bbox, bounds, "x")
#             ratio_y = self.auto_layout_dimension_ratio(bbox, bounds, "y")

#             axis = self.project_meta.get("growth_axis", "both")
#             if axis == "width":
#                 grow_x, grow_y = True, False
#             elif axis == "height":
#                 grow_x, grow_y = False, True
#             elif axis == "fixed":
#                 grow_x, grow_y = False, False
#             else:
#                 grow_x = ratio_x >= 0.55
#                 grow_y = ratio_y >= 0.55
#             group["link_x"] = "X = W"
#             group["link_y"] = "Y = H"
#             group["shift_dir_x"] = "Вправо"
#             group["shift_dir_y"] = "Вгору"
#             group["growth_p_w"] = 1.0 if grow_x else 0.0
#             group["growth_p_h"] = 1.0 if grow_y else 0.0

#             if grow_x:
#                 if abs(bx1 - min_x) <= edge_tol_x:
#                     group["growth_dir_x"] = "Вправо"
#                 elif abs(bx2 - max_x) <= edge_tol_x:
#                     group["growth_dir_x"] = "Вліво"
#                 else:
#                     group["growth_dir_x"] = "Центр"
#             else:
#                 group["growth_dir_x"] = "Центр"

#             if grow_y:
#                 if abs(by1 - min_y) <= edge_tol_y:
#                     group["growth_dir_y"] = "Вгору"
#                 elif abs(by2 - max_y) <= edge_tol_y:
#                     group["growth_dir_y"] = "Вниз"
#                 else:
#                     group["growth_dir_y"] = "Центр"
#             else:
#                 group["growth_dir_y"] = "Центр"

#             group["auto_layout"] = True
#             group["auto_layout_ratio_x"] = round(float(ratio_x), 6)
#             group["auto_layout_ratio_y"] = round(float(ratio_y), 6)
#             rows.append(
#                 f"{group.get('name')} uid={self.get_group_key(group)}: "
#                 f"ratioX={ratio_x:.3f}, ratioY={ratio_y:.3f}, "
#                 f"growthX={group['growth_p_w']:.1f} dirX={group['growth_dir_x']}, "
#                 f"growthY={group['growth_p_h']:.1f} dirY={group['growth_dir_y']}"
#             )
#         return rows

#     def finish_auto_layout_position_rules(self):
#         bounds = self.get_non_text_dxf_bounds()
#         min_x, min_y, max_x, max_y = bounds
#         if min_x is None:
#             return []

#         width = max(max_x - min_x, 0.0001)
#         height = max(max_y - min_y, 0.0001)
#         edge_tol_x = max(width * 0.025, 2.0)
#         edge_tol_y = max(height * 0.025, 2.0)
#         rows = ["AUTO LAYOUT FINISH / position shifts for fixed groups"]

#         for group in self.parametric_groups:
#             bbox = self.group_original_bbox(group)
#             if not bbox:
#                 continue
#             bx1, by1, bx2, by2 = bbox
#             cx = (bx1 + bx2) * 0.5
#             cy = (by1 + by2) * 0.5

#             if abs(float(group.get("growth_p_w", 0.0) or 0.0)) <= 0.000001:
#                 if abs(bx1 - min_x) <= edge_tol_x:
#                     k_w = 0.0
#                     reason_x = "left edge"
#                 elif abs(bx2 - max_x) <= edge_tol_x:
#                     k_w = 1.0
#                     reason_x = "right edge"
#                 else:
#                     k_w = (cx - min_x) / width
#                     reason_x = "relative center X"
#                 group["k_w"] = round(float(max(0.0, min(1.0, k_w))), 6)
#                 group["link_x"] = "X = W"
#                 group["shift_dir_x"] = "Вправо"
#                 rows.append(f"{group.get('name')}: k_w={group['k_w']:.6f} ({reason_x})")

#             if abs(float(group.get("growth_p_h", 0.0) or 0.0)) <= 0.000001:
#                 if abs(by1 - min_y) <= edge_tol_y:
#                     k_h = 0.0
#                     reason_y = "bottom edge"
#                 elif abs(by2 - max_y) <= edge_tol_y:
#                     k_h = 1.0
#                     reason_y = "top edge"
#                 else:
#                     k_h = (cy - min_y) / height
#                     reason_y = "relative center Y"
#                 group["k_h"] = round(float(max(0.0, min(1.0, k_h))), 6)
#                 group["link_y"] = "Y = H"
#                 group["shift_dir_y"] = "Вгору"
#                 rows.append(f"{group.get('name')}: k_h={group['k_h']:.6f} ({reason_y})")

#         return rows

#     def auto_layout_all_groups(self):
#         valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
#         if not valid_groups:
#             self.lbl_status_calc.setText("<font color='red'>Немає параметричних груп з геометрією для авторозстановки.</font>")
#             return

#         self.record_action_snapshot()
#         rows = ["AUTHOROZSTAVYTY ALL / Авторозставити все"]
#         rows.extend(self.seed_auto_layout_growth())

#         self.suppress_auto_chain_snapshot = True
#         try:
#             self.auto_chain_growth_x()
#             self.auto_chain_growth_y()
#         finally:
#             self.suppress_auto_chain_snapshot = False

#         rows.extend(self.finish_auto_layout_position_rules())
#         rows.append("Done: old k/growth coefficients are filled automatically; manual controls remain available.")

#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_viewer()
#         self.topology_debug_print("AUTHOROZSTAVYTY ALL / Авторозставити все", rows)
#         self.lbl_status_calc.setText("<font color='#a5d6a7'>Авторозставлення виконано: ріст і зсуви заповнені автоматично.</font>")

#     def auto_chain_growth_y(self):
#         """
#         AUTO CHAIN Y / Авто сума росту Y, але НЕ одним загальним списком.

#         ВАЖЛИВО:
#         - ліва вертикальна сторона рахується окремо;
#         - права вертикальна сторона рахується окремо;
#         - центр рахується від середнього/узгодженого результату лівої і правої сторони;
#         - групи, які лежать на одному Y-рівні, НЕ складаються одна з одною як 50%+50%.
#           Для одного рівня береться максимальний ріст рівня, бо це одна і та сама висотна зона.

#         Це виправляє ситуацію з логу:
#             1 росте 50%
#             рп1 росте 50%
#         Вони не мають давати 100%, якщо це ліва/права сторона одного рівня.
#         """
#         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
#         if min_x is None:
#             self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автоматичної суми росту Y.</font>")
#             self.topology_debug_print("AUTO CHAIN Y SIDES: немає геометрії")
#             return

#         axis_x = (min_x + max_x) * 0.5
#         width = max_x - min_x
#         height = max_y - min_y
#         center_tolerance_x = max(width * 0.015, 2.0)
#         level_tolerance_y = max(height * 0.003, 0.5)
#         balance_tolerance = 0.0005  # 0.05%

#         left_items = []
#         right_items = []
#         center_items = []

#         for group in self.parametric_groups:
#             bbox = self.group_original_bbox(group)
#             if not bbox:
#                 continue
#             self.ensure_topology_fields(group)
#             uid = self.get_group_key(group)
#             bx1, by1, bx2, by2 = bbox
#             center_x = (bx1 + bx2) * 0.5
#             center_y = (by1 + by2) * 0.5
#             growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))

#             item = {
#                 "group": group,
#                 "uid": uid,
#                 "name": group.get("name", ""),
#                 "bbox": bbox,
#                 "min_x": bx1,
#                 "max_x": bx2,
#                 "min_y": by1,
#                 "max_y": by2,
#                 "center_x": center_x,
#                 "center_y": center_y,
#                 "growth": growth,
#             }

#             # Якщо користувач уже вручну задав side_x у JSON — поважаємо це.
#             explicit_side = str(group.get("side_x", "")).strip().lower()
#             if explicit_side in ("left", "right", "center"):
#                 side = explicit_side
#             elif center_x < axis_x - center_tolerance_x:
#                 side = "left"
#             elif center_x > axis_x + center_tolerance_x:
#                 side = "right"
#             else:
#                 side = "center"

#             item["side"] = side
#             if side == "left":
#                 left_items.append(item)
#             elif side == "right":
#                 right_items.append(item)
#             else:
#                 center_items.append(item)

#         if not left_items and not right_items and not center_items:
#             self.lbl_status_calc.setText("<font color='red'>Немає груп для автоматичної суми росту Y.</font>")
#             self.topology_debug_print("AUTO CHAIN Y SIDES: немає валідних груп")
#             return

#         def sort_bottom_up(items):
#             items.sort(key=lambda item: (item["center_y"], item["min_y"], item["center_x"]))

#         sort_bottom_up(left_items)
#         sort_bottom_up(right_items)
#         sort_bottom_up(center_items)

#         def make_levels(items):
#             """Об'єднує групи з майже однаковим center_y в один висотний рівень."""
#             levels = []
#             for item in items:
#                 placed = False
#                 for level in levels:
#                     if abs(level["center_y"] - item["center_y"]) <= level_tolerance_y:
#                         level["items"].append(item)
#                         # Плавно уточнюємо центр рівня, щоб не залежати від першого елемента.
#                         level["center_y"] = sum(x["center_y"] for x in level["items"]) / len(level["items"])
#                         level["min_y"] = min(level["min_y"], item["min_y"])
#                         level["max_y"] = max(level["max_y"], item["max_y"])
#                         placed = True
#                         break
#                 if not placed:
#                     levels.append({
#                         "center_y": item["center_y"],
#                         "min_y": item["min_y"],
#                         "max_y": item["max_y"],
#                         "items": [item],
#                     })
#             levels.sort(key=lambda level: (level["center_y"], level["min_y"]))
#             for level in levels:
#                 # Рівень — це одна висотна зона. Не складаємо 50%+50% для паралельних деталей одного рівня.
#                 level["growth"] = max((x["growth"] for x in level["items"]), default=0.0)
#             return levels

#         left_levels = make_levels(left_items)
#         right_levels = make_levels(right_items)
#         center_levels = make_levels(center_items)

#         left_sum = sum(level["growth"] for level in left_levels)
#         right_sum = sum(level["growth"] for level in right_levels)
#         diff = abs(left_sum - right_sum)

#         rows = []
#         rows.append("AUTO CHAIN Y SIDES / Авто сума росту Y по лівій/правій стороні")
#         rows.append("Тепер це НЕ один список знизу вгору для всіх груп.")
#         rows.append("Ліва сторона, права сторона і центр розділяються по X.")
#         rows.append("Групи на одному Y-рівні не додаються одна до одної: для рівня береться MAX growth_p_h.")
#         rows.append("")
#         rows.append(f"bounds: minX={min_x:.3f}, maxX={max_x:.3f}, minY={min_y:.3f}, maxY={max_y:.3f}")
#         rows.append(f"axis_x={axis_x:.3f}, center_tolerance_x={center_tolerance_x:.3f}, level_tolerance_y={level_tolerance_y:.3f}")
#         rows.append("")

#         def describe_side(side_name, items, levels):
#             rows.append(f"{side_name} groups після поділу по X:")
#             if not items:
#                 rows.append("  немає")
#             for i, item in enumerate(items, start=1):
#                 rows.append(
#                     f"  {side_name[0]}#{i}: name={item['name']} uid={item['uid']} side={item['side']} "
#                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}, "
#                     f"minY={item['min_y']:.3f}, maxY={item['max_y']:.3f}) "
#                     f"centerX={item['center_x']:.3f}; centerY={item['center_y']:.3f}; "
#                     f"own_growth_p_h={item['growth']:.6f} ({item['growth']*100:.2f}%)"
#                 )
#             rows.append(f"{side_name} Y-рівні:")
#             if not levels:
#                 rows.append("  немає")
#             for j, level in enumerate(levels, start=1):
#                 names = ", ".join(f"{x['name']}[{x['uid']}]" for x in level["items"])
#                 item_growths = ", ".join(f"{x['growth']*100:.2f}%" for x in level["items"])
#                 rows.append(
#                     f"  level {j}: centerY≈{level['center_y']:.3f}; items={names}; "
#                     f"item_growths=[{item_growths}]; level_growth=MAX={level['growth']:.6f} ({level['growth']*100:.2f}%)"
#                 )
#             rows.append("")

#         describe_side("LEFT", left_items, left_levels)
#         describe_side("RIGHT", right_items, right_levels)
#         describe_side("CENTER", center_items, center_levels)

#         rows.append(f"SUM LEFT LEVELS  = {left_sum:.6f} ({left_sum*100:.2f}%)")
#         rows.append(f"SUM RIGHT LEVELS = {right_sum:.6f} ({right_sum*100:.2f}%)")
#         rows.append(f"DIFF             = {diff:.6f} ({diff*100:.2f}%)")

#         normalize_to = None
#         has_both_sides = bool(left_levels) and bool(right_levels)
#         if has_both_sides and diff > balance_tolerance:
#             rows.append("")
#             rows.append("WARNING: ліва і права сторона мають різний сумарний ріст по Y.")
#             rows.append("Перед записом k_h треба уточнити у конструктора.")
#             self.topology_debug_print("AUTO CHAIN Y SIDES / ПОТРІБНЕ УТОЧНЕННЯ", rows)

#             msg = (
#                 "Сумарний ріст по Y зліва і справа різний.\n\n"
#                 f"LEFT = {left_sum*100:.2f}%\n"
#                 f"RIGHT = {right_sum*100:.2f}%\n"
#                 f"DIFF = {diff*100:.2f}%\n\n"
#                 "Так — вирівняти до більшої суми пропорційно.\n"
#                 "Ні — застосувати як є, з різними зсувами.\n"
#                 "Cancel — нічого не змінювати."
#             )
#             answer = QMessageBox.question(
#                 self,
#                 "Y-сторони мають різний сумарний ріст",
#                 msg,
#                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
#                 QMessageBox.StandardButton.Cancel,
#             )

#             if answer == QMessageBox.StandardButton.Cancel:
#                 rows.append("КОНСТРУКТОР СКАСУВАВ: правила Y не застосовано.")
#                 self.topology_debug_print("AUTO CHAIN Y SIDES / Скасовано", rows)
#                 self.lbl_status_calc.setText("<font color='#ffcc80'>Авто сума Y скасована: сторони мали різний сумарний ріст.</font>")
#                 return

#             if answer == QMessageBox.StandardButton.Yes:
#                 normalize_to = max(left_sum, right_sum)
#                 rows.append("")
#                 rows.append(f"КОНСТРУКТОР ОБРАВ ВИРІВНЯТИ: target_sum={normalize_to:.6f} ({normalize_to*100:.2f}%)")
#             else:
#                 rows.append("")
#                 rows.append("КОНСТРУКТОР ОБРАВ ЗАСТОСУВАТИ ЯК Є: ліва/права сторона можуть мати різні k_h.")
#         elif has_both_sides:
#             rows.append("OK: сумарний ріст лівої і правої сторони по Y однаковий у межах допуску.")
#         else:
#             rows.append("INFO: знайдена тільки одна сторона або тільки центр; порівнювати LEFT/RIGHT немає з чим.")

#         if not getattr(self, "suppress_auto_chain_snapshot", False):
#             self.record_action_snapshot()

#         def scale_levels(levels, current_sum, target_sum, side_name):
#             if target_sum is None or abs(current_sum - target_sum) <= balance_tolerance:
#                 return
#             if current_sum <= 0.000001:
#                 rows.append(
#                     f"NORMALIZE {side_name}: поточна сума 0%, неможливо пропорційно масштабувати. "
#                     f"Задай growth_p_h хоча б для одного рівня цієї сторони вручну."
#                 )
#                 return
#             factor = target_sum / current_sum
#             rows.append(
#                 f"NORMALIZE {side_name}: current_sum={current_sum:.6f} -> target_sum={target_sum:.6f}; factor={factor:.6f}"
#             )
#             for level in levels:
#                 old_level_growth = level["growth"]
#                 new_level_growth = old_level_growth * factor
#                 level["growth"] = new_level_growth
#                 rows.append(
#                     f"  {side_name} level centerY≈{level['center_y']:.3f}: "
#                     f"level_growth {old_level_growth:.6f} -> {new_level_growth:.6f} "
#                     f"({old_level_growth*100:.2f}% -> {new_level_growth*100:.2f}%)"
#                 )
#                 # Масштабуємо тільки ті групи рівня, які реально мали ріст.
#                 for item in level["items"]:
#                     g = item["group"]
#                     old = abs(float(g.get("growth_p_h", 0.0) or 0.0))
#                     if old > 0.000001:
#                         new_val = old * factor
#                         g["growth_p_h"] = round(float(new_val), 6)
#                         item["growth"] = new_val
#                         rows.append(
#                             f"    {side_name} {g.get('name')} uid={item['uid']}: growth_p_h {old:.6f} -> {new_val:.6f} "
#                             f"({old*100:.2f}% -> {new_val*100:.2f}%)"
#                         )

#         if normalize_to is not None:
#             scale_levels(left_levels, left_sum, normalize_to, "LEFT")
#             scale_levels(right_levels, right_sum, normalize_to, "RIGHT")
#             left_sum = sum(level["growth"] for level in left_levels)
#             right_sum = sum(level["growth"] for level in right_levels)
#             diff = abs(left_sum - right_sum)
#             rows.append("")
#             rows.append("Після вирівнювання:")
#             rows.append(f"SUM LEFT LEVELS  = {left_sum:.6f} ({left_sum*100:.2f}%)")
#             rows.append(f"SUM RIGHT LEVELS = {right_sum:.6f} ({right_sum*100:.2f}%)")
#             rows.append(f"DIFF             = {diff:.6f} ({diff*100:.2f}%)")

#         def apply_levels(levels, side_name):
#             cumulative = 0.0
#             rows.append("")
#             rows.append(f"Застосування {side_name} Y-chain:")
#             for level_index, level in enumerate(levels, start=1):
#                 before = cumulative
#                 level_growth = float(level.get("growth", 0.0) or 0.0)
#                 rows.append(
#                     f"  {side_name} level {level_index}: centerY≈{level['center_y']:.3f}; "
#                     f"sum_below={before:.6f} ({before*100:.2f}%); "
#                     f"level_growth={level_growth:.6f} ({level_growth*100:.2f}%)"
#                 )
#                 for item in level["items"]:
#                     group = item["group"]
#                     uid = item["uid"]
#                     old_k = float(group.get("k_h", 0.0) or 0.0)
#                     old_growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))

#                     group["k_h"] = round(float(before), 6)
#                     group["growth_p_h"] = round(float(old_growth), 6)
#                     if old_growth > 0.000001:
#                         group["growth_dir_y"] = "Вгору"
#                     group["link_y"] = "Y = H"
#                     group["side_y_chain"] = side_name.lower()
#                     group["auto_chain_y"] = True
#                     group["auto_chain_y_mode"] = "side_levels"
#                     group["chain_shift_y"] = round(float(before), 6)
#                     group["chain_growth_own_y"] = round(float(old_growth), 6)
#                     group["chain_level_growth_y"] = round(float(level_growth), 6)
#                     group["chain_growth_after_y"] = round(float(before + level_growth), 6)

#                     rows.append(
#                         f"    {side_name} {group.get('name')} uid={uid}: "
#                         f"old_k_h={old_k:.6f} -> new_k_h={before:.6f} ({before*100:.2f}%); "
#                         f"own_growth_p_h={old_growth:.6f} ({old_growth*100:.2f}%); "
#                         f"level_growth_used={level_growth:.6f} ({level_growth*100:.2f}%); "
#                         f"dir={group.get('growth_dir_y')}"
#                     )
#                 cumulative += level_growth
#             rows.append(f"  {side_name} final cumulative={cumulative:.6f} ({cumulative*100:.2f}%)")
#             return cumulative

#         final_left = apply_levels(left_levels, "LEFT") if left_levels else 0.0
#         final_right = apply_levels(right_levels, "RIGHT") if right_levels else 0.0

#         # Центр не складається сам із собою. Для центральних груп беремо shift на їхньому Y-рівні
#         # як середнє між лівою і правою стороною для такого самого рівня.
#         def shift_at_y(levels, y):
#             cumulative = 0.0
#             for level in levels:
#                 if level["center_y"] < y - level_tolerance_y:
#                     cumulative += float(level.get("growth", 0.0) or 0.0)
#             return cumulative

#         rows.append("")
#         rows.append("Застосування CENTER Y-chain:")
#         if center_levels:
#             for level in center_levels:
#                 center_y = level["center_y"]
#                 left_shift = shift_at_y(left_levels, center_y) if left_levels else None
#                 right_shift = shift_at_y(right_levels, center_y) if right_levels else None
#                 if left_shift is not None and right_shift is not None:
#                     center_shift = (left_shift + right_shift) * 0.5
#                     reason = f"average(left_shift={left_shift:.6f}, right_shift={right_shift:.6f})"
#                 elif left_shift is not None:
#                     center_shift = left_shift
#                     reason = f"left_shift={left_shift:.6f}"
#                 elif right_shift is not None:
#                     center_shift = right_shift
#                     reason = f"right_shift={right_shift:.6f}"
#                 else:
#                     center_shift = 0.0
#                     reason = "no side levels"

#                 level_growth = float(level.get("growth", 0.0) or 0.0)
#                 for item in level["items"]:
#                     group = item["group"]
#                     uid = item["uid"]
#                     old_k = float(group.get("k_h", 0.0) or 0.0)
#                     old_growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))
#                     group["k_h"] = round(float(center_shift), 6)
#                     group["growth_p_h"] = round(float(old_growth), 6)
#                     if old_growth > 0.000001:
#                         group["growth_dir_y"] = "Вгору"
#                     group["link_y"] = "Y = H"
#                     group["side_y_chain"] = "center"
#                     group["auto_chain_y"] = True
#                     group["auto_chain_y_mode"] = "side_levels_center"
#                     group["chain_shift_y"] = round(float(center_shift), 6)
#                     group["chain_growth_own_y"] = round(float(old_growth), 6)
#                     group["chain_level_growth_y"] = round(float(level_growth), 6)
#                     rows.append(
#                         f"  CENTER {group.get('name')} uid={uid}: old_k_h={old_k:.6f} -> new_k_h={center_shift:.6f} "
#                         f"({center_shift*100:.2f}%); own_growth={old_growth:.6f}; reason={reason}"
#                     )
#         else:
#             rows.append("  немає")

#         rows.append("")
#         rows.append("ФІНАЛ Y:")
#         rows.append(f"  LEFT total  = {final_left:.6f} ({final_left*100:.2f}%)")
#         rows.append(f"  RIGHT total = {final_right:.6f} ({final_right*100:.2f}%)")
#         rows.append(f"  DIFF        = {abs(final_left-final_right):.6f} ({abs(final_left-final_right)*100:.2f}%)")
#         rows.append("  Тепер 1 і рп1 не складаються у 100%, якщо вони є лівою/правою стороною одного рівня.")

#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_viewer()
#         self.topology_debug_print("AUTO CHAIN Y SIDES / Авто сума росту Y по сторонах", rows)

#         if has_both_sides and abs(final_left - final_right) <= balance_tolerance:
#             self.lbl_status_calc.setText(
#                 f"<font color='#a5d6a7'>Авто сума Y по сторонах застосована. LEFT≈RIGHT={final_left*100:.1f}%.</font>"
#             )
#         else:
#             self.lbl_status_calc.setText(
#                 f"<font color='#ffcc80'>Авто сума Y застосована: LEFT={final_left*100:.1f}%, RIGHT={final_right*100:.1f}%.</font>"
#             )

#     def auto_chain_growth_x(self):
#         """
#         AUTO CHAIN X / Авто сума росту X, але правильно для дверей/вікон:

#         ВАЖЛИВО:
#         - ліва сторона рахується окремо: від лівого краю до центру;
#         - права сторона рахується окремо: від правого краю до центру;
#         - сумарний growth_p_w лівої сторони порівнюється із сумарним growth_p_w правої сторони;
#         - якщо суми різні, програма питає конструктора, що робити.

#         Для лівої сторони:
#             k_w = сума ростів лівіше
#             growth_dir_x = Вправо

#         Для правої сторони:
#             k_w = 1 - сума ростів правіше
#             growth_dir_x = Вліво

#         Приклад:
#             LEFT:  10% + 15% = 25%
#             RIGHT: 5% + 20%  = 25%
#             => OK, сторони збалансовані.

#             LEFT:  25%
#             RIGHT: 30%
#             => WARNING, треба уточнення конструктора.
#         """
#         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
#         if min_x is None:
#             self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автоматичної суми росту X.</font>")
#             self.topology_debug_print("AUTO CHAIN X SIDES: немає геометрії")
#             return

#         axis_x = (min_x + max_x) * 0.5
#         width = max_x - min_x
#         center_tolerance = max(width * 0.015, 2.0)

#         left_items = []
#         right_items = []
#         center_items = []

#         for group in self.parametric_groups:
#             bbox = self.group_original_bbox(group)
#             if not bbox:
#                 continue
#             self.ensure_topology_fields(group)
#             uid = self.get_group_key(group)
#             bx1, by1, bx2, by2 = bbox
#             center_x = (bx1 + bx2) * 0.5

#             item = {
#                 "group": group,
#                 "uid": uid,
#                 "name": group.get("name", ""),
#                 "bbox": bbox,
#                 "min_x": bx1,
#                 "max_x": bx2,
#                 "center_x": center_x,
#                 "growth": abs(float(group.get("growth_p_w", 0.0) or 0.0)),
#             }

#             if center_x < axis_x - center_tolerance:
#                 item["side"] = "left"
#                 left_items.append(item)
#             elif center_x > axis_x + center_tolerance:
#                 item["side"] = "right"
#                 right_items.append(item)
#             else:
#                 item["side"] = "center"
#                 center_items.append(item)

#         if not left_items and not right_items:
#             self.lbl_status_calc.setText("<font color='red'>Не знайдено лівих/правих груп для X-логіки.</font>")
#             self.topology_debug_print("AUTO CHAIN X SIDES: немає лівих/правих груп")
#             return

#         left_items.sort(key=lambda item: (item["center_x"], item["min_x"]))
#         # Права сторона рахується від правого краю до центру.
#         right_items.sort(key=lambda item: (-item["center_x"], -item["max_x"]))
#         center_items.sort(key=lambda item: (item["center_x"], item["min_x"]))

#         left_sum = sum(item["growth"] for item in left_items)
#         right_sum = sum(item["growth"] for item in right_items)
#         diff = abs(left_sum - right_sum)
#         balance_tolerance = 0.0005  # 0.05%

#         rows = []
#         rows.append("AUTO CHAIN X SIDES / Авто сума росту X по сторонах")
#         rows.append("НЕ один загальний ланцюг зліва направо, а два незалежні ланцюги:")
#         rows.append("  LEFT:  лівий край -> центр, growth_dir_x=Вправо")
#         rows.append("  RIGHT: правий край -> центр, growth_dir_x=Вліво")
#         rows.append("Після цього програма порівнює сумарний % росту LEFT і RIGHT.")
#         rows.append("")
#         rows.append(f"bounds_x: minX={min_x:.3f}, maxX={max_x:.3f}, width={width:.3f}")
#         rows.append(f"axis_x={axis_x:.3f}, center_tolerance={center_tolerance:.3f}")
#         rows.append("")

#         rows.append("LEFT groups, від лівого краю до центру:")
#         if left_items:
#             for i, item in enumerate(left_items, start=1):
#                 rows.append(
#                     f"  L#{i}: name={item['name']} uid={item['uid']} "
#                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
#                     f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
#                 )
#         else:
#             rows.append("  немає")

#         rows.append("")
#         rows.append("RIGHT groups, від правого краю до центру:")
#         if right_items:
#             for i, item in enumerate(right_items, start=1):
#                 rows.append(
#                     f"  R#{i}: name={item['name']} uid={item['uid']} "
#                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
#                     f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
#                 )
#         else:
#             rows.append("  немає")

#         rows.append("")
#         rows.append("CENTER groups, біля центру, не беруть участь у сумі сторін:")
#         if center_items:
#             for i, item in enumerate(center_items, start=1):
#                 rows.append(
#                     f"  C#{i}: name={item['name']} uid={item['uid']} "
#                     f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
#                     f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
#                 )
#         else:
#             rows.append("  немає")

#         rows.append("")
#         rows.append(f"SUM LEFT  = {left_sum:.6f} ({left_sum*100:.2f}%)")
#         rows.append(f"SUM RIGHT = {right_sum:.6f} ({right_sum*100:.2f}%)")
#         rows.append(f"DIFF      = {diff:.6f} ({diff*100:.2f}%)")

#         # Якщо суми не рівні, перед застосуванням питаємо конструктора.
#         normalize_to = None
#         if diff > balance_tolerance:
#             rows.append("")
#             rows.append("WARNING: Сумарний ріст лівої і правої сторони НЕ однаковий.")
#             rows.append("Програма має уточнити у конструктора перед записом k_w.")
#             self.topology_debug_print("AUTO CHAIN X SIDES / ПОТРІБНЕ УТОЧНЕННЯ", rows)

#             msg = (
#                 "Сумарний ріст лівої і правої сторони різний.\n\n"
#                 f"LEFT = {left_sum*100:.2f}%\n"
#                 f"RIGHT = {right_sum*100:.2f}%\n"
#                 f"DIFF = {diff*100:.2f}%\n\n"
#                 "Так — вирівняти до більшої суми пропорційно.\n"
#                 "Ні — застосувати як є, з різними зсувами.\n"
#                 "Cancel — нічого не змінювати."
#             )
#             answer = QMessageBox.question(
#                 self,
#                 "X-сторони мають різний сумарний ріст",
#                 msg,
#                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
#                 QMessageBox.StandardButton.Cancel,
#             )

#             if answer == QMessageBox.StandardButton.Cancel:
#                 rows.append("КОНСТРУКТОР СКАСУВАВ: правила X не застосовано.")
#                 self.topology_debug_print("AUTO CHAIN X SIDES / Скасовано", rows)
#                 self.lbl_status_calc.setText("<font color='#ffcc80'>Авто сума X скасована: сторони мали різний сумарний ріст.</font>")
#                 return

#             if answer == QMessageBox.StandardButton.Yes:
#                 normalize_to = max(left_sum, right_sum)
#                 rows.append("")
#                 rows.append(f"КОНСТРУКТОР ОБРАВ ВИРІВНЯТИ: target_sum={normalize_to:.6f} ({normalize_to*100:.2f}%)")
#             else:
#                 rows.append("")
#                 rows.append("КОНСТРУКТОР ОБРАВ ЗАСТОСУВАТИ ЯК Є: ліві і праві зсуви можуть відрізнятися.")
#         else:
#             rows.append("OK: Сумарний ріст лівої і правої сторони однаковий у межах допуску.")

#         if not getattr(self, "suppress_auto_chain_snapshot", False):
#             self.record_action_snapshot()

#         def scale_side(items, current_sum, target_sum, side_name):
#             if target_sum is None or abs(current_sum - target_sum) <= balance_tolerance:
#                 return
#             if current_sum <= 0.000001:
#                 rows.append(
#                     f"NORMALIZE {side_name}: поточна сума 0%, неможливо пропорційно масштабувати. "
#                     f"Задай growth_p_w хоча б для однієї групи цієї сторони вручну."
#                 )
#                 return
#             factor = target_sum / current_sum
#             rows.append(
#                 f"NORMALIZE {side_name}: current_sum={current_sum:.6f} -> target_sum={target_sum:.6f}; "
#                 f"factor={factor:.6f}"
#             )
#             for item in items:
#                 g = item["group"]
#                 old = abs(float(g.get("growth_p_w", 0.0) or 0.0))
#                 new_val = old * factor
#                 g["growth_p_w"] = round(float(new_val), 6)
#                 item["growth"] = new_val
#                 rows.append(
#                     f"  {side_name} {g.get('name')} uid={item['uid']}: growth_p_w {old:.6f} -> {new_val:.6f} "
#                     f"({old*100:.2f}% -> {new_val*100:.2f}%)"
#                 )

#         if normalize_to is not None:
#             scale_side(left_items, left_sum, normalize_to, "LEFT")
#             scale_side(right_items, right_sum, normalize_to, "RIGHT")
#             left_sum = sum(item["growth"] for item in left_items)
#             right_sum = sum(item["growth"] for item in right_items)
#             diff = abs(left_sum - right_sum)
#             rows.append("")
#             rows.append("Після вирівнювання:")
#             rows.append(f"SUM LEFT  = {left_sum:.6f} ({left_sum*100:.2f}%)")
#             rows.append(f"SUM RIGHT = {right_sum:.6f} ({right_sum*100:.2f}%)")
#             rows.append(f"DIFF      = {diff:.6f} ({diff*100:.2f}%)")

#         rows.append("")
#         rows.append("Застосування LEFT chain:")
#         cumulative_left = 0.0
#         for item in left_items:
#             group = item["group"]
#             uid = item["uid"]
#             old_k = float(group.get("k_w", 0.0) or 0.0)
#             own_growth = abs(float(group.get("growth_p_w", 0.0) or 0.0))
#             new_k = cumulative_left

#             group["k_w"] = round(float(new_k), 6)
#             group["growth_p_w"] = round(float(own_growth), 6)
#             group["growth_dir_x"] = "Вправо" if own_growth > 0.000001 else group.get("growth_dir_x", "Центр")
#             group["link_x"] = "X = W"
#             group["side_x"] = "left"
#             group["auto_chain_x"] = True
#             group["auto_chain_x_mode"] = "side_sum"
#             group["chain_shift_x"] = round(float(new_k), 6)
#             group["chain_growth_own_x"] = round(float(own_growth), 6)

#             before = cumulative_left
#             cumulative_left += own_growth
#             group["chain_growth_after_x"] = round(float(cumulative_left), 6)
#             group["side_sum_x"] = round(float(left_sum), 6)

#             rows.append(
#                 f"  LEFT {group.get('name')} uid={uid}: "
#                 f"old_k_w={old_k:.6f} -> new_k_w=sum_from_left={new_k:.6f} ({new_k*100:.2f}%); "
#                 f"own_growth={own_growth:.6f} ({own_growth*100:.2f}%); "
#                 f"sum_before={before:.6f}; sum_after={cumulative_left:.6f}; dir={group.get('growth_dir_x')}"
#             )

#         rows.append("")
#         rows.append("Застосування RIGHT chain:")
#         cumulative_right = 0.0
#         for item in right_items:
#             group = item["group"]
#             uid = item["uid"]
#             old_k = float(group.get("k_w", 0.0) or 0.0)
#             own_growth = abs(float(group.get("growth_p_w", 0.0) or 0.0))
#             # Права сторона прив'язана до правого краю.
#             # Найправіша група має k_w=1.0, а кожен внутрішній ріст справа зменшує k_w для наступних до центру.
#             new_k = 1.0 - cumulative_right

#             group["k_w"] = round(float(new_k), 6)
#             group["growth_p_w"] = round(float(own_growth), 6)
#             group["growth_dir_x"] = "Вліво" if own_growth > 0.000001 else group.get("growth_dir_x", "Центр")
#             group["link_x"] = "X = W"
#             group["side_x"] = "right"
#             group["auto_chain_x"] = True
#             group["auto_chain_x_mode"] = "side_sum"
#             group["chain_shift_x"] = round(float(new_k), 6)
#             group["chain_growth_own_x"] = round(float(own_growth), 6)

#             before = cumulative_right
#             cumulative_right += own_growth
#             group["chain_growth_after_x"] = round(float(cumulative_right), 6)
#             group["side_sum_x"] = round(float(right_sum), 6)

#             rows.append(
#                 f"  RIGHT {group.get('name')} uid={uid}: "
#                 f"old_k_w={old_k:.6f} -> new_k_w=1-sum_from_right={new_k:.6f} ({new_k*100:.2f}%); "
#                 f"own_growth={own_growth:.6f} ({own_growth*100:.2f}%); "
#                 f"sum_before={before:.6f}; sum_after={cumulative_right:.6f}; dir={group.get('growth_dir_x')}"
#             )

#         rows.append("")
#         rows.append("CENTER groups:")
#         center_k = left_sum if diff <= balance_tolerance or normalize_to is not None else (left_sum + (1.0 - right_sum)) * 0.5
#         for item in center_items:
#             group = item["group"]
#             old_k = float(group.get("k_w", 0.0) or 0.0)
#             group["k_w"] = round(float(center_k), 6)
#             group["link_x"] = "X = W"
#             group["side_x"] = "center"
#             group["auto_chain_x"] = True
#             group["auto_chain_x_mode"] = "side_sum_center"
#             group["chain_shift_x"] = round(float(center_k), 6)
#             group["side_sum_left_x"] = round(float(left_sum), 6)
#             group["side_sum_right_x"] = round(float(right_sum), 6)
#             rows.append(
#                 f"  CENTER {group.get('name')} uid={item['uid']}: old_k_w={old_k:.6f} -> new_k_w={center_k:.6f} "
#                 f"({center_k*100:.2f}%). Це центральна зона між лівою і правою сторонами."
#             )

#         rows.append("")
#         rows.append("ФІНАЛ:")
#         rows.append(f"  LEFT total  = {left_sum:.6f} ({left_sum*100:.2f}%)")
#         rows.append(f"  RIGHT total = {right_sum:.6f} ({right_sum*100:.2f}%)")
#         rows.append(f"  DIFF        = {abs(left_sum-right_sum):.6f} ({abs(left_sum-right_sum)*100:.2f}%)")
#         rows.append("  Ліві/праві групи можуть мати різні k_w, але сумарний % росту сторін контролюється.")

#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_viewer()
#         self.topology_debug_print("AUTO CHAIN X SIDES / Авто сума росту X по сторонах", rows)

#         if abs(left_sum - right_sum) <= balance_tolerance:
#             self.lbl_status_calc.setText(
#                 f"<font color='#a5d6a7'>Авто сума X по сторонах застосована. LEFT=RIGHT={left_sum*100:.1f}%.</font>"
#             )
#         else:
#             self.lbl_status_calc.setText(
#                 f"<font color='#ffcc80'>Авто сума X застосована з різними сторонами: LEFT={left_sum*100:.1f}%, RIGHT={right_sum*100:.1f}%.</font>"
#             )

#     def auto_detect_vertical_touch_constraints(self, tolerance=3.0):
#         """
#         TOUCH Y / Зберігати дотик Y.

#         Що робить:
#         1) очищає старі touch-зв'язки;
#         2) сортує групи знизу вгору;
#         3) для кожної нижньої групи шукає найближчу верхню групу;
#         4) перевіряє, чи вони перетинаються по X, тобто реально стоять одна над одною;
#         5) рахує gap = upper.minY - lower.maxY;
#         6) якщо gap від 0 до tolerance, записує:
#            lower.touch_y_enabled = True
#            lower.touch_to_uid = upper.uid
#            lower.touch_gap_y = gap

#         Під час глобального перерахунку calculate_touch_extra_y_shifts() тримає цей gap.
#         """
#         valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
#         if len(valid_groups) < 2:
#             self.lbl_status_calc.setText("<font color='red'>Потрібно мінімум дві групи для пошуку дотику.</font>")
#             self.topology_debug_print("TOUCH Y: потрібно мінімум дві групи")
#             return

#         self.record_action_snapshot()
#         rows = []
#         rows.append("TOUCH Y / Зберігати дотик Y")
#         rows.append(f"tolerance={tolerance:.3f} мм")
#         rows.append("Сенс: якщо нижня група торкається верхньої або має малий зазор, програма запам'ятовує цей зазор.")
#         rows.append("Потім при перерахунку верхня група додатково зсувається, щоб gap залишився такий самий.")
#         rows.append("")

#         for group in valid_groups:
#             self.ensure_topology_fields(group)
#             uid = self.get_group_key(group)
#             old_enabled = group.get("touch_y_enabled")
#             old_to = group.get("touch_to_uid")
#             old_gap = group.get("touch_gap_y")
#             group["touch_y_enabled"] = False
#             group["touch_to_uid"] = None
#             group["touch_gap_y"] = 0.0
#             rows.append(f"Очистка старого touch: group={group.get('name')} uid={uid}; old_enabled={old_enabled}; old_to={old_to}; old_gap={old_gap}")

#         sorted_groups = sorted(valid_groups, key=self.group_center_y)
#         rows.append("")
#         rows.append("Групи знизу вгору:")
#         for i, group in enumerate(sorted_groups, start=1):
#             bbox = self.group_original_bbox(group)
#             rows.append(
#                 f"  #{i}: name={group.get('name')} uid={self.get_group_key(group)} "
#                 f"bbox=(minX={bbox[0]:.3f}, minY={bbox[1]:.3f}, maxX={bbox[2]:.3f}, maxY={bbox[3]:.3f})"
#             )

#         constraints_count = 0
#         rows.append("")
#         rows.append("Пошук найближчої верхньої групи для кожної нижньої:")

#         for lower in sorted_groups:
#             lower_uid = self.get_group_key(lower)
#             lower_bbox = self.group_original_bbox(lower)
#             best_upper = None
#             best_gap = None

#             rows.append(f"\nLOWER group={lower.get('name')} uid={lower_uid}; lower_top=maxY={lower_bbox[3]:.3f}")

#             for upper in sorted_groups:
#                 if upper is lower:
#                     continue
#                 upper_uid = self.get_group_key(upper)
#                 upper_bbox = self.group_original_bbox(upper)
#                 overlap_x = self.groups_overlap_by_x(lower_bbox, upper_bbox, tolerance=tolerance)
#                 gap = upper_bbox[1] - lower_bbox[3]

#                 if not overlap_x:
#                     rows.append(
#                         f"  candidate upper={upper.get('name')} uid={upper_uid}: SKIP, "
#                         f"немає перетину по X; gap={gap:.3f}"
#                     )
#                     continue
#                 if gap < -tolerance:
#                     rows.append(
#                         f"  candidate upper={upper.get('name')} uid={upper_uid}: SKIP, "
#                         f"накладання по Y більше tolerance; gap={gap:.3f}"
#                     )
#                     continue

#                 rows.append(
#                     f"  candidate upper={upper.get('name')} uid={upper_uid}: OK candidate, "
#                     f"overlap_x=True; gap=upper.minY({upper_bbox[1]:.3f}) - lower.maxY({lower_bbox[3]:.3f}) = {gap:.3f}"
#                 )

#                 if best_gap is None or gap < best_gap:
#                     best_gap = gap
#                     best_upper = upper

#             if best_upper is not None and best_gap is not None and best_gap <= tolerance:
#                 upper_uid = self.get_group_key(best_upper)
#                 lower["touch_y_enabled"] = True
#                 lower["touch_to_uid"] = upper_uid
#                 lower["touch_gap_y"] = float(best_gap)
#                 constraints_count += 1
#                 rows.append(
#                     f"  => TOUCH SAVED: lower={lower_uid} -> upper={upper_uid}; "
#                     f"saved_gap_y={best_gap:.3f} мм"
#                 )
#             else:
#                 rows.append("  => TOUCH NOT SAVED: немає верхньої групи в межах tolerance")

#         rows.append("")
#         rows.append(f"РЕЗУЛЬТАТ: знайдено touch-зв'язків Y = {constraints_count}")
#         rows.append("Під час перерахунку буде лог [TOUCH DEBUG] START TOUCH Y CORRECTION — там видно корекцію у мм.")
#         self.topology_debug_print("TOUCH Y / Зберігати дотик Y", rows)

#         self.save_project_config()
#         self.load_groups_into_list()
#         self.update_viewer()
#         self.lbl_status_calc.setText(
#             f"<font color='#a5d6a7'>Знайдено вертикальних зв'язків дотику: {constraints_count}. Деталі дивись у консолі: [TOPOLOGY DEBUG] TOUCH Y.</font>"
#         )

#     # ============================================================
#     # РУХОМИЙ ПОЧАТКОВИЙ TEXT / MTEXT
#     # ============================================================
#     def on_existing_dxf_text_moved(self, item):
#         """
#         Коли користувач перетягнув TEXT/MTEXT, який вже був у початковому DXF,
#         ми оновлюємо insert у самому DXF і зберігаємо файл.
#         """
#         handle = getattr(item, "handle", None)
#         if not handle or handle not in self.doc.entitydb:
#             print(f"[TEXT MOVE DEBUG] handle={handle} не знайдено в DXF entitydb")
#             return

#         entity = self.doc.entitydb[handle]
#         tp = entity.dxftype()
#         pos = item.pos()
#         old_insert = tuple(entity.dxf.insert) if hasattr(entity.dxf, "insert") else None

#         # У сцені Y інвертований: CAD y = -scene_y - text_height.
#         text_height = float(getattr(entity.dxf, "height", 10.0) or 10.0)
#         new_x = float(pos.x())
#         new_y = float(-pos.y() - text_height)

#         if tp in ("TEXT", "MTEXT"):
#             entity.dxf.insert = (new_x, new_y, 0.0)

#         self.selected_handles = {handle}
#         self.doc.saveas(self.dxf_path)
#         self.save_original_geometries()
#         self.load_entities_into_list()
#         self.sync_list_from_handles()
#         self.save_project_config()

#         print("\n" + "=" * 90)
#         print("[TEXT MOVE DEBUG] Початковий текст DXF перетягнуто")
#         print("=" * 90)
#         print(f"handle={handle}; type={tp}")
#         print(f"old_insert={old_insert}")
#         print(f"scene_pos=(x={pos.x():.3f}, y={pos.y():.3f})")
#         print(f"new_dxf_insert=(x={new_x:.3f}, y={new_y:.3f}, z=0.000)")
#         print("Файл DXF збережено.")
#         print("=" * 90 + "\n")

#     # ============================================================
#     # ДЗЕРКАЛЬНІ СТОРОНИ X З ПІДТВЕРДЖЕННЯМ КОНСТРУКТОРА
#     # ============================================================
#     def bbox_signature_for_mirror(self, bbox, axis_x):
#         """
#         Нормалізований підпис bbox відносно центральної осі.
#         Для дзеркальних лівої/правої сторін відстані від осі мають збігатися.
#         """
#         min_x, min_y, max_x, max_y = bbox
#         dist_near = min(abs(min_x - axis_x), abs(max_x - axis_x))
#         dist_far = max(abs(min_x - axis_x), abs(max_x - axis_x))
#         return (round(dist_near, 1), round(dist_far, 1), round(min_y, 1), round(max_y, 1))

#     def find_mirror_x_group_pairs(self, tolerance=2.0):
#         """
#         Шукає пари груп, які виглядають як дзеркальні ліва/права сторона.
#         Порівнюємо bbox відносно центральної осі конструкції.
#         """
#         min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
#         if min_x is None:
#             return None, []

#         axis_x = (min_x + max_x) * 0.5
#         valid = []
#         for group in self.parametric_groups:
#             bbox = self.group_original_bbox(group)
#             if not bbox:
#                 continue
#             self.ensure_topology_fields(group)
#             uid = self.get_group_key(group)
#             cx = (bbox[0] + bbox[2]) * 0.5
#             side = "left" if cx < axis_x - tolerance else ("right" if cx > axis_x + tolerance else "center")
#             valid.append({"group": group, "uid": uid, "bbox": bbox, "cx": cx, "side": side})

#         left = [x for x in valid if x["side"] == "left"]
#         right = [x for x in valid if x["side"] == "right"]
#         pairs = []
#         used_right = set()

#         for l in left:
#             l_sig = self.bbox_signature_for_mirror(l["bbox"], axis_x)
#             best = None
#             best_score = None
#             for r in right:
#                 if r["uid"] in used_right:
#                     continue
#                 r_sig = self.bbox_signature_for_mirror(r["bbox"], axis_x)
#                 score = sum(abs(a - b) for a, b in zip(l_sig, r_sig))
#                 if best is None or score < best_score:
#                     best = r
#                     best_score = score
#             if best is not None and best_score is not None and best_score <= tolerance * 4:
#                 pairs.append((l, best, best_score))
#                 used_right.add(best["uid"])

#         return axis_x, pairs

#     def proposed_mirror_growth_value(self, left_group, right_group):
#         """
#         Якщо на одній стороні вже заданий ріст, копіюємо його на другу.
#         Якщо на обох різний — беремо середнє і показуємо це в діалозі.
#         """
#         gl = abs(float(left_group.get("growth_p_w", 0.0) or 0.0))
#         gr = abs(float(right_group.get("growth_p_w", 0.0) or 0.0))
#         if gl > 0 and gr == 0:
#             return gl, "взято ріст лівої сторони"
#         if gr > 0 and gl == 0:
#             return gr, "взято ріст правої сторони"
#         if gl > 0 and gr > 0 and abs(gl - gr) > 0.000001:
#             return (gl + gr) * 0.5, "обидві сторони мали різний ріст, взято середнє"
#         return max(gl, gr), "обидві сторони вже однакові або ріст 0%"

#     def confirm_and_apply_mirror_x_rules(self):
#         """
#         Перевіряє, чи ліва і права сторони дзеркальні.
#         Якщо так — показує конструктору список знайдених пар і тільки після підтвердження
#         прописує однаковий growth_p_w для обох сторін.
#         """
#         axis_x, pairs = self.find_mirror_x_group_pairs(tolerance=2.0)
#         rows = []
#         rows.append("MIRROR X / Дзеркальні сторони X")
#         rows.append("Сенс: якщо ліва і права сторони однакові дзеркально, їм треба дати однаковий % розтягування.")
#         rows.append("Перед записом правил програма питає підтвердження конструктора.")
#         rows.append("")
#         rows.append(f"axis_x={axis_x if axis_x is not None else 'None'}")
#         rows.append(f"found_pairs={len(pairs)}")

#         if axis_x is None or not pairs:
#             self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows + ["РЕЗУЛЬТАТ: дзеркальних пар не знайдено."])
#             self.lbl_status_calc.setText("<font color='red'>Дзеркальних ліво/право груп не знайдено.</font>")
#             return

#         message_lines = [
#             "Знайдено дзеркальні ліво/право пари.",
#             "Прописати їм однаковий відсоток розтягування по X?",
#             "",
#         ]

#         proposals = []
#         for i, (l, r, score) in enumerate(pairs, start=1):
#             gval, reason = self.proposed_mirror_growth_value(l["group"], r["group"])
#             proposals.append((l, r, gval, reason, score))
#             line = (
#                 f"{i}) {l['group'].get('name')} ↔ {r['group'].get('name')}: "
#                 f"growth_p_w = {gval*100:.2f}% ({reason})"
#             )
#             message_lines.append(line)
#             rows.append(
#                 f"pair#{i}: left={l['group'].get('name')} uid={l['uid']} bbox={tuple(round(v,3) for v in l['bbox'])}; "
#                 f"right={r['group'].get('name')} uid={r['uid']} bbox={tuple(round(v,3) for v in r['bbox'])}; "
#                 f"score={score:.3f}; proposed_growth={gval:.6f}; reason={reason}"
#             )

#         answer = QMessageBox.question(
#             self,
#             "Підтвердити дзеркальні правила X",
#             "\n".join(message_lines),
#             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
#             QMessageBox.StandardButton.No,
#         )

#         if answer != QMessageBox.StandardButton.Yes:
#             rows.append("КОНСТРУКТОР ВІДХИЛИВ: правила не записано.")
#             self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows)
#             self.lbl_status_calc.setText("<font color='#ffcc80'>Дзеркальні правила X не застосовано.</font>")
#             return

#         self.record_action_snapshot()
#         rows.append("")
#         rows.append("КОНСТРУКТОР ПІДТВЕРДИВ: записуємо однакове розтягування.")

#         for l, r, gval, reason, score in proposals:
#             lg = l["group"]
#             rg = r["group"]
#             old_l = float(lg.get("growth_p_w", 0.0) or 0.0)
#             old_r = float(rg.get("growth_p_w", 0.0) or 0.0)

#             lg["growth_p_w"] = round(float(gval), 6)
#             rg["growth_p_w"] = round(float(gval), 6)
#             lg["growth_dir_x"] = "Вліво"
#             rg["growth_dir_x"] = "Вправо"
#             lg["link_x"] = "X = W"
#             rg["link_x"] = "X = W"
#             lg["auto_mirror_x"] = True
#             rg["auto_mirror_x"] = True
#             lg["mirror_pair_uid"] = r["uid"]
#             rg["mirror_pair_uid"] = l["uid"]

#             rows.append(
#                 f"APPLY: {lg.get('name')} old_growth={old_l:.6f} -> {gval:.6f}, dir=Вліво; "
#                 f"{rg.get('name')} old_growth={old_r:.6f} -> {gval:.6f}, dir=Вправо"
#             )

#         self.save_project_config()
#         self.load_groups_into_list()
#         self.on_group_selection_changed()
#         self.update_viewer()
#         self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows)
#         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Дзеркальні правила X застосовано для пар: {len(proposals)}.</font>")

#     def calculate_touch_extra_y_shifts(self, cur_w, cur_h, target_w, target_h):
#         """
#         Повертає додатковий Y-зсув для груп, щоб зберегти початковий вертикальний дотик/зазор.
#         Формат: {uid: extra_shift_y}.
#         """
#         uid_to_group = {}
#         uid_to_bbox = {}
#         extra = {}

#         for group in self.parametric_groups:
#             if not self.group_original_bbox(group):
#                 continue
#             uid = self.get_group_key(group)
#             uid_to_group[uid] = group
#             bbox = self.simulated_group_bbox(group, cur_w, cur_h, target_w, target_h)
#             if bbox:
#                 uid_to_bbox[uid] = list(bbox)
#                 extra[uid] = 0.0

#         if len(uid_to_bbox) < 2:
#             if self.debug_output:
#                 print("[TOUCH DEBUG] Not enough groups for touch correction")
#             return extra

#         if self.debug_output:
#             print("\n" + "=" * 90)
#             print("[TOUCH DEBUG] START TOUCH Y CORRECTION")
#             for _uid, _bbox in uid_to_bbox.items():
#                 _g = uid_to_group[_uid]
#                 print(f"[TOUCH DEBUG] before uid={_uid}; name={_g.get('name')}; bbox={tuple(round(v,3) for v in _bbox)}; enabled={_g.get('touch_y_enabled')}; to={_g.get('touch_to_uid')}; gap={_g.get('touch_gap_y')}")

#         # Проходимо знизу вгору, щоб верхні деталі піднімались/опускались разом з тими, до кого вони прив'язані.
#         sorted_groups = sorted(uid_to_group.values(), key=self.group_center_y)
#         for _ in range(max(1, len(sorted_groups))):
#             changed = False
#             for lower in sorted_groups:
#                 if not lower.get("touch_y_enabled"):
#                     continue
#                 lower_uid = self.get_group_key(lower)
#                 upper_uid = lower.get("touch_to_uid")
#                 if lower_uid not in uid_to_bbox or upper_uid not in uid_to_bbox:
#                     continue

#                 lower_bbox = uid_to_bbox[lower_uid]
#                 upper_bbox = uid_to_bbox[upper_uid]
#                 wanted_gap = float(lower.get("touch_gap_y", 0.0) or 0.0)
#                 wanted_upper_min_y = lower_bbox[3] + wanted_gap
#                 correction = wanted_upper_min_y - upper_bbox[1]

#                 if abs(correction) > 0.001:
#                     if self.debug_output:
#                         print(
#                             f"[TOUCH DEBUG] lower={lower_uid} -> upper={upper_uid}; "
#                             f"wanted_gap={wanted_gap:.3f}; lower_top={lower_bbox[3]:.3f}; "
#                             f"upper_min_before={upper_bbox[1]:.3f}; correction={correction:.3f}"
#                         )
#                     uid_to_bbox[upper_uid][1] += correction
#                     uid_to_bbox[upper_uid][3] += correction
#                     extra[upper_uid] = extra.get(upper_uid, 0.0) + correction
#                     changed = True
#             if not changed:
#                 break

#         if self.debug_output:
#             print(f"[TOUCH DEBUG] extra result={extra}")
#             print("=" * 90 + "\n")
#         return extra

#     def process_parametric_percentage_scale(self, save_result=True, record_history=True):
#         try:
#             cur_w = float(self.input_current_width.text().strip())
#             target_w = float(self.input_target_width.text().strip())
#             cur_h = float(self.input_current_height.text().strip())
#             target_h = float(self.input_target_height.text().strip())
#         except ValueError:
#             return False

#         self.collect_text_settings_from_inputs()
#         if not self.validate_target_size_or_warn(cur_w, cur_h, target_w, target_h):
#             return False

#         should_record = save_result and record_history and not self.is_loading_history
#         if should_record:
#             before_snapshot = self.capture_full_state_snapshot()
#             self.history.save_state()
#             self.history.clear_redo()
#             self.save_zones_history_state()
#             self.zones_redo_stack.clear()
#             self.global_recalc_undo_stack.append(before_snapshot)
#             self.global_recalc_redo_stack.clear()
#             if len(self.global_recalc_undo_stack) > 30:
#                 self.global_recalc_undo_stack.pop(0)

#         delta_w = target_w - cur_w
#         delta_h = target_h - cur_h
#         if self.debug_output:
#             print("\n" + "=" * 90)
#             print("[RECALC DEBUG] START GLOBAL PARAMETRIC RECALC")
#             print(f"[RECALC DEBUG] cur_w={cur_w}, target_w={target_w}, delta_w={delta_w}")
#             print(f"[RECALC DEBUG] cur_h={cur_h}, target_h={target_h}, delta_h={delta_h}")
#             print("[RECALC DEBUG] Groups:")
#             for _g in self.parametric_groups:
#                 _uid = self.get_group_key(_g)
#                 print(
#                     f"  uid={_uid}; name={_g.get('name')}; "
#                     f"k_w={_g.get('k_w')}; growth_p_w={_g.get('growth_p_w')}; dir_x={_g.get('growth_dir_x')}; link_x={_g.get('link_x')}; "
#                     f"k_h={_g.get('k_h')}; growth_p_h={_g.get('growth_p_h')}; dir_y={_g.get('growth_dir_y')}; link_y={_g.get('link_y')}; "
#                     f"auto_chain_y={_g.get('auto_chain_y')}; chain_shift_y={_g.get('chain_shift_y')}; chain_growth_after_y={_g.get('chain_growth_after_y')}"
#                 )
#         touch_extra_y = self.calculate_touch_extra_y_shifts(cur_w, cur_h, target_w, target_h)
#         if self.debug_output:
#             print(f"[RECALC DEBUG] touch_extra_y={touch_extra_y}")
#         self.project_meta["source_width"] = cur_w
#         self.project_meta["source_height"] = cur_h
#         self.project_meta["target_width"] = target_w
#         self.project_meta["target_height"] = target_h

#         for hndl, orig in self.original_geometries.items():
#             if hndl not in self.doc.entitydb: continue
#             entity = self.doc.entitydb[hndl]

#             associated_group = None
#             for group in self.parametric_groups:
#                 if hndl in group["handles"]:
#                     associated_group = group
#                     break

#             if associated_group is None:
#                 if orig["type"] == "LINE":
#                     entity.dxf.start = orig["start"]
#                     entity.dxf.end = orig["end"]
#                 elif orig["type"] in ("CIRCLE", "ARC"):
#                     entity.dxf.center = orig["center"]
#                     entity.dxf.radius = orig["radius"]
#                 elif orig["type"] == "TEXT":
#                     entity.dxf.insert = orig["insert"]
#                     entity.dxf.height = orig["height"]
#                     entity.dxf.width = orig["width"]
#                     entity.dxf.rotation = orig["rotation"]
#                 continue

#             shift_v, growth_v = ParametricEngine.get_transform(delta_w, delta_h, associated_group)
#             if self.debug_output:
#                 print(
#                     f"[RECALC DEBUG] handle={hndl}; type={orig.get('type')}; "
#                     f"group={associated_group.get('name')} uid={self.get_group_key(associated_group)}; "
#                     f"base_shift=(x={shift_v[0]:.3f}, y={shift_v[1]:.3f}); "
#                     f"growth=(x={growth_v[0]:.3f}, y={growth_v[1]:.3f}); "
#                     f"k_w={associated_group.get('k_w')}; k_h={associated_group.get('k_h')}; "
#                     f"shift_dir_x={associated_group.get('shift_dir_x')}; shift_dir_y={associated_group.get('shift_dir_y')}; "
#                     f"growth_p_w={associated_group.get('growth_p_w')}; growth_p_h={associated_group.get('growth_p_h')}"
#                 )
           
#             group_uid = self.get_group_key(associated_group)
#             extra_y = touch_extra_y.get(group_uid, 0.0)
#             if abs(extra_y) > 0.0001:
#                 if self.debug_output:
#                     print(f"[RECALC DEBUG]   touch correction extra_y={extra_y:.3f} applied to group uid={group_uid}")
#                 shift_v = (shift_v[0], shift_v[1] + extra_y, shift_v[2])
            
#             growth_dir_x = associated_group.get("growth_dir_x", "Центр")
#             growth_dir_y = associated_group.get("growth_dir_y", "Центр")

#             if orig["type"] == "LINE":
#                 sx, sy, sz = orig["start"]
#                 ex, ey, ez = orig["end"]

#                 dsx, dsy = shift_v[0], shift_v[1]
#                 dex, dey = shift_v[0], shift_v[1]

#                 # --- ЛОГІКА ПО X (ШИРИНА) ---
#                 if sx < ex: left_p, right_p = "S", "E"
#                 elif sx > ex: left_p, right_p = "E", "S"
#                 else: left_p, right_p = "BOTH", "BOTH"

#                 if growth_dir_x == "Вправо":
#                     if right_p in ("S", "BOTH"): dsx += growth_v[0]
#                     if right_p in ("E", "BOTH"): dex += growth_v[0]
#                 elif growth_dir_x == "Вліво":
#                     if left_p in ("S", "BOTH"): dsx -= growth_v[0]
#                     if left_p in ("E", "BOTH"): dex -= growth_v[0]
#                 else: # Центр
#                     if left_p == "S": dsx -= growth_v[0] * 0.5
#                     if right_p == "S": dsx += growth_v[0] * 0.5
#                     if left_p == "E": dex -= growth_v[0] * 0.5
#                     if right_p == "E": dex += growth_v[0] * 0.5

#                 # --- ЛОГІКА ПО Y (ВИСОТА) ---
#                 if sy < ey: bottom_p, top_p = "S", "E"
#                 elif sy > ey: bottom_p, top_p = "E", "S"
#                 else: bottom_p, top_p = "BOTH", "BOTH"

#                 if growth_dir_y == "Вгору":
#                     if top_p in ("S", "BOTH"): dsy += growth_v[1]
#                     if top_p in ("E", "BOTH"): dey += growth_v[1]
#                 elif growth_dir_y == "Вниз":
#                     if bottom_p in ("S", "BOTH"): dsy -= growth_v[1]
#                     if bottom_p in ("E", "BOTH"): dey -= growth_v[1]
#                 else: # Центр
#                     if bottom_p == "S": dsy -= growth_v[1] * 0.5
#                     if top_p == "S": dsy += growth_v[1] * 0.5
#                     if bottom_p == "E": dey -= growth_v[1] * 0.5
#                     if top_p == "E": dey += growth_v[1] * 0.5

#                 entity.dxf.start = (sx + dsx, sy + dsy, sz)
#                 entity.dxf.end = (ex + dex, ey + dey, ez)

#             elif orig["type"] in ("CIRCLE", "ARC"):
#                 cx, cy, cz = orig["center"]
#                 r = orig["radius"]

#                 entity.dxf.center = (cx + shift_v[0], cy + shift_v[1], cz)

#                 new_r = r
#                 if growth_v[0] != 0.0 or growth_v[1] != 0.0:
#                     scale_factor = 1.0 + ((abs(growth_v[0]) + abs(growth_v[1])) / (cur_w + cur_h))
#                     new_r = r * scale_factor

#                 entity.dxf.radius = new_r

#             elif orig["type"] == "TEXT":
#                 x, y, z = orig["insert"]
#                 new_x = x + shift_v[0]
#                 new_y = y + shift_v[1]
#                 new_height = max(float(orig["height"]) + growth_v[1], 0.1)
#                 new_width = max(float(orig["width"]), 0.01)
#                 if growth_v[0] != 0.0:
#                     new_width = max(float(orig["width"]) + growth_v[0], 0.01)
#                 entity.dxf.insert = (new_x, new_y, z)
#                 entity.dxf.height = new_height
#                 entity.dxf.width = new_width

#                 settings = self.get_text_settings()
#                 if settings.get("handle") == hndl:
#                     settings["x"] = new_x
#                     settings["y"] = new_y
#                     settings["height"] = new_height
#                     settings["width_factor"] = new_width
#                     self.project_meta["door_text"] = settings

#         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔW={delta_w:+.1f} мм | ΔH={delta_h:+.1f} мм</font>")
#         self.apply_door_text_to_doc()
#         if save_result:
#             self.doc.saveas(self.dxf_path)
#         if not getattr(self, "suppress_project_config_save", False):
#             self.save_project_config()
#         if should_record:
#             self.history.save_state()
#             self.save_zones_history_state()
#             self.global_recalc_redo_stack.clear()
#             self.update_history_buttons_state()
#         self.update_viewer()
#         return True

#     # def commit_current_geometry_as_parametric_base(self, reason="", update_source_dimensions=True, preserve_target_dimensions=True):
#     #     """
#     #     Робить поточну геометрію DXF новою базою для параметричного перерахунку.

#     #     Навіщо:
#     #     - preview/process_parametric_percentage_scale() не рахує від поточного DXF напряму;
#     #     - він бере self.original_geometries як "початкову геометрію";
#     #     - після ROT/MIRROR потрібно оновити self.original_geometries, інакше "Перегляд"
#     #       застосує правила до геометрії ДО оберту.
#     #     """
#     #     old_source_w = self.project_meta.get("source_width")
#     #     old_source_h = self.project_meta.get("source_height")
#     #     old_target_w = self.project_meta.get("target_width")
#     #     old_target_h = self.project_meta.get("target_height")

#     #     self.save_original_geometries()

#     #     if update_source_dimensions:
#     #         new_w, new_h = self.get_dxf_bounds_dimensions()
#     #         if new_w is not None and new_h is not None:
#     #             self.project_meta["source_width"] = new_w
#     #             self.project_meta["source_height"] = new_h

#     #             # target_width/target_height не чіпаємо, якщо користувач уже задав новий розмір.
#     #             # Але якщо target був порожній або дорівнював старому source, синхронізуємо з новою базою,
#     #             # щоб після оберту поля не залишались у старій орієнтації.
#     #             if not preserve_target_dimensions:
#     #                 self.project_meta["target_width"] = new_w
#     #                 self.project_meta["target_height"] = new_h
#     #             else:
#     #                 if old_target_w is None or (old_source_w is not None and abs(float(old_target_w) - float(old_source_w)) < 0.001):
#     #                     self.project_meta["target_width"] = new_w
#     #                 if old_target_h is None or (old_source_h is not None and abs(float(old_target_h) - float(old_source_h)) < 0.001):
#     #                     self.project_meta["target_height"] = new_h

#     #     print("\n" + "=" * 90)
#     #     print("[BASE DEBUG] PARAMETRIC BASE UPDATED")
#     #     print(f"[BASE DEBUG] reason={reason}")
#     #     print(f"[BASE DEBUG] source before: W={old_source_w}, H={old_source_h}")
#     #     print(f"[BASE DEBUG] source after : W={self.project_meta.get('source_width')}, H={self.project_meta.get('source_height')}")
#     #     print(f"[BASE DEBUG] target after : W={self.project_meta.get('target_width')}, H={self.project_meta.get('target_height')}")
#     #     print(f"[BASE DEBUG] original_geometries handles={len(self.original_geometries)}")
#     #     print("=" * 90)

#     #     self.update_dimension_inputs_from_meta()

#     def commit_current_geometry_as_parametric_base(
#         self,
#         reason="",
#         update_source_dimensions=False,
#         preserve_target_dimensions=True
#     ):
#         """
#         Робить поточну геометрію DXF новою базою для параметричного перерахунку,
#         але НЕ міняє значення у полях ширини та висоти.
#         """

#         old_source_w = self.project_meta.get("source_width")
#         old_source_h = self.project_meta.get("source_height")
#         old_target_w = self.project_meta.get("target_width")
#         old_target_h = self.project_meta.get("target_height")

#         self.save_original_geometries()

#         if self.debug_output:
#             print("\n" + "=" * 90)
#             print("[BASE DEBUG] PARAMETRIC BASE UPDATED")
#             print(f"[BASE DEBUG] reason={reason}")
#             print(f"[BASE DEBUG] source kept : W={old_source_w}, H={old_source_h}")
#             print(f"[BASE DEBUG] target kept : W={old_target_w}, H={old_target_h}")
#             print(f"[BASE DEBUG] original_geometries handles={len(self.original_geometries)}")
#             print("=" * 90)


#     def save_original_geometries(self):
#         self.original_geometries.clear()
#         for entity in self.doc.modelspace():
#             hndl = entity.dxf.handle
#             tp = entity.dxftype()
#             if tp == "CIRCLE":
#                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
#             elif tp == "LINE":
#                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}
#             elif tp == "ARC":
#                 self.original_geometries[hndl] = {"type": "ARC", "center": entity.dxf.center, "radius": entity.dxf.radius, "start_angle": entity.dxf.start_angle, "end_angle": entity.dxf.end_angle}
#             elif tp == "TEXT":
#                 settings = self.get_text_settings()
#                 if settings.get("handle") == hndl:
#                     insert = (
#                         float(settings.get("x", 0.0)),
#                         float(settings.get("y", 0.0)),
#                         0.0
#                     )
#                     height = self.text_box_height(settings)
#                     width = self.text_box_width(settings)
#                     text_value = settings.get("text", "")
#                 else:
#                     insert = entity.dxf.insert
#                     height = float(entity.dxf.height)
#                     width = float(getattr(entity.dxf, "width", 1.0))
#                     text_value = entity.dxf.text
#                 self.original_geometries[hndl] = {
#                     "type": "TEXT",
#                     "insert": insert,
#                     "height": height,
#                     "width": width,
#                     "rotation": float(getattr(entity.dxf, "rotation", 0.0)),
#                     "text": text_value
#                 }

#     def save_zones_history_state(self):
#         state_snapshot = {
#             "parametric_groups": copy.deepcopy(self.parametric_groups),
#             "project_meta": copy.deepcopy(self.project_meta),
#             "block_keep_state": copy.deepcopy(self.block_keep_state)
#         }
#         self.zones_undo_stack.append(state_snapshot)
#         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

#     def capture_full_state_snapshot(self):
#         return {
#             "doc": copy.deepcopy(self.doc),
#             "parametric_groups": copy.deepcopy(self.parametric_groups),
#             "project_meta": copy.deepcopy(self.project_meta),
#             "block_keep_state": copy.deepcopy(self.block_keep_state)
#         }

#     def record_action_snapshot(self):
#         if self.is_loading_history:
#             return
#         self.global_recalc_undo_stack.append(self.capture_full_state_snapshot())
#         if len(self.global_recalc_undo_stack) > 50:
#             self.global_recalc_undo_stack.pop(0)
#         self.global_recalc_redo_stack.clear()
#         self.update_history_buttons_state()

#     def restore_full_state_snapshot(self, snapshot):
#         self.doc = copy.deepcopy(snapshot["doc"])
#         self.parametric_groups = copy.deepcopy(snapshot["parametric_groups"])
#         self.project_meta = copy.deepcopy(snapshot["project_meta"])
#         self.block_keep_state = copy.deepcopy(snapshot["block_keep_state"])
#         self.doc.saveas(self.dxf_path)
#         self.save_project_config()
#         self.save_original_geometries()
#         self.update_dimension_inputs_from_meta()
#         self.load_groups_into_list()
#         self.load_entities_into_list()
#         self.update_viewer()
#         self.update_history_buttons_state()

#     def push_to_history(self):
#         self.history.save_state()
#         self.history.clear_redo()
#         self.save_zones_history_state()
#         self.zones_redo_stack.clear()
#         self.update_history_buttons_state()

#     def undo(self):
#         if self.history.undo() and len(self.zones_undo_stack) > 1:
#             current_snapshot = self.zones_undo_stack.pop()
#             self.zones_redo_stack.append(current_snapshot)
#             previous_snapshot = self.zones_undo_stack[-1]
            
#             restored_groups = copy.deepcopy(previous_snapshot["parametric_groups"])
            
#             for rest_g in restored_groups:
#                 for cur_g in self.parametric_groups:
#                     if rest_g["name"] == cur_g["name"]:
#                         rest_g["k_w"] = cur_g.get("k_w", 0.0)
#                         rest_g["k_h"] = cur_g.get("k_h", 0.0)
#                         rest_g["growth_p_w"] = cur_g.get("growth_p_w", 0.0)
#                         rest_g["growth_p_h"] = cur_g.get("growth_p_h", 0.0)
#                         rest_g["growth_dir_x"] = cur_g.get("growth_dir_x", "Центр")
#                         rest_g["growth_dir_y"] = cur_g.get("growth_dir_y", "Центр")
#                         rest_g["shift_dir_x"] = cur_g.get("shift_dir_x", "Вправо")
#                         rest_g["shift_dir_y"] = cur_g.get("shift_dir_y", "Вгору")
#                         rest_g["link_x"] = cur_g.get("link_x", "X = W")
#                         rest_g["link_y"] = cur_g.get("link_y", "Y = H")
#                         break

#             self.parametric_groups = restored_groups
#             self.save_project_config()
#             self.reload_after_history_change()

#     def redo(self):
#         if self.history.redo() and self.zones_redo_stack:
#             next_snapshot = self.zones_redo_stack.pop()
#             self.zones_undo_stack.append(next_snapshot)
            
#             restored_groups = copy.deepcopy(next_snapshot["parametric_groups"])
            
#             for rest_g in restored_groups:
#                 for cur_g in self.parametric_groups:
#                     if rest_g["name"] == cur_g["name"]:
#                         rest_g["k_w"] = cur_g.get("k_w", 0.0)
#                         rest_g["k_h"] = cur_g.get("k_h", 0.0)
#                         rest_g["growth_p_w"] = cur_g.get("growth_p_w", 0.0)
#                         rest_g["growth_p_h"] = cur_g.get("growth_p_h", 0.0)
#                         rest_g["growth_dir_x"] = cur_g.get("growth_dir_x", "Центр")
#                         rest_g["growth_dir_y"] = cur_g.get("growth_dir_y", "Центр")
#                         rest_g["shift_dir_x"] = cur_g.get("shift_dir_x", "Вправо")
#                         rest_g["shift_dir_y"] = cur_g.get("shift_dir_y", "Вгору")
#                         rest_g["link_x"] = cur_g.get("link_x", "X = W")
#                         rest_g["link_y"] = cur_g.get("link_y", "Y = H")
#                         break

#             self.parametric_groups = restored_groups
#             self.save_project_config()
#             self.reload_after_history_change()

#     def restore_state_snapshot(self, snapshot):
#         self.parametric_groups = copy.deepcopy(snapshot["parametric_groups"])
#         self.project_meta = copy.deepcopy(snapshot.get("project_meta", self.project_meta))
#         self.block_keep_state = copy.deepcopy(snapshot.get("block_keep_state", self.block_keep_state))
#         self.save_project_config()
#         self.reload_after_history_change()

#     def undo(self):
#         if self.global_recalc_undo_stack:
#             self.global_recalc_redo_stack.append(self.capture_full_state_snapshot())
#             snapshot = self.global_recalc_undo_stack.pop()
#             self.restore_full_state_snapshot(snapshot)
#             return
#         if self.history.undo() and len(self.zones_undo_stack) > 1:
#             current_snapshot = self.zones_undo_stack.pop()
#             self.zones_redo_stack.append(current_snapshot)
#             self.restore_state_snapshot(self.zones_undo_stack[-1])

#     def redo(self):
#         if self.global_recalc_redo_stack:
#             self.global_recalc_undo_stack.append(self.capture_full_state_snapshot())
#             snapshot = self.global_recalc_redo_stack.pop()
#             self.restore_full_state_snapshot(snapshot)
#             return
#         if self.history.redo() and self.zones_redo_stack:
#             next_snapshot = self.zones_redo_stack.pop()
#             self.zones_undo_stack.append(next_snapshot)
#             self.restore_state_snapshot(next_snapshot)

#     def set_interface_theme(self, theme_name):
#         is_dark = theme_name == "Темна"
#         if is_dark:
#             self.setStyleSheet("""
#                 QMainWindow { background-color: #1e1e1e; }
#                 QWidget { color: #d4d4d4; font-size: 12px; }
                               
#                 QTabWidget::pane {
#                     border: 1px solid #3c3c3c;
#                     background: #1e1e1e;
#                     top: -1px; /* Прибирає подвійну рамку на стику */
#                 }
    
#                 /* Базовий стиль для всіх вкладок на панелі */
#                 QTabBar::tab {
#                     background: #3c3c3c;
#                     color: #fff;
#                     padding: 8px 16px;
#                     font-size: 13px;
#                     font-weight: 500;
#                     border: 1px solid #3c3c3c;
#                     border-bottom: none;
#                     border-top-left-radius: 4px;
#                     border-top-right-radius: 4px;
#                     min-width: 40px;
#                 }

#                 /* Стиль вкладки, коли на неї наводять мишкою */
#                 QTabBar::tab:hover {
#                     background: #2c3e50;
                    
#                 }

#                 /* Стиль строго для АКТИВНОЇ (обраної) вкладки */
#                QTabBar::tab:selected {
#                     background: #2c3e50;
#                     color: #ffffff ;
#                     font-weight: bold;
#                     border-bottom: 2px solid #2ecc71; 
#                 }
#                 QScrollArea { border: none; background-color: #252526; }
#                 QGroupBox {
#                     font-weight: bold; color: #4fc3f7; border: 1px solid #3c3c3c;
#                     border-radius: 6px; margin-top: 15px; padding-top: 10px;
#                 }
#                 QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
#                 QPushButton {
#                     background-color: #333333; border: 1px solid #454545; color: #ffffff;
#                     padding: 6px; border-radius: 4px;
#                 }
#                 QPushButton:hover { background-color: #454545; border-color: #007acc; }
#                 QPushButton:disabled { color: #777777; background-color: #252525; }
#                 QLineEdit, QComboBox {
#                     background-color: #1e1e1e; border: 1px solid #3c3c3c;
#                     color: #ffffff; padding: 4px; border-radius: 3px;
#                 }
#                 QListWidget {
#                     background-color: #1e1e1e; color: #d4d4d4;
#                     border: 1px solid #3c3c3c; border-radius: 4px;
#                 }
#                 QListWidget::item:selected { background-color: #0e639c; color: #ffffff; }
#                 QCheckBox { spacing: 6px; }
#                 QScrollBar:vertical { background: #252526; width: 12px; }
#                 QScrollBar::handle:vertical { background: #555555; border-radius: 5px; min-height: 24px; }
                               
#                  QGroupBox {
#                 font-size: 14px;
#                 font-weight: bold;
#                 color: #2d3748;
#                 margin-top: 12px; /* Відступ зверху для заголовка */
#                 border: 1px solid #cbd5e0;
#                 border-radius: 6px;
#                 padding-top: 16px; /* Внутрішній відступ від заголовка до елементів */
#             }

#             /* Зсув заголовка з чекбоксом трохи вище та лівіше */
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 subcontrol-position: top left;
#                 left: 10px;
#                 padding: 0 5px;
#             }

#             /* БАЗОВИЙ СТИЛЬ ЧЕКБОКСА всередині GroupBox */
#             QGroupBox::indicator {
#                 width: 18px;
#                 height: 18px;
#                 border: 2px solid #cbd5e0;
#                 border-radius: 4px;
#                 background-color: #ffffff;
#             }

#             /* Стан при наведенні курсору */
#             QGroupBox::indicator:hover {
#                 border-color: #3182ce;
#                 background-color: #f7fafc;
#             }

#             /* Стан, коли галочка ВСТАНОВЛЕНА (панель відкрита) */
#             QGroupBox::indicator:checked {
#                 border-color: #3182ce;
#                 background-color: #3182ce;
#                 /* Вбудована SVG-галочка білого кольору */
#                 image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
#             }

#             /* Стан, коли галочка ЗНЯТА (панель згорнута) */
#             QGroupBox::indicator:unchecked {
#                 border-color: #cbd5e0;
#                 background-color: #ffffff;
#             }
#             """)
#         else:
#             self.setStyleSheet("""
#                 QMainWindow { background-color: #eef2f7; color: #fff}
#                 QWidget { background-color: #ffffff; color: #1f2933; font-size: 12px; }
                               
#                                QTabWidget::pane {
#                     border: 1px solid #e0e0e0;
#                     background: #ffffff;
#                     top: -1px; /* Прибирає подвійну рамку на стику */
#                 }
    
#                 /* Базовий стиль для всіх вкладок на панелі */
#                 QTabBar::tab {
#                     background: #f8f9fa;
#                     color: #2c3e50;
#                      padding: 8px 16px;
#                     font-size: 13px;
#                     font-weight: 500;
#                     border: 1px solid #e0e0e0;
#                     border-bottom: none;
#                     border-top-left-radius: 4px;
#                     border-top-right-radius: 4px;
#                     min-width: 80px;
#                 }

#                 /* Стиль вкладки, коли на неї наводять мишкою */
#                 QTabBar::tab:hover {
#                     background: #eef2f7;
#                     color: #2ecc71; /* Зелений колір тексту при наведенні */
#                 }

#                 /* Стиль строго для АКТИВНОЇ (обраної) вкладки */
#                 QTabBar::tab:selected {
#                     background: #ffffff;
#                     color: #2c3e50  ;
#                     font-weight: bold;
#                     border-bottom: 2px solid #2ecc71; 
#                 }
#                 QScrollArea { border: none; background-color: #f7f9fc; }
#                 QGroupBox {
#                     background-color: #ffffff; font-weight: bold; color: #0b5cad;
#                     border: 1px solid #cfd7e3; border-radius: 6px;
#                     margin-top: 15px; padding-top: 10px;
#                 }
#                 QGroupBox::title {
#                     subcontrol-origin: margin; left: 10px; padding: 0 4px;
#                     background-color: #ffffff;
#                 }
#                 QPushButton {
#                     background-color: #ffffff; border: 1px solid #b8c4d4; color: #1f2933;
#                     padding: 6px; border-radius: 4px;
#                 }
#                 QPushButton:hover { background-color: #edf5ff; border-color: #0b5cad; }
#                 QPushButton:pressed { background-color: #dbeafe; }
#                 QPushButton:disabled { color: #9aa6b2; background-color: #edf0f4; }
#                 QLineEdit, QComboBox {
#                     background-color: #ffffff; border: 1px solid #b8c4d4;
#                     color: #111827; padding: 4px; border-radius: 3px;
#                     selection-background-color: #bfdbfe;
#                 }
#                 QListWidget {
#                     background-color: #ffffff; color: #1f2933;
#                     border: 1px solid #cfd7e3; border-radius: 4px;
#                     alternate-background-color: #f6f8fb;
#                 }
#                 QListWidget::item:selected { background-color: #dbeafe; color: #111827; }
#                 QCheckBox {  spacing: 6px; }
#                 QCheckBox::indicator:unchecked {
#                     background-color: #ffffff;
#                     border: 1px solid #1e1e1e;
#                 }
 
#                 QCheckBox::indicator:checked { background-color: #0b5cad; border: 1px solid #0b5cad; }
#                 QScrollBar:vertical { background: #f1f5f9; width: 12px; }
#                 QScrollBar::handle:vertical { background: #b8c4d4; border-radius: 5px; min-height: 24px; }
                               
#                  QGroupBox {
#                 font-size: 14px;
#                 font-weight: bold;
#                 color: #2d3748;
#                 margin-top: 12px; /* Відступ зверху для заголовка */
#                 border: 1px solid #cbd5e0;
#                 border-radius: 6px;
#                 padding-top: 16px; /* Внутрішній відступ від заголовка до елементів */
#             }

#             /* Зсув заголовка з чекбоксом трохи вище та лівіше */
#             QGroupBox::title {
#                 subcontrol-origin: margin;
#                 subcontrol-position: top left;
#                 left: 10px;
#                 padding: 0 5px;
#             }

#             /* БАЗОВИЙ СТИЛЬ ЧЕКБОКСА всередині GroupBox */
#             QGroupBox::indicator {
#                 width: 18px;
#                 height: 18px;
#                 border: 2px solid #cbd5e0;
#                 border-radius: 4px;
#                 background-color: #ffffff;
#             }

#             /* Стан при наведенні курсору */
#             QGroupBox::indicator:hover {
#                 border-color: #3182ce;
#                 background-color: #f7fafc;
#             }

#             /* Стан, коли галочка ВСТАНОВЛЕНА (панель відкрита) */
#             QGroupBox::indicator:checked {
#                 border-color: #3182ce;
#                 background-color: #3182ce;
#                 /* Вбудована SVG-галочка білого кольору */
#                 image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
#             }

#             /* Стан, коли галочка ЗНЯТА (панель згорнута) */
#             QGroupBox::indicator:unchecked {
#                 border-color: #cbd5e0;
#                 background-color: #ffffff;
#             }
#             """)
#         self.apply_theme_widget_overrides(is_dark)

#     def apply_theme_widget_overrides(self, is_dark):
#         styles = {
#             "btn_open_file": (
#                 "background-color: #37474f; color: white; font-weight: bold; padding: 4px;",
#                 "background-color: #e8f1fb; color: #123f68; border: 1px solid #9cb7d5; font-weight: bold; padding: 4px;"
#             ),
#             "chk_enable_inspector": (
#                 "color: #ff9800; font-weight: bold;",
#                 "color: #9a5b00; font-weight: bold;"
#             ),
#             "btn_snap_zero": (
#                 "background-color: #00897b; color: white; font-weight: bold; padding: 6px;",
#                 "background-color: #e0f2f1; color: #005f56; border: 1px solid #7bbdb5; font-weight: bold; padding: 6px;"
#             ),
#             "transform_group": (
#                 "QGroupBox { border: 1px solid #d32f2f; }",
#                 "QGroupBox { background-color: #fff7f7; border: 1px solid #e2a8a8; color: #8a1f1f; }"
#             ),
#             "lbl_status_calc": (
#                 "color: #4fc3f7; font-size: 11px;",
#                 "color: #0b5cad; font-size: 11px;"
#             ),
#             "btn_apply_auto_scale": (
#                 "background-color: #007acc; color: white; font-weight: bold; padding: 6px;",
#                 "background-color: #0b5cad; color: white; border: 1px solid #084b8d; font-weight: bold; padding: 6px;"
#             ),
#             "btn_export_new_dxf": (
#                 "background-color: #2e7d32; color: white; font-weight: bold; padding: 6px;",
#                 "background-color: #2e7d32; color: white; border: 1px solid #1f5d23; font-weight: bold; padding: 6px;"
#             ),
#             "btn_create_group": (
#                 "background-color: #673ab7; color: white; font-weight: bold;",
#                 "background-color: #ede7f6; color: #4527a0; border: 1px solid #b39ddb; font-weight: bold;"
#             ),
#             "btn_delete_from_dxf": (
#                 "background-color: #d32f2f; color: white; font-weight: bold;",
#                 "background-color: #fde8e8; color: #9b1c1c; border: 1px solid #f3aaaa; font-weight: bold;"
#             ),
#         }
#         for attr_name, (dark_style, light_style) in styles.items():
#             widget = getattr(self, attr_name, None)
#             if widget is not None:
#                 widget.setStyleSheet(dark_style if is_dark else light_style)

#     def on_scene_item_clicked(self, handle):
#         modifiers = QGuiApplication.keyboardModifiers()
#         if (modifiers & Qt.ControlModifier):
#             if handle in self.selected_handles: self.selected_handles.remove(handle)
#             else: self.selected_handles.add(handle)
#             self.sync_list_from_handles()
#             self.update_viewer()
#             return

#         group_idx = self.group_index_for_handle(handle)
#         if group_idx is not None:
#             self.select_group_by_index(group_idx)
#             return

#         self.group_list_widget.clearSelection()
#         self.selected_handles = {handle}
#         self.sync_list_from_handles()
#         self.update_viewer()

#     def group_index_for_handle(self, handle):
#         handle = str(handle)
#         for idx, group in enumerate(self.parametric_groups):
#             if handle in {str(h) for h in group.get("handles", set())}:
#                 return idx
#         return None

#     def select_group_by_index(self, idx):
#         if idx < 0 or idx >= self.group_list_widget.count():
#             return
#         self.group_list_widget.setCurrentRow(idx)
#         group = self.parametric_groups[idx]
#         self.selected_handles = set(group.get("handles", set()))
#         self.sync_list_from_handles()
#         self.update_viewer()

#     def update_history_buttons_state(self):
#         can_undo_history = len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1
#         can_redo_history = len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0
#         self.btn_undo.setEnabled(bool(self.global_recalc_undo_stack) or can_undo_history)
#         self.btn_redo.setEnabled(bool(self.global_recalc_redo_stack) or can_redo_history)

#     def reload_after_history_change(self):
#         self.is_loading_history = True
#         self.doc = ezdxf.readfile(self.dxf_path)
#         self.save_original_geometries()
#         self.update_dimension_inputs_from_meta()
#         self.load_groups_into_list()
#         self.load_entities_into_list()
#         self.update_history_buttons_state()
#         self.is_loading_history = False

#     def scan_project_folder_for_dxf(self):
#         self.file_explorer_list.blockSignals(True)
#         self.file_explorer_list.clear()
#         try:
#             files = os.listdir(self.project_dir)
#             dxf_files = [f for f in files if f.lower().endswith('.dxf')]
#             for file_name in dxf_files:
#                 item = QListWidgetItem(f"📄 {file_name}")
#                 item.setData(Qt.ItemDataRole.UserRole, file_name)
#                 self.file_explorer_list.addItem(item)
#                 if file_name.lower() == os.path.basename(self.dxf_path).lower():
#                     self.file_explorer_list.setCurrentItem(item)
#         except Exception as e:
#             print(f"Помилка провідника: {e}")
#         self.file_explorer_list.blockSignals(False)

#     def on_dxf_selection_changed_in_explorer(self):
#         selected_items = self.file_explorer_list.selectedItems()
#         if not selected_items: return
#         self.selected_handles.clear()
#         self.parametric_groups.clear()
#         base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
#         self.current_project_file_id = None
#         self.dxf_path = os.path.join(self.project_dir, base_file_name)
#         self.doc = ezdxf.readfile(self.dxf_path)

#         if len(selected_items) > 1:
#             for item in selected_items[1:]:
#                 addon_file_name = item.data(Qt.ItemDataRole.UserRole)
#                 addon_path = os.path.join(self.project_dir, addon_file_name)
#                 if os.path.exists(addon_path):
#                     try:
#                         addon_doc = ezdxf.readfile(addon_path)
#                         importer = Importer(addon_doc, self.doc)
#                         importer.import_modelspace()
#                         importer.finalize()
#                     except Exception as e: print(f"Помилка злиття: {e}")

#         self.load_project_config()
#         self.prompt_source_dimensions_on_open()
#         self.register_current_folder_model(show_errors=False)
#         self.update_dimension_inputs_from_meta()
#         self.history = HistoryManager(self.dxf_path)
#         self.history.save_state()
#         self.zones_undo_stack.clear()
#         self.zones_redo_stack.clear()
#         self.global_recalc_undo_stack.clear()
#         self.global_recalc_redo_stack.clear()
#         self.save_zones_history_state()
#         self.save_original_geometries()
#         self.update_viewer()
#         self.load_entities_into_list()
#         self.load_groups_into_list()
#         self.load_block_filter_list()
#         self.update_history_buttons_state()

#     def process_manual_rubber_band(self, rect):
#         modifiers = QGuiApplication.keyboardModifiers()
#         if not (modifiers & Qt.ControlModifier):
#             self.selected_handles.clear()
#         path = QPainterPath()
#         path.addRect(rect)
#         for item in self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape):
#             hndl = item.data(Qt.ItemDataRole.UserRole)
#             if hndl: self.selected_handles.add(hndl)
#         self.sync_list_from_handles()
#         self.update_viewer()

#     def sync_list_from_handles(self):
#         self.entity_list.blockSignals(True)
#         self.entity_list.clearSelection()
#         for i in range(self.entity_list.count()):
#             item = self.entity_list.item(i)
#             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
#         self.entity_list.blockSignals(False)

#     def on_list_selection_changed(self):
#         self.selected_handles.clear()
#         for item in self.entity_list.selectedItems():
#             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
#         self.update_viewer()

#     def clear_selection(self):
#         self.selected_handles.clear()
#         self.update_viewer()
#         self.entity_list.blockSignals(True)
#         self.entity_list.clearSelection()
#         self.entity_list.blockSignals(False)

#     def on_theme_changed(self, theme_name):
#         self.current_theme = theme_name
#         self.set_interface_theme(theme_name)
#         self.update_viewer()

#     def load_entities_into_list(self):
#         self.entity_list.blockSignals(True)
#         self.entity_list.clear()
#         seen = set()
#         for entity in self.doc.modelspace():
#             tp = entity.dxftype()
#             hndl = entity.dxf.handle
#             if tp == "CIRCLE":
#                 cx, cy, _ = entity.dxf.center
#                 if (round(cx, 1), round(cy, 1)) in seen: continue
#                 seen.add((round(cx, 1), round(cy, 1)))
#                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
#             elif tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 if (round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)) in seen: continue
#                 seen.add((round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)))
#                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм. Початок: ({x1:.1f}, {y1:.1f}), Кінець: ({x2:.1f}, {y2:.1f})"
#             elif tp == "ARC":
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 sa = float(entity.dxf.start_angle)
#                 ea = float(entity.dxf.end_angle)

#                 arc_key = (
#                     round(cx, 2),
#                     round(cy, 2),
#                     round(r, 2),
#                     round(sa, 2),
#                     round(ea, 2),
#                 )

#                 if arc_key in seen:
#                     continue

#                 seen.add(arc_key)

#                 text = (
#                     f"🌙 Дуга (ID: {hndl}) "
#                     f"Центр X:{cx:.1f}, Y:{cy:.1f}, "
#                     f"R:{r:.1f}, Кути: {sa:.1f}° → {ea:.1f}°"
#                 )
#             # elif tp == "ARC":
#             #     cx, cy, _ = entity.dxf.center
#             #     r = entity.dxf.radius
#             #     if (round(cx, 1), round(cy, 1), round(r, 1)) in seen: continue
#             #     seen.add((round(cx, 1), round(cy, 1), round(r, 1)))
#             #     text = f"🌙 Дуга (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}, R:{r:.1f}"
#             elif tp == "TEXT":
#                 x, y, _ = entity.dxf.insert
#                 label = entity.dxf.text.strip() or "[рамка тексту]"
#                 text = f"Текст (ID: {hndl}) \"{label}\" X:{x:.1f}, Y:{y:.1f}, H:{entity.dxf.height:.1f}"
#             else: continue
#             item = QListWidgetItem(text)
#             item.setData(Qt.ItemDataRole.UserRole, str(hndl))
#             self.entity_list.addItem(item)
#         self.entity_list.blockSignals(False)

#     def update_viewer(self):
#         items_to_remove = [item for item in self.scene.items() if item != self.coord_tooltip_item and item != self.coord_snap_marker]
#         for item in items_to_remove:
#             self.scene.removeItem(item)
            
#         self.overlay_items.clear()

#         if self.current_theme == "Темна":
#             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
#             base_line_color = QColor(220, 220, 220)
#         else:
#             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
#             base_line_color = QColor(80, 80, 80)

#         self.scene.addLine(-150, 0, 150, 0, QPen(QColor(33, 150, 243), 2))
#         self.scene.addLine(0, 150, 0, -150, QPen(QColor(76, 175, 80), 2))

#         for idx, group in enumerate(self.parametric_groups):
#             g_min_x, g_max_x, g_min_y, g_max_y = float('inf'), float('-inf'), float('inf'), float('-inf')
#             for hndl in group["handles"]:
#                 if hndl not in self.doc.entitydb: continue
#                 e = self.doc.entitydb[hndl]
#                 if e.dxftype() in ("CIRCLE", "ARC"):
#                     g_min_x = min(g_min_x, e.dxf.center[0] - e.dxf.radius)
#                     g_max_x = max(g_max_x, e.dxf.center[0] + e.dxf.radius)
#                     g_min_y = min(g_min_y, e.dxf.center[1] - e.dxf.radius)
#                     g_max_y = max(g_max_y, e.dxf.center[1] + e.dxf.radius)
#                 elif e.dxftype() == "LINE":
#                     g_min_x = min(g_min_x, e.dxf.start[0], e.dxf.end[0])
#                     g_max_x = max(g_max_x, e.dxf.start[0], e.dxf.end[0])
#                     g_min_y = min(g_min_y, e.dxf.start[1], e.dxf.end[1])
#                     g_max_y = max(g_max_y, e.dxf.start[1], e.dxf.end[1])

#             if g_min_x != float('inf'):
#                 rect_item = QGraphicsRectItem(g_min_x - 4, -(g_max_y + 4), (g_max_x - g_min_x) + 8, (g_max_y - g_min_y) + 8)
#                 rect_item.setBrush(QBrush(QColor(103, 58, 183, 20)))
#                 rect_item.setPen(QPen(QColor(103, 58, 183, 150), 1, Qt.PenStyle.DashLine))
#                 self.scene.addItem(rect_item)

#         seen_circles, seen_lines, seen_arcs = set(), set(), set()

#         for entity in self.doc.modelspace():
#             hndl = entity.dxf.handle
#             tp = entity.dxftype()
#             pyqt_item = None
            
#             if tp == "CIRCLE":
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
#                 seen_circles.add((round(cx, 2), round(cy, 2)))
#                 pyqt_item = SelectableCircle(
#                     cx - r,
#                     -cy - r,
#                     r * 2,
#                     r * 2,
#                     entity
#                 )
#             elif tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
#                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
#                 pyqt_item = SelectableLine(
#                     x1, -y1,
#                     x2, -y2,
#                     entity
#                 )

#             elif tp == "ARC":
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 sa = entity.dxf.start_angle
#                 ea = entity.dxf.end_angle
#                 if (round(cx, 2), round(cy, 2), round(sa, 2)) in seen_arcs: continue
#                 seen_arcs.add((round(cx, 2), round(cy, 2), round(sa, 2)))
#                 pyqt_item = SelectableArc(
#                     QPointF(cx, -cy),
#                     r,
#                     sa,
#                     ea,
#                     entity
#                 )

#             elif tp in ("TEXT", "MTEXT"):
#                 settings = self.get_text_settings()
#                 entity_text = getattr(entity.dxf, "text", "") if tp == "TEXT" else getattr(entity, "text", "")
#                 display_text = self.text_display_value(settings.get("text", entity_text))
#                 if settings.get("handle") == hndl:
#                     # Наш керований текстовий блок: лишається рамкою, яку можна рухати.
#                     box_x = float(settings.get("x", 0.0))
#                     box_y = float(settings.get("y", 0.0))
#                     box_w = self.text_box_width(settings)
#                     box_h = self.text_box_height(settings)
#                     pyqt_item = DraggableDoorTextBoxItem(
#                         0,
#                         0,
#                         box_w,
#                         box_h,
#                         self,
#                         hndl
#                     )
#                     pyqt_item.setPos(box_x, -box_y - box_h)
#                     pyqt_item.setBrush(QBrush(QColor(0, 120, 255, 55)))
#                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 1.5, Qt.PenStyle.DashLine))
#                     pyqt_item.setTransformOriginPoint(box_w * 0.5, box_h * 0.5)
#                     pyqt_item.setRotation(-float(settings.get("rotation", 0.0)))
#                     self.scene.addItem(pyqt_item)
#                     self.add_centered_text_preview(
#                         pyqt_item,
#                         display_text,
#                         box_w,
#                         box_h,
#                         str(settings.get("font", "STANDARD"))
#                     )
#                 else:
 
#                     x, y, _ = entity.dxf.insert
#                     if tp == "TEXT":
#                         display_text = entity.dxf.text.strip() or " "
#                         text_height = float(entity.dxf.height)
#                     else:
#                         display_text = str(getattr(entity, "text", "") or getattr(entity.dxf, "text", "") or " ").strip() or " "
#                         text_height = float(getattr(entity.dxf, "char_height", 10.0) or getattr(entity.dxf, "height", 10.0) or 10.0)
#                     pyqt_item = DraggableDxfTextItem(display_text, self, hndl, tp)
#                     pyqt_item.setDefaultTextColor(QColor(0, 120, 255) if hndl in self.selected_handles else base_line_color)
#                     font = pyqt_item.font()
#                     font.setPointSizeF(max(text_height, 1.0))
#                     pyqt_item.setFont(font)
#                     pyqt_item.setPos(x, -y - text_height)
#                     pyqt_item.setRotation(-float(getattr(entity.dxf, "rotation", 0.0)))
#                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
#                 self.overlay_items[hndl] = pyqt_item
#                 self.scene.addItem(pyqt_item) if pyqt_item.scene() is None else None
#                 continue

#             if pyqt_item:
#                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
#                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
                
#                 if hndl in self.selected_handles:
#                     pen_style = QPen(QColor(0, 120, 255), 2.5) 
#                 else:
#                     in_group = False
#                     for group in self.parametric_groups:
#                         if hndl in group["handles"]:
#                             group_key = self.get_group_key(group)
#                             if self.block_keep_state.get(group_key, True):
#                                 pen_style = QPen(QColor(76, 175, 80), 2)
#                             else:
#                                 pen_style = QPen(QColor(211, 47, 47), 2)
#                             in_group = True
#                             break
#                     if not in_group: pen_style = QPen(base_line_color, 1.5)
                
#                 pyqt_item.setPen(pen_style)
#                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
#                 self.scene.addItem(pyqt_item)
#                 self.overlay_items[hndl] = pyqt_item

#         settings = self.get_text_settings()
#         if settings.get("enabled") and not settings.get("handle"):
#             box_x = float(settings.get("x", 0.0))
#             box_y = float(settings.get("y", 0.0))
#             box_w = self.text_box_width(settings)
#             box_h = self.text_box_height(settings)
#             box_item = DraggableDoorTextBoxItem(0, 0, box_w, box_h, self)
#             box_item.setPos(box_x, -box_y - box_h)
#             box_item.setBrush(QBrush(QColor(0, 120, 255, 55)))
#             box_item.setPen(QPen(QColor(0, 120, 255), 1.5, Qt.PenStyle.DashLine))
#             box_item.setTransformOriginPoint(box_w * 0.5, box_h * 0.5)
#             box_item.setRotation(-float(settings.get("rotation", 0.0)))
#             self.scene.addItem(box_item)
#             display_text = self.text_display_value(settings.get("text", ""))
#             self.add_centered_text_preview(
#                 box_item,
#                 display_text,
#                 box_w,
#                 box_h,
#                 str(settings.get("font", "STANDARD"))
#             )

#         self.view.setSceneRect(self.scene.itemsBoundingRect())


# if __name__ == "__main__":
#     import PySide6.QtWidgets as qtw
#     app = qtw.QApplication(sys.argv)
#     window = MiniCAD()
#     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
#     window.show()
#     sys.exit(app.exec())
import os
import sys
import math
import copy
import io
import json
import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from PySide6.QtGui import QShortcut, QKeySequence
from parametric_db_new import LoginDialog, ParametricDb
import table_io
from designer_shell import create_fallback_shell, load_designer_shell

import ezdxf
import ezdxf.bbox as dxf_bbox
from ezdxf.enums import TextEntityAlignment
from ezdxf.math import Matrix44
from ezdxf.addons.importer import Importer 

from PySide6.QtWidgets import (
    QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QCheckBox,
    QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView, 
    QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem, QInputDialog, QFileDialog, QMessageBox,
    QGridLayout, QGraphicsTextItem, QGraphicsSimpleTextItem, QGraphicsItem, QTabWidget, QSizePolicy,
    QTreeWidget, QTreeWidgetItem, QDialog, QFormLayout, QDialogButtonBox
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


class MemoryHistoryManager:
    def __init__(self, owner):
        self.owner = owner
        self.undo_stack = []
        self.redo_stack = []

    def save_state(self):
        self.undo_stack.append(self.owner.dxf_doc_to_bytes())
        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) <= 1:
            return None
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        previous_state = self.undo_stack[-1]
        self.owner.doc = self.owner.read_dxf_doc_from_bytes(previous_state)
        return previous_state

    def redo(self):
        if not self.redo_stack:
            return None
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        self.owner.doc = self.owner.read_dxf_doc_from_bytes(next_state)
        return next_state

    def clear_redo(self):
        self.redo_stack.clear()


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

    if "/" in text: 
        try:
            parts = text.split("/")
            return float(parts[0]) / float(parts[1])
        except: return 0.0

    try:
        val = float(text.replace(',', '.'))
        if val > 1.0: 
            return val / 100.0
        return val
    except:
        return 0.0

def format_factor(val):
    """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
    if abs(val - 0.0) < 0.001: return "0% (Фіксовано)"
    if abs(val - 0.25) < 0.001: return "25% (Δ/4)"
    if abs(val - 0.333) < 0.01: return "33.3% (Δ/3)"
    if abs(val - 0.5) < 0.001: return "50% (Δ/2)"
    if abs(val - 0.667) < 0.01: return "66.7% (2Δ/3)"
    if abs(val - 0.75) < 0.01: return "75% (3Δ/4)"
    if abs(val - 1.0) < 0.001: return "100% (Δ)"
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


class DraggableDxfTextItem(QGraphicsTextItem):
    def __init__(self, text, owner, handle, entity_type="TEXT"):
        super().__init__(text)
        self.owner = owner
        self.handle = handle
        self.entity_type = entity_type
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
        self.owner.on_existing_dxf_text_moved(self)


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
    def signed_shift(value, direction, positive_name, negative_name):
        """Повертає зсув з урахуванням напрямку.

        Раніше зсув завжди додавався як +X/+Y. Через це після ROT180 або дзеркала
        група могла рости в правильний бік, але вся база групи все одно їхала вправо/вгору.
        """
        direction = str(direction or positive_name)
        if direction == negative_name:
            return -value
        return value

    @staticmethod
    def get_transform(delta_w, delta_h, group):
        val_x = delta_w if "W" in group.get("link_x", "W") else delta_h
        val_y = delta_h if "H" in group.get("link_y", "H") else delta_w

        raw_shift_x = val_x * group.get("k_w", 0.0)
        raw_shift_y = val_y * group.get("k_h", 0.0)

        shift_x = ParametricEngine.signed_shift(
            raw_shift_x,
            group.get("shift_dir_x", "Вправо"),
            "Вправо",
            "Вліво"
        )
        shift_y = ParametricEngine.signed_shift(
            raw_shift_y,
            group.get("shift_dir_y", "Вгору"),
            "Вгору",
            "Вниз"
        )

        growth_x = val_x * group.get("growth_p_w", 0.0)
        growth_y = val_y * group.get("growth_p_h", 0.0)

        return (shift_x, shift_y, 0), (growth_x, growth_y, 0)


class MiniCAD(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Параметризатор")
        self.setGeometry(100, 100, 1600, 950)

        self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
        self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
        self.debug_output = False
        self.db = ParametricDb()
        self.current_user = None
        self.current_theme = "Темна"
        self.current_project_file_id = None
        self.current_door_model_id = None
        self.selected_db_model_id = None
        self.current_db_file_name = None

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
            "source_door_opening": "left",
            "target_door_opening": "left",
            "growth_axis": "both",
            "axis_link_mode": "normal",
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
        if not self.authenticate_user():
            sys.exit(0)
        self.setup_shortcuts()
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
                self.save_current_dxf()
        else:
            dxf_files = [f for f in os.listdir(self.project_dir) if f.lower().endswith('.dxf')]
            if dxf_files:
                self.dxf_path = os.path.join(self.project_dir, dxf_files[0])
                self.doc = ezdxf.readfile(self.dxf_path)
            else:
                self.doc = ezdxf.new()
                self.save_current_dxf()

    def default_project_meta(self):
        return {
            "source_width": None,
            "source_height": None,
            "target_width": None,
            "target_height": None,
            "keep_blocks": [],
            "delete_blocks": [],
            "door_opening": "left",
            "source_door_opening": "left",
            "target_door_opening": "left",
            "growth_axis": "both",
            "axis_link_mode": "normal",
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

    def authenticate_user(self):
 
        if hasattr(self.db, "_check_connection"):
            self.db._check_connection()

       
        if not self.db.available:
            message = (
                "⚠️ <font color='#ff9800'><b>Увага: Немає зв'язку з SQL-сервером!</b></font><br><br>"
                f"Помилка: {self.db.last_error}<br><br>"
                "Введіть логін/пароль для спроби локального входу або перевірте підключення."
            )
        else:
            message = "Вхід"

      
        while True:
            dialog = LoginDialog(self, message)
            if dialog.exec() != LoginDialog.DialogCode.Accepted:
               
                return False
            
            username, password = dialog.credentials()
            
        
            if not self.db.available:
                QMessageBox.critical(
                    self, 
                    "Помилка підключення", 
                    f"Неможливо авторизуватись, оскільки SQL-сервер недоступний.\n\nДеталі помилки:\n{self.db.last_error}"
                )
                continue

            try:
                user = self.db.authenticate(username, password)
            except Exception as exc:
                QMessageBox.warning(self, "База даних", f"Помилка авторизації:\n{exc}")
                return False

            if user:
                self.current_user = user
                self.setWindowTitle(f"{self.windowTitle()} | {user.get('username')}")
                if hasattr(self, "lbl_status_calc"):
                    self.lbl_status_calc.setText(
                        f"<font color='#a5d6a7'>БД підключена. Користувач: {user.get('username')}</font>"
                    )
                self.update_admin_panel_visibility()
                self.refresh_rule_library_combo()
                self.save_current_project_to_db("Opened")
                self.register_current_folder_model(show_errors=False)
                self.update_file_status_panel()
                return True
                
            QMessageBox.warning(self, "Авторизація", "Невірний логін або пароль.")


    def current_user_id(self):
        if not self.current_user:
            return None
        return self.current_user.get("id")

    def is_current_user_admin(self):
        user = getattr(self, "current_user", None) or {}
        role = str(user.get("role") or "").strip().lower()
        return (
            bool(user.get("is_admin")) or
            str(user.get("username", "")).strip().lower() == "admin" or
            role in ("admin", "administrator", "адмін", "администратор")
        )

    def update_admin_panel_visibility(self):
        if hasattr(self, "admin_group"):
            self.admin_group.setVisible(self.is_current_user_admin())

    def admin_require(self):
        if self.is_current_user_admin():
            return True
        QMessageBox.warning(self, "Адмін", "Ця дія доступна тільки адміністратору.")
        return False

    def admin_add_user(self):
        if not self.admin_require():
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Новий користувач")
        form = QFormLayout(dialog)
        input_username = QLineEdit()
        input_full_name = QLineEdit()
        input_password = QLineEdit()
        input_password.setEchoMode(QLineEdit.EchoMode.Password)
        roles = self.db.list_roles() if getattr(self, "db", None) else []
        combo_role = QComboBox()
        role_by_label = {}
        for role in roles:
            label = f"{role.get('id')} | {role.get('name')}"
            combo_role.addItem(label)
            role_by_label[label] = role
        check_admin = QCheckBox("Адміністратор")
        form.addRow("Логін:", input_username)
        form.addRow("Ім'я:", input_full_name)
        form.addRow("Пароль:", input_password)
        if roles:
            form.addRow("Роль:", combo_role)
        else:
            form.addRow("", check_admin)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        selected_role = role_by_label.get(combo_role.currentText()) if roles else None
        user_id = self.db.create_user(
            input_username.text(),
            input_password.text(),
            input_full_name.text(),
            check_admin.isChecked() or str((selected_role or {}).get("name", "")).strip().lower() in ("admin", "administrator", "адмін", "администратор"),
            (selected_role or {}).get("id"),
        )
        if user_id:
            warning = ""
            if roles and not self.db.user_role_name(user_id):
                warning = "\n\nУвага: роль не прив'язалась. Перевірте, чи є RoleId/UserRoleId у Users або таблиця UserRoles(UserId, RoleId)."
            QMessageBox.information(self, "Адмін", f"Користувача створено: {input_username.text()}{warning}")
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося створити користувача:\n{self.db.last_error}")

    def admin_user_choices(self, include_inactive=True):
        users = self.db.list_users() if getattr(self, "db", None) else []
        choices = []
        by_label = {}
        for user in users:
            if not include_inactive and not user.get("is_active"):
                continue
            status = "активний" if user.get("is_active") else "вимкнений"
            role = user.get("role") or "-"
            label = f"{user.get('id')} | {user.get('username')} | {role} | {status}"
            choices.append(label)
            by_label[label] = user
        return choices, by_label

    def admin_pick_user(self, title="Користувач", include_inactive=True):
        choices, by_label = self.admin_user_choices(include_inactive=include_inactive)
        if not choices:
            QMessageBox.information(self, "Адмін", "Користувачів не знайдено.")
            return None
        label, ok = QInputDialog.getItem(self, title, "Виберіть користувача:", choices, 0, False)
        if not ok or not label:
            return None
        return by_label.get(label)

    def role_picker_data(self):
        roles = self.db.list_roles() if getattr(self, "db", None) else []
        labels = []
        by_label = {}
        for role in roles:
            label = f"{role.get('id')} | {role.get('name')}"
            labels.append(label)
            by_label[label] = role
        return roles, labels, by_label

    def admin_edit_user(self):
        if not self.admin_require():
            return
        user = self.admin_pick_user("Редагувати користувача", include_inactive=True)
        if not user:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редагувати користувача")
        form = QFormLayout(dialog)
        input_username = QLineEdit(str(user.get("username") or ""))
        input_full_name = QLineEdit(str(user.get("full_name") or ""))
        input_password = QLineEdit()
        input_password.setEchoMode(QLineEdit.EchoMode.Password)
        input_password.setPlaceholderText("лишити порожнім, щоб не міняти")
        check_active = QCheckBox("Активний")
        check_active.setChecked(bool(user.get("is_active")))

        roles, role_labels, role_by_label = self.role_picker_data()
        combo_role = QComboBox()
        if role_labels:
            combo_role.addItems(role_labels)
            current_role = str(user.get("role") or "").strip().lower()
            for idx, label in enumerate(role_labels):
                role_name = str(role_by_label[label].get("name") or "").strip().lower()
                if role_name == current_role:
                    combo_role.setCurrentIndex(idx)
                    break

        form.addRow("Логін:", input_username)
        form.addRow("Ім'я:", input_full_name)
        form.addRow("Новий пароль:", input_password)
        if role_labels:
            form.addRow("Роль:", combo_role)
        form.addRow("", check_active)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        selected_role = role_by_label.get(combo_role.currentText()) if role_labels else None
        ok = self.db.update_user(
            int(user.get("id")),
            input_username.text(),
            input_full_name.text(),
            input_password.text(),
            check_active.isChecked(),
            (selected_role or {}).get("id"),
        )
        if ok:
            if int(user.get("id")) == self.current_user_id():
                self.current_user["username"] = input_username.text().strip()
                self.current_user["full_name"] = input_full_name.text().strip()
                self.current_user["role"] = str((selected_role or {}).get("name") or self.current_user.get("role") or "").lower()
                self.current_user["is_admin"] = self.is_current_user_admin()
                self.update_admin_panel_visibility()
                self.update_file_status_panel()
            QMessageBox.information(self, "Адмін", "Користувача оновлено.")
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося оновити користувача:\n{self.db.last_error}")

    def admin_delete_user(self):
        if not self.admin_require():
            return
        user = self.admin_pick_user("Видалити користувача", include_inactive=True)
        if not user:
            return
        if int(user.get("id")) == self.current_user_id():
            QMessageBox.warning(self, "Адмін", "Не можна видалити поточного користувача під час активного входу.")
            return
        answer = QMessageBox.question(
            self,
            "Видалити користувача",
            f"Вимкнути користувача '{user.get('username')}'? Він більше не зможе увійти.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if self.db.delete_user(int(user.get("id"))):
            QMessageBox.information(self, "Адмін", "Користувача вимкнено.")
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося вимкнути користувача:\n{self.db.last_error}")

    def logout_user(self):
        if getattr(self, "current_user", None):
            self.save_current_project_to_db("Logout")
        self.current_user = None
        self.update_admin_panel_visibility()
        self.update_file_status_panel()
        self.setWindowTitle("MiniCAD")
        if not self.authenticate_user():
            sys.exit(0)

    def admin_add_group_name(self):
        if not self.admin_require():
            return
        name, ok = QInputDialog.getText(self, "Назва групи", "Нова типова назва групи:")
        if not ok or not name.strip():
            return
        template_id = self.db.add_group_name_template(name.strip(), self.current_user_id())
        if template_id:
            self.refresh_rule_library_combo()
            QMessageBox.information(self, "Адмін", f"Назву додано: {name.strip()}")
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося додати назву:\n{self.db.last_error}")

    def rule_from_group(self, group):
        return {
            "k_w": float(group.get("k_w", 0.0) or 0.0),
            "k_h": float(group.get("k_h", 0.0) or 0.0),
            "growth_p_w": float(group.get("growth_p_w", 0.0) or 0.0),
            "growth_p_h": float(group.get("growth_p_h", 0.0) or 0.0),
            "growth_dir_x": group.get("growth_dir_x") or "Центр",
            "growth_dir_y": group.get("growth_dir_y") or "Центр",
            "shift_dir_x": group.get("shift_dir_x") or "Вправо",
            "shift_dir_y": group.get("shift_dir_y") or "Вгору",
            "link_x": group.get("link_x") or self.project_meta.get("link_x") or "X = W",
            "link_y": group.get("link_y") or self.project_meta.get("link_y") or "Y = H",
        }

    def rule_from_current_controls(self):
        return {
            "k_w": parse_factor(self.combo_k_w.currentText()) if hasattr(self, "combo_k_w") else 0.0,
            "k_h": parse_factor(self.combo_k_h.currentText()) if hasattr(self, "combo_k_h") else 0.0,
            "growth_p_w": parse_factor(self.combo_growth_p_w.currentText()) if hasattr(self, "combo_growth_p_w") else 0.0,
            "growth_p_h": parse_factor(self.combo_growth_p_h.currentText()) if hasattr(self, "combo_growth_p_h") else 0.0,
            "growth_dir_x": self.combo_growth_dir_x.currentText() if hasattr(self, "combo_growth_dir_x") else "Центр",
            "growth_dir_y": self.combo_growth_dir_y.currentText() if hasattr(self, "combo_growth_dir_y") else "Центр",
            "shift_dir_x": self.combo_shift_dir_x.currentText() if hasattr(self, "combo_shift_dir_x") else "Вправо",
            "shift_dir_y": self.combo_shift_dir_y.currentText() if hasattr(self, "combo_shift_dir_y") else "Вгору",
            "link_x": self.project_meta.get("link_x") or "X = W",
            "link_y": self.project_meta.get("link_y") or "Y = H",
        }

    def admin_save_rule(self, default_name, rule):
        name, ok = QInputDialog.getText(self, "Шаблон правила", "Назва правила:", text=default_name)
        if not ok or not name.strip():
            return
        desc, desc_ok = QInputDialog.getText(self, "Шаблон правила", "Опис:", text="")
        if not desc_ok:
            desc = ""
        template_id = self.db.save_rule_template(name.strip(), desc, rule, self.current_user_id(), is_system=False, is_active=True)
        if template_id:
            self.refresh_rule_library_combo()
            QMessageBox.information(self, "Адмін", f"Правило збережено: {name.strip()}")
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося зберегти правило:\n{self.db.last_error}")

    def admin_save_selected_group_rule(self):
        if not self.admin_require():
            return
        selected = self.group_list_widget.selectedItems() if hasattr(self, "group_list_widget") else []
        if not selected:
            QMessageBox.information(self, "Адмін", "Спочатку виберіть групу.")
            return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        group = self.parametric_groups[idx]
        self.admin_save_rule(group.get("name", "Нове правило"), self.rule_from_group(group))

    def admin_add_rule_from_controls(self):
        if not self.admin_require():
            return
        self.admin_edit_rule_dialog(None, self.rule_from_current_controls())

    def admin_rule_choices(self, active_only=False):
        rows = self.db.list_rule_templates(active_only=active_only) if getattr(self, "db", None) else []
        choices = []
        by_label = {}
        for row in rows:
            state = "активне" if row.get("is_active") else "вимкнене"
            system = "system" if row.get("is_system") else "custom"
            label = f"{row.get('id')} | {row.get('name')} | {state} | {system}"
            choices.append(label)
            by_label[label] = row
        return choices, by_label

    def admin_pick_rule(self, title="Правило"):
        choices, by_label = self.admin_rule_choices(active_only=False)
        if not choices:
            QMessageBox.information(self, "Адмін", "Правил у RuleTemplates не знайдено.")
            return None
        label, ok = QInputDialog.getItem(self, title, "Виберіть правило:", choices, 0, False)
        if not ok or not label:
            return None
        return by_label.get(label)

    def add_combo_value(self, combo, value):
        value = str(value or "").strip()
        if value and combo.findText(value) < 0:
            combo.addItem(value)
        if value:
            combo.setCurrentText(value)

    def admin_rule_dialog_values(self, template=None, default_rule=None):
        template = template or {}
        rule = dict(default_rule or {})
        for key in (
            "k_w", "k_h", "growth_p_w", "growth_p_h",
            "growth_dir_x", "growth_dir_y", "shift_dir_x", "shift_dir_y",
            "link_x", "link_y",
        ):
            if key in template:
                rule[key] = template.get(key)

        dialog = QDialog(self)
        dialog.setWindowTitle("Правило обробки")
        form = QFormLayout(dialog)

        input_name = QLineEdit(str(template.get("name") or "Нове правило"))
        input_desc = QLineEdit(str(template.get("description") or ""))
        input_k_w = QLineEdit(str(rule.get("k_w", 0.0)))
        input_k_h = QLineEdit(str(rule.get("k_h", 0.0)))
        input_growth_p_w = QLineEdit(str(rule.get("growth_p_w", 0.0)))
        input_growth_p_h = QLineEdit(str(rule.get("growth_p_h", 0.0)))

        combo_growth_dir_x = QComboBox()
        combo_growth_dir_x.setEditable(True)
        combo_growth_dir_x.addItems(["Центр", "Вправо", "Вліво"])
        self.add_combo_value(combo_growth_dir_x, rule.get("growth_dir_x", "Центр"))

        combo_growth_dir_y = QComboBox()
        combo_growth_dir_y.setEditable(True)
        combo_growth_dir_y.addItems(["Центр", "Вгору", "Вниз"])
        self.add_combo_value(combo_growth_dir_y, rule.get("growth_dir_y", "Центр"))

        combo_shift_dir_x = QComboBox()
        combo_shift_dir_x.setEditable(True)
        combo_shift_dir_x.addItems(["Вправо", "Вліво"])
        self.add_combo_value(combo_shift_dir_x, rule.get("shift_dir_x", "Вправо"))

        combo_shift_dir_y = QComboBox()
        combo_shift_dir_y.setEditable(True)
        combo_shift_dir_y.addItems(["Вгору", "Вниз"])
        self.add_combo_value(combo_shift_dir_y, rule.get("shift_dir_y", "Вгору"))

        combo_link_x = QComboBox()
        combo_link_x.setEditable(True)
        combo_link_x.addItems(["X = W", "X = H"])
        self.add_combo_value(combo_link_x, rule.get("link_x", "X = W"))

        combo_link_y = QComboBox()
        combo_link_y.setEditable(True)
        combo_link_y.addItems(["Y = H", "Y = W"])
        self.add_combo_value(combo_link_y, rule.get("link_y", "Y = H"))

        check_system = QCheckBox("Системне")
        check_system.setChecked(bool(template.get("is_system", False)))
        check_active = QCheckBox("Активне")
        check_active.setChecked(bool(template.get("is_active", True)))

        form.addRow("Name:", input_name)
        form.addRow("Description:", input_desc)
        form.addRow("K_W:", input_k_w)
        form.addRow("K_H:", input_k_h)
        form.addRow("Growth_P_W:", input_growth_p_w)
        form.addRow("Growth_P_H:", input_growth_p_h)
        form.addRow("Growth_Dir_X:", combo_growth_dir_x)
        form.addRow("Growth_Dir_Y:", combo_growth_dir_y)
        form.addRow("Shift_Dir_X:", combo_shift_dir_x)
        form.addRow("Shift_Dir_Y:", combo_shift_dir_y)
        form.addRow("Link_X:", combo_link_x)
        form.addRow("Link_Y:", combo_link_y)
        form.addRow("", check_system)
        form.addRow("", check_active)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None

        return {
            "name": input_name.text().strip(),
            "description": input_desc.text().strip(),
            "rule": {
                "k_w": self.parse_numeric_text(input_k_w.text()) or 0.0,
                "k_h": self.parse_numeric_text(input_k_h.text()) or 0.0,
                "growth_p_w": self.parse_numeric_text(input_growth_p_w.text()) or 0.0,
                "growth_p_h": self.parse_numeric_text(input_growth_p_h.text()) or 0.0,
                "growth_dir_x": combo_growth_dir_x.currentText().strip() or "Центр",
                "growth_dir_y": combo_growth_dir_y.currentText().strip() or "Центр",
                "shift_dir_x": combo_shift_dir_x.currentText().strip() or "Вправо",
                "shift_dir_y": combo_shift_dir_y.currentText().strip() or "Вгору",
                "link_x": combo_link_x.currentText().strip() or "X = W",
                "link_y": combo_link_y.currentText().strip() or "Y = H",
            },
            "is_system": check_system.isChecked(),
            "is_active": check_active.isChecked(),
        }

    def admin_edit_rule_dialog(self, template=None, default_rule=None):
        values = self.admin_rule_dialog_values(template=template, default_rule=default_rule)
        if not values:
            return
        if template and template.get("id"):
            ok = self.db.update_rule_template(
                int(template.get("id")),
                values["name"],
                values["description"],
                values["rule"],
                self.current_user_id(),
                values["is_system"],
                values["is_active"],
            )
            message = "Правило оновлено."
        else:
            ok = bool(self.db.save_rule_template(
                values["name"],
                values["description"],
                values["rule"],
                self.current_user_id(),
                values["is_system"],
                values["is_active"],
            ))
            message = "Правило створено."
        if ok:
            self.refresh_rule_library_combo()
            QMessageBox.information(self, "Адмін", message)
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося зберегти правило:\n{self.db.last_error}")

    def admin_edit_rule_template(self):
        if not self.admin_require():
            return
        template = self.admin_pick_rule("Редагувати правило")
        if template:
            self.admin_edit_rule_dialog(template=template)

    def admin_delete_rule_template(self):
        if not self.admin_require():
            return
        template = self.admin_pick_rule("Вимкнути правило")
        if not template:
            return
        answer = QMessageBox.question(
            self,
            "Вимкнути правило",
            f"Вимкнути правило '{template.get('name')}'? Воно зникне зі списку активних правил.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        if self.db.delete_rule_template(int(template.get("id"))):
            self.refresh_rule_library_combo()
            QMessageBox.information(self, "Адмін", "Правило вимкнено.")
        else:
            QMessageBox.warning(self, "Адмін", f"Не вдалося вимкнути правило:\n{self.db.last_error}")

    def save_current_project_to_db(self, status="ConfigSaved"):
        if not getattr(self, "db", None) or not self.current_user_id():
            return
        dxf_bytes = self.dxf_doc_to_bytes() if self.is_db_file_open() else None
        file_name_override = getattr(self, "current_db_file_name", None) if self.is_db_file_open() else None

        project_file_id = self.db.save_project_snapshot(
            project_dir=self.project_dir,
            dxf_path=self.dxf_path,
            project_meta=self.project_meta,
            parametric_groups=self.parametric_groups,
            block_keep_state=self.block_keep_state,
            user_id=self.current_user_id(),
            status=status,
            project_file_id=getattr(self, "current_project_file_id", None),
            door_model_id=getattr(self, "current_door_model_id", None),
            dxf_bytes=dxf_bytes,
            file_name_override=file_name_override,
        )

        if project_file_id:
            self.current_project_file_id = project_file_id
            loaded = self.db.load_project_config(
                dxf_path=self.dxf_path,
                project_file_id=project_file_id,
                door_model_id=getattr(self, "current_door_model_id", None),
            )
            if loaded and loaded.get("door_model_id"):
                self.current_door_model_id = loaded.get("door_model_id")
            self.register_current_folder_model(show_errors=False)
            if hasattr(self, "lbl_status_calc"):
                self.lbl_status_calc.setText("<font color='#a5d6a7'>Проєкт/модель збережено в MSSQL.</font>")
        elif hasattr(self, "lbl_status_calc"):
            self.lbl_status_calc.setText(
                f"<font color='#ff9800'>БД не прийняла запис: {self.db.last_error}</font>"
            )

    def door_model_choices(self):
        models = self.db.list_door_models() if getattr(self, "db", None) else []
        choices = []
        by_label = {}
        for model in models:
            name = model.get("model_name") or f"Model {model.get('id')}"
            width = self.format_dimension_value(model.get("source_width"))
            height = self.format_dimension_value(model.get("source_height"))
            label = f"{model.get('id')} | {name} | {width} x {height} | файлів: {model.get('file_count', 0)}"
            choices.append(label)
            by_label[label] = model
        return choices, by_label

    def pick_door_model(self, title="Модель"):
        choices, by_label = self.door_model_choices()
        if not choices:
            QMessageBox.information(self, "Модель", "У БД немає моделей.")
            return None
        current_id = getattr(self, "current_door_model_id", None)
        current_index = 0
        for idx, label in enumerate(choices):
            if by_label[label].get("id") == current_id:
                current_index = idx
                break
        label, ok = QInputDialog.getItem(self, title, "Виберіть модель:", choices, current_index, False)
        if not ok or not label:
            return None
        return by_label.get(label)

    def edit_current_door_model(self):
        if not getattr(self, "db", None) or not getattr(self.db, "available", False):
            QMessageBox.warning(self, "Модель", "БД недоступна.")
            return

        model = None
        if getattr(self, "current_door_model_id", None):
            model = self.db.load_door_model(self.current_door_model_id)
            if model:
                model = {
                    "id": self.current_door_model_id,
                    "model_name": model.get("model_name"),
                    "source_width": (model.get("meta") or {}).get("source_width"),
                    "source_height": (model.get("meta") or {}).get("source_height"),
                    "source_door_opening": (model.get("meta") or {}).get("source_door_opening"),
                }
        if not model:
            model = self.pick_door_model("Редагувати модель")
        if not model:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редагувати модель")
        form = QFormLayout(dialog)
        input_name = QLineEdit(str(model.get("model_name") or f"Model {model.get('id')}"))
        input_width = QLineEdit(self.format_dimension_value(model.get("source_width")))
        input_height = QLineEdit(self.format_dimension_value(model.get("source_height")))
        combo_opening = QComboBox()
        combo_opening.addItems(["Ліве", "Праве"])
        if str(model.get("source_door_opening") or "").lower() == "right":
            combo_opening.setCurrentText("Праве")
        check_update_files = QCheckBox("Оновити W/H у всіх файлах цієї моделі")
        check_update_files.setChecked(True)
        form.addRow("Назва:", input_name)
        form.addRow("Початкова ширина W:", input_width)
        form.addRow("Початкова висота H:", input_height)
        form.addRow("Початкове відкривання:", combo_opening)
        form.addRow("", check_update_files)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        form.addRow(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        source_w = self.parse_numeric_text(input_width.text())
        source_h = self.parse_numeric_text(input_height.text())
        if source_w is None or source_h is None:
            QMessageBox.warning(self, "Модель", "Введіть коректні W та H.")
            return
        opening = "right" if combo_opening.currentText() == "Праве" else "left"
        ok = self.db.update_door_model_manual(
            int(model.get("id")),
            input_name.text().strip() or f"Model {model.get('id')}",
            source_w,
            source_h,
            opening,
            self.current_user_id(),
            update_project_files=check_update_files.isChecked(),
        )
        if not ok:
            QMessageBox.warning(self, "Модель", f"Не вдалося оновити модель:\n{self.db.last_error}")
            return

        if int(model.get("id")) == getattr(self, "current_door_model_id", None):
            self.project_meta["source_width"] = source_w
            self.project_meta["source_height"] = source_h
            self.project_meta["source_door_opening"] = opening
            self.project_meta["target_width"] = self.project_meta.get("target_width") or source_w
            self.project_meta["target_height"] = self.project_meta.get("target_height") or source_h
            self.update_dimension_inputs_from_meta()
            self.save_project_config()
        self.scan_project_folder_for_dxf()
        self.update_file_status_panel()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Параметри моделі оновлено.</font>")

    def attach_current_folder_to_model(self):
        if not getattr(self, "db", None) or not getattr(self.db, "available", False):
            QMessageBox.warning(self, "Модель", "БД недоступна.")
            return
        model = self.pick_door_model("Прив'язати до моделі")
        if not model:
            return
        target_model_id = int(model.get("id"))
        model_data = self.db.load_door_model(target_model_id)
        model_meta = (model_data or {}).get("meta") or {}

        if self.is_db_uri(getattr(self, "project_dir", "")):
            file_ids = []
            if getattr(self, "current_project_file_id", None):
                file_ids = [int(self.current_project_file_id)]
            elif getattr(self, "current_door_model_id", None):
                file_ids = [int(row.get("id")) for row in self.db.get_model_files(self.current_door_model_id)]
            if not file_ids:
                QMessageBox.warning(self, "Модель", "Немає DB-файлів для прив'язки.")
                return
            ok = self.db.assign_project_files_to_model(file_ids, target_model_id, self.current_user_id())
        else:
            register_meta = copy.deepcopy(self.project_meta)
            register_meta["source_width"] = model_meta.get("source_width")
            register_meta["source_height"] = model_meta.get("source_height")
            register_meta["source_door_opening"] = model_meta.get("source_door_opening") or "left"
            register_meta["door_opening"] = register_meta.get("door_opening") or register_meta["source_door_opening"]
            ok = bool(self.db.register_folder_dxf_files(
                self.project_dir,
                register_meta,
                self.current_user_id(),
                door_model_id=target_model_id,
            ))

        if not ok:
            QMessageBox.warning(self, "Модель", f"Не вдалося прив'язати:\n{self.db.last_error}")
            return

        self.current_door_model_id = target_model_id
        self.selected_db_model_id = target_model_id
        if model_data:
            self.project_meta["source_width"] = model_meta.get("source_width")
            self.project_meta["source_height"] = model_meta.get("source_height")
            self.project_meta["source_door_opening"] = model_meta.get("source_door_opening") or "left"
            self.project_meta["target_width"] = self.project_meta.get("target_width") or model_meta.get("source_width")
            self.project_meta["target_height"] = self.project_meta.get("target_height") or model_meta.get("source_height")
        self.update_dimension_inputs_from_meta()
        self.scan_project_folder_for_dxf()
        self.update_file_status_panel()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Папку/файли прив'язано до вибраної моделі.</font>")

    def delete_door_model_from_server(self):
        if not getattr(self, "db", None) or not getattr(self.db, "available", False):
            QMessageBox.warning(self, "Модель", "БД недоступна.")
            return
        if not self.admin_require():
            return

        model = self.pick_door_model("Видалити модель з сервера")
        if not model:
            return

        model_id = int(model.get("id"))
        model_name = model.get("model_name") or f"Model {model_id}"
        file_count = int(model.get("file_count") or 0)
        answer = QMessageBox.question(
            self,
            "Видалити модель",
            (
                f"Видалити модель '{model_name}' з сервера?\n\n"
                f"Буде видалено модель, {file_count} DXF-файлів, групи та експорти цієї моделі."
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        confirm, ok = QInputDialog.getText(
            self,
            "Підтвердження видалення",
            "Для підтвердження введіть DELETE:"
        )
        if not ok or confirm.strip().upper() != "DELETE":
            return

        if not self.db.delete_door_model(model_id):
            QMessageBox.warning(self, "Модель", f"Не вдалося видалити модель:\n{self.db.last_error}")
            return

        if getattr(self, "current_door_model_id", None) == model_id:
            self.current_door_model_id = None
            self.selected_db_model_id = None
            self.current_project_file_id = None
            self.current_db_file_name = None
            self.dxf_path = os.path.join(self.project_dir if not self.is_db_uri(getattr(self, "project_dir", "")) else os.getcwd(), "drawing.DXF")
            self.doc = ezdxf.new()
            self.selected_handles.clear()
            self.parametric_groups.clear()
            self.block_keep_state.clear()
            self.save_original_geometries()
            self.update_viewer()
            self.load_entities_into_list()
            self.load_groups_into_list()
            self.load_block_filter_list()

        self.scan_project_folder_for_dxf()
        self.update_file_status_panel()
        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Модель видалено з сервера: {model_name}</font>")


    def register_current_folder_model(self, show_errors=True):
        """One folder = one DoorModel. Register all DXF files in this folder under the same model."""
        if not getattr(self, "db", None) or not self.current_user_id():
            return None
        if self.is_db_uri(getattr(self, "project_dir", "")):
            return getattr(self, "current_door_model_id", None)

        try:
            door_model_id = self.db.register_folder_dxf_files(
                self.project_dir,
                self.project_meta,
                self.current_user_id(),
                getattr(self, "current_door_model_id", None),
            )
        except TypeError:
            door_model_id = self.db.register_folder_dxf_files(
                self.project_dir,
                self.project_meta,
                self.current_user_id(),
            )

        if door_model_id:
            self.current_door_model_id = door_model_id
            return door_model_id

        if show_errors and hasattr(self, "lbl_status_calc"):
            self.lbl_status_calc.setText(
                f"<font color='#ff9800'>Не вдалося зареєструвати папку як модель: {self.db.last_error}</font>"
            )
        return None

    def save_export_to_db(self, export_path, status="Exported"):
        if not getattr(self, "db", None) or not self.current_user_id():
            return
        if not getattr(self, "current_project_file_id", None):
            self.save_current_project_to_db("BeforeExport")
        if not getattr(self, "current_project_file_id", None):
            return

        self.db.save_export_file(
            self.current_project_file_id,
            export_path,
            self.project_meta.get("target_width"),
            self.project_meta.get("target_height"),
            self.export_target_opening(),
            self.current_user_id(),
            getattr(self, "current_door_model_id", None),
        )

    def save_export_doc_to_db(self, export_doc, export_file_name):
        if not getattr(self, "db", None) or not self.current_user_id():
            return False
        if not getattr(self, "current_project_file_id", None):
            self.save_current_project_to_db("BeforeExport")
        if not getattr(self, "current_project_file_id", None):
            return False

        return self.db.save_export_file_bytes(
            self.current_project_file_id,
            export_file_name,
            self.dxf_doc_to_bytes(export_doc),
            self.project_meta.get("target_width"),
            self.project_meta.get("target_height"),
            self.export_target_opening(),
            self.current_user_id(),
            getattr(self, "current_door_model_id", None),
        )

    def select_all_entities(self):
        self.selected_handles.clear()

        for i in range(self.entity_list.count()):
            item = self.entity_list.item(i)
            handle = item.data(Qt.UserRole)

            if handle is None:
                continue

            self.selected_handles.add(str(handle))
            item.setSelected(True)

        self.update_viewer()
        # self.sync_entity_list_selection()


    def clear_selection(self):
        self.selected_handles.clear()
        self.entity_list.clearSelection()
        self.group_list_widget.clearSelection()
        self.update_viewer()


    def zoom_extents(self):
        self.view.fitInView(
            self.scene.itemsBoundingRect(),
            Qt.KeepAspectRatio
        )


    def load_project_config(self):
        """
        Основне завантаження тільки з MSSQL.

        1) шукаємо DoorModel по поточній папці;
        2) шукаємо ProjectFile по DoorModelId + FileName;
        3) якщо файл ще не має груп, але DoorModel має початкові розміри —
           підтягуємо W/H/відкривання з DoorModels;
        4) JSON автоматично не читаємо.
        """
        self.parametric_groups.clear()
        self.project_meta = self.default_project_meta()
        self.block_keep_state = {}

        if not getattr(self, "db", None) or not getattr(self.db, "available", False):
            return

        try:
            if not getattr(self, "current_door_model_id", None):
                model_id = self.db.find_door_model_by_folder(self.project_dir)
                if model_id:
                    self.current_door_model_id = model_id

            loaded = None
            if getattr(self, "current_door_model_id", None):
                loaded = self.db.load_project_config(
                    dxf_path=self.dxf_path,
                    project_file_id=getattr(self, "current_project_file_id", None),
                    door_model_id=getattr(self, "current_door_model_id", None),
                    file_name=self.current_dxf_file_name(),
                )

            if not loaded and getattr(self, "current_door_model_id", None):
                model_data = self.db.load_door_model(self.current_door_model_id)
                if model_data:
                    meta = model_data.get("meta") or {}
                    # DoorModels дає тільки спільні параметри папки.
                    # Осі файлу не підтягуємо з DoorModels, бо вони окремі для кожного DXF.
                    self.project_meta["source_width"] = meta.get("source_width")
                    self.project_meta["source_height"] = meta.get("source_height")
                    self.project_meta["target_width"] = meta.get("target_width")
                    self.project_meta["target_height"] = meta.get("target_height")
                    self.project_meta["source_door_opening"] = meta.get("source_door_opening") or "left"
                    self.project_meta["target_door_opening"] = meta.get("target_door_opening") or self.project_meta["source_door_opening"]
                    self.project_meta["door_opening"] = meta.get("door_opening") or self.project_meta["source_door_opening"]

                    link_x, link_y = self.link_pair_for_mode(self.project_meta.get("axis_link_mode", "normal"))
                    self.project_meta["link_x"] = link_x
                    self.project_meta["link_y"] = link_y
                    text_settings = self.default_text_settings()
                    text_settings.update(self.project_meta.get("door_text") or {})
                    
                    self.project_meta["door_text"] = text_settings
                    return

            if not loaded:
                return

            self.current_project_file_id = loaded.get("project_file_id")
            if loaded.get("door_model_id"):
                self.current_door_model_id = loaded.get("door_model_id")

            self.project_meta.update(loaded.get("meta") or {})
            link_x, link_y = self.link_pair_for_mode(self.project_meta.get("axis_link_mode", "normal"))
            self.project_meta["link_x"] = link_x
            self.project_meta["link_y"] = link_y
            text_settings = self.default_text_settings()
            text_settings.update(self.project_meta.get("door_text") or {})
            self.project_meta["door_text"] = text_settings

            self.parametric_groups = loaded.get("groups") or []
            self.block_keep_state = loaded.get("block_keep_state") or {}

        except Exception as exc:
            print(f"Помилка завантаження конфігурації з БД: {exc}")

        for g in self.parametric_groups:
            g["handles"] = set(g.get("handles", []))
            self.get_group_key(g)

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

            # Прив'язка осей груп береться з AxisLinkMode файлу, а не зі старих значень групи.
            g["link_x"], g["link_y"] = self.link_pair_for_mode()

            if "growth_direction" in g:
                old_dir = g.pop("growth_direction")
                g["growth_dir_x"] = "Вправо" if "Вправо" in old_dir else ("Вліво" if "Вліво" in old_dir else "Центр")
                g["growth_dir_y"] = "Вгору" if "Вгору" in old_dir else ("Вниз" if "Вниз" in old_dir else "Центр")
            else:
                g["growth_dir_x"] = g.get("growth_dir_x", "Центр")
                g["growth_dir_y"] = g.get("growth_dir_y", "Центр")

            g["shift_dir_x"] = g.get("shift_dir_x", "Вправо")
            g["shift_dir_y"] = g.get("shift_dir_y", "Вгору")
            g["role_y"] = g.get("role_y", "manual")
            g["auto_rule"] = bool(g.get("auto_rule", False))
            g["touch_y_enabled"] = bool(g.get("touch_y_enabled", False))
            g["touch_to_uid"] = g.get("touch_to_uid")
            g["touch_gap_y"] = float(g.get("touch_gap_y", 0.0) or 0.0)

            if "resizes" not in g:
                g["resizes"] = (
                    abs(float(g.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
                    abs(float(g.get("growth_p_h", 0.0) or 0.0)) > 0.000001
                )

            key = self.get_group_key(g)
            if key not in self.block_keep_state:
                self.block_keep_state[key] = True

            self.apply_growth_axis_to_group(g)

        self.apply_axis_link_mode_to_groups()

    def save_project_config(self):
        """Замість JSON пишемо конфігурацію в MSSQL."""
        self.project_meta["keep_blocks"] = [name for name, keep in self.block_keep_state.items() if keep]
        self.project_meta["delete_blocks"] = [name for name, keep in self.block_keep_state.items() if not keep]
        self.save_current_project_to_db("ConfigSaved")


    def load_config_from_json_file(self):
        """
        Ручне завантаження старої JSON-конфігурації.

        Це єдине місце, де JSON читається.
        Після завантаження дані одразу записуються в MSSQL.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Завантажити налаштування з JSON",
            self.project_dir,
            "JSON Files (*.json);;All Files (*)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            self.parametric_groups.clear()
            self.block_keep_state = {}

            if isinstance(raw_data, dict):
                self.project_meta.update(raw_data.get("meta", {}))
                text_settings = self.default_text_settings()
                text_settings.update(self.project_meta.get("door_text") or {})
                self.project_meta["door_text"] = text_settings
                self.parametric_groups = raw_data.get("groups", [])
                self.block_keep_state = raw_data.get("block_keep_state", {}) or {}
            elif isinstance(raw_data, list):
                self.parametric_groups = raw_data
            else:
                QMessageBox.warning(self, "JSON", "Невідомий формат JSON-файлу.")
                return

            for g in self.parametric_groups:
                g["handles"] = set(g.get("handles", []))
                self.get_group_key(g)

                g["k_w"] = g.get("k_w", g.get("k_x", 0.0))
                g["k_h"] = g.get("k_h", g.get("k_y", 0.0))
                g["growth_p_w"] = g.get("growth_p_w", g.get("growth_p_x", 0.0))
                g["growth_p_h"] = g.get("growth_p_h", g.get("growth_p_y", 0.0))

                g["growth_dir_x"] = g.get("growth_dir_x", "Центр")
                g["growth_dir_y"] = g.get("growth_dir_y", "Центр")
                g["shift_dir_x"] = g.get("shift_dir_x", "Вправо")
                g["shift_dir_y"] = g.get("shift_dir_y", "Вгору")
                g["link_x"] = g.get("link_x", "X = W")
                g["link_y"] = g.get("link_y", "Y = H")
                g["resizes"] = bool(g.get("resizes", False))

                key = self.get_group_key(g)
                if key not in self.block_keep_state:
                    self.block_keep_state[key] = True

            self.save_project_config()
            self.update_dimension_inputs_from_meta()
            self.update_viewer()
            self.load_groups_into_list()
            self.load_block_filter_list()
            self.update_file_status_panel()

            QMessageBox.information(
                self,
                "JSON",
                "Налаштування завантажено з JSON і збережено в MSSQL."
            )

        except Exception as exc:
            QMessageBox.critical(self, "JSON", f"Не вдалося завантажити JSON:\n{exc}")

    def load_ui_shell(self):
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "main_window.ui")
        shell = load_designer_shell(self, ui_path)
        if shell:
            self.setCentralWidget(shell["widget"])
            self._designer_shell = shell
            self.central_layout = None
            return
        self._designer_shell = create_fallback_shell(self)
        self.central_layout = self._designer_shell["central"]

    def add_main_panel(self, widget, area, stretch=0):
        shell_layout = getattr(self, "_designer_shell", {}).get(area)
        if shell_layout is not None:
            shell_layout.addWidget(widget)
            return
        self.central_layout.addWidget(widget, stretch=stretch)

    def db_opening_enabled(self):
        return bool(getattr(self, "db", None) and getattr(self.db, "available", False))

    def is_db_uri(self, value):
        return str(value or "").startswith("db://")

    def is_db_file_open(self):
        return bool(getattr(self, "current_project_file_id", None) and self.is_db_uri(getattr(self, "dxf_path", "")))

    def current_dxf_file_name(self):
        if self.is_db_file_open():
            return getattr(self, "current_db_file_name", None) or f"project_file_{self.current_project_file_id}.dxf"
        return os.path.basename(self.dxf_path)

    def current_dxf_bytes(self):
        if self.is_db_file_open():
            return self.dxf_doc_to_bytes()
        if os.path.exists(self.dxf_path):
            with open(self.dxf_path, "rb") as f:
                return f.read()
        return None

    def read_dxf_doc_from_bytes(self, data):
        if isinstance(data, memoryview):
            data = data.tobytes()
        raw = bytes(data)
        last_error = None
        for encoding in ("utf-8", "cp1251", "cp1252", "latin1"):
            try:
                stream = io.TextIOWrapper(
                    io.BytesIO(raw),
                    encoding=encoding,
                    errors="surrogateescape",
                    newline=None,
                )
                doc = ezdxf.read(stream)
                doc._parametric_source_encoding = encoding
                return doc
            except Exception as exc:
                last_error = exc
        raise RuntimeError(f"Не вдалося прочитати DXF з БД як текстовий DXF: {last_error}")

    def dxf_doc_to_bytes(self, doc=None):
        stream = io.StringIO()
        (doc or self.doc).write(stream)
        return stream.getvalue().encode("utf-8", errors="surrogateescape")

    def make_history_manager(self):
        if self.is_db_file_open():
            return MemoryHistoryManager(self)
        return HistoryManager(self.dxf_path)

    def save_current_dxf(self):
        if self.is_db_file_open():
            self.db.update_project_file_binary(
                self.current_project_file_id,
                self.dxf_doc_to_bytes(),
            )
            return
        self.doc.saveas(self.dxf_path)

    def init_ui(self):
        self.load_ui_shell()

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

        self.btn_open_db_file = QPushButton("DB Відкрити з БД")
        self.btn_open_db_file.setStyleSheet("background-color: #455a64; color: white; font-weight: bold; padding: 4px;")
        self.btn_open_db_file.clicked.connect(self.open_dxf_from_db_picker)
        folder_explorer_layout.addWidget(self.btn_open_db_file)

        self.btn_load_json_settings = QPushButton("📥 Завантажити налаштування JSON")
        self.btn_load_json_settings.setStyleSheet("background-color: #455a64; color: white; font-weight: bold; padding: 4px;")
        self.btn_load_json_settings.clicked.connect(self.load_config_from_json_file)
        folder_explorer_layout.addWidget(self.btn_load_json_settings)
        
        self.file_explorer_list = QTreeWidget()
        self.file_explorer_list.setHeaderHidden(True)
        self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
        folder_explorer_layout.addWidget(self.file_explorer_list)
        self.add_main_panel(folder_explorer_widget, "folder", stretch=1)

        self.scene = QGraphicsScene()
        self.view = AdvancedGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setMouseTracking(True)  
        self.scene.mouseMoveEvent = self.on_scene_mouse_move
        self.add_main_panel(self.view, "view", stretch=5)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        control_panel = QWidget()
        control_panel_layout = QVBoxLayout(control_panel)
        control_panel_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_area.setWidget(control_panel)
        self.add_main_panel(self.scroll_area, "side", stretch=4)

        self.file_status_group = QGroupBox("Стан файлу")
        file_status_box = QGridLayout()
        file_status_box.setSpacing(4) 
        file_status_box.setContentsMargins(6, 12, 6, 6)

        self.lbl_file_status_source = QLabel("")
        self.lbl_file_status_target = QLabel("")
        self.lbl_file_status_opening = QLabel("")
        self.lbl_file_status_axis = QLabel("")
        self.lbl_file_status_db = QLabel("")

        file_status_box.addWidget(self.lbl_file_status_source, 0, 0)
        file_status_box.addWidget(self.lbl_file_status_target, 0, 1)
        file_status_box.addWidget(self.lbl_file_status_opening, 1, 0)
        file_status_box.addWidget(self.lbl_file_status_axis, 1, 1)
        file_status_box.addWidget(self.lbl_file_status_db, 2, 0, 1, 2)

        file_status_box.addWidget(QLabel("Осі файлу:"), 3, 0)

        axis_box = QHBoxLayout()

        self.combo_link_x = QComboBox()
        self.combo_link_x.addItems(["X = W", "X = H"])
        self.combo_link_x.setEnabled(True)
        self.combo_link_x.setToolTip("Глобальна прив'язка осей для всього файлу")
        axis_box.addWidget(self.combo_link_x)

        self.combo_link_y = QComboBox()
        self.combo_link_y.addItems(["Y = H", "Y = W"])
        self.combo_link_y.setEnabled(False)
        self.combo_link_y.setToolTip("Глобальна прив'язка осей для всього файлу")
        axis_box.addWidget(self.combo_link_y)

        file_status_box.addLayout(axis_box, 3, 1)

        self.file_status_group.setLayout(file_status_box)
        control_panel_layout.addWidget(self.file_status_group)

        model_actions_box = QHBoxLayout()
        self.btn_edit_door_model = QPushButton("Редагувати модель W/H")
        self.btn_edit_door_model.clicked.connect(self.edit_current_door_model)
        model_actions_box.addWidget(self.btn_edit_door_model)
        self.btn_attach_folder_to_model = QPushButton("Папку до моделі")
        self.btn_attach_folder_to_model.clicked.connect(self.attach_current_folder_to_model)
        model_actions_box.addWidget(self.btn_attach_folder_to_model)
        self.btn_delete_door_model = QPushButton("Видалити модель")
        self.btn_delete_door_model.clicked.connect(self.delete_door_model_from_server)
        model_actions_box.addWidget(self.btn_delete_door_model)
        control_panel_layout.addLayout(model_actions_box)

        self.side_tabs = QTabWidget()
        self.side_tabs.setDocumentMode(True)
        self.side_tabs.setUsesScrollButtons(True)
        self.tab_file = QWidget()
        self.tab_sizes = QWidget()
        self.tab_groups = QWidget()
        self.tab_text = QWidget()
        self.tab_more = QWidget()
        self.tab_file_layout = QVBoxLayout(self.tab_file)
        self.tab_sizes_layout = QVBoxLayout(self.tab_sizes)
        self.tab_groups_layout = QVBoxLayout(self.tab_groups)
        self.tab_text_layout = QVBoxLayout(self.tab_text)
        self.tab_more_layout = QVBoxLayout(self.tab_more)
        for layout in (
            self.tab_file_layout,
            self.tab_sizes_layout,
            self.tab_groups_layout,
            self.tab_text_layout,
            self.tab_more_layout,
        ):
            layout.setContentsMargins(3, 3, 3, 3)
            layout.setSpacing(4)
        self.side_tabs.addTab(self.tab_file, "Файл")
        self.side_tabs.addTab(self.tab_sizes, "Розміри")
        self.side_tabs.addTab(self.tab_groups, "Групи")
        self.side_tabs.addTab(self.tab_text, "Текст")
        self.side_tabs.addTab(self.tab_more, "Інше")
        control_panel_layout.addWidget(self.side_tabs)

        inspector_group = QGroupBox("")
        inspector_box = QVBoxLayout()
        self.chk_enable_inspector = QCheckBox(" Ввімкнути інтерактивний трекер точок")
        self.chk_enable_inspector.setStyleSheet("color: #ff9800; font-weight: bold;")
        self.chk_enable_inspector.clicked.connect(self.toggle_inspector_mode)
        inspector_box.addWidget(self.chk_enable_inspector)
        
        self.btn_snap_zero = QPushButton("↙️ Притиснути фігуру до (0, 0)")
        self.btn_snap_zero.setStyleSheet("background-color: #00897b; color: white; font-weight: bold; padding: 6px;")
        self.btn_snap_zero.clicked.connect(self.snap_to_zero)
        inspector_box.addWidget(self.btn_snap_zero)
        
        inspector_group.setLayout(inspector_box)
        self.tab_more_layout.addWidget(inspector_group)

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
        self.tab_file_layout.addWidget(self.transform_group)

        auto_scale_group = QGroupBox(" Параметрична трансформація розмірів")
        auto_scale_box = QVBoxLayout()

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Ширина:"))
        self.input_current_width = QLineEdit("1000")
        width_layout.addWidget(self.input_current_width)
        width_layout.addWidget(QLabel("➡️ Нова:"))
        self.input_target_width = QLineEdit("1050")
        width_layout.addWidget(self.input_target_width)
        auto_scale_box.addLayout(width_layout)

        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Висота:"))
        self.input_current_height = QLineEdit("2000")
        height_layout.addWidget(self.input_current_height)
        height_layout.addWidget(QLabel("➡️ Нова:"))
        self.input_target_height = QLineEdit("2080")
        height_layout.addWidget(self.input_target_height)
        auto_scale_box.addLayout(height_layout)

        self.lbl_status_calc = QLabel("Задайте нові розміри конструкції для автоматичного морфінгу.")
        self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
        auto_scale_box.addWidget(self.lbl_status_calc)

        self.btn_apply_auto_scale = QPushButton(" Запустити глобальний перерахунок")
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

        # self.btn_find_min_size = QPushButton("Мінімум без накладання")
        # self.btn_find_min_size.clicked.connect(self.find_minimum_safe_size)
        # auto_scale_box.addWidget(self.btn_find_min_size)

        auto_scale_group.setLayout(auto_scale_box)
        self.tab_sizes_layout.addWidget(auto_scale_group)

        opening_group = QGroupBox("Відкривання")
        opening_box = QHBoxLayout()
        opening_box.addWidget(QLabel("Початкове:"))
        self.combo_source_door_opening = QComboBox()
        self.combo_source_door_opening.addItems(["Ліве", "Праве"])
        self.combo_source_door_opening.currentTextChanged.connect(self.on_source_door_opening_changed)
        opening_box.addWidget(self.combo_source_door_opening)
        opening_box.addWidget(QLabel("Отримати:"))
        self.combo_door_opening = QComboBox()
        self.combo_door_opening.addItems(["Ліве", "Праве"])
        self.combo_door_opening.currentTextChanged.connect(self.on_door_opening_changed)
        opening_box.addWidget(self.combo_door_opening)
        self.btn_mirror_opening = QPushButton("Змінити L/R")
        self.btn_mirror_opening.clicked.connect(self.mirror_door_opening)
        opening_box.addWidget(self.btn_mirror_opening)
        opening_group.setLayout(opening_box)
        self.tab_sizes_layout.addWidget(opening_group)

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
        self.text_group = text_group
        self.text_box_layout = text_box
        text_group.setCheckable(True)
        text_group.toggled.connect(self.set_text_panel_expanded)
        text_settings = self.project_meta.get("door_text", {})
        text_open = bool(
            text_settings.get("enabled") or
            str(text_settings.get("text", "")).strip() or
            text_settings.get("handle")
        )
        text_group.setChecked(text_open)
        self.set_text_panel_expanded(text_open)
        self.tab_text_layout.addWidget(text_group)
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
        self.tab_file_layout.addWidget(history_group)

        group_constructor_group = QGroupBox(" Параметричні групи топології")
        group_box = QVBoxLayout()

        self.btn_create_group = QPushButton(" Створити параметричну групу")
        self.btn_create_group.setStyleSheet("background-color: #673ab7; color: white; font-weight: bold;")
        self.btn_create_group.clicked.connect(self.create_parametric_group)
        group_box.addWidget(self.btn_create_group)

        self.btn_auto_group_entities = QPushButton("Автогрупувати")
        self.btn_auto_group_entities.setStyleSheet("background-color: #455a64; color: white; font-weight: bold;")
        self.btn_auto_group_entities.clicked.connect(self.auto_group_entities)
        self.btn_auto_group_entities.hide()

        self.btn_delete_from_dxf = QPushButton(" Видалити об'єкти з креслення (DXF)")
        self.btn_delete_from_dxf.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        self.btn_delete_from_dxf.clicked.connect(self.delete_entities_from_dxf)
        group_box.addWidget(self.btn_delete_from_dxf)

        self.btn_remove_selected = QPushButton(" Виключити виділене з групи")
        self.btn_remove_selected.clicked.connect(self.remove_selected_from_group)
        group_box.addWidget(self.btn_remove_selected)

        self.btn_disband_group = QPushButton("Розформувати вибрану групу")
        self.btn_disband_group.clicked.connect(self.disband_parametric_group)
        group_box.addWidget(self.btn_disband_group)

        group_box.addWidget(QLabel("<b>Параметричні групи деталей:</b>"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setFixedHeight(76)
        self.group_list_widget.itemSelectionChanged.connect(self.on_group_selection_changed)
        group_box.addWidget(self.group_list_widget)

        group_box.addWidget(QLabel("<b>Блоки для нового DXF (галочка = лишити):</b>"))
        self.block_filter_list = QListWidget()
        self.block_filter_list.setFixedHeight(70)
        self.block_filter_list.itemChanged.connect(self.on_block_keep_state_changed)
        group_box.addWidget(self.block_filter_list)

   
        group_box.addWidget(QLabel("<b> Параметри трансформації:</b>"))
        
        growth_axis_layout = QHBoxLayout()
        growth_axis_layout.addWidget(QLabel("Режим файлу:"))
        self.combo_group_growth_axis = QComboBox()
        self.combo_group_growth_axis.addItems(["Ширина + висота", "Тільки ширина", "Тільки висота", "Не росте"])
        self.combo_group_growth_axis.currentTextChanged.connect(self.on_group_growth_axis_changed)
        growth_axis_layout.addWidget(self.combo_group_growth_axis)
        group_box.addLayout(growth_axis_layout)

        self.chk_group_resizes = QCheckBox("Група змінює розмір")
        self.chk_group_resizes.stateChanged.connect(self.on_group_resizes_changed)
        group_box.addWidget(self.chk_group_resizes)

        grid = QGridLayout()
        self.param_transform_grid = grid
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(4)
        grid.setVerticalSpacing(3)

        preset_items = [
            "0% (Фіксовано)",
            "25% (1/4)",
            "33.3% (1/3)",
            "50% (Центр / Δ/2)",
            "66.7% (2/3)",
            "75% (1/4)",
            "100% (Δ/1)",
            "Ввести вручну"
        ]

        self.combo_k_w = QComboBox()
        self.combo_k_w.setEditable(True)
        self.combo_k_w.addItems(preset_items)

        self.combo_shift_dir_x = QComboBox()
        self.combo_shift_dir_x.addItems(["Вправо", "Вліво"])

        self.combo_growth_p_w = QComboBox()
        self.combo_growth_p_w.setEditable(True)
        self.combo_growth_p_w.addItems(preset_items)

        self.combo_growth_dir_x = QComboBox()
        self.combo_growth_dir_x.addItems(["Вправо", "Вліво", "Центр"])

        self.combo_k_h = QComboBox()
        self.combo_k_h.setEditable(True)
        self.combo_k_h.addItems(preset_items)

        self.combo_shift_dir_y = QComboBox()
        self.combo_shift_dir_y.addItems(["Вгору", "Вниз"])

        self.combo_growth_p_h = QComboBox()
        self.combo_growth_p_h.setEditable(True)
        self.combo_growth_p_h.addItems(preset_items)

        self.combo_growth_dir_y = QComboBox()
        self.combo_growth_dir_y.addItems(["Вгору", "Вниз", "Центр"])

        self.lbl_shift_x = QLabel("X зсув")
        self.lbl_growth_x = QLabel("X ріст")
        self.lbl_shift_y = QLabel("Y зсув")
        self.lbl_growth_y = QLabel("Y ріст")

        grid.addWidget(self.lbl_shift_x, 0, 0)
        grid.addWidget(self.combo_k_w, 0, 1)
        grid.addWidget(self.combo_shift_dir_x, 0, 2)

        grid.addWidget(self.lbl_growth_x, 1, 0)
        grid.addWidget(self.combo_growth_p_w, 1, 1)
        grid.addWidget(self.combo_growth_dir_x, 1, 2)

        grid.addWidget(self.lbl_shift_y, 2, 0)
        grid.addWidget(self.combo_k_h, 2, 1)
        grid.addWidget(self.combo_shift_dir_y, 2, 2)

        grid.addWidget(self.lbl_growth_y, 3, 0)
        grid.addWidget(self.combo_growth_p_h, 3, 1)
        grid.addWidget(self.combo_growth_dir_y, 3, 2)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)

        group_box.addLayout(grid)

        rule_layout = QHBoxLayout()
        self.combo_rule_library = QComboBox()
        self.refresh_rule_library_combo()
        rule_layout.addWidget(self.combo_rule_library)
        self.btn_apply_rule = QPushButton("Застосувати правило")
        self.btn_apply_rule.clicked.connect(self.apply_selected_rule_to_group)
        rule_layout.addWidget(self.btn_apply_rule)
        group_box.addLayout(rule_layout)

        topology_layout = QHBoxLayout()
        # self.btn_auto_rules_y = QPushButton("Авто правила Y")
        # self.btn_auto_rules_y.setStyleSheet("background-color: #455a64; color: white; font-weight: bold;")
        # self.btn_auto_rules_y.clicked.connect(self.auto_apply_vertical_topology_rules)
        # topology_layout.addWidget(self.btn_auto_rules_y)

        # self.btn_touch_rules_y = QPushButton("Зберігати дотик Y")
        # self.btn_touch_rules_y.setStyleSheet("background-color: #00695c; color: white; font-weight: bold;")
        # self.btn_touch_rules_y.clicked.connect(self.auto_detect_vertical_touch_constraints)
        # topology_layout.addWidget(self.btn_touch_rules_y)

        self.btn_auto_chain_growth_y = QPushButton("Авто сума росту Y")
        self.btn_auto_chain_growth_y.setStyleSheet("background-color: #1565c0; color: white; font-weight: bold;")
        self.btn_auto_chain_growth_y.clicked.connect(self.auto_chain_growth_y)
        self.btn_auto_chain_growth_y.hide()

        self.btn_auto_chain_growth_x = QPushButton("Авто сума росту X")
        self.btn_auto_chain_growth_x.setStyleSheet("background-color: #6a1b9a; color: white; font-weight: bold;")
        self.btn_auto_chain_growth_x.clicked.connect(self.auto_chain_growth_x)
        self.btn_auto_chain_growth_x.hide()

        self.btn_auto_layout_all = QPushButton("Авторозставити все")
        self.btn_auto_layout_all.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        self.btn_auto_layout_all.clicked.connect(self.auto_layout_all_groups)
        self.btn_auto_layout_all.hide()

        # self.btn_auto_mirror_x = QPushButton("Дзеркальні сторони X")
        # self.btn_auto_mirror_x.setStyleSheet("background-color: #8d6e63; color: white; font-weight: bold;")
        # self.btn_auto_mirror_x.clicked.connect(self.confirm_and_apply_mirror_x_rules)
        # topology_layout.addWidget(self.btn_auto_mirror_x)
        group_box.addLayout(topology_layout)

        # Підключення сигналів сітки

        
        self.combo_k_w.currentTextChanged.connect(self.on_combo_k_w_changed)
        self.combo_k_h.currentTextChanged.connect(self.on_combo_k_h_changed)
        self.combo_growth_p_w.currentTextChanged.connect(self.on_combo_growth_p_w_changed)
        self.combo_growth_p_h.currentTextChanged.connect(self.on_combo_growth_p_h_changed)
        
        self.combo_growth_dir_x.currentTextChanged.connect(self.on_growth_dir_x_changed)
        self.combo_growth_dir_y.currentTextChanged.connect(self.on_growth_dir_y_changed)
        self.combo_shift_dir_x.currentTextChanged.connect(self.on_shift_dir_x_changed)
        self.combo_shift_dir_y.currentTextChanged.connect(self.on_shift_dir_y_changed)


        self.combo_link_x.currentTextChanged.connect(self.on_link_x_changed)
        self.combo_link_y.currentTextChanged.connect(self.on_link_y_changed)
        # -------------------------------------------------------------

        group_constructor_group.setLayout(group_box)
        self.tab_groups_layout.addWidget(group_constructor_group)

        self.tab_groups_layout.addWidget(QLabel("<b>Повний список ліній/отворів у файлі:</b>"))
        self.entity_list = QListWidget()
        self.entity_list.setFixedHeight(86)
        self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        self.tab_groups_layout.addWidget(self.entity_list)

        theme_group = QGroupBox(" Інтерфейс")
        theme_box = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темна", "Світла"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_box.addWidget(self.theme_combo)
        theme_group.setLayout(theme_box)
        self.tab_more_layout.addWidget(theme_group)

        account_group = QGroupBox("Акаунт")
        account_box = QVBoxLayout()
        self.btn_logout = QPushButton("Вийти з акаунта")
        self.btn_logout.clicked.connect(self.logout_user)
        account_box.addWidget(self.btn_logout)
        account_group.setLayout(account_box)
        self.tab_more_layout.addWidget(account_group)

        self.admin_group = QGroupBox("Адміністрування")
        admin_box = QVBoxLayout()
        self.btn_admin_add_user = QPushButton("Додати користувача")
        self.btn_admin_add_user.clicked.connect(self.admin_add_user)
        admin_box.addWidget(self.btn_admin_add_user)
        self.btn_admin_edit_user = QPushButton("Редагувати користувача")
        self.btn_admin_edit_user.clicked.connect(self.admin_edit_user)
        admin_box.addWidget(self.btn_admin_edit_user)
        self.btn_admin_delete_user = QPushButton("Видалити користувача")
        self.btn_admin_delete_user.clicked.connect(self.admin_delete_user)
        admin_box.addWidget(self.btn_admin_delete_user)
        self.btn_admin_add_group_name = QPushButton("Додати назву групи")
        self.btn_admin_add_group_name.clicked.connect(self.admin_add_group_name)
        admin_box.addWidget(self.btn_admin_add_group_name)
        self.btn_admin_save_rule = QPushButton("Зберегти правило з вибраної групи")
        self.btn_admin_save_rule.clicked.connect(self.admin_save_selected_group_rule)
        admin_box.addWidget(self.btn_admin_save_rule)
        self.btn_admin_add_rule = QPushButton("Додати правило вручну")
        self.btn_admin_add_rule.clicked.connect(self.admin_add_rule_from_controls)
        admin_box.addWidget(self.btn_admin_add_rule)
        self.btn_admin_edit_rule = QPushButton("Редагувати правило")
        self.btn_admin_edit_rule.clicked.connect(self.admin_edit_rule_template)
        admin_box.addWidget(self.btn_admin_edit_rule)
        self.btn_admin_delete_rule = QPushButton("Вимкнути правило")
        self.btn_admin_delete_rule.clicked.connect(self.admin_delete_rule_template)
        admin_box.addWidget(self.btn_admin_delete_rule)
        self.admin_group.setLayout(admin_box)
        self.admin_group.setVisible(False)
        self.tab_more_layout.addWidget(self.admin_group)

        self.tab_file_layout.addStretch()
        self.tab_sizes_layout.addStretch()
        self.tab_groups_layout.addStretch()
        self.tab_text_layout.addStretch()
        self.tab_more_layout.addStretch()
        control_panel_layout.addStretch()
        self.apply_compact_right_panel_style()
        self.apply_group_controls_visibility()
        self.update_history_buttons_state()



    def apply_compact_right_panel_style(self):
        """Компактний режим правої панелі: максимум 300 px і без горизонтального роз'їзду."""
        if hasattr(self, "scroll_area"):
            self.scroll_area.setFixedWidth(500)
            self.scroll_area.setMinimumWidth(500)
            self.scroll_area.setMaximumWidth(500)

        widgets = []
        if hasattr(self, "scroll_area") and self.scroll_area.widget():
            widgets = self.scroll_area.widget().findChildren(QWidget)

        for widget in widgets:
            if isinstance(widget, QLabel):
                widget.setWordWrap(True)
                widget.setMaximumWidth(486)
            elif isinstance(widget, QPushButton):
                widget.setMinimumHeight(24)
                widget.setMaximumHeight(30)
                widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            elif isinstance(widget, (QLineEdit, QComboBox)):
                widget.setMinimumHeight(22)
                widget.setMaximumHeight(26)
                widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            elif isinstance(widget, QListWidget):
                widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        for group in self.findChildren(QGroupBox):
            group.setMaximumWidth(486)

        self.setStyleSheet(self.styleSheet() + """
        QScrollArea { border: 0px; }
        QTabWidget::pane { border: 1px solid #444; padding: 2px; }
        QTabBar::tab { padding: 3px 5px; min-width: 42px; font-size: 10px; }
        QGroupBox {
            margin-top: 8px;
            padding-top: 8px;
            font-size: 10px;
        }
        QLabel { font-size: 10px; }
        QPushButton {
            font-size: 10px;
            padding: 3px 4px;
            text-align: center;
        }
        QLineEdit, QComboBox {
            font-size: 10px;
            padding: 1px 3px;
        }
        QListWidget {
            font-size: 10px;
        }
        QCheckBox {
            font-size: 10px;
            spacing: 3px;
        }
        """)

    def setup_shortcuts(self):

        # ---------- Файл ----------
        QShortcut(QKeySequence("Ctrl+O"), self, self.open_dxf_from_dialog)
        QShortcut(QKeySequence("Ctrl+S"), self, self.save_current_dxf)

        # ---------- Історія ----------
        QShortcut(QKeySequence("Ctrl+Z"), self, self.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self, self.redo)

        # Альтернативний redo як в AutoCAD
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self.redo)

        # ---------- Виділення ----------
        QShortcut(QKeySequence("Ctrl+A"), self, self.select_all_entities)

        # Зняти виділення
        QShortcut(QKeySequence("Escape"), self, self.clear_selection)

        # ---------- Видалення ----------
        QShortcut(QKeySequence("Delete"), self, self.delete_entities_from_dxf)

        # ---------- Перегляд ----------
        QShortcut(QKeySequence("F"), self, self.zoom_extents)      # Fit All
        QShortcut(QKeySequence("Home"), self, self.zoom_extents)

        # ---------- Перетворення ----------
        QShortcut(QKeySequence("Ctrl+R"), self,
                lambda: self.transform_selected_entities("ROT90"))

        QShortcut(QKeySequence("Ctrl+Shift+R"), self,
                lambda: self.transform_selected_entities("ROT180"))

        QShortcut(QKeySequence("Ctrl+M"), self,
                lambda: self.transform_selected_entities("MIRROR_H"))

        # ---------- Групи ----------
        QShortcut(QKeySequence("Ctrl+G"), self, self.create_parametric_group)

        QShortcut(QKeySequence("Ctrl+Shift+G"), self,
                self.disband_parametric_group)

        # ---------- Перерахунок ----------
        QShortcut(QKeySequence("F5"), self,
                self.process_parametric_percentage_scale)

        QShortcut(QKeySequence("F6"), self,
                self.preview_parametric_scale)

        # ---------- Експорт ----------
        QShortcut(QKeySequence("Ctrl+E"), self,
                self.export_new_dxf_with_dimensions)

    def typical_rule_library(self):
        return {
            
            "Фіксовано": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Рухається вправо": {
                "k_w": 1.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Рухається вліво": {
                "k_w": 1.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Рухається вгору": {
                "k_w": 0.0, "k_h": 1.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Центрувати по ширині": {
                "k_w": 0.5, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Центрувати по висоті": {
                "k_w": 0.0, "k_h": 0.5,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            
            "Правий край + ріст вгору": {
                "k_w": 1.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 1.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Верхній край + ріст вправо": {
                "k_w": 0.0, "k_h": 1.0,
                "growth_p_w": 1.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },

            # "Лівий край + ріст вправо": {
            #     "k_w": 0.0, "k_h": 0.0,
            #     "growth_p_w": 1.0, "growth_p_h": 0.0,
            #     "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
            #     "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
            #     "link_x": "X = W", "link_y": "Y = H"
            # },

            # "Правий край + ріст вліво": {
            #     "k_w": 1.0, "k_h": 0.0,
            #     "growth_p_w": 1.0, "growth_p_h": 0.0,
            #     "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
            #     "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
            #     "link_x": "X = W", "link_y": "Y = H"
            # },

            # "Нижній край + ріст вгору": {
            #     "k_w": 0.0, "k_h": 0.0,
            #     "growth_p_w": 0.0, "growth_p_h": 1.0,
            #     "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
            #     "shift_dir_x": "Вправо", "shift_dir_y": "Вниз",
            #     "link_x": "X = W", "link_y": "Y = H"
            # },

            # "Верхній край + ріст вниз": {
            #     "k_w": 0.0, "k_h": 1.0,
            #     "growth_p_w": 0.0, "growth_p_h": 1.0,
            #     "growth_dir_x": "Вправо", "growth_dir_y": "Вниз",
            #     "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
            #     "link_x": "X = W", "link_y": "Y = H"
            # },

            "1/3 ширини": {
                "k_w": 0.3333, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },

            "2/3 ширини": {
                "k_w": 0.6667, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            
            "Розтягнути вправо": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 1.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },
            "Розтягнути вгору": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 1.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },

            "Розтягнути вліво": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 1.0, "growth_p_h": 0.0,
                "growth_dir_x": "Вліво", "growth_dir_y": "Вгору",
                "shift_dir_x": "Вліво", "shift_dir_y": "Вгору",
                "link_x": "X = W", "link_y": "Y = H"
            },

            "Розтягнути вниз": {
                "k_w": 0.0, "k_h": 0.0,
                "growth_p_w": 0.0, "growth_p_h": 1.0,
                "growth_dir_x": "Вправо", "growth_dir_y": "Вниз",
                "shift_dir_x": "Вправо", "shift_dir_y": "Вниз",
                "link_x": "X = W", "link_y": "Y = H"
            }
        }

    def db_rule_library(self):
        rules = {}
        if getattr(self, "db", None) and getattr(self.db, "available", False):
            for row in self.db.list_rule_templates(active_only=True):
                name = str(row.get("name") or "").strip()
                if not name:
                    continue
                rules[name] = {
                    "k_w": row.get("k_w", 0.0),
                    "k_h": row.get("k_h", 0.0),
                    "growth_p_w": row.get("growth_p_w", 0.0),
                    "growth_p_h": row.get("growth_p_h", 0.0),
                    "growth_dir_x": row.get("growth_dir_x", "Центр"),
                    "growth_dir_y": row.get("growth_dir_y", "Центр"),
                    "shift_dir_x": row.get("shift_dir_x", "Вправо"),
                    "shift_dir_y": row.get("shift_dir_y", "Вгору"),
                    "link_x": row.get("link_x", "X = W"),
                    "link_y": row.get("link_y", "Y = H"),
                }
        return rules

    def rule_library(self):
        rules = dict(self.typical_rule_library())
        for name, rule in self.db_rule_library().items():
            key = name if name not in rules else f"БД: {name}"
            rules[key] = rule
        return rules

    def refresh_rule_library_combo(self):
        if not hasattr(self, "combo_rule_library"):
            return
        current = self.combo_rule_library.currentText()
        self.combo_rule_library.blockSignals(True)
        self.combo_rule_library.clear()
        self.combo_rule_library.addItems(list(self.rule_library().keys()))
        if current:
            idx = self.combo_rule_library.findText(current)
            if idx >= 0:
                self.combo_rule_library.setCurrentIndex(idx)
        self.combo_rule_library.blockSignals(False)

    def group_name_suggestions(self):
        names = []
        if getattr(self, "db", None) and getattr(self.db, "available", False):
            names.extend(self.db.list_group_name_suggestions())
        names.extend(["Полотно", "Бокова стійка", "Перемичка", "Підсилювач", "Поріг"])
        result = []
        seen = set()
        for name in names:
            text = str(name or "").strip()
            key = text.lower()
            if text and key not in seen:
                seen.add(key)
                result.append(text)
        return result

    def ask_group_name(self):
        suggestions = self.group_name_suggestions()
        if suggestions:
            name, ok = QInputDialog.getItem(
                self,
                "Нова група",
                "Виберіть або введіть назву групи:",
                suggestions,
                0,
                True,
            )
        else:
            name, ok = QInputDialog.getText(self, "Нова група", "Введіть назву групи:")
        if not ok or not str(name).strip():
            return f"Група {len(self.parametric_groups) + 1}"
        return str(name).strip()

    def apply_rule_to_group(self, group, rule_name):
        rule = self.rule_library().get(rule_name)
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
        """
        Оновлює поля розмірів тільки з project_meta.
        project_meta наповнюється з MSSQL, не з JSON/_folder_params.
        """
        source_w = self.project_meta.get("source_width")
        source_h = self.project_meta.get("source_height")

        if source_w is None or source_h is None:
            source_w, source_h = self.get_dxf_bounds_dimensions()
            self.project_meta["source_width"] = source_w
            self.project_meta["source_height"] = source_h

        target_w = self.project_meta.get("target_width") or source_w
        target_h = self.project_meta.get("target_height") or source_h

        self.project_meta["target_width"] = target_w
        self.project_meta["target_height"] = target_h

        self.input_current_width.setText(self.format_dimension_value(source_w))
        self.input_current_height.setText(self.format_dimension_value(source_h))
        self.input_target_width.setText(self.format_dimension_value(target_w))
        self.input_target_height.setText(self.format_dimension_value(target_h))

        self.sync_text_inputs_from_meta()
        self.sync_opening_inputs_from_meta()
        self.sync_file_growth_axis_combo()
        self.update_file_status_panel()

    def update_file_status_panel(self):
        if not hasattr(self, "lbl_file_status_source"):
            return
        source_w = self.format_dimension_value(self.project_meta.get("source_width"))
        source_h = self.format_dimension_value(self.project_meta.get("source_height"))
        target_w = self.format_dimension_value(self.project_meta.get("target_width"))
        target_h = self.format_dimension_value(self.project_meta.get("target_height"))
        source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
        target_opening = self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)
        opening_names = {"left": "Ліве", "right": "Праве"}
        link_x, link_y = self.link_pair_for_mode() if hasattr(self, "link_pair_for_mode") else ("X = W", "Y = H")
        db_state = "online" if getattr(getattr(self, "db", None), "available", False) else "offline"
        user = self.current_user.get("username") if getattr(self, "current_user", None) else "-"
        self.lbl_file_status_source.setText(f"Початковий: {source_w} x {source_h}")
        self.lbl_file_status_target.setText(f"Цільовий: {target_w} x {target_h}")
        self.lbl_file_status_opening.setText(
            f"Відкривання: {opening_names.get(source_opening, source_opening)} -> {opening_names.get(target_opening, target_opening)}"
        )
        self.lbl_file_status_axis.setText(f"Осі: {link_x}, {link_y}")
        model_id = getattr(self, "current_door_model_id", None) or "-"
        file_id = getattr(self, "current_project_file_id", None) or "-"
        self.lbl_file_status_db.setText(f"БД: {db_state} | користувач: {user} | модель: {model_id} | файл: {file_id}")


    def prompt_source_dimensions_on_open(self):
        """
        Початкові розміри і відкривання беруться з DoorModels.

        Якщо DoorModel для папки вже є в БД — нічого не питаємо.
        Якщо в БД ще немає початкових розмірів — питаємо один раз і записуємо в DoorModels.
        JSON тут не використовується.
        """
        if getattr(self, "db", None) and getattr(self.db, "available", False):
            if not getattr(self, "current_door_model_id", None):
                model_id = self.db.find_door_model_by_folder(self.project_dir)
                if model_id:
                    self.current_door_model_id = model_id

            if getattr(self, "current_door_model_id", None):
                model_data = self.db.load_door_model(self.current_door_model_id)
                if model_data:
                    meta = model_data.get("meta") or {}
                    source_w = meta.get("source_width")
                    source_h = meta.get("source_height")

                    if source_w is not None and source_h is not None:
                        opening = meta.get("source_door_opening") or "left"

                        self.project_meta["source_width"] = source_w
                        self.project_meta["source_height"] = source_h
                        self.project_meta["target_width"] = self.project_meta.get("target_width") or source_w
                        self.project_meta["target_height"] = self.project_meta.get("target_height") or source_h
                        self.project_meta["source_door_opening"] = opening
                        self.project_meta["target_door_opening"] = self.project_meta.get("target_door_opening") or opening
                        self.project_meta["door_opening"] = self.project_meta.get("door_opening") or opening
                        # Осі файлу не беремо з DoorModels.
                        # AxisLinkMode / LinkX / LinkY / GrowthAxis належать конкретному ProjectFile.
                        # Тут підтягуємо тільки спільні дані папки: W/H/відкривання.

                        self.update_dimension_inputs_from_meta()
                        return False

        guessed_w, guessed_h = self.get_dxf_bounds_dimensions()
        source_w = self.project_meta.get("source_width") or guessed_w
        source_h = self.project_meta.get("source_height") or guessed_h

        default_text = ""
        if source_w is not None and source_h is not None:
            default_text = f"{self.format_dimension_value(source_w)} x {self.format_dimension_value(source_h)}"

        text, ok = QInputDialog.getText(
            self,
            "Початковий розмір моделі",
            "Введіть початкову ширину і висоту для всієї папки (W x H):",
            text=default_text
        )
        if not ok:
            return False

        values = [
            float(value.replace(",", "."))
            for value in re.findall(r"-?\d+(?:[,.]\d+)?", text)
        ]

        if len(values) < 2:
            QMessageBox.warning(
                self,
                "Початковий розмір",
                "Введіть два числа, наприклад: 860 x 2040"
            )
            return False

        source_w, source_h = values[0], values[1]

        opening_text, opening_ok = QInputDialog.getItem(
            self,
            "Початкове відкривання",
            "Яке відкривання у файлах цієї папки?",
            ["Ліве", "Праве"],
            0,
            False
        )

        opening = "right" if opening_ok and "Прав" in opening_text else "left"

        self.project_meta["source_width"] = source_w
        self.project_meta["source_height"] = source_h
        self.project_meta["target_width"] = source_w
        self.project_meta["target_height"] = source_h
        self.project_meta["source_door_opening"] = opening
        self.project_meta["target_door_opening"] = opening
        self.project_meta["door_opening"] = opening

        if getattr(self, "db", None) and getattr(self.db, "available", False) and self.current_user_id():
            door_model_id = self.db.get_or_create_door_model(
                folder_path=self.project_dir,
                model_name=os.path.basename(self.project_dir),
                source_width=source_w,
                source_height=source_h,
                source_door_opening=opening,
                user_id=self.current_user_id(),
                growth_axis=self.project_meta.get("growth_axis", "both"),
                axis_link_mode=self.project_meta.get("axis_link_mode", "normal"),
                link_x=self.project_meta.get("link_x", "X = W"),
                link_y=self.project_meta.get("link_y", "Y = H"),
            )

            if door_model_id:
                self.current_door_model_id = door_model_id
                self.register_current_folder_model(show_errors=False)

        self.update_dimension_inputs_from_meta()
        self.save_project_config()
        return True


    def remember_source_dimensions(self):
        source_w = self.parse_numeric_text(self.input_current_width.text())
        source_h = self.parse_numeric_text(self.input_current_height.text())

        if source_w is None or source_h is None:
            source_w, source_h = self.get_dxf_bounds_dimensions()

        self.project_meta["source_width"] = source_w
        self.project_meta["source_height"] = source_h

        target_w = self.parse_numeric_text(self.input_target_width.text())
        target_h = self.parse_numeric_text(self.input_target_height.text())
        self.project_meta["target_width"] = target_w if target_w is not None else source_w
        self.project_meta["target_height"] = target_h if target_h is not None else source_h

        if getattr(self, "db", None) and getattr(self.db, "available", False) and self.current_user_id():
            if not getattr(self, "current_door_model_id", None):
                self.current_door_model_id = self.db.get_or_create_door_model(
                    folder_path=self.project_dir,
                    model_name=os.path.basename(self.project_dir),
                    source_width=source_w,
                    source_height=source_h,
                    source_door_opening=self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening") or "left",
                    user_id=self.current_user_id(),
                    growth_axis=self.project_meta.get("growth_axis", "both"),
                    axis_link_mode=self.project_meta.get("axis_link_mode", "normal"),
                    link_x=self.project_meta.get("link_x", "X = W"),
                    link_y=self.project_meta.get("link_y", "Y = H"),
                )

            if getattr(self, "current_door_model_id", None):
                self.db.update_door_model_from_meta(
                    self.current_door_model_id,
                    self.project_meta,
                    self.current_user_id(),
                )

        self.save_project_config()
        self.update_dimension_inputs_from_meta()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Початкові розміри збережено в БД.</font>")

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

    def set_text_panel_expanded(self, expanded):
        layout = getattr(self, "text_box_layout", None)
        if not layout:
            return
        for index in range(layout.count()):
            item = layout.itemAt(index)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.setVisible(expanded)
            elif child_layout:
                for child_index in range(child_layout.count()):
                    child_item = child_layout.itemAt(child_index)
                    child_widget = child_item.widget()
                    if child_widget:
                        child_widget.setVisible(expanded)

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
        if hasattr(self, "text_group"):
            should_open = bool(
                settings.get("enabled") or
                str(settings.get("text", "")).strip() or
                settings.get("handle")
            )
            self.text_group.setChecked(should_open)
            self.set_text_panel_expanded(should_open)

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
        self.save_current_dxf()
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
        self.save_current_dxf()
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
        self.save_current_dxf()
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
        self.save_current_dxf()
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
            self.save_current_dxf()
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
        self.save_current_dxf()
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

    def sync_opening_inputs_from_meta(self):
        if not hasattr(self, "combo_door_opening"):
            return
        source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
        target_opening = self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)
        if hasattr(self, "combo_source_door_opening"):
            self.combo_source_door_opening.blockSignals(True)
            self.combo_source_door_opening.setCurrentText("Праве" if source_opening == "right" else "Ліве")
            self.combo_source_door_opening.blockSignals(False)
        self.combo_door_opening.blockSignals(True)
        self.combo_door_opening.setCurrentText("Праве" if target_opening == "right" else "Ліве")
        self.combo_door_opening.blockSignals(False)


    def on_source_door_opening_changed(self, text):
        self.record_action_snapshot()
        self.project_meta["source_door_opening"] = "right" if "Прав" in text else "left"
        if not self.project_meta.get("target_door_opening"):
            self.project_meta["target_door_opening"] = self.project_meta["source_door_opening"]
        self.save_project_config()
        self.update_file_status_panel()

    def on_door_opening_changed(self, text):
        self.record_action_snapshot()
        self.project_meta["target_door_opening"] = "right" if "Прав" in text else "left"
        self.project_meta["door_opening"] = self.project_meta["target_door_opening"]
        self.save_project_config()
        self.update_file_status_panel()

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
        if tp in ("TEXT", "MTEXT"):
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


    def flip_x_direction(self, direction):
        if direction == "Вправо":
            return "Вліво"
        if direction == "Вліво":
            return "Вправо"
        return direction
    
    def flip_y_direction(self, direction):
        if direction == "Вгору":
            return "Вниз"
        if direction == "Вниз":
            return "Вгору"
        return direction

    def mirror_door_opening(self):
        min_x, min_y, max_x, max_y = self.get_dxf_bounds()
        if min_x is None:
            return

        self.record_action_snapshot()

        link_x, link_y = self.link_pair_for_mode()
        mirror_by_y = link_y == "Y = W"

        axis_x = (min_x + max_x) * 0.5
        axis_y = (min_y + max_y) * 0.5

        for entity in self.doc.modelspace():
            tp = entity.dxftype()

            if tp == "LINE":
                sx, sy, sz = entity.dxf.start
                ex, ey, ez = entity.dxf.end

                if mirror_by_y:
                    entity.dxf.start = (sx, 2 * axis_y - sy, sz)
                    entity.dxf.end = (ex, 2 * axis_y - ey, ez)
                else:
                    entity.dxf.start = (2 * axis_x - sx, sy, sz)
                    entity.dxf.end = (2 * axis_x - ex, ey, ez)

            elif tp in ("CIRCLE", "ARC"):
                cx, cy, cz = entity.dxf.center

                if mirror_by_y:
                    entity.dxf.center = (cx, 2 * axis_y - cy, cz)

                    if tp == "ARC":
                        old_start = float(entity.dxf.start_angle)
                        old_end = float(entity.dxf.end_angle)
                        entity.dxf.start_angle = (-old_end) % 360.0
                        entity.dxf.end_angle = (-old_start) % 360.0

                else:
                    entity.dxf.center = (2 * axis_x - cx, cy, cz)

                    if tp == "ARC":
                        old_start = float(entity.dxf.start_angle)
                        old_end = float(entity.dxf.end_angle)
                        entity.dxf.start_angle = (180.0 - old_end) % 360.0
                        entity.dxf.end_angle = (180.0 - old_start) % 360.0

            elif tp == "TEXT":
                x, y, z = entity.dxf.insert

                if mirror_by_y:
                    entity.dxf.insert = (x, 2 * axis_y - y, z)
                else:
                    entity.dxf.insert = (2 * axis_x - x, y, z)

                entity.dxf.rotation = float(getattr(entity.dxf, "rotation", 0.0))

        settings = self.get_text_settings()

        if mirror_by_y:
            settings["y"] = 2 * axis_y - float(settings.get("y", 0.0))
        else:
            settings["x"] = 2 * axis_x - (
                float(settings.get("x", 0.0)) + self.text_box_width(settings)
            )

        self.project_meta["door_text"] = settings
        self.apply_door_text_to_doc()

        for group in self.parametric_groups:
            if mirror_by_y:
                group["growth_dir_y"] = self.flip_y_direction(
                    group.get("growth_dir_y", "Вгору")
                )
                group["shift_dir_y"] = self.flip_y_direction(
                    group.get("shift_dir_y", "Вгору")
                )
            else:
                group["growth_dir_x"] = self.flip_x_direction(
                    group.get("growth_dir_x", "Вправо")
                )
                group["shift_dir_x"] = self.flip_x_direction(
                    group.get("shift_dir_x", "Вправо")
                )

        self.project_meta["door_opening"] = (
            "right" if self.project_meta.get("door_opening") != "right" else "left"
        )
        self.project_meta["target_door_opening"] = self.project_meta["door_opening"]

        self.save_current_dxf()
        self.save_original_geometries()
        self.apply_axis_link_mode_to_groups()
        self.save_project_config()
        self.sync_opening_inputs_from_meta()
        self.sync_text_inputs_from_meta()
        # self.sync_link_combos_from_file_mode()
        self.load_entities_into_list()
        self.update_viewer()
        self.update_file_status_panel()

        self.lbl_status_calc.setText(
            "<font color='#a5d6a7'>Відкривання дзеркально змінено.</font>"
        )

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

    def validate_target_size_or_warn(self, cur_w, cur_h, target_w, target_h):
        if len(self.parametric_groups) < 2:
            return True
        if not self.has_new_group_overlap(cur_w, cur_h, target_w, target_h):
            return True
        min_w = self.find_min_safe_axis(cur_w, cur_h, "width")
        min_h = self.find_min_safe_axis(cur_w, cur_h, "height")
        self.lbl_status_calc.setText(
            "<font color='red'>Заданий розмір дає накладання блоків. "
            f"Безпечний мінімум: W≈{min_w:.1f} мм, H≈{min_h:.1f} мм.</font>"
        )
        return False

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
            self.save_current_dxf()
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
        self.export_model_dxf_with_dimensions()

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
                    elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
                        opening = self.parse_door_opening_value(value)
                        if opening:
                            params[key] = opening
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
            elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
                opening = self.parse_door_opening_value(value)
                if opening:
                    params[key] = opening
            elif key in ("keep_blocks", "delete_blocks"):
                params[key] = self.split_block_names(value)
        return params

    def split_block_names(self, value):
        if value is None:
            return []
        return [part.strip() for part in re.split(r"[,;\n]+", str(value)) if part.strip()]

    def apply_imported_parameters(self, params, refresh_ui=True, save_config=True):
        for key in ("source_width", "source_height", "target_width", "target_height"):
            if key in params:
                self.project_meta[key] = params[key]
        source_opening = params.get("source_door_opening", params.get("source_opening"))
        target_opening = params.get("target_door_opening", params.get("target_opening", params.get("door_opening")))
        if source_opening:
            self.project_meta["source_door_opening"] = source_opening
        if target_opening:
            self.project_meta["target_door_opening"] = target_opening
            self.project_meta["door_opening"] = target_opening
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
        if refresh_ui:
            self.update_dimension_inputs_from_meta()
            self.sync_opening_inputs_from_meta()
            self.sync_text_inputs_from_meta()
            self.load_block_filter_list()
        if save_config:
            self.save_project_config()

    def sanitize_filename_part(self, value):
        text = self.format_dimension_value(value)
        return re.sub(r"[^0-9A-Za-zА-Яа-я_\-.]+", "_", text)

    def parse_door_opening_value(self, value):
        text = str(value or "").strip().lower()
        if not text:
            return None
        if text in ("right", "r", "prave") or "прав" in text or "right" in text:
            return "right"
        if text in ("left", "l", "live") or "лів" in text or "лев" in text or "left" in text:
            return "left"
        return None

    def get_export_output_dir(self, target_w, target_h):
        width_part = self.sanitize_filename_part(target_w)
        height_part = self.sanitize_filename_part(target_h)
        folder_name = f"generated_{width_part}_{height_part}"
        output_dir = os.path.join(self.project_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def build_export_file_name(self, target_w, target_h):
        base_name = os.path.splitext(self.current_dxf_file_name())[0]
        base_name = re.sub(r"(?<!\d)\d{3,5}_\d{3,5}(?!\d)", "", base_name).strip("_- ")
        width_part = self.sanitize_filename_part(target_w)
        height_part = self.sanitize_filename_part(target_h)
        return f"{base_name}_{width_part}_{height_part}.DXF"

    def build_export_path(self, target_w, target_h):
        name = self.build_export_file_name(target_w, target_h)
        base_name = os.path.splitext(name)[0]
        output_dir = self.get_export_output_dir(target_w, target_h)
        path = os.path.join(output_dir, name)
        counter = 2
        while os.path.exists(path):
            name = f"{base_name}_{width_part}_{height_part}_{counter}.DXF"
            path = os.path.join(output_dir, name)
            counter += 1
        return path

    def export_target_opening(self):
        source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
        return self.project_meta.get("target_door_opening") or self.project_meta.get("door_opening", source_opening)

    def export_needs_opening_mirror(self):
        source_opening = self.project_meta.get("source_door_opening") or self.project_meta.get("door_opening", "left")
        return source_opening != self.export_target_opening()

    def apply_opening_to_export_doc(self, export_doc):
        if not self.export_needs_opening_mirror():
            return
        min_x, _min_y, max_x, _max_y = self.get_dxf_bounds(export_doc)
        if min_x is None:
            return
        axis_x = (min_x + max_x) * 0.5
        for entity in export_doc.modelspace():
            self.mirror_entity_horizontally(entity, axis_x)


    def save_generated_folder_config(self, output_dir, target_w, target_h, target_opening):
        """
        _folder_params.json більше не створюємо.
        Початкові параметри моделі зберігаються в DoorModels.
        """
        return

    def save_generated_project_config(self, export_path, target_w, target_h):
        """
        JSON для згенерованого DXF більше не створюємо.
        Уся історія експорту зберігається в ProjectExports.
        """
        return

    def is_generated_dimension_dxf(self, file_name):
        base_name = os.path.splitext(file_name)[0]
        return re.search(r"_\d{2,5}_\d{2,5}(?:_\d+)?$", base_name) is not None

    def get_folder_source_dxf_files(self):
        try:
            files = os.listdir(self.project_dir)
        except Exception:
            return []
        return sorted(
            file_name for file_name in files
            if file_name.lower().endswith(".dxf")
            and not self.is_generated_dimension_dxf(file_name)
        )

    def preview_parametric_scale(self):
        self.record_action_snapshot()
        if self.debug_output:
            print("\n" + "=" * 90)
            print("[PREVIEW DEBUG] START PREVIEW")
            print("[PREVIEW DEBUG] Перегляд рахує не від файлу на диску, а від self.original_geometries")
            print(f"[PREVIEW DEBUG] base handles={len(self.original_geometries)}")
            print(f"[PREVIEW DEBUG] source W/H={self.project_meta.get('source_width')} / {self.project_meta.get('source_height')}")
            print(f"[PREVIEW DEBUG] target W/H={self.input_target_width.text()} / {self.input_target_height.text()}")
            print("=" * 90)
        if self.process_parametric_percentage_scale(save_result=False, record_history=False):
            self.lbl_status_calc.setText("<font color='#4fc3f7'>Перегляд застосовано тільки на екрані. Файл ще не збережено.</font>")

    def ask_model_export_options(self, target_w, target_h):
        dialog = QDialog(self)
        dialog.setWindowTitle("Створити комплект моделі")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(
            f"Новий розмір: {self.format_dimension_value(target_w)} x {self.format_dimension_value(target_h)}"
        ))
        check_db = QCheckBox("Створити записи в БД")
        check_db.setChecked(bool(getattr(self, "db", None) and getattr(self.db, "available", False)))
        check_download = QCheckBox("Вивантажити папку на комп'ютер")
        check_download.setChecked(False)
        layout.addWidget(check_db)
        layout.addWidget(check_download)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        if not check_db.isChecked() and not check_download.isChecked():
            QMessageBox.information(self, "Комплект моделі", "Виберіть хоча б один варіант: БД або папка на комп'ютері.")
            return None
        return {
            "save_to_db": check_db.isChecked(),
            "download": check_download.isChecked(),
        }

    def make_download_output_dir(self, target_w, target_h):
        parent = QFileDialog.getExistingDirectory(
            self,
            "Куди вивантажити папку з моделлю?",
            self.project_dir if not self.is_db_uri(getattr(self, "project_dir", "")) else os.getcwd(),
        )
        if not parent:
            return None
        model_name = "model"
        if getattr(self, "current_door_model_id", None) and getattr(self, "db", None):
            model = self.db.load_door_model(self.current_door_model_id)
            if model:
                model_name = model.get("model_name") or model_name
        elif not self.is_db_uri(getattr(self, "project_dir", "")):
            model_name = os.path.basename(self.project_dir) or model_name
        safe_model = re.sub(r"[^0-9A-Za-zА-Яа-я_\-.]+", "_", str(model_name)).strip("_") or "model"
        folder_name = f"{safe_model}_{self.sanitize_filename_part(target_w)}_{self.sanitize_filename_part(target_h)}"
        output_dir = os.path.join(parent, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def export_doc_to_path(self, export_doc, output_dir, export_name):
        path = os.path.join(output_dir, export_name)
        base, ext = os.path.splitext(export_name)
        counter = 2
        while os.path.exists(path):
            path = os.path.join(output_dir, f"{base}_{counter}{ext or '.DXF'}")
            counter += 1
        export_doc.saveas(path)
        return path

    def db_model_source_records(self):
        model_id = getattr(self, "current_door_model_id", None) or getattr(self, "selected_db_model_id", None)
        if not model_id or not getattr(self, "db", None):
            return []
        return [
            record for record in self.db.get_model_files(model_id)
            if str(record.get("file_name") or "").lower().endswith(".dxf")
        ]

    def restore_current_dxf_from_disk(self):
        if self.is_db_file_open():
            data = self.db.get_project_file_binary(self.current_project_file_id)
            if not data:
                return
            self.record_action_snapshot()
            self.doc = self.read_dxf_doc_from_bytes(data)
            self.save_original_geometries()
            self.update_dimension_inputs_from_meta()
            self.update_viewer()
            self.load_entities_into_list()
            self.lbl_status_calc.setText("<font color='#a5d6a7'>Повернуто стан з DXF у БД.</font>")
            return
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
        original_dxf_path = self.dxf_path
        original_bytes = None
        original_doc = copy.deepcopy(self.doc) if self.is_db_file_open() else None
        if not self.is_db_file_open() and os.path.exists(self.dxf_path):
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
        self.suppress_project_config_save = True
        try:
            ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
        finally:
            self.suppress_project_config_save = False
            self.is_loading_history = False
        if not ok_to_export:
            if original_doc is not None:
                self.doc = original_doc
                self.save_current_dxf()
                self.save_original_geometries()
            if original_bytes is not None:
                with open(self.dxf_path, "wb") as f:
                    f.write(original_bytes)
                self.doc = ezdxf.readfile(self.dxf_path)
                self.save_original_geometries()
            self.project_meta = original_meta
            self.parametric_groups = original_groups
            self.block_keep_state = original_keep_state
            self.update_dimension_inputs_from_meta()
            self.load_groups_into_list()
            self.load_entities_into_list()
            self.update_viewer()
            return

        target_w = self.project_meta.get("target_width")
        target_h = self.project_meta.get("target_height")

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

        self.apply_opening_to_export_doc(export_doc)
        if self.is_db_file_open():
            export_name = self.build_export_file_name(target_w, target_h)
            self.save_export_doc_to_db(export_doc, export_name)
        else:
            export_path = self.build_export_path(target_w, target_h)
            export_doc.saveas(export_path)
            self.save_generated_project_config(export_path, target_w, target_h)
            self.save_export_to_db(export_path)
        if original_bytes is not None:
            with open(self.dxf_path, "wb") as f:
                f.write(original_bytes)
            self.doc = ezdxf.readfile(self.dxf_path)
        elif original_doc is not None:
            self.doc = original_doc
            self.save_current_dxf()
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
        created_name = export_name if self.is_db_file_open() else os.path.basename(export_path)
        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Створено: {created_name}</font>")

    def export_model_dxf_with_dimensions(self):
        """Export all source DXF files from the current folder/model with the same target size."""
        self.collect_text_settings_from_inputs()

        target_w = self.parse_numeric_text(self.input_target_width.text())
        target_h = self.parse_numeric_text(self.input_target_height.text())
        source_w = self.parse_numeric_text(self.input_current_width.text())
        source_h = self.parse_numeric_text(self.input_current_height.text())
        if target_w is None or target_h is None or source_w is None or source_h is None:
            self.lbl_status_calc.setText("<font color='red'>Вкажіть початкові та цільові W/H.</font>")
            return

        options = self.ask_model_export_options(target_w, target_h)
        if not options:
            return

        download_dir = None
        if options["download"]:
            download_dir = self.make_download_output_dir(target_w, target_h)
            if not download_dir:
                return

        if options["save_to_db"] and not self.is_db_uri(getattr(self, "project_dir", "")):
            self.register_current_folder_model(show_errors=False)

        original_dxf_path = self.dxf_path
        original_project_file_id = getattr(self, "current_project_file_id", None)
        original_door_model_id = getattr(self, "current_door_model_id", None)
        original_selected_db_model_id = getattr(self, "selected_db_model_id", None)
        original_db_file_name = getattr(self, "current_db_file_name", None)
        original_doc = copy.deepcopy(self.doc)
        original_meta = copy.deepcopy(self.project_meta)
        original_groups = copy.deepcopy(self.parametric_groups)
        original_keep_state = copy.deepcopy(self.block_keep_state)

        db_records = self.db_model_source_records() if self.is_db_uri(getattr(self, "project_dir", "")) else []
        source_entries = []
        if db_records:
            for record in db_records:
                source_entries.append({"type": "db", "record": record})
        else:
            source_files = self.get_folder_source_dxf_files()
            if not source_files:
                source_files = [os.path.basename(self.dxf_path)]
            for source_file in source_files:
                source_path = os.path.join(self.project_dir, source_file)
                if os.path.exists(source_path):
                    source_entries.append({"type": "local", "file_name": source_file, "path": source_path})

        if not source_entries:
            self.lbl_status_calc.setText("<font color='red'>Немає DXF-файлів для створення комплекту.</font>")
            return

        created = []
        skipped = 0
        try:
            for entry in source_entries:
                if entry["type"] == "db":
                    record = entry["record"]
                    project_file_id = int(record.get("id"))
                    data = self.db.get_project_file_binary(project_file_id)
                    if not data:
                        skipped += 1
                        continue
                    file_name = record.get("file_name") or f"project_file_{project_file_id}.dxf"
                    if not file_name.lower().endswith(".dxf"):
                        file_name = f"{file_name}.dxf"
                    self.current_project_file_id = project_file_id
                    self.current_door_model_id = record.get("door_model_id") or original_door_model_id
                    self.selected_db_model_id = self.current_door_model_id
                    self.current_db_file_name = file_name
                    self.project_dir = f"db://door_model/{self.current_door_model_id or 'unknown'}"
                    self.dxf_path = f"db://project_file/{project_file_id}/{file_name}"
                    self.doc = self.read_dxf_doc_from_bytes(data)
                    loaded = self.db.load_project_config(project_file_id=project_file_id)
                    if loaded:
                        self.apply_loaded_project_config(loaded)
                    else:
                        self.load_project_config()
                else:
                    source_path = entry["path"]
                    self.dxf_path = source_path
                    self.current_db_file_name = None
                    self.current_project_file_id = None
                    self.current_door_model_id = original_door_model_id
                    self.doc = ezdxf.readfile(self.dxf_path)
                    self.load_project_config()

                self.save_original_geometries()

                self.project_meta["source_width"] = source_w
                self.project_meta["source_height"] = source_h
                self.project_meta["target_width"] = target_w
                self.project_meta["target_height"] = target_h

                self.is_loading_history = True
                self.suppress_project_config_save = True
                try:
                    ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
                finally:
                    self.suppress_project_config_save = False
                    self.is_loading_history = False

                if not ok_to_export:
                    skipped += 1
                    continue

                export_doc = copy.deepcopy(self.doc)
                export_msp = export_doc.modelspace()
                for hndl in self.get_export_delete_handles():
                    if hndl in export_doc.entitydb:
                        export_msp.delete_entity(export_doc.entitydb[hndl])

                self.apply_opening_to_export_doc(export_doc)
                export_name = self.build_export_file_name(target_w, target_h)
                outputs = []
                if options["save_to_db"]:
                    if self.save_export_doc_to_db(export_doc, export_name):
                        outputs.append("БД")
                if download_dir:
                    saved_path = self.export_doc_to_path(export_doc, download_dir, export_name)
                    outputs.append(os.path.basename(saved_path))
                created.append(f"{export_name} ({', '.join(outputs)})" if outputs else export_name)

            self.dxf_path = original_dxf_path
            self.current_project_file_id = original_project_file_id
            self.current_door_model_id = original_door_model_id
            self.selected_db_model_id = original_selected_db_model_id
            self.current_db_file_name = original_db_file_name
            self.doc = original_doc
            self.project_meta = original_meta
            self.parametric_groups = original_groups
            self.block_keep_state = original_keep_state
            self.save_original_geometries()
            if getattr(self, "current_user", None):
                self.save_project_config()
            self.scan_project_folder_for_dxf()
            self.update_dimension_inputs_from_meta()
            self.load_groups_into_list()
            self.load_entities_into_list()
            self.update_viewer()
            where = []
            if options["save_to_db"]:
                where.append("БД")
            if download_dir:
                where.append(download_dir)
            suffix = f" → {' + '.join(where)}" if where else ""
            if skipped:
                self.lbl_status_calc.setText(f"<font color='#ff9800'>Комплект створено: {len(created)} DXF{suffix}, пропущено: {skipped}</font>")
            else:
                self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Комплект створено: {len(created)} DXF{suffix}</font>")
        except Exception as e:
            self.dxf_path = original_dxf_path
            self.current_project_file_id = original_project_file_id
            self.current_door_model_id = original_door_model_id
            self.selected_db_model_id = original_selected_db_model_id
            self.current_db_file_name = original_db_file_name
            self.doc = original_doc
            self.project_meta = original_meta
            self.parametric_groups = original_groups
            self.block_keep_state = original_keep_state
            self.save_original_geometries()
            self.lbl_status_calc.setText(f"<font color='red'>Помилка експорту комплекту: {e}</font>")

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

        original_dxf_path = self.dxf_path
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
            source_files = self.get_folder_source_dxf_files()
            if not source_files:
                source_files = [os.path.basename(self.dxf_path)]
            created = []
            skipped = 0
            for job in jobs:
                for source_file in source_files:
                    source_path = os.path.join(self.project_dir, source_file)
                    if not os.path.exists(source_path):
                        continue
                    with open(source_path, "rb") as f:
                        source_bytes = f.read()

                    self.dxf_path = source_path
                    self.current_project_file_id = None
                    self.doc = ezdxf.readfile(self.dxf_path)
                    self.load_project_config()
                    self.save_original_geometries()
                    self.apply_imported_parameters(job, refresh_ui=False, save_config=False)
                    self.is_loading_history = True
                    self.suppress_project_config_save = True
                    try:
                        ok_to_export = self.process_parametric_percentage_scale(save_result=True, record_history=False)
                    finally:
                        self.suppress_project_config_save = False
                        self.is_loading_history = False
                    if not ok_to_export:
                        skipped += 1
                        with open(source_path, "wb") as f:
                            f.write(source_bytes)
                        self.doc = ezdxf.readfile(self.dxf_path)
                        self.save_original_geometries()
                        continue

                    target_w = self.project_meta.get("target_width")
                    target_h = self.project_meta.get("target_height")
                    export_path = self.build_export_path(target_w, target_h)
                    export_doc = copy.deepcopy(self.doc)
                    export_msp = export_doc.modelspace()
                    delete_handles = self.get_export_delete_handles()
                    for hndl in delete_handles:
                        if hndl in export_doc.entitydb:
                            export_msp.delete_entity(export_doc.entitydb[hndl])
                    self.apply_opening_to_export_doc(export_doc)
                    export_doc.saveas(export_path)
                    self.save_generated_project_config(export_path, target_w, target_h)
                    self.save_export_to_db(export_path)
                    created.append(os.path.basename(export_path))

                    with open(source_path, "wb") as f:
                        f.write(source_bytes)
                    self.doc = ezdxf.readfile(self.dxf_path)
                    self.save_original_geometries()

            self.dxf_path = original_dxf_path
            if os.path.exists(self.dxf_path):
                self.doc = ezdxf.readfile(self.dxf_path)
            self.project_meta = original_meta
            self.parametric_groups = original_groups
            self.block_keep_state = original_keep_state
            self.save_project_config()
            self.scan_project_folder_for_dxf()
            self.update_dimension_inputs_from_meta()
            self.load_groups_into_list()
            self.load_entities_into_list()
            self.update_viewer()
            if skipped:
                self.lbl_status_calc.setText(
                    f"<font color='#ff9800'>Пакет створено: {len(created)} DXF, пропущено через накладання: {skipped}</font>"
                )
            else:
                self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Пакет створено: {len(created)} DXF</font>")
        except Exception as e:
            self.lbl_status_calc.setText(f"<font color='red'>Помилка пакета: {e}</font>")
            self.dxf_path = original_dxf_path
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
                elif key in ("door_opening", "source_opening", "target_opening", "source_door_opening", "target_door_opening"):
                    opening = self.parse_door_opening_value(value)
                    if opening:
                        params[key] = opening
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

    def normalize_key(self, value):
        return table_io.normalize_key(value)

    def read_csv_rows(self, path):
        return table_io.read_csv_rows(path)

    def read_xlsx_rows(self, path):
        return table_io.read_xlsx_rows(path)

    def extract_table_parameters(self, rows):
        return table_io.extract_table_parameters(rows, self.parse_numeric_text)

    def split_block_names(self, value):
        return table_io.split_block_names(value)

    def parse_door_opening_value(self, value):
        return table_io.parse_door_opening_value(value)

    def extract_batch_jobs(self, rows):
        return table_io.extract_batch_jobs(rows, self.parse_numeric_text)

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

        if not file_path:
            return

        old_project_dir = getattr(self, "project_dir", None)
        old_dxf_path = getattr(self, "dxf_path", None)
        old_doc = getattr(self, "doc", None)
        old_project_file_id = getattr(self, "current_project_file_id", None)
        old_door_model_id = getattr(self, "current_door_model_id", None)
        old_selected = set(getattr(self, "selected_handles", set()))
        old_groups = copy.deepcopy(getattr(self, "parametric_groups", []))
        old_block_keep_state = dict(getattr(self, "block_keep_state", {}))
        old_project_meta = copy.deepcopy(getattr(self, "project_meta", {}))

        try:
            new_dxf_path = os.path.abspath(file_path)
            new_project_dir = os.path.dirname(new_dxf_path)

            if not os.path.exists(new_dxf_path):
                raise FileNotFoundError(new_dxf_path)

            new_doc = ezdxf.readfile(new_dxf_path)

            folder_changed = (
                old_project_dir is not None
                and os.path.abspath(old_project_dir) != os.path.abspath(new_project_dir)
            )

            self.project_dir = new_project_dir
            self.dxf_path = new_dxf_path
            self.doc = new_doc

            self.selected_handles.clear()
            self.parametric_groups.clear()
            self.block_keep_state.clear()

            self.current_project_file_id = None
            self.current_db_file_name = None
            if folder_changed:
                self.current_door_model_id = None

            self.zones_undo_stack.clear()
            self.zones_redo_stack.clear()
            self.global_recalc_undo_stack.clear()
            self.global_recalc_redo_stack.clear()

            self.load_project_config()
            self.prompt_source_dimensions_on_open()
            self.register_current_folder_model(show_errors=False)
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

        except Exception as exc:
            self.project_dir = old_project_dir
            self.dxf_path = old_dxf_path
            self.doc = old_doc
            self.current_project_file_id = old_project_file_id
            self.current_door_model_id = old_door_model_id
            self.selected_handles = old_selected
            self.parametric_groups = old_groups
            self.block_keep_state = old_block_keep_state
            self.project_meta = old_project_meta

            QMessageBox.warning(
                self,
                "Відкриття DXF",
                f"Помилка при відкритті файлу:\n{exc}"
            )

    def apply_loaded_project_config(self, loaded):
        if not loaded:
            return
        self.current_project_file_id = loaded.get("project_file_id")
        self.current_door_model_id = loaded.get("door_model_id")
        self.project_meta = self.default_project_meta()
        self.project_meta.update(loaded.get("meta") or {})
        text_settings = self.default_text_settings()
        text_settings.update(self.project_meta.get("door_text", {}))
        self.project_meta["door_text"] = text_settings
        self.parametric_groups = loaded.get("groups") or []
        for group in self.parametric_groups:
            group["handles"] = set(group.get("handles", []))
            self.ensure_topology_fields(group)
            self.apply_growth_axis_to_group(group)
        self.block_keep_state = loaded.get("block_keep_state") or {}

    def open_dxf_from_db_picker(self):
        if not self.db_opening_enabled():
            error = getattr(self.db, "last_error", "") if getattr(self, "db", None) else ""
            QMessageBox.warning(self, "DB", f"БД недоступна.{chr(10) + error if error else ''}")
            return

        models = self.db.list_door_models()
        if not models:
            error = getattr(self.db, "last_error", "")
            QMessageBox.information(self, "DB", f"У БД немає моделей дверей.{chr(10) + error if error else ''}")
            return

        labels = []
        by_label = {}
        for model in models:
            model_name = model.get("model_name") or f"Model {model.get('id')}"
            width = model.get("source_width")
            height = model.get("source_height")
            size_text = ""
            if width is not None and height is not None:
                size_text = f" | {self.format_dimension_value(width)}x{self.format_dimension_value(height)}"
            label = f"{model.get('id')} | {model_name}{size_text} | файлів: {model.get('file_count', 0)}"
            labels.append(label)
            by_label[label] = model

        label, ok = QInputDialog.getItem(
            self,
            "Відкрити з БД",
            "Виберіть модель / папку:",
            labels,
            0,
            False,
        )
        if ok and label:
            self.open_db_model_folder(by_label[label])
        return

        records = self.db.list_project_files()
        if not records:
            error = getattr(self.db, "last_error", "")
            QMessageBox.information(self, "DB", f"У БД немає завантажених DXF.{chr(10) + error if error else ''}")
            return

        labels = []
        by_label = {}
        for record in records:
            file_name = record.get("file_name") or f"DB file {record.get('id')}"
            status = record.get("status") or ""
            data_mark = "data" if record.get("has_file_data", True) else "no data"
            label = f"{record.get('id')} | {file_name} | {status} | {data_mark}"
            labels.append(label)
            by_label[label] = record

        label, ok = QInputDialog.getItem(
            self,
            "Відкрити з БД",
            "Виберіть DXF:",
            labels,
            0,
            False,
        )
        if ok and label:
            self.open_dxf_from_db_record(by_label[label])

    def open_db_model_folder(self, model):
        self.selected_db_model_id = model.get("id")
        self.current_door_model_id = model.get("id")
        self.current_project_file_id = None
        self.scan_project_folder_for_dxf()
        if hasattr(self, "lbl_status_calc"):
            model_name = model.get("model_name") or f"Model {model.get('id')}"
            self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Відкрито папку моделі з БД: {model_name}</font>")

    def open_dxf_from_db_record(self, record):
        old_state = {
            "project_dir": getattr(self, "project_dir", None),
            "dxf_path": getattr(self, "dxf_path", None),
            "doc": getattr(self, "doc", None),
            "project_file_id": getattr(self, "current_project_file_id", None),
            "door_model_id": getattr(self, "current_door_model_id", None),
            "selected_db_model_id": getattr(self, "selected_db_model_id", None),
            "db_file_name": getattr(self, "current_db_file_name", None),
            "selected": set(getattr(self, "selected_handles", set())),
            "groups": copy.deepcopy(getattr(self, "parametric_groups", [])),
            "block_keep_state": dict(getattr(self, "block_keep_state", {})),
            "project_meta": copy.deepcopy(getattr(self, "project_meta", {})),
        }
        try:
            project_file_id = int(record.get("id"))
            data = self.db.get_project_file_binary(project_file_id)
            if not data:
                raise RuntimeError("У записі ProjectFiles немає FileData для DXF.")

            file_name = record.get("file_name") or f"project_file_{project_file_id}.dxf"
            if not file_name.lower().endswith(".dxf"):
                file_name = f"{file_name}.dxf"

            self.current_db_file_name = file_name
            self.project_dir = f"db://door_model/{record.get('door_model_id') or 'unknown'}"
            self.dxf_path = f"db://project_file/{project_file_id}/{file_name}"
            self.doc = self.read_dxf_doc_from_bytes(data)
            entity_count = sum(1 for _ in self.doc.modelspace())
            source_encoding = getattr(self.doc, "_parametric_source_encoding", "unknown")

            self.selected_handles.clear()
            self.parametric_groups.clear()
            self.block_keep_state.clear()
            self.zones_undo_stack.clear()
            self.zones_redo_stack.clear()
            self.global_recalc_undo_stack.clear()
            self.global_recalc_redo_stack.clear()

            loaded = self.db.load_project_config(project_file_id=project_file_id)
            if loaded:
                self.apply_loaded_project_config(loaded)
            else:
                self.current_project_file_id = project_file_id
                self.current_door_model_id = record.get("door_model_id")
                self.load_project_config()
            self.selected_db_model_id = self.current_door_model_id or record.get("door_model_id")

            self.prompt_source_dimensions_on_open()
            self.update_dimension_inputs_from_meta()
            self.history = self.make_history_manager()
            self.history.save_state()
            self.save_zones_history_state()
            self.save_original_geometries()
            self.update_viewer()
            self.load_entities_into_list()
            self.load_groups_into_list()
            self.load_block_filter_list()
            self.update_history_buttons_state()
            self.update_file_status_panel()
            if hasattr(self, "lbl_status_calc"):
                self.lbl_status_calc.setText(
                    f"<font color='#a5d6a7'>DXF відкрито з БД: {file_name}; "
                    f"bytes={len(data)}; msp={entity_count}; enc={source_encoding}</font>"
                )
            return True
        except Exception as exc:
            self.project_dir = old_state["project_dir"]
            self.dxf_path = old_state["dxf_path"]
            self.doc = old_state["doc"]
            self.current_project_file_id = old_state["project_file_id"]
            self.current_door_model_id = old_state["door_model_id"]
            self.selected_db_model_id = old_state["selected_db_model_id"]
            self.current_db_file_name = old_state["db_file_name"]
            self.selected_handles = old_state["selected"]
            self.parametric_groups = old_state["groups"]
            self.block_keep_state = old_state["block_keep_state"]
            self.project_meta = old_state["project_meta"]
            QMessageBox.warning(self, "DB", f"Не вдалося відкрити DXF з БД:\n{exc}")
            return False

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

        for group in self.parametric_groups:
            if not group["handles"].isdisjoint(self.selected_handles):
           
                old_kw = group.get("k_w", 0.0)
                old_kh = group.get("k_h", 0.0)
                old_gpw = group.get("growth_p_w", 0.0)
                old_gph = group.get("growth_p_h", 0.0)
                
                old_link_x = group.get("link_x", "X = W")
                old_link_y = group.get("link_y", "Y = H")
                
                old_dir_x = group.get("growth_dir_x", "Вправо")
                old_dir_y = group.get("growth_dir_y", "Вгору")
                old_shift_dir_x = group.get("shift_dir_x", "Вправо")
                old_shift_dir_y = group.get("shift_dir_y", "Вгору")

                if mode == "ROT90":
                    group["k_w"], group["k_h"] = old_kh, old_kw
                    group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
                    group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
                    group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
            
                    map_x_to_y = {"Вправо": "Вгору", "Вліво": "Вниз", "Центр": "Центр"}
                    map_y_to_x = {"Вгору": "Вліво", "Вниз": "Вправо", "Центр": "Центр"}
                    group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
                    group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")
                    group["shift_dir_x"] = map_y_to_x.get(old_shift_dir_y, "Вправо")
                    group["shift_dir_y"] = map_x_to_y.get(old_shift_dir_x, "Вгору")

                elif mode == "ROT270":
                    group["k_w"], group["k_h"] = old_kh, old_kw
                    group["growth_p_w"], group["growth_p_h"] = old_gph, old_gpw
                    group["link_x"] = "X = W" if "W" in old_link_y else "X = H"
                    group["link_y"] = "Y = H" if "H" in old_link_x else "Y = W"
                    
           
                    map_x_to_y = {"Вправо": "Вниз", "Вліво": "Вгору", "Центр": "Центр"}
                    map_y_to_x = {"Вгору": "Вправо", "Вниз": "Вліво", "Центр": "Центр"}
                    group["growth_dir_x"] = map_y_to_x.get(old_dir_y, "Центр")
                    group["growth_dir_y"] = map_x_to_y.get(old_dir_x, "Центр")
                    group["shift_dir_x"] = map_y_to_x.get(old_shift_dir_y, "Вправо")
                    group["shift_dir_y"] = map_x_to_y.get(old_shift_dir_x, "Вгору")

                elif mode == "ROT180":
                    map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
                    map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
                    group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
                    group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
                    group["shift_dir_x"] = map_x.get(old_shift_dir_x, "Вправо")
                    group["shift_dir_y"] = map_y.get(old_shift_dir_y, "Вгору")

                elif mode == "MIRROR_H": 
                    map_x = {"Вправо": "Вліво", "Вліво": "Вправо", "Центр": "Центр"}
                    group["growth_dir_x"] = map_x.get(old_dir_x, "Центр")
                    group["shift_dir_x"] = map_x.get(old_shift_dir_x, "Вправо")

                elif mode == "MIRROR_V": 
                    map_y = {"Вгору": "Вниз", "Вниз": "Вгору", "Центр": "Центр"}
                    group["growth_dir_y"] = map_y.get(old_dir_y, "Центр")
                    group["shift_dir_y"] = map_y.get(old_shift_dir_y, "Вгору")
                    
        self.update_growth_axis_after_transform(mode)
        self.swap_axis_link_mode_for_quarter_turn(mode)
        self.save_current_dxf()

        self.commit_current_geometry_as_parametric_base(
            reason=f"TRANSFORM {mode}",
            update_source_dimensions=False,
            preserve_target_dimensions=True,
        )

        self.save_project_config()
        self.push_to_history()
        
        self.on_group_selection_changed() 
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

        self.save_current_dxf()
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
        
        self.save_current_dxf()
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

    def guess_growth_axis_for_bbox(self, bbox):
        bounds = self.get_non_text_dxf_bounds()
        if bounds[0] is None or not bbox:
            return "both"
        ratio_x = self.auto_layout_dimension_ratio(bbox, bounds, "x")
        ratio_y = self.auto_layout_dimension_ratio(bbox, bounds, "y")
        grows_x = ratio_x >= 0.55
        grows_y = ratio_y >= 0.55
        if grows_x and grows_y:
            return "both"
        if grows_x:
            return "width"
        if grows_y:
            return "height"
        return "fixed"

    def make_parametric_group_data(self, name, handles, growth_axis="both", auto_grouped=False):
        group = {
            "name": name,
            "handles": set(handles),
            "k_w": 0.0,
            "k_h": 0.0,
            "growth_p_w": 0.0,
            "growth_p_h": 0.0,
            "growth_dir_x": "Центр",
            "growth_dir_y": "Центр",
            "shift_dir_x": "Вправо",
            "shift_dir_y": "Вгору",
            "link_x": "X = W",
            "link_y": "Y = H",
            "growth_axis": growth_axis,
            "resizes": False,
            "role_y": "manual",
            "auto_rule": False,
            "auto_grouped": auto_grouped,
            "touch_y_enabled": False,
            "touch_to_uid": None,
            "touch_gap_y": 0.0
        }
        self.get_group_key(group)
        self.apply_growth_axis_to_group(group)
        return group

    def union_bboxes(self, bboxes):
        valid = [bbox for bbox in bboxes if bbox]
        if not valid:
            return None
        return (
            min(b[0] for b in valid),
            min(b[1] for b in valid),
            max(b[2] for b in valid),
            max(b[3] for b in valid),
        )

    def bboxes_near(self, a, b, tolerance):
        return not (
            a[2] < b[0] - tolerance or
            b[2] < a[0] - tolerance or
            a[3] < b[1] - tolerance or
            b[3] < a[1] - tolerance
        )

    def collect_autogroup_entries(self):
        entries = []
        for entity in self.doc.modelspace():
            bbox = self.entity_bbox(entity)
            if not bbox:
                continue
            handle = entity.dxf.handle
            layer = str(getattr(entity.dxf, "layer", "") or "0")
            entries.append({
                "handle": handle,
                "bbox": bbox,
                "layer": layer,
                "type": entity.dxftype(),
            })
        return entries

    def build_layer_autogroups(self, entries):
        layer_map = {}
        for entry in entries:
            layer_map.setdefault(entry["layer"], []).append(entry)
        useful_layers = {
            layer: items for layer, items in layer_map.items()
            if len(items) > 1 and layer.strip() and layer.strip() != "0"
        }
        if len(useful_layers) < 2:
            return []
        groups = []
        for layer, items in sorted(useful_layers.items()):
            handles = [item["handle"] for item in items]
            bbox = self.union_bboxes([item["bbox"] for item in items])
            groups.append((f"Шар {layer}", handles, bbox))
        return groups

    def build_proximity_autogroups(self, entries, tolerance=3.0):
        n = len(entries)
        visited = set()
        groups = []
        for start in range(n):
            if start in visited:
                continue
            stack = [start]
            visited.add(start)
            component = []
            while stack:
                idx = stack.pop()
                component.append(entries[idx])
                bbox = entries[idx]["bbox"]
                for other in range(n):
                    if other in visited:
                        continue
                    if self.bboxes_near(bbox, entries[other]["bbox"], tolerance):
                        visited.add(other)
                        stack.append(other)
            groups.append(component)
        result = []
        for i, component in enumerate(groups, start=1):
            handles = [item["handle"] for item in component]
            bbox = self.union_bboxes([item["bbox"] for item in component])
            result.append((f"Деталь {i}", handles, bbox))
        return result

    def auto_group_entities(self):
        entries = self.collect_autogroup_entries()
        if not entries:
            self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автогрупування.</font>")
            return
        if self.parametric_groups:
            answer = QMessageBox.question(
                self,
                "Автогрупувати",
                "Поточні параметричні групи буде замінено. Продовжити?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        auto_groups = self.build_layer_autogroups(entries)
        method = "layers"
        if not auto_groups:
            auto_groups = self.build_proximity_autogroups(entries)
            method = "proximity"

        auto_groups = [
            (name, handles, bbox)
            for name, handles, bbox in auto_groups
            if handles and bbox
        ]
        if not auto_groups:
            self.lbl_status_calc.setText("<font color='red'>Не вдалося сформувати групи автоматично.</font>")
            return

        self.record_action_snapshot()
        self.parametric_groups = []
        self.block_keep_state = {}
        file_axis = self.project_meta.get("growth_axis", "both")
        for name, handles, bbox in auto_groups:
            group = self.make_parametric_group_data(name, handles, file_axis, auto_grouped=True)
            self.parametric_groups.append(group)
            self.block_keep_state[group["uid"]] = True

        self.clear_selection()
        self.push_to_history()
        self.save_project_config()
        self.load_groups_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText(
            f"<font color='#a5d6a7'>Автогрупування: створено {len(self.parametric_groups)} груп ({method}).</font>"
        )

    def create_parametric_group(self):
        if len(self.selected_handles) < 1:
            return  

        name = self.ask_group_name()
        self.record_action_snapshot()

        for group in self.parametric_groups:
            group["handles"].difference_update(self.selected_handles)
        self.parametric_groups = [g for g in self.parametric_groups if len(g["handles"]) > 0]

        new_group = {
            "name": name,
            "handles": set(self.selected_handles),
            "k_w": 0.0, 
            "k_h": 0.0,
            "growth_p_w": 0.0, 
            "growth_p_h": 0.0,
            "growth_dir_x": "Центр",
            "growth_dir_y": "Центр",
            "shift_dir_x": "Вправо",
            "shift_dir_y": "Вгору",
            "link_x": "X = W",
            "link_y": "Y = H",
            "growth_axis": "both",
            "resizes": False,
            "role_y": "manual",
            "auto_rule": False,
            "touch_y_enabled": False,
            "touch_to_uid": None,
            "touch_gap_y": 0.0
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
            role = group.get("role_y", "manual")
            auto_mark = "⚙️" if group.get("auto_rule") else "✍️"
            touch_mark = "🔗" if group.get("touch_y_enabled") else ""
            axis_mark = {
                "both": "WH",
                "width": "W",
                "height": "H",
                "fixed": "fix",
            }.get(self.project_meta.get("growth_axis", "both"), "WH")
            text = f"🧩 {auto_mark}{touch_mark} {name} ({len(group['handles'])} об.) {axis_mark} Y:{role}"
            key = self.get_group_key(group)
            keep_mark = "keep" if self.block_keep_state.get(key, True) else "del"
            size_mark = "size" if self.group_resizes(group) else "move"
            link_x, link_y = self.link_pair_for_mode()
            text = f"{auto_mark}{touch_mark} {name} [{axis_mark} {size_mark} {keep_mark} {link_x}/{link_y}] ({len(group['handles'])} об.) Y:{role}"
            item = QListWidgetItem(text)
            item.setToolTip(text)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.group_list_widget.addItem(item)
        self.group_list_widget.blockSignals(False)
        self.load_block_filter_list()

    def on_group_selection_changed(self):
        selected = self.group_list_widget.selectedItems()
        widgets_to_toggle = [
            self.combo_k_w, self.combo_k_h, self.combo_growth_p_w, 
            self.combo_growth_p_h, self.combo_growth_dir_x, self.combo_growth_dir_y,
            self.combo_shift_dir_x, self.combo_shift_dir_y,
            self.chk_group_resizes
        ]
        
        if not selected:
            for widget in widgets_to_toggle: widget.setEnabled(False)
            self.chk_group_resizes.blockSignals(True)
            self.chk_group_resizes.setChecked(False)
            self.chk_group_resizes.blockSignals(False)
            self.apply_group_controls_visibility(None)
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
        self.chk_group_resizes.setChecked(self.group_resizes(group))
        
        self.combo_growth_dir_x.setCurrentText(group.get("growth_dir_x", "Вправо"))
        self.combo_growth_dir_y.setCurrentText(group.get("growth_dir_y", "Вгору"))
        self.combo_shift_dir_x.setCurrentText(group.get("shift_dir_x", "Вправо"))
        self.combo_shift_dir_y.setCurrentText(group.get("shift_dir_y", "Вгору"))
        
        self.apply_axis_link_mode_to_groups()
        self.sync_link_combos_from_file_mode()

        for widget in widgets_to_toggle:
            widget.blockSignals(False)

        self.apply_group_controls_visibility(group)
        self.selected_handles = set(group["handles"])
        self.sync_list_from_handles()
        self.update_viewer()

    def growth_axis_to_label(self, axis):
        return {
            "both": "Ширина + висота",
            "width": "Тільки ширина",
            "height": "Тільки висота",
            "fixed": "Не росте",
        }.get(axis, "Ширина + висота")

    def growth_axis_from_label(self, label):
        text = str(label)
        if "Тільки ширина" in text:
            return "width"
        if "Тільки висота" in text:
            return "height"
        if "Не росте" in text:
            return "fixed"
        return "both"

    def normalize_growth_axis(self, value=None):
        value = value or self.project_meta.get("growth_axis", "both")

        mapping = {
            "Ширина + висота": "both",
            "Тільки ширина": "width",
            "Тільки висота": "height",
            "Не росте": "none",
            "both": "both",
            "width": "width",
            "height": "height",
            "none": "none",
        }

        return mapping.get(str(value).strip(), "both")
    




    def set_param_grid_row_visible(self, row, visible):
        if not hasattr(self, "param_transform_grid"):
            return

        for col in range(self.param_transform_grid.columnCount()):
            item = self.param_transform_grid.itemAtPosition(row, col)
            if item is None:
                continue

            widget = item.widget()
            if widget is not None:
                widget.setVisible(visible)

    def swap_growth_axis_for_quarter_turn(self, axis):
        if axis == "width":
            return "height"
        if axis == "height":
            return "width"
        return axis
    
    

    def update_growth_axis_after_transform(self, mode):
        if mode not in ("ROT90", "ROT270"):
            return
        self.project_meta["growth_axis"] = self.swap_growth_axis_for_quarter_turn(
            self.project_meta.get("growth_axis", "both")
        )
        for group in self.parametric_groups:
            if "growth_axis" in group:
                group["growth_axis"] = self.swap_growth_axis_for_quarter_turn(
                    group.get("growth_axis", "both")
                )
        self.sync_file_growth_axis_combo()

    def link_pair_for_mode(self, mode=None):
        """Повертає пару прив'язок осей із режиму файлу.

        У БД зберігаємо тільки AxisLinkMode:
        - normal  => X = W, Y = H
        - rotated => X = H, Y = W
        """
        mode = str(mode or self.project_meta.get("axis_link_mode") or "normal").strip().lower()
        if mode == "rotated":
            return "X = H", "Y = W"
        return "X = W", "Y = H"

    def axis_mode_from_link_x(self, link_x=None):
        link_x = link_x or (self.combo_link_x.currentText() if hasattr(self, "combo_link_x") else "X = W")
        return "rotated" if str(link_x).strip() == "X = H" else "normal"

    def apply_axis_link_mode_to_groups(self):
        """Синхронізує глобальну прив'язку осей з усіма групами."""
        mode = str(self.project_meta.get("axis_link_mode") or "normal").strip().lower()
        if mode not in ("normal", "rotated"):
            mode = "normal"
        self.project_meta["axis_link_mode"] = mode

        link_x, link_y = self.link_pair_for_mode(mode)
        self.project_meta["link_x"] = link_x
        self.project_meta["link_y"] = link_y

        for group in self.parametric_groups:
            group["link_x"] = link_x
            group["link_y"] = link_y

    def sync_axis_inputs_from_meta(self):
        """Виставляє combo X/Y за AxisLinkMode, а не навпаки."""
        mode = str(self.project_meta.get("axis_link_mode") or "normal").strip().lower()
        if mode not in ("normal", "rotated"):
            mode = "normal"
        self.project_meta["axis_link_mode"] = mode

        link_x, link_y = self.link_pair_for_mode(mode)
        self.project_meta["link_x"] = link_x
        self.project_meta["link_y"] = link_y

        if hasattr(self, "combo_link_x"):
            self.combo_link_x.blockSignals(True)
            self.combo_link_x.setCurrentText(link_x)
            self.combo_link_x.blockSignals(False)

        if hasattr(self, "combo_link_y"):
            self.combo_link_y.blockSignals(True)
            self.combo_link_y.setCurrentText(link_y)
            self.combo_link_y.blockSignals(False)

    def swap_axis_link_mode_for_quarter_turn(self, mode):
        if mode not in ("ROT90", "ROT270"):
            return
        current = self.project_meta.get("axis_link_mode", "normal")
        self.project_meta["axis_link_mode"] = "rotated" if current == "normal" else "normal"
        self.apply_axis_link_mode_to_groups()
        self.sync_link_combos_from_file_mode()

    def set_param_grid_row_visible(self, row, visible):
        grid = getattr(self, "param_transform_grid", None)
        if not grid:
            return
        for col in range(grid.columnCount()):
            item = grid.itemAtPosition(row, col)
            if item and item.widget():
                item.widget().setVisible(visible)

    def apply_growth_axis_ui(self, axis):
        """Показує тільки ті осі, які дозволені режимом файлу."""
        axis = self.normalize_growth_axis(axis)
        self.project_meta["growth_axis"] = axis
        self.set_param_grid_row_visible(0, axis in ("both", "width"))
        self.set_param_grid_row_visible(2, axis in ("both", "height"))

    def set_param_grid_cells_visible(self, row, columns, visible):
        grid = getattr(self, "param_transform_grid", None)
        if not grid:
            return
        for col in columns:
            item = grid.itemAtPosition(row, col)
            if item and item.widget():
                item.widget().setVisible(visible)

    def group_resizes(self, group):
        if not group:
            return False
        if "resizes" in group:
            return bool(group.get("resizes"))
        return (
            abs(float(group.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
            abs(float(group.get("growth_p_h", 0.0) or 0.0)) > 0.000001
        )

    def apply_group_controls_visibility(self, group=None):
        axis = self.normalize_growth_axis(self.project_meta.get("growth_axis", "both"))

        show_growth = bool(group.get("resizes", False)) if group else False
        show_x = axis in ("both", "width")
        show_y = axis in ("both", "height")

        self.set_param_grid_row_visible(0, show_x)
        self.set_param_grid_row_visible(2, show_y)
        self.set_param_grid_row_visible(1, show_x and show_growth)
        self.set_param_grid_row_visible(3, show_y and show_growth)
        

    def sync_link_combos_from_file_mode(self):
        mode = self.project_meta.get("axis_link_mode", "normal")

        if mode == "rotated":
            link_x = "X = H"
            link_y = "Y = W"
        else:
            link_x = "X = W"
            link_y = "Y = H"

        self.project_meta["link_x"] = link_x
        self.project_meta["link_y"] = link_y

        if hasattr(self, "combo_link_x"):
            self.combo_link_x.blockSignals(True)
            self.combo_link_x.setCurrentText(link_x)
            self.combo_link_x.blockSignals(False)

        if hasattr(self, "combo_link_y"):
            self.combo_link_y.blockSignals(True)
            self.combo_link_y.setCurrentText(link_y)
            self.combo_link_y.blockSignals(False)

    def apply_growth_axis_to_group(self, group):
        axis = self.normalize_growth_axis(self.project_meta.get("growth_axis", "both"))
        self.project_meta["growth_axis"] = axis

        if not self.group_resizes(group):
            group["growth_p_w"] = 0.0
            group["growth_p_h"] = 0.0
            group["growth_dir_x"] = "Центр"
            group["growth_dir_y"] = "Центр"
            return

        if axis in ("height", "fixed"):
            group["growth_p_w"] = 0.0
            group["growth_dir_x"] = "Центр"
        if axis in ("width", "fixed"):
            group["growth_p_h"] = 0.0
            group["growth_dir_y"] = "Центр"

    def sync_file_growth_axis_combo(self):
        if not hasattr(self, "combo_group_growth_axis"):
            return
        self.combo_group_growth_axis.blockSignals(True)
        self.combo_group_growth_axis.setCurrentText(
            self.growth_axis_to_label(self.project_meta.get("growth_axis", "both"))
        )
        self.combo_group_growth_axis.blockSignals(False)
        current = self.group_list_widget.currentItem() if hasattr(self, "group_list_widget") else None
        group = self.parametric_groups[current.data(Qt.ItemDataRole.UserRole)] if current else None
        self.apply_group_controls_visibility(group)
        self.update_file_status_panel()

    def on_group_growth_axis_changed(self, text):
        self.record_action_snapshot()
        self.project_meta["growth_axis"] = self.normalize_growth_axis(self.growth_axis_from_label(text))
        for group in self.parametric_groups:
            self.apply_growth_axis_to_group(group)
        current = self.group_list_widget.currentItem()
        group = self.parametric_groups[current.data(Qt.ItemDataRole.UserRole)] if current else None
        self.apply_group_controls_visibility(group)
        self.save_project_config()
        self.on_group_selection_changed()

    def on_group_resizes_changed(self, state):
        selected = self.group_list_widget.selectedItems()
        if not selected:
            self.apply_group_controls_visibility(None)
            return

        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        if idx is None or idx < 0 or idx >= len(self.parametric_groups):
            self.apply_group_controls_visibility(None)
            return

        group = self.parametric_groups[idx]

        checked = state == Qt.CheckState.Checked or state == Qt.CheckState.Checked.value or bool(self.chk_group_resizes.isChecked())
        group["resizes"] = bool(checked)

        if not checked:
            group["growth_p_w"] = 0.0
            group["growth_p_h"] = 0.0
            group["growth_dir_x"] = "Центр"
            group["growth_dir_y"] = "Центр"
        else:
            # При вмиканні не задаємо ріст автоматично, тільки показуємо поля.
            group.setdefault("growth_p_w", 0.0)
            group.setdefault("growth_p_h", 0.0)
            if group.get("growth_dir_x") in (None, ""):
                group["growth_dir_x"] = "Вправо"
            if group.get("growth_dir_y") in (None, ""):
                group["growth_dir_y"] = "Вгору"

        self.apply_growth_axis_to_group(group)
        self.apply_group_controls_visibility(group)
        self.save_project_config()
        self.on_group_selection_changed()
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

    def on_link_x_changed(self, text=None):
        self.record_action_snapshot()
        self.project_meta["axis_link_mode"] = self.axis_mode_from_link_x(text)

        self.apply_axis_link_mode_to_groups()
        self.sync_axis_inputs_from_meta()
        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_file_status_panel()

    def on_link_y_changed(self, text=None):
        self.record_action_snapshot()
        text = text or (self.combo_link_y.currentText() if hasattr(self, "combo_link_y") else "Y = H")
        self.project_meta["axis_link_mode"] = "rotated" if str(text).strip() == "Y = W" else "normal"

        self.apply_axis_link_mode_to_groups()
        self.sync_axis_inputs_from_meta()
        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_file_status_panel()

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

    def on_shift_dir_x_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["shift_dir_x"] = text
        self.save_project_config()

    def on_shift_dir_y_changed(self, text):
        selected = self.group_list_widget.selectedItems()
        if not selected: return
        self.record_action_snapshot()
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        self.parametric_groups[idx]["shift_dir_y"] = text
        self.save_project_config()



    def group_center_y(self, group):
        bbox = self.group_original_bbox(group)
        if not bbox:
            return 0.0
        return (bbox[1] + bbox[3]) * 0.5

    def group_center_x(self, group):
        bbox = self.group_original_bbox(group)
        if not bbox:
            return 0.0
        return (bbox[0] + bbox[2]) * 0.5

    def ensure_topology_fields(self, group):
        self.get_group_key(group)
        group.setdefault("role_y", "manual")
        group.setdefault("auto_rule", False)
        group.setdefault("touch_y_enabled", False)
        group.setdefault("touch_to_uid", None)
        group.setdefault("touch_gap_y", 0.0)
        group.setdefault("growth_axis", "both")
        group.setdefault("resizes", (
            abs(float(group.get("growth_p_w", 0.0) or 0.0)) > 0.000001 or
            abs(float(group.get("growth_p_h", 0.0) or 0.0)) > 0.000001
        ))
        group.setdefault("auto_chain_x", False)
        group.setdefault("chain_shift_x", 0.0)
        group.setdefault("chain_growth_own_x", 0.0)
        group.setdefault("chain_growth_after_x", 0.0)

    def groups_overlap_by_x(self, bbox_a, bbox_b, tolerance=2.0):
        if not bbox_a or not bbox_b:
            return False
        return not (bbox_a[2] < bbox_b[0] - tolerance or bbox_b[2] < bbox_a[0] - tolerance)

    def auto_apply_vertical_topology_rules(self):
        """
        AUTO RULES Y / Авто правила Y.

        Що робить:
        1) бере всі параметричні групи, у яких є bbox;
        2) рахує центр групи по Y;
        3) знаходить найнижчий і найвищий центр;
        4) перетворює позицію групи у коефіцієнт k_h:
           - низ  => k_h = 0.0
           - верх => k_h = 1.0
           - середина => пропорційно, часто 0.5
        5) записує це в JSON як auto_rule=True, role_y=bottom/middle/top.

        ВАЖЛИВО:
        ця кнопка НЕ рахує суму ростів. Для суми ростів є кнопка "Авто сума росту Y".
        """
        valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
        if not valid_groups:
            self.lbl_status_calc.setText("<font color='red'>Немає груп з геометрією для автоаналізу Y.</font>")
            self.topology_debug_print("AUTO RULES Y: немає груп з bbox")
            return

        self.record_action_snapshot()

        rows = []
        rows.append("AUTO RULES Y / Авто правила Y")
        rows.append("Сенс: програма сама визначає низ/середину/верх і ставить k_h.")
        rows.append("Формула: k_h = (centerY - minCenterY) / (maxCenterY - minCenterY)")
        rows.append("Потім: близько до низу => 0; близько до верху => 1; близько до центру => 0.5")
        rows.append("")

        centers = [self.group_center_y(g) for g in valid_groups]
        min_c, max_c = min(centers), max(centers)
        span = max(max_c - min_c, 0.0001)
        rows.append(f"minCenterY={min_c:.3f}; maxCenterY={max_c:.3f}; span={span:.3f}")
        rows.append("")

        sorted_groups = sorted(valid_groups, key=self.group_center_y)
        rows.append("Групи знизу вгору:")
        for i, group in enumerate(sorted_groups, start=1):
            bbox = self.group_original_bbox(group)
            uid = self.get_group_key(group)
            cy = self.group_center_y(group)
            rows.append(
                f"  #{i}: name={group.get('name')} uid={uid} "
                f"bbox=(minY={bbox[1]:.3f}, maxY={bbox[3]:.3f}) centerY={cy:.3f}"
            )
        rows.append("")
        rows.append("Рішення по кожній групі:")

        for group in sorted_groups:
            self.ensure_topology_fields(group)
            uid = self.get_group_key(group)
            bbox = self.group_original_bbox(group)
            cy = self.group_center_y(group)
            raw_k = (cy - min_c) / span
            k = raw_k
            reason = "пропорційне положення між низом і верхом"

            if k < 0.15:
                role = "bottom"
                k = 0.0
                reason = "центр близько до нижнього краю => фіксуємо як НИЗ"
            elif k > 0.85:
                role = "top"
                k = 1.0
                reason = "центр близько до верхнього краю => фіксуємо як ВЕРХ"
            else:
                role = "middle"
                if abs(k - 0.5) < 0.18:
                    k = 0.5
                    reason = "центр близько до середини => ставимо 50%"

            old_k_h = float(group.get("k_h", 0.0) or 0.0)
            old_growth = float(group.get("growth_p_h", 0.0) or 0.0)
            old_dir = group.get("growth_dir_y", "Центр")

            group.update({
                "k_h": round(float(k), 4),
                "growth_p_h": 0.0,
                "growth_dir_y": "Центр",
                "link_y": "Y = H",
                "role_y": role,
                "auto_rule": True,
            })

            rows.append(
                f"  group={group.get('name')} uid={uid}: "
                f"centerY={cy:.3f}; raw_k={raw_k:.6f}; "
                f"old_k_h={old_k_h:.6f} -> new_k_h={k:.6f} ({k*100:.2f}%); "
                f"old_growth_p_h={old_growth:.6f} -> new_growth_p_h=0; "
                f"old_dir={old_dir} -> new_dir=Центр; role_y={role}; reason={reason}"
            )

        rows.append("")
        rows.append("РЕЗУЛЬТАТ: Авто правила Y тільки розставляють позиційний зсув k_h: низ=0%, середина≈50%, верх=100%.")
        rows.append("Якщо треба логіка 50% + 5% = 55%, натискай 'Авто сума росту Y'.")
        self.topology_debug_print("AUTO RULES Y / Авто правила Y", rows)

        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_viewer()
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Авто правила Y застосовано. Деталі дивись у консолі: [TOPOLOGY DEBUG] AUTO RULES Y.</font>")

    def topology_debug_print(self, title, rows=None):
        """Єдиний формат логів у консоль для топологічних розрахунків."""
        print("\n" + "=" * 90)
        print(f"[TOPOLOGY DEBUG] {title}")
        print("=" * 90)
        if rows:
            for row in rows:
                print(row)
        print("=" * 90 + "\n")

    def auto_layout_dimension_ratio(self, bbox, bounds, axis):
        min_x, min_y, max_x, max_y = bounds
        if axis == "x":
            total = max(max_x - min_x, 0.0001)
            return max((bbox[2] - bbox[0]) / total, 0.0)
        total = max(max_y - min_y, 0.0001)
        return max((bbox[3] - bbox[1]) / total, 0.0)
    

    def format_factor(val):
        """Конвертує коефіцієнт назад у зрозумілий текст для UI"""
        if abs(val - 0.0) < 0.001: return "0% (Фіксовано)"
        if abs(val - 0.25) < 0.001: return "25% (1/4)"
        if abs(val - 0.333) < 0.01: return "33.3% (Δ/3)"
        if abs(val - 0.5) < 0.001: return "50% (Δ/2)"
        if abs(val - 0.667) < 0.01: return "66.7% (Δ/3)"
        if abs(val - 0.75) < 0.01: return  "75% (1/4)"
        if abs(val - 1.0) < 0.001: return "100% (Δ)"
        return f"{val*100:g}%"
    


    def seed_auto_layout_growth(self):
        bounds = self.get_non_text_dxf_bounds()
        min_x, min_y, max_x, max_y = bounds
        if min_x is None:
            return []

        width = max(max_x - min_x, 0.0001)
        height = max(max_y - min_y, 0.0001)
        edge_tol_x = max(width * 0.025, 2.0)
        edge_tol_y = max(height * 0.025, 2.0)
        rows = [
            "AUTO LAYOUT SEED / start growth detection",
            f"bounds: minX={min_x:.3f}, maxX={max_x:.3f}, minY={min_y:.3f}, maxY={max_y:.3f}",
        ]

        for group in self.parametric_groups:
            bbox = self.group_original_bbox(group)
            if not bbox:
                continue
            self.ensure_topology_fields(group)
            bx1, by1, bx2, by2 = bbox
            ratio_x = self.auto_layout_dimension_ratio(bbox, bounds, "x")
            ratio_y = self.auto_layout_dimension_ratio(bbox, bounds, "y")

            axis = self.project_meta.get("growth_axis", "both")
            if axis == "width":
                grow_x, grow_y = True, False
            elif axis == "height":
                grow_x, grow_y = False, True
            elif axis == "fixed":
                grow_x, grow_y = False, False
            else:
                grow_x = ratio_x >= 0.55
                grow_y = ratio_y >= 0.55
            group["link_x"] = "X = W"
            group["link_y"] = "Y = H"
            group["shift_dir_x"] = "Вправо"
            group["shift_dir_y"] = "Вгору"
            group["growth_p_w"] = 1.0 if grow_x else 0.0
            group["growth_p_h"] = 1.0 if grow_y else 0.0

            if grow_x:
                if abs(bx1 - min_x) <= edge_tol_x:
                    group["growth_dir_x"] = "Вправо"
                elif abs(bx2 - max_x) <= edge_tol_x:
                    group["growth_dir_x"] = "Вліво"
                else:
                    group["growth_dir_x"] = "Центр"
            else:
                group["growth_dir_x"] = "Центр"

            if grow_y:
                if abs(by1 - min_y) <= edge_tol_y:
                    group["growth_dir_y"] = "Вгору"
                elif abs(by2 - max_y) <= edge_tol_y:
                    group["growth_dir_y"] = "Вниз"
                else:
                    group["growth_dir_y"] = "Центр"
            else:
                group["growth_dir_y"] = "Центр"

            group["auto_layout"] = True
            group["auto_layout_ratio_x"] = round(float(ratio_x), 6)
            group["auto_layout_ratio_y"] = round(float(ratio_y), 6)
            rows.append(
                f"{group.get('name')} uid={self.get_group_key(group)}: "
                f"ratioX={ratio_x:.3f}, ratioY={ratio_y:.3f}, "
                f"growthX={group['growth_p_w']:.1f} dirX={group['growth_dir_x']}, "
                f"growthY={group['growth_p_h']:.1f} dirY={group['growth_dir_y']}"
            )
        return rows

    def finish_auto_layout_position_rules(self):
        bounds = self.get_non_text_dxf_bounds()
        min_x, min_y, max_x, max_y = bounds
        if min_x is None:
            return []

        width = max(max_x - min_x, 0.0001)
        height = max(max_y - min_y, 0.0001)
        edge_tol_x = max(width * 0.025, 2.0)
        edge_tol_y = max(height * 0.025, 2.0)
        rows = ["AUTO LAYOUT FINISH / position shifts for fixed groups"]

        for group in self.parametric_groups:
            bbox = self.group_original_bbox(group)
            if not bbox:
                continue
            bx1, by1, bx2, by2 = bbox
            cx = (bx1 + bx2) * 0.5
            cy = (by1 + by2) * 0.5

            if abs(float(group.get("growth_p_w", 0.0) or 0.0)) <= 0.000001:
                if abs(bx1 - min_x) <= edge_tol_x:
                    k_w = 0.0
                    reason_x = "left edge"
                elif abs(bx2 - max_x) <= edge_tol_x:
                    k_w = 1.0
                    reason_x = "right edge"
                else:
                    k_w = (cx - min_x) / width
                    reason_x = "relative center X"
                group["k_w"] = round(float(max(0.0, min(1.0, k_w))), 6)
                group["link_x"] = "X = W"
                group["shift_dir_x"] = "Вправо"
                rows.append(f"{group.get('name')}: k_w={group['k_w']:.6f} ({reason_x})")

            if abs(float(group.get("growth_p_h", 0.0) or 0.0)) <= 0.000001:
                if abs(by1 - min_y) <= edge_tol_y:
                    k_h = 0.0
                    reason_y = "bottom edge"
                elif abs(by2 - max_y) <= edge_tol_y:
                    k_h = 1.0
                    reason_y = "top edge"
                else:
                    k_h = (cy - min_y) / height
                    reason_y = "relative center Y"
                group["k_h"] = round(float(max(0.0, min(1.0, k_h))), 6)
                group["link_y"] = "Y = H"
                group["shift_dir_y"] = "Вгору"
                rows.append(f"{group.get('name')}: k_h={group['k_h']:.6f} ({reason_y})")

        return rows

    def auto_layout_all_groups(self):
        valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
        if not valid_groups:
            self.lbl_status_calc.setText("<font color='red'>Немає параметричних груп з геометрією для авторозстановки.</font>")
            return

        self.record_action_snapshot()
        rows = ["AUTHOROZSTAVYTY ALL / Авторозставити все"]
        rows.extend(self.seed_auto_layout_growth())

        self.suppress_auto_chain_snapshot = True
        try:
            self.auto_chain_growth_x()
            self.auto_chain_growth_y()
        finally:
            self.suppress_auto_chain_snapshot = False

        rows.extend(self.finish_auto_layout_position_rules())
        rows.append("Done: old k/growth coefficients are filled automatically; manual controls remain available.")

        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_viewer()
        self.topology_debug_print("AUTHOROZSTAVYTY ALL / Авторозставити все", rows)
        self.lbl_status_calc.setText("<font color='#a5d6a7'>Авторозставлення виконано: ріст і зсуви заповнені автоматично.</font>")

    def auto_chain_growth_y(self):
        """
        AUTO CHAIN Y / Авто сума росту Y, але НЕ одним загальним списком.

        ВАЖЛИВО:
        - ліва вертикальна сторона рахується окремо;
        - права вертикальна сторона рахується окремо;
        - центр рахується від середнього/узгодженого результату лівої і правої сторони;
        - групи, які лежать на одному Y-рівні, НЕ складаються одна з одною як 50%+50%.
          Для одного рівня береться максимальний ріст рівня, бо це одна і та сама висотна зона.

        Це виправляє ситуацію з логу:
            1 росте 50%
            рп1 росте 50%
        Вони не мають давати 100%, якщо це ліва/права сторона одного рівня.
        """
        min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
        if min_x is None:
            self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автоматичної суми росту Y.</font>")
            self.topology_debug_print("AUTO CHAIN Y SIDES: немає геометрії")
            return

        axis_x = (min_x + max_x) * 0.5
        width = max_x - min_x
        height = max_y - min_y
        center_tolerance_x = max(width * 0.015, 2.0)
        level_tolerance_y = max(height * 0.003, 0.5)
        balance_tolerance = 0.0005  # 0.05%

        left_items = []
        right_items = []
        center_items = []

        for group in self.parametric_groups:
            bbox = self.group_original_bbox(group)
            if not bbox:
                continue
            self.ensure_topology_fields(group)
            uid = self.get_group_key(group)
            bx1, by1, bx2, by2 = bbox
            center_x = (bx1 + bx2) * 0.5
            center_y = (by1 + by2) * 0.5
            growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))

            item = {
                "group": group,
                "uid": uid,
                "name": group.get("name", ""),
                "bbox": bbox,
                "min_x": bx1,
                "max_x": bx2,
                "min_y": by1,
                "max_y": by2,
                "center_x": center_x,
                "center_y": center_y,
                "growth": growth,
            }

            # Якщо користувач уже вручну задав side_x у JSON — поважаємо це.
            explicit_side = str(group.get("side_x", "")).strip().lower()
            if explicit_side in ("left", "right", "center"):
                side = explicit_side
            elif center_x < axis_x - center_tolerance_x:
                side = "left"
            elif center_x > axis_x + center_tolerance_x:
                side = "right"
            else:
                side = "center"

            item["side"] = side
            if side == "left":
                left_items.append(item)
            elif side == "right":
                right_items.append(item)
            else:
                center_items.append(item)

        if not left_items and not right_items and not center_items:
            self.lbl_status_calc.setText("<font color='red'>Немає груп для автоматичної суми росту Y.</font>")
            self.topology_debug_print("AUTO CHAIN Y SIDES: немає валідних груп")
            return

        def sort_bottom_up(items):
            items.sort(key=lambda item: (item["center_y"], item["min_y"], item["center_x"]))

        sort_bottom_up(left_items)
        sort_bottom_up(right_items)
        sort_bottom_up(center_items)

        def make_levels(items):
            """Об'єднує групи з майже однаковим center_y в один висотний рівень."""
            levels = []
            for item in items:
                placed = False
                for level in levels:
                    if abs(level["center_y"] - item["center_y"]) <= level_tolerance_y:
                        level["items"].append(item)
                        # Плавно уточнюємо центр рівня, щоб не залежати від першого елемента.
                        level["center_y"] = sum(x["center_y"] for x in level["items"]) / len(level["items"])
                        level["min_y"] = min(level["min_y"], item["min_y"])
                        level["max_y"] = max(level["max_y"], item["max_y"])
                        placed = True
                        break
                if not placed:
                    levels.append({
                        "center_y": item["center_y"],
                        "min_y": item["min_y"],
                        "max_y": item["max_y"],
                        "items": [item],
                    })
            levels.sort(key=lambda level: (level["center_y"], level["min_y"]))
            for level in levels:
                # Рівень — це одна висотна зона. Не складаємо 50%+50% для паралельних деталей одного рівня.
                level["growth"] = max((x["growth"] for x in level["items"]), default=0.0)
            return levels

        left_levels = make_levels(left_items)
        right_levels = make_levels(right_items)
        center_levels = make_levels(center_items)

        left_sum = sum(level["growth"] for level in left_levels)
        right_sum = sum(level["growth"] for level in right_levels)
        diff = abs(left_sum - right_sum)

        rows = []
        rows.append("AUTO CHAIN Y SIDES / Авто сума росту Y по лівій/правій стороні")
        rows.append("Тепер це НЕ один список знизу вгору для всіх груп.")
        rows.append("Ліва сторона, права сторона і центр розділяються по X.")
        rows.append("Групи на одному Y-рівні не додаються одна до одної: для рівня береться MAX growth_p_h.")
        rows.append("")
        rows.append(f"bounds: minX={min_x:.3f}, maxX={max_x:.3f}, minY={min_y:.3f}, maxY={max_y:.3f}")
        rows.append(f"axis_x={axis_x:.3f}, center_tolerance_x={center_tolerance_x:.3f}, level_tolerance_y={level_tolerance_y:.3f}")
        rows.append("")

        def describe_side(side_name, items, levels):
            rows.append(f"{side_name} groups після поділу по X:")
            if not items:
                rows.append("  немає")
            for i, item in enumerate(items, start=1):
                rows.append(
                    f"  {side_name[0]}#{i}: name={item['name']} uid={item['uid']} side={item['side']} "
                    f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}, "
                    f"minY={item['min_y']:.3f}, maxY={item['max_y']:.3f}) "
                    f"centerX={item['center_x']:.3f}; centerY={item['center_y']:.3f}; "
                    f"own_growth_p_h={item['growth']:.6f} ({item['growth']*100:.2f}%)"
                )
            rows.append(f"{side_name} Y-рівні:")
            if not levels:
                rows.append("  немає")
            for j, level in enumerate(levels, start=1):
                names = ", ".join(f"{x['name']}[{x['uid']}]" for x in level["items"])
                item_growths = ", ".join(f"{x['growth']*100:.2f}%" for x in level["items"])
                rows.append(
                    f"  level {j}: centerY≈{level['center_y']:.3f}; items={names}; "
                    f"item_growths=[{item_growths}]; level_growth=MAX={level['growth']:.6f} ({level['growth']*100:.2f}%)"
                )
            rows.append("")

        describe_side("LEFT", left_items, left_levels)
        describe_side("RIGHT", right_items, right_levels)
        describe_side("CENTER", center_items, center_levels)

        rows.append(f"SUM LEFT LEVELS  = {left_sum:.6f} ({left_sum*100:.2f}%)")
        rows.append(f"SUM RIGHT LEVELS = {right_sum:.6f} ({right_sum*100:.2f}%)")
        rows.append(f"DIFF             = {diff:.6f} ({diff*100:.2f}%)")

        normalize_to = None
        has_both_sides = bool(left_levels) and bool(right_levels)
        if has_both_sides and diff > balance_tolerance:
            rows.append("")
            rows.append("WARNING: ліва і права сторона мають різний сумарний ріст по Y.")
            rows.append("Перед записом k_h треба уточнити у конструктора.")
            self.topology_debug_print("AUTO CHAIN Y SIDES / ПОТРІБНЕ УТОЧНЕННЯ", rows)

            msg = (
                "Сумарний ріст по Y зліва і справа різний.\n\n"
                f"LEFT = {left_sum*100:.2f}%\n"
                f"RIGHT = {right_sum*100:.2f}%\n"
                f"DIFF = {diff*100:.2f}%\n\n"
                "Так — вирівняти до більшої суми пропорційно.\n"
                "Ні — застосувати як є, з різними зсувами.\n"
                "Cancel — нічого не змінювати."
            )
            answer = QMessageBox.question(
                self,
                "Y-сторони мають різний сумарний ріст",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )

            if answer == QMessageBox.StandardButton.Cancel:
                rows.append("КОНСТРУКТОР СКАСУВАВ: правила Y не застосовано.")
                self.topology_debug_print("AUTO CHAIN Y SIDES / Скасовано", rows)
                self.lbl_status_calc.setText("<font color='#ffcc80'>Авто сума Y скасована: сторони мали різний сумарний ріст.</font>")
                return

            if answer == QMessageBox.StandardButton.Yes:
                normalize_to = max(left_sum, right_sum)
                rows.append("")
                rows.append(f"КОНСТРУКТОР ОБРАВ ВИРІВНЯТИ: target_sum={normalize_to:.6f} ({normalize_to*100:.2f}%)")
            else:
                rows.append("")
                rows.append("КОНСТРУКТОР ОБРАВ ЗАСТОСУВАТИ ЯК Є: ліва/права сторона можуть мати різні k_h.")
        elif has_both_sides:
            rows.append("OK: сумарний ріст лівої і правої сторони по Y однаковий у межах допуску.")
        else:
            rows.append("INFO: знайдена тільки одна сторона або тільки центр; порівнювати LEFT/RIGHT немає з чим.")

        if not getattr(self, "suppress_auto_chain_snapshot", False):
            self.record_action_snapshot()

        def scale_levels(levels, current_sum, target_sum, side_name):
            if target_sum is None or abs(current_sum - target_sum) <= balance_tolerance:
                return
            if current_sum <= 0.000001:
                rows.append(
                    f"NORMALIZE {side_name}: поточна сума 0%, неможливо пропорційно масштабувати. "
                    f"Задай growth_p_h хоча б для одного рівня цієї сторони вручну."
                )
                return
            factor = target_sum / current_sum
            rows.append(
                f"NORMALIZE {side_name}: current_sum={current_sum:.6f} -> target_sum={target_sum:.6f}; factor={factor:.6f}"
            )
            for level in levels:
                old_level_growth = level["growth"]
                new_level_growth = old_level_growth * factor
                level["growth"] = new_level_growth
                rows.append(
                    f"  {side_name} level centerY≈{level['center_y']:.3f}: "
                    f"level_growth {old_level_growth:.6f} -> {new_level_growth:.6f} "
                    f"({old_level_growth*100:.2f}% -> {new_level_growth*100:.2f}%)"
                )
                # Масштабуємо тільки ті групи рівня, які реально мали ріст.
                for item in level["items"]:
                    g = item["group"]
                    old = abs(float(g.get("growth_p_h", 0.0) or 0.0))
                    if old > 0.000001:
                        new_val = old * factor
                        g["growth_p_h"] = round(float(new_val), 6)
                        item["growth"] = new_val
                        rows.append(
                            f"    {side_name} {g.get('name')} uid={item['uid']}: growth_p_h {old:.6f} -> {new_val:.6f} "
                            f"({old*100:.2f}% -> {new_val*100:.2f}%)"
                        )

        if normalize_to is not None:
            scale_levels(left_levels, left_sum, normalize_to, "LEFT")
            scale_levels(right_levels, right_sum, normalize_to, "RIGHT")
            left_sum = sum(level["growth"] for level in left_levels)
            right_sum = sum(level["growth"] for level in right_levels)
            diff = abs(left_sum - right_sum)
            rows.append("")
            rows.append("Після вирівнювання:")
            rows.append(f"SUM LEFT LEVELS  = {left_sum:.6f} ({left_sum*100:.2f}%)")
            rows.append(f"SUM RIGHT LEVELS = {right_sum:.6f} ({right_sum*100:.2f}%)")
            rows.append(f"DIFF             = {diff:.6f} ({diff*100:.2f}%)")

        def apply_levels(levels, side_name):
            cumulative = 0.0
            rows.append("")
            rows.append(f"Застосування {side_name} Y-chain:")
            for level_index, level in enumerate(levels, start=1):
                before = cumulative
                level_growth = float(level.get("growth", 0.0) or 0.0)
                rows.append(
                    f"  {side_name} level {level_index}: centerY≈{level['center_y']:.3f}; "
                    f"sum_below={before:.6f} ({before*100:.2f}%); "
                    f"level_growth={level_growth:.6f} ({level_growth*100:.2f}%)"
                )
                for item in level["items"]:
                    group = item["group"]
                    uid = item["uid"]
                    old_k = float(group.get("k_h", 0.0) or 0.0)
                    old_growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))

                    group["k_h"] = round(float(before), 6)
                    group["growth_p_h"] = round(float(old_growth), 6)
                    if old_growth > 0.000001:
                        group["growth_dir_y"] = "Вгору"
                    group["link_y"] = "Y = H"
                    group["side_y_chain"] = side_name.lower()
                    group["auto_chain_y"] = True
                    group["auto_chain_y_mode"] = "side_levels"
                    group["chain_shift_y"] = round(float(before), 6)
                    group["chain_growth_own_y"] = round(float(old_growth), 6)
                    group["chain_level_growth_y"] = round(float(level_growth), 6)
                    group["chain_growth_after_y"] = round(float(before + level_growth), 6)

                    rows.append(
                        f"    {side_name} {group.get('name')} uid={uid}: "
                        f"old_k_h={old_k:.6f} -> new_k_h={before:.6f} ({before*100:.2f}%); "
                        f"own_growth_p_h={old_growth:.6f} ({old_growth*100:.2f}%); "
                        f"level_growth_used={level_growth:.6f} ({level_growth*100:.2f}%); "
                        f"dir={group.get('growth_dir_y')}"
                    )
                cumulative += level_growth
            rows.append(f"  {side_name} final cumulative={cumulative:.6f} ({cumulative*100:.2f}%)")
            return cumulative

        final_left = apply_levels(left_levels, "LEFT") if left_levels else 0.0
        final_right = apply_levels(right_levels, "RIGHT") if right_levels else 0.0

        # Центр не складається сам із собою. Для центральних груп беремо shift на їхньому Y-рівні
        # як середнє між лівою і правою стороною для такого самого рівня.
        def shift_at_y(levels, y):
            cumulative = 0.0
            for level in levels:
                if level["center_y"] < y - level_tolerance_y:
                    cumulative += float(level.get("growth", 0.0) or 0.0)
            return cumulative

        rows.append("")
        rows.append("Застосування CENTER Y-chain:")
        if center_levels:
            for level in center_levels:
                center_y = level["center_y"]
                left_shift = shift_at_y(left_levels, center_y) if left_levels else None
                right_shift = shift_at_y(right_levels, center_y) if right_levels else None
                if left_shift is not None and right_shift is not None:
                    center_shift = (left_shift + right_shift) * 0.5
                    reason = f"average(left_shift={left_shift:.6f}, right_shift={right_shift:.6f})"
                elif left_shift is not None:
                    center_shift = left_shift
                    reason = f"left_shift={left_shift:.6f}"
                elif right_shift is not None:
                    center_shift = right_shift
                    reason = f"right_shift={right_shift:.6f}"
                else:
                    center_shift = 0.0
                    reason = "no side levels"

                level_growth = float(level.get("growth", 0.0) or 0.0)
                for item in level["items"]:
                    group = item["group"]
                    uid = item["uid"]
                    old_k = float(group.get("k_h", 0.0) or 0.0)
                    old_growth = abs(float(group.get("growth_p_h", 0.0) or 0.0))
                    group["k_h"] = round(float(center_shift), 6)
                    group["growth_p_h"] = round(float(old_growth), 6)
                    if old_growth > 0.000001:
                        group["growth_dir_y"] = "Вгору"
                    group["link_y"] = "Y = H"
                    group["side_y_chain"] = "center"
                    group["auto_chain_y"] = True
                    group["auto_chain_y_mode"] = "side_levels_center"
                    group["chain_shift_y"] = round(float(center_shift), 6)
                    group["chain_growth_own_y"] = round(float(old_growth), 6)
                    group["chain_level_growth_y"] = round(float(level_growth), 6)
                    rows.append(
                        f"  CENTER {group.get('name')} uid={uid}: old_k_h={old_k:.6f} -> new_k_h={center_shift:.6f} "
                        f"({center_shift*100:.2f}%); own_growth={old_growth:.6f}; reason={reason}"
                    )
        else:
            rows.append("  немає")

        rows.append("")
        rows.append("ФІНАЛ Y:")
        rows.append(f"  LEFT total  = {final_left:.6f} ({final_left*100:.2f}%)")
        rows.append(f"  RIGHT total = {final_right:.6f} ({final_right*100:.2f}%)")
        rows.append(f"  DIFF        = {abs(final_left-final_right):.6f} ({abs(final_left-final_right)*100:.2f}%)")
        rows.append("  Тепер 1 і рп1 не складаються у 100%, якщо вони є лівою/правою стороною одного рівня.")

        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_viewer()
        self.topology_debug_print("AUTO CHAIN Y SIDES / Авто сума росту Y по сторонах", rows)

        if has_both_sides and abs(final_left - final_right) <= balance_tolerance:
            self.lbl_status_calc.setText(
                f"<font color='#a5d6a7'>Авто сума Y по сторонах застосована. LEFT≈RIGHT={final_left*100:.1f}%.</font>"
            )
        else:
            self.lbl_status_calc.setText(
                f"<font color='#ffcc80'>Авто сума Y застосована: LEFT={final_left*100:.1f}%, RIGHT={final_right*100:.1f}%.</font>"
            )

    def auto_chain_growth_x(self):
        """
        AUTO CHAIN X / Авто сума росту X, але правильно для дверей/вікон:

        ВАЖЛИВО:
        - ліва сторона рахується окремо: від лівого краю до центру;
        - права сторона рахується окремо: від правого краю до центру;
        - сумарний growth_p_w лівої сторони порівнюється із сумарним growth_p_w правої сторони;
        - якщо суми різні, програма питає конструктора, що робити.

        Для лівої сторони:
            k_w = сума ростів лівіше
            growth_dir_x = Вправо

        Для правої сторони:
            k_w = 1 - сума ростів правіше
            growth_dir_x = Вліво

        Приклад:
            LEFT:  10% + 15% = 25%
            RIGHT: 5% + 20%  = 25%
            => OK, сторони збалансовані.

            LEFT:  25%
            RIGHT: 30%
            => WARNING, треба уточнення конструктора.
        """
        min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
        if min_x is None:
            self.lbl_status_calc.setText("<font color='red'>Немає геометрії для автоматичної суми росту X.</font>")
            self.topology_debug_print("AUTO CHAIN X SIDES: немає геометрії")
            return

        axis_x = (min_x + max_x) * 0.5
        width = max_x - min_x
        center_tolerance = max(width * 0.015, 2.0)

        left_items = []
        right_items = []
        center_items = []

        for group in self.parametric_groups:
            bbox = self.group_original_bbox(group)
            if not bbox:
                continue
            self.ensure_topology_fields(group)
            uid = self.get_group_key(group)
            bx1, by1, bx2, by2 = bbox
            center_x = (bx1 + bx2) * 0.5

            item = {
                "group": group,
                "uid": uid,
                "name": group.get("name", ""),
                "bbox": bbox,
                "min_x": bx1,
                "max_x": bx2,
                "center_x": center_x,
                "growth": abs(float(group.get("growth_p_w", 0.0) or 0.0)),
            }

            if center_x < axis_x - center_tolerance:
                item["side"] = "left"
                left_items.append(item)
            elif center_x > axis_x + center_tolerance:
                item["side"] = "right"
                right_items.append(item)
            else:
                item["side"] = "center"
                center_items.append(item)

        if not left_items and not right_items:
            self.lbl_status_calc.setText("<font color='red'>Не знайдено лівих/правих груп для X-логіки.</font>")
            self.topology_debug_print("AUTO CHAIN X SIDES: немає лівих/правих груп")
            return

        left_items.sort(key=lambda item: (item["center_x"], item["min_x"]))
        # Права сторона рахується від правого краю до центру.
        right_items.sort(key=lambda item: (-item["center_x"], -item["max_x"]))
        center_items.sort(key=lambda item: (item["center_x"], item["min_x"]))

        left_sum = sum(item["growth"] for item in left_items)
        right_sum = sum(item["growth"] for item in right_items)
        diff = abs(left_sum - right_sum)
        balance_tolerance = 0.0005  # 0.05%

        rows = []
        rows.append("AUTO CHAIN X SIDES / Авто сума росту X по сторонах")
        rows.append("НЕ один загальний ланцюг зліва направо, а два незалежні ланцюги:")
        rows.append("  LEFT:  лівий край -> центр, growth_dir_x=Вправо")
        rows.append("  RIGHT: правий край -> центр, growth_dir_x=Вліво")
        rows.append("Після цього програма порівнює сумарний % росту LEFT і RIGHT.")
        rows.append("")
        rows.append(f"bounds_x: minX={min_x:.3f}, maxX={max_x:.3f}, width={width:.3f}")
        rows.append(f"axis_x={axis_x:.3f}, center_tolerance={center_tolerance:.3f}")
        rows.append("")

        rows.append("LEFT groups, від лівого краю до центру:")
        if left_items:
            for i, item in enumerate(left_items, start=1):
                rows.append(
                    f"  L#{i}: name={item['name']} uid={item['uid']} "
                    f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
                    f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
                )
        else:
            rows.append("  немає")

        rows.append("")
        rows.append("RIGHT groups, від правого краю до центру:")
        if right_items:
            for i, item in enumerate(right_items, start=1):
                rows.append(
                    f"  R#{i}: name={item['name']} uid={item['uid']} "
                    f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
                    f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
                )
        else:
            rows.append("  немає")

        rows.append("")
        rows.append("CENTER groups, біля центру, не беруть участь у сумі сторін:")
        if center_items:
            for i, item in enumerate(center_items, start=1):
                rows.append(
                    f"  C#{i}: name={item['name']} uid={item['uid']} "
                    f"bbox=(minX={item['min_x']:.3f}, maxX={item['max_x']:.3f}) "
                    f"centerX={item['center_x']:.3f}; own_growth={item['growth']:.6f} ({item['growth']*100:.2f}%)"
                )
        else:
            rows.append("  немає")

        rows.append("")
        rows.append(f"SUM LEFT  = {left_sum:.6f} ({left_sum*100:.2f}%)")
        rows.append(f"SUM RIGHT = {right_sum:.6f} ({right_sum*100:.2f}%)")
        rows.append(f"DIFF      = {diff:.6f} ({diff*100:.2f}%)")

        # Якщо суми не рівні, перед застосуванням питаємо конструктора.
        normalize_to = None
        if diff > balance_tolerance:
            rows.append("")
            rows.append("WARNING: Сумарний ріст лівої і правої сторони НЕ однаковий.")
            rows.append("Програма має уточнити у конструктора перед записом k_w.")
            self.topology_debug_print("AUTO CHAIN X SIDES / ПОТРІБНЕ УТОЧНЕННЯ", rows)

            msg = (
                "Сумарний ріст лівої і правої сторони різний.\n\n"
                f"LEFT = {left_sum*100:.2f}%\n"
                f"RIGHT = {right_sum*100:.2f}%\n"
                f"DIFF = {diff*100:.2f}%\n\n"
                "Так — вирівняти до більшої суми пропорційно.\n"
                "Ні — застосувати як є, з різними зсувами.\n"
                "Cancel — нічого не змінювати."
            )
            answer = QMessageBox.question(
                self,
                "X-сторони мають різний сумарний ріст",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )

            if answer == QMessageBox.StandardButton.Cancel:
                rows.append("КОНСТРУКТОР СКАСУВАВ: правила X не застосовано.")
                self.topology_debug_print("AUTO CHAIN X SIDES / Скасовано", rows)
                self.lbl_status_calc.setText("<font color='#ffcc80'>Авто сума X скасована: сторони мали різний сумарний ріст.</font>")
                return

            if answer == QMessageBox.StandardButton.Yes:
                normalize_to = max(left_sum, right_sum)
                rows.append("")
                rows.append(f"КОНСТРУКТОР ОБРАВ ВИРІВНЯТИ: target_sum={normalize_to:.6f} ({normalize_to*100:.2f}%)")
            else:
                rows.append("")
                rows.append("КОНСТРУКТОР ОБРАВ ЗАСТОСУВАТИ ЯК Є: ліві і праві зсуви можуть відрізнятися.")
        else:
            rows.append("OK: Сумарний ріст лівої і правої сторони однаковий у межах допуску.")

        if not getattr(self, "suppress_auto_chain_snapshot", False):
            self.record_action_snapshot()

        def scale_side(items, current_sum, target_sum, side_name):
            if target_sum is None or abs(current_sum - target_sum) <= balance_tolerance:
                return
            if current_sum <= 0.000001:
                rows.append(
                    f"NORMALIZE {side_name}: поточна сума 0%, неможливо пропорційно масштабувати. "
                    f"Задай growth_p_w хоча б для однієї групи цієї сторони вручну."
                )
                return
            factor = target_sum / current_sum
            rows.append(
                f"NORMALIZE {side_name}: current_sum={current_sum:.6f} -> target_sum={target_sum:.6f}; "
                f"factor={factor:.6f}"
            )
            for item in items:
                g = item["group"]
                old = abs(float(g.get("growth_p_w", 0.0) or 0.0))
                new_val = old * factor
                g["growth_p_w"] = round(float(new_val), 6)
                item["growth"] = new_val
                rows.append(
                    f"  {side_name} {g.get('name')} uid={item['uid']}: growth_p_w {old:.6f} -> {new_val:.6f} "
                    f"({old*100:.2f}% -> {new_val*100:.2f}%)"
                )

        if normalize_to is not None:
            scale_side(left_items, left_sum, normalize_to, "LEFT")
            scale_side(right_items, right_sum, normalize_to, "RIGHT")
            left_sum = sum(item["growth"] for item in left_items)
            right_sum = sum(item["growth"] for item in right_items)
            diff = abs(left_sum - right_sum)
            rows.append("")
            rows.append("Після вирівнювання:")
            rows.append(f"SUM LEFT  = {left_sum:.6f} ({left_sum*100:.2f}%)")
            rows.append(f"SUM RIGHT = {right_sum:.6f} ({right_sum*100:.2f}%)")
            rows.append(f"DIFF      = {diff:.6f} ({diff*100:.2f}%)")

        rows.append("")
        rows.append("Застосування LEFT chain:")
        cumulative_left = 0.0
        for item in left_items:
            group = item["group"]
            uid = item["uid"]
            old_k = float(group.get("k_w", 0.0) or 0.0)
            own_growth = abs(float(group.get("growth_p_w", 0.0) or 0.0))
            new_k = cumulative_left

            group["k_w"] = round(float(new_k), 6)
            group["growth_p_w"] = round(float(own_growth), 6)
            group["growth_dir_x"] = "Вправо" if own_growth > 0.000001 else group.get("growth_dir_x", "Центр")
            group["link_x"] = "X = W"
            group["side_x"] = "left"
            group["auto_chain_x"] = True
            group["auto_chain_x_mode"] = "side_sum"
            group["chain_shift_x"] = round(float(new_k), 6)
            group["chain_growth_own_x"] = round(float(own_growth), 6)

            before = cumulative_left
            cumulative_left += own_growth
            group["chain_growth_after_x"] = round(float(cumulative_left), 6)
            group["side_sum_x"] = round(float(left_sum), 6)

            rows.append(
                f"  LEFT {group.get('name')} uid={uid}: "
                f"old_k_w={old_k:.6f} -> new_k_w=sum_from_left={new_k:.6f} ({new_k*100:.2f}%); "
                f"own_growth={own_growth:.6f} ({own_growth*100:.2f}%); "
                f"sum_before={before:.6f}; sum_after={cumulative_left:.6f}; dir={group.get('growth_dir_x')}"
            )

        rows.append("")
        rows.append("Застосування RIGHT chain:")
        cumulative_right = 0.0
        for item in right_items:
            group = item["group"]
            uid = item["uid"]
            old_k = float(group.get("k_w", 0.0) or 0.0)
            own_growth = abs(float(group.get("growth_p_w", 0.0) or 0.0))
            # Права сторона прив'язана до правого краю.
            # Найправіша група має k_w=1.0, а кожен внутрішній ріст справа зменшує k_w для наступних до центру.
            new_k = 1.0 - cumulative_right

            group["k_w"] = round(float(new_k), 6)
            group["growth_p_w"] = round(float(own_growth), 6)
            group["growth_dir_x"] = "Вліво" if own_growth > 0.000001 else group.get("growth_dir_x", "Центр")
            group["link_x"] = "X = W"
            group["side_x"] = "right"
            group["auto_chain_x"] = True
            group["auto_chain_x_mode"] = "side_sum"
            group["chain_shift_x"] = round(float(new_k), 6)
            group["chain_growth_own_x"] = round(float(own_growth), 6)

            before = cumulative_right
            cumulative_right += own_growth
            group["chain_growth_after_x"] = round(float(cumulative_right), 6)
            group["side_sum_x"] = round(float(right_sum), 6)

            rows.append(
                f"  RIGHT {group.get('name')} uid={uid}: "
                f"old_k_w={old_k:.6f} -> new_k_w=1-sum_from_right={new_k:.6f} ({new_k*100:.2f}%); "
                f"own_growth={own_growth:.6f} ({own_growth*100:.2f}%); "
                f"sum_before={before:.6f}; sum_after={cumulative_right:.6f}; dir={group.get('growth_dir_x')}"
            )

        rows.append("")
        rows.append("CENTER groups:")
        center_k = left_sum if diff <= balance_tolerance or normalize_to is not None else (left_sum + (1.0 - right_sum)) * 0.5
        for item in center_items:
            group = item["group"]
            old_k = float(group.get("k_w", 0.0) or 0.0)
            group["k_w"] = round(float(center_k), 6)
            group["link_x"] = "X = W"
            group["side_x"] = "center"
            group["auto_chain_x"] = True
            group["auto_chain_x_mode"] = "side_sum_center"
            group["chain_shift_x"] = round(float(center_k), 6)
            group["side_sum_left_x"] = round(float(left_sum), 6)
            group["side_sum_right_x"] = round(float(right_sum), 6)
            rows.append(
                f"  CENTER {group.get('name')} uid={item['uid']}: old_k_w={old_k:.6f} -> new_k_w={center_k:.6f} "
                f"({center_k*100:.2f}%). Це центральна зона між лівою і правою сторонами."
            )

        rows.append("")
        rows.append("ФІНАЛ:")
        rows.append(f"  LEFT total  = {left_sum:.6f} ({left_sum*100:.2f}%)")
        rows.append(f"  RIGHT total = {right_sum:.6f} ({right_sum*100:.2f}%)")
        rows.append(f"  DIFF        = {abs(left_sum-right_sum):.6f} ({abs(left_sum-right_sum)*100:.2f}%)")
        rows.append("  Ліві/праві групи можуть мати різні k_w, але сумарний % росту сторін контролюється.")

        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_viewer()
        self.topology_debug_print("AUTO CHAIN X SIDES / Авто сума росту X по сторонах", rows)

        if abs(left_sum - right_sum) <= balance_tolerance:
            self.lbl_status_calc.setText(
                f"<font color='#a5d6a7'>Авто сума X по сторонах застосована. LEFT=RIGHT={left_sum*100:.1f}%.</font>"
            )
        else:
            self.lbl_status_calc.setText(
                f"<font color='#ffcc80'>Авто сума X застосована з різними сторонами: LEFT={left_sum*100:.1f}%, RIGHT={right_sum*100:.1f}%.</font>"
            )

    def auto_detect_vertical_touch_constraints(self, tolerance=3.0):
        """
        TOUCH Y / Зберігати дотик Y.

        Що робить:
        1) очищає старі touch-зв'язки;
        2) сортує групи знизу вгору;
        3) для кожної нижньої групи шукає найближчу верхню групу;
        4) перевіряє, чи вони перетинаються по X, тобто реально стоять одна над одною;
        5) рахує gap = upper.minY - lower.maxY;
        6) якщо gap від 0 до tolerance, записує:
           lower.touch_y_enabled = True
           lower.touch_to_uid = upper.uid
           lower.touch_gap_y = gap

        Під час глобального перерахунку calculate_touch_extra_y_shifts() тримає цей gap.
        """
        valid_groups = [g for g in self.parametric_groups if self.group_original_bbox(g)]
        if len(valid_groups) < 2:
            self.lbl_status_calc.setText("<font color='red'>Потрібно мінімум дві групи для пошуку дотику.</font>")
            self.topology_debug_print("TOUCH Y: потрібно мінімум дві групи")
            return

        self.record_action_snapshot()
        rows = []
        rows.append("TOUCH Y / Зберігати дотик Y")
        rows.append(f"tolerance={tolerance:.3f} мм")
        rows.append("Сенс: якщо нижня група торкається верхньої або має малий зазор, програма запам'ятовує цей зазор.")
        rows.append("Потім при перерахунку верхня група додатково зсувається, щоб gap залишився такий самий.")
        rows.append("")

        for group in valid_groups:
            self.ensure_topology_fields(group)
            uid = self.get_group_key(group)
            old_enabled = group.get("touch_y_enabled")
            old_to = group.get("touch_to_uid")
            old_gap = group.get("touch_gap_y")
            group["touch_y_enabled"] = False
            group["touch_to_uid"] = None
            group["touch_gap_y"] = 0.0
            rows.append(f"Очистка старого touch: group={group.get('name')} uid={uid}; old_enabled={old_enabled}; old_to={old_to}; old_gap={old_gap}")

        sorted_groups = sorted(valid_groups, key=self.group_center_y)
        rows.append("")
        rows.append("Групи знизу вгору:")
        for i, group in enumerate(sorted_groups, start=1):
            bbox = self.group_original_bbox(group)
            rows.append(
                f"  #{i}: name={group.get('name')} uid={self.get_group_key(group)} "
                f"bbox=(minX={bbox[0]:.3f}, minY={bbox[1]:.3f}, maxX={bbox[2]:.3f}, maxY={bbox[3]:.3f})"
            )

        constraints_count = 0
        rows.append("")
        rows.append("Пошук найближчої верхньої групи для кожної нижньої:")

        for lower in sorted_groups:
            lower_uid = self.get_group_key(lower)
            lower_bbox = self.group_original_bbox(lower)
            best_upper = None
            best_gap = None

            rows.append(f"\nLOWER group={lower.get('name')} uid={lower_uid}; lower_top=maxY={lower_bbox[3]:.3f}")

            for upper in sorted_groups:
                if upper is lower:
                    continue
                upper_uid = self.get_group_key(upper)
                upper_bbox = self.group_original_bbox(upper)
                overlap_x = self.groups_overlap_by_x(lower_bbox, upper_bbox, tolerance=tolerance)
                gap = upper_bbox[1] - lower_bbox[3]

                if not overlap_x:
                    rows.append(
                        f"  candidate upper={upper.get('name')} uid={upper_uid}: SKIP, "
                        f"немає перетину по X; gap={gap:.3f}"
                    )
                    continue
                if gap < -tolerance:
                    rows.append(
                        f"  candidate upper={upper.get('name')} uid={upper_uid}: SKIP, "
                        f"накладання по Y більше tolerance; gap={gap:.3f}"
                    )
                    continue

                rows.append(
                    f"  candidate upper={upper.get('name')} uid={upper_uid}: OK candidate, "
                    f"overlap_x=True; gap=upper.minY({upper_bbox[1]:.3f}) - lower.maxY({lower_bbox[3]:.3f}) = {gap:.3f}"
                )

                if best_gap is None or gap < best_gap:
                    best_gap = gap
                    best_upper = upper

            if best_upper is not None and best_gap is not None and best_gap <= tolerance:
                upper_uid = self.get_group_key(best_upper)
                lower["touch_y_enabled"] = True
                lower["touch_to_uid"] = upper_uid
                lower["touch_gap_y"] = float(best_gap)
                constraints_count += 1
                rows.append(
                    f"  => TOUCH SAVED: lower={lower_uid} -> upper={upper_uid}; "
                    f"saved_gap_y={best_gap:.3f} мм"
                )
            else:
                rows.append("  => TOUCH NOT SAVED: немає верхньої групи в межах tolerance")

        rows.append("")
        rows.append(f"РЕЗУЛЬТАТ: знайдено touch-зв'язків Y = {constraints_count}")
        rows.append("Під час перерахунку буде лог [TOUCH DEBUG] START TOUCH Y CORRECTION — там видно корекцію у мм.")
        self.topology_debug_print("TOUCH Y / Зберігати дотик Y", rows)

        self.save_project_config()
        self.load_groups_into_list()
        self.update_viewer()
        self.lbl_status_calc.setText(
            f"<font color='#a5d6a7'>Знайдено вертикальних зв'язків дотику: {constraints_count}. Деталі дивись у консолі: [TOPOLOGY DEBUG] TOUCH Y.</font>"
        )

    # ============================================================
    # РУХОМИЙ ПОЧАТКОВИЙ TEXT / MTEXT
    # ============================================================
    def on_existing_dxf_text_moved(self, item):
        """
        Коли користувач перетягнув TEXT/MTEXT, який вже був у початковому DXF,
        ми оновлюємо insert у самому DXF і зберігаємо файл.
        """
        handle = getattr(item, "handle", None)
        if not handle or handle not in self.doc.entitydb:
            print(f"[TEXT MOVE DEBUG] handle={handle} не знайдено в DXF entitydb")
            return

        entity = self.doc.entitydb[handle]
        tp = entity.dxftype()
        pos = item.pos()
        old_insert = tuple(entity.dxf.insert) if hasattr(entity.dxf, "insert") else None

        # У сцені Y інвертований: CAD y = -scene_y - text_height.
        text_height = float(getattr(entity.dxf, "height", 10.0) or 10.0)
        new_x = float(pos.x())
        new_y = float(-pos.y() - text_height)

        if tp in ("TEXT", "MTEXT"):
            entity.dxf.insert = (new_x, new_y, 0.0)

        self.selected_handles = {handle}
        self.save_current_dxf()
        self.save_original_geometries()
        self.load_entities_into_list()
        self.sync_list_from_handles()
        self.save_project_config()

        print("\n" + "=" * 90)
        print("[TEXT MOVE DEBUG] Початковий текст DXF перетягнуто")
        print("=" * 90)
        print(f"handle={handle}; type={tp}")
        print(f"old_insert={old_insert}")
        print(f"scene_pos=(x={pos.x():.3f}, y={pos.y():.3f})")
        print(f"new_dxf_insert=(x={new_x:.3f}, y={new_y:.3f}, z=0.000)")
        print("Файл DXF збережено.")
        print("=" * 90 + "\n")

    # ============================================================
    # ДЗЕРКАЛЬНІ СТОРОНИ X З ПІДТВЕРДЖЕННЯМ КОНСТРУКТОРА
    # ============================================================
    def bbox_signature_for_mirror(self, bbox, axis_x):
        """
        Нормалізований підпис bbox відносно центральної осі.
        Для дзеркальних лівої/правої сторін відстані від осі мають збігатися.
        """
        min_x, min_y, max_x, max_y = bbox
        dist_near = min(abs(min_x - axis_x), abs(max_x - axis_x))
        dist_far = max(abs(min_x - axis_x), abs(max_x - axis_x))
        return (round(dist_near, 1), round(dist_far, 1), round(min_y, 1), round(max_y, 1))

    def find_mirror_x_group_pairs(self, tolerance=2.0):
        """
        Шукає пари груп, які виглядають як дзеркальні ліва/права сторона.
        Порівнюємо bbox відносно центральної осі конструкції.
        """
        min_x, min_y, max_x, max_y = self.get_non_text_dxf_bounds()
        if min_x is None:
            return None, []

        axis_x = (min_x + max_x) * 0.5
        valid = []
        for group in self.parametric_groups:
            bbox = self.group_original_bbox(group)
            if not bbox:
                continue
            self.ensure_topology_fields(group)
            uid = self.get_group_key(group)
            cx = (bbox[0] + bbox[2]) * 0.5
            side = "left" if cx < axis_x - tolerance else ("right" if cx > axis_x + tolerance else "center")
            valid.append({"group": group, "uid": uid, "bbox": bbox, "cx": cx, "side": side})

        left = [x for x in valid if x["side"] == "left"]
        right = [x for x in valid if x["side"] == "right"]
        pairs = []
        used_right = set()

        for l in left:
            l_sig = self.bbox_signature_for_mirror(l["bbox"], axis_x)
            best = None
            best_score = None
            for r in right:
                if r["uid"] in used_right:
                    continue
                r_sig = self.bbox_signature_for_mirror(r["bbox"], axis_x)
                score = sum(abs(a - b) for a, b in zip(l_sig, r_sig))
                if best is None or score < best_score:
                    best = r
                    best_score = score
            if best is not None and best_score is not None and best_score <= tolerance * 4:
                pairs.append((l, best, best_score))
                used_right.add(best["uid"])

        return axis_x, pairs

    def proposed_mirror_growth_value(self, left_group, right_group):
        """
        Якщо на одній стороні вже заданий ріст, копіюємо його на другу.
        Якщо на обох різний — беремо середнє і показуємо це в діалозі.
        """
        gl = abs(float(left_group.get("growth_p_w", 0.0) or 0.0))
        gr = abs(float(right_group.get("growth_p_w", 0.0) or 0.0))
        if gl > 0 and gr == 0:
            return gl, "взято ріст лівої сторони"
        if gr > 0 and gl == 0:
            return gr, "взято ріст правої сторони"
        if gl > 0 and gr > 0 and abs(gl - gr) > 0.000001:
            return (gl + gr) * 0.5, "обидві сторони мали різний ріст, взято середнє"
        return max(gl, gr), "обидві сторони вже однакові або ріст 0%"

    def confirm_and_apply_mirror_x_rules(self):
        """
        Перевіряє, чи ліва і права сторони дзеркальні.
        Якщо так — показує конструктору список знайдених пар і тільки після підтвердження
        прописує однаковий growth_p_w для обох сторін.
        """
        axis_x, pairs = self.find_mirror_x_group_pairs(tolerance=2.0)
        rows = []
        rows.append("MIRROR X / Дзеркальні сторони X")
        rows.append("Сенс: якщо ліва і права сторони однакові дзеркально, їм треба дати однаковий % розтягування.")
        rows.append("Перед записом правил програма питає підтвердження конструктора.")
        rows.append("")
        rows.append(f"axis_x={axis_x if axis_x is not None else 'None'}")
        rows.append(f"found_pairs={len(pairs)}")

        if axis_x is None or not pairs:
            self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows + ["РЕЗУЛЬТАТ: дзеркальних пар не знайдено."])
            self.lbl_status_calc.setText("<font color='red'>Дзеркальних ліво/право груп не знайдено.</font>")
            return

        message_lines = [
            "Знайдено дзеркальні ліво/право пари.",
            "Прописати їм однаковий відсоток розтягування по X?",
            "",
        ]

        proposals = []
        for i, (l, r, score) in enumerate(pairs, start=1):
            gval, reason = self.proposed_mirror_growth_value(l["group"], r["group"])
            proposals.append((l, r, gval, reason, score))
            line = (
                f"{i}) {l['group'].get('name')} ↔ {r['group'].get('name')}: "
                f"growth_p_w = {gval*100:.2f}% ({reason})"
            )
            message_lines.append(line)
            rows.append(
                f"pair#{i}: left={l['group'].get('name')} uid={l['uid']} bbox={tuple(round(v,3) for v in l['bbox'])}; "
                f"right={r['group'].get('name')} uid={r['uid']} bbox={tuple(round(v,3) for v in r['bbox'])}; "
                f"score={score:.3f}; proposed_growth={gval:.6f}; reason={reason}"
            )

        answer = QMessageBox.question(
            self,
            "Підтвердити дзеркальні правила X",
            "\n".join(message_lines),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            rows.append("КОНСТРУКТОР ВІДХИЛИВ: правила не записано.")
            self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows)
            self.lbl_status_calc.setText("<font color='#ffcc80'>Дзеркальні правила X не застосовано.</font>")
            return

        self.record_action_snapshot()
        rows.append("")
        rows.append("КОНСТРУКТОР ПІДТВЕРДИВ: записуємо однакове розтягування.")

        for l, r, gval, reason, score in proposals:
            lg = l["group"]
            rg = r["group"]
            old_l = float(lg.get("growth_p_w", 0.0) or 0.0)
            old_r = float(rg.get("growth_p_w", 0.0) or 0.0)

            lg["growth_p_w"] = round(float(gval), 6)
            rg["growth_p_w"] = round(float(gval), 6)
            lg["growth_dir_x"] = "Вліво"
            rg["growth_dir_x"] = "Вправо"
            lg["link_x"] = "X = W"
            rg["link_x"] = "X = W"
            lg["auto_mirror_x"] = True
            rg["auto_mirror_x"] = True
            lg["mirror_pair_uid"] = r["uid"]
            rg["mirror_pair_uid"] = l["uid"]

            rows.append(
                f"APPLY: {lg.get('name')} old_growth={old_l:.6f} -> {gval:.6f}, dir=Вліво; "
                f"{rg.get('name')} old_growth={old_r:.6f} -> {gval:.6f}, dir=Вправо"
            )

        self.save_project_config()
        self.load_groups_into_list()
        self.on_group_selection_changed()
        self.update_viewer()
        self.topology_debug_print("MIRROR X / Дзеркальні сторони X", rows)
        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Дзеркальні правила X застосовано для пар: {len(proposals)}.</font>")

    def calculate_touch_extra_y_shifts(self, cur_w, cur_h, target_w, target_h):
        """
        Повертає додатковий Y-зсув для груп, щоб зберегти початковий вертикальний дотик/зазор.
        Формат: {uid: extra_shift_y}.
        """
        uid_to_group = {}
        uid_to_bbox = {}
        extra = {}

        for group in self.parametric_groups:
            if not self.group_original_bbox(group):
                continue
            uid = self.get_group_key(group)
            uid_to_group[uid] = group
            bbox = self.simulated_group_bbox(group, cur_w, cur_h, target_w, target_h)
            if bbox:
                uid_to_bbox[uid] = list(bbox)
                extra[uid] = 0.0

        if len(uid_to_bbox) < 2:
            if self.debug_output:
                print("[TOUCH DEBUG] Not enough groups for touch correction")
            return extra

        if self.debug_output:
            print("\n" + "=" * 90)
            print("[TOUCH DEBUG] START TOUCH Y CORRECTION")
            for _uid, _bbox in uid_to_bbox.items():
                _g = uid_to_group[_uid]
                print(f"[TOUCH DEBUG] before uid={_uid}; name={_g.get('name')}; bbox={tuple(round(v,3) for v in _bbox)}; enabled={_g.get('touch_y_enabled')}; to={_g.get('touch_to_uid')}; gap={_g.get('touch_gap_y')}")

        # Проходимо знизу вгору, щоб верхні деталі піднімались/опускались разом з тими, до кого вони прив'язані.
        sorted_groups = sorted(uid_to_group.values(), key=self.group_center_y)
        for _ in range(max(1, len(sorted_groups))):
            changed = False
            for lower in sorted_groups:
                if not lower.get("touch_y_enabled"):
                    continue
                lower_uid = self.get_group_key(lower)
                upper_uid = lower.get("touch_to_uid")
                if lower_uid not in uid_to_bbox or upper_uid not in uid_to_bbox:
                    continue

                lower_bbox = uid_to_bbox[lower_uid]
                upper_bbox = uid_to_bbox[upper_uid]
                wanted_gap = float(lower.get("touch_gap_y", 0.0) or 0.0)
                wanted_upper_min_y = lower_bbox[3] + wanted_gap
                correction = wanted_upper_min_y - upper_bbox[1]

                if abs(correction) > 0.001:
                    if self.debug_output:
                        print(
                            f"[TOUCH DEBUG] lower={lower_uid} -> upper={upper_uid}; "
                            f"wanted_gap={wanted_gap:.3f}; lower_top={lower_bbox[3]:.3f}; "
                            f"upper_min_before={upper_bbox[1]:.3f}; correction={correction:.3f}"
                        )
                    uid_to_bbox[upper_uid][1] += correction
                    uid_to_bbox[upper_uid][3] += correction
                    extra[upper_uid] = extra.get(upper_uid, 0.0) + correction
                    changed = True
            if not changed:
                break

        if self.debug_output:
            print(f"[TOUCH DEBUG] extra result={extra}")
            print("=" * 90 + "\n")
        return extra

    def process_parametric_percentage_scale(self, save_result=True, record_history=True):
        try:
            cur_w = float(self.input_current_width.text().strip())
            target_w = float(self.input_target_width.text().strip())
            cur_h = float(self.input_current_height.text().strip())
            target_h = float(self.input_target_height.text().strip())
        except ValueError:
            return False

        self.collect_text_settings_from_inputs()
        if not self.validate_target_size_or_warn(cur_w, cur_h, target_w, target_h):
            return False

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
        if self.debug_output:
            print("\n" + "=" * 90)
            print("[RECALC DEBUG] START GLOBAL PARAMETRIC RECALC")
            print(f"[RECALC DEBUG] cur_w={cur_w}, target_w={target_w}, delta_w={delta_w}")
            print(f"[RECALC DEBUG] cur_h={cur_h}, target_h={target_h}, delta_h={delta_h}")
            print("[RECALC DEBUG] Groups:")
            for _g in self.parametric_groups:
                _uid = self.get_group_key(_g)
                print(
                    f"  uid={_uid}; name={_g.get('name')}; "
                    f"k_w={_g.get('k_w')}; growth_p_w={_g.get('growth_p_w')}; dir_x={_g.get('growth_dir_x')}; link_x={_g.get('link_x')}; "
                    f"k_h={_g.get('k_h')}; growth_p_h={_g.get('growth_p_h')}; dir_y={_g.get('growth_dir_y')}; link_y={_g.get('link_y')}; "
                    f"auto_chain_y={_g.get('auto_chain_y')}; chain_shift_y={_g.get('chain_shift_y')}; chain_growth_after_y={_g.get('chain_growth_after_y')}"
                )
        touch_extra_y = self.calculate_touch_extra_y_shifts(cur_w, cur_h, target_w, target_h)
        if self.debug_output:
            print(f"[RECALC DEBUG] touch_extra_y={touch_extra_y}")
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
            if self.debug_output:
                print(
                    f"[RECALC DEBUG] handle={hndl}; type={orig.get('type')}; "
                    f"group={associated_group.get('name')} uid={self.get_group_key(associated_group)}; "
                    f"base_shift=(x={shift_v[0]:.3f}, y={shift_v[1]:.3f}); "
                    f"growth=(x={growth_v[0]:.3f}, y={growth_v[1]:.3f}); "
                    f"k_w={associated_group.get('k_w')}; k_h={associated_group.get('k_h')}; "
                    f"shift_dir_x={associated_group.get('shift_dir_x')}; shift_dir_y={associated_group.get('shift_dir_y')}; "
                    f"growth_p_w={associated_group.get('growth_p_w')}; growth_p_h={associated_group.get('growth_p_h')}"
                )
           
            group_uid = self.get_group_key(associated_group)
            extra_y = touch_extra_y.get(group_uid, 0.0)
            if abs(extra_y) > 0.0001:
                if self.debug_output:
                    print(f"[RECALC DEBUG]   touch correction extra_y={extra_y:.3f} applied to group uid={group_uid}")
                shift_v = (shift_v[0], shift_v[1] + extra_y, shift_v[2])
            
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
            self.save_current_dxf()
        if not getattr(self, "suppress_project_config_save", False):
            self.save_project_config()
        if should_record:
            self.history.save_state()
            self.save_zones_history_state()
            self.global_recalc_redo_stack.clear()
            self.update_history_buttons_state()
        self.update_viewer()
        return True

    # def commit_current_geometry_as_parametric_base(self, reason="", update_source_dimensions=True, preserve_target_dimensions=True):
    #     """
    #     Робить поточну геометрію DXF новою базою для параметричного перерахунку.

    #     Навіщо:
    #     - preview/process_parametric_percentage_scale() не рахує від поточного DXF напряму;
    #     - він бере self.original_geometries як "початкову геометрію";
    #     - після ROT/MIRROR потрібно оновити self.original_geometries, інакше "Перегляд"
    #       застосує правила до геометрії ДО оберту.
    #     """
    #     old_source_w = self.project_meta.get("source_width")
    #     old_source_h = self.project_meta.get("source_height")
    #     old_target_w = self.project_meta.get("target_width")
    #     old_target_h = self.project_meta.get("target_height")

    #     self.save_original_geometries()

    #     if update_source_dimensions:
    #         new_w, new_h = self.get_dxf_bounds_dimensions()
    #         if new_w is not None and new_h is not None:
    #             self.project_meta["source_width"] = new_w
    #             self.project_meta["source_height"] = new_h

    #             # target_width/target_height не чіпаємо, якщо користувач уже задав новий розмір.
    #             # Але якщо target був порожній або дорівнював старому source, синхронізуємо з новою базою,
    #             # щоб після оберту поля не залишались у старій орієнтації.
    #             if not preserve_target_dimensions:
    #                 self.project_meta["target_width"] = new_w
    #                 self.project_meta["target_height"] = new_h
    #             else:
    #                 if old_target_w is None or (old_source_w is not None and abs(float(old_target_w) - float(old_source_w)) < 0.001):
    #                     self.project_meta["target_width"] = new_w
    #                 if old_target_h is None or (old_source_h is not None and abs(float(old_target_h) - float(old_source_h)) < 0.001):
    #                     self.project_meta["target_height"] = new_h

    #     print("\n" + "=" * 90)
    #     print("[BASE DEBUG] PARAMETRIC BASE UPDATED")
    #     print(f"[BASE DEBUG] reason={reason}")
    #     print(f"[BASE DEBUG] source before: W={old_source_w}, H={old_source_h}")
    #     print(f"[BASE DEBUG] source after : W={self.project_meta.get('source_width')}, H={self.project_meta.get('source_height')}")
    #     print(f"[BASE DEBUG] target after : W={self.project_meta.get('target_width')}, H={self.project_meta.get('target_height')}")
    #     print(f"[BASE DEBUG] original_geometries handles={len(self.original_geometries)}")
    #     print("=" * 90)

    #     self.update_dimension_inputs_from_meta()

    def commit_current_geometry_as_parametric_base(
        self,
        reason="",
        update_source_dimensions=False,
        preserve_target_dimensions=True
    ):
        """
        Робить поточну геометрію DXF новою базою для параметричного перерахунку,
        але НЕ міняє значення у полях ширини та висоти.
        """

        old_source_w = self.project_meta.get("source_width")
        old_source_h = self.project_meta.get("source_height")
        old_target_w = self.project_meta.get("target_width")
        old_target_h = self.project_meta.get("target_height")

        self.save_original_geometries()

        if self.debug_output:
            print("\n" + "=" * 90)
            print("[BASE DEBUG] PARAMETRIC BASE UPDATED")
            print(f"[BASE DEBUG] reason={reason}")
            print(f"[BASE DEBUG] source kept : W={old_source_w}, H={old_source_h}")
            print(f"[BASE DEBUG] target kept : W={old_target_w}, H={old_target_h}")
            print(f"[BASE DEBUG] original_geometries handles={len(self.original_geometries)}")
            print("=" * 90)


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
        self.save_current_dxf()
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
                        rest_g["shift_dir_x"] = cur_g.get("shift_dir_x", "Вправо")
                        rest_g["shift_dir_y"] = cur_g.get("shift_dir_y", "Вгору")
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
                        rest_g["shift_dir_x"] = cur_g.get("shift_dir_x", "Вправо")
                        rest_g["shift_dir_y"] = cur_g.get("shift_dir_y", "Вгору")
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
                               
                QTabWidget::pane {
                    border: 1px solid #3c3c3c;
                    background: #1e1e1e;
                    top: -1px; /* Прибирає подвійну рамку на стику */
                }
    
                /* Базовий стиль для всіх вкладок на панелі */
                QTabBar::tab {
                    background: #3c3c3c;
                    color: #fff;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    border: 1px solid #3c3c3c;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 40px;
                }

                /* Стиль вкладки, коли на неї наводять мишкою */
                QTabBar::tab:hover {
                    background: #2c3e50;
                    
                }

                /* Стиль строго для АКТИВНОЇ (обраної) вкладки */
               QTabBar::tab:selected {
                    background: #2c3e50;
                    color: #ffffff ;
                    font-weight: bold;
                    border-bottom: 2px solid #2ecc71; 
                }
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
                               
                 QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2d3748;
                margin-top: 12px; /* Відступ зверху для заголовка */
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                padding-top: 16px; /* Внутрішній відступ від заголовка до елементів */
            }

            /* Зсув заголовка з чекбоксом трохи вище та лівіше */
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }

            /* БАЗОВИЙ СТИЛЬ ЧЕКБОКСА всередині GroupBox */
            QGroupBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #cbd5e0;
                border-radius: 4px;
                background-color: #ffffff;
            }

            /* Стан при наведенні курсору */
            QGroupBox::indicator:hover {
                border-color: #3182ce;
                background-color: #f7fafc;
            }

            /* Стан, коли галочка ВСТАНОВЛЕНА (панель відкрита) */
            QGroupBox::indicator:checked {
                border-color: #3182ce;
                background-color: #3182ce;
                /* Вбудована SVG-галочка білого кольору */
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
            }

            /* Стан, коли галочка ЗНЯТА (панель згорнута) */
            QGroupBox::indicator:unchecked {
                border-color: #cbd5e0;
                background-color: #ffffff;
            }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #eef2f7; color: #fff}
                QWidget { background-color: #ffffff; color: #1f2933; font-size: 12px; }
                               
                               QTabWidget::pane {
                    border: 1px solid #e0e0e0;
                    background: #ffffff;
                    top: -1px; /* Прибирає подвійну рамку на стику */
                }
    
                /* Базовий стиль для всіх вкладок на панелі */
                QTabBar::tab {
                    background: #f8f9fa;
                    color: #2c3e50;
                     padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    border: 1px solid #e0e0e0;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    min-width: 80px;
                }

                /* Стиль вкладки, коли на неї наводять мишкою */
                QTabBar::tab:hover {
                    background: #eef2f7;
                    color: #2ecc71; /* Зелений колір тексту при наведенні */
                }

                /* Стиль строго для АКТИВНОЇ (обраної) вкладки */
                QTabBar::tab:selected {
                    background: #ffffff;
                    color: #2c3e50  ;
                    font-weight: bold;
                    border-bottom: 2px solid #2ecc71; 
                }
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
                QCheckBox {  spacing: 6px; }
                QCheckBox::indicator:unchecked {
                    background-color: #ffffff;
                    border: 1px solid #1e1e1e;
                }
 
                QCheckBox::indicator:checked { background-color: #0b5cad; border: 1px solid #0b5cad; }
                QScrollBar:vertical { background: #f1f5f9; width: 12px; }
                QScrollBar::handle:vertical { background: #b8c4d4; border-radius: 5px; min-height: 24px; }
                               
                 QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2d3748;
                margin-top: 12px; /* Відступ зверху для заголовка */
                border: 1px solid #cbd5e0;
                border-radius: 6px;
                padding-top: 16px; /* Внутрішній відступ від заголовка до елементів */
            }

            /* Зсув заголовка з чекбоксом трохи вище та лівіше */
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }

            /* БАЗОВИЙ СТИЛЬ ЧЕКБОКСА всередині GroupBox */
            QGroupBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #cbd5e0;
                border-radius: 4px;
                background-color: #ffffff;
            }

            /* Стан при наведенні курсору */
            QGroupBox::indicator:hover {
                border-color: #3182ce;
                background-color: #f7fafc;
            }

            /* Стан, коли галочка ВСТАНОВЛЕНА (панель відкрита) */
            QGroupBox::indicator:checked {
                border-color: #3182ce;
                background-color: #3182ce;
                /* Вбудована SVG-галочка білого кольору */
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://w3.org' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
            }

            /* Стан, коли галочка ЗНЯТА (панель згорнута) */
            QGroupBox::indicator:unchecked {
                border-color: #cbd5e0;
                background-color: #ffffff;
            }
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
            self.sync_list_from_handles()
            self.update_viewer()
            return

        group_idx = self.group_index_for_handle(handle)
        if group_idx is not None:
            self.select_group_by_index(group_idx)
            return

        self.group_list_widget.clearSelection()
        self.selected_handles = {handle}
        self.sync_list_from_handles()
        self.update_viewer()

    def group_index_for_handle(self, handle):
        handle = str(handle)
        for idx, group in enumerate(self.parametric_groups):
            if handle in {str(h) for h in group.get("handles", set())}:
                return idx
        return None

    def select_group_by_index(self, idx):
        if idx < 0 or idx >= self.group_list_widget.count():
            return
        self.group_list_widget.setCurrentRow(idx)
        group = self.parametric_groups[idx]
        self.selected_handles = set(group.get("handles", set()))
        self.sync_list_from_handles()
        self.update_viewer()

    def update_history_buttons_state(self):
        can_undo_history = len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1
        can_redo_history = len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0
        self.btn_undo.setEnabled(bool(self.global_recalc_undo_stack) or can_undo_history)
        self.btn_redo.setEnabled(bool(self.global_recalc_redo_stack) or can_redo_history)

    def reload_after_history_change(self):
        self.is_loading_history = True
        if not self.is_db_file_open():
            self.doc = ezdxf.readfile(self.dxf_path)
        self.save_original_geometries()
        self.update_dimension_inputs_from_meta()
        self.load_groups_into_list()
        self.load_entities_into_list()
        self.update_history_buttons_state()
        self.is_loading_history = False

    def populate_db_model_tree(self):
        models = self.db.list_door_models()
        if not models:
            return False

        current_item = None
        for model in models:
            selected_model_id = getattr(self, "selected_db_model_id", None)
            if selected_model_id is not None and model.get("id") != selected_model_id:
                continue

            model_name = model.get("model_name") or f"Model {model.get('id')}"
            width = model.get("source_width")
            height = model.get("source_height")
            size_text = ""
            if width is not None and height is not None:
                size_text = f" [{self.format_dimension_value(width)}x{self.format_dimension_value(height)}]"

            model_item = QTreeWidgetItem([f"Модель {model_name}{size_text} ({model.get('file_count', 0)})"])
            model_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "model", **model})
            self.file_explorer_list.addTopLevelItem(model_item)

            for record in self.db.get_model_files(model.get("id")):
                file_name = record.get("file_name") or f"DB file {record.get('id')}"
                status = record.get("status") or ""
                size = record.get("file_data_size")
                size_text = f" [{size} b]" if size is not None else ""
                child = QTreeWidgetItem([f"DXF {file_name} {status}{size_text}".strip()])
                child.setData(0, Qt.ItemDataRole.UserRole, {"type": "db_file", **record})
                model_item.addChild(child)
                if record.get("id") == self.current_project_file_id:
                    current_item = child

            if model.get("id") == self.current_door_model_id:
                model_item.setExpanded(True)

        if self.file_explorer_list.topLevelItemCount() == 0:
            return False

        if current_item is not None:
            parent = current_item.parent()
            if parent is not None:
                parent.setExpanded(True)
            self.file_explorer_list.setCurrentItem(current_item)
        else:
            self.file_explorer_list.expandToDepth(0)
        return True

    def populate_local_file_tree(self):
        if self.is_db_uri(getattr(self, "project_dir", "")):
            return False
        files = os.listdir(self.project_dir)
        dxf_files = [f for f in files if f.lower().endswith('.dxf')]
        for file_name in dxf_files:
            item = QTreeWidgetItem([f"DXF {file_name}"])
            item.setData(0, Qt.ItemDataRole.UserRole, file_name)
            self.file_explorer_list.addTopLevelItem(item)
            if file_name.lower() == os.path.basename(self.dxf_path).lower():
                self.file_explorer_list.setCurrentItem(item)
        return True

    def scan_project_folder_for_dxf(self):
        self.file_explorer_list.blockSignals(True)
        self.file_explorer_list.clear()
        try:
            if self.db_opening_enabled() and self.populate_db_model_tree():
                self.file_explorer_list.blockSignals(False)
                return

            if self.db_opening_enabled():
                db_files = self.db.list_project_files()
                if db_files:
                    for record in db_files:
                        file_name = record.get("file_name") or f"DB file {record.get('id')}"
                        status = record.get("status") or ""
                        data_mark = "data" if record.get("has_file_data", True) else "no data"
                        item = QTreeWidgetItem([f"DB {file_name} {status} {data_mark}".strip()])
                        item.setData(0, Qt.ItemDataRole.UserRole, {"type": "db_file", **record})
                        self.file_explorer_list.addTopLevelItem(item)
                        if record.get("id") == self.current_project_file_id:
                            self.file_explorer_list.setCurrentItem(item)
                    self.file_explorer_list.blockSignals(False)
                    return

            if self.populate_local_file_tree():
                self.file_explorer_list.blockSignals(False)
                return

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
        first_data = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if isinstance(first_data, dict):
            if first_data.get("type") == "model":
                selected_items[0].setExpanded(not selected_items[0].isExpanded())
                return
            self.open_dxf_from_db_record(first_data)
            return
        self.selected_handles.clear()
        self.parametric_groups.clear()
        base_file_name = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        self.current_project_file_id = None
        self.current_db_file_name = None
        self.dxf_path = os.path.join(self.project_dir, base_file_name)
        self.doc = ezdxf.readfile(self.dxf_path)

        if len(selected_items) > 1:
            for item in selected_items[1:]:
                addon_file_name = item.data(0, Qt.ItemDataRole.UserRole)
                addon_path = os.path.join(self.project_dir, addon_file_name)
                if os.path.exists(addon_path):
                    try:
                        addon_doc = ezdxf.readfile(addon_path)
                        importer = Importer(addon_doc, self.doc)
                        importer.import_modelspace()
                        importer.finalize()
                    except Exception as e: print(f"Помилка злиття: {e}")

        self.load_project_config()
        self.prompt_source_dimensions_on_open()
        self.register_current_folder_model(show_errors=False)
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
                sa = float(entity.dxf.start_angle)
                ea = float(entity.dxf.end_angle)

                arc_key = (
                    round(cx, 2),
                    round(cy, 2),
                    round(r, 2),
                    round(sa, 2),
                    round(ea, 2),
                )

                if arc_key in seen:
                    continue

                seen.add(arc_key)

                text = (
                    f"🌙 Дуга (ID: {hndl}) "
                    f"Центр X:{cx:.1f}, Y:{cy:.1f}, "
                    f"R:{r:.1f}, Кути: {sa:.1f}° → {ea:.1f}°"
                )
            # elif tp == "ARC":
            #     cx, cy, _ = entity.dxf.center
            #     r = entity.dxf.radius
            #     if (round(cx, 1), round(cy, 1), round(r, 1)) in seen: continue
            #     seen.add((round(cx, 1), round(cy, 1), round(r, 1)))
            #     text = f"🌙 Дуга (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}, R:{r:.1f}"
            elif tp == "TEXT":
                x, y, _ = entity.dxf.insert
                label = entity.dxf.text.strip() or "[рамка тексту]"
                text = f"Текст (ID: {hndl}) \"{label}\" X:{x:.1f}, Y:{y:.1f}, H:{entity.dxf.height:.1f}"
            else: continue
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, str(hndl))
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

            elif tp in ("TEXT", "MTEXT"):
                settings = self.get_text_settings()
                entity_text = getattr(entity.dxf, "text", "") if tp == "TEXT" else getattr(entity, "text", "")
                display_text = self.text_display_value(settings.get("text", entity_text))
                if settings.get("handle") == hndl:
                    # Наш керований текстовий блок: лишається рамкою, яку можна рухати.
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
                    if tp == "TEXT":
                        display_text = entity.dxf.text.strip() or " "
                        text_height = float(entity.dxf.height)
                    else:
                        display_text = str(getattr(entity, "text", "") or getattr(entity.dxf, "text", "") or " ").strip() or " "
                        text_height = float(getattr(entity.dxf, "char_height", 10.0) or getattr(entity.dxf, "height", 10.0) or 10.0)
                    pyqt_item = DraggableDxfTextItem(display_text, self, hndl, tp)
                    pyqt_item.setDefaultTextColor(QColor(0, 120, 255) if hndl in self.selected_handles else base_line_color)
                    font = pyqt_item.font()
                    font.setPointSizeF(max(text_height, 1.0))
                    pyqt_item.setFont(font)
                    pyqt_item.setPos(x, -y - text_height)
                    pyqt_item.setRotation(-float(getattr(entity.dxf, "rotation", 0.0)))
                pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
                self.overlay_items[hndl] = pyqt_item
                self.scene.addItem(pyqt_item) if pyqt_item.scene() is None else None
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

