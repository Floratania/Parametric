from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QPushButton, QSlider, QGroupBox, QComboBox, QLineEdit,
    QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

from graphics_view import AdvancedGraphicsView

class CADUiLayout(QMainWindow):
    """
    Ізольований модуль інтерфейсу. Захищає інженерні методи від затирання.
    """
    def build_ui_structure(self):
        main_widget = QWidget()
        self.central_layout = QHBoxLayout(main_widget)
        self.setCentralWidget(main_widget)

        # --- ЛІВИЙ ПРОВІДНИК ПАПКИ ПРОЕКТУ ---
        folder_explorer_widget = QWidget()
        folder_explorer_layout = QVBoxLayout(folder_explorer_widget)
        folder_explorer_layout.setContentsMargins(0, 0, 5, 0)
        
        lbl_explorer_title = QLabel("📁 <b>Провідник DXF (утримуйте Ctrl):</b>")
        lbl_explorer_title.setStyleSheet("font-size: 11px; color: #ff9800;")
        folder_explorer_layout.addWidget(lbl_explorer_title)
        
        self.file_explorer_list = QListWidget()
        self.file_explorer_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        folder_explorer_layout.addWidget(self.file_explorer_list)
        self.central_layout.addWidget(folder_explorer_widget, stretch=1)

        # --- ЦЕНТРАЛЬНИЙ ГРАФІЧНИЙ БЛОК ---
        self.scene = None  
        self.view = AdvancedGraphicsView(None, self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.central_layout.addWidget(self.view, stretch=4)

        # --- ПРАВА ПАНЕЛЬ КЕРУВАННЯ ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(5, 0, 0, 0)
        self.central_layout.addWidget(control_panel, stretch=2)

        # --- БЛОК 1: АДАНТАЦІЯ ПІД РОЗМІРИ ЗАМОВЛЕННЯ ---
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

        # --- БЛОК 2: ОРІЄНТАЦІЯ ТА ОБЕРТАННЯ ДЕТАЛЕЙ ---
        transform_group = QGroupBox("🔄 Орієнтація та обертання виділених деталей")
        transform_box = QVBoxLayout()
        
        rot_layout = QHBoxLayout()
        self.btn_rot_90 = QPushButton("↪️ Поворот 90°")
        self.btn_rot_180 = QPushButton("🔁 Поворот 180°")
        rot_layout.addWidget(self.btn_rot_90)
        rot_layout.addWidget(self.btn_rot_180)
        transform_box.addLayout(rot_layout)

        mirror_layout = QHBoxLayout()
        self.btn_mirror_h = QPushButton("↔️ Віддзеркалити по Х")
        self.btn_mirror_v = QPushButton("↕️ Віддзеркалити по Y")
        mirror_layout.addWidget(self.btn_mirror_h)
        mirror_layout.addWidget(self.btn_mirror_v)
        transform_box.addLayout(mirror_layout)

        transform_group.setLayout(transform_box)
        control_layout.addWidget(transform_group)

        # --- БЛОК 3: ИНЖЕНЕРНЕ ПРИТИСКАННЯ (БАЗУВАННЯ) ---
        align_group = QGroupBox("📍 Притулити (базувати) виділене до краю дверей")
        align_box = QVBoxLayout()

        align_x_layout = QHBoxLayout()
        self.btn_align_left = QPushButton("🟢 До лівого краю (Х)")
        self.btn_align_right = QPushButton("🔴 До правого краю (Х)")
        align_x_layout.addWidget(self.btn_align_left)
        align_x_layout.addWidget(self.btn_align_right)
        align_box.addLayout(align_x_layout)

        align_y_layout = QHBoxLayout()
        self.btn_align_bottom = QPushButton("🔵 До нижнього краю (Y)")
        self.btn_align_top = QPushButton("🟡 До верхнього краю (Y)")
        align_y_layout.addWidget(self.btn_align_bottom)
        align_y_layout.addWidget(self.btn_align_top)
        align_box.addLayout(align_y_layout)

        align_group.setLayout(align_box)
        control_layout.addWidget(align_group)

        # --- БЛОК СТИЛЮ ТА ТЕМИ ---
        theme_group = QGroupBox("🎨 Стиль оформлення (Тема)")
        theme_box = QHBoxLayout()
        theme_box.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темна", "Світла"])
        theme_box.addWidget(self.theme_combo)
        theme_group.setLayout(theme_box)
        control_layout.addWidget(theme_group)

        # --- БЛОК ІСТОРІЇ ЗМІН (UNDO / REDO) ---
        history_group = QGroupBox("Історія конструкторських змін")
        history_box = QHBoxLayout()
        self.btn_undo = QPushButton("⬅️ Назад (Undo)")
        self.btn_redo = QPushButton("Вперед (Redo) ➡️")
        history_box.addWidget(self.btn_undo)
        history_box.addWidget(self.btn_redo)
        history_group.setLayout(history_box)
        control_layout.addWidget(history_group)

        # --- ГРУПА ФІКСАЦІЇ СТОРІН ---
        fix_group = QGroupBox("1. Фіксація жорстких блоків (елементів фурнітури)")
        fix_box = QVBoxLayout()
        h_fix_layout = QHBoxLayout()
        self.btn_set_left_fix = QPushButton("🟢 Лівий блок (X)")
        self.btn_set_right_fix = QPushButton("🔴 Правий блок (X)")
        self.btn_set_left_fix.setObjectName("leftFixBtn")
        self.btn_set_right_fix.setObjectName("rightFixBtn")
        h_fix_layout.addWidget(self.btn_set_left_fix)
        h_fix_layout.addWidget(self.btn_set_right_fix)
        fix_box.addLayout(h_fix_layout)

        v_fix_layout = QHBoxLayout()
        self.btn_set_bottom_fix = QPushButton("🔵 Нижній блок (Y)")
        self.btn_set_top_fix = QPushButton("🟡  Верхній блок (Y)")
        self.btn_set_bottom_fix.setObjectName("bottomFixBtn")
        self.btn_set_top_fix.setObjectName("topFixBtn")
        v_fix_layout.addWidget(self.btn_set_bottom_fix)
        v_fix_layout.addWidget(self.btn_set_top_fix)
        fix_box.addLayout(v_fix_layout)
        fix_group.setLayout(fix_box)
        control_layout.addWidget(fix_group)

        # --- МЕНЕДЖЕР ЗОН РОЗТЯГУВАННЯ ---
        zone_group = QGroupBox("2. Створення зон деформації простору")
        zone_box = QVBoxLayout()
        self.btn_add_zone_x = QPushButton("↔️ Оголосити виділене ЗОНОЮ розтягування (X)")
        self.btn_add_zone_y = QPushButton("↕️ Оголосити виділене ЗОНОЮ розтягування (Y)")
        self.btn_clear_zones = QPushButton("🔄 Скинути всі зони та фіксації")
        zone_box.addWidget(self.btn_add_zone_x)
        zone_box.addWidget(self.btn_add_zone_y)
        zone_box.addWidget(self.btn_clear_zones)
        zone_group.setLayout(zone_box)
        control_layout.addWidget(zone_group)

        control_layout.addWidget(QLabel("<b>Список створених зон розтягування:</b>"))
        self.zone_list_widget = QListWidget()
        control_layout.addWidget(self.zone_list_widget)

        control_layout.addWidget(QLabel("<b>Елементи креслення дверей:</b>"))
        self.entity_list = QListWidget()
        self.entity_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        control_layout.addWidget(self.entity_list)

        self.slider_label = QLabel("Або скористайтеся ручним слайдером зони")
        control_layout.addWidget(self.slider_label)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 600)
        self.slider.setValue(0)
        self.slider.setEnabled(False)
        control_layout.addWidget(self.slider)

        control_layout.addStretch()

            
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