from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import logging

logger = logging.getLogger(__name__)

class SettingsPage(QWidget):
    """设置页面"""
    
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        
        self._setup_ui()

    def _setup_ui(self):
        """创建UI"""
        layout = QVBoxLayout(self)
        
        # 添加设置内容
        settings_label = QLabel("设置页面")
        layout.addWidget(settings_label)
