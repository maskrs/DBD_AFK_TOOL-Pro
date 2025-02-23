from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtCore import Qt
from UI.utils.theme_manager import ThemeManager
from UI.components.nav_bar import NavBar
from UI.pages.home_page import HomePage
from UI.pages.settings_page import SettingsPage
from UI.components.animated_stack import AnimatedStackedWidget
import UI.resources.resources_rc

import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager()
        
        # 设置窗口属性
        self._setup_window()
        
        # 创建UI
        self._setup_ui()
        
        # 设置主题
        self.theme_manager.setWindow(self)

    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("DBD AFK Tool Pro")
        self.resize(800, 600)
        if self.theme_manager._supports_mica:
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAutoFillBackground(False)

    def _setup_ui(self):
        """创建UI"""
        # 创建中心部件
        central_widget = QWidget()
        central_widget.theme_manager = self.theme_manager
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建导航栏和页面堆栈
        self.nav_bar = NavBar(self)
        self.nav_bar.theme_manager = self.theme_manager
        self.page_stack = AnimatedStackedWidget()
        
        layout.addWidget(self.nav_bar)
        layout.addWidget(self.page_stack)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        
        # 创建页面
        self._setup_pages()
        
        # 连接信号
        self.nav_bar.pageChanged.connect(self._on_page_changed)

    def _setup_pages(self):
        """创建所有页面"""
        # 主页页面
        home_page = HomePage(self.theme_manager)
        self.page_stack.addWidget(home_page)
        self.nav_bar.addPage("home", "主页", "home")
        
        # 设置页面
        settings_page = SettingsPage(self.theme_manager)
        self.page_stack.addWidget(settings_page)
        self.nav_bar.addPage("setting", "设置", "settings")

    def _on_page_changed(self, page_id: str):
        """页面切换处理"""
        try:
            index = self.nav_bar.get_page_index(page_id)
            if index >= 0 and index != self.page_stack.currentIndex():
                self.page_stack.setCurrentIndex(index)
        except Exception:
            pass