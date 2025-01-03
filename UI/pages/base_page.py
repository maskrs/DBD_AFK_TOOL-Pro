from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter

class BasePage(QWidget):
    """页面基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)
        
        # 创建主布局
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(10)
        
        # 初始化UI
        self._setup_ui()
    
    def _setup_ui(self):
        """初始化UI"""
        pass  # 子类实现具体UI
    
    def paintEvent(self, event):
        """确保透明绘制"""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)  # 使用透明填充
