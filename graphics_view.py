# from PyQt5.QtWidgets import QGraphicsView
# from PyQt5.QtCore import Qt


# class AdvancedGraphicsView(QGraphicsView):
#     def __init__(self, scene, parent=None):
#         super().__init__(scene, parent)

#         self.main_window = parent

#         self.setDragMode(QGraphicsView.RubberBandDrag)
#         self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
#         self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

#     def wheelEvent(self, event):
#         zoom_in_factor = 1.25
#         zoom_out_factor = 1 / zoom_in_factor

#         old_pos = self.mapToScene(event.pos())

#         if event.angleDelta().y() > 0:
#             zoom_factor = zoom_in_factor
#         else:
#             zoom_factor = zoom_out_factor

#         self.scale(zoom_factor, zoom_factor)

#         new_pos = self.mapToScene(event.pos())
#         delta = new_pos - old_pos

#         self.translate(delta.x(), delta.y())

#     def mousePressEvent(self, event):
#         if event.button() == Qt.RightButton:
#             self.setDragMode(QGraphicsView.ScrollHandDrag)

#             fake_event = event
#             fake_event.setAccepted(False)

#             super().mousePressEvent(fake_event)
#         else:
#             super().mousePressEvent(event)

#     def mouseReleaseEvent(self, event):
#         rubber_band_rect = None

#         if (
#             self.dragMode() == QGraphicsView.RubberBandDrag
#             and event.button() == Qt.LeftButton
#         ):
#             if hasattr(self, "rubberBandRect") and self.rubberBandRect().isValid():
#                 rubber_band_rect = (
#                     self.mapToScene(self.rubberBandRect()).boundingRect()
#                 )

#         super().mouseReleaseEvent(event)

#         self.setDragMode(QGraphicsView.RubberBandDrag)

#         if event.button() == Qt.LeftButton:
#             if rubber_band_rect:
#                 self.main_window.process_manual_rubber_band(rubber_band_rect)
#             else:
#                 item = self.itemAt(event.pos())

#                 if not item:
                 
#                     self.main_window.clear_selection()


from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QGuiApplication, QMouseEvent, QPainterPath


class AdvancedGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)

        self.main_window = parent

        # Налаштування режимів перетягування та масштабування під курсором
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Оновлено отримання позиції під PySide6
        event_pos = event.position().toPoint()
        old_pos = self.mapToScene(event_pos)

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

        new_pos = self.mapToScene(event_pos)
        delta = new_pos - old_pos

        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
            if event.button() == Qt.MouseButton.RightButton:
                # 1. Вмикаємо режим "руки"
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                
                # 2. Перемикаємо подію, щоб Qt думав, що це лівий клік (це ініціює перетягування)
                fake_event = QMouseEvent(
                    event.type(), event.pos(), Qt.MouseButton.LeftButton, 
                    Qt.MouseButton.LeftButton, event.modifiers()
                )
                super().mousePressEvent(fake_event)
            else:
                # Для звичайного виділення рамкою
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
            # 1. Якщо це була ліва кнопка, спочатку дізнаємось, що було виділено
            if event.button() == Qt.MouseButton.LeftButton:
                rect = self.rubberBandRect()
                
                # Якщо рамка валідна, обробляємо її
                if rect.isValid():
                    scene_rect = self.mapToScene(rect).boundingRect()
                    self.main_window.process_manual_rubber_band(scene_rect)
                else:
                    # Це був одиночний клік
                    item = self.itemAt(event.position().toPoint())
                    if not item:
                        self.main_window.clear_selection()

            # 2. Тільки ТЕПЕР викликаємо супер, щоб він завершив логіку Qt
            super().mouseReleaseEvent(event)
            
            # 3. Повертаємо режим (якщо треба)
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)


    def process_manual_rubber_band(self, rect):
    # Додайте підтримку Ctrl для мульти-вибору
        if not (QGuiApplication.keyboardModifiers() & Qt.ControlModifier):
            self.selected_handles.clear()
            
        path = QPainterPath()
        path.addRect(rect)
        matched_items = self.scene.items(path, Qt.ItemSelectionMode.IntersectsItemShape)
        
        for item in matched_items:
            hndl = item.data(Qt.ItemDataRole.UserRole)
            if hndl:
                self.selected_handles.add(hndl)
                
        self.sync_list_from_handles()
        self.update_viewer()