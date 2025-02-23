from PySide6.QtWidgets import (QWidget, QVBoxLayout, 
                               QGraphicsDropShadowEffect, QScrollArea, QFrame,
                               QApplication)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QPainterPath

class Drawer(QWidget):
    """现代化抽屉组件，从右侧滑出的次级页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark_mode = False
        self._accent_color = None
        self._drawer_width = 420  # 抽屉宽度
        self._slide_position = 0  # 滑动位置
        self._opacity = 0.0  # 遮罩透明度
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self.set_dark_mode)
            self.theme_manager.accentColorChanged.connect(self._update_accent_color)
            self._is_dark_mode = self.theme_manager.isDarkMode()
            self._accent_color = self.theme_manager.accent_color
            
        # 创建UI
        self._setup_ui()
        
        # 更新样式
        self._update_style()
        
        # 初始化动画
        self._setup_animations()
        
    def _setup_ui(self):
        """初始化UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建背景遮罩
        self.background_widget = QWidget()
        self.background_widget.setObjectName("background_widget")
        
        # 背景布局
        self.background_layout = QVBoxLayout(self.background_widget)
        self.background_layout.setContentsMargins(0, 0, 0, 0)
        self.background_layout.setSpacing(0)
        
        # 抽屉容器
        self.drawer_container = QWidget()
        self.drawer_container.setObjectName("drawer_container")
        self.drawer_container.setFixedWidth(self._drawer_width)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self.drawer_container)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(-2, 0)
        self.drawer_container.setGraphicsEffect(shadow)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea(self.drawer_container)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # 创建滚动区域的内容容器
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(24, 24, 24, 24)
        self.content_layout.setSpacing(16)
        
        # 设置滚动区域的内容
        self.scroll_area.setWidget(self.content_widget)
        
        # 抽屉容器布局
        drawer_layout = QVBoxLayout(self.drawer_container)
        drawer_layout.setContentsMargins(0, 0, 0, 0)
        drawer_layout.setSpacing(0)
        drawer_layout.addWidget(self.scroll_area)
        
        # 将抽屉容器添加到背景布局右侧
        self.background_layout.addWidget(self.drawer_container, 0, Qt.AlignRight)
        
        # 将背景添加到主布局
        self.main_layout.addWidget(self.background_widget)
        
    def _setup_animations(self):
        """设置动画效果"""
        # 背景淡入动画
        self.background_anim = QPropertyAnimation(self, b"opacity")
        self.background_anim.setDuration(300)
        self.background_anim.setStartValue(0.0)
        self.background_anim.setEndValue(0.6)
        self.background_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # 抽屉滑入动画
        self.drawer_anim = QPropertyAnimation(self, b"slidePosition")
        self.drawer_anim.setDuration(300)
        self.drawer_anim.setStartValue(self._drawer_width)
        self.drawer_anim.setEndValue(0)
        self.drawer_anim.setEasingCurve(QEasingCurve.OutCubic)
        
    def _update_style(self):
        """更新样式"""
        # 背景色
        bg_color = "#1e1e1e" if self._is_dark_mode else "#ffffff"
        
        # 边框色
        border_color = "rgba(255, 255, 255, 0.15)" if self._is_dark_mode else "rgba(0, 0, 0, 0.08)"
        
        # 滚动条样式
        scroll_bar_bg = "#2c2c2c" if self._is_dark_mode else "#f0f0f0"
        scroll_bar_handle = "#404040" if self._is_dark_mode else "#c0c0c0"
        scroll_bar_handle_hover = "#4f4f4f" if self._is_dark_mode else "#a0a0a0"
        
        self.setStyleSheet(f"""
            QWidget#background_widget {{
                background-color: transparent;
            }}
            
            QWidget#drawer_container {{
                background: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            
            QScrollArea#scroll_area {{
                background: transparent;
                border: none;
                border-radius: 12px;
            }}
            
            QWidget#content_widget {{
                background: transparent;
                border-radius: 12px;
            }}
            
            QScrollBar:vertical {{
                background: {scroll_bar_bg};
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {scroll_bar_handle};
                min-height: 30px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {scroll_bar_handle_hover};
            }}
            
            QScrollBar::add-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
    def set_dark_mode(self, is_dark):
        """设置主题模式"""
        self._is_dark_mode = is_dark
        self._update_style()
        
    def _update_accent_color(self, accent_color):
        """更新强调色"""
        self._accent_color = accent_color
        self._update_style()
        
    def get_slide_position(self):
        """获取滑动位置"""
        return self._slide_position
        
    def set_slide_position(self, pos):
        """设置滑动位置"""
        self._slide_position = pos
        # 更新抽屉容器的位置（从右侧开始计算）
        if self.isVisible():
            right_pos = self.width() - self._drawer_width + pos
            # 保持垂直位置不变
            self.drawer_container.move(right_pos, self.drawer_container.y())
        
    def get_opacity(self):
        """获取遮罩透明度"""
        return self._opacity
        
    def set_opacity(self, value):
        """设置遮罩透明度"""
        self._opacity = value
        self.update()  # 触发重绘
        
    # 定义属性
    slidePosition = Property(int, get_slide_position, set_slide_position)
    opacity = Property(float, get_opacity, set_opacity)
    
    def paintEvent(self, event):
        """绘制事件，用于绘制遮罩"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角遮罩路径
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 8, 8)
        
        # 绘制半透明黑色遮罩
        painter.fillPath(path, QColor(0, 0, 0, int(255 * self._opacity)))
        
    def show_drawer(self):
        """显示抽屉"""
        # 获取顶级窗口
        top_window = QApplication.activeWindow()
        
        if top_window:
            # 使用frameGeometry获取完整的窗口大小（包括边框）
            window_rect = top_window.frameGeometry()
            # 设置抽屉大小和位置
            self.setFixedSize(window_rect.size())
            self.move(window_rect.topLeft())
            
            # 设置抽屉容器高度比窗口小一些，并居中显示
            drawer_height = window_rect.height() - 16  # 上下各留出8px的间距
            self.drawer_container.setFixedHeight(drawer_height)
            
            # 初始化抽屉位置（在右侧）
            # 计算右侧位置：窗口宽度 - 抽屉宽度 + 当前滑动位置
            right_pos = window_rect.width() - self._drawer_width + self._slide_position
            top_pos = (window_rect.height() - drawer_height) // 2  # 垂直居中
            self.drawer_container.move(right_pos, top_pos)
        
        # 显示抽屉
        self.show()
        
        # 开始动画
        self.background_anim.start()
        self.drawer_anim.start()
        
    def add_widget(self, widget):
        """添加部件到抽屉内容区域"""
        self.content_layout.addWidget(widget)
        
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        # 获取点击位置
        pos = event.pos()
        # 获取抽屉容器的几何区域
        drawer_rect = self.drawer_container.geometry()
        
        # 如果点击位置不在抽屉容器内，则关闭抽屉
        if not drawer_rect.contains(pos):
            self.close_drawer()
            event.accept()
        else:
            event.ignore()  # 让事件继续传递给子部件
            
    def close_drawer(self):
        """关闭抽屉"""
        # 断开之前的连接（如果有）
        try:
            self.drawer_anim.finished.disconnect(self._on_close_animation_finished)
        except:
            pass
            
        # 反转动画
        self.background_anim.setDirection(QPropertyAnimation.Backward)
        self.drawer_anim.setDirection(QPropertyAnimation.Backward)
        
        # 开始动画
        self.background_anim.start()
        self.drawer_anim.start()
        
        # 动画结束后关闭窗口（使用一次性连接）
        self.drawer_anim.finished.connect(self._on_close_animation_finished)
        
    def _on_close_animation_finished(self):
        """关闭动画完成后的处理"""
        # 断开连接
        self.drawer_anim.finished.disconnect(self._on_close_animation_finished)
        # 重置动画方向
        self.background_anim.setDirection(QPropertyAnimation.Forward)
        self.drawer_anim.setDirection(QPropertyAnimation.Forward)
        # 关闭窗口
        self.close() 