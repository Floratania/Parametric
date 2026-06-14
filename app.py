import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSlider, QLabel, QGraphicsView, 
                             QGraphicsScene, QListWidget, QListWidgetItem, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QAbstractItemView, QPushButton)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QPainterPath

import ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.pyqt import PyQtBackend

# Класи з точною геометрією форми для виділення
class SelectableCircle(QGraphicsEllipseItem):
    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.rect())
        return path

class SelectableLine(QGraphicsLineItem):
    def shape(self):
        path = QPainterPath()
        path.moveTo(self.line().p1())
        path.lineTo(self.line().p2())
        return path


class AdvancedGraphicsView(QGraphicsView):
    """Переглядач із ручним ловом рамки виділення та зумом"""
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.main_window = parent
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        old_pos = self.mapToScene(event.pos())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fake_event = event
            fake_event.setAccepted(False)
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        rubber_band_rect = None
        if self.dragMode() == QGraphicsView.RubberBandDrag and event.button() == Qt.LeftButton:
            if hasattr(self, 'rubberBandRect') and self.rubberBandRect().isValid():
                rubber_band_rect = self.mapToScene(self.rubberBandRect()).boundingRect()

        super().mouseReleaseEvent(event)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
        if event.button() == Qt.LeftButton:
            if rubber_band_rect:
                self.main_window.process_manual_rubber_band(rubber_band_rect)
            else:
                item = self.itemAt(event.pos())
                if not item:
                    self.main_window.clear_selection()


class MiniCAD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CAD Редактор: Розумна дедуплікація об'єктів")
        self.setGeometry(100, 100, 1200, 750)

        self.dxf_path = "drawing.DXF"
        self.selected_handles = set()
        self.overlay_items = {}

        self.undo_stack = []
        self.redo_stack = []
        self.is_loading_history = False

        if not os.path.exists(self.dxf_path):
            print(f"Помилка: Файл {self.dxf_path} не знайдено!")
            sys.exit()

        self.doc = ezdxf.readfile(self.dxf_path)
        self.save_to_undo_stack()

        self.init_ui()
        self.update_viewer()
        self.load_entities_into_list()

    def init_ui(self):
        main_widget = QWidget()
        self.central_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        self.scene = QGraphicsScene()
        self.view = AdvancedGraphicsView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.central_layout.addWidget(self.view, stretch=4)

        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        self.central_layout.addWidget(control_panel, stretch=2)

        history_layout = QHBoxLayout()
        self.btn_undo = QPushButton("⬅️ Назад (Undo)")
        self.btn_undo.clicked.connect(self.undo)
        self.btn_redo = QPushButton("Вперед (Redo) ➡️")
        self.btn_redo.clicked.connect(self.redo)
        history_layout.addWidget(self.btn_undo)
        history_layout.addWidget(self.btn_redo)
        control_layout.addLayout(history_layout)
        
        self.update_history_buttons_state()

        control_layout.addWidget(QLabel("Список деталей (мультивиділення):"))
        self.entity_list = QListWidget()
        self.entity_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.entity_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        control_layout.addWidget(self.entity_list)

        self.slider_label = QLabel("Розмір обраних деталей:")
        control_layout.addWidget(self.slider_label)
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(1, 150)
        self.slider.setValue(20)
        self.slider.setEnabled(False)
        
        self.slider.valueChanged.connect(self.on_geometry_change)
        self.slider.sliderReleased.connect(self.on_slider_released)
        control_layout.addWidget(self.slider)

        control_layout.addStretch()

    # --- МЕХАНІЗМ UNDO / REDO ---
    def save_to_undo_stack(self):
        with open(self.dxf_path, "rb") as f:
            self.undo_stack.append(f.read())
        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) <= 1:
            return
        current_state = self.undo_stack.pop()
        self.redo_stack.append(current_state)
        previous_state = self.undo_stack[-1]
        with open(self.dxf_path, "wb") as f:
            f.write(previous_state)
        self.reload_after_history_change()

    def redo(self):
        if not self.redo_stack:
            return
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        with open(self.dxf_path, "wb") as f:
            f.write(next_state)
        self.reload_after_history_change()

    def on_slider_released(self):
        self.doc.saveas(self.dxf_path)
        self.save_to_undo_stack()
        self.redo_stack.clear()
        self.update_history_buttons_state()

    def reload_after_history_change(self):
        self.is_loading_history = True
        self.doc = ezdxf.readfile(self.dxf_path)
        self.update_viewer()
        self.load_entities_into_list()
        self.update_history_buttons_state()
        
        if self.selected_handles:
            hndl = list(self.selected_handles)[0]
            if hndl in self.doc.entitydb:
                entity = self.doc.entitydb[hndl]
                if entity.dxftype() == 'CIRCLE':
                    self.slider.setValue(int(entity.dxf.radius))
                elif entity.dxftype() == 'LINE':
                    self.slider.setValue(int(entity.dxf.end[0]))
        self.is_loading_history = False

    def update_history_buttons_state(self):
        self.btn_undo.setEnabled(len(self.undo_stack) > 1)
        self.btn_redo.setEnabled(len(self.redo_stack) > 0)

    # --- РОЗУМНИЙ РЕНДЕРИНГ БЕЗ ДУБЛІКАТІВ ---
    def update_viewer(self):
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.overlay_items.clear()

        msp = self.doc.modelspace()

        # Множини для відстеження унікальності геометрії на екрані
        seen_circles = set()
        seen_lines = set()

        for entity in msp:
            hndl = entity.dxf.handle
            tp = entity.dxftype()
            pyqt_item = None
            
            if tp == 'CIRCLE':
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                
                # Округляємо координати до 2 знаків, щоб уникнути похибок float
                geo_key = (round(cx, 2), round(cy, 2), round(r, 2))
                if geo_key in seen_circles:
                    continue  # Пропускаємо дублікат
                seen_circles.add(geo_key)
                
                pyqt_item = SelectableCircle(cx - r, -cy - r, r * 2, r * 2)
                
            elif tp == 'LINE':
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                
                geo_key = (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2))
                if geo_key in seen_lines:
                    continue  # Пропускаємо дублікат
                seen_lines.add(geo_key)
                
                pyqt_item = SelectableLine(x1, -y1, x2, -y2)

            if pyqt_item:
                pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsSelectable, False)
                pyqt_item.setFlag(QGraphicsEllipseItem.ItemIsFocusable, False)
                
                pyqt_item.mousePressEvent = lambda event, h=hndl: self.on_scene_item_clicked(h)
                
                if hndl in self.selected_handles:
                    pyqt_item.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
                else:
                    pyqt_item.setPen(QPen(QColor(80, 80, 80), 2, Qt.SolidLine))

                pyqt_item.setData(Qt.UserRole, hndl)
                self.scene.addItem(pyqt_item)
                self.overlay_items[hndl] = pyqt_item

        self.view.setSceneRect(self.scene.itemsBoundingRect())

    def on_scene_item_clicked(self, handle):
        self.selected_handles = {handle}
        self.sync_list_from_handles()
        self.update_viewer()
        self.update_slider_state()

    def process_manual_rubber_band(self, rect):
        self.selected_handles.clear()
        path = QPainterPath()
        path.addRect(rect)
        
        matched_items = self.scene.items(path, Qt.IntersectsItemShape)
        for item in matched_items:
            hndl = item.data(Qt.UserRole)
            if hndl:
                self.selected_handles.add(hndl)
                
        self.sync_list_from_handles()
        self.update_viewer()
        self.update_slider_state()

    def sync_list_from_handles(self):
        self.entity_list.blockSignals(True)
        self.entity_list.clearSelection()
        for i in range(self.entity_list.count()):
            item = self.entity_list.item(i)
            if item.data(Qt.UserRole) in self.selected_handles:
                item.setSelected(True)
        self.entity_list.blockSignals(False)

    def on_list_selection_changed(self):
        self.selected_handles.clear()
        for item in self.entity_list.selectedItems():
            self.selected_handles.add(item.data(Qt.UserRole))
            
        for hndl, pyqt_item in self.overlay_items.items():
            if hndl in self.selected_handles:
                pyqt_item.setPen(QPen(QColor(255, 0, 0), 3, Qt.SolidLine))
            else:
                pyqt_item.setPen(QPen(QColor(80, 80, 80), 2, Qt.SolidLine))
                
        self.update_slider_state()

    def clear_selection(self):
        self.selected_handles.clear()
        self.update_viewer()
        self.slider.setEnabled(False)
        self.slider_label.setText("Розмір обраних деталей:")
        self.entity_list.blockSignals(True)
        self.entity_list.clearSelection()
        self.entity_list.blockSignals(False)

    def load_entities_into_list(self):
        self.entity_list.blockSignals(True)
        self.entity_list.clear()
        
        msp = self.doc.modelspace()
        seen_circles = set()
        seen_lines = set()

        for entity in msp:
            tp = entity.dxftype()
            hndl = entity.dxf.handle
            
            if tp == 'CIRCLE':
                cx, cy, _ = entity.dxf.center
                r = entity.dxf.radius
                geo_key = (round(cx, 2), round(cy, 2), round(r, 2))
                if geo_key in seen_circles: continue
                seen_circles.add(geo_key)
                
                text = f"🔘 Коло (ID: {hndl}) | R={r:.1f}"
                
            elif tp == 'LINE':
                x1, y1, _ = entity.dxf.start
                x2, y2, _ = entity.dxf.end
                geo_key = (round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2))
                if geo_key in seen_lines: continue
                seen_lines.add(geo_key)
                
                text = f"📏 Лінія (ID: {hndl})"
            else:
                continue

            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, hndl)
            self.entity_list.addItem(item)
            
            if hndl in self.selected_handles:
                item.setSelected(True)
                
        self.entity_list.blockSignals(False)

    def update_slider_state(self):
        if not self.selected_handles:
            self.slider.setEnabled(False)
            self.slider_label.setText("Розмір обраних деталей:")
            return

        self.slider.blockSignals(True)
        self.slider.setEnabled(True)
        self.slider_label.setText(f"Змінити размер ({len(self.selected_handles)} деталей) одночасно:")
        
        hndl = list(self.selected_handles)[0]
        entity = self.doc.entitydb[hndl]
        if entity.dxftype() == 'CIRCLE':
            self.slider.setRange(1, 100)
            self.slider.setValue(int(entity.dxf.radius))
        elif entity.dxftype() == 'LINE':
            self.slider.setRange(0, 2000)
            self.slider.setValue(int(entity.dxf.end[0]))
        self.slider.blockSignals(False)

    def on_geometry_change(self, value):
        if not self.selected_handles or self.is_loading_history:
            return

        for hndl in self.selected_handles:
            if hndl not in self.doc.entitydb:
                continue
            entity = self.doc.entitydb[hndl]
            
            if entity.dxftype() == 'CIRCLE':
                entity.dxf.radius = float(value)
            elif entity.dxftype() == 'LINE':
                current_end = entity.dxf.end
                entity.dxf.end = (float(value), current_end[1], current_end[2])

        self.update_viewer()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MiniCAD()
    window.view.fitInView(window.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
    window.show()
    sys.exit(app.exec_())