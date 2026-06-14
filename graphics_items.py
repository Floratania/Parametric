# # from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
# # from PyQt5.QtGui import QPainterPath


# # class SelectableCircle(QGraphicsEllipseItem):
# #     def shape(self):
# #         path = QPainterPath()
# #         path.addEllipse(self.rect())
# #         return path


# # class SelectableLine(QGraphicsLineItem):
# #     def shape(self):
# #         path = QPainterPath()
# #         path.moveTo(self.line().p1())
# #         path.lineTo(self.line().p2())
# #         return path

# from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsLineItem
# from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPainterPathStroker, QPen


# from PySide6.QtWidgets import QGraphicsEllipseItem
# from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPen
# from PySide6.QtCore import Qt

# from PySide6.QtWidgets import QGraphicsPathItem
# from PySide6.QtGui import QPainterPath, QPainterPathStroker, QPen
# from PySide6.QtCore import Qt, QPointF

# class SelectableArc(QGraphicsPathItem):
#     def __init__(self, center, radius, start_angle, end_angle, entity=None):
#         super().__init__()
#         self.entity = entity
        
#         # Створюємо шлях арки
#         path = QPainterPath()
#         # arcMoveTo та arcTo використовують градуси
#         # Увага: arcTo у Qt працює з кутами в градусах (0 - 3 саміт, проти годинникової стрілки)
#         # ezdxf також працює у градусах.
#         path.arcMoveTo(center.x() - radius, center.y() - radius, 
#                        radius * 2, radius * 2, start_angle)
#         path.arcTo(center.x() - radius, center.y() - radius, 
#                    radius * 2, radius * 2, start_angle, end_angle - start_angle)
        
#         self.setPath(path)

#     def shape(self):
#         """Збільшуємо зону кліку навколо дуги."""
#         stroker = QPainterPathStroker()
#         stroker.setWidth(6) # Зона кліку 6 пікселів
#         return stroker.createStroke(self.path())

#     def paint(self, painter, option, widget):
#             # 1. Визначаємо товщину на основі ezdxf lineweight
#             lw = self.entity.dxf.lineweight if self.entity and hasattr(self.entity.dxf, 'lineweight') else 0
#             pixel_width = max(0.5, lw / 100.0) if lw > 0 else 1.0
            
#             # 2. Модифікуємо поточне перо елемента
#             pen = self.pen() 
#             pen.setWidthF(pixel_width)
#             pen.setCosmetic(False) 
            
#             # ФІКС ПОМИЛКИ: Використовуємо повні назви перерахувань PySide6
#             pen.setCapStyle(Qt.PenCapStyle.RoundCap)
#             pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            
#             # 3. Передаємо налаштоване перо та малюємо
#             painter.setPen(pen)
#             painter.drawPath(self.path())


# class SelectableCircle(QGraphicsEllipseItem):
#     def __init__(self, x, y, w, h, entity=None):
#         super().__init__(x, y, w, h)
#         self.entity = entity

#     def shape(self):
#         """Збільшуємо зону кліку навколо контуру кола."""
#         path = QPainterPath()
#         path.addEllipse(self.rect())
        
#         # Створюємо зону захоплення (stroker)
#         stroker = QPainterPathStroker()
#         stroker.setWidth(6) # Зона кліку 6 пікселів
#         return stroker.createStroke(path)

#     def paint(self, painter, option, widget):
          
#             lw = self.entity.dxf.lineweight if self.entity and hasattr(self.entity.dxf, 'lineweight') else 0
#             pixel_width = max(0.5, lw / 100.0) if lw > 0 else 1.0
            
#             # 2. Модифікуємо ПРАВИЛЬНЕ поточне перо (зберігаємо колір, стилі виділення тощо)
#             pen = self.pen() 
#             pen.setWidthF(pixel_width)
#             pen.setCosmetic(False) # Лінія пропорційно товстішає при наближенні (зумі)
            

#             from PyQt5.QtCore import Qt  
#             pen.setCapStyle(Qt.RoundCap)
#             pen.setJoinStyle(Qt.RoundJoin)
        
#             painter.setPen(pen)
#             painter.drawPath(self.path())


# class SelectableLine(QGraphicsLineItem):
#     def __init__(self, x1, y1, x2, y2, entity=None):
#         super().__init__(x1, y1, x2, y2)
#         self.entity = entity

#     def paint(self, painter, option, widget):
#         # БЕЗПЕЧНА ПЕРЕВІРКА:
#         # Якщо entity існує І має атрибут dxf, тоді беремо товщину.
#         # В іншому випадку використовуємо 0 (або інше значення за замовчуванням).
#         if self.entity is not None and hasattr(self.entity, 'dxf'):
#             lw = getattr(self.entity.dxf, 'lineweight', 0)
#             pixel_width = max(0.5, lw / 100.0) if lw > 0 else 1.0
#         else:
#             pixel_width = 1.0
            
#         pen = QPen(self.pen().color(), pixel_width)
#         pen.setCosmetic(False)
#         painter.setPen(pen)
#         painter.drawLine(self.line())

#     def shape(self):
#         path = QPainterPath()
#         path.moveTo(self.line().p1())
#         path.lineTo(self.line().p2())
        
#         stroker = QPainterPathStroker()
#         # Зменште з 10 до 3 або 4. Це дасть 1.5-2 пікселі запасу з кожного боку.
#         # Це достатньо для кліку, але не буде "склеювати" сусідні лінії.
#         stroker.setWidth(2) 
#         return stroker.createStroke(path)
    

from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QPainterPath, QPainterPathStroker
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsLineItem


class SelectableArc(QGraphicsPathItem):
    def __init__(self, center, radius, start_angle, end_angle, entity=None):
        super().__init__()
        self.entity = entity
        
        path = QPainterPath()
        path.arcMoveTo(center.x() - radius, center.y() - radius, 
                       radius * 2, radius * 2, start_angle)
        sa = entity.dxf.start_angle
        ea = entity.dxf.end_angle

        if ea < sa:
            ea += 360

        path.arcTo(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2,
            sa,
            ea - sa
        )
        self.setPath(path)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(6)  # Зона кліку 6 пікселів
        return stroker.createStroke(self.path())

    def paint(self, painter, option, widget):
        lw = self.entity.dxf.lineweight if self.entity and hasattr(self.entity.dxf, 'lineweight') else 0
        pixel_width = max(0.5, lw / 100.0) if lw > 0 else 1.0
        
        # Модифікуємо існуюче перо
        pen = self.pen()
        pen.setWidthF(pixel_width)
        pen.setCosmetic(True) 
        
        # ПРАВИЛЬНИЙ СИНТАКСИС ДЛЯ PYSIDE6
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
        painter.setPen(pen)
        painter.drawPath(self.path())


# ---------------------------------------------------------------------------
# 🔘 КЛАС КОЛА (ОТВОРУ)
# ---------------------------------------------------------------------------
class SelectableCircle(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, entity=None):
        super().__init__(x, y, w, h)
        self.entity = entity

    def shape(self):
        path = QPainterPath()
        path.addEllipse(self.rect())
        
        stroker = QPainterPathStroker()
        stroker.setWidth(6)
        return stroker.createStroke(path)

    def paint(self, painter, option, widget):
        lw = self.entity.dxf.lineweight if self.entity and hasattr(self.entity.dxf, 'lineweight') else 0
        pixel_width = max(0.5, lw / 100.0) if lw > 0 else 1.0
        
        pen = self.pen()
        pen.setWidthF(pixel_width)
        pen.setCosmetic(True)  
        
        # ДЛЯ КОЛА НАЛАШТУВАННЯ CAPSTYLE НЕ ПОТРІБНІ (воно замкнене)
        painter.setPen(pen)
        painter.drawEllipse(self.rect())


# ---------------------------------------------------------------------------
# 📏 КЛАС ЛІНІЇ
# ---------------------------------------------------------------------------
class SelectableLine(QGraphicsLineItem):
    def __init__(self, x1, y1, x2, y2, entity=None):
        super().__init__(x1, y1, x2, y2)
        self.entity = entity

    def shape(self):
        path = QPainterPath()
        path.moveTo(self.line().p1())
        path.lineTo(self.line().p2())
        
        stroker = QPainterPathStroker()
        stroker.setWidth(2) 
        return stroker.createStroke(path)

    def paint(self, painter, option, widget):
        if self.entity is not None and hasattr(self.entity, 'dxf'):
            lw = getattr(self.entity.dxf, 'lineweight', 0)
            pixel_width = max(0.5, lw / 100.0) if lw > 0 else 1.0
        else:
            pixel_width = 1.0
            
        pen = self.pen()  # Використовуємо self.pen() замість створення нового QPen з нуля
        pen.setWidthF(pixel_width)
        pen.setCosmetic(True)
        
        # Для ліній дверей теж корисно зробити красиві скруглені кінці без помилок:
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        
        painter.setPen(pen)
        painter.drawLine(self.line())