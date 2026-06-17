# import sys

# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import Qt

# from cad_window import MiniCAD


# def main():
#     app = QApplication(sys.argv)

#     window = MiniCAD()

#     window.view.fitInView(
#         window.scene.itemsBoundingRect(),
#         Qt.KeepAspectRatio
#     )

#     window.show()

#     sys.exit(app.exec_())


# if __name__ == "__main__":
#     main()

import sys

# Оновлено імпорти під PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from cad_window_2 import MiniCAD


def main():
    app = QApplication(sys.argv)

    window = MiniCAD()

  
    window.view.fitInView(
        window.scene.itemsBoundingRect(),
        Qt.AspectRatioMode.KeepAspectRatio
    )

    window.show()

   
    sys.exit(app.exec())


if __name__ == "__main__":
    main()