from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt
from UI.components.modern_card import ModernCard
from UI.components.modern_line_edit import ModernLineEdit
from UI.components.modern_text_edit import ModernTextEdit
from UI.components.modern_button import ModernButton
from UI.components.modern_notification import NotificationManager
from Utils.config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class SettingsPage(QWidget):
    """设置页面"""

    def __init__(self, theme_manager=None, parent=None):
        # 调用父类初始化
        super().__init__(parent)

        # 设置对象名称
        self.setObjectName("SettingsPage")

        # 初始化属性
        self.theme_manager = theme_manager
        self.notification_manager = NotificationManager()

       # 创建布局
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(20)
        self._layout.setContentsMargins(20, 10, 20, 10)
        self._setup_ui()

    def _setup_ui(self):    
        """创建UI"""
        # 创建卡片
        card = ModernCard("设置", self)
        card.set_content_direction(True)
        card.set_content_container_width(125)