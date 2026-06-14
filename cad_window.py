# # # # # # # # # # # # # # # # import os
# # # # # # # # # # # # # # # # import sys
# # # # # # # # # # # # # # # # import math

# # # # # # # # # # # # # # # # import ezdxf
# # # # # # # # # # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж без крашів

# # # # # # # # # # # # # # # # from PyQt5.QtWidgets import (
# # # # # # # # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # # # # # # # #     QGroupBox, QGraphicsRectItem
# # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # from PyQt5.QtCore import Qt
# # # # # # # # # # # # # # # # from PyQt5.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # # # # # # # # Обов'язкові імпорти ваших кастомних модулів:
# # # # # # # # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # # # # # # # from graphics_view import AdvancedGraphicsView


# # # # # # # # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # # # # # # # #     def __init__(self):
# # # # # # # # # # # # # # # #         super().__init__()

# # # # # # # # # # # # # # # #         self.setWindowTitle("CAD Двері: 2D Багатозонний Параметризатор (X та Y)")
# # # # # # # # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # # # # # # # #         self.dxf_path = "drawing.DXF"

# # # # # # # # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # # # # # #         # Списки для ручного розподілу елементів по жорстких зонах фіксації
# # # # # # # # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # # # # # # # # #         # Формат: {'min': float, 'max': float, 'stretch_val': float, 'axis': 'X' або 'Y'}
# # # # # # # # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # # # # # # # #             sys.exit()

# # # # # # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # # # # # # # #         self.init_ui()
# # # # # # # # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     def init_ui(self):
# # # # # # # # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # # # # # # # #         # Графічна сцена та в'ювер
# # # # # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # # # # # # # #         self.view.setRenderHint(QPainter.Antialiasing)
# # # # # # # # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # # # # # # # #         # Права бічна панель управління
# # # # # # # # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # # # # # # # #         # Фіксація по горизонталі (X)
# # # # # # # # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("background-color: #e8f5e9; font-weight: bold;")
# # # # # # # # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("background-color: #ffebee; font-weight: bold;")
# # # # # # # # # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # # # # # # # #         # Фіксація по вертикалі (Y)
# # # # # # # # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
# # # # # # # # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡 Верхній блок (Y)")
# # # # # # # # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("background-color: #fffde7; font-weight: bold;")
# # # # # # # # # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # # # # # # # # #         # Список створених параметричних прямокутників деформації полотна
# # # # # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # # # # # # # #         # Список елементів креслення
# # # # # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
# # # # # # # # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # # # # # # # #         # Панель управління повзунком
# # # # # # # # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # # # # # # # #         self.slider = QSlider(Qt.Horizontal)
# # # # # # # # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     # ЛОГІКА КНОПОК ФІКСАЦІЇ СТОРІН
# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     # СТВОРЕННЯ МНОЖИННИХ ЗОН ТА ПРЯМОКУТНИКІВ
# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # # # # # # # #         """Збирає координати виділених рамкою деталей та створює кольорову зону розтягування."""
# # # # # # # # # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # # # # # # # # #             return

# # # # # # # # # # # # # # # #         coords = []
# # # # # # # # # # # # # # # #         for hndl in self.selected_handles:
# # # # # # # # # # # # # # # #             if hndl in self.original_geometries:
# # # # # # # # # # # # # # # #                 orig = self.original_geometries[hndl]
# # # # # # # # # # # # # # # #                 if axis == 'X':
# # # # # # # # # # # # # # # #                     if orig["type"] == "CIRCLE": coords.append(orig["center"][0])
# # # # # # # # # # # # # # # #                     elif orig["type"] == "LINE": coords.extend([orig["start"][0], orig["end"][0]])
# # # # # # # # # # # # # # # #                 elif axis == 'Y':
# # # # # # # # # # # # # # # #                     if orig["type"] == "CIRCLE": coords.append(orig["center"][1])
# # # # # # # # # # # # # # # #                     elif orig["type"] == "LINE": coords.extend([orig["start"][1], orig["end"][1]])

# # # # # # # # # # # # # # # #         if not coords: return

# # # # # # # # # # # # # # # #         min_val, max_val = min(coords), max(coords)

# # # # # # # # # # # # # # # #         # Перевірка на дублікати
# # # # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_val) < 5.0 and abs(zone['max'] - max_val) < 5.0:
# # # # # # # # # # # # # # # #                 return

# # # # # # # # # # # # # # # #         new_zone = {
# # # # # # # # # # # # # # # #             'min': min_val,
# # # # # # # # # # # # # # # #             'max': max_val,
# # # # # # # # # # # # # # # #             'stretch_val': 0.0,
# # # # # # # # # # # # # # # #             'axis': axis
# # # # # # # # # # # # # # # #         }
# # # # # # # # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # # # # # # # #         # Сортуємо зони окремо для правильної каскадної математики зсуву
# # # # # # # # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))

# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # # # #         self.clear_selection()

# # # # # # # # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # # # # # # # #             text = f"{axis_icon} Зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # # # # #             item.setData(Qt.UserRole, idx)
# # # # # # # # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # # # # # # # #         if not selected:
# # # # # # # # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # # # # # # # #             return

# # # # # # # # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.UserRole)
# # # # # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # # # # # # # #             return

# # # # # # # # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # # # # # # # #         # Перераховуємо 2D координати для всього креслення полотна дверей
# # # # # # # # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # #         Універсальна каскадна функція для X та Y.
# # # # # # # # # # # # # # # #         Розраховує зміщення точки на основі приналежності до зафіксованих блоків дверей 
# # # # # # # # # # # # # # # #         та проходження через прямокутники розтягування.
# # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # #         # Перевірка жорстких фіксованих користувачем блоків фурнітури
# # # # # # # # # # # # # # # #         if axis == 'X':
# # # # # # # # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # # # # # # # #                 # Зміщується монолітом на суму розширень усіх зон по осі X
# # # # # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # # # # # # # #         elif axis == 'Y':
# # # # # # # # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # # # # # # # #                 # Зміщується монолітом на суму розширень усіх зон по осі Y
# # # # # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # # # # # # # #         # Геометричний каскадний прорахунок зон деформації простору
# # # # # # # # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # # # # # # # #             z_min = zone['min']
# # # # # # # # # # # # # # # #             z_max = zone['max']
# # # # # # # # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # # # # # # # #                 shifted_val += val
# # # # # # # # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # # # # # # # #                 if width > 0:
# # # # # # # # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # # # # # # # #         return shifted_val

# # # # # # # # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # # # # # # # #         self.doc.saveas(self.dxf_path)
# # # # # # # # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # # # # # # # #         # Перераховуємо і заморожуємо кастомні координати прямокутників на сцені
# # # # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # # # #             zone['min'] = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # # # # #             zone['max'] = self.calculate_cascade_shift(zone['max'], zone['axis'], None)
# # # # # # # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     # ВІЗУАЛІЗАЦІЯ 2D ЗОН (ЗАМАЛЬОВУВАННЯ ГРАФІЧНИХ КВАДРАТІВ)
# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     def update_viewer(self):
# # # # # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # # # # # # # #         # Визначаємо загальні габарити для правильного замальовування фонових прямокутників
# # # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # # # # # # # #         except Exception:
# # # # # # # # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # # # # # # # #         # 1. МАЛЮЄМО НАПІВПРОЗОРІ КОЛЬОРОВІ КВАДРАТИ / ПРЯМОКУТНИКИ РОЗТЯГУВАННЯ
# # # # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # # # # #             disp_max = disp_min + (zone['max'] - zone['min']) + zone['stretch_val']

# # # # # # # # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # # # # # # # #                 # Вертикальна смуга розтягування (Зміна ширини дверей)
# # # # # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # #                 # Горизонтальна смуга розтягування (Зміна висоти дверей)
# # # # # # # # # # # # # # # #                 # У Qt вісь Y направлена вниз, тому інвертуємо для відображення DXF
# # # # # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # # # # # # # #             # Підсвічування активного прямокутника
# # # # # # # # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # # # # # # # #                 rect_item.setPen(QPen(color.darker(), 1.5, Qt.DashLine))
# # # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.DotLine))
                
# # # # # # # # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # # # # # # # #         # 2. ОТРИСОВКА ГЕОМЕТРІЇ КРЕСЛЕННЯ
# # # # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # # # #             pyqt_item = None

# # # # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # # # # # # # #             if pyqt_item:
# # # # # # # # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
# # # # # # # # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # # # # # # # #                 # Кольорова диференціація зафіксованих елементів у списку
# # # # # # # # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.SolidLine))
# # # # # # # # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # # #                 else: pyqt_item.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))

# # # # # # # # # # # # # # # #                 pyqt_item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # # # # # # # #                 }
# # # # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # # # # # # # #                 }

# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     # СИНХРОНІЗАЦІЯ І СЛУЖБОВІ МЕТОДИ
# # # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # # # #         path = QPainterPath()
# # # # # # # # # # # # # # # #         path.addRect(rect)
# # # # # # # # # # # # # # # #         matched_items = self.scene.items(path, Qt.IntersectsItemShape)
# # # # # # # # # # # # # # # #         for item in matched_items:
# # # # # # # # # # # # # # # #             hndl = item.data(Qt.UserRole)
# # # # # # # # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # # # # # # # #             if item.data(Qt.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # # # # # # # #             self.selected_handles.add(item.data(Qt.UserRole))
# # # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # # #     def clear_selection(self):
# # # # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # # # # # # # #         seen = set()
# # # # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ ФІКС] "
# # # # # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ ФІКС] "
# # # # # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ ФІКС] "
# # # # # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ ФІКС] "
# # # # # # # # # # # # # # # #                 else: prefix = "🔘 "
# # # # # # # # # # # # # # # #                 text = f"{prefix}Отвір (ID: {hndl}) X:{cx:.0f}, Y:{cy:.0f}"
# # # # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # # # # # # #                 text = f"📏 Лінія (ID: {hndl}) X: {x1:.0f} -> {x2:.0f}"
# # # # # # # # # # # # # # # #             else: continue
# # # # # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # # # # #             item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # # # # #             self.entity_list.addItem(item)
# # # # # # # # # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # # # # # # # #     import PyQt5.QtWidgets as qtw
# # # # # # # # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # # # # # # # #     window = MiniCAD()
# # # # # # # # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# # # # # # # # # # # # # # # #     window.show()
# # # # # # # # # # # # # # # #     sys.exit(app.exec_())


# # # # # # # # # # # # # # # import os
# # # # # # # # # # # # # # # import sys
# # # # # # # # # # # # # # # import math

# # # # # # # # # # # # # # # import ezdxf
# # # # # # # # # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж без крашів

# # # # # # # # # # # # # # # from PyQt5.QtWidgets import (
# # # # # # # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # # # # # # #     QGroupBox, QGraphicsRectItem
# # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # from PyQt5.QtCore import Qt
# # # # # # # # # # # # # # # from PyQt5.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # # # # # # # Обов'язкові імпорти ваших кастомних модулів:
# # # # # # # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # # # # # # from graphics_view import AdvancedGraphicsView


# # # # # # # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # # # # # # #     def __init__(self):
# # # # # # # # # # # # # # #         super().__init__()

# # # # # # # # # # # # # # #         self.setWindowTitle("CAD Двері: Розумна автогенерація зон розтягування")
# # # # # # # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # # # # # # #         self.dxf_path = "drawing.DXF"

# # # # # # # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # # # # #         # Списки для ручного розподілу елементів по жорстких зонах фіксації
# # # # # # # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # # # # # # # #         # Формат: [{'min': float, 'max': float, 'stretch_val': float, 'axis': 'X' або 'Y'}]
# # # # # # # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # # # # # # #             sys.exit()

# # # # # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # # # # # # #         self.init_ui()
# # # # # # # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     def init_ui(self):
# # # # # # # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # # # # # # #         # Графічна сцена та в'ювер
# # # # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # # # # # # #         self.view.setRenderHint(QPainter.Antialiasing)
# # # # # # # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # # # # # # #         # Права бічна панель управління
# # # # # # # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # # # # # # #         # Фіксація по горизонталі (X)
# # # # # # # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("background-color: #e8f5e9; font-weight: bold;")
# # # # # # # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("background-color: #ffebee; font-weight: bold;")
# # # # # # # # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # # # # # # #         # Фіксація по вертикалі (Y)
# # # # # # # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
# # # # # # # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("background-color: #fffde7; font-weight: bold;")
# # # # # # # # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # # # # # # #         control_layout.addWidget(zone_group)


# # # # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # # # # # # #         # Список елементів креслення
# # # # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
# # # # # # # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # # # # # # #         # Панель управління повзунком
# # # # # # # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # # # # # # #         self.slider = QSlider(Qt.Horizontal)
# # # # # # # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     # МОДИФІКОВАНА ЛОГІКА АВТОМАТИЧНОГО ВИЗНАЧЕННЯ ПРОСТОРУ
# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # #         self.auto_detect_between_zone('X')  # Автоперевірка простору між X блоками
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # #         self.auto_detect_between_zone('X')  # Автоперевірка простору між X блоками
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # #         self.auto_detect_between_zone('Y')  # Автоперевірка простору між Y блоками
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # # #         self.auto_detect_between_zone('Y')  # Автоперевірка простору між Y блоками
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # #         НОВА ФУНКЦІЯ: Автоматично знаходить порожнечу (білий квадрат) між протилежними 
# # # # # # # # # # # # # # #         зафіксованими блоками фурнітури та реєструє її як готову зону розтягування.
# # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
           
# # # # # # # # # # # # # # #             max_left_x = -float('inf')
# # # # # # # # # # # # # # #             for h in self.left_fixed_handles:
# # # # # # # # # # # # # # #                 if h in self.original_geometries:
# # # # # # # # # # # # # # #                     orig = self.original_geometries[h]
# # # # # # # # # # # # # # #                     x = orig["center"][0] if orig["type"] == "CIRCLE" else max(orig["start"][0], orig["end"][0])
# # # # # # # # # # # # # # #                     max_left_x = max(max_left_x, x)

# # # # # # # # # # # # # # #             # Шукаємо найлівішу точку правого блоку
# # # # # # # # # # # # # # #             min_right_x = float('inf')
# # # # # # # # # # # # # # #             for h in self.right_fixed_handles:
# # # # # # # # # # # # # # #                 if h in self.original_geometries:
# # # # # # # # # # # # # # #                     orig = self.original_geometries[h]
# # # # # # # # # # # # # # #                     x = orig["center"][0] if orig["type"] == "CIRCLE" else min(orig["start"][0], orig["end"][0])
# # # # # # # # # # # # # # #                     min_right_x = min(min_right_x, x)

# # # # # # # # # # # # # # #             # Якщо між ними є фізичний простір, створюємо зону авто-стрейчу
# # # # # # # # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x, min_right_x, 'X')

# # # # # # # # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # # # # # # # #             # Шукаємо найвищу точку нижнього блоку
# # # # # # # # # # # # # # #             max_bottom_y = -float('inf')
# # # # # # # # # # # # # # #             for h in self.bottom_fixed_handles:
# # # # # # # # # # # # # # #                 if h in self.original_geometries:
# # # # # # # # # # # # # # #                     orig = self.original_geometries[h]
# # # # # # # # # # # # # # #                     y = orig["center"][1] if orig["type"] == "CIRCLE" else max(orig["start"][1], orig["end"][1])
# # # # # # # # # # # # # # #                     max_bottom_y = max(max_bottom_y, y)

# # # # # # # # # # # # # # #             # Шукаємо найнижчу точку верхнього блоку
# # # # # # # # # # # # # # #             min_top_y = float('inf')
# # # # # # # # # # # # # # #             for h in self.top_fixed_handles:
# # # # # # # # # # # # # # #                 if h in self.original_geometries:
# # # # # # # # # # # # # # #                     orig = self.original_geometries[h]
# # # # # # # # # # # # # # #                     y = orig["center"][1] if orig["type"] == "CIRCLE" else min(orig["start"][1], orig["end"][1])
# # # # # # # # # # # # # # #                     min_top_y = min(min_top_y, y)

# # # # # # # # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # # # # # # # #         """Допоміжний метод додавання та автоматичного фокусування на створеній авто-зоні."""
# # # # # # # # # # # # # # #         # Перевіряємо, чи така зона вже була додана раніше
# # # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # # # # # # # #                 return

# # # # # # # # # # # # # # #         new_zone = {
# # # # # # # # # # # # # # #             'min': min_v,
# # # # # # # # # # # # # # #             'max': max_v,
# # # # # # # # # # # # # # #             'stretch_val': 0.0,
# # # # # # # # # # # # # # #             'axis': axis
# # # # # # # # # # # # # # #         }
# # # # # # # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        
# # # # # # # # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # # # # # # # #         # Автоматично підсвічуємо щойно створену авто-зону у списку, щоб користувач міг відразу її тягнути
# # # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # # # # # # # #                 break

# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     # СТВОРЕННЯ МНОЖИННИХ ЗОН ВРУЧНУ
# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # # # # # # # #             return

# # # # # # # # # # # # # # #         coords = []
# # # # # # # # # # # # # # #         for hndl in self.selected_handles:
# # # # # # # # # # # # # # #             if hndl in self.original_geometries:
# # # # # # # # # # # # # # #                 orig = self.original_geometries[hndl]
# # # # # # # # # # # # # # #                 if axis == 'X':
# # # # # # # # # # # # # # #                     if orig["type"] == "CIRCLE": coords.append(orig["center"][0])
# # # # # # # # # # # # # # #                     elif orig["type"] == "LINE": coords.extend([orig["start"][0], orig["end"][0]])
# # # # # # # # # # # # # # #                 elif axis == 'Y':
# # # # # # # # # # # # # # #                     if orig["type"] == "CIRCLE": coords.append(orig["center"][1])
# # # # # # # # # # # # # # #                     elif orig["type"] == "LINE": coords.extend([orig["start"][1], orig["end"][1]])

# # # # # # # # # # # # # # #         if not coords: return
# # # # # # # # # # # # # # #         min_val, max_val = min(coords), max(coords)
# # # # # # # # # # # # # # #         self.add_or_update_zone_bounds(min_val, max_val, axis)
# # # # # # # # # # # # # # #         self.clear_selection()

# # # # # # # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # # # #             item.setData(Qt.UserRole, idx)
# # # # # # # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # # # # # # #     def zone_index_from_idx(self, idx):
# # # # # # # # # # # # # # #         return idx

# # # # # # # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # # # # # # #         if not selected:
# # # # # # # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # # # # # # #             return

# # # # # # # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.UserRole)
# # # # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # # # # # # #             return

# # # # # # # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # # # # # # #             z_min = zone['min']
# # # # # # # # # # # # # # #             z_max = zone['max']
# # # # # # # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # # # # # # #                 shifted_val += val
# # # # # # # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # # # # # # #                 if width > 0:
# # # # # # # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # # # # # # #         return shifted_val

# # # # # # # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # # # # # # #         self.doc.saveas(self.dxf_path)
# # # # # # # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # # #             zone['min'] = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # # # #             zone['max'] = self.calculate_cascade_shift(zone['max'], zone['axis'], None)
# # # # # # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     # ВІЗУАЛІЗАЦІЯ 2D ЗОН (ЗАМАЛЬОВУВАННЯ ГРАФІЧНИХ КВАДРАТІВ)
# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     def update_viewer(self):
# # # # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # # # # # # #         except Exception:
# # # # # # # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # # # # # # #         # 1. МАЛЮЄМО НАПІВПРОЗОРІ КОЛЬОРОВІ КВАДРАТИ / ПРЯМОКУТНИКИ РОЗТЯГУВАННЯ
# # # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # # # #             disp_max = disp_min + (zone['max'] - zone['min']) + zone['stretch_val']

# # # # # # # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # # # # # # #                 rect_item.setPen(QPen(color.darker(), 1.5, Qt.DashLine))
# # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.DotLine))
                
# # # # # # # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # # # # # # #         # 2. ОТРИСОВКА ГЕОМЕТРІЇ КРЕСЛЕННЯ
# # # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # # #             pyqt_item = None

# # # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # # # # # # #             if pyqt_item:
# # # # # # # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
# # # # # # # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.SolidLine))
# # # # # # # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # # #                 else: pyqt_item.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))

# # # # # # # # # # # # # # #                 pyqt_item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # # # # # # #                 }
# # # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # # # # # # #                 }

# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     # СИНХРОНІЗАЦІЯ І СЛУЖБОВІ МЕТОДИ
# # # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # # #         path = QPainterPath()
# # # # # # # # # # # # # # #         path.addRect(rect)
# # # # # # # # # # # # # # #         matched_items = self.scene.items(path, Qt.IntersectsItemShape)
# # # # # # # # # # # # # # #         for item in matched_items:
# # # # # # # # # # # # # # #             hndl = item.data(Qt.UserRole)
# # # # # # # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # # # # # # #             if item.data(Qt.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # # # # # # #             self.selected_handles.add(item.data(Qt.UserRole))
# # # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # # #     def clear_selection(self):
# # # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # # # # # # #         seen = set()
        
# # # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # # # # # # # #             # Отримання базових метаданих CAD (спільних для всіх фігур)
# # # # # # # # # # # # # # #             layer = entity.dxf.layer if entity.has_dxf_attrib('layer') else "Default"
# # # # # # # # # # # # # # #             color_index = entity.dxf.color if entity.has_dxf_attrib('color') else "ByLayer"
# # # # # # # # # # # # # # #             linetype = entity.dxf.linetype if entity.has_dxf_attrib('linetype') else "ByLayer"
            
# # # # # # # # # # # # # # #             # Товщина лінії (lineweight в ezdxf повертається в сотих частках мм, наприклад, 25 = 0.25мм)
# # # # # # # # # # # # # # #             # Значення <= 0 зазвичай означають варіації "ByLayer" або "ByBlock"
# # # # # # # # # # # # # # #             lw_raw = entity.dxf.lineweight if entity.has_dxf_attrib('lineweight') else -1
# # # # # # # # # # # # # # #             if lw_raw == -1:
# # # # # # # # # # # # # # #                 lineweight = "За шаром (ByLayer)"
# # # # # # # # # # # # # # #             elif lw_raw == -2:
# # # # # # # # # # # # # # #                 lineweight = "За блоком (ByBlock)"
# # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # #                 lineweight = f"{lw_raw / 100:.2f} мм"

# # # # # # # # # # # # # # #             text = ""

# # # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # # #                 cx, cy, cz = entity.dxf.center
# # # # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # # # #                 diameter = r * 2
# # # # # # # # # # # # # # #                 length_of_circle = 2 * math.pi * r  # Довжина кола
# # # # # # # # # # # # # # #                 area = math.pi * (r ** 2)          # Площа кола

# # # # # # # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ ФІКС] "
# # # # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ ФІКС] "
# # # # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ ФІКС] "
# # # # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ ФІКС] "
# # # # # # # # # # # # # # #                 else: prefix = "🔘 "

# # # # # # # # # # # # # # #                 text = (
# # # # # # # # # # # # # # #                     f"{prefix}Отвір (ID: {hndl})\n"
# # # # # # # # # # # # # # #                     f"  ├─ Центр: X: {cx:.2f}, Y: {cy:.2f}, Z: {cz:.2f}\n"
# # # # # # # # # # # # # # #                     f"  ├─ Радіус: {r:.2f} мм | Діаметр: {diameter:.2f} мм\n"
# # # # # # # # # # # # # # #                     f"  ├─ Довжина кола: {length_of_circle:.2f} мм\n"
# # # # # # # # # # # # # # #                     f"  ├─ Площа: {area:.2f} мм²\n"
# # # # # # # # # # # # # # #                     f"  └─ Шар: {layer} | Товщина: {lineweight} | Колір ACI: {color_index} | Тип: {linetype}"
# # # # # # # # # # # # # # #                 )

# # # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # # #                 x1, y1, z1 = entity.dxf.start
# # # # # # # # # # # # # # #                 x2, y2, z2 = entity.dxf.end
# # # # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                
# # # # # # # # # # # # # # #                 # Розрахунок повної довжини відрізка у 3D просторі
# # # # # # # # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

# # # # # # # # # # # # # # #                 text = (
# # # # # # # # # # # # # # #                     f"📏 Лінія (ID: {hndl})\n"
# # # # # # # # # # # # # # #                     f"  ├─ Старт: X: {x1:.2f}, Y: {y1:.2f}, Z: {z1:.2f}\n"
# # # # # # # # # # # # # # #                     f"  ├─ Кінець: X: {x2:.2f}, Y: {y2:.2f}, Z: {z2:.2f}\n"
# # # # # # # # # # # # # # #                     f"  ├─ Довжина: {length:.2f} мм\n"
# # # # # # # # # # # # # # #                     f"  └─ Шар: {layer} | Товщина: {lineweight} | Колір ACI: {color_index} | Тип: {linetype}"
# # # # # # # # # # # # # # #                 )
            
# # # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # # #                 # На випадок якщо у файлі з'являться інші типи геометрії (напр. ARC, TEXT)
# # # # # # # # # # # # # # #                 continue

# # # # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # # # #             item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # # # #             self.entity_list.addItem(item)
            
# # # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # # # # # # #     import PyQt5.QtWidgets as qtw
# # # # # # # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # # # # # # #     window = MiniCAD()
# # # # # # # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# # # # # # # # # # # # # # #     window.show()
# # # # # # # # # # # # # # #     sys.exit(app.exec_())
# # # # # # # # # # # # # # import os
# # # # # # # # # # # # # # import sys
# # # # # # # # # # # # # # import math

# # # # # # # # # # # # # # import ezdxf
# # # # # # # # # # # # # # import ezdxf.bbox as dxf_bbox  # Використовуємо для точного прорахунку меж

# # # # # # # # # # # # # # from PyQt5.QtWidgets import (
# # # # # # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # # # # # #     QGroupBox, QGraphicsRectItem
# # # # # # # # # # # # # # )
# # # # # # # # # # # # # # from PyQt5.QtCore import Qt
# # # # # # # # # # # # # # from PyQt5.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # # # # # # Обов'язкові імпорти ваших кастомних модулів:
# # # # # # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # # # # # from graphics_view import AdvancedGraphicsView


# # # # # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # # # def patch_ezdxf_entities():
# # # # # # # # # # # # # #     """
# # # # # # # # # # # # # #     Додає у класи ezdxf Line та Circle зручні властивості left_x, right_x, bottom_y, top_y,
# # # # # # # # # # # # # #     щоб не писати min/max вручну по всьому коду програми.
# # # # # # # # # # # # # #     """

# # # # # # # # # # # # # #     from ezdxf.entities import Line
# # # # # # # # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # # # # # # # #     # 2. Розширення для КОЛА (ezdxf.entities.Circle)
# # # # # # # # # # # # # #     from ezdxf.entities import Circle
# # # # # # # # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # # # # # # # # Викликаємо патч сутностей перед запуску всього CAD-редактора
# # # # # # # # # # # # # # patch_ezdxf_entities()
# # # # # # # # # # # # # # # ---------------------------------------------------------------------------


# # # # # # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # # # # # #     def __init__(self):
# # # # # # # # # # # # # #         super().__init__()

# # # # # # # # # # # # # #         self.setWindowTitle("CAD Двері: Розумна автогенерація 2D зон")
# # # # # # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # # # # # #         self.dxf_path = "drawing.DXF"

# # # # # # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # # # #         # Списки для жорстких зон фіксації
# # # # # # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # # # # # #             sys.exit()

# # # # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # # # # # #         self.init_ui()
# # # # # # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     def init_ui(self):
# # # # # # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # # # # # #         self.view.setRenderHint(QPainter.Antialiasing)
# # # # # # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("background-color: #e8f5e9; font-weight: bold;")
# # # # # # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("background-color: #ffebee; font-weight: bold;")
# # # # # # # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
# # # # # # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡 Верхній блок (Y)")
# # # # # # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("background-color: #fffde7; font-weight: bold;")
# # # # # # # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
# # # # # # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # # # # # #         self.slider = QSlider(Qt.Horizontal)
# # # # # # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     # ЧИСТА АВТОГЕНЕРАЦІЯ ЗОН (ЗАВДЯКИ НАШИМ НОВИМ АТРИБУТАМ)
# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # # # # # # #         """
# # # # # # # # # # # # # #         Автовизначення порожнечі між фіксами. Завдяки патчу ezdxf, 
# # # # # # # # # # # # # #         код здихався від громіздких конструкцій min/max.
# # # # # # # # # # # # # #         """
# # # # # # # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # # # # # # # #             # Використовуємо .right_x прямо як готовий атрибут сутності ezdxf!
# # # # # # # # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # # # # #             # Використовуємо .left_x прямо як готовий атрибут!
# # # # # # # # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x , min_right_x , 'X')

# # # # # # # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # # # # # # #             # Використовуємо наш новий .top_y атрибут
# # # # # # # # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # # # # #             # Використовуємо наш новий .bottom_y атрибут
# # # # # # # # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y , min_top_y , 'Y')

# # # # # # # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # # # # # # #                 return

# # # # # # # # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        
# # # # # # # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # # # # # # #                 break

# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     # СТВОРЕННЯ МНОЖИННИХ ЗОН ВРУЧНУ (ТАКОЖ З НОВИМИ АТРИБУТАМИ)
# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # # # # # #             """
# # # # # # # # # # # # # #             Створює зону розтягування СУТО В ПОРОЖНЕЧІ між виділеними елементами,
# # # # # # # # # # # # # #             повністю виключаючи самі деталі з зони деформації.
# # # # # # # # # # # # # #             """
# # # # # # # # # # # # # #             if not self.selected_handles or not self.original_geometries:
# # # # # # # # # # # # # #                 return

# # # # # # # # # # # # # #             active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # # # # # # # #             if not active_entities: 
# # # # # # # # # # # # # #                 return

# # # # # # # # # # # # # #             # Якщо виділено менше 2 елементів, ми не можемо знайти порожнечу МІЖ ними
# # # # # # # # # # # # # #             if len(active_entities) < 2:
# # # # # # # # # # # # # #                 self.clear_selection()
# # # # # # # # # # # # # #                 return

# # # # # # # # # # # # # #             if axis == 'X':
# # # # # # # # # # # # # #                 # Зона починається після ПРАВОГО краю найлівішого елемента
# # # # # # # # # # # # # #                 min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # # # # # # # #                 # Зона закінчується перед ЛІВИМ краєм найправішого елемента
# # # # # # # # # # # # # #                 max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # #                 # Зона починається після ВЕРХНЬОГО краю найнижчого елемента
# # # # # # # # # # # # # #                 min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # # # # # # # #                 # Зона закінчується перед НИЖНІМ краєм найвищого елемента
# # # # # # # # # # # # # #                 max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # # # # # # # #             # Ставимо безпечний запобіжник: якщо простір між деталями коректний — додаємо зону
# # # # # # # # # # # # # #             if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # # # # # # # #                 self.add_or_update_zone_bounds(min_val, max_val, axis)
                
# # # # # # # # # # # # # #             self.clear_selection()

# # # # # # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # # #             item.setData(Qt.UserRole, idx)
# # # # # # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # # # # # #         if not selected:
# # # # # # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # # # # # #             return

# # # # # # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.UserRole)
# # # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # # # # # #             return

# # # # # # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # # # # # #             z_min = zone['min']
# # # # # # # # # # # # # #             z_max = zone['max']
# # # # # # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # # # # # #                 shifted_val += val
# # # # # # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # # # # # #                 if width > 0:
# # # # # # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # # # # # #         return shifted_val

# # # # # # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # # # # # #         self.doc.saveas(self.dxf_path)
# # # # # # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # # #             zone['min'] = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # # #             zone['max'] = self.calculate_cascade_shift(zone['max'], zone['axis'], None)
# # # # # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     # ВІЗУАЛІЗАЦІЯ ЗОН (ЗАМАЛЬОВУВАННЯ ПРЯМОКУТНИКІВ)
# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     def update_viewer(self):
# # # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # # # # # #         try:
# # # # # # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # # # # # #         except Exception:
# # # # # # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # # #             disp_max = disp_min + (zone['max'] - zone['min']) + zone['stretch_val']

# # # # # # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # # # # # #                 rect_item.setPen(QPen(color.darker(), 1.5, Qt.DashLine))
# # # # # # # # # # # # # #             else:
# # # # # # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.DotLine))
                
# # # # # # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # #             pyqt_item = None

# # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # # # # # #             if pyqt_item:
# # # # # # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
# # # # # # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.SolidLine))
# # # # # # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.SolidLine))
# # # # # # # # # # # # # #                 else: pyqt_item.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))

# # # # # # # # # # # # # #                 pyqt_item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # # # # # #                 }
# # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # # # # # #                 }

# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     # СЛУЖБОВІ МЕТОДИ СИНХРОНІЗАЦІЇ СПИСКІВ
# # # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # #         path = QPainterPath()
# # # # # # # # # # # # # #         path.addRect(rect)
# # # # # # # # # # # # # #         matched_items = self.scene.items(path, Qt.IntersectsItemShape)
# # # # # # # # # # # # # #         for item in matched_items:
# # # # # # # # # # # # # #             hndl = item.data(Qt.UserRole)
# # # # # # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # # # # # #             if item.data(Qt.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # # # # # #             self.selected_handles.add(item.data(Qt.UserRole))
# # # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # # #     def clear_selection(self):
# # # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # # # # # #         seen = set()
        
# # # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # # # # # # #             layer = entity.dxf.layer if entity.has_dxf_attrib('layer') else "Default"
# # # # # # # # # # # # # #             color_index = entity.dxf.color if entity.has_dxf_attrib('color') else "ByLayer"
# # # # # # # # # # # # # #             linetype = entity.dxf.linetype if entity.has_dxf_attrib('linetype') else "ByLayer"
            
# # # # # # # # # # # # # #             lw_raw = entity.dxf.lineweight if entity.has_dxf_attrib('lineweight') else -1
# # # # # # # # # # # # # #             if lw_raw == -1: lineweight = "ByLayer"
# # # # # # # # # # # # # #             elif lw_raw == -2: lineweight = "ByBlock"
# # # # # # # # # # # # # #             else: lineweight = f"{lw_raw / 100:.2f} мм"

# # # # # # # # # # # # # #             text = ""

# # # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # # #                 cx, cy, cz = entity.dxf.center
# # # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # # #                 diameter = r * 2
# # # # # # # # # # # # # #                 length_of_circle = 2 * math.pi * r
# # # # # # # # # # # # # #                 area = math.pi * (r ** 2)

# # # # # # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ] "
# # # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ] "
# # # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ] "
# # # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ] "
# # # # # # # # # # # # # #                 else: prefix = "🔘 "

# # # # # # # # # # # # # #                 text = (
# # # # # # # # # # # # # #                     f"{prefix}Отвір (ID: {hndl})\n"
# # # # # # # # # # # # # #                     f"  ├─ Центр: X: {cx:.1f}, Y: {cy:.1f}\n"
# # # # # # # # # # # # # #                     f"  ├─ Радіус: {r:.1f} мм | Діаметр: {diameter:.1f} мм\n"
# # # # # # # # # # # # # #                     f"  └─ Шар: {layer} | Товщина: {lineweight}"
# # # # # # # # # # # # # #                 )

# # # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # # #                 x1, y1, z1 = entity.dxf.start
# # # # # # # # # # # # # #                 x2, y2, z2 = entity.dxf.end
# # # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                
# # # # # # # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

# # # # # # # # # # # # # #                 # Отримуємо товщину (вагу) лінії
# # # # # # # # # # # # # #                 lw_value = entity.dxf.get('lineweight', 256)
# # # # # # # # # # # # # #                 if lw_value == 256:
# # # # # # # # # # # # # #                     lineweight_str = "За шаром"
# # # # # # # # # # # # # #                 elif lw_value < 0:
# # # # # # # # # # # # # #                     lineweight_str = "Стандартна"
# # # # # # # # # # # # # #                 else:
# # # # # # # # # # # # # #                     lineweight_str = f"{lw_value / 100:.2f} мм"

# # # # # # # # # # # # # #                 text = (
# # # # # # # # # # # # # #                     f"📏 Лінія (ID: {hndl})\n"
# # # # # # # # # # # # # #                     f"  ├─ Старт: X: {x1:.1f}, Y: {y1:.1f}\n"
# # # # # # # # # # # # # #                     f"  ├─ Кінець: X: {x2:.1f}, Y: {y2:.1f}\n"
# # # # # # # # # # # # # #                     f"  ├─ Товщина лінії: {lineweight_str}\n"
# # # # # # # # # # # # # #                     f"  └─ Довжина: {length:.1f} мм"
# # # # # # # # # # # # # #                 )

# # # # # # # # # # # # # #             else: continue

# # # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # # #             item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # # #             self.entity_list.addItem(item)
            
# # # # # # # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # # # # # #     import PyQt5.QtWidgets as qtw
# # # # # # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # # # # # #     window = MiniCAD()
# # # # # # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# # # # # # # # # # # # # #     window.show()
# # # # # # # # # # # # # #     sys.exit(app.exec_())

# # # # # # # # # # # # # import os
# # # # # # # # # # # # # import sys
# # # # # # # # # # # # # import math

# # # # # # # # # # # # # import ezdxf
# # # # # # # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж без крашів

# # # # # # # # # # # # # from PyQt5.QtWidgets import (
# # # # # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # # # # #     QGroupBox, QGraphicsRectItem
# # # # # # # # # # # # # )
# # # # # # # # # # # # # from PyQt5.QtCore import Qt
# # # # # # # # # # # # # from PyQt5.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # # # # # Обов'язкові імпорти ваших кастомних модулів:
# # # # # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # # # # # # # from history_manager import HistoryManager


# # # # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # # def patch_ezdxf_entities():
# # # # # # # # # # # # #     """
# # # # # # # # # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # # # # # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf через ручний прорахунок.
# # # # # # # # # # # # #     """
# # # # # # # # # # # # #     from ezdxf.entities import Line
# # # # # # # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # # # # # # #     from ezdxf.entities import Circle
# # # # # # # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # # # # # # # Викликаємо патч сутностей перед запуском всього CAD-редактора
# # # # # # # # # # # # # patch_ezdxf_entities()
# # # # # # # # # # # # # # ---------------------------------------------------------------------------


# # # # # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # # # # #     def __init__(self):
# # # # # # # # # # # # #         super().__init__()

# # # # # # # # # # # # #         self.setWindowTitle("CAD Двері: Безпомилковий 2D багатозонний параметризатор")
# # # # # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # # # # #         self.dxf_path = "drawing.DXF"

# # # # # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # # #         # Списки для жорстких зон фіксації
# # # # # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # # # # #             sys.exit()

# # # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # # # # #         # Ініціалізація історії змін
# # # # # # # # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # # # # # # # #         self.history.save_state()

# # # # # # # # # # # # #         self.init_ui()
# # # # # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # #     def init_ui(self):
# # # # # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # # # # #         self.view.setRenderHint(QPainter.Antialiasing)
# # # # # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # # # # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # # # # # # # # #         history_box = QHBoxLayout()
# # # # # # # # # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # # # # # # # # #         self.btn_undo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # # # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # # # # # # # # #         self.btn_redo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # # # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # # # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # # # # # # # #         history_group.setLayout(history_box)
# # # # # # # # # # # # #         control_layout.addWidget(history_group)
# # # # # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # # # # #         fix_group = QGroupBox("1.  Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("background-color: #e8f5e9; font-weight: bold;")
# # # # # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("background-color: #ffebee; font-weight: bold;")
# # # # # # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
# # # # # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("background-color: #fffde7; font-weight: bold;")
# # # # # # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
# # # # # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # # # # #         self.slider = QSlider(Qt.Horizontal)
# # # # # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     # УПРАВЛІННЯ ІСТОРІЄЮ ЗМІН (UNDO / REDO)
# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     def undo(self):
# # # # # # # # # # # # #         if self.history.undo(): 
# # # # # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # # # # #     def redo(self):
# # # # # # # # # # # # #         if self.history.redo(): 
# # # # # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # # # # #     def update_history_buttons_state(self):
# # # # # # # # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1)
# # # # # # # # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0)

# # # # # # # # # # # # #     def reload_after_history_change(self):
# # # # # # # # # # # # #         """Повне відновлення інтерфейсу та зон деформації."""
# # # # # # # # # # # # #         self.is_loading_history = True
# # # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # # # # #         # Скидаємо накопичені стрейчі, зони автоматично повернуться на базові місця
# # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # # # # #         self.update_history_buttons_state()
        
# # # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     # АВТОГЕНЕРАЦІЯ ЗОН РОЗТЯГУВАННЯ
# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')

# # # # # # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # # # # # #                 return

# # # # # # # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        
# # # # # # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # # # # # #                 break

# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     # СТВОРЕННЯ МНОЖИННИХ ЗОН ВРУЧНУ (ЧИСТА ПОРОЖНЕЧА)
# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # # # # # #             return

# # # # # # # # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # # # # # # # #             self.clear_selection()
# # # # # # # # # # # # #             return

# # # # # # # # # # # # #         if axis == 'X':
# # # # # # # # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # # # # # # #         else:
# # # # # # # # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
            
# # # # # # # # # # # # #         self.clear_selection()

# # # # # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # #             item.setData(Qt.UserRole, idx)
# # # # # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # # # # #         if not selected:
# # # # # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # # # # #             return

# # # # # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.UserRole)
# # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # # # # #             return

# # # # # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # # # # #             z_min = zone['min']
# # # # # # # # # # # # #             z_max = zone['max']
# # # # # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # # # # #                 shifted_val += val
# # # # # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # # # # #                 if width > 0:
# # # # # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # # # # #         return shifted_val

# # # # # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # # # # # # # #         # Фіксуємо поточний стан креслення в стек Undo історії
# # # # # # # # # # # # #         self.history.save_state()
# # # # # # # # # # # # #         self.history.clear_redo()
# # # # # # # # # # # # #         self.update_history_buttons_state()
        
# # # # # # # # # # # # #         # ВИПРАВЛЕНО: Ми більше НЕ перетираємо координати меж прямокутників zone['min'].
# # # # # # # # # # # # #         # Замість цього ми просто скидаємо тимчасовий слайдер stretch_val = 0.0, 
# # # # # # # # # # # # #         # оскільки геометрія вже зафіксована, а приріст перейшов у саму DXF-модель.
# # # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # # # #         self.save_original_geometries()

# # # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     # ВІЗУАЛІЗАЦІЯ ЗОН (ЗАМАЛЬОВУВАННЯ ПРЯМОКУТНИКІВ)
# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     def update_viewer(self):
# # # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # # # # #         try:
# # # # # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # # # # #         except Exception:
# # # # # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # # # # #         # МАЛЮЄМО НАПІВПРОЗОРІ КОЛЬОРОВІ КВАДРАТИ / ПРЯМОКУТНИКИ РОЗТЯГУВАННЯ
# # # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # # #             # ВИПРАВЛЕНО: Пропускаємо межі ПРЯМОКУТНИКА крізь каскадний зсув!
# # # # # # # # # # # # #             # Завдяки цьому при зміщенні Зони №1, Зона №2 автоматично від'їжджає на екрані.
# # # # # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None)

# # # # # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # # # # #             else:
# # # # # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # # # # #                 rect_item.setPen(QPen(color.darker(), 1.5, Qt.DashLine))
# # # # # # # # # # # # #             else:
# # # # # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.DotLine))
                
# # # # # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # #             pyqt_item = None

# # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # # # # #             if pyqt_item:
# # # # # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
# # # # # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.SolidLine))
# # # # # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.SolidLine))
# # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.SolidLine))
# # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.SolidLine))
# # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.SolidLine))
# # # # # # # # # # # # #                 else: pyqt_item.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))

# # # # # # # # # # # # #                 pyqt_item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # # # # #                 }
# # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # # # # #                 }

# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     # СЛУЖБОВІ МЕТОДИ СИНХРОНІЗАЦІЇ СПИСКІВ
# # # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # #         path = QPainterPath()
# # # # # # # # # # # # #         path.addRect(rect)
# # # # # # # # # # # # #         matched_items = self.scene.items(path, Qt.IntersectsItemShape)
# # # # # # # # # # # # #         for item in matched_items:
# # # # # # # # # # # # #             hndl = item.data(Qt.UserRole)
# # # # # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # # # # #             if item.data(Qt.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # # # # #             self.selected_handles.add(item.data(Qt.UserRole))
# # # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # # #     def clear_selection(self):
# # # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # # # # #         seen = set()
        
# # # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # # # # # #             layer = entity.dxf.layer if entity.has_dxf_attrib('layer') else "Default"
# # # # # # # # # # # # #             color_index = entity.dxf.color if entity.has_dxf_attrib('color') else "ByLayer"
# # # # # # # # # # # # #             linetype = entity.dxf.linetype if entity.has_dxf_attrib('linetype') else "ByLayer"
            
# # # # # # # # # # # # #             lw_raw = entity.dxf.lineweight if entity.has_dxf_attrib('lineweight') else -1
# # # # # # # # # # # # #             if lw_raw == -1: lineweight = "ByLayer"
# # # # # # # # # # # # #             elif lw_raw == -2: lineweight = "ByBlock"
# # # # # # # # # # # # #             else: lineweight = f"{lw_raw / 100:.2f} мм"

# # # # # # # # # # # # #             text = ""

# # # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # # #                 cx, cy, cz = entity.dxf.center
# # # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # # #                 diameter = r * 2
# # # # # # # # # # # # #                 length_of_circle = 2 * math.pi * r
# # # # # # # # # # # # #                 area = math.pi * (r ** 2)

# # # # # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ] "
# # # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ] "
# # # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ] "
# # # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ] "
# # # # # # # # # # # # #                 else: prefix = "🔘 "

# # # # # # # # # # # # #                 text = (
# # # # # # # # # # # # #                     f"{prefix}Отвір (ID: {hndl})\n"
# # # # # # # # # # # # #                     f"  ├─ Центр: X: {cx:.1f}, Y: {cy:.1f}\n"
# # # # # # # # # # # # #                     f"  ├─ Радіус: {r:.1f} мм | Діаметр: {diameter:.1f} мм\n"
# # # # # # # # # # # # #                     f"  └─ Шар: {layer} | Top: {lineweight}"
# # # # # # # # # # # # #                 )

# # # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # # #                 x1, y1, z1 = entity.dxf.start
# # # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                
# # # # # # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z1 - z1)**2)

# # # # # # # # # # # # #                 lw_value = entity.dxf.get('lineweight', 256)
# # # # # # # # # # # # #                 if lw_value == 256: lineweight_str = "За шаром"
# # # # # # # # # # # # #                 elif lw_value < 0: lineweight_str = "Стандартна"
# # # # # # # # # # # # #                 else: lineweight_str = f"{lw_value / 100:.2f} мм"

# # # # # # # # # # # # #                 text = (
# # # # # # # # # # # # #                     f"📏 Лінія (ID: {hndl})\n"
# # # # # # # # # # # # #                     f"  ├─ Старт: X: {x1:.1f}, Y: {y1:.1f}\n"
# # # # # # # # # # # # #                     f"  ├─ Кінець: X: {x2:.1f}, Y: {y2:.1f}\n"
# # # # # # # # # # # # #                     f"  ├─ Товщина лінії: {lineweight_str}\n"
# # # # # # # # # # # # #                     f"  └─ Довжина: {length:.1f} мм"
# # # # # # # # # # # # #                 )
# # # # # # # # # # # # #             else: continue

# # # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # # #             item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # # #             self.entity_list.addItem(item)
            
# # # # # # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # # # # #     import PyQt5.QtWidgets as qtw
# # # # # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # # # # #     window = MiniCAD()
# # # # # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# # # # # # # # # # # # #     window.show()
# # # # # # # # # # # # #     sys.exit(app.exec_())

# # # # # # # # # # # # import os
# # # # # # # # # # # # import sys
# # # # # # # # # # # # import math
# # # # # # # # # # # # import copy  # Додано для глибокого копіювання станів зон в Undo/Redo

# # # # # # # # # # # # import ezdxf
# # # # # # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж без крашів

# # # # # # # # # # # # from PyQt5.QtWidgets import (
# # # # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # # # #     QGroupBox, QGraphicsRectItem
# # # # # # # # # # # # )
# # # # # # # # # # # # from PyQt5.QtCore import Qt
# # # # # # # # # # # # from PyQt5.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # # # # Обов'язкові імпорти ваших кастомних модулів:
# # # # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # # # # # # from history_manager import HistoryManager


# # # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # def patch_ezdxf_entities():
# # # # # # # # # # # #     """
# # # # # # # # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # # # # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf.
# # # # # # # # # # # #     """
# # # # # # # # # # # #     from ezdxf.entities import Line
# # # # # # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # # # # # #     from ezdxf.entities import Circle
# # # # # # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # # # # # # Викликаємо патч сутностей перед запуском всього CAD-редактора
# # # # # # # # # # # # patch_ezdxf_entities()
# # # # # # # # # # # # # ---------------------------------------------------------------------------


# # # # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # # # #     def __init__(self):
# # # # # # # # # # # #         super().__init__()

# # # # # # # # # # # #         self.setWindowTitle("CAD Двері: 2D параметризатор")
# # # # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # # # #         self.dxf_path = "drawing.DXF"

# # # # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # #         # Списки для жорстких зон фіксації
# # # # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # # # #         # Стек для синхронного відкоту прямокутників разом із DXF-файлом
# # # # # # # # # # # #         self.zones_undo_stack = []
# # # # # # # # # # # #         self.zones_redo_stack = []

# # # # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # # # #             sys.exit()

# # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # # # #         # Ініціалізація історії змін DXF
# # # # # # # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # # # # # # #         self.history.save_state()
# # # # # # # # # # # #         self.save_zones_history_state()  # Зберігаємо стартовий стан прямокутників

# # # # # # # # # # # #         self.init_ui()
# # # # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # #     def init_ui(self):
# # # # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # # # #         self.view.setRenderHint(QPainter.Antialiasing)
# # # # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # # # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # # # # # # # #         history_box = QHBoxLayout()
# # # # # # # # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # # # # # # # #         self.btn_undo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # # # # # # # #         self.btn_redo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # # # # # # #         history_group.setLayout(history_box)
# # # # # # # # # # # #         control_layout.addWidget(history_group)
# # # # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("background-color: #e8f5e9; font-weight: bold;")
# # # # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("background-color: #ffebee; font-weight: bold;")
# # # # # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
# # # # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡 Верхній блок (Y)")
# # # # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("background-color: #fffde7; font-weight: bold;")
# # # # # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
# # # # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # # # #         self.slider = QSlider(Qt.Horizontal)
# # # # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     # УПРАВЛІННЯ ІСТОРІЄЮ ЗМІН ПРЯМОКУТНИКІВ ЗОН
# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     def save_zones_history_state(self):
# # # # # # # # # # # #         """Зберігає глибоку копію масиву прямокутників зон в Undo-стек."""
# # # # # # # # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # # # # # # # #         if len(self.zones_undo_stack) > 30:
# # # # # # # # # # # #             self.zones_undo_stack.pop(0)

# # # # # # # # # # # #     def undo(self):
# # # # # # # # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # # # # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # # # # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # # # # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # # # #     def redo(self):
# # # # # # # # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # # # # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # # # # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # # # # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # # # #     def update_history_buttons_state(self):
# # # # # # # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # # # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # # # # # # # #     def reload_after_history_change(self):
# # # # # # # # # # # #         self.is_loading_history = True
# # # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # # # #         self.update_history_buttons_state()
# # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     # АВТОГЕНЕРАЦІЯ ЗОН РОЗТЯГУВАННЯ
# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')

# # # # # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # # # # #                 return

# # # # # # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        
# # # # # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # # # # #                 break

# # # # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # # # # #             return

# # # # # # # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # # # # # # #             self.clear_selection()
# # # # # # # # # # # #             return

# # # # # # # # # # # #         if axis == 'X':
# # # # # # # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # # # # # #         else:
# # # # # # # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
            
# # # # # # # # # # # #         self.clear_selection()

# # # # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # #             item.setData(Qt.UserRole, idx)
# # # # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # # # #         if not selected:
# # # # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # # # #             return

# # # # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.UserRole)
# # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # # # #             return

# # # # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # # # #             z_min = zone['min']
# # # # # # # # # # # #             z_max = zone['max']
# # # # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # # # #                 shifted_val += val
# # # # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # # # #                 if width > 0:
# # # # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # # # #         return shifted_val

# # # # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # # # #         """Фіксація та каскадне зміщення меж сусідніх помаранчевих прямокутників."""
# # # # # # # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # # # # # # #         # 1. ЗАФІКСОВУЄМО МЕЖІ САМИХ ЗОН НА ОСНОВІ КАСКАДУ
# # # # # # # # # # # #         active_zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # # #         stretch_amount = active_zone['stretch_val']
# # # # # # # # # # # #         active_axis = active_zone['axis']
# # # # # # # # # # # #         active_max = active_zone['max']

# # # # # # # # # # # #         # Збільшуємо ширину/висоту самої активної розтягнутої області
# # # # # # # # # # # #         active_zone['max'] += stretch_amount

# # # # # # # # # # # #         # Каскадно зміщуємо всі НАСТУПНІ створені зони деформації простору, що лежать далі
# # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # #             if idx == self.active_zone_index or zone['axis'] != active_axis:
# # # # # # # # # # # #                 continue
# # # # # # # # # # # #             if zone['min'] >= active_max:
# # # # # # # # # # # #                 zone['min'] += stretch_amount
# # # # # # # # # # # #                 zone['max'] += stretch_amount

# # # # # # # # # # # #         # Скидаємо тимчасовий приріст слайдера
# # # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # # #         # Зберігаємо фінальний стан у стек Undo історії
# # # # # # # # # # # #         self.history.save_state()
# # # # # # # # # # # #         self.history.clear_redo()
# # # # # # # # # # # #         self.save_zones_history_state()
# # # # # # # # # # # #         self.zones_redo_stack.clear()
# # # # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # # # #         self.save_original_geometries()

# # # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     # ВІЗУАЛІЗАЦІЯ ЗОН (ЗАМАЛЬОВУВАННЯ ПРЯМОКУТНИКІВ)
# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     def update_viewer(self):
# # # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # # # #         try:
# # # # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # # # #         except Exception:
# # # # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # # # #         # МАЛЮЄМО НАПІВПРОЗОРІ КОЛЬОРОВІ КВАДРАТИ / ПРЯМОКУТНИКИ РОЗТЯГУВАННЯ
# # # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # # #             disp_max = disp_min + (zone['max'] - zone['min']) + zone['stretch_val']

# # # # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # # # #             else:
# # # # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # # # #                 rect_item.setPen(QPen(color.darker(), 1.5, Qt.DashLine))
# # # # # # # # # # # #             else:
# # # # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.DotLine))
                
# # # # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # #             pyqt_item = None

# # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # # # #             if pyqt_item:
# # # # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
# # # # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.SolidLine))
# # # # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.SolidLine))
# # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.SolidLine))
# # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.SolidLine))
# # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.SolidLine))
# # # # # # # # # # # #                 else: pyqt_item.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))

# # # # # # # # # # # #                 pyqt_item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # # # #                 }
# # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # # # #                 }

# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     # СЛУЖБОВІ МЕТОДИ СИНХРОНІЗАЦІЇ СПИСКІВ
# # # # # # # # # # # #     # ---------------------------
# # # # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # #         path = QPainterPath()
# # # # # # # # # # # #         path.addRect(rect)
# # # # # # # # # # # #         matched_items = self.scene.items(path, Qt.IntersectsItemShape)
# # # # # # # # # # # #         for item in matched_items:
# # # # # # # # # # # #             hndl = item.data(Qt.UserRole)
# # # # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # # # #             if item.data(Qt.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # # # #             self.selected_handles.add(item.data(Qt.UserRole))
# # # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # # #     def clear_selection(self):
# # # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # # # #         seen = set()
        
# # # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # # # # #             layer = entity.dxf.layer if entity.has_dxf_attrib('layer') else "Default"
# # # # # # # # # # # #             color_index = entity.dxf.color if entity.has_dxf_attrib('color') else "ByLayer"
# # # # # # # # # # # #             linetype = entity.dxf.linetype if entity.has_dxf_attrib('linetype') else "ByLayer"
            
# # # # # # # # # # # #             lw_raw = entity.dxf.lineweight if entity.has_dxf_attrib('lineweight') else -1
# # # # # # # # # # # #             if lw_raw == -1: lineweight = "ByLayer"
# # # # # # # # # # # #             elif lw_raw == -2: lineweight = "ByBlock"
# # # # # # # # # # # #             else: lineweight = f"{lw_raw / 100:.2f} мм"

# # # # # # # # # # # #             text = ""

# # # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # # #                 cx, cy, cz = entity.dxf.center
# # # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # # #                 diameter = r * 2
# # # # # # # # # # # #                 length_of_circle = 2 * math.pi * r
# # # # # # # # # # # #                 area = math.pi * (r ** 2)

# # # # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ] "
# # # # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ] "
# # # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ] "
# # # # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ] "
# # # # # # # # # # # #                 else: prefix = "🔘 "

# # # # # # # # # # # #                 text = (
# # # # # # # # # # # #                     f"{prefix}Отвір (ID: {hndl})\n"
# # # # # # # # # # # #                     f"  ├─ Центр: X: {cx:.1f}, Y: {cy:.1f}\n"
# # # # # # # # # # # #                     f"  ├─ Радіус: {r:.1f} мм | Діаметр: {diameter:.1f} мм\n"
# # # # # # # # # # # #                     f"  └─ Шар: {layer} | Товщина: {lineweight}"
# # # # # # # # # # # #                 )

# # # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # # #                 x1, y1, z1 = entity.dxf.start
# # # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                
# # # # # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z1 - z1)**2)

# # # # # # # # # # # #                 lw_value = entity.dxf.get('lineweight', 256)
# # # # # # # # # # # #                 if lw_value == 256: lineweight_str = "За шаром"
# # # # # # # # # # # #                 elif lw_value < 0: lineweight_str = "Стандартна"
# # # # # # # # # # # #                 else: lineweight_str = f"{lw_value / 100:.2f} мм"

# # # # # # # # # # # #                 text = (
# # # # # # # # # # # #                     f"📏 Лінія (ID: {hndl})\n"
# # # # # # # # # # # #                     f"  ├─ Старт: X: {x1:.1f}, Y: {y1:.1f}\n"
# # # # # # # # # # # #                     f"  ├─ Кінець: X: {x2:.1f}, Y: {y2:.1f}\n"
# # # # # # # # # # # #                     f"  ├─ Товщина лінії: {lineweight_str}\n"
# # # # # # # # # # # #                     f"  └─ Довжина: {length:.1f} мм"
# # # # # # # # # # # #                 )
# # # # # # # # # # # #             else: continue

# # # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # # #             item.setData(Qt.UserRole, hndl)
# # # # # # # # # # # #             self.entity_list.addItem(item)
            
# # # # # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # # # #     import PyQt5.QtWidgets as qtw
# # # # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # # # #     window = MiniCAD()
# # # # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# # # # # # # # # # # #     window.show()
# # # # # # # # # # # #     sys.exit(app.exec_())

# # # # # # # # # # # import os
# # # # # # # # # # # import sys
# # # # # # # # # # # import math
# # # # # # # # # # # import copy  # Для глибокого копіювання станів прямокутників зон в Undo/Redo

# # # # # # # # # # # import ezdxf
# # # # # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж без крашів

# # # # # # # # # # # # Оновлені імпорти інтерфейсу під PySide6
# # # # # # # # # # # from PySide6.QtWidgets import (
# # # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # # #     QGroupBox, QGraphicsRectItem
# # # # # # # # # # # )
# # # # # # # # # # # from PySide6.QtCore import Qt
# # # # # # # # # # # from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # # # Імпорти ваших кастомних модулів:
# # # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # # # # # from history_manager import HistoryManager


# # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # # def patch_ezdxf_entities():
# # # # # # # # # # #     """
# # # # # # # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # # # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf.
# # # # # # # # # # #     """
# # # # # # # # # # #     from ezdxf.entities import Line
# # # # # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # # # # #     from ezdxf.entities import Circle
# # # # # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # # # # # Викликаємо патч сутностей перед запуском всього CAD-редактора
# # # # # # # # # # # patch_ezdxf_entities()
# # # # # # # # # # # # ---------------------------------------------------------------------------


# # # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # # #     def __init__(self):
# # # # # # # # # # #         super().__init__()

# # # # # # # # # # #         self.setWindowTitle("CAD Двері: Розумна параметризація 2D зон (PySide6)")
# # # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # # #         self.dxf_path = "drawing.DXF"

# # # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # #         # Списки для жорстких зон фіксації
# # # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # # #         # Стек для синхронного відкоту прямокутників разом із DXF-файлом
# # # # # # # # # # #         self.zones_undo_stack = []
# # # # # # # # # # #         self.zones_redo_stack = []

# # # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # # #             sys.exit()

# # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # # #         # Ініціалізація історії змін DXF
# # # # # # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # # # # # #         self.history.save_state()
# # # # # # # # # # #         self.save_zones_history_state()  # Зберігаємо стартовий стан прямокутників

# # # # # # # # # # #         self.init_ui()
# # # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # #     def init_ui(self):
# # # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # # #         self.view.setRenderHint(QPainter.Antialiasing)
# # # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # # # # # # #         history_box = QHBoxLayout()
# # # # # # # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # # # # # # #         self.btn_undo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # # # # # # #         self.btn_redo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # # # # # #         history_group.setLayout(history_box)
# # # # # # # # # # #         control_layout.addWidget(history_group)
# # # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("background-color: #e8f5e9; font-weight: bold;")
# # # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("background-color: #ffebee; font-weight: bold;")
# # # # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("background-color: #e3f2fd; font-weight: bold;")
# # # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("background-color: #fffde7; font-weight: bold;")
# # # # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
# # # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # # #         self.slider = QSlider(Qt.Horizontal)
# # # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     # УПРАВЛІННЯ ІСТОРІЄЮ ЗМІН ПРЯМОКУТНИКІВ ЗОН
# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     def save_zones_history_state(self):
# # # # # # # # # # #         """Зберігає глибоку копію масиву прямокутників зон в Undo-стек."""
# # # # # # # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # # # # # # #         if len(self.zones_undo_stack) > 30:
# # # # # # # # # # #             self.zones_undo_stack.pop(0)

# # # # # # # # # # #     def undo(self):
# # # # # # # # # # #         # Оновлено адаптацію під типізацію колекцій PySide6
# # # # # # # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # # # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # # # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # # # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # # #     def redo(self):
# # # # # # # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # # # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # # # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # # # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # # #     def update_history_buttons_state(self):
# # # # # # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # # # # # # #     def reload_after_history_change(self):
# # # # # # # # # # #         self.is_loading_history = True
# # # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # # #         # Скидаємо накопичені стрейчі
# # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # # #         self.update_history_buttons_state()
# # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     # АВТОГЕНЕРАЦІЯ ЗОН РОЗТЯГУВАННЯ
# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')

# # # # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # # # #                 return

# # # # # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        
# # # # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # # # #                 break

# # # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # # # #             return

# # # # # # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # # # # # #             self.clear_selection()
# # # # # # # # # # #             return

# # # # # # # # # # #         if axis == 'X':
# # # # # # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # # # # #         else:
# # # # # # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
            
# # # # # # # # # # #         self.clear_selection()

# # # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # #             item.setData(Qt.UserRole, idx)
# # # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # # #         if not selected:
# # # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # # #             return

# # # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.UserRole)
# # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # # #             return

# # # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # # #             z_min = zone['min']
# # # # # # # # # # #             z_max = zone['max']
# # # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # # #                 shifted_val += val
# # # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # # #                 if width > 0:
# # # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # # #         return shifted_val

# # # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # # #         """Фіксація та каскадне зміщення меж сусідніх помаранчевих прямокутників."""
# # # # # # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # # # # # #         active_zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # # #         stretch_amount = active_zone['stretch_val']
# # # # # # # # # # #         active_axis = active_zone['axis']
# # # # # # # # # # #         active_max = active_zone['max']

# # # # # # # # # # #         # Збільшуємо ширину/висоту самої активної розтягнутої області
# # # # # # # # # # #         active_zone['max'] += stretch_amount

# # # # # # # # # # #         # Каскадно зміщуємо всі НАСТУПНІ створені зони деформації простору, що лежать далі
# # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # #             if idx == self.active_zone_index or zone['axis'] != active_axis:
# # # # # # # # # # #                 continue
# # # # # # # # # # #             if zone['min'] >= active_max:
# # # # # # # # # # #                 zone['min'] += stretch_amount
# # # # # # # # # # #                 zone['max'] += stretch_amount

# # # # # # # # # # #         # Скидаємо тимчасовий приріст слайдера
# # # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # # #         # Зберігаємо фінальний стан у стек Undo історії
# # # # # # # # # # #         self.history.save_state()
# # # # # # # # # # #         self.history.clear_redo()
# # # # # # # # # # #         self.save_zones_history_state()
# # # # # # # # # # #         self.zones_redo_stack.clear()
# # # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # # #         self.save_original_geometries()

# # # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     # ВІЗУАЛІЗАЦІЯ ЗОН (ЗАМАЛЬОВУВАННЯ ПРЯМОКУТНИКІВ)
# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     def update_viewer(self):
# # # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # # #         try:
# # # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # # #         except Exception:
# # # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # # #         # МАЛЮЄМО НАПІВПРОЗОРІ КОЛЬОРОВІ КВАДРАТИ / ПРЯМОКУТНИКИ РОЗТЯГУВАННЯ
# # # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None)

# # # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # # #             else:
# # # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # # #                 # Налаштування кольору адаптовано під суворішу типізацію сигналів PySide6
# # # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 120), 1.5, Qt.DashLine))
# # # # # # # # # # #             else:
# # # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.DotLine))
                
# # # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # #             pyqt_item = None

# # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # # #             if pyqt_item:
# # # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
# # # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.SolidLine))
# # # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.SolidLine))
# # # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.SolidLine))
# # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.SolidLine))
# # # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.SolidLine))
# # # # # # # # # # #                 else: pyqt_item.setPen(QPen(QColor(100, 100, 100), 2, Qt.SolidLine))

# # # # # # # # # # #                 pyqt_item.setData(Qt.UserRole, hndl)
# # # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # # #                 }
# # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # # #                 }

# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     # СЛУЖБОВІ МЕТОДИ СИНХРОНІЗАЦІЇ СПИСКІВ
# # # # # # # # # # #     # ---------------------------
# # # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # #         path = QPainterPath()
# # # # # # # # # # #         path.addRect(rect)
# # # # # # # # # # #         matched_items = self.scene.items(path, Qt.IntersectsItemShape)
# # # # # # # # # # #         for item in matched_items:
# # # # # # # # # # #             hndl = item.data(Qt.UserRole)
# # # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # # #             if item.data(Qt.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # # #             self.selected_handles.add(item.data(Qt.UserRole))
# # # # # # # # # # #         self.update_viewer()

# # # # # # # # # # #     def clear_selection(self):
# # # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # # #         self.update_viewer()
# # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # # #         seen = set()
        
# # # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # # # #             layer = entity.dxf.layer if entity.has_dxf_attrib('layer') else "Default"
# # # # # # # # # # #             color_index = entity.dxf.color if entity.has_dxf_attrib('color') else "ByLayer"
# # # # # # # # # # #             linetype = entity.dxf.linetype if entity.has_dxf_attrib('linetype') else "ByLayer"
            
# # # # # # # # # # #             lw_raw = entity.dxf.lineweight if entity.has_dxf_attrib('lineweight') else -1
# # # # # # # # # # #             if lw_raw == -1: lineweight = "ByLayer"
# # # # # # # # # # #             elif lw_raw == -2: lineweight = "ByBlock"
# # # # # # # # # # #             else: lineweight = f"{lw_raw / 100:.2f} мм"

# # # # # # # # # # #             text = ""

# # # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # # #                 cx, cy, cz = entity.dxf.center
# # # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # # #                 diameter = r * 2
# # # # # # # # # # #                 length_of_circle = 2 * math.pi * r
# # # # # # # # # # #                 area = math.pi * (r ** 2)

# # # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ] "
# # # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ] "
# # # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ] "
# # # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ] "
# # # # # # # # # # #                 else: prefix = "🔘 "

# # # # # # # # # # #                 text = (
# # # # # # # # # # #                     f"{prefix}Отвір (ID: {hndl})\n"
# # # # # # # # # # #                     f"  ├─ Центр: X: {cx:.1f}, Y: {cy:.1f}\n"
# # # # # # # # # # #                     f"  ├─ Радіус: {r:.1f} мм | Діаметр: {diameter:.1f} мм\n"
# # # # # # # # # # #                     f"  └─ Шар: {layer} | Товщина: {lineweight}"
# # # # # # # # # # #                 )

# # # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # # #                 x1, y1, z1 = entity.dxf.start
# # # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                
# # # # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z1 - z1)**2)

# # # # # # # # # # #                 lw_value = entity.dxf.get('lineweight', 256)
# # # # # # # # # # #                 if lw_value == 256: lineweight_str = "За шаром"
# # # # # # # # # # #                 elif lw_value < 0: lineweight_str = "Стандартна"
# # # # # # # # # # #                 else: lineweight_str = f"{lw_value / 100:.2f} мм"

# # # # # # # # # # #                 text = (
# # # # # # # # # # #                     f"📏 Лінія (ID: {hndl})\n"
# # # # # # # # # # #                     f"  ├─ Старт: X: {x1:.1f}, Y: {y1:.1f}\n"
# # # # # # # # # # #                     f"  ├─ Кінець: X: {x2:.1f}, Y: {y2:.1f}\n"
# # # # # # # # # # #                     f"  ├─ Товщина лінії: {lineweight_str}\n"
# # # # # # # # # # #                     f"  └─ Довжина: {length:.1f} мм"
# # # # # # # # # # #                 )
# # # # # # # # # # #             else: continue

# # # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # # #             item.setData(Qt.UserRole, hndl)
# # # # # # # # # # #             self.entity_list.addItem(item)
            
# # # # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # # #     import PySide6.QtWidgets as qtw
# # # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # # #     window = MiniCAD()
# # # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# # # # # # # # # # #     window.show()
# # # # # # # # # # #     sys.exit(app.exec_())

# # # # # # # # # # import os
# # # # # # # # # # import sys
# # # # # # # # # # import math
# # # # # # # # # # import copy

# # # # # # # # # # import ezdxf
# # # # # # # # # # import ezdxf.bbox as dxf_bbox

# # # # # # # # # # from PySide6.QtWidgets import (
# # # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # # #     QGroupBox, QGraphicsRectItem, QComboBox
# # # # # # # # # # )
# # # # # # # # # # from PySide6.QtCore import Qt
# # # # # # # # # # from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # # # # from history_manager import HistoryManager


# # # # # # # # # # def patch_ezdxf_entities():
# # # # # # # # # #     from ezdxf.entities import Line
# # # # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # # # #     from ezdxf.entities import Circle
# # # # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # # # patch_ezdxf_entities()


# # # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # # #     def __init__(self):
# # # # # # # # # #         super().__init__()

# # # # # # # # # #         self.setWindowTitle("CAD Двері: Розумна параметризація 2D зон")
# # # # # # # # # #         self.setGeometry(100, 100, 1400, 850)

# # # # # # # # # #         self.dxf_path = "drawing.DXF"
# # # # # # # # # #         self.current_theme = "Темна"  # Дефолтна тема при запуску

# # # # # # # # # #         self.selected_handles = set()
# # # # # # # # # #         self.overlay_items = {}
# # # # # # # # # #         self.original_geometries = {}
# # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # # #         self.stretch_zones = []
# # # # # # # # # #         self.active_zone_index = None

# # # # # # # # # #         self.zones_undo_stack = []
# # # # # # # # # #         self.zones_redo_stack = []

# # # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # # #             sys.exit()

# # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # # # # #         self.history.save_state()
# # # # # # # # # #         self.save_zones_history_state()

# # # # # # # # # #         self.init_ui()
# # # # # # # # # #         self.set_interface_theme(self.current_theme)  # Застосовуємо тему інтерфейсу
# # # # # # # # # #         self.save_original_geometries()
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # #     def init_ui(self):
# # # # # # # # # #         main_widget = QWidget()
# # # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # # #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# # # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # # #         control_panel = QWidget()
# # # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # # #         # --- НОВИЙ БЛОК: ВИБІР ТЕМИ ОФОРМЛЕННЯ ---
# # # # # # # # # #         theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
# # # # # # # # # #         theme_box = QHBoxLayout()
# # # # # # # # # #         theme_box.addWidget(QLabel("Оберіть тему:"))
# # # # # # # # # #         self.theme_combo = QComboBox()
# # # # # # # # # #         self.theme_combo.addItems(["Темна", "Світла"])
# # # # # # # # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # # # # # # # #         theme_box.addWidget(self.theme_combo)
# # # # # # # # # #         theme_group.setLayout(theme_box)
# # # # # # # # # #         control_layout.addWidget(theme_group)

# # # # # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # # # # # #         history_box = QHBoxLayout()
# # # # # # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # # # # # #         self.btn_undo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # # # # # #         self.btn_redo.setStyleSheet("font-weight: bold; padding: 5px;")
# # # # # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # # # # #         history_group.setLayout(history_box)
# # # # # # # # # #         control_layout.addWidget(history_group)
# # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # # #         fix_box = QVBoxLayout()
        
# # # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # # #         self.btn_set_left_fix.setStyleSheet("font-weight: bold;")
# # # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # # #         self.btn_set_right_fix.setStyleSheet("font-weight: bold;")
# # # # # # # # # #         self.btn_set_left_fix.setObjectName("leftFixBtn")
# # # # # # # # # #         self.btn_set_right_fix.setObjectName("rightFixBtn")
# # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # # #         self.btn_set_bottom_fix.setStyleSheet("font-weight: bold;")
# # # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # # # # #         self.btn_set_top_fix.setStyleSheet("font-weight: bold;")
# # # # # # # # # #         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
# # # # # # # # # #         self.btn_set_top_fix.setObjectName("topFixBtn")
# # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # # #         fix_box.addLayout(v_fix_layout)
        
# # # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # # #         zone_box = QVBoxLayout()

# # # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # # #         self.btn_add_zone_x.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)

# # # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # # #         self.btn_add_zone_y.setStyleSheet("font-weight: bold; padding: 4px;")
# # # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)

# # # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)

# # # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон (оберіть для зміни):</b>"))
# # # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# # # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # # #         self.slider_label = QLabel("Оберіть зону деформації зі списку")
# # # # # # # # # #         control_layout.addWidget(self.slider_label)

# # # # # # # # # #         self.slider = QSlider(Qt.Orientation.Horizontal)
# # # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # # #         control_layout.addStretch()

# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     # ЛОГІКА ЗМІНИ ТЕМ ОФОРМЛЕННЯ
# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     def on_theme_changed(self, theme_name):
# # # # # # # # # #         self.current_theme = theme_name
# # # # # # # # # #         self.set_interface_theme(theme_name)
# # # # # # # # # #         self.update_viewer()  # Перемальовуємо графіку під нові кольори сцени

# # # # # # # # # #     def set_interface_theme(self, theme_name):
# # # # # # # # # #         """Зміна стилю правої панелі за допомогою таблиць стилів Qt (QSS)."""
# # # # # # # # # #         if theme_name == "Темна":
# # # # # # # # # #             self.setStyleSheet("""
# # # # # # # # # #                 QMainWindow { background-color: #252526; }
# # # # # # # # # #                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
# # # # # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
# # # # # # # # # #                 QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
# # # # # # # # # #                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
# # # # # # # # # #                 QPushButton:hover { background-color: #505050; }
# # # # # # # # # #                 QPushButton:pressed { background-color: #1e1e1e; }
# # # # # # # # # #                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
# # # # # # # # # #                 QListWidget::item:selected { background-color: #04396c; color: white; }
# # # # # # # # # #                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
# # # # # # # # # #                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
# # # # # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # # # # #                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
# # # # # # # # # #                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
# # # # # # # # # #                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
# # # # # # # # # #                 #topFixBtn { background-color: #524705; color: #fffde7; }
# # # # # # # # # #             """)
# # # # # # # # # #         else:  # Світла тема
# # # # # # # # # #             self.setStyleSheet("""
# # # # # # # # # #                 QMainWindow { background-color: #f3f3f3; }
# # # # # # # # # #                 QWidget { color: #000000; font-family: 'Segoe UI'; }
# # # # # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
# # # # # # # # # #                 QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
# # # # # # # # # #                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
# # # # # # # # # #                 QPushButton:hover { background-color: #d0d0d0; }
# # # # # # # # # #                 QPushButton:pressed { background-color: #cccccc; }
# # # # # # # # # #                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
# # # # # # # # # #                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
# # # # # # # # # #                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
# # # # # # # # # #                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
# # # # # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # # # # #                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
# # # # # # # # # #                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
# # # # # # # # # #                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
# # # # # # # # # #                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
# # # # # # # # # #             """)

# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     # УПРАВЛІННЯ ІСТОРІЄЮ ЗМІН ПРЯМОКУТНИКІВ ЗОН
# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     def save_zones_history_state(self):
# # # # # # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # # # # # #         if len(self.zones_undo_stack) > 30:
# # # # # # # # # #             self.zones_undo_stack.pop(0)

# # # # # # # # # #     def undo(self):
# # # # # # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # #     def redo(self):
# # # # # # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # # # # # #             self.reload_after_history_change()

# # # # # # # # # #     def update_history_buttons_state(self):
# # # # # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # # # # # #     def reload_after_history_change(self):
# # # # # # # # # #         self.is_loading_history = True
# # # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # #         self.update_history_buttons_state()
# # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # #         self.is_loading_history = False

# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     # АВТОГЕНЕРАЦІЯ ЗОН РОЗТЯГУВАННЯ
# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')

# # # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # # #                 return

# # # # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        
# # # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # # #                 break

# # # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # # #             return

# # # # # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # # # # #             self.clear_selection()
# # # # # # # # # #             return

# # # # # # # # # #         if axis == 'X':
# # # # # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # # # #         else:
# # # # # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
            
# # # # # # # # # #         self.clear_selection()

# # # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # # #         self.active_zone_index = None
# # # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # #         self.load_entities_into_list()

# # # # # # # # # #     def load_zones_into_list(self):
# # # # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # # # #         self.zone_list_widget.clear()
# # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # # # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # # #         if not selected:
# # # # # # # # # #             self.active_zone_index = None
# # # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # # #             return

# # # # # # # # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # # #         self.update_viewer()

# # # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # # #             return

# # # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # # #                 new_cx = self.calculate_cascade_shift(cx, 'X', hndl)
# # # # # # # # # #                 new_cy = self.calculate_cascade_shift(cy, 'Y', hndl)
# # # # # # # # # #                 entity.dxf.center = (new_cx, new_cy, cz)

# # # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # # #                 ex, ey, ez = orig["end"]
                
# # # # # # # # # #                 new_sx = self.calculate_cascade_shift(sx, 'X', hndl)
# # # # # # # # # #                 new_sy = self.calculate_cascade_shift(sy, 'Y', hndl)
# # # # # # # # # #                 new_ex = self.calculate_cascade_shift(ex, 'X', hndl)
# # # # # # # # # #                 new_ey = self.calculate_cascade_shift(ey, 'Y', hndl)
                
# # # # # # # # # #                 entity.dxf.start = (new_sx, new_sy, sz)
# # # # # # # # # #                 entity.dxf.end = (new_ex, new_ey, ez)

# # # # # # # # # #         self.update_viewer()

# # # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # # #         shifted_val = orig_val
# # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # # #             z_min = zone['min']
# # # # # # # # # #             z_max = zone['max']
# # # # # # # # # #             val = zone['stretch_val']

# # # # # # # # # #             if orig_val >= z_max:
# # # # # # # # # #                 shifted_val += val
# # # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # # #                 width = z_max - z_min
# # # # # # # # # #                 if width > 0:
# # # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # # #         return shifted_val

# # # # # # # # # #     def on_slider_released(self):
# # # # # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # # # # #         active_zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # # #         stretch_amount = active_zone['stretch_val']
# # # # # # # # # #         active_axis = active_zone['axis']
# # # # # # # # # #         active_max = active_zone['max']

# # # # # # # # # #         active_zone['max'] += stretch_amount

# # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # #             if idx == self.active_zone_index or zone['axis'] != active_axis:
# # # # # # # # # #                 continue
# # # # # # # # # #             if zone['min'] >= active_max:
# # # # # # # # # #                 zone['min'] += stretch_amount
# # # # # # # # # #                 zone['max'] += stretch_amount

# # # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # # #         self.history.save_state()
# # # # # # # # # #         self.history.clear_redo()
# # # # # # # # # #         self.save_zones_history_state()
# # # # # # # # # #         self.zones_redo_stack.clear()
# # # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # # #         self.save_original_geometries()

# # # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # # #         self.slider.setValue(0)
# # # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # # #         self.load_zones_into_list()
# # # # # # # # # #         self.load_entities_into_list()
# # # # # # # # # #         self.update_viewer()

# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     # ОНОВЛЕНА ВІЗУАЛІЗАЦІЯ З УРАХУВАННЯМ ТЕМИ КРЕСЛЕННЯ
# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     def update_viewer(self):
# # # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # # #         self.overlay_items.clear()

# # # # # # # # # #         # Налаштування кольору тла графічного вікна залежно від теми
# # # # # # # # # #         if self.current_theme == "Темна":
# # # # # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))  # Глибокий темно-сірий (як в AutoCAD)
# # # # # # # # # #             base_line_color = QColor(220, 220, 220)                  # Світло-сірі контрастні лінії деталей
# # # # # # # # # #         else:
# # # # # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))  # Чистий білий фон
# # # # # # # # # #             base_line_color = QColor(80, 80, 80)                         # Темні лінії деталей

# # # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # # #         try:
# # # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # # #         except Exception:
# # # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # # #         # МАЛЮЄМО НАПІВПРОЗОРІ КВАДРАТИ / ПРЯМОКУТНИКИ РОЗТЯГУВАННЯ
# # # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']

# # # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # # #             else:
# # # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # # # # # # # #             else:
# # # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 15))) 
# # # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 50), 1, Qt.PenStyle.DotLine))
                
# # # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # #             pyqt_item = None

# # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # # #             if pyqt_item:
# # # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 140, 255), 3, Qt.PenStyle.SolidLine))
# # # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # # #                 else: 
# # # # # # # # # #                     # Використовуємо динамічно розрахований під тему базовий колір ліній контурів
# # # # # # # # # #                     pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))

# # # # # # # # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # # #     def save_original_geometries(self):
# # # # # # # # # #         self.original_geometries.clear()
# # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # # #                 }
# # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # # #                 }

# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     # СЛУЖБОВІ МЕТОДИ СИНХРОНІЗАЦІЇ СПИСКІВ
# # # # # # # # # #     # ---------------------------
# # # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # #         self.update_viewer()

# # # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # #         path = QPainterPath()
# # # # # # # # # #         path.addRect(rect)
# # # # # # # # # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # # # # # # # # #         for item in matched_items:
# # # # # # # # # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # # #         self.update_viewer()

# # # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # # # # # # # #         self.update_viewer()

# # # # # # # # # #     def clear_selection(self):
# # # # # # # # # #         self.selected_handles.clear()
# # # # # # # # # #         self.update_viewer()
# # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # # #         self.entity_list.clear()
# # # # # # # # # #         seen = set()
        
# # # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # # #             tp = entity.dxftype()
# # # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # # #             layer = entity.dxf.layer if entity.has_dxf_attrib('layer') else "Default"
# # # # # # # # # #             color_index = entity.dxf.color if entity.has_dxf_attrib('color') else "ByLayer"
# # # # # # # # # #             linetype = entity.dxf.linetype if entity.has_dxf_attrib('linetype') else "ByLayer"
            
# # # # # # # # # #             lw_raw = entity.dxf.lineweight if entity.has_dxf_attrib('lineweight') else -1
# # # # # # # # # #             if lw_raw == -1: lineweight = "ByLayer"
# # # # # # # # # #             elif lw_raw == -2: lineweight = "ByBlock"
# # # # # # # # # #             else: lineweight = f"{lw_raw / 100:.2f} мм"

# # # # # # # # # #             text = ""

# # # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # # #                 cx, cy, cz = entity.dxf.center
# # # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
                
# # # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # # #                 diameter = r * 2
# # # # # # # # # #                 length_of_circle = 2 * math.pi * r
# # # # # # # # # #                 area = math.pi * (r ** 2)

# # # # # # # # # #                 if hndl in self.left_fixed_handles: prefix = "🟢 [ЛІВИЙ] "
# # # # # # # # # #                 elif hndl in self.right_fixed_handles: prefix = "🔴 [ПРАВИЙ] "
# # # # # # # # # #                 elif hndl in self.bottom_fixed_handles: prefix = "🔵 [НИЖНІЙ] "
# # # # # # # # # #                 elif hndl in self.top_fixed_handles: prefix = "🟡 [ВЕРХНІЙ] "
# # # # # # # # # #                 else: prefix = "🔘 "

# # # # # # # # # #                 text = (
# # # # # # # # # #                     f"{prefix}Отвір (ID: {hndl})\n"
# # # # # # # # # #                     f"  ├─ Центр: X: {cx:.1f}, Y: {cy:.1f}\n"
# # # # # # # # # #                     f"  ├─ Радіус: {r:.1f} мм | Діаметр: {diameter:.1f} мм\n"
# # # # # # # # # #                     f"  └─ Шар: {layer} | Товщина: {lineweight}"
# # # # # # # # # #                 )

# # # # # # # # # #             elif tp == "LINE":
# # # # # # # # # #                 x1, y1, z1 = entity.dxf.start
# # # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                
# # # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z1 - z1)**2)

# # # # # # # # # #                 lw_value = entity.dxf.get('lineweight', 256)
# # # # # # # # # #                 if lw_value == 256: lineweight_str = "За шаром"
# # # # # # # # # #                 elif lw_value < 0: lineweight_str = "Стандартна"
# # # # # # # # # #                 else: lineweight_str = f"{lw_value / 100:.2f} мм"

# # # # # # # # # #                 text = (
# # # # # # # # # #                     f"📏 Лінія (ID: {hndl})\n"
# # # # # # # # # #                     f"  ├─ Старт: X: {x1:.1f}, Y: {y1:.1f}\n"
# # # # # # # # # #                     f"  ├─ Кінець: X: {x2:.1f}, Y: {y2:.1f}\n"
# # # # # # # # # #                     f"  ├─ Товщина лінії: {lineweight_str}\n"
# # # # # # # # # #                     f"  └─ Довжина: {length:.1f} мм"
# # # # # # # # # #                 )
# # # # # # # # # #             else: continue

# # # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # # # # #             self.entity_list.addItem(item)
            
# # # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # # if __name__ == "__main__":
# # # # # # # # # #     import PySide6.QtWidgets as qtw
# # # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # # #     window = MiniCAD()
# # # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
# # # # # # # # # #     window.show()
# # # # # # # # # #     sys.exit(app.exec())


# # # # # # # # # import os
# # # # # # # # # import sys
# # # # # # # # # import math
# # # # # # # # # import copy  # Для глибокого копіювання станів прямокутників зон в Undo/Redo

# # # # # # # # # import ezdxf
# # # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж без крашів

# # # # # # # # # # Сучасні імпорти під PySide6
# # # # # # # # # from PySide6.QtWidgets import (
# # # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # # #     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit
# # # # # # # # # )
# # # # # # # # # from PySide6.QtCore import Qt
# # # # # # # # # from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # # Імпорти кастомних модулів вашого проекту:
# # # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # # # from history_manager import HistoryManager


# # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # def patch_ezdxf_entities():
# # # # # # # # #     """
# # # # # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf.
# # # # # # # # #     """
# # # # # # # # #     from ezdxf.entities import Line
# # # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # # #     from ezdxf.entities import Circle
# # # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # # # Викликаємо патч сутностей перед запуском всього CAD-редактора
# # # # # # # # # patch_ezdxf_entities()
# # # # # # # # # # ---------------------------------------------------------------------------


# # # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # # #     def __init__(self):
# # # # # # # # #         super().__init__()

# # # # # # # # #         self.setWindowTitle("CAD Двері: Розумна параметризація 2D зон")
# # # # # # # # #         self.setGeometry(100, 100, 1400, 900)

# # # # # # # # #         self.dxf_path = "drawing.DXF"
# # # # # # # # #         self.current_theme = "Темна"  # Дефолтна тема при запуску

# # # # # # # # #         self.selected_handles = set()
# # # # # # # # #         self.overlay_items = {}
# # # # # # # # #         self.original_geometries = {}
# # # # # # # # #         self.is_loading_history = False

# # # # # # # # #         # Списки для жорстких зон фіксації
# # # # # # # # #         self.left_fixed_handles = set()
# # # # # # # # #         self.right_fixed_handles = set()
# # # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # # #         self.stretch_zones = []
# # # # # # # # #         self.active_zone_index = None

# # # # # # # # #         # Стек для синхронного відкоту прямокутників разом із DXF-файлом
# # # # # # # # #         self.zones_undo_stack = []
# # # # # # # # #         self.zones_redo_stack = []

# # # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # # #             sys.exit()

# # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # # # #         # Ініціалізація історії змін DXF
# # # # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # # # #         self.history.save_state()
# # # # # # # # #         self.save_zones_history_state()  # Зберігаємо стартовий стан прямокутників

# # # # # # # # #         self.init_ui()
# # # # # # # # #         self.set_interface_theme(self.current_theme)  # Застосовуємо тему інтерфейсу
# # # # # # # # #         self.save_original_geometries()
# # # # # # # # #         self.recalculate_current_dxf_dimensions()  # Зчитуємо початкові розміри полотна
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_entities_into_list()

# # # # # # # # #     def init_ui(self):
# # # # # # # # #         main_widget = QWidget()
# # # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # # #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# # # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # # #         control_panel = QWidget()
# # # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # # #         # --- БЛОК: АВТОМАТИЧНИЙ КУРС НА НОВІ ГАБАРИТИ ---
# # # # # # # # #         auto_scale_group = QGroupBox("🚀 Авто-адаптація під нове замовлення")
# # # # # # # # #         auto_scale_box = QVBoxLayout()

# # # # # # # # #         self.lbl_current_size = QLabel("Поточний розмір моделі: <b>0 х 0 мм</b>")
# # # # # # # # #         self.lbl_current_size.setStyleSheet("color: #4fc3f7; font-size: 13px;")
# # # # # # # # #         auto_scale_box.addWidget(self.lbl_current_size)

# # # # # # # # #         input_layout = QHBoxLayout()
# # # # # # # # #         input_layout.addWidget(QLabel("Нова Ширина (X):"))
# # # # # # # # #         self.input_target_width = QLineEdit()
# # # # # # # # #         self.input_target_width.setPlaceholderText("напр. 1000")
# # # # # # # # #         input_layout.addWidget(self.input_target_width)
        
# # # # # # # # #         input_layout.addWidget(QLabel("Нова Висота (Y):"))
# # # # # # # # #         self.input_target_height = QLineEdit()
# # # # # # # # #         self.input_target_height.setPlaceholderText("напр. 2050")
# # # # # # # # #         input_layout.addWidget(self.input_target_height)
# # # # # # # # #         auto_scale_box.addLayout(input_layout)

# # # # # # # # #         self.btn_apply_auto_scale = QPushButton("⚡ Розрахувати та деформувати під розмір")
# # # # # # # # #         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
# # # # # # # # #         self.btn_apply_auto_scale.clicked.connect(self.process_automatic_dimension_scale)
# # # # # # # # #         auto_scale_box.addWidget(self.btn_apply_auto_scale)

# # # # # # # # #         auto_scale_group.setLayout(auto_scale_box)
# # # # # # # # #         control_layout.addWidget(auto_scale_group)

# # # # # # # # #         # --- БЛОК СТИЛЮ ТА ТЕМИ ---
# # # # # # # # #         theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
# # # # # # # # #         theme_box = QHBoxLayout()
# # # # # # # # #         theme_box.addWidget(QLabel("Тема:"))
# # # # # # # # #         self.theme_combo = QComboBox()
# # # # # # # # #         self.theme_combo.addItems(["Темна", "Світла"])
# # # # # # # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # # # # # # #         theme_box.addWidget(self.theme_combo)
# # # # # # # # #         theme_group.setLayout(theme_box)
# # # # # # # # #         control_layout.addWidget(theme_group)

# # # # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # # # # #         history_box = QHBoxLayout()
# # # # # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # # # #         history_group.setLayout(history_box)
# # # # # # # # #         control_layout.addWidget(history_group)
# # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # # #         fix_box = QVBoxLayout()
# # # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # # #         self.btn_set_left_fix.setObjectName("leftFixBtn")
# # # # # # # # #         self.btn_set_right_fix.setObjectName("rightFixBtn")
# # # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # # # #         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
# # # # # # # # #         self.btn_set_top_fix.setObjectName("topFixBtn")
# # # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # # #         fix_box.addLayout(v_fix_layout)
# # # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # # #         zone_box = QVBoxLayout()
# # # # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)
# # # # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)
# # # # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # # #         zone_box.addWidget(self.btn_clear_zones)
# # # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
# # # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # # #         self.entity_list = QListWidget()
# # # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# # # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # # #         self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
# # # # # # # # #         control_layout.addWidget(self.slider_label)
# # # # # # # # #         self.slider = QSlider(Qt.Orientation.Horizontal)
# # # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # # #         control_layout.addStretch()

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # УПРАВЛІННЯ ІСТОРІЄЮ ЗМІН ПРЯМОКУТНИКІВ ЗОН
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def save_zones_history_state(self):
# # # # # # # # #         """Зберігає глибоку копію масиву прямокутників зон в Undo-стек."""
# # # # # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # # # # #         if len(self.zones_undo_stack) > 30:
# # # # # # # # #             self.zones_undo_stack.pop(0)

# # # # # # # # #     def undo(self):
# # # # # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # # # # #             self.reload_after_history_change()

# # # # # # # # #     def redo(self):
# # # # # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # # # # #             self.reload_after_history_change()

# # # # # # # # #     def update_history_buttons_state(self):
# # # # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # # # # #     def reload_after_history_change(self):
# # # # # # # # #         self.is_loading_history = True
# # # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # # # #         self.save_original_geometries()
        
# # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # #         self.slider.setValue(0)
# # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # #         self.recalculate_current_dxf_dimensions()
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_zones_into_list()
# # # # # # # # #         self.load_entities_into_list()
# # # # # # # # #         self.update_history_buttons_state()
# # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # #         self.is_loading_history = False

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # АВТОМАТИЧНИЙ КУРС НА НОВІ ГАБАРИТИ ДВЕРЕЙ
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def recalculate_current_dxf_dimensions(self):
# # # # # # # # #         """Обчислює повну ширину та висоту контуру завантаженої моделі дверей."""
# # # # # # # # #         try:
# # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # #             self.current_dxf_width = bounds.extmax[0] - bounds.extmin[0]
# # # # # # # # #             self.current_dxf_height = bounds.extmax[1] - bounds.extmin[1]
# # # # # # # # #         except Exception:
# # # # # # # # #             self.current_dxf_width = 1000.0
# # # # # # # # #             self.current_dxf_height = 2040.0
            
# # # # # # # # #         self.lbl_current_size.setText(
# # # # # # # # #             f"Поточний розмір моделі: <b>{self.current_dxf_width:.0f} х {self.current_dxf_height:.0f} мм</b>"
# # # # # # # # #         )

# # # # # # # # #     def process_automatic_dimension_scale(self):
# # # # # # # # #         """Автоматично розраховує дельту і ділить міліметри приросту між створеними порожнечами."""
# # # # # # # # #         if not self.stretch_zones:
# # # # # # # # #             self.lbl_current_size.setText("<font color='red'>Помилка: Створіть бодай одну зону стрейчу!</font>")
# # # # # # # # #             return

# # # # # # # # #         raw_w = self.input_target_width.text().strip()
# # # # # # # # #         raw_h = self.input_target_height.text().strip()

# # # # # # # # #         target_w = float(raw_w) if raw_w else self.current_dxf_width
# # # # # # # # #         target_h = float(raw_h) if raw_h else self.current_dxf_height

# # # # # # # # #         delta_x = target_w - self.current_dxf_width
# # # # # # # # #         delta_y = target_h - self.current_dxf_height

# # # # # # # # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # # # # # # # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # #                 zone['stretch_val'] = share_delta_x
# # # # # # # # #             elif zone['axis'] == 'Y':
# # # # # # # # #                 zone['stretch_val'] = share_delta_y

# # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # #                 entity.dxf.center = (
# # # # # # # # #                     self.calculate_cascade_shift(cx, 'X', hndl),
# # # # # # # # #                     self.calculate_cascade_shift(cy, 'Y', hndl),
# # # # # # # # #                     cz
# # # # # # # # #                 )
# # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # #                 ex, ey, ez = orig["end"]
# # # # # # # # #                 entity.dxf.start = (
# # # # # # # # #                     self.calculate_cascade_shift(sx, 'X', hndl),
# # # # # # # # #                     self.calculate_cascade_shift(sy, 'Y', hndl),
# # # # # # # # #                     sz
# # # # # # # # #                 )
# # # # # # # # #                 entity.dxf.end = (
# # # # # # # # #                     self.calculate_cascade_shift(ex, 'X', hndl),
# # # # # # # # #                     self.calculate_cascade_shift(ey, 'Y', hndl),
# # # # # # # # #                     ez
# # # # # # # # #                 )

# # # # # # # # #         self.on_slider_released()
# # # # # # # # #         self.input_target_width.clear()
# # # # # # # # #         self.input_target_height.clear()

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # УПРАВЛІННЯ ТЕМАМИ ІНТЕРФЕЙСУ
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def on_theme_changed(self, theme_name):
# # # # # # # # #         self.current_theme = theme_name
# # # # # # # # #         self.set_interface_theme(theme_name)
# # # # # # # # #         self.update_viewer()

# # # # # # # # #     def set_interface_theme(self, theme_name):
# # # # # # # # #         if theme_name == "Темна":
# # # # # # # # #             self.setStyleSheet("""
# # # # # # # # #                 QMainWindow { background-color: #252526; }
# # # # # # # # #                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
# # # # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
# # # # # # # # #                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
# # # # # # # # #                 QPushButton:hover { background-color: #505050; }
# # # # # # # # #                 QLineEdit { background-color: #1e1e1e; border: 1px solid #555555; color: white; padding: 4px; }
# # # # # # # # #                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
# # # # # # # # #                 QListWidget::item:selected { background-color: #04396c; color: white; }
# # # # # # # # #                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
# # # # # # # # #                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
# # # # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # # # #                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
# # # # # # # # #                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
# # # # # # # # #                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
# # # # # # # # #                 #topFixBtn { background-color: #524705; color: #fffde7; }
# # # # # # # # #             """)
# # # # # # # # #         else:
# # # # # # # # #             self.setStyleSheet("""
# # # # # # # # #                 QMainWindow { background-color: #f3f3f3; }
# # # # # # # # #                 QWidget { color: #000000; font-family: 'Segoe UI'; }
# # # # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
# # # # # # # # #                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
# # # # # # # # #                 QPushButton:hover { background-color: #d0d0d0; }
# # # # # # # # #                 QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: black; padding: 4px; }
# # # # # # # # #                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
# # # # # # # # #                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
# # # # # # # # #                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
# # # # # # # # #                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
# # # # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # # # #                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
# # # # # # # # #                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
# # # # # # # # #                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
# # # # # # # # #                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
# # # # # # # # #             """)

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # ПРИВ'ЯЗКА ФУРНІТУРИ ДО СТОРІН ПОЛОТНА
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def assign_to_left_fix(self):
# # # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_entities_into_list()

# # # # # # # # #     def assign_to_right_fix(self):
# # # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_entities_into_list()

# # # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_entities_into_list()

# # # # # # # # #     def assign_to_top_fix(self):
# # # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_entities_into_list()

# # # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')

# # # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # # #                 return

# # # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
# # # # # # # # #         self.load_zones_into_list()
        
# # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # # #                 break

# # # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # # #             return

# # # # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # # # #             self.clear_selection()
# # # # # # # # #             return

# # # # # # # # #         if axis == 'X':
# # # # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # # #         else:
# # # # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# # # # # # # # #         self.clear_selection()

# # # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # # #         self.stretch_zones.clear()
# # # # # # # # #         self.active_zone_index = None
# # # # # # # # #         self.slider.setEnabled(False)
# # # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.load_zones_into_list()
# # # # # # # # #         self.load_entities_into_list()

# # # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # # #         if not selected:
# # # # # # # # #             self.active_zone_index = None
# # # # # # # # #             self.slider.setEnabled(False)
# # # # # # # # #             return

# # # # # # # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # #         self.slider.setEnabled(True)
# # # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # # #         self.slider.blockSignals(False)
# # # # # # # # #         self.update_viewer()

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # МАТЕМАТИКА КА-СКАДНОГО ЗСУВУ ДЛЯ 2ОХ ОСЕЙ
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # # #             return

# # # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # # #                 entity.dxf.center = (
# # # # # # # # #                     self.calculate_cascade_shift(cx, 'X', hndl),
# # # # # # # # #                     self.calculate_cascade_shift(cy, 'Y', hndl),
# # # # # # # # #                     cz
# # # # # # # # #                 )
# # # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # # #                 ex, ey, ez = orig["end"]
# # # # # # # # #                 entity.dxf.start = (
# # # # # # # # #                     self.calculate_cascade_shift(sx, 'X', hndl),
# # # # # # # # #                     self.calculate_cascade_shift(sy, 'Y', hndl),
# # # # # # # # #                     sz
# # # # # # # # #                 )
# # # # # # # # #                 entity.dxf.end = (
# # # # # # # # #                     self.calculate_cascade_shift(ex, 'X', hndl),
# # # # # # # # #                     self.calculate_cascade_shift(ey, 'Y', hndl),
# # # # # # # # #                     ez
# # # # # # # # #                 )

# # # # # # # # #         self.update_viewer()

# # # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # # #         if axis == 'X' and hndl:
# # # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # # #         shifted_val = orig_val
# # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # # #             z_min = zone['min']
# # # # # # # # #             z_max = zone['max']
# # # # # # # # #             val = zone['stretch_val']

# # # # # # # # #             if orig_val >= z_max:
# # # # # # # # #                 shifted_val += val
# # # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # # #                 width = z_max - z_min
# # # # # # # # #                 if width > 0:
# # # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # # #         return shifted_val

# # # # # # # # #     def on_slider_released(self):
# # # # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # # # #         active_zone = self.stretch_zones[self.active_zone_index]
# # # # # # # # #         stretch_amount = active_zone['stretch_val']
# # # # # # # # #         active_axis = active_zone['axis']
# # # # # # # # #         active_max = active_zone['max']

# # # # # # # # #         active_zone['max'] += stretch_amount

# # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # #             if idx == self.active_zone_index or zone['axis'] != active_axis:
# # # # # # # # #                 continue
# # # # # # # # #             if zone['min'] >= active_max:
# # # # # # # # #                 zone['min'] += stretch_amount
# # # # # # # # #                 zone['max'] += stretch_amount

# # # # # # # # #         for zone in self.stretch_zones:
# # # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # # #         self.history.save_state()
# # # # # # # # #         self.history.clear_redo()
# # # # # # # # #         self.save_zones_history_state()
# # # # # # # # #         self.zones_redo_stack.clear()
# # # # # # # # #         self.update_history_buttons_state()

# # # # # # # # #         self.save_original_geometries()
# # # # # # # # #         self.recalculate_current_dxf_dimensions()

# # # # # # # # #         self.slider.blockSignals(True)
# # # # # # # # #         self.slider.setValue(0)
# # # # # # # # #         self.slider.blockSignals(False)

# # # # # # # # #         self.load_zones_into_list()
# # # # # # # # #         self.load_entities_into_list()
# # # # # # # # #         self.update_viewer()

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # КРИТИЧНО НАОЧНИЙ МЕТОД ЗБЕРЕЖЕННЯ ОРИГІНАЛЬНОЇ ГЕОМЕТРІЇ (ДОДАНО НАЗАД)
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def save_original_geometries(self):
# # # # # # # # #         """Зберігає чисті стартові координати шаблону дверей для правильної каскадної деформації."""
# # # # # # # # #         self.original_geometries.clear()
# # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # #             tp = entity.dxftype()
# # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # # #                 }
# # # # # # # # #             elif tp == "LINE":
# # # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # # #                 }

# # # # # # # # #     # ---------------------------
# # # # # # # # #     # ВІЗУАЛІЗАЦІЯ СЦЕНИ CAD В РЕАЛЬНОМУ ЧАСІ
# # # # # # # # #     # ---------------------------
# # # # # # # # #     def update_viewer(self):
# # # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # # #         self.view.setScene(self.scene)
# # # # # # # # #         self.overlay_items.clear()

# # # # # # # # #         if self.current_theme == "Темна":
# # # # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # # # # # # # #             base_line_color = QColor(220, 220, 220)
# # # # # # # # #         else:
# # # # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # # # # # # # #             base_line_color = QColor(80, 80, 80)

# # # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # # #         try:
# # # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # # #         except Exception:
# # # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']

# # # # # # # # #             if zone['axis'] == 'X':
# # # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # # #             else:
# # # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # # #             if idx == self.active_zone_index:
# # # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # # # # # # #             else:
# # # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # #             hndl = entity.dxf.handle
# # # # # # # # #             tp = entity.dxftype()
# # # # # # # # #             pyqt_item = None

# # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # #                 r = entity.dxf.radius
# # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # # #             elif tp == "LINE":
# # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # # #             if pyqt_item:
# # # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))

# # # # # # # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # # #         self.selected_handles = {handle}
# # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # #         self.update_viewer()

# # # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # # #         self.selected_handles.clear()
# # # # # # # # #         path = QPainterPath()
# # # # # # # # #         path.addRect(rect)
# # # # # # # # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # # # # # # # #         for item in matched_items:
# # # # # # # # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # # #         self.sync_list_from_handles()
# # # # # # # # #         self.update_viewer()

# # # # # # # # #     def sync_list_from_handles(self):
# # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # # #             item = self.entity_list.item(i)
# # # # # # # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # #     def on_list_selection_changed(self):
# # # # # # # # #         self.selected_handles.clear()
# # # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # # # # # # #         self.update_viewer()

# # # # # # # # #     def clear_selection(self):
# # # # # # # # #         self.selected_handles.clear()
# # # # # # # # #         self.update_viewer()
# # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # #         self.entity_list.clearSelection()
# # # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # # #     def load_entities_into_list(self):
# # # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # # #         self.entity_list.clear()
# # # # # # # # #         seen = set()
# # # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # # #             tp = entity.dxftype()
# # # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # # #             if tp == "CIRCLE":
# # # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
# # # # # # # # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # # # # # # # #             elif tp == "LINE":
# # # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
# # # # # # # # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {length:.1f} мм"
# # # # # # # # #             else: continue

# # # # # # # # #             item = QListWidgetItem(text)
# # # # # # # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # # # #             self.entity_list.addItem(item)
# # # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # # if __name__ == "__main__":
# # # # # # # # #     import PySide6.QtWidgets as qtw
# # # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # # #     window = MiniCAD()
# # # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
# # # # # # # # #     window.show()
# # # # # # # # #     sys.exit(app.exec())

# # # Остання найстабільніша версія з усіма критично важливими функціями, включаючи збереження оригінальної геометрії для коректної каскадної деформації та автоматичне визначення зон між фіксованими ручками. Цей код є основою для подальшого розвитку та оптимізації вашого параметризатора дверей.

# # # # # # # # import os
# # # # # # # # import sys
# # # # # # # # import math
# # # # # # # # import copy  # Для глибокого копіювання станів прямокутників зон в Undo/Redo

# # # # # # # # import ezdxf
# # # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж сцени

# # # # # # # # # Сучасні імпорти під PySide6                                                                   
# # # # # # # # from PySide6.QtWidgets import (
# # # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # # #     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit
# # # # # # # # )
# # # # # # # # from PySide6.QtCore import Qt
# # # # # # # # from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # # Імпорти кастомних модулів вашого проекту:
# # # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # # from history_manager import HistoryManager


# # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # def patch_ezdxf_entities():
# # # # # # # #     """
# # # # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf.
# # # # # # # #     """
# # # # # # # #     from ezdxf.entities import Line
# # # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # # #     from ezdxf.entities import Circle
# # # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)


# # # # # # # # patch_ezdxf_entities()
# # # # # # # # # ---------------------------------------------------------------------------


# # # # # # # # class MiniCAD(QMainWindow):
# # # # # # # #     def __init__(self):
# # # # # # # #         super().__init__()

# # # # # # # #         self.setWindowTitle("Двері: Параметризатор з ручним заданням габаритів")
# # # # # # # #         self.setGeometry(100, 100, 1400, 900)

# # # # # # # #         self.dxf_path = "drawing.DXF"
# # # # # # # #         self.current_theme = "Світла"  

# # # # # # # #         self.selected_handles = set()
# # # # # # # #         self.overlay_items = {}
# # # # # # # #         self.original_geometries = {}
# # # # # # # #         self.is_loading_history = False

# # # # # # # #         # Списки для жорстких зон фіксації
# # # # # # # #         self.left_fixed_handles = set()
# # # # # # # #         self.right_fixed_handles = set()
# # # # # # # #         self.bottom_fixed_handles = set()
# # # # # # # #         self.top_fixed_handles = set()
        
# # # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # # #         self.stretch_zones = []
# # # # # # # #         self.active_zone_index = None

# # # # # # # #         self.zones_undo_stack = []
# # # # # # # #         self.zones_redo_stack = []

# # # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # # #             sys.exit()

# # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

    
# # # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # # #         self.history.save_state()
# # # # # # # #         self.save_zones_history_state()  

# # # # # # # #         self.init_ui()
# # # # # # # #         self.set_interface_theme(self.current_theme)  
# # # # # # # #         self.save_original_geometries()
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_entities_into_list()

# # # # # # # #     def init_ui(self):
# # # # # # # #         main_widget = QWidget()
# # # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # # #         self.setCentralWidget(main_widget)

# # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # # #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# # # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # # #         control_panel = QWidget()
# # # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # # #         auto_scale_group = QGroupBox("Розміри замовлення")
# # # # # # # #         auto_scale_box = QVBoxLayout()


# # # # # # # #         width_layout = QHBoxLayout()
# # # # # # # #         width_layout.addWidget(QLabel("<b>Ширина (X):</b>  Поточна:"))
# # # # # # # #         self.input_current_width = QLineEdit()
# # # # # # # #         self.input_current_width.setPlaceholderText("напр. 1000")
# # # # # # # #         width_layout.addWidget(self.input_current_width)
        
# # # # # # # #         width_layout.addWidget(QLabel(" Нова:"))
# # # # # # # #         self.input_target_width = QLineEdit()
# # # # # # # #         self.input_target_width.setPlaceholderText("напр. 1010")
# # # # # # # #         width_layout.addWidget(self.input_target_width)
# # # # # # # #         auto_scale_box.addLayout(width_layout)

# # # # # # # #         # Поля вертикальних габаритів (Висота Y)
# # # # # # # #         height_layout = QHBoxLayout()
# # # # # # # #         height_layout.addWidget(QLabel("<b>Висота (Y):</b>  Поточна:"))
# # # # # # # #         self.input_current_height = QLineEdit()
# # # # # # # #         self.input_current_height.setPlaceholderText("напр. 2040")
# # # # # # # #         height_layout.addWidget(self.input_current_height)
        
# # # # # # # #         height_layout.addWidget(QLabel(" Нова:"))
# # # # # # # #         self.input_target_height = QLineEdit()
# # # # # # # #         self.input_target_height.setPlaceholderText("напр. 2050")
# # # # # # # #         height_layout.addWidget(self.input_target_height)
# # # # # # # #         auto_scale_box.addLayout(height_layout)

# # # # # # # #         # Статусне повідомлення розрахунків
# # # # # # # #         self.lbl_status_calc = QLabel("Введіть розміри та натисніть кнопку нижче")
# # # # # # # #         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
# # # # # # # #         auto_scale_box.addWidget(self.lbl_status_calc)

# # # # # # # #         # Кнопка запуску перетворення
# # # # # # # #         self.btn_apply_auto_scale = QPushButton(" Автоматично розрахувати дельту та змінити")
# # # # # # # #         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
# # # # # # # #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# # # # # # # #         auto_scale_box.addWidget(self.btn_apply_auto_scale)

# # # # # # # #         auto_scale_group.setLayout(auto_scale_box)
# # # # # # # #         control_layout.addWidget(auto_scale_group)

# # # # # # # #         # --- БЛОК СТИЛЮ ТА ТЕМИ ---
# # # # # # # #         theme_group = QGroupBox(" Стиль оформлення (Тема)")
# # # # # # # #         theme_box = QHBoxLayout()
# # # # # # # #         theme_box.addWidget(QLabel("Тема:"))
# # # # # # # #         self.theme_combo = QComboBox()
# # # # # # # #         self.theme_combo.addItems(["Світла", "Темна"])
# # # # # # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # # # # # #         theme_box.addWidget(self.theme_combo)
# # # # # # # #         theme_group.setLayout(theme_box)
# # # # # # # #         control_layout.addWidget(theme_group)

# # # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # # # #         history_box = QHBoxLayout()
# # # # # # # #         self.btn_undo = QPushButton(" Назад (Undo)")
# # # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ")
# # # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # # #         history_group.setLayout(history_box)
# # # # # # # #         control_layout.addWidget(history_group)
# # # # # # # #         self.update_history_buttons_state()

# # # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # # #         fix_box = QVBoxLayout()
# # # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # # #         self.btn_set_left_fix.setObjectName("leftFixBtn")
# # # # # # # #         self.btn_set_right_fix.setObjectName("rightFixBtn")
# # # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # # #         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
# # # # # # # #         self.btn_set_top_fix.setObjectName("topFixBtn")
# # # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # # #         fix_box.addLayout(v_fix_layout)
# # # # # # # #         fix_group.setLayout(fix_box)
# # # # # # # #         control_layout.addWidget(fix_group)

# # # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # # #         zone_box = QVBoxLayout()
# # # # # # # #         self.btn_add_zone_x = QPushButton(" Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # # #         zone_box.addWidget(self.btn_add_zone_x)
# # # # # # # #         self.btn_add_zone_y = QPushButton(" Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # # #         zone_box.addWidget(self.btn_add_zone_y)
# # # # # # # #         self.btn_clear_zones = QPushButton(" Скинути всі зони та фіксації")
# # # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # # #         zone_box.addWidget(self.btn_clear_zones)
# # # # # # # #         zone_group.setLayout(zone_box)
# # # # # # # #         control_layout.addWidget(zone_group)

# # # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
# # # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # # #         self.entity_list = QListWidget()
# # # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# # # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # # #         self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
# # # # # # # #         control_layout.addWidget(self.slider_label)
# # # # # # # #         self.slider = QSlider(Qt.Orientation.Horizontal)
# # # # # # # #         self.slider.setRange(0, 600)
# # # # # # # #         self.slider.setEnabled(False)
# # # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # # #         control_layout.addWidget(self.slider)

# # # # # # # #         control_layout.addStretch()

# # # # # # # #     # ---------------------------
# # # # # # # #     # ЛОГІКА ОБЧИСЛЕННЯ ЧИСТОЇ ДЕЛЬТИ З УРАХУВАННЯМ РУЧНИХ ПРИПУСКІВ
# # # # # # # #     # ---------------------------
# # # # # # # #     def process_manual_input_dimension_scale(self):
# # # # # # # #         """
# # # # # # # #         НОВА ЛОГІКА: Бере введені технологом вручну поточні габарити виробу,
# # # # # # # #         віднімає їх від бажаних нових, знаходить чисту інженерну дельту (різницю) 
# # # # # # # #         і автоматично розтягує полотно, зберігаючи всі зазори.
# # # # # # # #         """
# # # # # # # #         if not self.stretch_zones:
# # # # # # # #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть бодай одну область стрейчу!</font>")
# # # # # # # #             return

# # # # # # # #         # Зчитуємо ручні параметри ширини (X)
# # # # # # # #         cur_w_str = self.input_current_width.text().strip()
# # # # # # # #         new_w_str = self.input_target_width.text().strip()
        
# # # # # # # #         # Зчитуємо ручні параметри висоти (Y)
# # # # # # # #         cur_h_str = self.input_current_height.text().strip()
# # # # # # # #         new_h_str = self.input_target_height.text().strip()

# # # # # # # #         # Рахуємо дельту по ширині, якщо заповнені обидва поля
# # # # # # # #         delta_x = 0.0
# # # # # # # #         if cur_w_str and new_w_str:
# # # # # # # #             delta_x = float(new_w_str) - float(cur_w_str)

# # # # # # # #         # Рахуємо дельту по висоті, якщо заповнені обидва поля
# # # # # # # #         delta_y = 0.0
# # # # # # # #         if cur_h_str and new_h_str:
# # # # # # # #             delta_y = float(new_h_str) - float(cur_h_str)

# # # # # # # #         if delta_x == 0.0 and delta_y == 0.0:
# # # # # # # #             self.lbl_status_calc.setText("<font color='yellow'>Різниця 0 мм. Введіть нові значення.</font>")
# # # # # # # #             return

# # # # # # # #         # Рахуємо кількість діючих порожнеч (зон) по осях
# # # # # # # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # #         # Ділимо чисту дельту порівну між зонами відповідної осі
# # # # # # # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # # # # # # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # # # # # # #         # Розподіляємо приріст по масиву зон простору
# # # # # # # #         for zone in self.stretch_zones:
# # # # # # # #             if zone['axis'] == 'X':
# # # # # # # #                 zone['stretch_val'] = share_delta_x
# # # # # # # #             elif zone['axis'] == 'Y':
# # # # # # # #                 zone['stretch_val'] = share_delta_y

# # # # # # # #         # Модифікуємо координати елементів за єдиним каскадним правилом
# # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # #                 entity.dxf.center = (
# # # # # # # #                     self.calculate_cascade_shift(cx, 'X', hndl),
# # # # # # # #                     self.calculate_cascade_shift(cy, 'Y', hndl),
# # # # # # # #                     cz
# # # # # # # #                 )
# # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # #                 ex, ey, ez = orig["end"]
# # # # # # # #                 entity.dxf.start = (
# # # # # # # #                     self.calculate_cascade_shift(sx, 'X', hndl),
# # # # # # # #                     self.calculate_cascade_shift(sy, 'Y', hndl),
# # # # # # # #                     sz
# # # # # # # #                 )
# # # # # # # #                 entity.dxf.end = (
# # # # # # # #                     self.calculate_cascade_shift(ex, 'X', hndl),
# # # # # # # #                     self.calculate_cascade_shift(ey, 'Y', hndl),
# # # # # # # #                     ez
# # # # # # # #                 )

# # # # # # # #         # Виводимо звіт про виконану автоматичну роботу конструктора
# # # # # # # #         self.lbl_status_calc.setText(
# # # # # # # #             f"<font color='#a5d6a7'>Успішно додано: ΔX = {delta_x:+.1f} мм | ΔY = {delta_y:+.1f} мм</font>"
# # # # # # # #         )

# # # # # # # #         # Заморожуємо отримані результати в DXF та оновлюємо екран
# # # # # # # #         self.on_slider_released()
        
# # # # # # # #         # Очищуємо поля для наступного замовлення
# # # # # # # #         self.input_current_width.clear()
# # # # # # # #         self.input_target_width.clear()
# # # # # # # #         self.input_current_height.clear()
# # # # # # # #         self.input_target_height.clear()

# # # # # # # #     # ---------------------------
# # # # # # # #     # УПРАВЛІННЯ ІСТОРІЄЮ ЗМІН ПРЯМОКУТНИКІВ ЗОН
# # # # # # # #     # ---------------------------
# # # # # # # #     def save_zones_history_state(self):
# # # # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # # # #         if len(self.zones_undo_stack) > 30:
# # # # # # # #             self.zones_undo_stack.pop(0)

# # # # # # # #     def undo(self):
# # # # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # # # #             self.reload_after_history_change()

# # # # # # # #     def redo(self):
# # # # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # # # #             self.reload_after_history_change()

# # # # # # # #     def update_history_buttons_state(self):
# # # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # # # #     def reload_after_history_change(self):
# # # # # # # #         self.is_loading_history = True
# # # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # # #         self.save_original_geometries()
        
# # # # # # # #         for zone in self.stretch_zones:
# # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # #         self.slider.blockSignals(True)
# # # # # # # #         self.slider.setValue(0)
# # # # # # # #         self.slider.blockSignals(False)

# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_zones_into_list()
# # # # # # # #         self.load_entities_into_list()
# # # # # # # #         self.update_history_buttons_state()
# # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # #         self.is_loading_history = False

# # # # # # # #     # ---------------------------
# # # # # # # #     # ТЕМИ ОФОРМЛЕННЯ (QSS СТИЛІ)
# # # # # # # #     # ---------------------------
# # # # # # # #     def on_theme_changed(self, theme_name):
# # # # # # # #         self.current_theme = theme_name
# # # # # # # #         self.set_interface_theme(theme_name)
# # # # # # # #         self.update_viewer()

# # # # # # # #     def set_interface_theme(self, theme_name):
# # # # # # # #         if theme_name == "Темна":
# # # # # # # #             self.setStyleSheet("""
# # # # # # # #                 QMainWindow { background-color: #252526; }
# # # # # # # #                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
# # # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
# # # # # # # #                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
# # # # # # # #                 QPushButton:hover { background-color: #505050; }
# # # # # # # #                 QLineEdit { background-color: #1e1e1e; border: 1px solid #555555; color: white; padding: 4px; border-radius: 3px; }
# # # # # # # #                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
# # # # # # # #                 QListWidget::item:selected { background-color: #04396c; color: white; }
# # # # # # # #                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
# # # # # # # #                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
# # # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # # #                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
# # # # # # # #                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
# # # # # # # #                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
# # # # # # # #                 #topFixBtn { background-color: #524705; color: #fffde7; }
# # # # # # # #             """)
# # # # # # # #         else:
# # # # # # # #             self.setStyleSheet("""
# # # # # # # #                 QMainWindow { background-color: #f3f3f3; }
# # # # # # # #                 QWidget { color: #000000; font-family: 'Segoe UI'; }
# # # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
# # # # # # # #                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
# # # # # # # #                 QPushButton:hover { background-color: #d0d0d0; }
# # # # # # # #                 QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: black; padding: 4px; border-radius: 3px; }
# # # # # # # #                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
# # # # # # # #                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
# # # # # # # #                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
# # # # # # # #                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
# # # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # # #                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
# # # # # # # #                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
# # # # # # # #                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
# # # # # # # #                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
# # # # # # # #             """)

# # # # # # # #     # ---------------------------
# # # # # # # #     # СЛУЖБОВІ МЕТОДИ CAD ЗОН
# # # # # # # #     # ---------------------------
# # # # # # # #     def assign_to_left_fix(self):
# # # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_entities_into_list()

# # # # # # # #     def assign_to_right_fix(self):
# # # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # # #         self.auto_detect_between_zone('X')
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_entities_into_list()

# # # # # # # #     def assign_to_bottom_fix(self):
# # # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_entities_into_list()

# # # # # # # #     def assign_to_top_fix(self):
# # # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_entities_into_list()

# # # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)

# # # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')

# # # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)

# # # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # # # # #         for zone in self.stretch_zones:
# # # # # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0:
# # # # # # # #                 return

# # # # # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # # # # #         self.stretch_zones.append(new_zone)
# # # # # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
# # # # # # # #         self.load_zones_into_list()
        
# # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # # # # #                 break

# # # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # # #         if not self.selected_handles or not self.original_geometries:
# # # # # # # #             return

# # # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # # #             self.clear_selection()
# # # # # # # #             return

# # # # # # # #         if axis == 'X':
# # # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # # #         else:
# # # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))

# # # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# # # # # # # #         self.clear_selection()

# # # # # # # #     def reset_all_parametric_zones(self):
# # # # # # # #         self.left_fixed_handles.clear()
# # # # # # # #         self.right_fixed_handles.clear()
# # # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # # #         self.top_fixed_handles.clear()
# # # # # # # #         self.stretch_zones.clear()
# # # # # # # #         self.active_zone_index = None
# # # # # # # #         self.slider.setEnabled(False)
# # # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.load_zones_into_list()
# # # # # # # #         self.load_entities_into_list()

# # # # # # # #     def load_zones_into_list(self):
# # # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # # #         self.zone_list_widget.clear()
# # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}] | Подовження: +{zone['stretch_val']:.0f} мм"
# # # # # # # #             item = QListWidgetItem(text)
# # # # # # # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # # #     def on_zone_selection_changed(self):
# # # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # # #         if not selected:
# # # # # # # #             self.active_zone_index = None
# # # # # # # #             self.slider.setEnabled(False)
# # # # # # # #             return

# # # # # # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # # # # # #         zone = self.stretch_zones[self.active_zone_index]

# # # # # # # #         self.slider.blockSignals(True)
# # # # # # # #         self.slider.setEnabled(True)
# # # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # # #         self.slider.blockSignals(False)
# # # # # # # #         self.update_viewer()

# # # # # # # #     # ---------------------------
# # # # # # # #     # МАТЕМАТИКА 2D КАСКАДНОГО ЗСУВУ ДЛЯ ДВОХ ОСЕЙ (STRETCH)
# # # # # # # #     # ---------------------------
# # # # # # # #     def on_slider_value_changed(self, value):
# # # # # # # #         if self.active_zone_index is None or self.is_loading_history:
# # # # # # # #             return

# # # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # # #                 entity.dxf.center = (
# # # # # # # #                     self.calculate_cascade_shift(cx, 'X', hndl),
# # # # # # # #                     self.calculate_cascade_shift(cy, 'Y', hndl),
# # # # # # # #                     cz
# # # # # # # #                 )
# # # # # # # #             elif orig["type"] == "LINE":
# # # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # # #                 ex, ey, ez = orig["end"]
# # # # # # # #                 entity.dxf.start = (
# # # # # # # #                     self.calculate_cascade_shift(sx, 'X', hndl),
# # # # # # # #                     self.calculate_cascade_shift(sy, 'Y', hndl),
# # # # # # # #                     sz
# # # # # # # #                 )
# # # # # # # #                 entity.dxf.end = (
# # # # # # # #                     self.calculate_cascade_shift(ex, 'X', hndl),
# # # # # # # #                     self.calculate_cascade_shift(ey, 'Y', hndl),
# # # # # # # #                     ez
# # # # # # # #                 )

# # # # # # # #         self.update_viewer()

# # # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # # #         if axis == 'X' and hndl:
# # # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # # #         elif axis == 'Y' and hndl:
# # # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # # #         shifted_val = orig_val
# # # # # # # #         for zone in self.stretch_zones:
# # # # # # # #             if zone['axis'] != axis: continue
# # # # # # # #             z_min = zone['min']
# # # # # # # #             z_max = zone['max']
# # # # # # # #             val = zone['stretch_val']

# # # # # # # #             if orig_val >= z_max:
# # # # # # # #                 shifted_val += val
# # # # # # # #             elif z_min < orig_val < z_max:
# # # # # # # #                 width = z_max - z_min
# # # # # # # #                 if width > 0:
# # # # # # # #                     ratio = (orig_val - z_min) / width
# # # # # # # #                     shifted_val += val * ratio
                    
# # # # # # # #         return shifted_val

# # # # # # # #     def on_slider_released(self):
# # # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # # #         active_zone = self.stretch_zones[self.active_zone_index]
# # # # # # # #         stretch_amount = active_zone['stretch_val']
# # # # # # # #         active_axis = active_zone['axis']
# # # # # # # #         active_max = active_zone['max']

# # # # # # # #         active_zone['max'] += stretch_amount

# # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # #             if idx == self.active_zone_index or zone['axis'] != active_axis:
# # # # # # # #                 continue
# # # # # # # #             if zone['min'] >= active_max:
# # # # # # # #                 zone['min'] += stretch_amount
# # # # # # # #                 zone['max'] += stretch_amount

# # # # # # # #         for zone in self.stretch_zones:
# # # # # # # #             zone['stretch_val'] = 0.0

# # # # # # # #         self.history.save_state()
# # # # # # # #         self.history.clear_redo()
# # # # # # # #         self.save_zones_history_state()
# # # # # # # #         self.zones_redo_stack.clear()
# # # # # # # #         self.update_history_buttons_state()

# # # # # # # #         self.save_original_geometries()

# # # # # # # #         self.slider.blockSignals(True)
# # # # # # # #         self.slider.setValue(0)
# # # # # # # #         self.slider.blockSignals(False)

# # # # # # # #         self.load_zones_into_list()
# # # # # # # #         self.load_entities_into_list()
# # # # # # # #         self.update_viewer()

# # # # # # # #     def save_original_geometries(self):
      
# # # # # # # #         self.original_geometries.clear()
# # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # #             hndl = entity.dxf.handle
# # # # # # # #             tp = entity.dxftype()
# # # # # # # #             if tp == "CIRCLE":
# # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # #                     "type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius
# # # # # # # #                 }
# # # # # # # #             elif tp == "LINE":
# # # # # # # #                 self.original_geometries[hndl] = {
# # # # # # # #                     "type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end
# # # # # # # #                 }


# # # # # # # #     def update_viewer(self):
# # # # # # # #         self.scene = QGraphicsScene()
# # # # # # # #         self.view.setScene(self.scene)
# # # # # # # #         self.overlay_items.clear()

# # # # # # # #         if self.current_theme == "Темна":
# # # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # # # # # # #             base_line_color = QColor(220, 220, 220)
# # # # # # # #         else:
# # # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # # # # # # #             base_line_color = QColor(80, 80, 80)

# # # # # # # #         seen_circles, seen_lines = set(), set()
        
# # # # # # # #         try:
# # # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # # #         except Exception:
# # # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']

# # # # # # # #             if zone['axis'] == 'X':
# # # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # # #             else:
# # # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # # #             if idx == self.active_zone_index:
# # # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # # # # # #             else:
# # # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # # # # # # #             self.scene.addItem(rect_item)

# # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # #             hndl = entity.dxf.handle
# # # # # # # #             tp = entity.dxftype()
# # # # # # # #             pyqt_item = None

# # # # # # # #             if tp == "CIRCLE":
# # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # #                 r = entity.dxf.radius
# # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)

# # # # # # # #             elif tp == "LINE":
# # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # # #             if pyqt_item:
# # # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)

# # # # # # # #                 if hndl in self.selected_handles:
# # # # # # # #                     pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # # # # # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))

# # # # # # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # # #     def on_scene_item_clicked(self, handle):
# # # # # # # #         self.selected_handles = {handle}
# # # # # # # #         self.sync_list_from_handles()
# # # # # # # #         self.update_viewer()

# # # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # # #         self.selected_handles.clear()
# # # # # # # #         path = QPainterPath()
# # # # # # # #         path.addRect(rect)
# # # # # # # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # # # # # # #         for item in matched_items:
# # # # # # # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # # #         self.sync_list_from_handles()
# # # # # # # #         self.update_viewer()

# # # # # # # #     def sync_list_from_handles(self):
# # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # #         self.entity_list.clearSelection()
# # # # # # # #         for i in range(self.entity_list.count()):
# # # # # # # #             item = self.entity_list.item(i)
# # # # # # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # #     def on_list_selection_changed(self):
# # # # # # # #         self.selected_handles.clear()
# # # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # # # # # #         self.update_viewer()

# # # # # # # #     def clear_selection(self):
# # # # # # # #         self.selected_handles.clear()
# # # # # # # #         self.update_viewer()
# # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # #         self.entity_list.clearSelection()
# # # # # # # #         self.entity_list.blockSignals(False)

# # # # # # # #     def load_entities_into_list(self):
# # # # # # # #         self.entity_list.blockSignals(True)
# # # # # # # #         self.entity_list.clear()
# # # # # # # #         seen = set()
# # # # # # # #         for entity in self.doc.modelspace():
# # # # # # # #             tp = entity.dxftype()
# # # # # # # #             hndl = entity.dxf.handle
            
# # # # # # # #             if tp == "CIRCLE":
# # # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
# # # # # # # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # # # # # # #             elif tp == "LINE":
# # # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # # #                 length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
# # # # # # # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {length:.1f} мм"
# # # # # # # #             else: continue

# # # # # # # #             item = QListWidgetItem(text)
# # # # # # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # # #             self.entity_list.addItem(item)
# # # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # # if __name__ == "__main__":
# # # # # # # #     import PySide6.QtWidgets as qtw
# # # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # # #     window = MiniCAD()
# # # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
# # # # # # # #     window.show()
# # # # # # # #     sys.exit(app.exec())
# # # # # # # import os
# # # # # # # import sys
# # # # # # # import math
# # # # # # # import copy  # Для глибокого копіювання масивів зон при синхронізації Undo/Redo

# # # # # # # import ezdxf
# # # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж сцени
# # # # # # # from ezdxf.math import Matrix44  # Для матричних поворотів та дзеркал

# # # # # # # # Сучасні імпорти графічного інтерфейсу під PySide6
# # # # # # # from PySide6.QtWidgets import (
# # # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # # #     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit
# # # # # # # )
# # # # # # # from PySide6.QtCore import Qt
# # # # # # # from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # # Імпорти кастомних модулів вашого проекту:
# # # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # # from history_manager import HistoryManager


# # # # # # # # ---------------------------------------------------------------------------
# # # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # # ---------------------------------------------------------------------------
# # # # # # # def patch_ezdxf_entities():
# # # # # # #     """
# # # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf.
# # # # # # #     """
# # # # # # #     from ezdxf.entities import Line
# # # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # # #     from ezdxf.entities import Circle
# # # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # # Викликаємо патч сутностей перед запуском всього CAD-редактора
# # # # # # # patch_ezdxf_entities()
# # # # # # # # ---------------------------------------------------------------------------


# # # # # # # class MiniCAD(QMainWindow):
# # # # # # #     def __init__(self):
# # # # # # #         super().__init__()

# # # # # # #         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор з Базуванням Деталей")
# # # # # # #         self.setGeometry(100, 100, 1450, 950)

# # # # # # #         self.dxf_path = "drawing.DXF"
# # # # # # #         self.current_theme = "Темна"  # Дефолтна тема при запуску

# # # # # # #         self.selected_handles = set()
# # # # # # #         self.overlay_items = {}
# # # # # # #         self.original_geometries = {}
# # # # # # #         self.is_loading_history = False

# # # # # # #         # Списки для жорстких зон фіксації
# # # # # # #         self.left_fixed_handles = set()
# # # # # # #         self.right_fixed_handles = set()
# # # # # # #         self.bottom_fixed_handles = set()
# # # # # # #         self.top_fixed_handles = set()
        
# # # # # # #         # Списки збереження кастомних зон розтягування
# # # # # # #         self.stretch_zones = []
# # # # # # #         self.active_zone_index = None

# # # # # # #         # Стек для синхронного відкоту прямокутників разом із DXF-файлом
# # # # # # #         self.zones_undo_stack = []
# # # # # # #         self.zones_redo_stack = []

# # # # # # #         if not os.path.exists(self.dxf_path):
# # # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # # #             sys.exit()

# # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # # #         # Ініціалізація історії змін DXF
# # # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # # #         self.history.save_state()
# # # # # # #         self.save_zones_history_state()  # Зберігаємо стартовий стан прямокутників

# # # # # # #         self.init_ui()
# # # # # # #         self.set_interface_theme(self.current_theme)  # Застосовуємо тему інтерфейсу
# # # # # # #         self.save_original_geometries()
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     def init_ui(self):
# # # # # # #         main_widget = QWidget()
# # # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # # #         self.setCentralWidget(main_widget)

# # # # # # #         self.scene = QGraphicsScene()
# # # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # # #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# # # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # # #         control_panel = QWidget()
# # # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # # #         # --- БЛОК 1: АДАНТАЦІЯ ПІД РОЗМІРИ ЗАМОВЛЕННЯ ---
# # # # # # #         auto_scale_group = QGroupBox("🚀 Адаптація під розміри замовлення (з припусками)")
# # # # # # #         auto_scale_box = QVBoxLayout()

# # # # # # #         width_layout = QHBoxLayout()
# # # # # # #         width_layout.addWidget(QLabel("<b>Ширина (X):</b> Поточна:"))
# # # # # # #         self.input_current_width = QLineEdit()
# # # # # # #         self.input_current_width.setPlaceholderText("1000")
# # # # # # #         width_layout.addWidget(self.input_current_width)
# # # # # # #         width_layout.addWidget(QLabel("➡️ Нова:"))
# # # # # # #         self.input_target_width = QLineEdit()
# # # # # # #         self.input_target_width.setPlaceholderText("1010")
# # # # # # #         width_layout.addWidget(self.input_target_width)
# # # # # # #         auto_scale_box.addLayout(width_layout)

# # # # # # #         height_layout = QHBoxLayout()
# # # # # # #         height_layout.addWidget(QLabel("<b>Висота (Y):</b> Поточна:"))
# # # # # # #         self.input_current_height = QLineEdit()
# # # # # # #         self.input_current_height.setPlaceholderText("2040")
# # # # # # #         height_layout.addWidget(self.input_current_height)
# # # # # # #         height_layout.addWidget(QLabel("➡️ Нова:"))
# # # # # # #         self.input_target_height = QLineEdit()
# # # # # # #         self.input_target_height.setPlaceholderText("2050")
# # # # # # #         height_layout.addWidget(self.input_target_height)
# # # # # # #         auto_scale_box.addLayout(height_layout)

# # # # # # #         self.lbl_status_calc = QLabel("Введіть розміри та натисніть кнопку нижче")
# # # # # # #         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
# # # # # # #         auto_scale_box.addWidget(self.lbl_status_calc)

# # # # # # #         self.btn_apply_auto_scale = QPushButton("⚡ Автоматично розрахувати дельту та змінити")
# # # # # # #         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
# # # # # # #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# # # # # # #         auto_scale_box.addWidget(self.btn_apply_auto_scale)

# # # # # # #         auto_scale_group.setLayout(auto_scale_box)
# # # # # # #         control_layout.addWidget(auto_scale_group)

# # # # # # #         # --- БЛОК 2: ОРІЄНТАЦІЯ ТА ОБЕРТАННЯ ДЕТАЛЕЙ ---
# # # # # # #         transform_group = QGroupBox("🔄 Орієнтація та обертання виділених деталей")
# # # # # # #         transform_box = QVBoxLayout()
        
# # # # # # #         rot_layout = QHBoxLayout()
# # # # # # #         self.btn_rot_90 = QPushButton("↪️ Поворот 90°")
# # # # # # #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# # # # # # #         self.btn_rot_180 = QPushButton("🔁 Поворот 180°")
# # # # # # #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# # # # # # #         rot_layout.addWidget(self.btn_rot_90)
# # # # # # #         rot_layout.addWidget(self.btn_rot_180)
# # # # # # #         transform_box.addLayout(rot_layout)

# # # # # # #         mirror_layout = QHBoxLayout()
# # # # # # #         self.btn_mirror_h = QPushButton("↔️ Віддзеркалити по Х")
# # # # # # #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# # # # # # #         self.btn_mirror_v = QPushButton("↕️ Віддзеркалити по Y")
# # # # # # #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
# # # # # # #         mirror_layout.addWidget(self.btn_mirror_h)
# # # # # # #         mirror_layout.addWidget(self.btn_mirror_v)
# # # # # # #         transform_box.addLayout(mirror_layout)

# # # # # # #         transform_group.setLayout(transform_box)
# # # # # # #         control_layout.addWidget(transform_group)

# # # # # # #         # --- БЛОК 3: ИНЖЕНЕРНЕ ПРИТИСКАННЯ (БАЗУВАННЯ) ---
# # # # # # #         align_group = QGroupBox("📍 Притулити (базувати) виділене до краю дверей")
# # # # # # #         align_box = QVBoxLayout()

# # # # # # #         align_x_layout = QHBoxLayout()
# # # # # # #         self.btn_align_left = QPushButton("🟢 До лівого краю (Х)")
# # # # # # #         self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
# # # # # # #         self.btn_align_right = QPushButton("🔴 До правого краю (Х)")
# # # # # # #         self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
# # # # # # #         align_x_layout.addWidget(self.btn_align_left)
# # # # # # #         align_x_layout.addWidget(self.btn_align_right)
# # # # # # #         align_box.addLayout(align_x_layout)

# # # # # # #         align_y_layout = QHBoxLayout()
# # # # # # #         self.btn_align_bottom = QPushButton("🔵 До нижнього краю (Y)")
# # # # # # #         self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
# # # # # # #         self.btn_align_top = QPushButton("🟡 До верхнього краю (Y)")
# # # # # # #         self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
# # # # # # #         align_y_layout.addWidget(self.btn_align_bottom)
# # # # # # #         align_y_layout.addWidget(self.btn_align_top)
# # # # # # #         align_box.addLayout(align_y_layout)

# # # # # # #         align_group.setLayout(align_box)
# # # # # # #         control_layout.addWidget(align_group)

# # # # # # #         # --- БЛОК СТИЛЮ ТА ТЕМИ ---
# # # # # # #         theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
# # # # # # #         theme_box = QHBoxLayout()
# # # # # # #         theme_box.addWidget(QLabel("Тема:"))
# # # # # # #         self.theme_combo = QComboBox()
# # # # # # #         self.theme_combo.addItems(["Темна", "Світла"])
# # # # # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # # # # #         theme_box.addWidget(self.theme_combo)
# # # # # # #         theme_group.setLayout(theme_box)
# # # # # # #         control_layout.addWidget(theme_group)

# # # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # # #         history_group = QGroupBox("Історія constructorських змін")
# # # # # # #         history_box = QHBoxLayout()
# # # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # # #         history_box.addWidget(self.btn_undo)
# # # # # # #         history_box.addWidget(self.btn_redo)
# # # # # # #         history_group.setLayout(history_box)
# # # # # # #         control_layout.addWidget(history_group)
# # # # # # #         self.update_history_buttons_state()

# # # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # # #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# # # # # # #         fix_box = QVBoxLayout()
# # # # # # #         h_fix_layout = QHBoxLayout()
# # # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # # #         self.btn_set_left_fix.setObjectName("leftFixBtn")
# # # # # # #         self.btn_set_right_fix.setObjectName("rightFixBtn")
# # # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # # #         v_fix_layout = QHBoxLayout()
# # # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # # #         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
# # # # # # #         self.btn_set_top_fix.setObjectName("topFixBtn")
# # # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # # #         fix_box.addLayout(v_fix_layout)
# # # # # # #         fix_group.setLayout(fix_box)
# # # # # # #         control_layout.addWidget(fix_group)

# # # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # # #         zone_box = QVBoxLayout()
# # # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # # #         zone_box.addWidget(self.btn_add_zone_x)
# # # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # # #         zone_box.addWidget(self.btn_add_zone_y)
# # # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # # #         zone_box.addWidget(self.btn_clear_zones)
# # # # # # #         zone_group.setLayout(zone_box)
# # # # # # #         control_layout.addWidget(zone_group)

# # # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
# # # # # # #         self.zone_list_widget = QListWidget()
# # # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # # #         self.entity_list = QListWidget()
# # # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# # # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # # #         control_layout.addWidget(self.entity_list)

# # # # # # #         self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
# # # # # # #         control_layout.addWidget(self.slider_label)
# # # # # # #         self.slider = QSlider(Qt.Orientation.Horizontal)
# # # # # # #         self.slider.setRange(0, 600)
# # # # # # #         self.slider.setEnabled(False)
# # # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # # #         control_layout.addWidget(self.slider)

# # # # # # #         control_layout.addStretch()

# # # # # # #     # ---------------------------
# # # # # # #     # МЕТОДИ ФІКСАЦІЇ ЕЛЕМЕНТІВ ФУРНІТУРИ
# # # # # # #     # ---------------------------
# # # # # # #     def assign_to_left_fix(self):
# # # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # # #         self.auto_detect_between_zone('X')
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     def assign_to_right_fix(self):
# # # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # # #         self.auto_detect_between_zone('X')
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     def assign_to_bottom_fix(self):
# # # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     def assign_to_top_fix(self):
# # # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # # #         self.auto_detect_between_zone('Y')
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     # ---------------------------
# # # # # # #     # ЛОГІКА АВТОМАТИЧНОЇ АДАПТАЦІЇ ТА КАСКАДНОГО ОНОВЛЕННЯ ІНФОРМАЦІЇ ПРО ЗОНИ
# # # # # # #     # ---------------------------
# # # # # # #     def process_manual_input_dimension_scale(self):
# # # # # # #         if not self.stretch_zones:
# # # # # # #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
# # # # # # #             return

# # # # # # #         cur_w_str = self.input_current_width.text().strip()
# # # # # # #         new_w_str = self.input_target_width.text().strip()
# # # # # # #         cur_h_str = self.input_current_height.text().strip()
# # # # # # #         new_h_str = self.input_target_height.text().strip()

# # # # # # #         delta_x = float(new_w_str) - float(cur_w_str) if (cur_w_str and new_w_str) else 0.0
# # # # # # #         delta_y = float(new_h_str) - float(cur_h_str) if (cur_h_str and new_h_str) else 0.0

# # # # # # #         if delta_x == 0.0 and delta_y == 0.0:
# # # # # # #             self.lbl_status_calc.setText("<font color='yellow'>Різниця 0 мм. Змініть значення.</font>")
# # # # # # #             return

# # # # # # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # # # # # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # # # # # #         # Тимчасово записуємо дельти стрейчу для кожної зони, щоб прогнати через каскадний зміщувач
# # # # # # #         for zone in self.stretch_zones:
# # # # # # #             if zone['axis'] == 'X':
# # # # # # #                 zone['stretch_val'] = share_delta_x
# # # # # # #             elif zone['axis'] == 'Y':
# # # # # # #                 zone['stretch_val'] = share_delta_y

# # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # #             entity = self.doc.entitydb[hndl]

# # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # # # # #             elif orig["type"] == "LINE":
# # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # #                 ex, ey, ez = orig["end"]
# # # # # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # # # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

# # # # # # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Адаптовано: ΔX={delta_x:+.1f}мм | ΔY={delta_y:+.1f}мм</font>")
        
# # # # # # #         # Фізично фіксуємо зміни в DXF
# # # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # # #         # КРИТИЧНЕ ОНОВЛЕННЯ ІНФОРМАЦІЇ: Фізично перераховуємо текстові межі для ВСІХ зон у масиві
# # # # # # #         for zone in self.stretch_zones:
# # # # # # #             stretch_amount = zone['stretch_val']
# # # # # # #             if stretch_amount == 0: continue
# # # # # # #             active_axis = zone['axis']
# # # # # # #             active_max = zone['max']
# # # # # # #             zone['max'] += stretch_amount
# # # # # # #             for sub_z in self.stretch_zones:
# # # # # # #                 if sub_z == zone or sub_z['axis'] != active_axis: continue
# # # # # # #                 if sub_z['min'] >= active_max:
# # # # # # #                     sub_z['min'] += stretch_amount
# # # # # # #                     sub_z['max'] += stretch_amount

# # # # # # #         # Скидаємо приріст, оскільки координати меж прямокутників тепер стали новою статичною базою виробу
# # # # # # #         for zone in self.stretch_zones:
# # # # # # #             zone['stretch_val'] = 0.0

# # # # # # #         # Запис у стеки історії змін
# # # # # # #         self.history.save_state()
# # # # # # #         self.history.clear_redo()
# # # # # # #         self.save_zones_history_state()
# # # # # # #         self.zones_redo_stack.clear()
# # # # # # #         self.update_history_buttons_state()
# # # # # # #         self.save_original_geometries()

# # # # # # #         self.input_current_width.clear()
# # # # # # #         self.input_target_width.clear()
# # # # # # #         self.input_current_height.clear()
# # # # # # #         self.input_target_height.clear()

# # # # # # #         # Повністю синхронізуємо та оновлюємо текстовий список зон на екрані!
# # # # # # #         self.load_zones_into_list()
# # # # # # #         self.load_entities_into_list()
# # # # # # #         self.update_viewer()

# # # # # # #     # ---------------------------
# # # # # # #     # ЛОГІКА ОБЕРТАННЯ ТА ДЗЕРКАЛА (МАТРИЦЯ EZDXF)
# # # # # # #     # ---------------------------
# # # # # # #     def transform_selected_entities(self, mode):
# # # # # # #         if not self.selected_handles: return
# # # # # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # #         if not selected_entities: return

# # # # # # #         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
# # # # # # #         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

# # # # # # #         for entity in selected_entities:
# # # # # # #             if mode == "ROT90":
# # # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(90)), Matrix44.translate(cx, cy, 0))
# # # # # # #             elif mode == "ROT180":
# # # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(180)), Matrix44.translate(cx, cy, 0))
# # # # # # #             elif mode == "MIRROR_H":
# # # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
# # # # # # #             elif mode == "MIRROR_V":
# # # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
# # # # # # #             else: continue
# # # # # # #             entity.transform(m)

# # # # # # #         self.doc.saveas(self.dxf_path)
# # # # # # #         self.history.save_state()
# # # # # # #         self.save_zones_history_state()
# # # # # # #         self.save_original_geometries()
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     # ---------------------------
# # # # # # #     # ЛОГІКА ПРИТУЛЕННЯ ДО КРАЇВ (БАЗУВАННЯ З ВІДСТУПОМ 5ММ)
# # # # # # #     # ---------------------------
# # # # # # #     def align_selected_to_edge(self, edge):
# # # # # # #         if not self.selected_handles: return
# # # # # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # #         if not selected_entities: return

# # # # # # #         try:
# # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # #             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
# # # # # # #             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
# # # # # # #         except Exception:
# # # # # # #             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

# # # # # # #         margin = 5.0
# # # # # # #         shift_x, shift_y = 0.0, 0.0

# # # # # # #         sel_min_x = min(e.left_x for e in selected_entities)
# # # # # # #         sel_max_x = max(e.right_x for e in selected_entities)
# # # # # # #         sel_min_y = min(e.bottom_y for e in selected_entities)
# # # # # # #         sel_max_y = max(e.top_y for e in selected_entities)

# # # # # # #         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
# # # # # # #         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
# # # # # # #         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
# # # # # # #         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

# # # # # # #         for entity in selected_entities:
# # # # # # #             entity.translate(shift_x, shift_y, 0)

# # # # # # #         self.doc.saveas(self.dxf_path)
# # # # # # #         self.history.save_state()
# # # # # # #         self.save_zones_history_state()
# # # # # # #         self.save_original_geometries()
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     # ---------------------------
# # # # # # #     # СЛУЖБОВІ СТЕКИ UNDO / REDO
# # # # # # #     # ---------------------------
# # # # # # #     def save_zones_history_state(self):
# # # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # # #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# # # # # # #     def undo(self):
# # # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # # #             self.reload_after_history_change()

# # # # # # #     def redo(self):
# # # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # # #             self.reload_after_history_change()

# # # # # # #     def update_history_buttons_state(self):
# # # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # # #     def reload_after_history_change(self):
# # # # # # #         self.is_loading_history = True
# # # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # # #         self.save_original_geometries()
# # # # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0
# # # # # # #         self.slider.blockSignals(True)
# # # # # # #         self.slider.setValue(0)
# # # # # # #         self.slider.blockSignals(False)
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_zones_into_list()
# # # # # # #         self.load_entities_into_list()
# # # # # # #         self.update_history_buttons_state()
# # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # #         self.is_loading_history = False

# # # # # # #     def on_theme_changed(self, theme_name):
# # # # # # #         self.current_theme = theme_name
# # # # # # #         self.set_interface_theme(theme_name)
# # # # # # #         self.update_viewer()

# # # # # # #     def set_interface_theme(self, theme_name):
# # # # # # #         if theme_name == "Темна":
# # # # # # #             self.setStyleSheet("""
# # # # # # #                 QMainWindow { background-color: #252526; }
# # # # # # #                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
# # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
# # # # # # #                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
# # # # # # #                 QPushButton:hover { background-color: #505050; }
# # # # # # #                 QLineEdit { background-color: #1e1e1e; border: 1px solid #555555; color: white; padding: 4px; border-radius: 3px; }
# # # # # # #                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
# # # # # # #                 QListWidget::item:selected { background-color: #04396c; color: white; }
# # # # # # #                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
# # # # # # #                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
# # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # #                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
# # # # # # #                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
# # # # # # #                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
# # # # # # #                 #topFixBtn { background-color: #524705; color: #fffde7; }
# # # # # # #             """)
# # # # # # #         else:
# # # # # # #             self.setStyleSheet("""
# # # # # # #                 QMainWindow { background-color: #f3f3f3; }
# # # # # # #                 QWidget { color: #000000; font-family: 'Segoe UI'; }
# # # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
# # # # # # #                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
# # # # # # #                 QPushButton:hover { background-color: #d0d0d0; }
# # # # # # #                 QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: black; padding: 4px; border-radius: 3px; }
# # # # # # #                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
# # # # # # #                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
# # # # # # #                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
# # # # # # #                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
# # # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # # #                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
# # # # # # #                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
# # # # # # #                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
# # # # # # #                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
# # # # # # #             """)

# # # # # # #     def auto_detect_between_zone(self, axis):
# # # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
# # # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
# # # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
# # # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # # #     def load_zones_into_list(self):
# # # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # # #         self.zone_list_widget.clear()
# # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}]"
# # # # # # #             item = QListWidgetItem(text)
# # # # # # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # # # # # #             self.zone_list_widget.addItem(item)
# # # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # # #     def on_zone_selection_changed(self):
# # # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # # #         if not selected:
# # # # # # #             self.active_zone_index = None
# # # # # # #             self.slider.setEnabled(False)
# # # # # # #             return
# # # # # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # #         self.slider.blockSignals(True)
# # # # # # #         self.slider.setEnabled(True)
# # # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # # #         self.slider.blockSignals(False)
# # # # # # #         self.update_viewer()

# # # # # # #     # ---------------------------
# # # # # # #     # ВІДНОВЛЕНІ МЕТОДИ СЛАЙДЕРА (ВИПРАВЛЕННЯ ПОМИЛКИ ATTRIBUTEERROR)
# # # # # # #     # ---------------------------
# # # # # # #     def on_slider_value_changed(self, value):
# # # # # # #         """Здійснює динамічне відображення каскадного розтягування при русі повзунка."""
# # # # # # #         if self.active_zone_index is None or self.is_loading_history: 
# # # # # # #             return
# # # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # # #             entity = self.doc.entitydb[hndl]
# # # # # # #             if orig["type"] == "CIRCLE":
# # # # # # #                 cx, cy, cz = orig["center"]
# # # # # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # # # # #             elif orig["type"] == "LINE":
# # # # # # #                 sx, sy, sz = orig["start"]
# # # # # # #                 ex, ey, ez = orig["end"]
# # # # # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # # # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)
# # # # # # #         self.update_viewer()

# # # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # # #         """Математичний двигун: прораховує 2D зсуви з урахуванням каскадів та фіксаторів."""
# # # # # # #         if axis == 'X' and hndl:
# # # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # # #             if hndl in self.right_fixed_handles:
# # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # # #         elif axis == 'Y' and hndl:
# # # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # # #             if hndl in self.top_fixed_handles:
# # # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # # #         shifted_val = orig_val
# # # # # # #         for zone in self.stretch_zones:
# # # # # # #             if zone['axis'] != axis: continue
# # # # # # #             z_min = zone['min']
# # # # # # #             z_max = zone['max']
# # # # # # #             val = zone['stretch_val']

# # # # # # #             if orig_val >= z_max: shifted_val += val
# # # # # # #             elif z_min < orig_val < z_max:
# # # # # # #                 width = z_max - z_min
# # # # # # #                 if width > 0: shifted_val += val * ((orig_val - z_min) / width)
                    
# # # # # # #         return shifted_val

# # # # # # #     def on_slider_released(self):
# # # # # # #         self.doc.saveas(self.dxf_path)
# # # # # # #         active_zone = self.stretch_zones[self.active_zone_index] if self.active_zone_index is not None else None
        
# # # # # # #         if active_zone:
# # # # # # #             stretch_amount = active_zone['stretch_val']
# # # # # # #             active_axis = active_zone['axis']
# # # # # # #             active_max = active_zone['max']
# # # # # # #             active_zone['max'] += stretch_amount
# # # # # # #             for idx, zone in enumerate(self.stretch_zones):
# # # # # # #                 if idx == self.active_zone_index or zone['axis'] != active_axis: continue
# # # # # # #                 if zone['min'] >= active_max:
# # # # # # #                     zone['min'] += stretch_amount
# # # # # # #                     zone['max'] += stretch_amount

# # # # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # # # # # #         self.history.save_state()
# # # # # # #         self.history.clear_redo()
# # # # # # #         self.save_zones_history_state()
# # # # # # #         self.zones_redo_stack.clear()
# # # # # # #         self.update_history_buttons_state()
# # # # # # #         self.save_original_geometries()

# # # # # # #         self.slider.blockSignals(True)
# # # # # # #         self.slider.setValue(0)
# # # # # # #         self.slider.blockSignals(False)

# # # # # # #         self.load_zones_into_list()
# # # # # # #         self.load_entities_into_list()
# # # # # # #         self.update_viewer()

# # # # # # #     # ---------------------------
# # # # # # #     # ВІДНОВЛЕНІ МЕТОДИ СКИДАННЯ (ВИПРАВЛЕННЯ ПОМИЛКИ ATTRIBUTEERROR)
# # # # # # #     # ---------------------------
# # # # # # #     def reset_all_parametric_zones(self):
# # # # # # #         """Повністю очищає всі зафіксовані блоки фурнітури та створені прямокутники деформації."""
# # # # # # #         self.left_fixed_handles.clear()
# # # # # # #         self.right_fixed_handles.clear()
# # # # # # #         self.bottom_fixed_handles.clear()
# # # # # # #         self.top_fixed_handles.clear()
# # # # # # #         self.stretch_zones.clear()
# # # # # # #         self.active_zone_index = None
# # # # # # #         self.slider.setEnabled(False)
# # # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # # #         self.update_viewer()
# # # # # # #         self.load_zones_into_list()
# # # # # # #         self.load_entities_into_list()

# # # # # # #     def save_original_geometries(self):
# # # # # # #         self.original_geometries.clear()
# # # # # # #         for entity in self.doc.modelspace():
# # # # # # #             hndl = entity.dxf.handle
# # # # # # #             tp = entity.dxftype()
# # # # # # #             if tp == "CIRCLE":
# # # # # # #                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
# # # # # # #             elif tp == "LINE":
# # # # # # #                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}

# # # # # # #     # ---------------------------
# # # # # # #     # ВІЗУАЛІЗАЦІЯ СЦЕНИ ТА СТВОРЕННЯ КООРДИНАТНИХ ОСЕЙ
# # # # # # #     # ---------------------------
# # # # # # #     def update_viewer(self):
# # # # # # #         self.scene = QGraphicsScene()
# # # # # # #         self.view.setScene(self.scene)
# # # # # # #         self.overlay_items.clear()

# # # # # # #         if self.current_theme == "Темна":
# # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # # # # # #             base_line_color = QColor(220, 220, 220)
# # # # # # #         else:
# # # # # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # # # # # #             base_line_color = QColor(80, 80, 80)

# # # # # # #         # МАЛЮЄМО СИСТЕМУ КООРДИНАТНИХ ОСЕЙ
# # # # # # #         axis_len = 150.0
# # # # # # #         self.scene.addLine(-50, 0, axis_len, 0, QPen(QColor(33, 150, 243), 2.5))
# # # # # # #         self.scene.addLine(axis_len, 0, axis_len - 10, -4, QPen(QColor(33, 150, 243), 2.5))
# # # # # # #         self.scene.addLine(axis_len, 0, axis_len - 10, 4, QPen(QColor(33, 150, 243), 2.5))
# # # # # # #         self.scene.addLine(0, 50, 0, -axis_len, QPen(QColor(76, 175, 80), 2.5))
# # # # # # #         self.scene.addLine(0, -axis_len, -4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))
# # # # # # #         self.scene.addLine(0, -axis_len, 4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))

# # # # # # #         seen_circles, seen_lines = set(), set()
# # # # # # #         try:
# # # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # # #         except Exception:
# # # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']
# # # # # # #             if zone['axis'] == 'X':
# # # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # # #             else:
# # # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # # #             if idx == self.active_zone_index:
# # # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # # # # #             else:
# # # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # # # # # #             self.scene.addItem(rect_item)

# # # # # # #         for entity in self.doc.modelspace():
# # # # # # #             hndl = entity.dxf.handle
# # # # # # #             tp = entity.dxftype()
# # # # # # #             pyqt_item = None
# # # # # # #             if tp == "CIRCLE":
# # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # #                 r = entity.dxf.radius
# # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
# # # # # # #             elif tp == "LINE":
# # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # # #             if pyqt_item:
# # # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
# # # # # # #                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # # # # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
# # # # # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # #                 self.scene.addItem(pyqt_item)
# # # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # # #     def create_zone_from_selection(self, axis):
# # # # # # #         if not self.selected_handles or not self.original_geometries: return
# # # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # # #             self.clear_selection()
# # # # # # #             return
# # # # # # #         if axis == 'X':
# # # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # # #         else:
# # # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
# # # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# # # # # # #         self.clear_selection()

# # # # # # #     def process_manual_rubber_band(self, rect):
# # # # # # #         self.selected_handles.clear()
# # # # # # #         path = QPainterPath()
# # # # # # #         path.addRect(rect)
# # # # # # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # # # # # #         for item in matched_items:
# # # # # # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # # #         self.sync_list_from_handles()
# # # # # # #         self.update_viewer()

# # # # # # #     def sync_list_from_handles(self):
# # # # # # #         self.entity_list.blockSignals(True)
# # # # # # #         self.entity_list.clearSelection()
# # # # # # #         for i in range(self.entity_list.count()):
# # # # # # #             item = self.entity_list.item(i)
# # # # # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # # #         self.entity_list.blockSignals(False)

# # # # # # #     def on_list_selection_changed(self):
# # # # # # #         self.selected_handles.clear()
# # # # # # #         for item in self.entity_list.selectedItems():
# # # # # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # # # # #         self.update_viewer()

# # # # # # #     def clear_selection(self):
# # # # # # #         self.selected_handles.clear()
# # # # # # #         self.update_viewer()
# # # # # # #         self.entity_list.blockSignals(True)
# # # # # # #         self.entity_list.clearSelection()
# # # # # # #         self.entity_list.blockSignals(False)

# # # # # # #     def load_entities_into_list(self):
# # # # # # #         self.entity_list.blockSignals(True)
# # # # # # #         self.entity_list.clear()
# # # # # # #         seen = set()
# # # # # # #         for entity in self.doc.modelspace():
# # # # # # #             tp = entity.dxftype()
# # # # # # #             hndl = entity.dxf.handle
# # # # # # #             if tp == "CIRCLE":
# # # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
# # # # # # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # # # # # #             elif tp == "LINE":
# # # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм"
# # # # # # #             else: continue
# # # # # # #             item = QListWidgetItem(text)
# # # # # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # # #             self.entity_list.addItem(item)
# # # # # # #         self.entity_list.blockSignals(False)


# # # # # # # if __name__ == "__main__":
# # # # # # #     import PySide6.QtWidgets as qtw
# # # # # # #     app = qtw.QApplication(sys.argv)
# # # # # # #     window = MiniCAD()
# # # # # # #     window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
# # # # # # #     window.show()
# # # # # # #     sys.exit(app.exec())

# # # # # # import os
# # # # # # import sys
# # # # # # import math
# # # # # # import copy  # Для глибокого копіювання масивів зон при синхронізації Undo/Redo

# # # # # # import ezdxf
# # # # # # import ezdxf.bbox as dxf_bbox  # Для безпечного прорахунку меж сцени
# # # # # # from ezdxf.math import Matrix44  # Для матричних поворотів та дзеркал

# # # # # # # Сучасні імпорти графічного інтерфейсу під PySide6
# # # # # # from PySide6.QtWidgets import (
# # # # # #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# # # # # #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# # # # # #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# # # # # #     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit
# # # # # # )
# # # # # # from PySide6.QtCore import Qt
# # # # # # from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QBrush

# # # # # # # Імпорти кастомних модулів вашого проекту:
# # # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # # from graphics_view import AdvancedGraphicsView
# # # # # # from history_manager import HistoryManager


# # # # # # # ---------------------------------------------------------------------------
# # # # # # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ ЛІВИХ/ПРАВИХ КООРДИНАТ)
# # # # # # # ---------------------------------------------------------------------------
# # # # # # def patch_ezdxf_entities():
# # # # # #     """
# # # # # #     Універсальний патч: додає властивості left_x, right_x, bottom_y, top_y
# # # # # #     одразу для ВСІХ графічних елементів бібліотеки ezdxf.
# # # # # #     """
# # # # # #     from ezdxf.entities import Line
# # # # # #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # # # #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # # # #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # # # #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # # # #     from ezdxf.entities import Circle
# # # # # #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # # # #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # # # #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # # # #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # # # # # Викликаємо патч сутностей перед запуском всього CAD-редактора
# # # # # # patch_ezdxf_entities()
# # # # # # # ---------------------------------------------------------------------------


# # # # # # class MiniCAD(QMainWindow):
# # # # # #     def __init__(self):
# # # # # #         super().__init__()

# # # # # #         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор з Базуванням Деталей")
# # # # # #         self.setGeometry(100, 100, 1450, 950)

# # # # # #         self.dxf_path = "drawing.DXF"
# # # # # #         self.current_theme = "Темна"  # Дефолтна тема при запуску

# # # # # #         self.selected_handles = set()
# # # # # #         self.overlay_items = {}
# # # # # #         self.original_geometries = {}
# # # # # #         self.is_loading_history = False

# # # # # #         # Списки для жорстких зон фіксації
# # # # # #         self.left_fixed_handles = set()
# # # # # #         self.right_fixed_handles = set()
# # # # # #         self.bottom_fixed_handles = set()
# # # # # #         self.top_fixed_handles = set()
        
# # # # # #         # Списки збереження кастомних зон розтягування
# # # # # #         self.stretch_zones = []
# # # # # #         self.active_zone_index = None

# # # # # #         # Стек для синхронного відкоту прямокутників разом із DXF-файлом
# # # # # #         self.zones_undo_stack = []
# # # # # #         self.zones_redo_stack = []

# # # # # #         if not os.path.exists(self.dxf_path):
# # # # # #             print(f"Помилка: Файл {self.dxf_path} не знайдено!")
# # # # # #             sys.exit()

# # # # # #         self.doc = ezdxf.readfile(self.dxf_path)

# # # # # #         # Ініціалізація історії змін DXF
# # # # # #         self.history = HistoryManager(self.dxf_path)
# # # # # #         self.history.save_state()
# # # # # #         self.save_zones_history_state()  # Зберігаємо стартовий стан прямокутників

# # # # # #         self.init_ui()
# # # # # #         self.set_interface_theme(self.current_theme)  # Застосовуємо тему інтерфейсу
# # # # # #         self.save_original_geometries()
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     def init_ui(self):
# # # # # #         main_widget = QWidget()
# # # # # #         self.central_layout = QHBoxLayout(main_widget)
# # # # # #         self.setCentralWidget(main_widget)

# # # # # #         self.scene = QGraphicsScene()
# # # # # #         self.view = AdvancedGraphicsView(self.scene, self)
# # # # # #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# # # # # #         self.central_layout.addWidget(self.view, stretch=4)

# # # # # #         control_panel = QWidget()
# # # # # #         control_layout = QVBoxLayout(control_panel)
# # # # # #         self.central_layout.addWidget(control_panel, stretch=2)

# # # # # #         # --- БЛОК 1: АДАНТАЦІЯ ПІД РОЗМІРИ ЗАМОВЛЕННЯ ---
# # # # # #         auto_scale_group = QGroupBox("🚀 Адаптація під розміри замовлення (з припусками)")
# # # # # #         auto_scale_box = QVBoxLayout()

# # # # # #         width_layout = QHBoxLayout()
# # # # # #         width_layout.addWidget(QLabel("<b>Ширина (X):</b> Поточна:"))
# # # # # #         self.input_current_width = QLineEdit()
# # # # # #         self.input_current_width.setPlaceholderText("1000")
# # # # # #         width_layout.addWidget(self.input_current_width)
# # # # # #         width_layout.addWidget(QLabel("➡️ Нова:"))
# # # # # #         self.input_target_width = QLineEdit()
# # # # # #         self.input_target_width.setPlaceholderText("1010")
# # # # # #         width_layout.addWidget(self.input_target_width)
# # # # # #         auto_scale_box.addLayout(width_layout)

# # # # # #         height_layout = QHBoxLayout()
# # # # # #         height_layout.addWidget(QLabel("<b>Висота (Y):</b> Поточна:"))
# # # # # #         self.input_current_height = QLineEdit()
# # # # # #         self.input_current_height.setPlaceholderText("2040")
# # # # # #         height_layout.addWidget(self.input_current_height)
# # # # # #         height_layout.addWidget(QLabel("➡️ Нова:"))
# # # # # #         self.input_target_height = QLineEdit()
# # # # # #         self.input_target_height.setPlaceholderText("2050")
# # # # # #         height_layout.addWidget(self.input_target_height)
# # # # # #         auto_scale_box.addLayout(height_layout)

# # # # # #         self.lbl_status_calc = QLabel("Введіть розміри та натисніть кнопку нижче")
# # # # # #         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
# # # # # #         auto_scale_box.addWidget(self.lbl_status_calc)

# # # # # #         self.btn_apply_auto_scale = QPushButton("⚡ Автоматично розрахувати дельту та змінити")
# # # # # #         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
# # # # # #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# # # # # #         auto_scale_box.addWidget(self.btn_apply_auto_scale)

# # # # # #         auto_scale_group.setLayout(auto_scale_box)
# # # # # #         control_layout.addWidget(auto_scale_group)

# # # # # #         # --- БЛОК 2: ОРІЄНТАЦІЯ ТА ОБЕРТАННЯ ДЕТАЛЕЙ ---
# # # # # #         transform_group = QGroupBox("🔄 Орієнтація та обертання виділених деталей")
# # # # # #         transform_box = QVBoxLayout()
        
# # # # # #         rot_layout = QHBoxLayout()
# # # # # #         self.btn_rot_90 = QPushButton("↪️ Поворот 90°")
# # # # # #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# # # # # #         self.btn_rot_180 = QPushButton("🔁 Поворот 180°")
# # # # # #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# # # # # #         rot_layout.addWidget(self.btn_rot_90)
# # # # # #         rot_layout.addWidget(self.btn_rot_180)
# # # # # #         transform_box.addLayout(rot_layout)

# # # # # #         mirror_layout = QHBoxLayout()
# # # # # #         self.btn_mirror_h = QPushButton("↔️ Віддзеркалити по Х")
# # # # # #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# # # # # #         self.btn_mirror_v = QPushButton("↕️ Віддзеркалити по Y")
# # # # # #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
# # # # # #         mirror_layout.addWidget(self.btn_mirror_h)
# # # # # #         mirror_layout.addWidget(self.btn_mirror_v)
# # # # # #         transform_box.addLayout(mirror_layout)

# # # # # #         transform_group.setLayout(transform_box)
# # # # # #         control_layout.addWidget(transform_group)

# # # # # #         # --- БЛОК 3: ИНЖЕНЕРНЕ ПРИТИСКАННЯ (БАЗУВАННЯ) ---
# # # # # #         align_group = QGroupBox("📍 Притулити (базувати) виділене до краю дверей")
# # # # # #         align_box = QVBoxLayout()

# # # # # #         align_x_layout = QHBoxLayout()
# # # # # #         self.btn_align_left = QPushButton("🟢 До лівого краю (Х)")
# # # # # #         self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
# # # # # #         self.btn_align_right = QPushButton("🔴 До правого краю (Х)")
# # # # # #         self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
# # # # # #         align_x_layout.addWidget(self.btn_align_left)
# # # # # #         align_x_layout.addWidget(self.btn_align_right)
# # # # # #         align_box.addLayout(align_x_layout)

# # # # # #         align_y_layout = QHBoxLayout()
# # # # # #         self.btn_align_bottom = QPushButton("🔵 До нижнього краю (Y)")
# # # # # #         self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
# # # # # #         self.btn_align_top = QPushButton("🟡 До верхнього краю (Y)")
# # # # # #         self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
# # # # # #         align_y_layout.addWidget(self.btn_align_bottom)
# # # # # #         align_y_layout.addWidget(self.btn_align_top)
# # # # # #         align_box.addLayout(align_y_layout)

# # # # # #         align_group.setLayout(align_box)
# # # # # #         control_layout.addWidget(align_group)

# # # # # #         # --- БЛОК СТИЛЮ ТА ТЕМИ ---
# # # # # #         theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
# # # # # #         theme_box = QHBoxLayout()
# # # # # #         theme_box.addWidget(QLabel("Тема:"))
# # # # # #         self.theme_combo = QComboBox()
# # # # # #         self.theme_combo.addItems(["Темна", "Світла"])
# # # # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # # # #         theme_box.addWidget(self.theme_combo)
# # # # # #         theme_group.setLayout(theme_box)
# # # # # #         control_layout.addWidget(theme_group)

# # # # # #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# # # # # #         history_group = QGroupBox("Історія конструкторських змін")
# # # # # #         history_box = QHBoxLayout()
# # # # # #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# # # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # # #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# # # # # #         self.btn_redo.clicked.connect(self.redo)
# # # # # #         history_box.addWidget(self.btn_undo)
# # # # # #         history_box.addWidget(self.btn_redo)
# # # # # #         history_group.setLayout(history_box)
# # # # # #         control_layout.addWidget(history_group)
# # # # # #         self.update_history_buttons_state()

# # # # # #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# # # # # #         fix_group = QGroupBox("1.  Фіксація жорстких блоків (елементів фурнітури)")
# # # # # #         fix_box = QVBoxLayout()
# # # # # #         h_fix_layout = QHBoxLayout()
# # # # # #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# # # # # #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# # # # # #         self.btn_set_left_fix.setObjectName("leftFixBtn")
# # # # # #         self.btn_set_right_fix.setObjectName("rightFixBtn")
# # # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # # #         h_fix_layout.addWidget(self.btn_set_left_fix)
# # # # # #         h_fix_layout.addWidget(self.btn_set_right_fix)
# # # # # #         fix_box.addLayout(h_fix_layout)

# # # # # #         v_fix_layout = QHBoxLayout()
# # # # # #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# # # # # #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# # # # # #         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
# # # # # #         self.btn_set_top_fix.setObjectName("topFixBtn")
# # # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# # # # # #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# # # # # #         v_fix_layout.addWidget(self.btn_set_top_fix)
# # # # # #         fix_box.addLayout(v_fix_layout)
# # # # # #         fix_group.setLayout(fix_box)
# # # # # #         control_layout.addWidget(fix_group)

# # # # # #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# # # # # #         zone_group = QGroupBox("2. Створення зон деформації простору")
# # # # # #         zone_box = QVBoxLayout()
# # # # # #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# # # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # # #         zone_box.addWidget(self.btn_add_zone_x)
# # # # # #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# # # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # # #         zone_box.addWidget(self.btn_add_zone_y)
# # # # # #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# # # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# # # # # #         zone_box.addWidget(self.btn_clear_zones)
# # # # # #         zone_group.setLayout(zone_box)
# # # # # #         control_layout.addWidget(zone_group)

# # # # # #         control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
# # # # # #         self.zone_list_widget = QListWidget()
# # # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # # #         control_layout.addWidget(self.zone_list_widget)

# # # # # #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# # # # # #         self.entity_list = QListWidget()
# # # # # #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# # # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# # # # # #         control_layout.addWidget(self.entity_list)

# # # # # #         self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
# # # # # #         control_layout.addWidget(self.slider_label)
# # # # # #         self.slider = QSlider(Qt.Orientation.Horizontal)
# # # # # #         self.slider.setRange(0, 600)
# # # # # #         self.slider.setEnabled(False)
# # # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # # #         control_layout.addWidget(self.slider)

# # # # # #         control_layout.addStretch()

# # # # # #     # ---------------------------
# # # # # #     # МЕТОДИ ФІКСАЦІЇ ЕЛЕМЕНТІВ ФУРНІТУРИ
# # # # # #     # ---------------------------
# # # # # #     def assign_to_left_fix(self):
# # # # # #         self.left_fixed_handles.update(self.selected_handles)
# # # # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # # # #         self.auto_detect_between_zone('X')
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     def assign_to_right_fix(self):
# # # # # #         self.right_fixed_handles.update(self.selected_handles)
# # # # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # # # #         self.auto_detect_between_zone('X')
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     def assign_to_bottom_fix(self):
# # # # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # # # #         self.auto_detect_between_zone('Y')
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     def assign_to_top_fix(self):
# # # # # #         self.top_fixed_handles.update(self.selected_handles)
# # # # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # # # #         self.auto_detect_between_zone('Y')
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     # ---------------------------
# # # # # #     # ЛОГІКА АВТОМАТИЧНОЇ АДАПТАЦІЇ ТА КАСКАДНОГО ОНОВЛЕННЯ ІНФОРМАЦІЇ ПРО ЗОНИ
# # # # # #     # ---------------------------
# # # # # #     def process_manual_input_dimension_scale(self):
# # # # # #         if not self.stretch_zones:
# # # # # #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
# # # # # #             return

# # # # # #         cur_w_str = self.input_current_width.text().strip()
# # # # # #         new_w_str = self.input_target_width.text().strip()
# # # # # #         cur_h_str = self.input_current_height.text().strip()
# # # # # #         new_h_str = self.input_target_height.text().strip()

# # # # # #         delta_x = float(new_w_str) - float(cur_w_str) if (cur_w_str and new_w_str) else 0.0
# # # # # #         delta_y = float(new_h_str) - float(cur_h_str) if (cur_h_str and new_h_str) else 0.0

# # # # # #         if delta_x == 0.0 and delta_y == 0.0:
# # # # # #             self.lbl_status_calc.setText("<font color='yellow'>Різниця 0 мм. Змініть значення.</font>")
# # # # # #             return

# # # # # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # # # # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # # # # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # # # # #         # Тимчасово записуємо дельти стрейчу для кожної зони, щоб прогнати через каскадний зміщувач
# # # # # #         for zone in self.stretch_zones:
# # # # # #             if zone['axis'] == 'X':
# # # # # #                 zone['stretch_val'] = share_delta_x
# # # # # #             elif zone['axis'] == 'Y':
# # # # # #                 zone['stretch_val'] = share_delta_y

# # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # #             entity = self.doc.entitydb[hndl]

# # # # # #             if orig["type"] == "CIRCLE":
# # # # # #                 cx, cy, cz = orig["center"]
# # # # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # # # #             elif orig["type"] == "LINE":
# # # # # #                 sx, sy, sz = orig["start"]
# # # # # #                 ex, ey, ez = orig["end"]
# # # # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

# # # # # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Адаптовано: ΔX={delta_x:+.1f}мм | ΔY={delta_y:+.1f}мм</font>")
        
# # # # # #         # Фізично фіксуємо зміни в DXF
# # # # # #         self.doc.saveas(self.dxf_path)
        
# # # # # #         # КРИТИЧНЕ ОНОВЛЕННЯ ІНФОРМАЦІЇ: Фізично перераховуємо текстові межі для ВСІХ зон у масиві
# # # # # #         for zone in self.stretch_zones:
# # # # # #             stretch_amount = zone['stretch_val']
# # # # # #             if stretch_amount == 0: continue
# # # # # #             active_axis = zone['axis']
# # # # # #             active_max = zone['max']
# # # # # #             zone['max'] += stretch_amount
# # # # # #             for sub_z in self.stretch_zones:
# # # # # #                 if sub_z == zone or sub_z['axis'] != active_axis: continue
# # # # # #                 if sub_z['min'] >= active_max:
# # # # # #                     sub_z['min'] += stretch_amount
# # # # # #                     sub_z['max'] += stretch_amount

# # # # # #         # Скидаємо приріст, оскільки координати меж прямокутників тепер стали новою статичною базою виробу
# # # # # #         for zone in self.stretch_zones:
# # # # # #             zone['stretch_val'] = 0.0

# # # # # #         # Запис у стеки історії змін
# # # # # #         self.history.save_state()
# # # # # #         self.history.clear_redo()
# # # # # #         self.save_zones_history_state()
# # # # # #         self.zones_redo_stack.clear()
# # # # # #         self.update_history_buttons_state()
# # # # # #         self.save_original_geometries()

# # # # # #         self.input_current_width.clear()
# # # # # #         self.input_target_width.clear()
# # # # # #         self.input_current_height.clear()
# # # # # #         self.input_target_height.clear()

# # # # # #         # Повністю синхронізуємо та оновлюємо текстовий список зон на екрані!
# # # # # #         self.load_zones_into_list()
# # # # # #         self.load_entities_into_list()
# # # # # #         self.update_viewer()

# # # # # #     # ---------------------------
# # # # # #     # ЛОГІКА ОБЕРТАННЯ ТА ДЗЕРКАЛА (МАТРИЦЯ EZDXF)
# # # # # #     # ---------------------------
# # # # # #     def transform_selected_entities(self, mode):
# # # # # #         if not self.selected_handles: return
# # # # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # #         if not selected_entities: return

# # # # # #         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
# # # # # #         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

# # # # # #         for entity in selected_entities:
# # # # # #             if mode == "ROT90":
# # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotation(math.radians(90)), Matrix44.translate(cx, cy, 0))
# # # # # #             elif mode == "ROT180":
# # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotation(math.radians(180)), Matrix44.translate(cx, cy, 0))
# # # # # #             elif mode == "MIRROR_H":
# # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
# # # # # #             elif mode == "MIRROR_V":
# # # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
# # # # # #             else: continue
# # # # # #             entity.transform(m)

# # # # # #         self.doc.saveas(self.dxf_path)
# # # # # #         self.history.save_state()
# # # # # #         self.save_zones_history_state()
# # # # # #         self.save_original_geometries()
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     # ---------------------------
# # # # # #     # ЛОГІКА ПРИТУЛЕННЯ ДО КРАЇВ (БАЗУВАННЯ З ВІДСТУПОМ 5ММ)
# # # # # #     # ---------------------------
# # # # # #     def align_selected_to_edge(self, edge):
# # # # # #         if not self.selected_handles: return
# # # # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # #         if not selected_entities: return

# # # # # #         try:
# # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # #             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
# # # # # #             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
# # # # # #         except Exception:
# # # # # #             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

# # # # # #         margin = 5.0
# # # # # #         shift_x, shift_y = 0.0, 0.0

# # # # # #         sel_min_x = min(e.left_x for e in selected_entities)
# # # # # #         sel_max_x = max(e.right_x for e in selected_entities)
# # # # # #         sel_min_y = min(e.bottom_y for e in selected_entities)
# # # # # #         sel_max_y = max(e.top_y for e in selected_entities)

# # # # # #         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
# # # # # #         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
# # # # # #         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
# # # # # #         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

# # # # # #         for entity in selected_entities:
# # # # # #             entity.translate(shift_x, shift_y, 0)

# # # # # #         self.doc.saveas(self.dxf_path)
# # # # # #         self.history.save_state()
# # # # # #         self.save_zones_history_state()
# # # # # #         self.save_original_geometries()
# # # # # #         self.update_viewer()
# # # # # #         self.load_entities_into_list()

# # # # # #     # ---------------------------
# # # # # #     # СЛУЖБОВІ СТЕКИ UNDO / REDO
# # # # # #     # ---------------------------
# # # # # #     def save_zones_history_state(self):
# # # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # # #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# # # # # #     def undo(self):
# # # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # # #             current_zones = self.zones_undo_stack.pop()
# # # # # #             self.zones_redo_stack.append(current_zones)
# # # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # # #             self.reload_after_history_change()

# # # # # #     def redo(self):
# # # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # # #             next_zones = self.zones_redo_stack.pop()
# # # # # #             self.zones_undo_stack.append(next_zones)
# # # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # # #             self.reload_after_history_change()

# # # # # #     def update_history_buttons_state(self):
# # # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # # #     def reload_after_history_change(self):
# # # # # #         self.is_loading_history = True
# # # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # # #         self.save_original_geometries()
# # # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0
# # # # # #         self.slider.blockSignals(True)
# # # # # #         self.slider.setValue(0)
# # # # # #         self.slider.blockSignals(False)
# # # # # #         self.update_viewer()
# # # # # #         self.load_zones_into_list()
# # # # # #         self.load_entities_into_list()
# # # # # #         self.update_history_buttons_state()
# # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # #         self.is_loading_history = False

# # # # # #     def on_theme_changed(self, theme_name):
# # # # # #         self.current_theme = theme_name
# # # # # #         self.set_interface_theme(theme_name)
# # # # # #         self.update_viewer()

# # # # # #     def set_interface_theme(self, theme_name):
# # # # # #         if theme_name == "Темна":
# # # # # #             self.setStyleSheet("""
# # # # # #                 QMainWindow { background-color: #252526; }
# # # # # #                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
# # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
# # # # # #                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
# # # # # #                 QPushButton:hover { background-color: #505050; }
# # # # # #                 QLineEdit { background-color: #1e1e1e; border: 1px solid #555555; color: white; padding: 4px; border-radius: 3px; }
# # # # # #                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
# # # # # #                 QListWidget::item:selected { background-color: #04396c; color: white; }
# # # # # #                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
# # # # # #                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
# # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # #                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
# # # # # #                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
# # # # # #                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
# # # # # #                 #topFixBtn { background-color: #524705; color: #fffde7; }
# # # # # #             """)
# # # # # #         else:
# # # # # #             self.setStyleSheet("""
# # # # # #                 QMainWindow { background-color: #f3f3f3; }
# # # # # #                 QWidget { color: #000000; font-family: 'Segoe UI'; }
# # # # # #                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
# # # # # #                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
# # # # # #                 QPushButton:hover { background-color: #d0d0d0; }
# # # # # #                 QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: black; padding: 4px; border-radius: 3px; }
# # # # # #                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
# # # # # #                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
# # # # # #                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
# # # # # #                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
# # # # # #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# # # # # #                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
# # # # # #                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
# # # # # #                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
# # # # # #                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
# # # # # #             """)

# # # # # #     def auto_detect_between_zone(self, axis):
# # # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
# # # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
# # # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
# # # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # # #     def load_zones_into_list(self):
# # # # # #         self.zone_list_widget.blockSignals(True)
# # # # # #         self.zone_list_widget.clear()
# # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}]"
# # # # # #             item = QListWidgetItem(text)
# # # # # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # # # # #             self.zone_list_widget.addItem(item)
# # # # # #         self.zone_list_widget.blockSignals(False)

# # # # # #     def on_zone_selection_changed(self):
# # # # # #         selected = self.zone_list_widget.selectedItems()
# # # # # #         if not selected:
# # # # # #             self.active_zone_index = None
# # # # # #             self.slider.setEnabled(False)
# # # # # #             return
# # # # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # #         self.slider.blockSignals(True)
# # # # # #         self.slider.setEnabled(True)
# # # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # # #         self.slider.blockSignals(False)
# # # # # #         self.update_viewer()

# # # # # #     # ---------------------------
# # # # # #     # ЗБЕРЕЖЕНІ ТА ВІДНОВЛЕНІ МЕТОДИ РУЧНОГО СЛАЙДЕРА
# # # # # #     # ---------------------------
# # # # # #     def on_slider_value_changed(self, value):
# # # # # #         """Здійснює динамічне відображення каскадного розтягування при русі повзунка."""
# # # # # #         if self.active_zone_index is None or self.is_loading_history: 
# # # # # #             return
# # # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # # #         for hndl, orig in self.original_geometries.items():
# # # # # #             if hndl not in self.doc.entitydb: continue
# # # # # #             entity = self.doc.entitydb[hndl]
# # # # # #             if orig["type"] == "CIRCLE":
# # # # # #                 cx, cy, cz = orig["center"]
# # # # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # # # #             elif orig["type"] == "LINE":
# # # # # #                 sx, sy, sz = orig["start"]
# # # # # #                 ex, ey, ez = orig["end"]
# # # # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)
# # # # # #         self.update_viewer()

# # # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # # #         """Математичний двигун: прораховує 2D зсуви з урахуванням каскадів та фіксаторів."""
# # # # # #         if axis == 'X' and hndl:
# # # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # # #             if hndl in self.right_fixed_handles:
# # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # # #         elif axis == 'Y' and hndl:
# # # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # # #             if hndl in self.top_fixed_handles:
# # # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # # #         shifted_val = orig_val
# # # # # #         for zone in self.stretch_zones:
# # # # # #             if zone['axis'] != axis: continue
# # # # # #             z_min = zone['min']
# # # # # #             z_max = zone['max']
# # # # # #             val = zone['stretch_val']

# # # # # #             if orig_val >= z_max: shifted_val += val
# # # # # #             elif z_min < orig_val < z_max:
# # # # # #                 width = z_max - z_min
# # # # # #                 if width > 0: shifted_val += val * ((orig_val - z_min) / width)
                    
# # # # # #         return shifted_val

# # # # # #     def on_slider_released(self):
# # # # # #         self.doc.saveas(self.dxf_path)
# # # # # #         active_zone = self.stretch_zones[self.active_zone_index] if self.active_zone_index is not None else None
        
# # # # # #         if active_zone:
# # # # # #             stretch_amount = active_zone['stretch_val']
# # # # # #             active_axis = active_zone['axis']
# # # # # #             active_max = active_zone['max']
# # # # # #             active_zone['max'] += stretch_amount
# # # # # #             for idx, zone in enumerate(self.stretch_zones):
# # # # # #                 if idx == self.active_zone_index or zone['axis'] != active_axis: continue
# # # # # #                 if zone['min'] >= active_max:
# # # # # #                     zone['min'] += stretch_amount
# # # # # #                     zone['max'] += stretch_amount

# # # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # # # # #         self.history.save_state()
# # # # # #         self.history.clear_redo()
# # # # # #         self.save_zones_history_state()
# # # # # #         self.zones_redo_stack.clear()
# # # # # #         self.update_history_buttons_state()
# # # # # #         self.save_original_geometries()

# # # # # #         self.slider.blockSignals(True)
# # # # # #         self.slider.setValue(0)
# # # # # #         self.slider.blockSignals(False)

# # # # # #         self.load_zones_into_list()
# # # # # #         self.load_entities_into_list()
# # # # # #         self.update_viewer()

# # # # # #     # ---------------------------
# # # # # #     # МЕТОД ПОВНОГО СКИНУТИ ВСІХ ПАРАМЕТРИЧНИХ ЗОН ТА ФІКСАЦІЙ
# # # # # #     # ---------------------------
# # # # # #     def reset_all_parametric_zones(self):
# # # # # #         """Повністю очищає всі зафіксовані блоки фурнітури та створені прямокутники деформації."""
# # # # # #         self.left_fixed_handles.clear()
# # # # # #         self.right_fixed_handles.clear()
# # # # # #         self.bottom_fixed_handles.clear()
# # # # # #         self.top_fixed_handles.clear()
# # # # # #         self.stretch_zones.clear()
# # # # # #         self.active_zone_index = None
# # # # # #         self.slider.setEnabled(False)
# # # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # # #         self.update_viewer()
# # # # # #         self.load_zones_into_list()
# # # # # #         self.load_entities_into_list()

# # # # # #     # ---------------------------
# # # # # #     # ВІЗУАЛІЗАЦІЯ СЦЕНИ ТА СТВОРЕННЯ КООРДИНАТНИХ ОСЕЙ
# # # # # #     # ---------------------------
# # # # # #     def update_viewer(self):
# # # # # #         self.scene = QGraphicsScene()
# # # # # #         self.view.setScene(self.scene)
# # # # # #         self.overlay_items.clear()

# # # # # #         if self.current_theme == "Темна":
# # # # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # # # # #             base_line_color = QColor(220, 220, 220)
# # # # # #         else:
# # # # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # # # # #             base_line_color = QColor(80, 80, 80)

# # # # # #         # МАЛЮЄМО СИСТЕМУ КООРДИНАТНИХ ОСЕЙ
# # # # # #         axis_len = 150.0
# # # # # #         self.scene.addLine(-50, 0, axis_len, 0, QPen(QColor(33, 150, 243), 2.5))
# # # # # #         self.scene.addLine(axis_len, 0, axis_len - 10, -4, QPen(QColor(33, 150, 243), 2.5))
# # # # # #         self.scene.addLine(axis_len, 0, axis_len - 10, 4, QPen(QColor(33, 150, 243), 2.5))
# # # # # #         self.scene.addLine(0, 50, 0, -axis_len, QPen(QColor(76, 175, 80), 2.5))
# # # # # #         self.scene.addLine(0, -axis_len, -4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))
# # # # # #         self.scene.addLine(0, -axis_len, 4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))

# # # # # #         seen_circles, seen_lines = set(), set()
# # # # # #         try:
# # # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # # #         except Exception:
# # # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']
# # # # # #             if zone['axis'] == 'X':
# # # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # # #             else:
# # # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # # #             if idx == self.active_zone_index:
# # # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # # #                 rect_item.setBrush(QBrush(color))
# # # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # # # #             else:
# # # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # # # # #             self.scene.addItem(rect_item)

# # # # # #         for entity in self.doc.modelspace():
# # # # # #             hndl = entity.dxf.handle
# # # # # #             tp = entity.dxftype()
# # # # # #             pyqt_item = None
# # # # # #             if tp == "CIRCLE":
# # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # #                 r = entity.dxf.radius
# # # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
# # # # # #             elif tp == "LINE":
# # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # # #             if pyqt_item:
# # # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
# # # # # #                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # # # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
# # # # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # #                 self.scene.addItem(pyqt_item)
# # # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # # #     def create_zone_from_selection(self, axis):
# # # # # #         if not self.selected_handles or not self.original_geometries: return
# # # # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # # #         if not active_entities or len(active_entities) < 2: 
# # # # # #             self.clear_selection()
# # # # # #             return
# # # # # #         if axis == 'X':
# # # # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # # # #         else:
# # # # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
# # # # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# # # # # #         self.clear_selection()

# # # # # #     def process_manual_rubber_band(self, rect):
# # # # # #         self.selected_handles.clear()
# # # # # #         path = QPainterPath()
# # # # # #         path.addRect(rect)
# # # # # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # # # # #         for item in matched_items:
# # # # # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # # # # #             if hndl: self.selected_handles.add(hndl)
# # # # # #         self.sync_list_from_handles()
# # # # # #         self.update_viewer()

# # # # # #     def sync_list_from_handles(self):
# # # # # #         self.entity_list.blockSignals(True)
# # # # # #         self.entity_list.clearSelection()
# # # # # #         for i in range(self.entity_list.count()):
# # # # # #             item = self.entity_list.item(i)
# # # # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # # # #         self.entity_list.blockSignals(False)

# # # # # #     def on_list_selection_changed(self):
# # # # # #         self.selected_handles.clear()
# # # # # #         for item in self.entity_list.selectedItems():
# # # # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # # # #         self.update_viewer()

# # # # # #     def clear_selection(self):
# # # # # #         self.selected_handles.clear()
# # # # # #         self.update_viewer()
# # # # # #         self.entity_list.blockSignals(True)
# # # # # #         self.entity_list.clearSelection()
# # # # # #         self.entity_list.blockSignals(False)

# # # # # #     def load_entities_into_list(self):
# # # # # #         self.entity_list.blockSignals(True)
# # # # # #         self.entity_list.clear()
# # # # # #         seen = set()
# # # # # #         for entity in self.doc.modelspace():
# # # # # #             tp = entity.dxftype()
# # # # # #             hndl = entity.dxf.handle
# # # # # #             if tp == "CIRCLE":
# # # # # #                 cx, cy, _ = entity.dxf.center
# # # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # # #                 seen.add((round(cx, 2), round(cy, 2)))
# # # # # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # # # # #             elif tp == "LINE":
# # # # # #                 x1, y1, _ = entity.dxf.start
# # # # # #                 x2, y2, _ = entity.dxf.end
# # # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм"
# # # # # #             else: continue
# # # # # #             item = QListWidgetItem(text)
# # # # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # # #             self.entity_list.addItem(item)
# # # # # #         self.entity_list.blockSignals(False)


# # # # # import os
# # # # # import sys
# # # # # import math
# # # # # import copy

# # # # # import ezdxf
# # # # # import ezdxf.bbox as dxf_bbox
# # # # # from ezdxf.math import Matrix44

# # # # # from PySide6.QtWidgets import QGraphicsScene, QListWidgetItem, QGraphicsEllipseItem
# # # # # from PySide6.QtCore import Qt
# # # # # from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath

# # # # # from graphics_items import SelectableCircle, SelectableLine
# # # # # from history_manager import HistoryManager

# # # # # # Підключаємо наш винесений ізольований модуль інтерфейсу
# # # # # from cad_ui_blocks import CADUiLayout

# # # # # class MiniCAD(CADUiLayout):
# # # # #     def __init__(self):
# # # # #         super().__init__()

# # # # #         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор")
# # # # #         self.setGeometry(100, 100, 1600, 950)

# # # # #         # Визначаємо робочу директорію папки проектів
# # # # #         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
# # # # #         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
# # # # #         self.current_theme = "Темна"

# # # # #         self.selected_handles = set()
# # # # #         self.overlay_items = {}
# # # # #         self.original_geometries = {}
# # # # #         self.is_loading_history = False

# # # # #         self.left_fixed_handles = set()
# # # # #         self.right_fixed_handles = set()
# # # # #         self.bottom_fixed_handles = set()
# # # # #         self.top_fixed_handles = set()
        
# # # # #         self.stretch_zones = []
# # # # #         self.active_zone_index = None

# # # # #         self.zones_undo_stack = []
# # # # #         self.zones_redo_stack = []

# # # # #         # Стабільне завантаження стартової моделі
# # # # #         if os.path.exists(self.dxf_path):
# # # # #             self.doc = ezdxf.readfile(self.dxf_path)
# # # # #         else:
# # # # #             self.doc = ezdxf.new()
# # # # #             self.doc.saveas(self.dxf_path)

# # # # #         self.history = HistoryManager(self.dxf_path)
# # # # #         self.history.save_state()
# # # # #         self.save_zones_history_state()

# # # # #         # Збираємо інтерфейс з ізольованого файлу компонування
# # # # #         self.build_ui_structure()
# # # # #         self.connect_ui_signals()
        
# # # # #         self.set_interface_theme(self.current_theme)
# # # # #         self.save_original_geometries()
# # # # #         self.update_viewer()
# # # # #         self.load_entities_into_list()
# # # # #         self.scan_project_folder_for_dxf()

# # # # #     def connect_ui_signals(self):
# # # # #         """Створює залізобетонні зв'язки між кнопками та алгоритмами."""
# # # # #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# # # # #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# # # # #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# # # # #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# # # # #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
        
# # # # #         self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
# # # # #         self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
# # # # #         self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
# # # # #         self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
        
# # # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # # #         self.btn_undo.clicked.connect(self.undo)
# # # # #         self.btn_redo.clicked.connect(self.redo)
        
# # # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
        
# # # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
        
# # # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        
# # # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # # #         self.file_explorer_list.itemClicked.connect(self.on_dxf_file_selected_from_explorer)

# # # # #     # ---------------------------
# # # # #     # ЛОГІКА СКАНУВАННЯ ТА ПЕРЕМИКАННЯ ФАЙЛІВ З ЛІВОЇ ПАНЕЛІ ПРОВІДНИКА
# # # # #     # ---------------------------
# # # # #     def scan_project_folder_for_dxf(self):
# # # # #         self.file_explorer_list.blockSignals(True)
# # # # #         self.file_explorer_list.clear()
# # # # #         try:
# # # # #             files = os.listdir(self.project_dir)
# # # # #             dxf_files = [f for f in files if f.lower().endswith('.dxf')]
# # # # #             for file_name in dxf_files:
# # # # #                 item = QListWidgetItem(f"📄 {file_name}")
# # # # #                 item.setData(Qt.ItemDataRole.UserRole, file_name)
# # # # #                 self.file_explorer_list.addItem(item)
# # # # #                 if file_name.lower() == os.path.basename(self.dxf_path).lower():
# # # # #                     self.file_explorer_list.setCurrentItem(item)
# # # # #         except Exception as e:
# # # # #             print(f"Помилка сканування: {e}")
# # # # #         self.file_explorer_list.blockSignals(False)

# # # # #     def on_dxf_file_selected_from_explorer(self, item):
# # # # #         file_name = item.data(Qt.ItemDataRole.UserRole)
# # # # #         new_dxf_path = os.path.join(self.project_dir, file_name)
# # # # #         if not os.path.exists(new_dxf_path): return
        
# # # # #         self.dxf_path = new_dxf_path
# # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # #         self.selected_handles.clear()
# # # # #         self.reset_all_parametric_zones()
        
# # # # #         self.history = HistoryManager(self.dxf_path)
# # # # #         self.history.save_state()
# # # # #         self.zones_undo_stack.clear()
# # # # #         self.zones_redo_stack.clear()
# # # # #         self.save_zones_history_state()
        
# # # # #         self.save_original_geometries()
# # # # #         self.update_viewer()
# # # # #         self.load_entities_into_list()
# # # # #         self.update_history_buttons_state()
# # # # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Відкрито: {file_name}</font>")

# # # # #     def save_original_geometries(self):
# # # # #         self.original_geometries.clear()
# # # # #         for entity in self.doc.modelspace():
# # # # #             hndl = entity.dxf.handle
# # # # #             tp = entity.dxftype()
# # # # #             if tp == "CIRCLE":
# # # # #                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
# # # # #             elif tp == "LINE":
# # # # #                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}

# # # # #     # ---------------------------
# # # # #     # АВТОМАТИЧНИЙ РОЗРАХУНОК РІЗНИЦІ ГАБАРИТІВ З ПРИПУСКАМИ
# # # # #     # ---------------------------
# # # # #     def process_manual_input_dimension_scale(self):
# # # # #         if not self.stretch_zones:
# # # # #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
# # # # #             return

# # # # #         cur_w = self.input_current_width.text().strip()
# # # # #         new_w = self.input_target_width.text().strip()
# # # # #         cur_h = self.input_current_height.text().strip()
# # # # #         new_h = self.input_target_height.text().strip()

# # # # #         delta_x = float(new_w) - float(cur_w) if (cur_w and new_w) else 0.0
# # # # #         delta_y = float(new_h) - float(cur_h) if (cur_h and new_h) else 0.0

# # # # #         if delta_x == 0.0 and delta_y == 0.0:
# # # # #             self.lbl_status_calc.setText("<font color='yellow'>Різниця 0 мм. Змініть значення.</font>")
# # # # #             return

# # # # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # # # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # # # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # # # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # # # #         for zone in self.stretch_zones:
# # # # #             if zone['axis'] == 'X': zone['stretch_val'] = share_delta_x
# # # # #             elif zone['axis'] == 'Y': zone['stretch_val'] = share_delta_y

# # # # #         for hndl, orig in self.original_geometries.items():
# # # # #             if hndl not in self.doc.entitydb: continue
# # # # #             entity = self.doc.entitydb[hndl]
# # # # #             if orig["type"] == "CIRCLE":
# # # # #                 cx, cy, cz = orig["center"]
# # # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # # #             elif orig["type"] == "LINE":
# # # # #                 sx, sy, sz = orig["start"]
# # # # #                 ex, ey, ez = orig["end"]
# # # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

# # # # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔX={delta_x:+.1f}мм | ΔY={delta_y:+.1f}мм</font>")
# # # # #         self.doc.saveas(self.dxf_path)
        
# # # # #         # КАСКАДНЕ ОНОВЛЕННЯ МЕЖ ІНШИХ ЗОН НА ЕКРАНІ
# # # # #         for zone in self.stretch_zones:
# # # # #             stretch_amount = zone['stretch_val']
# # # # #             if stretch_amount == 0: continue
# # # # #             active_axis = zone['axis']
# # # # #             active_max = zone['max']
# # # # #             zone['max'] += stretch_amount
# # # # #             for sub_z in self.stretch_zones:
# # # # #                 if sub_z == zone or sub_z['axis'] != active_axis: continue
# # # # #                 if sub_z['min'] >= active_max:
# # # # #                     sub_z['min'] += stretch_amount
# # # # #                     sub_z['max'] += stretch_amount

# # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # # # #         self.history.save_state()
# # # # #         self.history.clear_redo()
# # # # #         self.save_zones_history_state()
# # # # #         self.zones_redo_stack.clear()
# # # # #         self.update_history_buttons_state()
# # # # #         self.save_original_geometries()

# # # # #         self.input_current_width.clear()
# # # # #         self.input_target_width.clear()
# # # # #         self.input_current_height.clear()
# # # # #         self.input_target_height.clear()

# # # # #         self.load_zones_into_list()
# # # # #         self.load_entities_into_list()
# # # # #         self.update_viewer()

# # # # #     # ---------------------------
# # # # #     # МАТРИЦЯ ОБЕРТАННЯ ТА ДЗЕРКАЛА (Matrix44)
# # # # #     # ---------------------------
# # # # #     def transform_selected_entities(self, mode):
# # # # #         if not self.selected_handles: return
# # # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # #         if not selected_entities: return

# # # # #         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
# # # # #         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

# # # # #         for entity in selected_entities:
# # # # #             if mode == "ROT90":
# # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotation(math.radians(90)), Matrix44.translate(cx, cy, 0))
# # # # #             elif mode == "ROT180":
# # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotation(math.radians(180)), Matrix44.translate(cx, cy, 0))
# # # # #             elif mode == "MIRROR_H":
# # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
# # # # #             elif mode == "MIRROR_V":
# # # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
# # # # #             else: continue
# # # # #             entity.transform(m)

# # # # #         self.doc.saveas(self.dxf_path)
# # # # #         self.history.save_state()
# # # # #         self.save_zones_history_state()
# # # # #         self.save_original_geometries()
# # # # #         self.update_viewer()
# # # # #         self.load_entities_into_list()

# # # # #     # ---------------------------
# # # # #     # ЛОГІКА ІНЖЕНЕРНОГО ПРИТУЛЕННЯ ДО КРАЇВ (МАРЖА 5ММ)
# # # # #     # ---------------------------
# # # # #     def align_selected_to_edge(self, edge):
# # # # #         if not self.selected_handles: return
# # # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # # #         if not selected_entities: return

# # # # #         try:
# # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # #             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
# # # # #             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
# # # # #         except Exception:
# # # # #             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

# # # # #         margin = 5.0
# # # # #         shift_x, shift_y = 0.0, 0.0

# # # # #         sel_min_x = min(e.left_x for e in selected_entities)
# # # # #         sel_max_x = max(e.right_x for e in selected_entities)
# # # # #         sel_min_y = min(e.bottom_y for e in selected_entities)
# # # # #         sel_max_y = max(e.top_y for e in selected_entities)

# # # # #         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
# # # # #         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
# # # # #         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
# # # # #         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

# # # # #         for entity in selected_entities:
# # # # #             entity.translate(shift_x, shift_y, 0)

# # # # #         self.doc.saveas(self.dxf_path)
# # # # #         self.history.save_state()
# # # # #         self.save_zones_history_state()
# # # # #         self.save_original_geometries()
# # # # #         self.update_viewer()
# # # # #         self.load_entities_into_list()

# # # # #     # ---------------------------
# # # # #     # СИНХРОННЕ КЕРУВАННЯ ІСТОРІЄЮ UNDO / REDO
# # # # #     # ---------------------------
# # # # #     def save_zones_history_state(self):
# # # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # # #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# # # # #     def undo(self):
# # # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # # #             current_zones = self.zones_undo_stack.pop()
# # # # #             self.zones_redo_stack.append(current_zones)
# # # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # # #             self.reload_after_history_change()

# # # # #     def redo(self):
# # # # #         if self.history.redo() and self.zones_redo_stack:
# # # # #             next_zones = self.zones_redo_stack.pop()
# # # # #             self.zones_undo_stack.append(next_zones)
# # # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # # #             self.reload_after_history_change()

# # # # #     def update_history_buttons_state(self):
# # # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # # #     def reload_after_history_change(self):
# # # # #         self.is_loading_history = True
# # # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # # #         self.save_original_geometries()
# # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0
# # # # #         self.slider.blockSignals(True)
# # # # #         self.slider.setValue(0)
# # # # #         self.slider.blockSignals(False)
# # # # #         self.update_viewer()
# # # # #         self.load_zones_into_list()
# # # # #         self.load_entities_into_list()
# # # # #         self.update_history_buttons_state()
# # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # #         self.is_loading_history = False

# # # # #     def reset_all_parametric_zones(self):
# # # # #         self.left_fixed_handles.clear()
# # # # #         self.right_fixed_handles.clear()
# # # # #         self.bottom_fixed_handles.clear()
# # # # #         self.top_fixed_handles.clear()
# # # # #         self.stretch_zones.clear()
# # # # #         self.active_zone_index = None
# # # # #         self.slider.setEnabled(False)
# # # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # # #         self.update_viewer()
# # # # #         self.load_zones_into_list()
# # # # #         self.load_entities_into_list()

# # # # #     def on_theme_changed(self, theme_name):
# # # # #         self.current_theme = theme_name
# # # # #         self.set_interface_theme(theme_name)
# # # # #         self.update_viewer()

# # # # #     def auto_detect_between_zone(self, axis):
# # # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
# # # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
# # # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
# # # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # # #     def load_zones_into_list(self):
# # # # #         self.zone_list_widget.blockSignals(True)
# # # # #         self.zone_list_widget.clear()
# # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}]"
# # # # #             item = QListWidgetItem(text)
# # # # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # # # #             self.zone_list_widget.addItem(item)
# # # # #         self.zone_list_widget.blockSignals(False)

# # # # #     def on_zone_selection_changed(self):
# # # # #         selected = self.zone_list_widget.selectedItems()
# # # # #         if not selected:
# # # # #             self.active_zone_index = None
# # # # #             self.slider.setEnabled(False)
# # # # #             return
# # # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # #         self.slider.blockSignals(True)
# # # # #         self.slider.setEnabled(True)
# # # # #         self.slider.setValue(int(zone['stretch_val']))
# # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # # #         self.slider.blockSignals(False)
# # # # #         self.update_viewer()

# # # # #     # ---------------------------
# # # # #     # МАТЕМАТИКА КА-СКАДНОГО ЗСУВУ ТА РУЧНОГО СЛАЙДЕРА
# # # # #     # ---------------------------
# # # # #     def on_slider_value_changed(self, value):
# # # # #         if self.active_zone_index is None or self.is_loading_history: return
# # # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # # #         zone = self.stretch_zones[self.active_zone_index]
# # # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # # #         for hndl, orig in self.original_geometries.items():
# # # # #             if hndl not in self.doc.entitydb: continue
# # # # #             entity = self.doc.entitydb[hndl]
# # # # #             if orig["type"] == "CIRCLE":
# # # # #                 cx, cy, cz = orig["center"]
# # # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # # #             elif orig["type"] == "LINE":
# # # # #                 sx, sy, sz = orig["start"]
# # # # #                 ex, ey, ez = orig["end"]
# # # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)
# # # # #         self.update_viewer()

# # # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # # #         if axis == 'X' and hndl:
# # # # #             if hndl in self.left_fixed_handles: return orig_val
# # # # #             if hndl in self.right_fixed_handles:
# # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # # #         elif axis == 'Y' and hndl:
# # # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # # #             if hndl in self.top_fixed_handles:
# # # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # # #         shifted_val = orig_val
# # # # #         for zone in self.stretch_zones:
# # # # #             if zone['axis'] != axis: continue
# # # # #             z_min = zone['min']
# # # # #             z_max = zone['max']
# # # # #             val = zone['stretch_val']

# # # # #             if orig_val >= z_max: shifted_val += val
# # # # #             elif z_min < orig_val < z_max:
# # # # #                 width = z_max - z_min
# # # # #                 if width > 0: shifted_val += val * ((orig_val - z_min) / width)
                    
# # # # #         return shifted_val

# # # # #     def on_slider_released(self):
# # # # #         self.doc.saveas(self.dxf_path)
# # # # #         active_zone = self.stretch_zones[self.active_zone_index] if self.active_zone_index is not None else None
# # # # #         if active_zone:
# # # # #             stretch_amount = active_zone['stretch_val']
# # # # #             active_axis = active_zone['axis']
# # # # #             active_max = active_zone['max']
# # # # #             active_zone['max'] += stretch_amount
# # # # #             for idx, zone in enumerate(self.stretch_zones):
# # # # #                 if idx == self.active_zone_index or zone['axis'] != active_axis: continue
# # # # #                 if zone['min'] >= active_max:
# # # # #                     zone['min'] += stretch_amount
# # # # #                     zone['max'] += stretch_amount

# # # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # # # #         self.history.save_state()
# # # # #         self.history.clear_redo()
# # # # #         self.save_zones_history_state()
# # # # #         self.zones_redo_stack.clear()
# # # # #         self.update_history_buttons_state()
# # # # #         self.save_original_geometries()

# # # # #         self.slider.blockSignals(True)
# # # # #         self.slider.setValue(0)
# # # # #         self.slider.blockSignals(False)

# # # # #         self.load_zones_into_list()
# # # # #         self.load_entities_into_list()
# # # # #         self.update_viewer()

# # # # #     def update_viewer(self):
# # # # #         self.scene = QGraphicsScene()
# # # # #         self.view.setScene(self.scene)
# # # # #         self.overlay_items.clear()

# # # # #         if self.current_theme == "Темна":
# # # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # # # #             base_line_color = QColor(220, 220, 220)
# # # # #         else:
# # # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # # # #             base_line_color = QColor(80, 80, 80)

# # # # #         # МАЛЮЄМО СИСТЕМУ КООРДИНАТНИХ ОСЕЙ
# # # # #         axis_len = 150.0
# # # # #         self.scene.addLine(-50, 0, axis_len, 0, QPen(QColor(33, 150, 243), 2.5))
# # # # #         self.scene.addLine(axis_len, 0, axis_len - 10, -4, QPen(QColor(33, 150, 243), 2.5))
# # # # #         self.scene.addLine(axis_len, 0, axis_len - 10, 4, QPen(QColor(33, 150, 243), 2.5))
# # # # #         self.scene.addLine(0, 50, 0, -axis_len, QPen(QColor(76, 175, 80), 2.5))
# # # # #         self.scene.addLine(0, -axis_len, -4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))
# # # # #         self.scene.addLine(0, -axis_len, 4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))

# # # # #         seen_circles, seen_lines = set(), set()
# # # # #         try:
# # # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # # #         except Exception:
# # # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']
# # # # #             if zone['axis'] == 'X':
# # # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # # #             else:
# # # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # # #             if idx == self.active_zone_index:
# # # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # # #                 rect_item.setBrush(QBrush(color))
# # # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # # #             else:
# # # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # # # #             self.scene.addItem(rect_item)

# # # # #         for entity in self.doc.modelspace():
# # # # #             hndl = entity.dxf.handle
# # # # #             tp = entity.dxftype()
# # # # #             pyqt_item = None
# # # # #             if tp == "CIRCLE":
# # # # #                 cx, cy, _ = entity.dxf.center
# # # # #                 r = entity.dxf.radius
# # # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
# # # # #             elif tp == "LINE":
# # # # #                 x1, y1, _ = entity.dxf.start
# # # # #                 x2, y2, _ = entity.dxf.end
# # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # # #             if pyqt_item:
# # # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
# # # # #                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
# # # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # #                 self.scene.addItem(pyqt_item)
# # # # #                 self.overlay_items[hndl] = pyqt_item

# # # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # # #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# # # # #         for zone in self.stretch_zones:
# # # # #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0: return
# # # # #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# # # # #         self.stretch_zones.append(new_zone)
# # # # #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
# # # # #         self.load_zones_into_list()
# # # # #         for idx, zone in enumerate(self.stretch_zones):
# # # # #             if zone['axis'] == axis and zone['min'] == min_v:
# # # # #                 self.zone_list_widget.setCurrentRow(idx)
# # # # #                 break

# # # # #     def on_scene_item_clicked(self, handle):
# # # # #         self.selected_handles = {handle}
# # # # #         self.sync_list_from_handles()
# # # # #         self.update_viewer()

# # # # #     def sync_list_from_handles(self):
# # # # #         self.entity_list.blockSignals(True)
# # # # #         self.entity_list.clearSelection()
# # # # #         for i in range(self.entity_list.count()):
# # # # #             item = self.entity_list.item(i)
# # # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # # #         self.entity_list.blockSignals(False)

# # # # #     def on_list_selection_changed(self):
# # # # #         self.selected_handles.clear()
# # # # #         for item in self.entity_list.selectedItems():
# # # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # # #         self.update_viewer()

# # # # #     def clear_selection(self):
# # # # #         self.selected_handles.clear()
# # # # #         self.update_viewer()
# # # # #         self.entity_list.blockSignals(True)
# # # # #         self.entity_list.clearSelection()
# # # # #         self.entity_list.blockSignals(False)

# # # # #     def load_entities_into_list(self):
# # # # #         self.entity_list.blockSignals(True)
# # # # #         self.entity_list.clear()
# # # # #         seen = set()
# # # # #         for entity in self.doc.modelspace():
# # # # #             tp = entity.dxftype()
# # # # #             hndl = entity.dxf.handle
# # # # #             if tp == "CIRCLE":
# # # # #                 cx, cy, _ = entity.dxf.center
# # # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # # #                 seen.add((round(cx, 2), round(cy, 2)))
# # # # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # # # #             elif tp == "LINE":
# # # # #                 x1, y1, _ = entity.dxf.start
# # # # #                 x2, y2, _ = entity.dxf.end
# # # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм"
# # # # #             else: continue
# # # # #             item = QListWidgetItem(text)
# # # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # # #             self.entity_list.addItem(item)
# # # # #         self.entity_list.blockSignals(False)
# # # # import os
# # # # import sys
# # # # import math
# # # # import copy

# # # # import ezdxf
# # # # import ezdxf.bbox as dxf_bbox
# # # # from ezdxf.math import Matrix44

# # # # from PySide6.QtWidgets import QGraphicsScene, QListWidgetItem, QGraphicsEllipseItem
# # # # from PySide6.QtCore import Qt
# # # # from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath

# # # # from graphics_items import SelectableCircle, SelectableLine
# # # # from history_manager import HistoryManager

# # # # # Імпортуємо відокремлений модуль інтерфейсу
# # # # from cad_ui_blocks import CADUiLayout

# # # # class MiniCAD(CADUiLayout):
# # # #     def __init__(self):
# # # #         super().__init__()

# # # #         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор")
# # # #         self.setGeometry(100, 100, 1600, 950)

# # # #         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
# # # #         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
# # # #         self.current_theme = "Темна"

# # # #         self.selected_handles = set()
# # # #         self.overlay_items = {}
# # # #         self.original_geometries = {}
# # # #         self.is_loading_history = False

# # # #         self.left_fixed_handles = set()
# # # #         self.right_fixed_handles = set()
# # # #         self.bottom_fixed_handles = set()
# # # #         self.top_fixed_handles = set()
        
# # # #         self.stretch_zones = []
# # # #         self.active_zone_index = None

# # # #         self.zones_undo_stack = []
# # # #         self.zones_redo_stack = []

# # # #         # Динамічно ініціалізуємо патч властивостей
# # # #         self.apply_ezdxf_patch()

# # # #         if os.path.exists(self.dxf_path):
# # # #             self.doc = ezdxf.readfile(self.dxf_path)
# # # #         else:
# # # #             self.doc = ezdxf.new()
# # # #             self.doc.saveas(self.dxf_path)

# # # #         self.history = HistoryManager(self.dxf_path)
# # # #         self.history.save_state()
# # # #         self.save_zones_history_state()

# # # #         # Будуємо UI-структуру з батьківського класу cad_ui_blocks
# # # #         self.build_ui_structure()
# # # #         self.connect_ui_signals()
        
# # # #         self.set_interface_theme(self.current_theme)
# # # #         self.save_original_geometries()
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()
# # # #         self.scan_project_folder_for_dxf()

# # # #     def apply_ezdxf_patch(self):
# # # #         """Гарантує наявність left_x, right_x, bottom_y, top_y властивостей у об'єктів ezdxf."""
# # # #         from ezdxf.entities import Line, Circle
# # # #         Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # # #         Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # # #         Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # # #         Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # # #         Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # # #         Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # # #         Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # # #         Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # # #     def connect_ui_signals(self):
# # # #         """Зв'язує графічні віджети з інженерними алгоритмами."""
# # # #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# # # #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# # # #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# # # #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# # # #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
        
# # # #         self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
# # # #         self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
# # # #         self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
# # # #         self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
        
# # # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # # #         self.btn_undo.clicked.connect(self.undo)
# # # #         self.btn_redo.clicked.connect(self.redo)
        
# # # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
        
# # # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
        
# # # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        
# # # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # # #         self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)

# # # #     def scan_project_folder_for_dxf(self):
# # # #         self.file_explorer_list.blockSignals(True)
# # # #         self.file_explorer_list.clear()
# # # #         try:
# # # #             files = os.listdir(self.project_dir)
# # # #             dxf_files = [f for f in files if f.lower().endswith('.dxf')]
# # # #             for file_name in dxf_files:
# # # #                 item = QListWidgetItem(f"📄 {file_name}")
# # # #                 item.setData(Qt.ItemDataRole.UserRole, file_name)
# # # #                 self.file_explorer_list.addItem(item)
# # # #                 if file_name.lower() == os.path.basename(self.dxf_path).lower():
# # # #                     self.file_explorer_list.setCurrentItem(item)
# # # #         except Exception as e:
# # # #             print(f"Помилка провідника: {e}")
# # # #         self.file_explorer_list.blockSignals(False)

# # # #     def on_dxf_selection_changed_in_explorer(self):
# # # #         selected_items = self.file_explorer_list.selectedItems()
# # # #         if not selected_items: return
        
# # # #         base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
# # # #         self.dxf_path = os.path.join(self.project_dir, base_file_name)
# # # #         self.doc = ezdxf.readfile(self.dxf_path)
        
# # # #         self.selected_handles.clear()
# # # #         self.reset_all_parametric_zones()

# # # #         if len(selected_items) > 1:
# # # #             for item in selected_items[1:]:
# # # #                 addon_file_name = item.data(Qt.ItemDataRole.UserRole)
# # # #                 addon_path = os.path.join(self.project_dir, addon_file_name)
# # # #                 if os.path.exists(addon_path):
# # # #                     try:
# # # #                         addon_doc = ezdxf.readfile(addon_path)
# # # #                         for entity in addon_doc.modelspace():
# # # #                             entity.copy().move_to_layout(self.doc.modelspace())
# # # #                     except Exception as e:
# # # #                         print(f"Помилка накладання {addon_file_name}: {e}")

# # # #         # Примусово накладаємо інженерний патч на новоутворені класи
# # # #         self.apply_ezdxf_patch()

# # # #         self.history = HistoryManager(self.dxf_path)
# # # #         self.history.save_state()
# # # #         self.zones_undo_stack.clear()
# # # #         self.zones_redo_stack.clear()
# # # #         self.save_zones_history_state()
        
# # # #         self.save_original_geometries()
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()
# # # #         self.update_history_buttons_state()
# # # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Поєднано DXF: {len(selected_items)} шт.</font>")

# # # #     def save_original_geometries(self):
# # # #         self.original_geometries.clear()
# # # #         for entity in self.doc.modelspace():
# # # #             hndl = entity.dxf.handle
# # # #             tp = entity.dxftype()
# # # #             if tp == "CIRCLE":
# # # #                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
# # # #             elif tp == "LINE":
# # # #                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}

# # # #     def process_manual_input_dimension_scale(self):
# # # #         if not self.stretch_zones:
# # # #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
# # # #             return

# # # #         cur_w = self.input_current_width.text().strip()
# # # #         new_w = self.input_target_width.text().strip()
# # # #         cur_h = self.input_current_height.text().strip()
# # # #         new_h = self.input_target_height.text().strip()

# # # #         delta_x = float(new_w) - float(cur_w) if (cur_w and new_w) else 0.0
# # # #         delta_y = float(new_h) - float(cur_h) if (cur_h and new_h) else 0.0

# # # #         if delta_x == 0.0 and delta_y == 0.0:
# # # #             self.lbl_status_calc.setText("<font color='yellow'>Дельта 0 мм. Змініть габарити.</font>")
# # # #             return

# # # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # # #         for zone in self.stretch_zones:
# # # #             if zone['axis'] == 'X': zone['stretch_val'] = share_delta_x
# # # #             elif zone['axis'] == 'Y': zone['stretch_val'] = share_delta_y

# # # #         for hndl, orig in self.original_geometries.items():
# # # #             if hndl not in self.doc.entitydb: continue
# # # #             entity = self.doc.entitydb[hndl]
# # # #             if orig["type"] == "CIRCLE":
# # # #                 cx, cy, cz = orig["center"]
# # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # #             elif orig["type"] == "LINE":
# # # #                 sx, sy, sz = orig["start"]
# # # #                 ex, ey, ez = orig["end"]
# # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

# # # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔX={delta_x:+.1f}мм | ΔY={delta_y:+.1f}мм</font>")
# # # #         self.doc.saveas(self.dxf_path)
        
# # # #         for zone in self.stretch_zones:
# # # #             stretch_amount = zone['stretch_val']
# # # #             if stretch_amount == 0: continue
# # # #             active_axis = zone['axis']
# # # #             active_max = zone['max']
# # # #             zone['max'] += stretch_amount
# # # #             for sub_z in self.stretch_zones:
# # # #                 if sub_z == zone or sub_z['axis'] != active_axis: continue
# # # #                 if sub_z['min'] >= active_max:
# # # #                     sub_z['min'] += stretch_amount
# # # #                     sub_z['max'] += stretch_amount

# # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # # #         self.history.save_state()
# # # #         self.history.clear_redo()
# # # #         self.save_zones_history_state()
# # # #         self.zones_redo_stack.clear()
# # # #         self.update_history_buttons_state()
# # # #         self.save_original_geometries()

# # # #         self.input_current_width.clear()
# # # #         self.input_target_width.clear()
# # # #         self.input_current_height.clear()
# # # #         self.input_target_height.clear()

# # # #         self.load_zones_into_list()
# # # #         self.load_entities_into_list()
# # # #         self.update_viewer()

# # # #     def transform_selected_entities(self, mode):
# # # #         if not self.selected_handles: return
# # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # #         if not selected_entities: return

# # # #         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
# # # #         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

# # # #         for entity in selected_entities:
# # # #             if mode == "ROT90":
# # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(90)), Matrix44.translate(cx, cy, 0))
# # # #             elif mode == "ROT180":
# # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(180)), Matrix44.translate(cx, cy, 0))
# # # #             elif mode == "MIRROR_H":
# # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
# # # #             elif mode == "MIRROR_V":
# # # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
# # # #             else: continue
# # # #             entity.transform(m)

# # # #         self.doc.saveas(self.dxf_path)
# # # #         self.history.save_state()
# # # #         self.save_zones_history_state()
# # # #         self.save_original_geometries()
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()

# # # #     def align_selected_to_edge(self, edge):
# # # #         if not self.selected_handles: return
# # # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # #         if not selected_entities: return

# # # #         try:
# # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # #             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
# # # #             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
# # # #         except Exception:
# # # #             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

# # # #         margin = 5.0
# # # #         shift_x, shift_y = 0.0, 0.0

# # # #         sel_min_x = min(e.left_x for e in selected_entities)
# # # #         sel_max_x = max(e.right_x for e in selected_entities)
# # # #         sel_min_y = min(e.bottom_y for e in selected_entities)
# # # #         sel_max_y = max(e.top_y for e in selected_entities)

# # # #         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
# # # #         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
# # # #         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
# # # #         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

# # # #         for entity in selected_entities:
# # # #             entity.translate(shift_x, shift_y, 0)

# # # #         self.doc.saveas(self.dxf_path)
# # # #         self.history.save_state()
# # # #         self.save_zones_history_state()
# # # #         self.save_original_geometries()
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()

# # # #     def save_zones_history_state(self):
# # # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # # #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# # # #     def undo(self):
# # # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # # #             current_zones = self.zones_undo_stack.pop()
# # # #             self.zones_redo_stack.append(current_zones)
# # # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # # #             self.reload_after_history_change()

# # # #     def redo(self):
# # # #         if self.history.redo() and self.zones_redo_stack:
# # # #             next_zones = self.zones_redo_stack.pop()
# # # #             self.zones_undo_stack.append(next_zones)
# # # #             self.stretch_zones = copy.deepcopy(next_zones)
# # # #             self.reload_after_history_change()

# # # #     def update_history_buttons_state(self):
# # # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # # #     def reload_after_history_change(self):
# # # #         self.is_loading_history = True
# # # #         self.doc = ezdxf.readfile(self.dxf_path)
# # # #         self.save_original_geometries()
# # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0
# # # #         self.slider.blockSignals(True)
# # # #         self.slider.setValue(0)
# # # #         self.slider.blockSignals(False)
# # # #         self.update_viewer()
# # # #         self.load_zones_into_list()
# # # #         self.load_entities_into_list()
# # # #         self.update_history_buttons_state()
# # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # #         self.is_loading_history = False

# # # #     def reset_all_parametric_zones(self):
# # # #         self.left_fixed_handles.clear()
# # # #         self.right_fixed_handles.clear()
# # # #         self.bottom_fixed_handles.clear()
# # # #         self.top_fixed_handles.clear()
# # # #         self.stretch_zones.clear()
# # # #         self.active_zone_index = None
# # # #         self.slider.setEnabled(False)
# # # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # # #         self.update_viewer()
# # # #         self.load_zones_into_list()
# # # #         self.load_entities_into_list()

# # # #     def auto_detect_between_zone(self, axis):
# # # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
# # # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
# # # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
# # # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # # #     def load_zones_into_list(self):
# # # #         self.zone_list_widget.blockSignals(True)
# # # #         self.zone_list_widget.clear()
# # # #         for idx, zone in enumerate(self.stretch_zones):
# # # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}]"
# # # #             item = QListWidgetItem(text)
# # # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # # #             self.zone_list_widget.addItem(item)
# # # #         self.zone_list_widget.blockSignals(False)

# # # #     def on_zone_selection_changed(self):
# # # #         selected = self.zone_list_widget.selectedItems()
# # # #         if not selected:
# # # #             self.active_zone_index = None
# # # #             self.slider.setEnabled(False)
# # # #             return
# # # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # # #         zone = self.stretch_zones[self.active_zone_index]
# # # #         self.slider.blockSignals(True)
# # # #         self.slider.setEnabled(True)
# # # #         self.slider.setValue(int(zone['stretch_val']))
# # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # # #         self.slider.blockSignals(False)
# # # #         self.update_viewer()

# # # #     def on_slider_value_changed(self, value):
# # # #         if self.active_zone_index is None or self.is_loading_history: return
# # # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # # #         zone = self.stretch_zones[self.active_zone_index]
# # # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # # #         for hndl, orig in self.original_geometries.items():
# # # #             if hndl not in self.doc.entitydb: continue
# # # #             entity = self.doc.entitydb[hndl]
# # # #             if orig["type"] == "CIRCLE":
# # # #                 cx, cy, cz = orig["center"]
# # # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # # #             elif orig["type"] == "LINE":
# # # #                 sx, sy, sz = orig["start"]
# # # #                 ex, ey, ez = orig["end"]
# # # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)
# # # #         self.update_viewer()

# # # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # # #         if axis == 'X' and hndl:
# # # #             if hndl in self.left_fixed_handles: return orig_val
# # # #             if hndl in self.right_fixed_handles:
# # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # # #         elif axis == 'Y' and hndl:
# # # #             if hndl in self.bottom_fixed_handles: return orig_val
# # # #             if hndl in self.top_fixed_handles:
# # # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # # #         shifted_val = orig_val
# # # #         for zone in self.stretch_zones:
# # # #             if zone['axis'] != axis: continue
# # # #             z_min = zone['min']
# # # #             z_max = zone['max']
# # # #             val = zone['stretch_val']

# # # #             if orig_val >= z_max: shifted_val += val
# # # #             elif z_min < orig_val < z_max:
# # # #                 width = z_max - z_min
# # # #                 if width > 0: shifted_val += val * ((orig_val - z_min) / width)
                    
# # # #         return shifted_val

# # # #     def on_slider_released(self):
# # # #         self.doc.saveas(self.dxf_path)
# # # #         active_zone = self.stretch_zones[self.active_zone_index] if self.active_zone_index is not None else None
# # # #         if active_zone:
# # # #             stretch_amount = active_zone['stretch_val']
# # # #             active_axis = active_zone['axis']
# # # #             active_max = active_zone['max']
# # # #             active_zone['max'] += stretch_amount
# # # #             for idx, zone in enumerate(self.stretch_zones):
# # # #                 if idx == self.active_zone_index or zone['axis'] != active_axis: continue
# # # #                 if zone['min'] >= active_max:
# # # #                     zone['min'] += stretch_amount
# # # #                     zone['max'] += stretch_amount

# # # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # # #         self.history.save_state()
# # # #         self.history.clear_redo()
# # # #         self.save_zones_history_state()
# # # #         self.zones_redo_stack.clear()
# # # #         self.update_history_buttons_state()
# # # #         self.save_original_geometries()

# # # #         self.slider.blockSignals(True)
# # # #         self.slider.setValue(0)
# # # #         self.slider.blockSignals(False)

# # # #         self.load_zones_into_list()
# # # #         self.load_entities_into_list()
# # # #         self.update_viewer()

# # # #     def update_viewer(self):
# # # #         self.scene = QGraphicsScene()
# # # #         self.view.setScene(self.scene)
# # # #         self.overlay_items.clear()

# # # #         if self.current_theme == "Темна":
# # # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # # #             base_line_color = QColor(220, 220, 220)
# # # #         else:
# # # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # # #             base_line_color = QColor(80, 80, 80)

# # # #         axis_len = 150.0
# # # #         self.scene.addLine(-50, 0, axis_len, 0, QPen(QColor(33, 150, 243), 2.5))
# # # #         self.scene.addLine(axis_len, 0, axis_len - 10, -4, QPen(QColor(33, 150, 243), 2.5))
# # # #         self.scene.addLine(axis_len, 0, axis_len - 10, 4, QPen(QColor(33, 150, 243), 2.5))
# # # #         self.scene.addLine(0, 50, 0, -axis_len, QPen(QColor(76, 175, 80), 2.5))
# # # #         self.scene.addLine(0, -axis_len, -4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))
# # # #         self.scene.addLine(0, -axis_len, 4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))

# # # #         seen_circles, seen_lines = set(), set()
# # # #         try:
# # # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # # #         except Exception:
# # # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # # #         for idx, zone in enumerate(self.stretch_zones):
# # # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']
# # # #             if zone['axis'] == 'X':
# # # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # # #             else:
# # # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # # #             if idx == self.active_zone_index:
# # # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # # #                 rect_item.setBrush(QBrush(color))
# # # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # # #             else:
# # # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # # #             self.scene.addItem(rect_item)

# # # #         for entity in self.doc.modelspace():
# # # #             hndl = entity.dxf.handle
# # # #             tp = entity.dxftype()
# # # #             pyqt_item = None
# # # #             if tp == "CIRCLE":
# # # #                 cx, cy, _ = entity.dxf.center
# # # #                 r = entity.dxf.radius
# # # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
# # # #             elif tp == "LINE":
# # # #                 x1, y1, _ = entity.dxf.start
# # # #                 x2, y2, _ = entity.dxf.end
# # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # # #             if pyqt_item:
# # # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
# # # #                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
# # # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # #                 self.scene.addItem(pyqt_item)
# # # #                 self.overlay_items[hndl] = pyqt_item

# # # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # # #     def create_zone_from_selection(self, axis):
# # # #         if not self.selected_handles or not self.original_geometries: return
# # # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # # #         if not active_entities or len(active_entities) < 2: 
# # # #             self.clear_selection()
# # # #             return
# # # #         if axis == 'X':
# # # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # # #         else:
# # # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
# # # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# # # #         self.clear_selection()

# # # #     def process_manual_rubber_band(self, rect):
# # # #         self.selected_handles.clear()
# # # #         path = QPainterPath()
# # # #         path.addRect(rect)
# # # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # # #         for item in matched_items:
# # # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # # #             if hndl: self.selected_handles.add(hndl)
# # # #         self.sync_list_from_handles()
# # # #         self.update_viewer()

# # # #     def sync_list_from_handles(self):
# # # #         self.entity_list.blockSignals(True)
# # # #         self.entity_list.clearSelection()
# # # #         for i in range(self.entity_list.count()):
# # # #             item = self.entity_list.item(i)
# # # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # # #         self.entity_list.blockSignals(False)

# # # #     def on_list_selection_changed(self):
# # # #         self.selected_handles.clear()
# # # #         for item in self.entity_list.selectedItems():
# # # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # # #         self.update_viewer()

# # # #     def clear_selection(self):
# # # #         self.selected_handles.clear()
# # # #         self.update_viewer()
# # # #         self.entity_list.blockSignals(True)
# # # #         self.entity_list.clearSelection()
# # # #         self.entity_list.blockSignals(False)

# # # #     def on_theme_changed(self, theme_name):
# # # #         self.current_theme = theme_name
# # # #         self.set_interface_theme(theme_name)
# # # #         self.update_viewer()

# # # #     def assign_to_left_fix(self):
# # # #         self.left_fixed_handles.update(self.selected_handles)
# # # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # # #         self.auto_detect_between_zone('X')
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()

# # # #     def assign_to_right_fix(self):
# # # #         self.right_fixed_handles.update(self.selected_handles)
# # # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # # #         self.auto_detect_between_zone('X')
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()

# # # #     def assign_to_bottom_fix(self):
# # # #         self.bottom_fixed_handles.update(self.selected_handles)
# # # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # # #         self.auto_detect_between_zone('Y')
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()

# # # #     def assign_to_top_fix(self):
# # # #         self.top_fixed_handles.update(self.selected_handles)
# # # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # # #         self.auto_detect_between_zone('Y')
# # # #         self.update_viewer()
# # # #         self.load_entities_into_list()



# # # #     def load_entities_into_list(self):
# # # #         self.entity_list.blockSignals(True)
# # # #         self.entity_list.clear()
# # # #         seen = set()
# # # #         for entity in self.doc.modelspace():
# # # #             tp = entity.dxftype()
# # # #             hndl = entity.dxf.handle
# # # #             if tp == "CIRCLE":
# # # #                 cx, cy, _ = entity.dxf.center
# # # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # # #                 seen.add((round(cx, 2), round(cy, 2)))
# # # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # # #             elif tp == "LINE":
# # # #                 x1, y1, _ = entity.dxf.start
# # # #                 x2, y2, _ = entity.dxf.end
# # # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм"
# # # #             else: continue
# # # #             item = QListWidgetItem(text)
# # # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # # #             self.entity_list.addItem(item)
# # # #         self.entity_list.blockSignals(False)

# # # import os
# # # import sys
# # # import math
# # # import copy

# # # import ezdxf
# # # import ezdxf.bbox as dxf_bbox
# # # from ezdxf.math import Matrix44
# # # from ezdxf.addons.importer import Importer  # ВИПРАВЛЕНО: Надійний інструмент злиття креслень

# # # from PySide6.QtWidgets import QGraphicsScene, QListWidgetItem, QGraphicsEllipseItem
# # # from PySide6.QtCore import Qt
# # # from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath

# # # from graphics_items import SelectableCircle, SelectableLine
# # # from history_manager import HistoryManager

# # # # Підключаємо наш відокремлений модуль інтерфейсу
# # # from cad_ui_blocks import CADUiLayout

# # # class MiniCAD(CADUiLayout):
# # #     def __init__(self):
# # #         super().__init__()

# # #         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор")
# # #         self.setGeometry(100, 100, 1600, 950)

# # #         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
# # #         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
# # #         self.current_theme = "Темна"

# # #         self.selected_handles = set()
# # #         self.overlay_items = {}
# # #         self.original_geometries = {}
# # #         self.is_loading_history = False

# # #         self.left_fixed_handles = set()
# # #         self.right_fixed_handles = set()
# # #         self.bottom_fixed_handles = set()
# # #         self.top_fixed_handles = set()
        
# # #         self.stretch_zones = []
# # #         self.active_zone_index = None

# # #         self.zones_undo_stack = []
# # #         self.zones_redo_stack = []

# # #         # Гарантуємо наявність властивостей ezdxf
# # #         self.apply_ezdxf_patch()

# # #         if os.path.exists(self.dxf_path):
# # #             self.doc = ezdxf.readfile(self.dxf_path)
# # #         else:
# # #             self.doc = ezdxf.new()
# # #             self.doc.saveas(self.dxf_path)

# # #         self.history = HistoryManager(self.dxf_path)
# # #         self.history.save_state()
# # #         self.save_zones_history_state()

# # #         # Збираємо інтерфейс з ізольованого файлу
# # #         self.build_ui_structure()
# # #         self.connect_ui_signals()
        
# # #         self.set_interface_theme(self.current_theme)
# # #         self.save_original_geometries()
# # #         self.update_viewer()
# # #         self.load_entities_into_list()
# # #         self.scan_project_folder_for_dxf()

# # #     def apply_ezdxf_patch(self):
# # #         from ezdxf.entities import Line, Circle
# # #         Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# # #         Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# # #         Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# # #         Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# # #         Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# # #         Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# # #         Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# # #         Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # #     def connect_ui_signals(self):
# # #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# # #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# # #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# # #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# # #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
        
# # #         self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
# # #         self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
# # #         self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
# # #         self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
        
# # #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# # #         self.btn_undo.clicked.connect(self.undo)
# # #         self.btn_redo.clicked.connect(self.redo)
        
# # #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# # #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# # #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# # #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
        
# # #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# # #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# # #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
        
# # #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# # #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        
# # #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# # #         self.slider.sliderReleased.connect(self.on_slider_released)
# # #         self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)

# # #     def scan_project_folder_for_dxf(self):
# # #         self.file_explorer_list.blockSignals(True)
# # #         self.file_explorer_list.clear()
# # #         try:
# # #             files = os.listdir(self.project_dir)
# # #             dxf_files = [f for f in files if f.lower().endswith('.dxf')]
# # #             for file_name in dxf_files:
# # #                 item = QListWidgetItem(f"📄 {file_name}")
# # #                 item.setData(Qt.ItemDataRole.UserRole, file_name)
# # #                 self.file_explorer_list.addItem(item)
# # #                 if file_name.lower() == os.path.basename(self.dxf_path).lower():
# # #                     self.file_explorer_list.setCurrentItem(item)
# # #         except Exception as e:
# # #             print(f"Помилка провідника: {e}")
# # #         self.file_explorer_list.blockSignals(False)

# # #     # ---------------------------
# # #     # ЗАЛІЗОБЕТОННЕ НАКЛАДАННЯ ДЕКІЛЬКОХ КРЕСЛЕНЬ НА ОДНУ СЦЕНУ
# # #     # ---------------------------
# # #     def on_dxf_selection_changed_in_explorer(self):
# # #         selected_items = self.file_explorer_list.selectedItems()
# # #         if not selected_items: return
        
# # #         # Перший обраний файл завантажуємо як чисте полотно дверей
# # #         base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
# # #         self.dxf_path = os.path.join(self.project_dir, base_file_name)
# # #         self.doc = ezdxf.readfile(self.dxf_path)
        
# # #         self.selected_handles.clear()
# # #         self.reset_all_parametric_zones()

# # #         # Послідовно імпортуємо наступні виділені DXF-файли фурнітури через офіційний Importer
# # #         if len(selected_items) > 1:
# # #             for item in selected_items[1:]:
# # #                 addon_file_name = item.data(Qt.ItemDataRole.UserRole)
# # #                 addon_path = os.path.join(self.project_dir, addon_file_name)
# # #                 if os.path.exists(addon_path):
# # #                     try:
# # #                         addon_doc = ezdxf.readfile(addon_path)
# # #                         # Надбудова Importer залізобетонно копіює лінії, кола, шари та Handles
# # #                         importer = Importer(addon_doc, self.doc)
# # #                         importer.import_modelspace()
# # #                         importer.finalize()
# # #                     except Exception as e:
# # #                         print(f"Помилка злиття файлу {addon_file_name}: {e}")

# # #         # Повторно накочуємо патч інженерних властивостей на об'єднану базу даних
# # #         self.apply_ezdxf_patch()

# # #         self.history = HistoryManager(self.dxf_path)
# # #         self.history.save_state()
# # #         self.zones_undo_stack.clear()
# # #         self.zones_redo_stack.clear()
# # #         self.save_zones_history_state()
        
# # #         self.save_original_geometries()
# # #         self.update_viewer()
# # #         self.load_entities_into_list()
# # #         self.update_history_buttons_state()
# # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Відображено проектів: {len(selected_items)} шт.</font>")

# # #     def save_original_geometries(self):
# # #         self.original_geometries.clear()
# # #         for entity in self.doc.modelspace():
# # #             hndl = entity.dxf.handle
# # #             tp = entity.dxftype()
# # #             if tp == "CIRCLE":
# # #                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
# # #             elif tp == "LINE":
# # #                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}

# # #     def process_manual_input_dimension_scale(self):
# # #         if not self.stretch_zones:
# # #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
# # #             return

# # #         cur_w = self.input_current_width.text().strip()
# # #         new_w = self.input_target_width.text().strip()
# # #         cur_h = self.input_current_height.text().strip()
# # #         new_h = self.input_target_height.text().strip()

# # #         delta_x = float(new_w) - float(cur_w) if (cur_w and new_w) else 0.0
# # #         delta_y = float(new_h) - float(cur_h) if (cur_h and new_h) else 0.0

# # #         if delta_x == 0.0 and delta_y == 0.0:
# # #             self.lbl_status_calc.setText("<font color='yellow'>Дельта 0 мм. Змініть габарити.</font>")
# # #             return

# # #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# # #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# # #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# # #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# # #         for zone in self.stretch_zones:
# # #             if zone['axis'] == 'X': zone['stretch_val'] = share_delta_x
# # #             elif zone['axis'] == 'Y': zone['stretch_val'] = share_delta_y

# # #         for hndl, orig in self.original_geometries.items():
# # #             if hndl not in self.doc.entitydb: continue
# # #             entity = self.doc.entitydb[hndl]
# # #             if orig["type"] == "CIRCLE":
# # #                 cx, cy, cz = orig["center"]
# # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # #             elif orig["type"] == "LINE":
# # #                 sx, sy, sz = orig["start"]
# # #                 ex, ey, ez = orig["end"]
# # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), sz)
# # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

# # #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔX={delta_x:+.1f}мм | ΔY={delta_y:+.1f}мм</font>")
# # #         self.doc.saveas(self.dxf_path)
        
# # #         for zone in self.stretch_zones:
# # #             stretch_amount = zone['stretch_val']
# # #             if stretch_amount == 0: continue
# # #             active_axis = zone['axis']
# # #             active_max = zone['max']
# # #             zone['max'] += stretch_amount
# # #             for sub_z in self.stretch_zones:
# # #                 if sub_z == zone or sub_z['axis'] != active_axis: continue
# # #                 if sub_z['min'] >= active_max:
# # #                     sub_z['min'] += stretch_amount
# # #                     sub_z['max'] += stretch_amount

# # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # #         self.history.save_state()
# # #         self.history.clear_redo()
# # #         self.save_zones_history_state()
# # #         self.zones_redo_stack.clear()
# # #         self.update_history_buttons_state()
# # #         self.save_original_geometries()

# # #         self.input_current_width.clear()
# # #         self.input_target_width.clear()
# # #         self.input_current_height.clear()
# # #         self.input_target_height.clear()

# # #         self.load_zones_into_list()
# # #         self.load_entities_into_list()
# # #         self.update_viewer()

# # #     def transform_selected_entities(self, mode):
# # #         if not self.selected_handles: return
# # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # #         if not selected_entities: return

# # #         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
# # #         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

# # #         for entity in selected_entities:
# # #             if mode == "ROT90":
# # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotation(math.radians(90)), Matrix44.translate(cx, cy, 0))
# # #             elif mode == "ROT180":
# # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotation(math.radians(180)), Matrix44.translate(cx, cy, 0))
# # #             elif mode == "MIRROR_H":
# # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
# # #             elif mode == "MIRROR_V":
# # #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
# # #             else: continue
# # #             entity.transform(m)

# # #         self.doc.saveas(self.dxf_path)
# # #         self.history.save_state()
# # #         self.save_zones_history_state()
# # #         self.save_original_geometries()
# # #         self.update_viewer()
# # #         self.load_entities_into_list()

# # #     def align_selected_to_edge(self, edge):
# # #         if not self.selected_handles: return
# # #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # #         if not selected_entities: return

# # #         try:
# # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # #             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
# # #             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
# # #         except Exception:
# # #             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

# # #         margin = 5.0
# # #         shift_x, shift_y = 0.0, 0.0

# # #         sel_min_x = min(e.left_x for e in selected_entities)
# # #         sel_max_x = max(e.right_x for e in selected_entities)
# # #         sel_min_y = min(e.bottom_y for e in selected_entities)
# # #         sel_max_y = max(e.top_y for e in selected_entities)

# # #         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
# # #         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
# # #         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
# # #         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

# # #         for entity in selected_entities:
# # #             entity.translate(shift_x, shift_y, 0)

# # #         self.doc.saveas(self.dxf_path)
# # #         self.history.save_state()
# # #         self.save_zones_history_state()
# # #         self.save_original_geometries()
# # #         self.update_viewer()
# # #         self.load_entities_into_list()

# # #     def assign_to_left_fix(self):
# # #         self.left_fixed_handles.update(self.selected_handles)
# # #         self.right_fixed_handles.difference_update(self.selected_handles)
# # #         self.auto_detect_between_zone('X')
# # #         self.update_viewer()
# # #         self.load_entities_into_list()

# # #     def assign_to_right_fix(self):
# # #         self.right_fixed_handles.update(self.selected_handles)
# # #         self.left_fixed_handles.difference_update(self.selected_handles)
# # #         self.auto_detect_between_zone('X')
# # #         self.update_viewer()
# # #         self.load_entities_into_list()

# # #     def assign_to_bottom_fix(self):
# # #         self.bottom_fixed_handles.update(self.selected_handles)
# # #         self.top_fixed_handles.difference_update(self.selected_handles)
# # #         self.auto_detect_between_zone('Y')
# # #         self.update_viewer()
# # #         self.load_entities_into_list()

# # #     def assign_to_top_fix(self):
# # #         self.top_fixed_handles.update(self.selected_handles)
# # #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# # #         self.auto_detect_between_zone('Y')
# # #         self.update_viewer()
# # #         self.load_entities_into_list()

# # #     def save_zones_history_state(self):
# # #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# # #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# # #     def undo(self):
# # #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# # #             current_zones = self.zones_undo_stack.pop()
# # #             self.zones_redo_stack.append(current_zones)
# # #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# # #             self.reload_after_history_change()

# # #     def redo(self):
# # #         if self.history.redo() and self.zones_redo_stack:
# # #             next_zones = self.zones_redo_stack.pop()
# # #             self.zones_undo_stack.append(next_zones)
# # #             self.stretch_zones = copy.deepcopy(next_zones)
# # #             self.reload_after_history_change()

# # #     def update_history_buttons_state(self):
# # #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# # #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# # #     def reload_after_history_change(self):
# # #         self.is_loading_history = True
# # #         self.doc = ezdxf.readfile(self.dxf_path)
# # #         self.save_original_geometries()
# # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0
# # #         self.slider.blockSignals(True)
# # #         self.slider.setValue(0)
# # #         self.slider.blockSignals(False)
# # #         self.update_viewer()
# # #         self.load_zones_into_list()
# # #         self.load_entities_into_list()
# # #         self.update_history_buttons_state()
# # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # #         self.is_loading_history = False

# # #     def reset_all_parametric_zones(self):
# # #         self.left_fixed_handles.clear()
# # #         self.right_fixed_handles.clear()
# # #         self.bottom_fixed_handles.clear()
# # #         self.top_fixed_handles.clear()
# # #         self.stretch_zones.clear()
# # #         self.active_zone_index = None
# # #         self.slider.setEnabled(False)
# # #         self.slider_label.setText("Оберіть зону деформації зі списку")
# # #         self.update_viewer()
# # #         self.load_zones_into_list()
# # #         self.load_entities_into_list()

# # #     def auto_detect_between_zone(self, axis):
# # #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# # #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# # #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
# # #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# # #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
# # #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# # #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# # #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
# # #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# # #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# # #     def load_zones_into_list(self):
# # #         self.zone_list_widget.blockSignals(True)
# # #         self.zone_list_widget.clear()
# # #         for idx, zone in enumerate(self.stretch_zones):
# # #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# # #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}]"
# # #             item = QListWidgetItem(text)
# # #             item.setData(Qt.ItemDataRole.UserRole, idx)
# # #             self.zone_list_widget.addItem(item)
# # #         self.zone_list_widget.blockSignals(False)

# # #     def on_zone_selection_changed(self):
# # #         selected = self.zone_list_widget.selectedItems()
# # #         if not selected:
# # #             self.active_zone_index = None
# # #             self.slider.setEnabled(False)
# # #             return
# # #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# # #         zone = self.stretch_zones[self.active_zone_index]
# # #         self.slider.blockSignals(True)
# # #         self.slider.setEnabled(True)
# # #         self.slider.setValue(int(zone['stretch_val']))
# # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# # #         self.slider.blockSignals(False)
# # #         self.update_viewer()

# # #     def on_slider_value_changed(self, value):
# # #         if self.active_zone_index is None or self.is_loading_history: return
# # #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# # #         zone = self.stretch_zones[self.active_zone_index]
# # #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# # #         for hndl, orig in self.original_geometries.items():
# # #             if hndl not in self.doc.entitydb: continue
# # #             entity = self.doc.entitydb[hndl]
# # #             if orig["type"] == "CIRCLE":
# # #                 cx, cy, cz = orig["center"]
# # #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# # #             elif orig["type"] == "LINE":
# # #                 sx, sy, sz = orig["start"]
# # #                 ex, ey, ez = orig["end"]
# # #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# # #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)
# # #         self.update_viewer()

# # #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# # #         if axis == 'X' and hndl:
# # #             if hndl in self.left_fixed_handles: return orig_val
# # #             if hndl in self.right_fixed_handles:
# # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# # #         elif axis == 'Y' and hndl:
# # #             if hndl in self.bottom_fixed_handles: return orig_val
# # #             if hndl in self.top_fixed_handles:
# # #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# # #         shifted_val = orig_val
# # #         for zone in self.stretch_zones:
# # #             if zone['axis'] != axis: continue
# # #             z_min = zone['min']
# # #             z_max = zone['max']
# # #             val = zone['stretch_val']

# # #             if orig_val >= z_max: shifted_val += val
# # #             elif z_min < orig_val < z_max:
# # #                 width = z_max - z_min
# # #                 if width > 0: shifted_val += val * ((orig_val - z_min) / width)
                    
# # #         return shifted_val

# # #     def on_slider_released(self):
# # #         self.doc.saveas(self.dxf_path)
# # #         active_zone = self.stretch_zones[self.active_zone_index] if self.active_zone_index is not None else None
# # #         if active_zone:
# # #             stretch_amount = active_zone['stretch_val']
# # #             active_axis = active_zone['axis']
# # #             active_max = active_zone['max']
# # #             active_zone['max'] += stretch_amount
# # #             for idx, zone in enumerate(self.stretch_zones):
# # #                 if idx == self.active_zone_index or zone['axis'] != active_axis: continue
# # #                 if zone['min'] >= active_max:
# # #                     zone['min'] += stretch_amount
# # #                     zone['max'] += stretch_amount

# # #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# # #         self.history.save_state()
# # #         self.history.clear_redo()
# # #         self.save_zones_history_state()
# # #         self.zones_redo_stack.clear()
# # #         self.update_history_buttons_state()
# # #         self.save_original_geometries()

# # #         self.slider.blockSignals(True)
# # #         self.slider.setValue(0)
# # #         self.slider.blockSignals(False)

# # #         self.load_zones_into_list()
# # #         self.load_entities_into_list()
# # #         self.update_viewer()

# # #     def update_viewer(self):
# # #         self.scene = QGraphicsScene()
# # #         self.view.setScene(self.scene)
# # #         self.overlay_items.clear()

# # #         if self.current_theme == "Темна":
# # #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# # #             base_line_color = QColor(220, 220, 220)
# # #         else:
# # #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# # #             base_line_color = QColor(80, 80, 80)

# # #         axis_len = 150.0
# # #         self.scene.addLine(-50, 0, axis_len, 0, QPen(QColor(33, 150, 243), 2.5))
# # #         self.scene.addLine(axis_len, 0, axis_len - 10, -4, QPen(QColor(33, 150, 243), 2.5))
# # #         self.scene.addLine(axis_len, 0, axis_len - 10, 4, QPen(QColor(33, 150, 243), 2.5))
# # #         self.scene.addLine(0, 50, 0, -axis_len, QPen(QColor(76, 175, 80), 2.5))
# # #         self.scene.addLine(0, -axis_len, -4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))
# # #         self.scene.addLine(0, -axis_len, 4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))

# # #         seen_circles, seen_lines = set(), set()
# # #         try:
# # #             bounds = dxf_bbox.extents(self.doc.modelspace())
# # #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# # #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# # #         except Exception:
# # #             abs_min_x, abs_max_x = -100.0, 1000.0
# # #             abs_min_y, abs_max_y = -100.0, 2000.0

# # #         for idx, zone in enumerate(self.stretch_zones):
# # #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# # #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']
# # #             if zone['axis'] == 'X':
# # #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# # #             else:
# # #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# # #             if idx == self.active_zone_index:
# # #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# # #                 rect_item.setBrush(QBrush(color))
# # #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# # #             else:
# # #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# # #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# # #             self.scene.addItem(rect_item)

# # #         for entity in self.doc.modelspace():
# # #             hndl = entity.dxf.handle
# # #             tp = entity.dxftype()
# # #             pyqt_item = None
# # #             if tp == "CIRCLE":
# # #                 cx, cy, _ = entity.dxf.center
# # #                 r = entity.dxf.radius
# # #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# # #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# # #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
# # #             elif tp == "LINE":
# # #                 x1, y1, _ = entity.dxf.start
# # #                 x2, y2, _ = entity.dxf.end
# # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# # #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# # #             if pyqt_item:
# # #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# # #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
# # #                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# # #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# # #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# # #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# # #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# # #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
# # #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# # #                 self.scene.addItem(pyqt_item)
# # #                 self.overlay_items[hndl] = pyqt_item

# # #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# # #     def create_zone_from_selection(self, axis):
# # #         if not self.selected_handles or not self.original_geometries: return
# # #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# # #         if not active_entities or len(active_entities) < 2: 
# # #             self.clear_selection()
# # #             return
# # #         if axis == 'X':
# # #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# # #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# # #         else:
# # #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# # #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
# # #         if max_val > min_val and (max_val - min_val) > 2.0:
# # #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# # #         self.clear_selection()

# # #     def process_manual_rubber_band(self, rect):
# # #         self.selected_handles.clear()
# # #         path = QPainterPath()
# # #         path.addRect(rect)
# # #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# # #         for item in matched_items:
# # #             hndl = item.data(Qt.ItemDataRole.UserRole)
# # #             if hndl: self.selected_handles.add(hndl)
# # #         self.sync_list_from_handles()
# # #         self.update_viewer()

# # #     def on_scene_item_clicked(self, handle):
# # #         self.selected_handles = {handle}
# # #         self.sync_list_from_handles()
# # #         self.update_viewer()

# # #     def sync_list_from_handles(self):
# # #         self.entity_list.blockSignals(True)
# # #         self.entity_list.clearSelection()
# # #         for i in range(self.entity_list.count()):
# # #             item = self.entity_list.item(i)
# # #             if item.data(Qt.ItemDataRole.UserRole) in self.selected_handles: item.setSelected(True)
# # #         self.entity_list.blockSignals(False)

# # #     def on_list_selection_changed(self):
# # #         self.selected_handles.clear()
# # #         for item in self.entity_list.selectedItems():
# # #             self.selected_handles.add(item.data(Qt.ItemDataRole.UserRole))
# # #         self.update_viewer()

# # #     def clear_selection(self):
# # #         self.selected_handles.clear()
# # #         self.update_viewer()
# # #         self.entity_list.blockSignals(True)
# # #         self.entity_list.clearSelection()
# # #         self.entity_list.blockSignals(False)

# # #     def on_theme_changed(self, theme_name):
# # #         self.current_theme = theme_name
# # #         self.set_interface_theme(theme_name)
# # #         self.update_viewer()

# # #     def load_entities_into_list(self):
# # #         self.entity_list.blockSignals(True)
# # #         self.entity_list.clear()
# # #         seen = set()
# # #         for entity in self.doc.modelspace():
# # #             tp = entity.dxftype()
# # #             hndl = entity.dxf.handle
# # #             if tp == "CIRCLE":
# # #                 cx, cy, _ = entity.dxf.center
# # #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# # #                 seen.add((round(cx, 2), round(cy, 2)))
# # #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# # #             elif tp == "LINE":
# # #                 x1, y1, _ = entity.dxf.start
# # #                 x2, y2, _ = entity.dxf.end
# # #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# # #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# # #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм"
# # #             else: continue
# # #             item = QListWidgetItem(text)
# # #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# # #             self.entity_list.addItem(item)
# # #         self.entity_list.blockSignals(False)

# # import os
# # import sys
# # import math
# # import copy

# # import ezdxf
# # import ezdxf.bbox as dxf_bbox
# # from ezdxf.math import Matrix44
# # from ezdxf.addons.importer import Importer  # Надійний інструмент злиття креслень

# # from PySide6.QtWidgets import (
# #     QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
# #     QListWidget, QListWidgetItem, QPushButton, QSlider, 
# #     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
# #     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit
# # )
# # from PySide6.QtCore import Qt
# # from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath, QPainter

# # from graphics_items import SelectableCircle, SelectableLine
# # from graphics_view import AdvancedGraphicsView
# # from history_manager import HistoryManager


# # # ---------------------------------------------------------------------------
# # # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ КООРДИНАТ)
# # # ---------------------------------------------------------------------------
# # def patch_ezdxf_entities():
# #     from ezdxf.entities import Line, Circle
# #     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# #     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# #     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# #     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# #     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# #     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# #     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# #     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# # patch_ezdxf_entities()
# # # ---------------------------------------------------------------------------


# # class MiniCAD(QMainWindow):
# #     def __init__(self):
# #         super().__init__()

# #         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор")
# #         self.setGeometry(100, 100, 1600, 950)

# #         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
# #         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
# #         self.current_theme = "Темна"

# #         self.selected_handles = set()
# #         self.overlay_items = {}
# #         self.original_geometries = {}
# #         self.is_loading_history = False

# #         self.left_fixed_handles = set()
# #         self.right_fixed_handles = set()
# #         self.bottom_fixed_handles = set()
# #         self.top_fixed_handles = set()
        
# #         self.stretch_zones = []
# #         self.active_zone_index = None

# #         self.zones_undo_stack = []
# #         self.zones_redo_stack = []

# #         if os.path.exists(self.dxf_path):
# #             self.doc = ezdxf.readfile(self.dxf_path)
# #         else:
# #             self.doc = ezdxf.new()
# #             self.doc.saveas(self.dxf_path)

# #         self.history = HistoryManager(self.dxf_path)
# #         self.history.save_state()
# #         self.save_zones_history_state()

# #         self.init_ui()
# #         self.set_interface_theme(self.current_theme)
# #         self.save_original_geometries()
# #         self.update_viewer()
# #         self.load_entities_into_list()
# #         self.scan_project_folder_for_dxf()

# #     def init_ui(self):
# #         main_widget = QWidget()
# #         self.central_layout = QHBoxLayout(main_widget)
# #         self.setCentralWidget(main_widget)

# #         # --- ЛІВИЙ ПРОВІДНИК ПАПКИ ПРОЕКТУ ---
# #         folder_explorer_widget = QWidget()
# #         folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
# #         folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
# #         lbl_explorer_title = QLabel("📁 <b>Провідник DXF (утримуйте Ctrl):</b>")
# #         lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
# #         folder_explorer_layout.addWidget(lbl_explorer_title)
        
# #         self.file_explorer_list = QListWidget()
# #         self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# #         self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
# #         folder_explorer_layout.addWidget(self.file_explorer_list)
# #         self.central_layout.addWidget(folder_explorer_widget, stretch=1)

# #         # --- ЦЕНТРАЛЬНИЙ ГРАФІЧНИЙ БЛОК ---
# #         self.scene = QGraphicsScene()
# #         self.view = AdvancedGraphicsView(self.scene, self)
# #         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
# #         self.central_layout.addWidget(self.view, stretch=4)

# #         # --- ПРАВА ПАНЕЛЬ КЕРУВАННЯ ---
# #         control_panel = QWidget()
# #         control_layout = QVBoxLayout(control_panel)
# #         control_layout.setContentsMargins(5, 0, 0, 0)
# #         self.central_layout.addWidget(control_panel, stretch=2)

# #         # --- БЛОК 1: АДАНТАЦІЯ ПІД РОЗМІРИ ЗАМОВЛЕННЯ ---
# #         auto_scale_group = QGroupBox("🚀 Адаптація під розміри замовлення (з припусками)")
# #         auto_scale_box = QVBoxLayout()

# #         width_layout = QHBoxLayout()
# #         width_layout.addWidget(QLabel("<b>Ширина (X):</b> Поточна:"))
# #         self.input_current_width = QLineEdit()
# #         self.input_current_width.setPlaceholderText("1000")
# #         width_layout.addWidget(self.input_current_width)
# #         width_layout.addWidget(QLabel("➡️ Нова:"))
# #         self.input_target_width = QLineEdit()
# #         self.input_target_width.setPlaceholderText("1010")
# #         width_layout.addWidget(self.input_target_width)
# #         auto_scale_box.addLayout(width_layout)

# #         height_layout = QHBoxLayout()
# #         height_layout.addWidget(QLabel("<b>Висота (Y):</b> Поточна:"))
# #         self.input_current_height = QLineEdit()
# #         self.input_current_height.setPlaceholderText("2040")
# #         height_layout.addWidget(self.input_current_height)
# #         height_layout.addWidget(QLabel("➡️ Нова:"))
# #         self.input_target_height = QLineEdit()
# #         self.input_target_height.setPlaceholderText("2050")
# #         height_layout.addWidget(self.input_target_height)
# #         auto_scale_box.addLayout(height_layout)

# #         self.lbl_status_calc = QLabel("Введіть розміри та натисніть кнопку нижче")
# #         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
# #         auto_scale_box.addWidget(self.lbl_status_calc)

# #         self.btn_apply_auto_scale = QPushButton("⚡ Автоматично розрахувати дельту та змінити")
# #         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
# #         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
# #         auto_scale_box.addWidget(self.btn_apply_auto_scale)

# #         auto_scale_group.setLayout(auto_scale_box)
# #         control_layout.addWidget(auto_scale_group)

# #         # --- БЛОК 2: ОРІЄНТАЦІЯ ТА ОБЕРТАННЯ ДЕТАЛЕЙ ---
# #         transform_group = QGroupBox("🔄 Орієнтація та обертання виділених деталей")
# #         transform_box = QVBoxLayout()
        
# #         rot_layout = QHBoxLayout()
# #         self.btn_rot_90 = QPushButton("↪️ Поворот 90°")
# #         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
# #         self.btn_rot_180 = QPushButton("🔁 Поворот 180°")
# #         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
# #         rot_layout.addWidget(self.btn_rot_90)
# #         rot_layout.addWidget(self.btn_rot_180)
# #         transform_box.addLayout(rot_layout)

# #         mirror_layout = QHBoxLayout()
# #         self.btn_mirror_h = QPushButton("↔️ Віддзеркалити по Х")
# #         self.btn_mirror_v = QPushButton("↕️ Віддзеркалити по Y")
# #         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
# #         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
# #         mirror_layout.addWidget(self.btn_mirror_h)
# #         mirror_layout.addWidget(self.btn_mirror_v)
# #         transform_box.addLayout(mirror_layout)

# #         transform_group.setLayout(transform_box)
# #         control_layout.addWidget(transform_group)

# #         # --- БЛОК 3: ИНЖЕНЕРНЕ ПРИТИСКАННЯ (БАЗУВАННЯ) ---
# #         align_group = QGroupBox("📍 Притулити (базувати) виділене до краю дверей")
# #         align_box = QVBoxLayout()

# #         align_x_layout = QHBoxLayout()
# #         self.btn_align_left = QPushButton("🟢 До лівого краю (Х)")
# #         self.btn_align_right = QPushButton("🔴 До правого краю (Х)")
# #         self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
# #         self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
# #         align_x_layout.addWidget(self.btn_align_left)
# #         align_x_layout.addWidget(self.btn_align_right)
# #         align_box.addLayout(align_x_layout)

# #         align_y_layout = QHBoxLayout()
# #         self.btn_align_bottom = QPushButton("🔵 До нижнього краю (Y)")
# #         self.btn_align_top = QPushButton("🟡 До верхнього краю (Y)")
# #         self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
# #         self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
# #         align_y_layout.addWidget(self.btn_align_bottom)
# #         align_y_layout.addWidget(self.btn_align_top)
# #         align_box.addLayout(align_y_layout)

# #         align_group.setLayout(align_box)
# #         control_layout.addWidget(align_group)

# #         # --- БЛОК СТИЛЮ ТА ТЕМИ ---
# #         theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
# #         theme_box = QHBoxLayout()
# #         theme_box.addWidget(QLabel("Тема:"))
# #         self.theme_combo = QComboBox()
# #         self.theme_combo.addItems(["Темна", "Світла"])
# #         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
# #         theme_box.addWidget(self.theme_combo)
# #         theme_group.setLayout(theme_box)
# #         control_layout.addWidget(theme_group)

# #         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
# #         history_group = QGroupBox("Історія конструкторських змін")
# #         history_box = QHBoxLayout()
# #         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
# #         self.btn_undo.clicked.connect(self.undo)
# #         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
# #         self.btn_redo.clicked.connect(self.redo)
# #         history_box.addWidget(self.btn_undo)
# #         history_box.addWidget(self.btn_redo)
# #         history_group.setLayout(history_box)
# #         control_layout.addWidget(history_group)
# #         self.update_history_buttons_state()

# #         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
# #         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
# #         fix_box = QVBoxLayout()
# #         h_fix_layout = QHBoxLayout()
# #         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
# #         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
# #         self.btn_set_left_fix.setObjectName("leftFixBtn")
# #         self.btn_set_right_fix.setObjectName("rightFixBtn")
# #         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
# #         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
# #         h_fix_layout.addWidget(self.btn_set_left_fix)
# #         h_fix_layout.addWidget(self.btn_set_right_fix)
# #         fix_box.addLayout(h_fix_layout)

# #         v_fix_layout = QHBoxLayout()
# #         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
# #         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
# #         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
# #         self.btn_set_top_fix.setObjectName("topFixBtn")
# #         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
# #         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
# #         v_fix_layout.addWidget(self.btn_set_bottom_fix)
# #         v_fix_layout.addWidget(self.btn_set_top_fix)
# #         fix_box.addLayout(v_fix_layout)
# #         fix_group.setLayout(fix_box)
# #         control_layout.addWidget(fix_group)

# #         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
# #         zone_group = QGroupBox("2. Створення зон деформації простору")
# #         zone_box = QVBoxLayout()
# #         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
# #         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
# #         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
# #         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
# #         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
# #         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
# #         zone_box.addWidget(self.btn_add_zone_x)
# #         zone_box.addWidget(self.btn_add_zone_y)
# #         zone_box.addWidget(self.btn_clear_zones)
# #         zone_group.setLayout(zone_box)
# #         control_layout.addWidget(zone_group)

# #         control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
# #         self.zone_list_widget = QListWidget()
# #         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
# #         control_layout.addWidget(self.zone_list_widget)

# #         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
# #         self.entity_list = QListWidget()
# #         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
# #         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
# #         control_layout.addWidget(self.entity_list)

# #         self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
# #         control_layout.addWidget(self.slider_label)
# #         self.slider = QSlider(Qt.Orientation.Horizontal)
# #         self.slider.setRange(0, 600)
# #         self.slider.setValue(0)
# #         self.slider.setEnabled(False)
# #         self.slider.valueChanged.connect(self.on_slider_value_changed)
# #         self.slider.sliderReleased.connect(self.on_slider_released)
# #         control_layout.addWidget(self.slider)

# #         control_layout.addStretch()

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
        
# #         base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
# #         self.dxf_path = os.path.join(self.project_dir, base_file_name)
# #         self.doc = ezdxf.readfile(self.dxf_path)
        
# #         self.selected_handles.clear()
# #         self.reset_all_parametric_zones()

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
# #                     except Exception as e:
# #                         print(f"Помилка злиття файлу {addon_file_name}: {e}")

# #         self.apply_ezdxf_patch()

# #         self.history = HistoryManager(self.dxf_path)
# #         self.history.save_state()
# #         self.zones_undo_stack.clear()
# #         self.zones_redo_stack.clear()
# #         self.save_zones_history_state()
        
# #         self.save_original_geometries()
# #         self.update_viewer()
# #         self.load_entities_into_list()
# #         self.update_history_buttons_state()
# #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Відображено проектів: {len(selected_items)} шт.</font>")

# #     def save_original_geometries(self):
# #         self.original_geometries.clear()
# #         for entity in self.doc.modelspace():
# #             hndl = entity.dxf.handle
# #             tp = entity.dxftype()
# #             if tp == "CIRCLE":
# #                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
# #             elif tp == "LINE":
# #                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}


# #     def update_viewer(self):
# #         self.scene = QGraphicsScene()
# #         self.view.setScene(self.scene)
# #         self.overlay_items.clear()

# #         if self.current_theme == "Темна":
# #             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
# #             base_line_color = QColor(220, 220, 220)
# #         else:
# #             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
# #             base_line_color = QColor(80, 80, 80)

# #         axis_len = 150.0
# #         self.scene.addLine(-50, 0, axis_len, 0, QPen(QColor(33, 150, 243), 2.5))
# #         self.scene.addLine(axis_len, 0, axis_len - 10, -4, QPen(QColor(33, 150, 243), 2.5))
# #         self.scene.addLine(axis_len, 0, axis_len - 10, 4, QPen(QColor(33, 150, 243), 2.5))
# #         self.scene.addLine(0, 50, 0, -axis_len, QPen(QColor(76, 175, 80), 2.5))
# #         self.scene.addLine(0, -axis_len, -4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))
# #         self.scene.addLine(0, -axis_len, 4, -axis_len + 10, QPen(QColor(76, 175, 80), 2.5))

# #         seen_circles, seen_lines = set(), set()
# #         try:
# #             bounds = dxf_bbox.extents(self.doc.modelspace())
# #             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
# #             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
# #         except Exception:
# #             abs_min_x, abs_max_x = -100.0, 1000.0
# #             abs_min_y, abs_max_y = -100.0, 2000.0

# #         for idx, zone in enumerate(self.stretch_zones):
# #             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
# #             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) + zone['stretch_val']
# #             if zone['axis'] == 'X':
# #                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
# #             else:
# #                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

# #             if idx == self.active_zone_index:
# #                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
# #                 rect_item.setBrush(QBrush(color))
# #                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
# #             else:
# #                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
# #                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
# #             self.scene.addItem(rect_item)

# #         for entity in self.doc.modelspace():
# #             hndl = entity.dxf.handle
# #             tp = entity.dxftype()
# #             pyqt_item = None
# #             if tp == "CIRCLE":
# #                 cx, cy, _ = entity.dxf.center
# #                 r = entity.dxf.radius
# #                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
# #                 seen_circles.add((round(cx, 2), round(cy, 2)))
# #                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
# #             elif tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
# #                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# #                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

# #             if pyqt_item:
# #                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
# #                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
# #                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
# #                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
# #                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
# #                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
# #                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
# #                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
# #                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
# #                 self.scene.addItem(pyqt_item)
# #                 self.overlay_items[hndl] = pyqt_item

# #         self.view.setSceneRect(self.scene.itemsBoundingRect())

# #     def process_manual_input_dimension_scale(self):
# #         if not self.stretch_zones:
# #             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
# #             return

# #         cur_w = self.input_current_width.text().strip()
# #         new_w = self.input_target_width.text().strip()
# #         cur_h = self.input_current_height.text().strip()
# #         new_h = self.input_target_height.text().strip()

# #         delta_x = float(new_w) - float(cur_w) if (cur_w and new_w) else 0.0
# #         delta_y = float(new_h) - float(cur_h) if (cur_h and new_h) else 0.0

# #         if delta_x == 0.0 and delta_y == 0.0:
# #             self.lbl_status_calc.setText("<font color='yellow'>Дельта 0 мм. Змініть габарити.</font>")
# #             return

# #         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
# #         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

# #         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
# #         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

# #         for zone in self.stretch_zones:
# #             if zone['axis'] == 'X': zone['stretch_val'] = share_delta_x
# #             elif zone['axis'] == 'Y': zone['stretch_val'] = share_delta_y

# #         for hndl, orig in self.original_geometries.items():
# #             if hndl not in self.doc.entitydb: continue
# #             entity = self.doc.entitydb[hndl]
# #             if orig["type"] == "CIRCLE":
# #                 cx, cy, cz = orig["center"]
# #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# #             elif orig["type"] == "LINE":
# #                 sx, sy, sz = orig["start"]
# #                 ex, ey, ez = orig["end"]
# #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

# #         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔX={delta_x:+.1f}мм | ΔY={delta_y:+.1f}мм</font>")
# #         self.doc.saveas(self.dxf_path)
        
# #         for zone in self.stretch_zones:
# #             stretch_amount = zone['stretch_val']
# #             if stretch_amount == 0: continue
# #             active_axis = zone['axis']
# #             active_max = zone['max']
# #             zone['max'] += stretch_amount
# #             for sub_z in self.stretch_zones:
# #                 if sub_z == zone or sub_z['axis'] != active_axis: continue
# #                 if sub_z['min'] >= active_max:
# #                     sub_z['min'] += stretch_amount
# #                     sub_z['max'] += stretch_amount

# #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# #         self.history.save_state()
# #         self.history.clear_redo()
# #         self.save_zones_history_state()
# #         self.zones_redo_stack.clear()
# #         self.update_history_buttons_state()
# #         self.save_original_geometries()

# #         self.input_current_width.clear()
# #         self.input_target_width.clear()
# #         self.input_current_height.clear()
# #         self.input_target_height.clear()

# #         self.load_zones_into_list()
# #         self.load_entities_into_list()
# #         self.update_viewer()

# #     def transform_selected_entities(self, mode):
# #         if not self.selected_handles: return
# #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# #         if not selected_entities: return

# #         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
# #         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

# #         for entity in selected_entities:
# #             if mode == "ROT90":
# #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(90)), Matrix44.translate(cx, cy, 0))
# #             elif mode == "ROT180":
# #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(180)), Matrix44.translate(cx, cy, 0))
# #             elif mode == "MIRROR_H":
# #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
# #             elif mode == "MIRROR_V":
# #                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
# #             else: continue
# #             entity.transform(m)

# #         self.doc.saveas(self.dxf_path)
# #         self.history.save_state()
# #         self.save_zones_history_state()
# #         self.save_original_geometries()
# #         self.update_viewer()
# #         self.load_entities_into_list()


# #     def process_manual_rubber_band(self, rect):
# #         self.selected_handles.clear()
# #         path = QPainterPath()
# #         path.addRect(rect)
# #         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
# #         for item in matched_items:
# #             hndl = item.data(Qt.ItemDataRole.UserRole)
# #             if hndl: self.selected_handles.add(hndl)
# #         self.sync_list_from_handles()
# #         self.update_viewer()

# #     def align_selected_to_edge(self, edge):
# #         if not self.selected_handles: return
# #         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# #         if not selected_entities: return

# #         try:
# #             bounds = dxf_bbox.extents(self.doc.modelspace())
# #             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
# #             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
# #         except Exception:
# #             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

# #         margin = 5.0
# #         shift_x, shift_y = 0.0, 0.0

# #         sel_min_x = min(e.left_x for e in selected_entities)
# #         sel_max_x = max(e.right_x for e in selected_entities)
# #         sel_min_y = min(e.bottom_y for e in selected_entities)
# #         sel_max_y = max(e.top_y for e in selected_entities)

# #         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
# #         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
# #         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
# #         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

# #         for entity in selected_entities:
# #             entity.translate(shift_x, shift_y, 0)

# #         self.doc.saveas(self.dxf_path)
# #         self.history.save_state()
# #         self.save_zones_history_state()
# #         self.save_original_geometries()
# #         self.update_viewer()
# #         self.load_entities_into_list()

# #     def assign_to_left_fix(self):
# #         self.left_fixed_handles.update(self.selected_handles)
# #         self.right_fixed_handles.difference_update(self.selected_handles)
# #         self.auto_detect_between_zone('X')
# #         self.update_viewer()
# #         self.load_entities_into_list()

# #     def assign_to_right_fix(self):
# #         self.right_fixed_handles.update(self.selected_handles)
# #         self.left_fixed_handles.difference_update(self.selected_handles)
# #         self.auto_detect_between_zone('X')
# #         self.update_viewer()
# #         self.load_entities_into_list()

# #     def assign_to_bottom_fix(self):
# #         self.bottom_fixed_handles.update(self.selected_handles)
# #         self.top_fixed_handles.difference_update(self.selected_handles)
# #         self.auto_detect_between_zone('Y')
# #         self.update_viewer()
# #         self.load_entities_into_list()

# #     def assign_to_top_fix(self):
# #         self.top_fixed_handles.update(self.selected_handles)
# #         self.bottom_fixed_handles.difference_update(self.selected_handles)
# #         self.auto_detect_between_zone('Y')
# #         self.update_viewer()
# #         self.load_entities_into_list()

# #     def save_zones_history_state(self):
# #         self.zones_undo_stack.append(copy.deepcopy(self.stretch_zones))
# #         if len(self.zones_undo_stack) > 30: self.zones_undo_stack.pop(0)

# #     def undo(self):
# #         if self.history.undo() and len(self.zones_undo_stack) > 1:
# #             current_zones = self.zones_undo_stack.pop()
# #             self.zones_redo_stack.append(current_zones)
# #             self.stretch_zones = copy.deepcopy(self.zones_undo_stack[-1])
# #             self.reload_after_history_change()

# #     def redo(self):
# #         if self.history.redo() and self.zones_redo_stack:
# #             next_zones = self.zones_redo_stack.pop()
# #             self.zones_undo_stack.append(next_zones)
# #             self.stretch_zones = copy.deepcopy(next_zones)
# #             self.reload_after_history_change()

# #     def update_history_buttons_state(self):
# #         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
# #         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

# #     def reload_after_history_change(self):
# #         self.is_loading_history = True
# #         self.doc = ezdxf.readfile(self.dxf_path)
# #         self.save_original_geometries()
# #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0
# #         self.slider.blockSignals(True)
# #         self.slider.setValue(0)
# #         self.slider.blockSignals(False)
# #         self.update_viewer()
# #         self.load_zones_into_list()
# #         self.load_entities_into_list()
# #         self.update_history_buttons_state()
# #         self.slider_label.setText("Оберіть зону деформації зі списку")
# #         self.is_loading_history = False

# #     def reset_all_parametric_zones(self):
# #         self.left_fixed_handles.clear()
# #         self.right_fixed_handles.clear()
# #         self.bottom_fixed_handles.clear()
# #         self.top_fixed_handles.clear()
# #         self.stretch_zones.clear()
# #         self.active_zone_index = None
# #         self.slider.setEnabled(False)
# #         self.slider_label.setText("Оберіть зону деформації зі списку")
# #         self.update_viewer()
# #         self.load_zones_into_list()
# #         self.load_entities_into_list()

# #     def on_theme_changed(self, theme_name):
# #         self.current_theme = theme_name
# #         self.set_interface_theme(theme_name)
# #         self.update_viewer()

# #     def set_interface_theme(self, theme_name):
# #         if theme_name == "Темна":
# #             self.setStyleSheet("""
# #                 QMainWindow { background-color: #252526; }
# #                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
# #                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
# #                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
# #                 QPushButton:hover { background-color: #505050; }
# #                 QLineEdit { background-color: #1e1e1e; border: 1px solid #555555; color: white; padding: 4px; border-radius: 3px; }
# #                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
# #                 QListWidget::item:selected { background-color: #04396c; color: white; }
# #                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
# #                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
# #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# #                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
# #                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
# #                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
# #                 #topFixBtn { background-color: #524705; color: #fffde7; }
# #             """)
# #         else:
# #             self.setStyleSheet("""
# #                 QMainWindow { background-color: #f3f3f3; }
# #                 QWidget { color: #000000; font-family: 'Segoe UI'; }
# #                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
# #                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
# #                 QPushButton:hover { background-color: #d0d0d0; }
# #                 QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: black; padding: 4px; border-radius: 3px; }
# #                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
# #                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
# #                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
# #                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
# #                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
# #                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
# #                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
# #                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
# #                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
# #             """)

# #     def auto_detect_between_zone(self, axis):
# #         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
# #             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
# #             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
# #             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
# #                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
# #         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
# #             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
# #             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
# #             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
# #                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')

# #     def add_or_update_zone_bounds(self, min_v, max_v, axis):
# #         for zone in self.stretch_zones:
# #             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0: return
# #         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
# #         self.stretch_zones.append(new_zone)
# #         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
# #         self.load_zones_into_list()
# #         for idx, zone in enumerate(self.stretch_zones):
# #             if zone['axis'] == axis and zone['min'] == min_v:
# #                 self.zone_list_widget.setCurrentRow(idx)
# #                 break

# #     def load_zones_into_list(self):
# #         self.zone_list_widget.blockSignals(True)
# #         self.zone_list_widget.clear()
# #         for idx, zone in enumerate(self.stretch_zones):
# #             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
# #             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.0f} -> {zone['max']:.0f}]"
# #             item = QListWidgetItem(text)
# #             item.setData(Qt.ItemDataRole.UserRole, idx)
# #             self.zone_list_widget.addItem(item)
# #         self.zone_list_widget.blockSignals(False)

# #     def on_zone_selection_changed(self):
# #         selected = self.zone_list_widget.selectedItems()
# #         if not selected:
# #             self.active_zone_index = None
# #             self.slider.setEnabled(False)
# #             return
# #         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
# #         zone = self.stretch_zones[self.active_zone_index]
# #         self.slider.blockSignals(True)
# #         self.slider.setEnabled(True)
# #         self.slider.setValue(int(zone['stretch_val']))
# #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
# #         self.slider.blockSignals(False)
# #         self.update_viewer()

# #     def on_slider_value_changed(self, value):
# #         if self.active_zone_index is None or self.is_loading_history: return
# #         self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
# #         zone = self.stretch_zones[self.active_zone_index]
# #         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

# #         for hndl, orig in self.original_geometries.items():
# #             if hndl not in self.doc.entitydb: continue
# #             entity = self.doc.entitydb[hndl]
# #             if orig["type"] == "CIRCLE":
# #                 cx, cy, cz = orig["center"]
# #                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
# #             elif orig["type"] == "LINE":
# #                 sx, sy, sz = orig["start"]
# #                 ex, ey, ez = orig["end"]
# #                 # ВИПРАВЛЕНО: Замінено cy на sy для коректного обрахунку каскаду Y ліній
# #                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
# #                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)
# #         self.update_viewer()

# #     def calculate_cascade_shift(self, orig_val, axis, hndl):
# #         if axis == 'X' and hndl:
# #             if hndl in self.left_fixed_handles: return orig_val
# #             if hndl in self.right_fixed_handles:
# #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
# #         elif axis == 'Y' and hndl:
# #             if hndl in self.bottom_fixed_handles: return orig_val
# #             if hndl in self.top_fixed_handles:
# #                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

# #         shifted_val = orig_val
# #         for zone in self.stretch_zones:
# #             if zone['axis'] != axis: continue
# #             z_min = zone['min']
# #             z_max = zone['max']
# #             val = zone['stretch_val']

# #             if orig_val >= z_max: shifted_val += val
# #             elif z_min < orig_val < z_max:
# #                 width = z_max - z_min
# #                 if width > 0: shifted_val += val * ((orig_val - z_min) / width)
                    
# #         return shifted_val

# #     def on_slider_released(self):
# #         self.doc.saveas(self.dxf_path)
# #         active_zone = self.stretch_zones[self.active_zone_index] if self.active_zone_index is not None else None
# #         if active_zone:
# #             stretch_amount = active_zone['stretch_val']
# #             active_axis = active_zone['axis']
# #             active_max = active_zone['max']
# #             active_zone['max'] += stretch_amount
# #             for idx, zone in enumerate(self.stretch_zones):
# #                 if idx == self.active_zone_index or zone['axis'] != active_axis: continue
# #                 if zone['min'] >= active_max:
# #                     zone['min'] += stretch_amount
# #                     zone['max'] += stretch_amount

# #         for zone in self.stretch_zones: zone['stretch_val'] = 0.0

# #         self.history.save_state()
# #         self.history.clear_redo()
# #         self.save_zones_history_state()
# #         self.zones_redo_stack.clear()
# #         self.update_history_buttons_state()
# #         self.save_original_geometries()

# #         self.slider.blockSignals(True)
# #         self.slider.setValue(0)
# #         self.slider.blockSignals(False)

# #         self.load_zones_into_list()
# #         self.load_entities_into_list()
# #         self.update_viewer()

# #     def on_scene_item_clicked(self, handle):
# #         self.selected_handles = {handle}
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

# #     def create_zone_from_selection(self, axis):
# #         if not self.selected_handles or not self.original_geometries: return
# #         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
# #         if not active_entities or len(active_entities) < 2: 
# #             self.clear_selection()
# #             return
# #         if axis == 'X':
# #             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
# #             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
# #         else:
# #             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
# #             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
# #         if max_val > min_val and (max_val - min_val) > 2.0:
# #             self.add_or_update_zone_bounds(min_val, max_val, axis)
# #         self.clear_selection()

    
# #     def apply_ezdxf_patch(self):
# #         from ezdxf.entities import Line, Circle
# #         Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
# #         Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
# #         Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
# #         Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

# #         Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
# #         Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
# #         Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
# #         Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# #     def load_entities_into_list(self):
# #         self.entity_list.blockSignals(True)
# #         self.entity_list.clear()
# #         seen = set()
# #         for entity in self.doc.modelspace():
# #             tp = entity.dxftype()
# #             hndl = entity.dxf.handle
# #             if tp == "CIRCLE":
# #                 cx, cy, _ = entity.dxf.center
# #                 if (round(cx, 2), round(cy, 2)) in seen: continue
# #                 seen.add((round(cx, 2), round(cy, 2)))
# #                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.1f}, Y:{cy:.1f}"
# #             elif tp == "LINE":
# #                 x1, y1, _ = entity.dxf.start
# #                 x2, y2, _ = entity.dxf.end
# #                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
# #                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
# #                 text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.1f} мм"
# #             else: continue
# #             item = QListWidgetItem(text)
# #             item.setData(Qt.ItemDataRole.UserRole, hndl)
# #             self.entity_list.addItem(item)
# #         self.entity_list.blockSignals(False)


# import os
# import sys
# import math
# import copy

# import ezdxf
# import ezdxf.bbox as dxf_bbox
# from ezdxf.math import Matrix44
# from ezdxf.addons.importer import Importer 

# from PySide6.QtWidgets import (
#     QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
#     QListWidget, QListWidgetItem, QPushButton, QSlider, 
#     QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
#     QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView
# )
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath, QPainter

# from graphics_items import SelectableCircle, SelectableLine
# from graphics_view import AdvancedGraphicsView
# from history_manager import HistoryManager
# from PySide6.QtGui import QGuiApplication 
# from PySide6.QtWidgets import QFileDialog


# from PySide6.QtGui import QGuiApplication, QPainterPath
# from PySide6.QtCore import Qt



# # ---------------------------------------------------------------------------
# # 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ КООРДИНАТ)
# # ---------------------------------------------------------------------------
# def patch_ezdxf_entities():
#     from ezdxf.entities import Line, Circle
#     Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
#     Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
#     Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
#     Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

#     Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
#     Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
#     Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
#     Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

# patch_ezdxf_entities()
# # ---------------------------------------------------------------------------


# class MiniCAD(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор")
#         self.setGeometry(100, 100, 1600, 950)

#         self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
#         self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
#         self.current_theme = "Темна"

#         self.selected_handles = set()
#         self.overlay_items = {}
#         self.original_geometries = {}
#         self.is_loading_history = False

#         # Списки для жорстких зон фіксації фурнітури
#         self.left_fixed_handles = set()
#         self.right_fixed_handles = set()
#         self.bottom_fixed_handles = set()
#         self.top_fixed_handles = set()
        
#         # Списки параметричних зон простору
#         self.stretch_zones = []
#         self.active_zone_index = None

#         # Універсальні інженерні стеки для синхронного відкоту абсолютно всього
#         self.zones_undo_stack = []
#         self.zones_redo_stack = []

#         if os.path.exists(self.dxf_path):
#             self.doc = ezdxf.readfile(self.dxf_path)
#         else:
#             self.doc = ezdxf.new()
#             self.doc.saveas(self.dxf_path)

#         self.history = HistoryManager(self.dxf_path)
        
#         # Фіксуємо перший початковий стан програми
#         self.history.save_state()
#         self.save_zones_history_state()

#         self.init_ui()
#         self.set_interface_theme(self.current_theme)
#         self.save_original_geometries()
#         self.update_viewer()
#         self.load_entities_into_list()
#         self.scan_project_folder_for_dxf()

#     def init_ui(self):
#         main_widget = QWidget()
#         self.central_layout = QHBoxLayout(main_widget)
#         self.setCentralWidget(main_widget)

#         # --- ЛІВИЙ ПРОВІДНИК ПАПКИ ПРОЕКТУ ---
#         folder_explorer_widget = QWidget()
#         folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
#         folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
#         lbl_explorer_title = QLabel("📁 <b>Провідник DXF (утримуйте Ctrl):</b>")
#         lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
#         folder_explorer_layout.addWidget(lbl_explorer_title)
        
#         self.file_explorer_list = QListWidget()
#         self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#         self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
#         folder_explorer_layout.addWidget(self.file_explorer_list)
#         self.central_layout.addWidget(folder_explorer_widget, stretch=1)

#         # --- ЦЕНТРАЛЬНИЙ ГРАФІЧНИЙ БЛОК ---
#         self.scene = QGraphicsScene()
#         self.view = AdvancedGraphicsView(self.scene, self)
#         self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
#         self.central_layout.addWidget(self.view, stretch=4)

#         # У вашому init_ui або окремій функції конфігурації в'ювера:
#         self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) # Дозволяє виділяти рамкою
#         self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse) # Зум до точки курсора
#         self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
#         self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

#         # --- ПРАВА ПАНЕЛЬ КЕРУВАННЯ ---


#         self.scroll_area = QScrollArea()
#         self.scroll_area.setWidgetResizable(True) # Це критично для прокрутки!
#         self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
#         control_panel = QWidget()
#         control_layout = QVBoxLayout(control_panel)
#         control_layout.setContentsMargins(5, 5, 5, 5)
#         self.scroll_area.setWidget(control_panel)
#         self.central_layout.addWidget(self.scroll_area, stretch=2)

#         # --- БЛОК 1: АДАНТАЦІЯ ПІД РОЗМІРИ ЗАМОВЛЕННЯ ---
#         auto_scale_group = QGroupBox("🚀 Адаптація під розміри замовлення (з припусками)")
#         auto_scale_box = QVBoxLayout()

#         width_layout = QHBoxLayout()
#         width_layout.addWidget(QLabel("<b>Ширина (X):</b> Поточна:"))
#         self.input_current_width = QLineEdit()
#         self.input_current_width.setPlaceholderText("1000")
#         width_layout.addWidget(self.input_current_width)
#         width_layout.addWidget(QLabel("➡️ Нова:"))
#         self.input_target_width = QLineEdit()
#         self.input_target_width.setPlaceholderText("1010")
#         width_layout.addWidget(self.input_target_width)
#         auto_scale_box.addLayout(width_layout)

#         height_layout = QHBoxLayout()
#         height_layout.addWidget(QLabel("<b>Висота (Y):</b> Поточна:"))
#         self.input_current_height = QLineEdit()
#         self.input_current_height.setPlaceholderText("2040")
#         height_layout.addWidget(self.input_current_height)
#         height_layout.addWidget(QLabel("➡️ Нова:"))
#         self.input_target_height = QLineEdit()
#         self.input_target_height.setPlaceholderText("2050")
#         height_layout.addWidget(self.input_target_height)
#         auto_scale_box.addLayout(height_layout)

#         self.lbl_status_calc = QLabel("Введіть розміри та натисніть кнопку нижче")
#         self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
#         auto_scale_box.addWidget(self.lbl_status_calc)

#         self.btn_apply_auto_scale = QPushButton("⚡ Автоматично розрахувати дельту та змінити")
#         self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
#         self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
#         auto_scale_box.addWidget(self.btn_apply_auto_scale)

#         auto_scale_group.setLayout(auto_scale_box)
#         control_layout.addWidget(auto_scale_group)



#         # --- БЛОК 3: ИНЖЕНЕРНЕ ПРИТИСКАННЯ (БАЗУВАННЯ) ---
#         # align_group = QGroupBox("📍 Притулити (базувати) виділене до краю дверей")
#         # align_box = QVBoxLayout()

#         # align_x_layout = QHBoxLayout()
#         # self.btn_align_left = QPushButton("🟢 До лівого краю (Х)")
#         # self.btn_align_right = QPushButton("🔴 До правого краю (Х)")
#         # self.btn_align_left.clicked.connect(lambda: self.align_selected_to_edge("LEFT"))
#         # self.btn_align_right.clicked.connect(lambda: self.align_selected_to_edge("RIGHT"))
#         # align_x_layout.addWidget(self.btn_align_left)
#         # align_x_layout.addWidget(self.btn_align_right)
#         # align_box.addLayout(align_x_layout)

#         # align_y_layout = QHBoxLayout()
#         # self.btn_align_bottom = QPushButton("🔵 До нижнього краю (Y)")
#         # self.btn_align_top = QPushButton("🟡 До верхнього краю (Y)")
#         # self.btn_align_bottom.clicked.connect(lambda: self.align_selected_to_edge("BOTTOM"))
#         # self.btn_align_top.clicked.connect(lambda: self.align_selected_to_edge("TOP"))
#         # align_y_layout.addWidget(self.btn_align_bottom)
#         # align_y_layout.addWidget(self.btn_align_top)
#         # align_box.addLayout(align_y_layout)

#         # align_group.setLayout(align_box)
#         # control_layout.addWidget(align_group)

#         # --- БЛОК СТИЛЮ ТА ТЕМИ ---

    

#         btn_open = QPushButton("📂 Відкрити файл")
#         btn_open.clicked.connect(self.open_dxf_file)

#         control_layout.addWidget(btn_open)

        

#         # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
#         history_group = QGroupBox("Історія конструкторських змін")
#         history_box = QHBoxLayout()
#         self.btn_undo = QPushButton("⬅️ Назад (Undo)")
#         self.btn_undo.clicked.connect(self.undo)
#         self.btn_redo = QPushButton("Вперед (Redo) ➡️")
#         self.btn_redo.clicked.connect(self.redo)
#         history_box.addWidget(self.btn_undo)
#         history_box.addWidget(self.btn_redo)
#         history_group.setLayout(history_box)
#         control_layout.addWidget(history_group)
#         self.update_history_buttons_state()

#         # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
#         fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
#         fix_box = QVBoxLayout()
#         h_fix_layout = QHBoxLayout()
#         self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
#         self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
#         self.btn_set_left_fix.setObjectName("leftFixBtn")
#         self.btn_set_right_fix.setObjectName("rightFixBtn")
#         self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
#         self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
#         h_fix_layout.addWidget(self.btn_set_left_fix)
#         h_fix_layout.addWidget(self.btn_set_right_fix)
#         fix_box.addLayout(h_fix_layout)

#         v_fix_layout = QHBoxLayout()
#         self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
#         self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
#         self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
#         self.btn_set_top_fix.setObjectName("topFixBtn")
#         self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
#         self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
#         v_fix_layout.addWidget(self.btn_set_bottom_fix)
#         v_fix_layout.addWidget(self.btn_set_top_fix)
#         fix_box.addLayout(v_fix_layout)
#         fix_group.setLayout(fix_box)
#         control_layout.addWidget(fix_group)

#         control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
#         self.entity_list = QListWidget()
#         self.entity_list.setFixedHeight(150)
#         self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
#         self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
#         control_layout.addWidget(self.entity_list)

#         # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
#         zone_group = QGroupBox("2. Створення зон деформації простору")
#         zone_box = QVBoxLayout()
#         self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
#         self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
#         self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
#         self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
#         self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
#         self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
#         zone_box.addWidget(self.btn_add_zone_x)
#         zone_box.addWidget(self.btn_add_zone_y)
#         zone_box.addWidget(self.btn_clear_zones)
#         zone_group.setLayout(zone_box)
#         control_layout.addWidget(zone_group)



#         control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
#         self.zone_list_widget = QListWidget()
#         self.zone_list_widget.setFixedHeight(150)
#         self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
#         control_layout.addWidget(self.zone_list_widget)







#         self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
#         control_layout.addWidget(self.slider_label)
#         self.slider = QSlider(Qt.Orientation.Horizontal)
#         self.slider.setRange(0, 600)
#         self.slider.setValue(0)
#         self.slider.setEnabled(False)
#         self.slider.valueChanged.connect(self.on_slider_value_changed)
#         self.slider.sliderReleased.connect(self.on_slider_released)
#         control_layout.addWidget(self.slider)


#                 # --- БЛОК 2: ОРІЄНТАЦІЯ ТА ОБЕРТАННЯ ДЕТАЛЕЙ ---
#         transform_group = QGroupBox("🔄 Орієнтація та обертання виділених деталей")
#         transform_box = QVBoxLayout()
        
#         rot_layout = QHBoxLayout()
#         self.btn_rot_90 = QPushButton("↪️ Поворот 90°")
#         self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
#         self.btn_rot_180 = QPushButton("🔁 Поворот 180°")
#         self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
#         rot_layout.addWidget(self.btn_rot_90)
#         rot_layout.addWidget(self.btn_rot_180)
#         transform_box.addLayout(rot_layout)

#         mirror_layout = QHBoxLayout()
#         self.btn_mirror_h = QPushButton("↔️ Віддзеркалити по Х")
#         self.btn_mirror_v = QPushButton("↕️ Віддзеркалити по Y")
#         self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
#         self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
#         mirror_layout.addWidget(self.btn_mirror_h)
#         mirror_layout.addWidget(self.btn_mirror_v)
#         transform_box.addLayout(mirror_layout)

#         transform_group.setLayout(transform_box)
#         control_layout.addWidget(transform_group)


#         theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
#         theme_box = QHBoxLayout()
#         theme_box.addWidget(QLabel("Тема:"))
#         self.theme_combo = QComboBox()
#         self.theme_combo.addItems(["Темна", "Світла"])
#         self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
#         theme_box.addWidget(self.theme_combo)
#         theme_group.setLayout(theme_box)
#         control_layout.addWidget(theme_group)

#         control_layout.addStretch()

#     # ---------------------------
#     # УНІВЕРСАЛЬНИЙ СТЕК КОНТРОЛЮ ІСТОРІЇ (ОНОВЛЕНО)
#     # ---------------------------
#     def save_zones_history_state(self):
#         """Зберігає повний зліпок параметричного середовища в Undo-стек."""
#         state_snapshot = {
#             "stretch_zones": copy.deepcopy(self.stretch_zones),
#             "left_fixed": copy.deepcopy(self.left_fixed_handles),
#             "right_fixed": copy.deepcopy(self.right_fixed_handles),
#             "bottom_fixed": copy.deepcopy(self.bottom_fixed_handles),
#             "top_fixed": copy.deepcopy(self.top_fixed_handles)
#         }
#         self.zones_undo_stack.append(state_snapshot)
#         if len(self.zones_undo_stack) > 30:
#             self.zones_undo_stack.pop(0)


#     def open_dxf_file(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Відкрити DXF файл", "", "DXF Files (*.dxf)")
#         if file_path:
#             self.dxf_path = file_path
#             self.project_dir = os.path.dirname(file_path)
#             self.doc = ezdxf.readfile(file_path)
            
#             # Скидання стану
#             self.selected_handles.clear()
#             self.stretch_zones.clear()
#             self.active_zone_index = None
            
#             self.apply_ezdxf_patch()
#             self.save_original_geometries()
#             self.scan_project_folder_for_dxf() 
#             self.update_viewer()
#             self.load_entities_into_list()

#     def on_zone_selection_changed(self):
#         selected = self.zone_list_widget.selectedItems()
#         if not selected:
#             self.active_zone_index = None
#             self.slider.setEnabled(False)
#             return
#         self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
#         zone = self.stretch_zones[self.active_zone_index]
#         self.slider.blockSignals(True)
#         self.slider.setEnabled(True)
#         self.slider.setValue(int(zone['stretch_val']))
#         self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
#         self.slider.blockSignals(False)
#         self.update_viewer()


#     def push_to_history(self):
#         """Головна інженерна точка фіксації дій у стек історії."""
#         self.history.save_state()
#         self.history.clear_redo()
#         self.save_zones_history_state()
#         self.zones_redo_stack.clear()
#         self.update_history_buttons_state()

#     def undo(self):
#         """Повертає абсолютно всі інженерні параметри на крок назад."""
#         if self.history.undo() and len(self.zones_undo_stack) > 1:
#             current_snapshot = self.zones_undo_stack.pop()
#             self.zones_redo_stack.append(current_snapshot)
            
#             # Відновлюємо масиви з попереднього збереженого стану
#             previous_snapshot = self.zones_undo_stack[-1]
#             self.stretch_zones = copy.deepcopy(previous_snapshot["stretch_zones"])
#             self.left_fixed_handles = copy.deepcopy(previous_snapshot["left_fixed"])
#             self.right_fixed_handles = copy.deepcopy(previous_snapshot["right_fixed"])
#             self.bottom_fixed_handles = copy.deepcopy(previous_snapshot["bottom_fixed"])
#             self.top_fixed_handles = copy.deepcopy(previous_snapshot["top_fixed"])
            
#             self.reload_after_history_change()

#     def redo(self):
#         """Повертає абсолютно всі інженерні параметри на крок вперед."""
#         if self.history.redo() and self.zones_redo_stack:
#             next_snapshot = self.zones_redo_stack.pop()
#             self.zones_undo_stack.append(next_snapshot)
            
#             # Відновлюємо масиви наступного стану
#             self.stretch_zones = copy.deepcopy(next_snapshot["stretch_zones"])
#             self.left_fixed_handles = copy.deepcopy(next_snapshot["left_fixed"])
#             self.right_fixed_handles = copy.deepcopy(next_snapshot["right_fixed"])
#             self.bottom_fixed_handles = copy.deepcopy(next_snapshot["bottom_fixed"])
#             self.top_fixed_handles = copy.deepcopy(next_snapshot["top_fixed"])
            
#             self.reload_after_history_change()

#     def update_history_buttons_state(self):
#         self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
#         self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

#     def reload_after_history_change(self):
#         self.is_loading_history = True
#         self.doc = ezdxf.readfile(self.dxf_path)
#         self.save_original_geometries()
        
#         for zone in self.stretch_zones: 
#             zone['stretch_val'] = 0.0
            
#         self.slider.blockSignals(True)
#         self.slider.setValue(0)
#         self.slider.blockSignals(False)
        
#         self.update_viewer()
#         self.load_zones_into_list()
#         self.load_entities_into_list()
#         self.update_history_buttons_state()
#         self.slider_label.setText("Оберіть зону деформації зі списку")
#         self.is_loading_history = False

#     # ---------------------------
#     # ПРОВІДНИК DXF ФАЙЛІВ ПАПКИ
#     # ---------------------------
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
        
#         base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
#         self.dxf_path = os.path.join(self.project_dir, base_file_name)
#         self.doc = ezdxf.readfile(self.dxf_path)
        
#         self.selected_handles.clear()
        
#         # Повне скидання при виборі нової карти файлів
#         self.left_fixed_handles.clear()
#         self.right_fixed_handles.clear()
#         self.bottom_fixed_handles.clear()
#         self.top_fixed_handles.clear()
#         self.stretch_zones.clear()
#         self.active_zone_index = None

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
#                     except Exception as e:
#                         print(f"Помилка злиття файлу {addon_file_name}: {e}")

#         self.apply_ezdxf_patch()

#         self.history = HistoryManager(self.dxf_path)
#         self.history.save_state()
#         self.zones_undo_stack.clear()
#         self.zones_redo_stack.clear()
#         self.save_zones_history_state()
        
#         self.save_original_geometries()
#         self.update_viewer()
#         self.load_entities_into_list()
#         self.update_history_buttons_state()
#         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Відображено проектів: {len(selected_items)} шт.</font>")

#     def save_original_geometries(self):
#         self.original_geometries.clear()
#         for entity in self.doc.modelspace():
#             hndl = entity.dxf.handle
#             tp = entity.dxftype()
#             if tp == "CIRCLE":
#                 self.original_geometries[hndl] = {"type": "CIRCLE", "center": entity.dxf.center, "radius": entity.dxf.radius}
#             elif tp == "LINE":
#                 self.original_geometries[hndl] = {"type": "LINE", "start": entity.dxf.start, "end": entity.dxf.end}

#     # ---------------------------
#     # АВТОМАТИЧНА АДАПТАЦІЯ РОЗМІРІВ ЗАМОВЛЕННЯ
#     # ---------------------------
#     def process_manual_input_dimension_scale(self):
#         if not self.stretch_zones:
#             self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
#             return

#         cur_w = self.input_current_width.text().strip()
#         new_w = self.input_target_width.text().strip()
#         cur_h = self.input_current_height.text().strip()
#         new_h = self.input_target_height.text().strip()

#         delta_x = float(new_w) - float(cur_w) if (cur_w and new_w) else 0.0
#         delta_y = float(new_h) - float(cur_h) if (cur_h and new_h) else 0.0

#         if delta_x == 0.0 and delta_y == 0.0:
#             self.lbl_status_calc.setText("<font color='yellow'>Дельта 0 мм. Змініть габарити.</font>")
#             return

#         count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
#         count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

#         share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
#         share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

#         for zone in self.stretch_zones:
#             if zone['axis'] == 'X': zone['stretch_val'] = share_delta_x
#             elif zone['axis'] == 'Y': zone['stretch_val'] = share_delta_y

#         for hndl, orig in self.original_geometries.items():
#             if hndl not in self.doc.entitydb: continue
#             entity = self.doc.entitydb[hndl]
#             if orig["type"] == "CIRCLE":
#                 cx, cy, cz = orig["center"]
#                 entity.dxf.center = (self.calculate_cascade_shift(cx, 'X', hndl), self.calculate_cascade_shift(cy, 'Y', hndl), cz)
#             elif orig["type"] == "LINE":
#                 sx, sy, sz = orig["start"]
#                 ex, ey, ez = orig["end"]
#                 entity.dxf.start = (self.calculate_cascade_shift(sx, 'X', hndl), self.calculate_cascade_shift(sy, 'Y', hndl), sz)
#                 entity.dxf.end = (self.calculate_cascade_shift(ex, 'X', hndl), self.calculate_cascade_shift(ey, 'Y', hndl), ez)

#         self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔX={delta_x:+.2f}мм | ΔY={delta_y:+.2f}мм</font>")
#         self.doc.saveas(self.dxf_path)
        
#         # Каскадний зсув меж прямокутників зон розтягування
#         for zone in self.stretch_zones:
#             stretch_amount = zone['stretch_val']
#             if stretch_amount == 0: continue
#             active_axis = zone['axis']
#             active_max = zone['max']
#             zone['max'] += stretch_amount
#             for sub_z in self.stretch_zones:
#                 if sub_z == zone or sub_z['axis'] != active_axis: continue
#                 if sub_z['min'] >= active_max:
#                     sub_z['min'] += stretch_amount
#                     sub_z['max'] += stretch_amount

#         for zone in self.stretch_zones: 
#             zone['stretch_val'] = 0.0

#         # Зберігаємо оновлений стан в історію
#         self.push_to_history()

#         self.input_current_width.clear()
#         self.input_target_width.clear()
#         self.input_current_height.clear()
#         self.input_target_height.clear()

#         self.load_zones_into_list()
#         self.load_entities_into_list()
#         self.update_viewer()

#     # ---------------------------
#     # МАТРИЦЯ ОБЕРТАННЯ ТА ДЗЕРКАЛА (Matrix44)
#     # ---------------------------
#     def transform_selected_entities(self, mode):
#         if not self.selected_handles: return
#         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
#         if not selected_entities: return

#         cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
#         cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

#         for entity in selected_entities:
#             if mode == "ROT90":
#                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(90)), Matrix44.translate(cx, cy, 0))
#             elif mode == "ROT180":
#                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(180)), Matrix44.translate(cx, cy, 0))
#             elif mode == "MIRROR_H":
#                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
#             elif mode == "MIRROR_V":
#                 m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
#             else: continue
#             entity.transform(m)

#         self.doc.saveas(self.dxf_path)
        
#         # Зберігаємо оновлений стан в історію
#         self.push_to_history()
        
#         self.update_viewer()
#         self.load_entities_into_list()

#     # ---------------------------
#     # ІНЖЕНЕРНЕ ПРИТИСКАННЯ ДО КРАЇВ (МАРЖА 5ММ)
#     # ---------------------------
#     def align_selected_to_edge(self, edge):
#         if not self.selected_handles: return
#         selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
#         if not selected_entities: return

#         try:
#             bounds = dxf_bbox.extents(self.doc.modelspace())
#             door_min_x, door_max_x = bounds.extmin[0], bounds.extmax[0]
#             door_min_y, door_max_y = bounds.extmin[1], bounds.extmax[1]
#         except Exception:
#             door_min_x, door_max_x, door_min_y, door_max_y = 0.0, 1000.0, 0.0, 2040.0

#         margin = 5.0
#         shift_x, shift_y = 0.0, 0.0

#         sel_min_x = min(e.left_x for e in selected_entities)
#         sel_max_x = max(e.right_x for e in selected_entities)
#         sel_min_y = min(e.bottom_y for e in selected_entities)
#         sel_max_y = max(e.top_y for e in selected_entities)

#         if edge == "LEFT": shift_x = door_min_x + margin - sel_min_x
#         elif edge == "RIGHT": shift_x = door_max_x - margin - sel_max_x
#         elif edge == "BOTTOM": shift_y = door_min_y + margin - sel_min_y
#         elif edge == "TOP": shift_y = door_max_y - margin - sel_max_y

#         for entity in selected_entities:
#             entity.translate(shift_x, shift_y, 0)

#         self.doc.saveas(self.dxf_path)
        
#         # Зберігаємо оновлений стан в історію
#         self.push_to_history()
        
#         self.update_viewer()
#         self.load_entities_into_list()

 
#     def assign_to_left_fix(self):
#         self.left_fixed_handles.update(self.selected_handles)
#         self.right_fixed_handles.difference_update(self.selected_handles)
#         self.auto_detect_between_zone('X')
#         self.push_to_history()  # Фіксуємо подію в Undo
#         self.update_viewer()
#         self.load_entities_into_list()

#     def assign_to_right_fix(self):
#         self.right_fixed_handles.update(self.selected_handles)
#         self.left_fixed_handles.difference_update(self.selected_handles)
#         self.auto_detect_between_zone('X')
#         self.push_to_history()  # Фіксуємо подію в Undo
#         self.update_viewer()
#         self.load_entities_into_list()

#     def assign_to_bottom_fix(self):
#         self.bottom_fixed_handles.update(self.selected_handles)
#         self.top_fixed_handles.difference_update(self.selected_handles)
#         self.auto_detect_between_zone('Y')
#         self.push_to_history()  # Фіксуємо подію в Undo
#         self.update_viewer()
#         self.load_entities_into_list()

#     def assign_to_top_fix(self):
#         self.top_fixed_handles.update(self.selected_handles)
#         self.bottom_fixed_handles.difference_update(self.selected_handles)
#         self.auto_detect_between_zone('Y')
#         self.push_to_history()  # Фіксуємо подію в Undo
#         self.update_viewer()
#         self.load_entities_into_list()


    
#     def set_interface_theme(self, theme_name):
#         if theme_name == "Темна":
#             self.setStyleSheet("""
#                 QMainWindow { background-color: #252526; }
#                 QWidget { color: #ffffff; font-family: 'Segoe UI'; }
#                 QGroupBox { font-weight: bold; border: 1px solid #454545; margin-top: 12px; padding-top: 10px; }
#                 QPushButton { background-color: #3c3c3c; border: 1px solid #555555; padding: 6px; border-radius: 4px; }
#                 QPushButton:hover { background-color: #505050; }
#                 QLineEdit { background-color: #1e1e1e; border: 1px solid #555555; color: white; padding: 4px; border-radius: 3px; }
#                 QListWidget { background-color: #1e1e1e; border: 1px solid #3c3c3c; color: #d4d4d4; }
#                 QListWidget::item:selected { background-color: #04396c; color: white; }
#                 QComboBox { background-color: #3c3c3c; border: 1px solid #555555; padding: 4px; color: white; }
#                 QSlider::groove:horizontal { border: 1px solid #555555; height: 8px; background: #3c3c3c; border-radius: 4px; }
#                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
#                 #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; }
#                 #rightFixBtn { background-color: #611a15; color: #ffebee; }
#                 #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; }
#                 #topFixBtn { background-color: #524705; color: #fffde7; }
#             """)
#         else:
#             self.setStyleSheet("""
#                 QMainWindow { background-color: #f3f3f3; }
#                 QWidget { color: #000000; font-family: 'Segoe UI'; }
#                 QGroupBox { font-weight: bold; border: 1px solid #cccccc; margin-top: 12px; padding-top: 10px; }
#                 QPushButton { background-color: #e1e1e1; border: 1px solid #bbbbbb; padding: 6px; border-radius: 4px; }
#                 QPushButton:hover { background-color: #d0d0d0; }
#                 QLineEdit { background-color: #ffffff; border: 1px solid #cccccc; color: black; padding: 4px; border-radius: 3px; }
#                 QListWidget { background-color: #ffffff; border: 1px solid #cccccc; color: #000000; }
#                 QListWidget::item:selected { background-color: #b1d7f7; color: black; }
#                 QComboBox { background-color: #ffffff; border: 1px solid #cccccc; padding: 4px; color: black; }
#                 QSlider::groove:horizontal { border: 1px solid #cccccc; height: 8px; background: #e1e1e1; border-radius: 4px; }
#                 QSlider::handle:horizontal { background: #007acc; width: 18px; margin: -5px 0; border-radius: 9px; }
#                 #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
#                 #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
#                 #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
#                 #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
#             """)


#     def reset_all_parametric_zones(self):
#         self.left_fixed_handles.clear()
#         self.right_fixed_handles.clear()
#         self.bottom_fixed_handles.clear()
#         self.top_fixed_handles.clear()
#         self.stretch_zones.clear()
#         self.active_zone_index = None
#         self.slider.setEnabled(False)
#         self.slider_label.setText("Оберіть зону деформації зі списку")
#         self.update_viewer()
#         self.load_zones_into_list()
#         self.load_entities_into_list()


#     # ---------------------------
#     # МЕНЕДЖЕР ПАРАМЕТРИЧНИХ ЗОН ПРОСТОРУ
#     # ---------------------------
#     def create_zone_from_selection(self, axis):
#         if not self.selected_handles or not self.original_geometries: return
#         active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
#         if not active_entities or len(active_entities) < 2: 
#             self.clear_selection()
#             return
#         if axis == 'X':
#             min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
#             max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
#         else:
#             min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
#             max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
#         if max_val > min_val and (max_val - min_val) > 2.0:
#             self.add_or_update_zone_bounds(min_val, max_val, axis)
#             self.push_to_history()  # Фіксуємо подію створення зони в Undo
#         self.clear_selection()


#     # ---------------------------
#     # СЛУЖБОВІ МЕТОДИ СИНХРОНІЗАЦІЇ
#     # ---------------------------
# # Не забудьте додати імпорт

#     def process_manual_rubber_band(self, rect):
#         # Отримуємо стан клавіші Ctrl
#         modifiers = QGuiApplication.keyboardModifiers()
#         is_ctrl_pressed = (modifiers & Qt.ControlModifier)
        
#         # Якщо Ctrl не натиснуто, очищуємо попередній вибір
#         if not is_ctrl_pressed:
#             self.selected_handles.clear()
                
#         path = QPainterPath()
#         path.addRect(rect)
        
#         # Використовуємо items з PATH
#         # IntersectsItemShape - хороший вибір для CAD
#         matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
        
#         found_any = False
#         for item in matched_items:
#             # Важливо: ігноруємо елементи, що не мають даних (наприклад, фонові об'єкти)
#             hndl = item.data(Qt.ItemDataRole.UserRole)
#             if hndl:
#                 self.selected_handles.add(hndl)
#                 found_any = True
                    
#         if found_any:
#             self.sync_list_from_handles()
#             self.update_viewer()

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

    
#     def on_slider_value_changed(self, value):
#             if self.active_zone_index is None or self.is_loading_history:
#                 return

#             self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
#             zone = self.stretch_zones[self.active_zone_index]
#             self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

#             for hndl, orig in self.original_geometries.items():
#                 if hndl not in self.doc.entitydb: continue
#                 entity = self.doc.entitydb[hndl]

#                 if orig["type"] == "CIRCLE":
#                     cx, cy, cz = orig["center"]
#                     entity.dxf.center = (
#                         self.calculate_cascade_shift(cx, 'X', hndl),
#                         self.calculate_cascade_shift(cy, 'Y', hndl),
#                         cz
#                     )
#                 elif orig["type"] == "LINE":
#                     sx, sy, sz = orig["start"]
#                     ex, ey, ez = orig["end"]
#                     entity.dxf.start = (
#                         self.calculate_cascade_shift(sx, 'X', hndl),
#                         self.calculate_cascade_shift(sy, 'Y', hndl),
#                         sz
#                     )
#                     entity.dxf.end = (
#                         self.calculate_cascade_shift(ex, 'X', hndl),
#                         self.calculate_cascade_shift(ey, 'Y', hndl),
#                         ez
#                     )

#             self.update_viewer()

#     def calculate_cascade_shift(self, orig_val, axis, hndl):
#         if axis == 'X' and hndl:
#             if hndl in self.left_fixed_handles: return orig_val
#             if hndl in self.right_fixed_handles:
#                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
#         elif axis == 'Y' and hndl:
#             if hndl in self.bottom_fixed_handles: return orig_val
#             if hndl in self.top_fixed_handles:
#                 return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

#         shifted_val = orig_val
#         for zone in self.stretch_zones:
#             if zone['axis'] != axis: continue
#             z_min = zone['min']
#             z_max = zone['max']
#             val = zone['stretch_val']

#             if orig_val >= z_max:
#                 shifted_val += val
#             elif z_min < orig_val < z_max:
#                 width = z_max - z_min
#                 if width > 0:
#                     ratio = (orig_val - z_min) / width
#                     shifted_val += val * ratio
                    
#         return shifted_val

#     def on_slider_released(self):
#         self.doc.saveas(self.dxf_path)
        
#         active_zone = self.stretch_zones[self.active_zone_index]
#         stretch_amount = active_zone['stretch_val']
#         active_axis = active_zone['axis']
#         active_max = active_zone['max']

#         active_zone['max'] += stretch_amount

#         for idx, zone in enumerate(self.stretch_zones):
#             if idx == self.active_zone_index or zone['axis'] != active_axis:
#                 continue
#             if zone['min'] >= active_max:
#                 zone['min'] += stretch_amount
#                 zone['max'] += stretch_amount

#         for zone in self.stretch_zones:
#             zone['stretch_val'] = 0.0

#         self.history.save_state()
#         self.history.clear_redo()
#         self.save_zones_history_state()
#         self.zones_redo_stack.clear()
#         self.update_history_buttons_state()

#         self.save_original_geometries()

#         self.slider.blockSignals(True)
#         self.slider.setValue(0)
#         self.slider.blockSignals(False)

#         self.load_zones_into_list()
#         self.load_entities_into_list()
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
#                 if (round(cx, 2), round(cy, 2)) in seen: continue
#                 seen.add((round(cx, 2), round(cy, 2)))
#                 text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.2f}, Y:{cy:.2f}"
#             elif tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
#                 seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
#                 text = f"📏 Лінія (ID: {hndl}) Початок: ({x1:.2f}, {y1:.2f}), Кінець: ({x2:.2f}, {y2:.2f}), Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.2f} мм"
#             else: continue
#             item = QListWidgetItem(text)
#             item.setData(Qt.ItemDataRole.UserRole, hndl)
#             self.entity_list.addItem(item)
#         self.entity_list.blockSignals(False)



#     def update_viewer(self):
#         self.scene = QGraphicsScene()
#         self.view.setScene(self.scene)
#         self.overlay_items.clear()

#         if self.current_theme == "Темна":
#             self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
#             base_line_color = QColor(220, 220, 220)
#         else:
#             self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
#             base_line_color = QColor(80, 80, 80)
# # Довжина осей в обидва боки
#         length = 150.0 
        
#         # Вісь X: від -length до +length (синя)
#         self.scene.addLine(-length, 0, length, 0, QPen(QColor(33, 150, 243), 2.5))
#         # Стрілочка на кінці X
#         self.scene.addLine(length, 0, length - 10, -4, QPen(QColor(33, 150, 243), 2.5))
#         self.scene.addLine(length, 0, length - 10, 4, QPen(QColor(33, 150, 243), 2.5))

#         # Вісь Y: від -length до +length (зелена)
#         # Оскільки в Qt Y зростає вниз, для візуального "вгору" ми використовуємо від'ємні значення
#         self.scene.addLine(0, length, 0, -length, QPen(QColor(76, 175, 80), 2.5))
#         # Стрілочка на кінці Y (на "верхньому" кінці, тобто при -length)
#         self.scene.addLine(0, -length, -4, -length + 10, QPen(QColor(76, 175, 80), 2.5))
#         self.scene.addLine(0, -length, 4, -length + 10, QPen(QColor(76, 175, 80), 2.5))

#         # Додайте це після малювання осей
#         marker = QGraphicsEllipseItem(-2, -2, 4, 4) # Маленьке коло 4x4 пікселі
#         marker.setBrush(QBrush(QColor("red")))
#         self.scene.addItem(marker)

#         seen_circles, seen_lines = set(), set()
#         try:
#             bounds = dxf_bbox.extents(self.doc.modelspace())
#             abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
#             abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
#         except Exception:
#             abs_min_x, abs_max_x = -100.0, 1000.0
#             abs_min_y, abs_max_y = -100.0, 2000.0


#         bounds = dxf_bbox.extents(self.doc.modelspace())
#         # print(f"DXF Extents: Min={bounds.extmin}, Max={bounds.extmax}")

#         for idx, zone in enumerate(self.stretch_zones):
#             disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
#             disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) 
#             if zone['axis'] == 'X':
#                 rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
#             else:
#                 rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

#             if idx == self.active_zone_index:
#                 color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
#                 rect_item.setBrush(QBrush(color))
#                 rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
#             else:
#                 rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
#                 rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
#             self.scene.addItem(rect_item)

#         for entity in self.doc.modelspace():
#             hndl = entity.dxf.handle
#             tp = entity.dxftype()
#             pyqt_item = None
#             if tp == "CIRCLE":
#                 cx, cy, _ = entity.dxf.center
#                 r = entity.dxf.radius
#                 if (round(cx, 2), round(cy, 2)) in seen_circles: continue
#                 seen_circles.add((round(cx, 2), round(cy, 2)))
#                 pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
#             elif tp == "LINE":
#                 x1, y1, _ = entity.dxf.start
#                 x2, y2, _ = entity.dxf.end
#                 if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen_lines: continue
#                 seen_lines.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
#                 pyqt_item = SelectableLine(x1, -y1, x2, -y2)

#             if pyqt_item:
#                 pyqt_item.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, False)
#                 pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
#                 if hndl in self.selected_handles: pyqt_item.setPen(QPen(QColor(0, 120, 255), 3, Qt.PenStyle.SolidLine))
#                 elif hndl in self.left_fixed_handles: pyqt_item.setPen(QPen(QColor(46, 125, 50), 2.5, Qt.PenStyle.SolidLine))
#                 elif hndl in self.right_fixed_handles: pyqt_item.setPen(QPen(QColor(198, 40, 40), 2.5, Qt.PenStyle.SolidLine))
#                 elif hndl in self.bottom_fixed_handles: pyqt_item.setPen(QPen(QColor(21, 101, 192), 2.5, Qt.PenStyle.SolidLine))
#                 elif hndl in self.top_fixed_handles: pyqt_item.setPen(QPen(QColor(249, 168, 37), 2.5, Qt.PenStyle.SolidLine))
#                 else: pyqt_item.setPen(QPen(base_line_color, 2, Qt.PenStyle.SolidLine))
#                 pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
#                 self.scene.addItem(pyqt_item)
#                 self.overlay_items[hndl] = pyqt_item

#         self.view.setSceneRect(self.scene.itemsBoundingRect())

#     def apply_ezdxf_patch(self):
#         from ezdxf.entities import Line, Circle
#         Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
#         Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
#         Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
#         Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

#         Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
#         Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
#         Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
#         Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

#     def on_scene_item_clicked(self, handle):
#         modifiers = QGuiApplication.keyboardModifiers()
#         is_ctrl_pressed = (modifiers & Qt.ControlModifier)
        
#         if is_ctrl_pressed:
#             # Якщо Ctrl натиснуто - перемикаємо стан (якщо було - видаляємо, якщо не було - додаємо)
#             if handle in self.selected_handles:
#                 self.selected_handles.remove(handle)
#             else:
#                 self.selected_handles.add(handle)
#         else:
#             # Якщо не натиснуто - вибираємо тільки один
#             self.selected_handles = {handle}
            
#         self.sync_list_from_handles()
#         self.update_viewer()

        
#     def load_zones_into_list(self):
#         self.zone_list_widget.blockSignals(True)
#         self.zone_list_widget.clear()
#         for idx, zone in enumerate(self.stretch_zones):
#             axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
#             text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.2f} -> {zone['max']:.2f}] Довжина: {(zone['max'] - zone['min']):.2f} мм"
#             item = QListWidgetItem(text)
#             item.setData(Qt.ItemDataRole.UserRole, idx)
#             self.zone_list_widget.addItem(item)
#         self.zone_list_widget.blockSignals(False)

    
#     def add_or_update_zone_bounds(self, min_v, max_v, axis):
#         for zone in self.stretch_zones:
#             if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0: return
#         new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
#         self.stretch_zones.append(new_zone)eight
#         self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
#         self.load_zones_into_list()
#         for idx, zone in enumerate(self.stretch_zones):
#             if zone['axis'] == axis and zone['min'] == min_v:
#                 self.zone_list_widget.setCurrentRow(idx)
#                 break


    
#     def auto_detect_between_zone(self, axis):
#         if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
#             max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
#             min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
#             if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
#                 self.add_or_update_zone_bounds(max_left_x + 5.0, min_right_x - 5.0, 'X')
#         elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
#             max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
#             min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
#             if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
#                 self.add_or_update_zone_bounds(max_bottom_y + 5.0, min_top_y - 5.0, 'Y')



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

import ezdxf
import ezdxf.bbox as dxf_bbox
from ezdxf.math import Matrix44
from ezdxf.addons.importer import Importer 

from PySide6.QtWidgets import (
    QMainWindow, QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QSlider, 
    QGraphicsScene, QAbstractItemView, QGraphicsEllipseItem,
    QGroupBox, QGraphicsRectItem, QComboBox, QLineEdit, QGraphicsView, QGraphicsPathItem
)
from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QPen, QPainterPath, QPainter, QGuiApplication


# Припускаємо, що ці класи лежать у сусідніх файлах, як у вашому проекті
try:
    from graphics_items import SelectableCircle, SelectableLine, SelectableArc
    from graphics_view import AdvancedGraphicsView
    from history_manager import HistoryManager
except ImportError:
    # Заглушки для автономного запуску, якщо файли розділені
    AdvancedGraphicsView = QGraphicsView
    class HistoryManager:
        def __init__(self, p): self.p = p; self.undo_stack=[1]; self.redo_stack=[]
        def save_state(self): pass
        def clear_redo(self): pass
        def undo(self): return True
        def redo(self): return True

# ---------------------------------------------------------------------------
# 📐 ДИНАМІЧНЕ РОЗШИРЕННЯ БІБЛІОТЕКИ EZDXF (ПАТЧ ДЛЯ КООРДИНАТ + АРКИ)
# ---------------------------------------------------------------------------
def patch_ezdxf_entities():
    from ezdxf.entities import Line, Circle, Arc
    
    # Лінії
    Line.left_x = property(lambda self: min(self.dxf.start[0], self.dxf.end[0]))
    Line.right_x = property(lambda self: max(self.dxf.start[0], self.dxf.end[0]))
    Line.bottom_y = property(lambda self: min(self.dxf.start[1], self.dxf.end[1]))
    Line.top_y = property(lambda self: max(self.dxf.start[1], self.dxf.end[1]))

    # Кола
    Circle.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
    Circle.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
    Circle.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
    Circle.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

    # Дуги (Простий інженерний bbox за радіусом центра, безпечний для розрахунку зон)
    Arc.left_x = property(lambda self: self.dxf.center[0] - self.dxf.radius)
    Arc.right_x = property(lambda self: self.dxf.center[0] + self.dxf.radius)
    Arc.bottom_y = property(lambda self: self.dxf.center[1] - self.dxf.radius)
    Arc.top_y = property(lambda self: self.dxf.center[1] + self.dxf.radius)

patch_ezdxf_entities()


class MiniCAD(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAD Двері: Професійний 2D Параметризатор")
        self.setGeometry(100, 100, 1600, 950)

        self.project_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
        
     
        self.dxf_path = os.path.join(self.project_dir, "drawing.DXF")
        self.current_theme = "Темна"

        self.selected_handles = set()
        self.overlay_items = {}
        self.original_geometries = {}
        self.is_loading_history = False

        self.left_fixed_handles = set()
        self.right_fixed_handles = set()
        self.bottom_fixed_handles = set()
        self.top_fixed_handles = set()

        self.rigid_blocks = []
        self.rigid_groups = []  
        
        self.stretch_zones = []
        self.active_zone_index = None

        self.zones_undo_stack = []
        self.zones_redo_stack = []
        self.stretchable_handles = set() 

        self.load_doc_safely()

        self.history = HistoryManager(self.dxf_path)
        self.history.save_state()
        self.save_zones_history_state()

        self.init_ui()
        self.set_interface_theme(self.current_theme)
        self.save_original_geometries()
        self.update_viewer()
        self.load_entities_into_list()
        self.scan_project_folder_for_dxf()

    def load_doc_safely(self):
        """Безпечне завантаження: якщо файл відсутній - створюємо порожній."""
        if os.path.exists(self.dxf_path):
            try:
                self.doc = ezdxf.readfile(self.dxf_path)
            except Exception as e:
                print(f"Помилка читання файлу, створюю новий: {e}")
                self.doc = ezdxf.new()
                self.doc.saveas(self.dxf_path)
        else:
            # Спробуємо знайти хоча б якийсь DXF в папці, якщо drawing.DXF немає
            dxf_files = [f for f in os.listdir(self.project_dir) if f.lower().endswith('.dxf')]
            if dxf_files:
                self.dxf_path = os.path.join(self.project_dir, dxf_files[0])
                self.doc = ezdxf.readfile(self.dxf_path)
            else:
                self.doc = ezdxf.new()
                self.doc.saveas(self.dxf_path)


    def init_ui(self):
        main_widget = QWidget()
        self.central_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # --- ЛІВИЙ ПРОВІДНИК ---
        folder_explorer_widget = QWidget()
        folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
        folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
        lbl_explorer_title = QLabel("📁 <b>Провідник DXF (утримуйте Ctrl):</b>")
        lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
        folder_explorer_layout.addWidget(lbl_explorer_title)
        
        self.file_explorer_list = QListWidget()
        self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_explorer_list.itemSelectionChanged.connect(self.on_dxf_selection_changed_in_explorer)
        folder_explorer_layout.addWidget(self.file_explorer_list)
        self.central_layout.addWidget(folder_explorer_widget, stretch=1)

        # --- ЦЕНТРАЛЬНИЙ ГРАФІЧНИЙ БЛОК ---
        self.scene = QGraphicsScene()
        self.view = AdvancedGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.central_layout.addWidget(self.view, stretch=4)

        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag) 
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse) 
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # --- ПРАВА ПАНЕЛЬ КЕРУВАННЯ ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True) 
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_area.setWidget(control_panel)
        self.central_layout.addWidget(self.scroll_area, stretch=2)

        # БЛОК 1: АДАПТАЦІЯ
        auto_scale_group = QGroupBox("🚀 Адаптація під розміри замовлення (з припусками)")
        auto_scale_box = QVBoxLayout()

        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("<b>Ширина (X):</b> Поточна:"))
        self.input_current_width = QLineEdit()
        self.input_current_width.setPlaceholderText("1000")
        width_layout.addWidget(self.input_current_width)
        width_layout.addWidget(QLabel("➡️ Нова:"))
        self.input_target_width = QLineEdit()
        self.input_target_width.setPlaceholderText("1010")
        width_layout.addWidget(self.input_target_width)
        auto_scale_box.addLayout(width_layout)

        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("<b>Висота (Y):</b> Поточна:"))
        self.input_current_height = QLineEdit()
        self.input_current_height.setPlaceholderText("2040")
        height_layout.addWidget(self.input_current_height)
        height_layout.addWidget(QLabel("➡️ Нова:"))
        self.input_target_height = QLineEdit()
        self.input_target_height.setPlaceholderText("2050")
        height_layout.addWidget(self.input_target_height)
        auto_scale_box.addLayout(height_layout)

        self.lbl_status_calc = QLabel("Введіть розміри та натисніть кнопку нижче")
        self.lbl_status_calc.setStyleSheet("color: #4fc3f7; font-size: 11px;")
        auto_scale_box.addWidget(self.lbl_status_calc)

        self.btn_apply_auto_scale = QPushButton("⚡ Автоматично розрахувати дельту та змінити")
        self.btn_apply_auto_scale.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 8px;")
        self.btn_apply_auto_scale.clicked.connect(self.process_manual_input_dimension_scale)
        auto_scale_box.addWidget(self.btn_apply_auto_scale)

        auto_scale_group.setLayout(auto_scale_box)
        control_layout.addWidget(auto_scale_group)

        btn_open = QPushButton("📂 Відкрити файл")
        btn_open.clicked.connect(self.open_dxf_file)
        control_layout.addWidget(btn_open)

        # БЛОК ІСТОРІЇ
        history_group = QGroupBox("Історія конструкторських змін")
        history_box = QHBoxLayout()
        self.btn_undo = QPushButton("⬅️ Назад (Undo)")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_redo = QPushButton("Вперед (Redo) ➡️")
        self.btn_redo.clicked.connect(self.redo)
        history_box.addWidget(self.btn_undo)
        history_box.addWidget(self.btn_redo)
        history_group.setLayout(history_box)
        control_layout.addWidget(history_group)

        # ГРУПА ФІКСАЦІЇ СТОРІН
        fix_group = QGroupBox("1.  Фіксація жорстких блоків (елементів фурнітури)")
        fix_box = QVBoxLayout()
  # Кнопки керування жорсткими групами деталей
        self.btn_create_group = QPushButton("🧩 Згрупувати виділене в Жорстку Групу")
        self.btn_create_group.setStyleSheet("background-color: #673ab7; color: white;")
        self.btn_create_group.clicked.connect(self.create_rigid_group)
        fix_box.addWidget(self.btn_create_group)

        self.btn_disband_group = QPushButton("💥 Розформувати вибрану групу")
        self.btn_disband_group.clicked.connect(self.disband_group)
        fix_box.addWidget(self.btn_disband_group)

        fix_box.addWidget(QLabel("<b>Список жорстких груп:</b>"))
        self.group_list_widget = QListWidget()
        self.group_list_widget.setFixedHeight(80)
        self.group_list_widget.itemSelectionChanged.connect(self.on_group_list_selection)
        fix_box.addWidget(self.group_list_widget)
        h_fix_layout = QHBoxLayout()
        self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
        self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
        self.btn_set_left_fix.setObjectName("leftFixBtn")
        self.btn_set_right_fix.setObjectName("rightFixBtn")
        self.btn_set_left_fix.clicked.connect(self.assign_to_left_fix)
        self.btn_set_right_fix.clicked.connect(self.assign_to_right_fix)
     
        h_fix_layout.addWidget(self.btn_set_left_fix)
        h_fix_layout.addWidget(self.btn_set_right_fix)
        
        fix_box.addLayout(h_fix_layout)

        v_fix_layout = QHBoxLayout()
        self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
        self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
        self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
        self.btn_set_top_fix.setObjectName("topFixBtn")
        self.btn_set_bottom_fix.clicked.connect(self.assign_to_bottom_fix)
        self.btn_set_top_fix.clicked.connect(self.assign_to_top_fix)
        v_fix_layout.addWidget(self.btn_set_bottom_fix)
        v_fix_layout.addWidget(self.btn_set_top_fix)
        fix_box.addLayout(v_fix_layout)
        fix_group.setLayout(fix_box)
        control_layout.addWidget(fix_group)

        control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
        self.entity_list = QListWidget()
        self.entity_list.setFixedHeight(150)
        self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        control_layout.addWidget(self.entity_list)

        zone_group = QGroupBox("2. Створення зон деформації простору")
        zone_box = QVBoxLayout()
        self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
        self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
        self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
        self.btn_add_zone_x.clicked.connect(lambda: self.create_zone_from_selection('X'))
        self.btn_add_zone_y.clicked.connect(lambda: self.create_zone_from_selection('Y'))
        self.btn_clear_zones.clicked.connect(self.reset_all_parametric_zones)
        self.btn_toggle_stretch = QPushButton(" Позначити виділене як еластичне")
        self.btn_toggle_stretch.setStyleSheet("background-color: #ff9800; color: black; font-weight: bold;")
        self.btn_toggle_stretch.clicked.connect(self.toggle_stretchable)
        zone_box.addWidget(self.btn_toggle_stretch)
        zone_box.addWidget(self.btn_add_zone_x)
        zone_box.addWidget(self.btn_add_zone_y)
        zone_box.addWidget(self.btn_clear_zones)
        zone_group.setLayout(zone_box)
        control_layout.addWidget(zone_group)

        self.btn_auto_detect_zones = QPushButton("✨ Авто-визначення ідеальних зон (X та Y)")
        self.btn_auto_detect_zones.setStyleSheet("background-color: #009688; color: white; font-weight: bold;")
        self.btn_auto_detect_zones.clicked.connect(self.smart_auto_detect_zones)
        zone_box.addWidget(self.btn_auto_detect_zones)

        control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
        self.zone_list_widget = QListWidget()
        self.zone_list_widget.setFixedHeight(150)
        self.zone_list_widget.itemSelectionChanged.connect(self.on_zone_selection_changed)
        control_layout.addWidget(self.zone_list_widget)

        self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
        control_layout.addWidget(self.slider_label)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 600)
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        self.slider.valueChanged.connect(self.on_slider_value_changed)
        self.slider.sliderReleased.connect(self.on_slider_released)
        control_layout.addWidget(self.slider)

        # ТРАНСФОРМАЦІЇ
        transform_group = QGroupBox("🔄 Орієнтація та обертання виділених деталей")
        transform_box = QVBoxLayout()
        rot_layout = QHBoxLayout()
        self.btn_rot_90 = QPushButton("↪️ Поворот 90°")
        self.btn_rot_90.clicked.connect(lambda: self.transform_selected_entities("ROT90"))
        self.btn_rot_180 = QPushButton("🔁 Поворот 180°")
        self.btn_rot_180.clicked.connect(lambda: self.transform_selected_entities("ROT180"))
        rot_layout.addWidget(self.btn_rot_90)
        rot_layout.addWidget(self.btn_rot_180)
        transform_box.addLayout(rot_layout)

        mirror_layout = QHBoxLayout()
        self.btn_mirror_h = QPushButton("↔️ Віддзеркалити по Х")
        self.btn_mirror_v = QPushButton("↕️ Віддзеркалити по Y")
        self.btn_mirror_h.clicked.connect(lambda: self.transform_selected_entities("MIRROR_H"))
        self.btn_mirror_v.clicked.connect(lambda: self.transform_selected_entities("MIRROR_V"))
        mirror_layout.addWidget(self.btn_mirror_h)
        mirror_layout.addWidget(self.btn_mirror_v)
        transform_box.addLayout(mirror_layout)
        transform_group.setLayout(transform_box)
        control_layout.addWidget(transform_group)

        theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
        theme_box = QHBoxLayout()
        theme_box.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темна", "Світла"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_box.addWidget(self.theme_combo)
        theme_group.setLayout(theme_box)
        control_layout.addWidget(theme_group)

        control_layout.addStretch()
        self.update_history_buttons_state()


          
    def set_interface_theme(self, theme_name):
        if theme_name == "Темна":
            self.setStyleSheet("""
                /* Головне вікно та загальні налаштування тексту */
                QMainWindow { 
                    background-color: #1e1e1e; 
                }
                QWidget { 
                    color: #d4d4d4; 
                    font-family: 'Segoe UI', -apple-system, sans-serif; 
                    font-size: 12px;
                }
                
                /* Скрол-зона та панель керування */
                QScrollArea {
                    border: none;
                    background-color: #252526;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: #252526;
                }

                /* Контейнери (Group Boxes) */
                QGroupBox { 
                    font-weight: bold; 
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    color: #007acc;
                    border: 1px solid #3c3c3c; 
                    border-radius: 6px;
                    margin-top: 15px; 
                    padding-top: 15px; 
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-bottom: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 10px;
                    padding: 0 5px;
                    background-color: #252526;
                }

                /* Кнопки загальні */
                QPushButton { 
                    background-color: #333333; 
                    border: 1px solid #454545; 
                    color: #ffffff;
                    padding: 8px 12px; 
                    border-radius: 4px; 
                    font-weight: 500;
                }
                QPushButton:hover { 
                    background-color: #454545; 
                    border-color: #007acc;
                }
                QPushButton:pressed {
                    background-color: #1e1e1e;
                }
                QPushButton:disabled {
                    background-color: #2d2d2d;
                    color: #5a5a5a;
                    border-color: #333333;
                }

                /* Поля введення розмірів дверного полотна (Line Edits) */
                QLineEdit { 
                    background-color: #1e1e1e; 
                    border: 1px solid #3c3c3c; 
                    color: #ffffff; 
                    padding: 6px; 
                    border-radius: 4px; 
                    selection-background-color: #04396c;
                }
                QLineEdit:focus {
                    border: 1px solid #007acc;
                    background-color: #202020;
                }
                QLineEdit::placeholder {
                    color: #5a5a5a;
                }

                /* Інженерні списки (Елементи та Зони дверей) */
                QListWidget { 
                    background-color: #1e1e1e; 
                    border: 1px solid #3c3c3c; 
                    border-radius: 4px;
                    color: #d4d4d4; 
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 6px;
                    border-bottom: 1px solid #2d2d2d;
                    border-radius: 2px;
                }
                QListWidget::item:hover {
                    background-color: #2a2d2e;
                    color: #ffffff;
                }
                QListWidget::item:selected { 
                    background-color: #04396c; 
                    color: #ffffff; 
                }

                /* Випадні списки (Теми) */
                QComboBox { 
                    background-color: #333333; 
                    border: 1px solid #454545; 
                    border-radius: 4px;
                    padding: 5px 10px; 
                    color: #ffffff; 
                }
                QComboBox:hover {
                    border-color: #007acc;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #1e1e1e;
                    border: 1px solid #3c3c3c;
                    selection-background-color: #04396c;
                }

                /* Слайдери розтягування зон (Sliders) */
                QSlider::groove:horizontal { 
                    border: 1px solid #454545; 
                    height: 6px; 
                    background: #333333; 
                    border-radius: 3px; 
                }
                QSlider::sub-page:horizontal {
                    background: #007acc;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal { 
                    background: #007acc; 
                    width: 16px; 
                    height: 16px;
                    margin-top: -5px; 
                    margin-bottom: -5px;
                    border-radius: 8px; 
                }
                QSlider::handle:horizontal:hover {
                    background: #1496ff;
                }
                QSlider::handle:horizontal:disabled {
                    background: #555555;
                }

                /* Кастомні кнопки швидкої фіксації завіс/замків */
                #leftFixBtn { background-color: #1b4d22; color: #e8f5e9; border: 1px solid #2e7d32; }
                #leftFixBtn:hover { background-color: #225c29; }
                
                #rightFixBtn { background-color: #611a15; color: #ffebee; border: 1px solid #c62828; }
                #rightFixBtn:hover { background-color: #73211b; }
                
                #bottomFixBtn { background-color: #0d3a5f; color: #e3f2fd; border: 1px solid #1565c0; }
                #bottomFixBtn:hover { background-color: #124d7d; }
                
                #topFixBtn { background-color: #524705; color: #fffde7; border: 1px solid #f9a825; }
                #topFixBtn:hover { background-color: #635608; }
                
                /* Скролбари (Scroll Bars) */
                QScrollBar:vertical {
                    background-color: #1e1e1e;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #424242;
                    min-height: 20px;
                    border-radius: 6px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #4f4f4f;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none; background: none;
                }
            """)
        else:
            self.setStyleSheet("""
                /* Головне вікно та загальні налаштування тексту */
                QMainWindow { 
                    background-color: #f3f3f3; 
                }
                QWidget { 
                    color: #242424; 
                    font-family: 'Segoe UI', -apple-system, sans-serif; 
                    font-size: 12px;
                }
                
                /* Скрол-зона та панель керування */
                QScrollArea {
                    border: none;
                    background-color: #ffffff;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: #ffffff;
                }

                /* Контейнери (Group Boxes) */
                QGroupBox { 
                    font-weight: bold; 
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    color: #005fb8;
                    border: 1px solid #d2d2d2; 
                    border-radius: 6px;
                    margin-top: 15px; 
                    padding-top: 15px; 
                    padding-left: 10px;
                    padding-right: 10px;
                    padding-bottom: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 10px;
                    padding: 0 5px;
                    background-color: #ffffff;
                }

                /* Кнопки загальні */
                QPushButton { 
                    background-color: #fbfbfb; 
                    border: 1px solid #cccccc; 
                    color: #242424;
                    padding: 8px 12px; 
                    border-radius: 4px; 
                    font-weight: 500;
                }
                QPushButton:hover { 
                    background-color: #f5f5f5; 
                    border-color: #005fb8;
                }
                QPushButton:pressed {
                    background-color: #e5e5e5;
                }
                QPushButton:disabled {
                    background-color: #eaeaea;
                    color: #a1a1a1;
                    border-color: #e0e0e0;
                }

                /* Поля введення розмірів дверного полотна (Line Edits) */
                QLineEdit { 
                    background-color: #ffffff; 
                    border: 1px solid #cccccc; 
                    color: #000000; 
                    padding: 6px; 
                    border-radius: 4px; 
                    selection-background-color: #b1d7f7;
                }
                QLineEdit:focus {
                    border: 1px solid #005fb8;
                    background-color: #ffffff;
                }
                QLineEdit::placeholder {
                    color: #a1a1a1;
                }

                /* Інженерні списки (Елементи та Зони дверей) */
                QListWidget { 
                    background-color: #ffffff; 
                    border: 1px solid #cccccc; 
                    border-radius: 4px;
                    color: #242424; 
                    padding: 5px;
                }
                QListWidget::item {
                    padding: 6px;
                    border-bottom: 1px solid #eaeaea;
                    border-radius: 2px;
                }
                QListWidget::item:hover {
                    background-color: #f3f3f3;
                    color: #000000;
                }
                QListWidget::item:selected { 
                    background-color: #b1d7f7; 
                    color: #000000; 
                }

                /* Випадні списки (Теми) */
                QComboBox { 
                    background-color: #ffffff; 
                    border: 1px solid #cccccc; 
                    border-radius: 4px;
                    padding: 5px 10px; 
                    color: #242424; 
                }
                QComboBox:hover {
                    border-color: #005fb8;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    selection-background-color: #b1d7f7;
                }

                /* Слайдери розтягування зон (Sliders) */
                QSlider::groove:horizontal { 
                    border: 1px solid #cccccc; 
                    height: 6px; 
                    background: #eaeaea; 
                    border-radius: 3px; 
                }
                QSlider::sub-page:horizontal {
                    background: #005fb8;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal { 
                    background: #005fb8; 
                    width: 16px; 
                    height: 16px;
                    margin-top: -5px; 
                    margin-bottom: -5px;
                    border-radius: 8px; 
                }
                QSlider::handle:horizontal:hover {
                    background: #0078d4;
                }
                QSlider::handle:horizontal:disabled {
                    background: #cccccc;
                }

                /* Кастомні кнопки швидкої фіксації завіс/замків */
                #leftFixBtn { background-color: #e8f5e9; color: #1b4d22; border: 1px solid #a5d6a7; }
                #leftFixBtn:hover { background-color: #c8e6c9; }
                
                #rightFixBtn { background-color: #ffebee; color: #611a15; border: 1px solid #ef9a9a; }
                #rightFixBtn:hover { background-color: #ffcdd2; }
                
                #bottomFixBtn { background-color: #e3f2fd; color: #0d3a5f; border: 1px solid #90caf9; }
                #bottomFixBtn:hover { background-color: #bbdefb; }
                
                #topFixBtn { background-color: #fffde7; color: #524705; border: 1px solid #fff59d; }
                #topFixBtn:hover { background-color: #fff9c4; }
                
                /* Скролбари (Scroll Bars) */
                QScrollBar:vertical {
                    background-color: #f3f3f3;
                    width: 12px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background-color: #cccccc;
                    min-height: 20px;
                    border-radius: 6px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #b3b3b3;
                }
                QScrollBar:vertical, QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none; background: none;
                }
            """)


    def create_rigid_group(self):
        if len(self.selected_handles) < 2:
            return  
            
        # Видаляємо деталі зі старих груп, якщо вони там були
        self.rigid_groups = [g for g in self.rigid_groups if not g.intersection(self.selected_handles)]
        
        # Створюємо нову групу
        self.rigid_groups.append(set(self.selected_handles))
        self.clear_selection()
        self.push_to_history()
        self.update_viewer()
        self.load_groups_into_list()


    def toggle_stretchable(self):
        if not self.selected_handles: 
            return
            
        # Працює як перемикач (вмикає/вимикає еластичність)
        if not self.selected_handles.issubset(self.stretchable_handles):
            self.stretchable_handles.update(self.selected_handles)
        else:
            self.stretchable_handles.difference_update(self.selected_handles)
            
        self.push_to_history()
        self.update_viewer()

    def load_groups_into_list(self):
        self.group_list_widget.blockSignals(True)
        self.group_list_widget.clear()
        for idx, group in enumerate(getattr(self, 'rigid_groups', [])):
            item = QListWidgetItem(f"🧩 Група №{idx+1} (Деталей: {len(group)})")
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.group_list_widget.addItem(item)
        self.group_list_widget.blockSignals(False)

    def get_rigid_group_shift(self, hndl):
        for group in getattr(self, 'rigid_groups', []):
            if hndl in group:
                min_x, max_x = float('inf'), float('-inf')
                min_y, max_y = float('inf'), float('-inf')

                for g_hndl in group:
                    if g_hndl not in self.original_geometries: continue
                    orig = self.original_geometries[g_hndl]
                    if orig['type'] in ('CIRCLE', 'ARC'):
                        cx, cy, _ = orig['center']
                        r = orig['radius']
                        min_x = min(min_x, cx - r); max_x = max(max_x, cx + r)
                        min_y = min(min_y, cy - r); max_y = max(max_y, cy + r)
                    elif orig['type'] == 'LINE':
                        sx, sy, _ = orig['start']
                        ex, ey, _ = orig['end']
                        min_x = min(min_x, sx, ex); max_x = max(max_x, sx, ex)
                        min_y = min(min_y, sy, ey); max_y = max(max_y, sy, ey)

                if min_x != float('inf'):
                    gcx = (min_x + max_x) / 2.0
                    gcy = (min_y + max_y) / 2.0
                    shift_x = self.calculate_cascade_shift(gcx, 'X', hndl) - gcx
                    shift_y = self.calculate_cascade_shift(gcy, 'Y', hndl) - gcy
                    return shift_x, shift_y
        return None

    def on_group_list_selection(self):
        selected = self.group_list_widget.selectedItems()
        if not selected: 
            return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
    
        self.selected_handles = set(self.rigid_groups[idx])
        self.sync_list_from_handles()
        self.update_viewer()

    def disband_group(self):
        selected = self.group_list_widget.selectedItems()
        if not selected: 
            return
        idx = selected[0].data(Qt.ItemDataRole.UserRole)
        del self.rigid_groups[idx]  
        self.clear_selection()
        self.push_to_history()
        self.update_viewer()
        self.load_groups_into_list()



    def smart_auto_detect_zones(self):
        self.stretch_zones.clear() 
        
        
        self._calculate_axis_gaps('X')
        self._calculate_axis_gaps('Y')
        
        self.active_zone_index = None
        self.load_zones_into_list()
        self.push_to_history()
        self.update_viewer()

    def _calculate_axis_gaps(self, axis):
        intervals = []
        
        # Створюємо набір усіх handles, які входять до будь-якої жорсткої групи
        all_grouped_handles = set()
        for group in getattr(self, 'rigid_groups', []):
            all_grouped_handles.update(group)

        # Збираємо інші поодинокі фіксації сторін
        explicit_obstacles = set()
        explicit_obstacles.update(self.left_fixed_handles)
        explicit_obstacles.update(self.right_fixed_handles)
        explicit_obstacles.update(self.bottom_fixed_handles)
        explicit_obstacles.update(self.top_fixed_handles)

        # Absolute межі всього креслення для "віртуальних стін"
        abs_min = float('inf')
        abs_max = float('-inf')

        # ---------------------------------------------------------------------------
        # 🧱 КРОК 1: Обчислюємо загальні габарити для кожної ЖОРСТКОЇ ГРУПИ
        # ---------------------------------------------------------------------------
        for group in getattr(self, 'rigid_groups', []):
            g_min = float('inf')
            g_max = float('-inf')
            
            for hndl in group:
                if hndl not in self.original_geometries: continue
                orig = self.original_geometries[hndl]
                
                if orig['type'] == 'LINE':
                    sx, sy = orig['start'][0], orig['start'][1]
                    ex, ey = orig['end'][0], orig['end'][1]
                    length = math.sqrt((ex - sx)**2 + (ey - sy)**2)
                    is_stretchable = hasattr(self, 'stretchable_handles') and hndl in self.stretchable_handles
                    
                
                    if is_stretchable:
                        dx = abs(ex - sx)
                        dy = abs(ey - sy)
                        if axis == 'X' and dx > dy: continue  
                        if axis == 'Y' and dy > dx: continue  
                        
                    if length > 350.0:
                        continue
                
                if orig['type'] in ('CIRCLE', 'ARC'):
                    c_val = orig['center'][0] if axis == 'X' else orig['center'][1]
                    r = orig['radius']
                    g_min = min(g_min, c_val - r)
                    g_max = max(g_max, c_val + r)
                elif orig['type'] == 'LINE':
                    v1 = orig['start'][0] if axis == 'X' else orig['start'][1]
                    v2 = orig['end'][0] if axis == 'X' else orig['end'][1]
                    g_min = min(g_min, v1, v2)
                    g_max = max(g_max, v1, v2)
            
            if g_min != float('inf'):
                intervals.append([g_min, g_max])
                abs_min = min(abs_min, g_min)
                abs_max = max(abs_max, g_max)

        for entity in self.doc.modelspace():
            hndl = entity.dxf.handle
            e_type = entity.dxftype()
            
            if hndl in all_grouped_handles:
                continue
            
            if e_type == "LINE":
                x1, y1 = entity.dxf.start[0], entity.dxf.start[1]
                x2, y2 = entity.dxf.end[0], entity.dxf.end[1]
                
                v1 = x1 if axis == 'X' else y1
                v2 = x2 if axis == 'X' else y2
                abs_min = min(abs_min, v1, v2)
                abs_max = max(abs_max, v1, v2)

                length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                is_stretchable = hasattr(self, 'stretchable_handles') and hndl in self.stretchable_handles
                
                dx = abs(x2 - x1)
                dy = abs(y2 - y1)
                
     
                if axis == 'X':
                    if dx > dy and length > 100.0: continue
                elif axis == 'Y':
                    if dy > dx: continue

               
                if is_stretchable:
                    if axis == 'X' and dx > dy: continue
                    if axis == 'Y' and dy > dx: continue
                    
                if length > 350.0 and hndl not in explicit_obstacles:
                    continue
                    
                intervals.append([min(v1, v2), max(v1, v2)])
                
            elif e_type in ("CIRCLE", "ARC"):
                c_val = entity.dxf.center[0] if axis == 'X' else entity.dxf.center[1]
                r = entity.dxf.radius
                
                abs_min = min(abs_min, c_val - r)
                abs_max = max(abs_max, c_val + r)
                
                intervals.append([c_val - r, c_val + r])

       
        if abs_min != float('inf'):
            intervals.append([abs_min - 1.0, abs_min])
            intervals.append([abs_max, abs_max + 1.0])

        if not intervals: return

   
        intervals.sort(key=lambda x: x[0])
        merged = [intervals[0]]
        for current in intervals[1:]:
            last = merged[-1]
            if current[0] <= last[1] + 2.0: 
                last[1] = max(last[1], current[1])
            else:
                merged.append(current)

     
        for i in range(len(merged) - 1):
            gap_start = merged[i][1]
            gap_end = merged[i+1][0]
            gap_width = gap_end - gap_start

            if gap_width >= 100.0:
                safe_start = gap_start + 15.0
                safe_end = gap_end - 15.0
                if safe_end > safe_start:
                    self.add_or_update_zone_bounds(safe_start, safe_end, axis)


    def save_zones_history_state(self):
        state_snapshot = {
            "stretch_zones": copy.deepcopy(self.stretch_zones),
            "left_fixed": copy.deepcopy(self.left_fixed_handles),
            "right_fixed": copy.deepcopy(self.right_fixed_handles),
            "bottom_fixed": copy.deepcopy(self.bottom_fixed_handles),
            "top_fixed": copy.deepcopy(self.top_fixed_handles),
            "rigid_blocks": copy.deepcopy(self.rigid_blocks),
            "rigid_groups": copy.deepcopy(self.rigid_groups),
            "stretchable": copy.deepcopy(self.stretchable_handles)
        }
        self.zones_undo_stack.append(state_snapshot)
        if len(self.zones_undo_stack) > 30:
            self.zones_undo_stack.pop(0)


    def create_rigid_block(self):
        if len(self.selected_handles) < 2:
            return 
            

        self.rigid_blocks = [b for b in self.rigid_blocks if not b.intersection(self.selected_handles)]
        
      
        self.rigid_blocks.append(set(self.selected_handles))
        self.clear_selection()
        self.push_to_history()
        self.update_viewer()


    def get_rigid_block_shift(self, hndl):
        for block in self.rigid_blocks:
            if hndl in block:
              
                min_x, max_x = float('inf'), float('-inf')
                min_y, max_y = float('inf'), float('-inf')

                for b_hndl in block:
                    if b_hndl not in self.original_geometries: continue
                    orig = self.original_geometries[b_hndl]
                    if orig['type'] in ('CIRCLE', 'ARC'):
                        cx, cy, _ = orig['center']
                        r = orig['radius']
                        min_x = min(min_x, cx - r); max_x = max(max_x, cx + r)
                        min_y = min(min_y, cy - r); max_y = max(max_y, cy + r)
                    elif orig['type'] == 'LINE':
                        sx, sy, _ = orig['start']
                        ex, ey, _ = orig['end']
                        min_x = min(min_x, sx, ex); max_x = max(max_x, sx, ex)
                        min_y = min(min_y, sy, ey); max_y = max(max_y, sy, ey)

                if min_x != float('inf'):
                    # Спільний центр усього блоку
                    bcx = (min_x + max_x) / 2.0
                    bcy = (min_y + max_y) / 2.0
                    
                    # Розраховуємо, наскільки зсунеться цей центр
                    shift_x = self.calculate_cascade_shift(bcx, 'X', hndl) - bcx
                    shift_y = self.calculate_cascade_shift(bcy, 'Y', hndl) - bcy
                    return shift_x, shift_y
        return None

    def open_dxf_file(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Відкрити DXF файл", "", "DXF Files (*.dxf)")
        if file_path:
            self.dxf_path = file_path
            self.project_dir = os.path.dirname(file_path)
            self.doc = ezdxf.readfile(file_path)
            self.selected_handles.clear()
            self.stretch_zones.clear()
            self.active_zone_index = None
            self.apply_ezdxf_patch()
            self.save_original_geometries()
            self.scan_project_folder_for_dxf() 
            self.update_viewer()
            self.load_entities_into_list()

    def on_zone_selection_changed(self):
        selected = self.zone_list_widget.selectedItems()
        if not selected:
            self.active_zone_index = None
            self.slider.setEnabled(False)
            return
        self.active_zone_index = selected[0].data(Qt.ItemDataRole.UserRole)
        zone = self.stretch_zones[self.active_zone_index]
        self.slider.blockSignals(True)
        self.slider.setEnabled(True)
        self.slider.setValue(int(zone['stretch_val']))
        self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {zone['stretch_val']:.0f} мм")
        self.slider.blockSignals(False)
        self.update_viewer()

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
            self.stretch_zones = copy.deepcopy(previous_snapshot["stretch_zones"])
            self.left_fixed_handles = copy.deepcopy(previous_snapshot["left_fixed"])
            self.right_fixed_handles = copy.deepcopy(previous_snapshot["right_fixed"])
            self.bottom_fixed_handles = copy.deepcopy(previous_snapshot["bottom_fixed"])
            self.top_fixed_handles = copy.deepcopy(previous_snapshot["top_fixed"])
            self.rigid_blocks = copy.deepcopy(previous_snapshot["rigid_blocks"])
            self.reload_after_history_change()

    def redo(self):
        if self.history.redo() and self.zones_redo_stack:
            next_snapshot = self.zones_redo_stack.pop()
            self.zones_undo_stack.append(next_snapshot)
            self.stretch_zones = copy.deepcopy(next_snapshot["stretch_zones"])
            self.left_fixed_handles = copy.deepcopy(next_snapshot["left_fixed"])
            self.right_fixed_handles = copy.deepcopy(next_snapshot["right_fixed"])
            self.bottom_fixed_handles = copy.deepcopy(next_snapshot["bottom_fixed"])
            self.top_fixed_handles = copy.deepcopy(next_snapshot["top_fixed"])
            self.rigid_blocks = copy.deepcopy(next_snapshot["rigid_blocks"])
            self.reload_after_history_change()

    def update_history_buttons_state(self):
        self.btn_undo.setEnabled(len(self.history.undo_stack) > 1 and len(self.zones_undo_stack) > 1)
        self.btn_redo.setEnabled(len(self.history.redo_stack) > 0 and len(self.zones_redo_stack) > 0)

    def reload_after_history_change(self):
        self.is_loading_history = True
        self.doc = ezdxf.readfile(self.dxf_path)
        self.save_original_geometries()
        for zone in self.stretch_zones: 
            zone['stretch_val'] = 0.0
        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)
        self.update_viewer()
        self.load_zones_into_list()
        self.load_entities_into_list()
        self.update_history_buttons_state()
        self.slider_label.setText("Оберіть зону деформації зі списку")
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
        
        # 1. ЗАЛИЗОВОБЕТОННЕ ОЧИЩЕННЯ
        self.selected_handles.clear()
        self.reset_all_parametric_zones()  # Очищує зони, слайдери, списки та фіксатори
        self.rigid_blocks = []             # Очищуємо жорсткі групи
        self.rigid_groups = []             # Очищуємо жорсткі групи
        self.stretchable_handles.clear()   # Очищуємо еластичність
        
        # 2. Вибір файлу
        base_file_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.dxf_path = os.path.join(self.project_dir, base_file_name)
        self.doc = ezdxf.readfile(self.dxf_path)

        # 3. Імпорт додаткових файлів (якщо вибрано кілька)
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
                    except Exception as e:
                        print(f"Помилка злиття файлу {addon_file_name}: {e}")

        # 4. Ініціалізація нового стану
        self.apply_ezdxf_patch()
        self.history = HistoryManager(self.dxf_path)
        self.history.save_state()
        self.zones_undo_stack.clear()
        self.zones_redo_stack.clear()
        self.save_zones_history_state()
        
        self.save_original_geometries()
        self.update_viewer()
        self.load_entities_into_list()
        self.load_groups_into_list() # Оновлюємо порожній список груп
        self.update_history_buttons_state()
        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>Завантажено: {base_file_name}</font>")

    # ---------------------------------------------------------------------------
    # 💾 ЗБЕРЕЖЕННЯ ОРИГІНАЛЬНИХ ГЕОМЕТРІЙ (ДОДАНО ARC)
    # ---------------------------------------------------------------------------
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
                # Фіксуємо початковий стан дуги
                self.original_geometries[hndl] = {
                    "type": "ARC", 
                    "center": entity.dxf.center, 
                    "radius": entity.dxf.radius,
                    "start_angle": entity.dxf.start_angle,
                    "end_angle": entity.dxf.end_angle
                }
        self.update_auto_line_clusters()

    # ---------------------------------------------------------------------------
    # 🚀 ПАРАМЕТРИЧНА АДАПТАЦІЯ ТА ОБЧИСЛЕННЯ (МАСШТАБУВАННЯ ДУГ)
    # ---------------------------------------------------------------------------
    def process_manual_input_dimension_scale(self):
        if not self.stretch_zones:
            self.lbl_status_calc.setText("<font color='red'>Помилка: Створіть області розтягування!</font>")
            return

        cur_w = self.input_current_width.text().strip()
        new_w = self.input_target_width.text().strip()
        cur_h = self.input_current_height.text().strip()
        new_h = self.input_target_height.text().strip()

        delta_x = float(new_w) - float(cur_w) if (cur_w and new_w) else 0.0
        delta_y = float(new_h) - float(cur_h) if (cur_h and new_h) else 0.0

        if delta_x == 0.0 and delta_y == 0.0:
            return

        count_zones_x = sum(1 for z in self.stretch_zones if z['axis'] == 'X')
        count_zones_y = sum(1 for z in self.stretch_zones if z['axis'] == 'Y')

        share_delta_x = delta_x / count_zones_x if count_zones_x > 0 else 0.0
        share_delta_y = delta_y / count_zones_y if count_zones_y > 0 else 0.0

        for zone in self.stretch_zones:
            if zone['axis'] == 'X': zone['stretch_val'] = share_delta_x
            elif zone['axis'] == 'Y': zone['stretch_val'] = share_delta_y

        for hndl, orig in self.original_geometries.items():
            if hndl not in self.doc.entitydb: continue
            entity = self.doc.entitydb[hndl]
            
            # Перевіряємо, чи належить деталь до якогось блоку
            block_shift = self.get_rigid_group_shift(hndl)

            if orig["type"] in ("CIRCLE", "ARC"):
                cx, cy, cz = orig["center"]
                if block_shift:
                    # Монолітний зсув у складі блоку
                    entity.dxf.center = (cx + block_shift[0], cy + block_shift[1], cz)
                else:
                    # Стандартний зсув окремого елемента
                    entity.dxf.center = (
                        self.calculate_cascade_shift(cx, 'X', hndl), 
                        self.calculate_cascade_shift(cy, 'Y', hndl), 
                        cz
                    )
            elif orig["type"] == "LINE":
                sx, sy, sz = orig["start"]
                ex, ey, ez = orig["end"]
                
                # Перевіряємо, чи дозволив користувач розтягувати цю лінію
                is_stretchable = hasattr(self, 'stretchable_handles') and hndl in self.stretchable_handles
                
                # Якщо лінія в групі, і вона НЕ еластична -> зміщуємо монолітно (як частину замка/фурнітури)
                if block_shift and not is_stretchable:
                    entity.dxf.start = (sx + block_shift[0], sy + block_shift[1], sz)
                    entity.dxf.end = (ex + block_shift[0], ey + block_shift[1], ez)
                # Якщо лінія еластична (навіть якщо в групі!) АБО не в групі -> віддаємо алгоритму розтягування
                else:
                    new_start, new_end = self.get_line_shifted_coords(sx, sy, sz, ex, ey, ez, hndl)
                    entity.dxf.start = new_start
                    entity.dxf.end = new_end

        self.lbl_status_calc.setText(f"<font color='#a5d6a7'>ΔX={delta_x:+.2f}мм | ΔY={delta_y:+.2f}мм</font>")
        self.doc.saveas(self.dxf_path)
        
        for zone in self.stretch_zones:
            stretch_amount = zone['stretch_val']
            if stretch_amount == 0: continue
            active_axis = zone['axis']
            active_max = zone['max']
            zone['max'] += stretch_amount
            for sub_z in self.stretch_zones:
                if sub_z == zone or sub_z['axis'] != active_axis: continue
                if sub_z['min'] >= active_max:
                    sub_z['min'] += stretch_amount
                    sub_z['max'] += stretch_amount

        for zone in self.stretch_zones: 
            zone['stretch_val'] = 0.0

        self.push_to_history()
        self.input_current_width.clear()
        self.input_target_width.clear()
        self.input_current_height.clear()
        self.input_target_height.clear()
        self.load_zones_into_list()
        self.load_entities_into_list()
        self.update_viewer()

    def transform_selected_entities(self, mode):
        if not self.selected_handles: return
        selected_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
        if not selected_entities: return

        cx = sum((e.left_x + e.right_x) / 2 for e in selected_entities) / len(selected_entities)
        cy = sum((e.bottom_y + e.top_y) / 2 for e in selected_entities) / len(selected_entities)

        for entity in selected_entities:
            if mode == "ROT90":
                m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(90)), Matrix44.translate(cx, cy, 0))
            elif mode == "ROT180":
                m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.z_rotate(math.radians(180)), Matrix44.translate(cx, cy, 0))
            elif mode == "MIRROR_H":
                m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(-1, 1, 1), Matrix44.translate(cx, cy, 0))
            elif mode == "MIRROR_V":
                m = Matrix44.chain(Matrix44.translate(-cx, -cy, 0), Matrix44.scale(1, -1, 1), Matrix44.translate(cx, cy, 0))
            else: continue
            entity.transform(m)

        self.doc.saveas(self.dxf_path)
        self.push_to_history()
        self.update_viewer()
        self.load_entities_into_list()

    def assign_to_left_fix(self):
        self.left_fixed_handles.update(self.selected_handles)
        self.right_fixed_handles.difference_update(self.selected_handles)
        self.auto_detect_between_zone('X')
        self.push_to_history()
        self.update_viewer()
        self.load_entities_into_list()

    def assign_to_right_fix(self):
        self.right_fixed_handles.update(self.selected_handles)
        self.left_fixed_handles.difference_update(self.selected_handles)
        self.auto_detect_between_zone('X')
        self.push_to_history()
        self.update_viewer()
        self.load_entities_into_list()

    def assign_to_bottom_fix(self):
        self.bottom_fixed_handles.update(self.selected_handles)
        self.top_fixed_handles.difference_update(self.selected_handles)
        self.auto_detect_between_zone('Y')
        self.push_to_history()
        self.update_viewer()
        self.load_entities_into_list()

    def assign_to_top_fix(self):
        self.top_fixed_handles.update(self.selected_handles)
        self.bottom_fixed_handles.difference_update(self.selected_handles)
        self.auto_detect_between_zone('Y')
        self.push_to_history()
        self.update_viewer()
        self.load_entities_into_list()

    
    def reset_all_parametric_zones(self):
        self.left_fixed_handles.clear()
        self.right_fixed_handles.clear()
        self.bottom_fixed_handles.clear()
        self.top_fixed_handles.clear()
        self.stretch_zones.clear()
        self.active_zone_index = None
        self.slider.setEnabled(False)
        self.slider_label.setText("Оберіть зону деформації зі списку")
        self.update_viewer()
        self.load_zones_into_list()
        self.load_entities_into_list()

    def create_zone_from_selection(self, axis):
        if not self.selected_handles or not self.original_geometries: return
        active_entities = [self.doc.entitydb[h] for h in self.selected_handles if h in self.doc.entitydb]
        if not active_entities or len(active_entities) < 2: 
            self.clear_selection()
            return
        if axis == 'X':
            min_val = max(e.right_x for e in active_entities if e.right_x < max(el.left_x for el in active_entities))
            max_val = min(e.left_x for e in active_entities if e.left_x > min(el.right_x for el in active_entities))
        else:
            min_val = max(e.top_y for e in active_entities if e.top_y < max(el.bottom_y for el in active_entities))
            max_val = min(e.bottom_y for e in active_entities if e.bottom_y > min(e_el.top_y for e_el in active_entities))
        if max_val > min_val and (max_val - min_val) > 2.0:
            self.add_or_update_zone_bounds(min_val, max_val, axis)
            self.push_to_history() 
        self.clear_selection()

    def process_manual_rubber_band(self, rect):
        modifiers = QGuiApplication.keyboardModifiers()
        is_ctrl_pressed = (modifiers & Qt.ControlModifier)
        if not is_ctrl_pressed:
            self.selected_handles.clear()
                
        path = QPainterPath()
        path.addRect(rect)
        matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
        
        found_any = False
        for item in matched_items:
            hndl = item.data(Qt.ItemDataRole.UserRole)
            if hndl:
                self.selected_handles.add(hndl)
                found_any = True
                    
        if found_any:
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

    # ---------------------------------------------------------------------------
    # СИНХРОННИЙ ЗСУВ СЛАЙДЕРА (ПІДТРИМКА ARC)
    # ---------------------------------------------------------------------------
    def on_slider_value_changed(self, value):
        if self.active_zone_index is None or self.is_loading_history:
            return

        self.stretch_zones[self.active_zone_index]['stretch_val'] = float(value)
        zone = self.stretch_zones[self.active_zone_index]
        self.slider_label.setText(f"Розтягування зони №{self.active_zone_index+1} ({zone['axis']}) на: {value} мм")

        for hndl, orig in self.original_geometries.items():
            if hndl not in self.doc.entitydb: continue
            entity = self.doc.entitydb[hndl]
            
            # Перевіряємо, чи належить деталь до якогось блоку
            block_shift = self.get_rigid_group_shift(hndl)

            if orig["type"] in ("CIRCLE", "ARC"):
                cx, cy, cz = orig["center"]
                if block_shift:
                    # Монолітний зсув у складі блоку
                    entity.dxf.center = (cx + block_shift[0], cy + block_shift[1], cz)
                else:
                    # Стандартний зсув окремого елемента
                    entity.dxf.center = (
                        self.calculate_cascade_shift(cx, 'X', hndl), 
                        self.calculate_cascade_shift(cy, 'Y', hndl), 
                        cz
                    )
            elif orig["type"] == "LINE":
                sx, sy, sz = orig["start"]
                ex, ey, ez = orig["end"]
                
      
                is_stretchable = hasattr(self, 'stretchable_handles') and hndl in self.stretchable_handles
                
              
                if block_shift and not is_stretchable:
                    entity.dxf.start = (sx + block_shift[0], sy + block_shift[1], sz)
                    entity.dxf.end = (ex + block_shift[0], ey + block_shift[1], ez)
               
                else:
                    new_start, new_end = self.get_line_shifted_coords(sx, sy, sz, ex, ey, ez, hndl)
                    entity.dxf.start = new_start
                    entity.dxf.end = new_end
        self.update_viewer()

    def calculate_cascade_shift(self, orig_val, axis, hndl=None):
        if axis == 'X' and hndl:
            if hndl in self.left_fixed_handles: return orig_val
            if hndl in self.right_fixed_handles:
                return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'X')
        elif axis == 'Y' and hndl:
            if hndl in self.bottom_fixed_handles: return orig_val
            if hndl in self.top_fixed_handles:
                return orig_val + sum(z['stretch_val'] for z in self.stretch_zones if z['axis'] == 'Y')

        shifted_val = orig_val
        for zone in self.stretch_zones:
            if zone['axis'] != axis: continue
            z_min = zone['min']
            z_max = zone['max']
            val = zone['stretch_val']

            if orig_val >= z_max:
                shifted_val += val
            elif z_min <= orig_val < z_max:
                # 🚀 ШУКАЄМО ЕЛАСТИЧНИЙ "ПОРШЕНЬ" У ЦІЙ ЗОНІ
                elastic_center = None
                for s_hndl in getattr(self, 'stretchable_handles', set()):
                    if s_hndl not in self.original_geometries: continue
                    orig = self.original_geometries[s_hndl]
                    if orig['type'] == 'LINE':
                        lx1, ly1 = orig['start'][0], orig['start'][1]
                        lx2, ly2 = orig['end'][0], orig['end'][1]
                        
                        if axis == 'X':
                            cx = (lx1 + lx2) / 2.0
                            # Перевіряємо, чи горизонтальна еластична лінія лежить у цій X-зоні
                            if z_min <= cx <= z_max and abs(lx2 - lx1) > abs(ly2 - ly1):
                                elastic_center = cx
                                break
                        elif axis == 'Y':
                            cy = (ly1 + ly2) / 2.0
                            # Перевіряємо, чи вертикальна еластична лінія лежить у цій Y-зони
                            if z_min <= cy <= z_max and abs(ly2 - ly1) > abs(lx2 - lx1):
                                elastic_center = cy
                                break
                
                if elastic_center is not None:
                    # 🎯 ПОРШЕНЬ ЗНАЙДЕНО: усе, що за його центром, отримує 100% приріст
                    if orig_val >= elastic_center:
                        shifted_val += val
                else:
                    # Якщо еластичної лінії немає (порожня зона), залишаємо пропорційний розподіл
                    width = z_max - z_min
                    if width > 0:
                        ratio = (orig_val - z_min) / width
                        shifted_val += val * ratio
                        
        return shifted_val

    def on_slider_released(self):
        self.doc.saveas(self.dxf_path)
        active_zone = self.stretch_zones[self.active_zone_index]
        stretch_amount = active_zone['stretch_val']
        active_axis = active_zone['axis']
        active_max = active_zone['max']
        active_zone['max'] += stretch_amount

        for idx, zone in enumerate(self.stretch_zones):
            if idx == self.active_zone_index or zone['axis'] != active_axis:
                continue
            if zone['min'] >= active_max:
                zone['min'] += stretch_amount
                zone['max'] += stretch_amount

        for zone in self.stretch_zones: zone['stretch_val'] = 0.0

        self.push_to_history()
        self.save_original_geometries()

        self.slider.blockSignals(True)
        self.slider.setValue(0)
        self.slider.blockSignals(False)

        self.load_zones_into_list()
        self.load_entities_into_list()
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

    # ---------------------------------------------------------------------------
    # ТЕКСТОВИЙ СПИСОК ЕЛЕМЕНТІВ (ДОДАНО ВАРІАНТ ДЛЯ ARC)
    # ---------------------------------------------------------------------------
    def load_entities_into_list(self):
        self.entity_list.blockSignals(True)
        self.entity_list.clear()
        seen = set()
        for entity in self.doc.modelspace():
            tp = entity.dxftype()
            hndl = entity.dxf.handle
            if tp == "CIRCLE":
                cx, cy, _ = entity.dxf.center
                if (round(cx, 2), round(cy, 2)) in seen: continue
                seen.add((round(cx, 2), round(cy, 2)))
                text = f"🔘 Отвір (ID: {hndl}) Центр X:{cx:.2f}, Y:{cy:.2f}"
            elif tp == "LINE":
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                if (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)) in seen: continue
                seen.add((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
                text = f"📏 Лінія (ID: {hndl}) Довжина: {math.sqrt((x2 - x1)**2 + (y2 - y1)**2):.2f} мм. Початок: ({x1:.2f}, {y1:.2f}), Кінець: ({x2:.2f}, {y2:.2f})"
            elif tp == "ARC":
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                if (round(cx, 2), round(cy, 2), round(r, 2)) in seen: continue
                seen.add((round(cx, 2), round(cy, 2), round(r, 2)))
                text = f"🌙 Дуга/Арка (ID: {hndl}) Центр X:{cx:.2f}, Y:{cy:.2f}, R:{r:.1f}"
            else: continue
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, hndl)
            self.entity_list.addItem(item)
        self.entity_list.blockSignals(False)


    def update_viewer(self):
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.overlay_items.clear()

        if self.current_theme == "Темна":
            self.view.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
            base_line_color = QColor(220, 220, 220)
        else:
            self.view.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
            base_line_color = QColor(80, 80, 80)

        length = 150.0 
        self.scene.addLine(-length, 0, length, 0, QPen(QColor(33, 150, 243), 2.5))
        self.scene.addLine(0, length, 0, -length, QPen(QColor(76, 175, 80), 2.5))

        marker = QGraphicsEllipseItem(-2, -2, 4, 4) 
        marker.setBrush(QBrush(QColor("red")))
        self.scene.addItem(marker)

        try:
            bounds = dxf_bbox.extents(self.doc.modelspace())
            abs_min_x, abs_max_x = bounds.extmin[0] - 50.0, bounds.extmax[0] + 50.0
            abs_min_y, abs_max_y = bounds.extmin[1] - 50.0, bounds.extmax[1] + 50.0
        except Exception:
            abs_min_x, abs_max_x = -100.0, 1000.0
            abs_min_y, abs_max_y = -100.0, 2000.0


        # Малюємо напівпрозорі рамки навколо жорстких груп
        for idx, group in enumerate(getattr(self, 'rigid_groups', [])):
            g_min_x, g_max_x = float('inf'), float('-inf')
            g_min_y, g_max_y = float('inf'), float('-inf')

            for hndl in group:
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
                pad = 5.0
                rect_item = QGraphicsRectItem(g_min_x - pad, -(g_max_y + pad), (g_max_x - g_min_x) + pad*2, (g_max_y - g_min_y) + pad*2)
                
                is_selected = self.group_list_widget.currentItem() and self.group_list_widget.currentItem().data(Qt.ItemDataRole.UserRole) == idx
                
                if is_selected:
                    rect_item.setBrush(QBrush(QColor(103, 58, 183, 50)))
                    rect_item.setPen(QPen(QColor(103, 58, 183, 200), 2, Qt.PenStyle.SolidLine))
                else:
                    rect_item.setBrush(QBrush(QColor(103, 58, 183, 15)))
                    rect_item.setPen(QPen(QColor(103, 58, 183, 120), 1, Qt.PenStyle.DashLine))
                    
                self.scene.addItem(rect_item)

        for idx, zone in enumerate(self.stretch_zones):
            disp_min = self.calculate_cascade_shift(zone['min'], zone['axis'], None)
            disp_max = self.calculate_cascade_shift(zone['max'], zone['axis'], None) 
            if zone['axis'] == 'X':
                rect_item = QGraphicsRectItem(disp_min, -abs_max_y, (disp_max - disp_min), (abs_max_y - abs_min_y))
            else:
                rect_item = QGraphicsRectItem(abs_min_x, -disp_max, (abs_max_x - abs_min_x), (disp_max - disp_min))

            if idx == self.active_zone_index:
                color = QColor(0, 120, 255, 45) if zone['axis'] == 'X' else QColor(0, 200, 100, 45)
                rect_item.setBrush(QBrush(color))
                rect_item.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 150), 1.5, Qt.PenStyle.DashLine))
            else:
                rect_item.setBrush(QBrush(QColor(255, 152, 0, 20))) 
                rect_item.setPen(QPen(QColor(255, 152, 0, 60), 1, Qt.PenStyle.DotLine))
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
                
                # Колірне фарбування за статусом фіксації
                if hndl in self.selected_handles:
                    pen_style = QPen(QColor(0, 120, 255), 2)

                elif hndl in self.left_fixed_handles:
                    pen_style = QPen(QColor(46, 125, 50), 2)

                elif hndl in self.right_fixed_handles:
                    pen_style = QPen(QColor(198, 40, 40), 2)

                elif hndl in self.bottom_fixed_handles:
                    pen_style = QPen(QColor(21, 101, 192), 2)

                elif hndl in self.top_fixed_handles:
                    pen_style = QPen(QColor(249, 168, 37), 2)

                elif any(hndl in b for b in getattr(self, 'rigid_blocks', [])):
                    pen_style = QPen(QColor(103, 58, 183), 2) 

                elif hndl in getattr(self, 'stretchable_handles', set()):
                    pen_style = QPen(QColor(255, 152, 0), 2) 

                else:
                    pen_style = QPen(base_line_color, 2)
                
                pyqt_item.setPen(pen_style)
                pyqt_item.setData(Qt.ItemDataRole.UserRole, hndl)
                self.scene.addItem(pyqt_item)
                self.overlay_items[hndl] = pyqt_item

        self.view.setSceneRect(self.scene.itemsBoundingRect())

    def apply_ezdxf_patch(self):
        patch_ezdxf_entities()

    def on_scene_item_clicked(self, handle):
        modifiers = QGuiApplication.keyboardModifiers()
        is_ctrl_pressed = (modifiers & Qt.ControlModifier)
        if is_ctrl_pressed:
            if handle in self.selected_handles: self.selected_handles.remove(handle)
            else: self.selected_handles.add(handle)
        else:
            self.selected_handles = {handle}
        self.sync_list_from_handles()
        self.update_viewer()
        
    def load_zones_into_list(self):
        self.zone_list_widget.blockSignals(True)
        self.zone_list_widget.clear()
        for idx, zone in enumerate(self.stretch_zones):
            axis_icon = "↔️" if zone['axis'] == 'X' else "↕️"
            text = f"{axis_icon} Авто-зона {idx+1} [{zone['axis']}: {zone['min']:.2f} -> {zone['max']:.2f}] Довжина: {(zone['max'] - zone['min']):.2f} мм"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, idx)
            self.zone_list_widget.addItem(item)
        self.zone_list_widget.blockSignals(False)
    
    def add_or_update_zone_bounds(self, min_v, max_v, axis):
        for zone in self.stretch_zones:
            if zone['axis'] == axis and abs(zone['min'] - min_v) < 10.0: return
        new_zone = {'min': min_v, 'max': max_v, 'stretch_val': 0.0, 'axis': axis}
        self.stretch_zones.append(new_zone)
        self.stretch_zones.sort(key=lambda z: (z['axis'], z['min']))
        self.load_zones_into_list()
        for idx, zone in enumerate(self.stretch_zones):
            if zone['axis'] == axis and zone['min'] == min_v:
                self.zone_list_widget.setCurrentRow(idx)
                break


    def update_auto_line_clusters(self):
        self.line_cluster_centers = {} 
        self.line_clusters = [] # 💾 Додаємо список для зберігання множин дотичних ланцюжків
        lines = {}
        
        explicit_grouped = set()
        for group in getattr(self, 'rigid_groups', []):
            explicit_grouped.update(group)
            
        for hndl, orig in self.original_geometries.items():
            if orig['type'] == 'LINE' and hndl not in explicit_grouped:
                if hasattr(self, 'stretchable_handles') and hndl in self.stretchable_handles:
                    # Дозволяємо внутрішнім коротким еластичним лініям брати участь у кластері!
                    pass
                
                sx, sy = orig['start'][0], orig['start'][1]
                ex, ey = orig['end'][0], orig['end'][1]
                length = math.sqrt((ex - sx)**2 + (ey - sy)**2)
                if length > 350.0: # Виключаємо лише довгу зовнішню раму
                    continue
                lines[hndl] = orig

        def snap_pt(pt):
            return (round(pt[0], 2), round(pt[1], 2))

        pt_to_handles = {}
        for hndl, orig in lines.items():
            p1 = snap_pt(orig['start'])
            p2 = snap_pt(orig['end'])
            pt_to_handles.setdefault(p1, set()).add(hndl)
            pt_to_handles.setdefault(p2, set()).add(hndl)

        adj = {h: set() for h in lines}
        for hndls in pt_to_handles.values():
            for h1 in hndls:
                for h2 in hndls:
                    if h1 != h2:
                        adj[h1].add(h2)

        visited = set()
        for hndl in lines:
            if hndl not in visited:
                cluster = set()
                queue = [hndl]
                visited.add(hndl)
                while queue:
                    curr = queue.pop(0)
                    cluster.add(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

                if len(cluster) >= 2:
                    self.line_clusters.append(cluster) # Зберігаємо склад кластера
                    
                    min_x, max_x = float('inf'), float('-inf')
                    min_y, max_y = float('inf'), float('-inf')
                    for c_hndl in cluster:
                        orig = lines[c_hndl]
                        sx, sy = orig['start'][0], orig['start'][1]
                        ex, ey = orig['end'][0], orig['end'][1]
                        min_x = min(min_x, sx, ex); max_x = max(max_x, sx, ex)
                        min_y = min(min_y, sy, ey); max_y = max(max_y, sy, ey)

                    ccx = (min_x + max_x) / 2.0
                    ccy = (min_y + max_y) / 2.0
                    for c_hndl in cluster:
                        self.line_cluster_centers[c_hndl] = (ccx, ccy)


    
    def auto_detect_between_zone(self, axis):
        if axis == 'X' and self.left_fixed_handles and self.right_fixed_handles:
            max_left_x = max(self.doc.entitydb[h].right_x for h in self.left_fixed_handles if h in self.doc.entitydb)
            min_right_x = min(self.doc.entitydb[h].left_x for h in self.right_fixed_handles if h in self.doc.entitydb)
            if min_right_x > max_left_x and (min_right_x - max_left_x) > 10.0:
                self.add_or_update_zone_bounds(max_left_x, min_right_x , 'X')
        elif axis == 'Y' and self.bottom_fixed_handles and self.top_fixed_handles:
            max_bottom_y = max(self.doc.entitydb[h].top_y for h in self.bottom_fixed_handles if h in self.doc.entitydb)
            min_top_y = min(self.doc.entitydb[h].bottom_y for h in self.top_fixed_handles if h in self.doc.entitydb)
            if min_top_y > max_bottom_y and (min_top_y - max_bottom_y) > 10.0:
                self.add_or_update_zone_bounds(max_bottom_y , min_top_y, 'Y')


    


    def get_line_shifted_coords(self, sx, sy, sz, ex, ey, ez, hndl):
        # 1. Базові каскадні зсуви через оновлене багатосходинкове ядро
        shift_sx = self.calculate_cascade_shift(sx, 'X', hndl) - sx
        shift_ex = self.calculate_cascade_shift(ex, 'X', hndl) - ex
        shift_sy = self.calculate_cascade_shift(sy, 'Y', hndl) - sy
        shift_ey = self.calculate_cascade_shift(ey, 'Y', hndl) - ey

        in_cluster = hasattr(self, 'line_cluster_centers') and hndl in self.line_cluster_centers
        is_stretchable = hasattr(self, 'stretchable_handles') and hndl in self.stretchable_handles
        
        if is_stretchable and not in_cluster:
            return (sx + shift_sx, sy + shift_sy, sz), (ex + shift_ex, ey + shift_ey, ez)

        # 2. Інтелектуальний розподіл усередині дотичного кластера
        if in_cluster:
            current_cluster = None
            for cl in getattr(self, 'line_clusters', []):
                if hndl in cl:
                    current_cluster = cl
                    break
            
            if current_cluster:
                cluster_elastic_hndls = [h for h in current_cluster if h in getattr(self, 'stretchable_handles', set())]
                
                if cluster_elastic_hndls:
                    elastic_hndl = cluster_elastic_hndls[0]
                    orig_elastic = self.original_geometries[elastic_hndl]
                    
                    # --- ↔️ Розрахунок по X ---
                    el_cx = (orig_elastic['start'][0] + orig_elastic['end'][0]) / 2.0
                    cx_cluster = self.line_cluster_centers[hndl][0]
                    for zone in self.stretch_zones:
                        if zone['axis'] == 'X' and zone['min'] <= cx_cluster <= zone['max']:
                            # Зчитуємо точні крокові значення зсуву з ядра
                            shift_left = self.calculate_cascade_shift(el_cx - 0.01, 'X', None) - (el_cx - 0.01)
                            shift_right = self.calculate_cascade_shift(el_cx + 0.01, 'X', None) - (el_cx + 0.01)
                            
                            shift_sx = shift_right if sx >= el_cx else shift_left
                            shift_ex = shift_right if ex >= el_cx else shift_left
                            break

                    # --- ↕️ Розрахунок по Y ---
                    el_cy = (orig_elastic['start'][1] + orig_elastic['end'][1]) / 2.0
                    cy_cluster = self.line_cluster_centers[hndl][1]
                    for zone in self.stretch_zones:
                        if zone['axis'] == 'Y' and zone['min'] <= cy_cluster <= zone['max']:
                            # Зчитуємо точні крокові значення зсуву з ядра
                            shift_down = self.calculate_cascade_shift(el_cy - 0.01, 'Y', None) - (el_cy - 0.01)
                            shift_up = self.calculate_cascade_shift(el_cy + 0.01, 'Y', None) - (el_cy + 0.01)
                            
                            shift_sy = shift_up if sy >= el_cy else shift_down
                            shift_ey = shift_up if ey >= el_cy else shift_down
                            break
                            
                    return (sx + shift_sx, sy + shift_sy, sz), (ex + shift_ex, ey + shift_ey, ez)
                else:
                    # Якщо в кластері немає своєї еластичної лінії, він просто жорстко зміщується за ядром
                    cx_cluster, cy_cluster = self.line_cluster_centers[hndl]
                    shift_sx = self.calculate_cascade_shift(cx_cluster, 'X', hndl) - cx_cluster
                    shift_ex = shift_sx
                    shift_sy = self.calculate_cascade_shift(cy_cluster, 'Y', hndl) - cy_cluster
                    shift_ey = shift_sy
                    return (sx + shift_sx, sy + shift_sy, sz), (ex + shift_ex, ey + shift_ey, ez)

        return (sx + shift_sx, sy + shift_sy, sz), (ex + shift_ex, ey + shift_ey, ez)
    


    
if __name__ == "__main__":
    import PySide6.QtWidgets as qtw
    app = qtw.QApplication(sys.argv)
    window = MiniCAD()
    window.view.fitInView(window.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
    window.show()
    sys.exit(app.exec())