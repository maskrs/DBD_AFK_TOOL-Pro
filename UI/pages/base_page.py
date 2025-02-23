from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from Utils.config_manager import config_manager

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
        
        # 初始化配置
        config_manager.load_configs()  # 加载配置文件
        self.ui_config = config_manager.get_ui_config()
        
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
        
    def get_config_value(self, section, key, default=None):
        """获取配置值"""
        return self.ui_config.get(section, {}).get(key, default)
        
    def save_config_value(self, section, key, value):
        """保存配置值"""
        if section not in self.ui_config:
            self.ui_config[section] = {}
        self.ui_config[section][key] = value
        config_manager.update_ui_states({section: {key: value}})
        
    def get_user_config(self, key, default=None):
        """获取用户配置"""
        return config_manager.get_user_config(key, default)
        
    def save_user_config(self, key, value):
        """保存用户配置"""
        config_manager.set_user_config(key, value)
        config_manager.save_configs()  # 保存到文件
