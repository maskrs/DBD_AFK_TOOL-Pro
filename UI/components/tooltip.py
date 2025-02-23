from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

class ToolTip(QWidget):
    """现代化工具提示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化属性
        self._init_properties()
        self._init_ui()
        self._setup_animations()
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self._is_dark_mode = self.theme_manager.isDarkMode()
            self._update_colors()
            
    def _init_properties(self):
        """初始化属性"""
        self._is_dark_mode = False
        self._border_radius = 4
        
        # 设置窗口属性
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
    def _init_ui(self):
        """初始化UI"""
        # 创建文本标签
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignLeft)
        self._label.setWordWrap(True)  # 启用自动换行
        self._max_width = 300  # 设置最大宽度
        self._h_padding = 10  # 水平内边距
        
        # 设置初始大小
        self.resize(10, 36)
        
    def _update_colors(self):
        """更新颜色"""
        if self._is_dark_mode:
            bg_color = "rgb(50, 42, 49)"
            text_color = "#DFDFDF"
        else:
            bg_color = "rgb(249, 249, 245)"
            text_color = "#2D2932"
            
        # 更新样式
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        self._label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: {self._border_radius}px;
                padding: 6px {self._h_padding}px;
                font-size: 12px;
                font-family: "Segoe UI";
            }}
        """)
        
    def _setup_animations(self):
        """设置动画"""
        # 几何动画
        self._geometry_animation = QPropertyAnimation(self, b"geometry", self)
        self._geometry_animation.setDuration(200)
        self._geometry_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # 不透明度动画
        self._opacity_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._opacity_animation.setDuration(100)
        self._opacity_animation.setEasingCurve(QEasingCurve.OutQuad)
        self._opacity_animation.finished.connect(self._on_opacity_animation_finished)
        
    def _on_theme_changed(self, is_dark: bool):
        """主题切换响应"""
        self._is_dark_mode = is_dark
        self._update_colors()
        self.update()
        
    def _on_opacity_animation_finished(self):
        """不透明度动画结束处理"""
        if self.windowOpacity() == 0:
            super().hide()
            
    def setText(self, text: str):
        """设置提示文本"""
        self._label.setText(text)
        self._adjust_size()
        
    def _adjust_size(self):
        """调整大小"""
        # 先计算不换行时的文本宽度
        fm = self._label.fontMetrics()
        text_width = fm.horizontalAdvance(self._label.text())
        
        # 如果文本宽度小于最大可用宽度，则使用实际宽度
        if text_width <= (self._max_width - 25):  # 左右padding的总和
            self._label.setWordWrap(False)  # 禁用自动换行
            self._label.adjustSize()
            actual_width = text_width + 25
        else:
            # 如果超过最大宽度，则启用自动换行
            self._label.setWordWrap(True)
            # 计算换行后的文本区域
            text_rect = fm.boundingRect(
                0, 0, self._max_width - 30, 1000,
                Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter,
                self._label.text()
            )
            actual_width = self._max_width
            
        # 设置标签宽度并让它调整高度
        self._label.setFixedWidth(actual_width)
        self._label.adjustSize()
        
        # 调整窗口大小
        self.resize(self._label.width(), self._label.height())
        # 设置标签位置和大小（填满整个窗口）
        self._label.setGeometry(0, 0, self.width(), self.height())
        
    def show(self):
        """显示工具提示"""
        if not self.isVisible():
            # 获取鼠标位置
            pos = self.cursor().pos()
            
            # 设置初始位置和大小
            target_geometry = QRect(
                pos.x() + 10,  # 增加与鼠标的距离
                pos.y() - self.height() - 8,  # 向上偏移更多
                self.width(),
                self.height()
            )
            start_geometry = QRect(
                target_geometry.x(),
                target_geometry.y(),
                1,  # 初始宽度
                target_geometry.height()
            )
            
            # 设置动画
            self._geometry_animation.setStartValue(start_geometry)
            self._geometry_animation.setEndValue(target_geometry)
            
            self._opacity_animation.setStartValue(0.0)
            self._opacity_animation.setEndValue(1.0)
            
            # 显示窗口并开始动画
            super().show()
            self._geometry_animation.start()
            self._opacity_animation.start()
        
    def hide(self):
        """隐藏工具提示"""
        if self.isVisible():
            self._opacity_animation.setStartValue(self.windowOpacity())
            self._opacity_animation.setEndValue(0.0)
            self._opacity_animation.start()
        