class StyleManager:
    def __init__(self):
        self.dark_mode = False
        
    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        
    def is_dark_mode(self):
        """Return current theme mode"""
        return self.dark_mode
        
    def get_main_stylesheet(self):
        """Get the main application stylesheet"""
        if self.dark_mode:
            return self._get_dark_stylesheet()
        else:
            return self._get_light_stylesheet()
            
    def _get_light_stylesheet(self):
        """Get light theme stylesheet"""
        return """
            QMainWindow, QDialog {
                background-color: #f5f5f5;
            }
            
            QWidget {
                color: #333333;
            }
            
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
            }
            
            QTabBar::tab {
                background-color: #e6e6e6;
                border: 1px solid #cccccc;
                padding: 6px 12px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom-color: #ffffff;
            }
            
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            
            QPushButton:hover {
                background-color: #0d8beb;
            }
            
            QPushButton:pressed {
                background-color: #0a7fd1;
            }
            
            QLineEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px;
                background-color: white;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2196f3;
            }
            
            QTableWidget {
                alternate-background-color: #f9f9f9;
                gridline-color: #dddddd;
            }
            
            QHeaderView::section {
                background-color: #e6e6e6;
                padding: 4px;
                border: 1px solid #cccccc;
                border-top: none;
                border-left: none;
            }
            
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #444444;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #cccccc;
                height: 8px;
                background: #f0f0f0;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #2196f3;
                border: 1px solid #1565c0;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            
            QStatusBar {
                background-color: #e6e6e6;
                color: #333333;
            }
        """
        
    def _get_dark_stylesheet(self):
        """Get dark theme stylesheet"""
        return """
            QMainWindow, QDialog {
                background-color: #2d2d2d;
            }
            
            QWidget {
                color: #e0e0e0;
            }
            
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3d3d3d;
            }
            
            QTabBar::tab {
                background-color: #353535;
                border: 1px solid #555555;
                padding: 6px 12px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                border-bottom-color: #3d3d3d;
            }
            
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 3px;
            }
            
            QPushButton:hover {
                background-color: #0d8beb;
            }
            
            QPushButton:pressed {
                background-color: #0a7fd1;
            }
            
            QLineEdit, QComboBox {
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 4px;
                background-color: #3d3d3d;
                color: #e0e0e0;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #2196f3;
            }
            
            QTableWidget {
                alternate-background-color: #353535;
                gridline-color: #555555;
                color: #e0e0e0;
                background-color: #2d2d2d;
            }
            
            QHeaderView::section {
                background-color: #353535;
                padding: 4px;
                border: 1px solid #555555;
                border-top: none;
                border-left: none;
                color: #e0e0e0;
            }
            
            QGroupBox {
                border: 1px solid #555555;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #e0e0e0;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background: #454545;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #2196f3;
                border: 1px solid #1565c0;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            
            QStatusBar {
                background-color: #353535;
                color: #e0e0e0;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #3d3d3d;
                width: 10px;
                margin: 10px 0 10px 0;
            }
            
            QScrollBar::handle:vertical {
                background: #555555;
                min-height: 20px;
                border-radius: 5px;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """