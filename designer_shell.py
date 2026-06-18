import os

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

try:
    from PySide6.QtUiTools import QUiLoader
except ImportError:
    QUiLoader = None


def _host_layout(host):
    layout = QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    return layout


def load_designer_shell(parent, ui_path):
    if QUiLoader is None or not os.path.exists(ui_path):
        return None

    ui_file = QFile(ui_path)
    if not ui_file.open(QFile.OpenModeFlag.ReadOnly):
        return None

    try:
        shell = QUiLoader().load(ui_file, parent)
    finally:
        ui_file.close()

    if shell is None:
        return None

    hosts = {
        "folder": shell.findChild(QWidget, "folderHost"),
        "view": shell.findChild(QWidget, "viewHost"),
        "side": shell.findChild(QWidget, "sideHost"),
    }
    if any(host is None for host in hosts.values()):
        return None

    return {
        "widget": shell,
        "folder": _host_layout(hosts["folder"]),
        "view": _host_layout(hosts["view"]),
        "side": _host_layout(hosts["side"]),
    }


def create_fallback_shell(parent):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    parent.setCentralWidget(widget)
    return {"widget": widget, "central": layout}
