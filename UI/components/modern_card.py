from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QPainterPath, QColor

class ModernCard(QWidget):
    """现代化卡片组件"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self._content = None
        
        # 初始化属性
        self._is_dark_mode = False
        self._shadow_strength = 30
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self.set_dark_mode)
            self._is_dark_mode = self.theme_manager.isDarkMode()
        
        # 设置UI和效果
        self._setup_ui()
        self._setup_effects()
        self._setup_animations()
        
        # 允许背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 设置默认尺寸
        self.setFixedSize(200, 180)
        
        self._update_style()
        
    def _setup_ui(self):
        """初始化UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 20, 15)
        self.layout.setSpacing(10)
        
        # 标题标签
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        self.layout.addWidget(self.title_label)
        
        # 内容区域的占位符
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 5, 0, 5)
        self.layout.addWidget(self.content_widget)
        
    def _setup_effects(self):
        """设置阴影效果"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)
        
    def _setup_animations(self):
        """设置动画效果"""
        # 阴影动画
        self._shadow_animation = QPropertyAnimation(self, b"shadow_strength", self)
        self._shadow_animation.setDuration(200)
        self._shadow_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def _get_shadow_strength(self):
        return self._shadow_strength
        
    def _set_shadow_strength(self, value):
        self._shadow_strength = value
        shadow = self.graphicsEffect()
        if shadow:
            shadow.setColor(QColor(0, 0, 0, int(value)))
            
    # 定义属性
    shadow_strength = Property(float, _get_shadow_strength, _set_shadow_strength)
    
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._shadow_animation.setEndValue(50)
        self._shadow_animation.start()
        self.update()  # 触发重绘以更新背景色
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        if not self._is_dark_mode:
            # 亮色主题下恢复阴影
            self._shadow_animation.setEndValue(30)
            self._shadow_animation.start()
        self.update()  # 触发重绘以更新背景色
        super().leaveEvent(event)
        
    def set_content(self, widget):
        """设置卡片内容"""
        if self._content:
            self.content_layout.removeWidget(self._content)
            self._content.deleteLater()
        self._content = widget
        self.content_layout.addWidget(widget)
        
    def set_dark_mode(self, is_dark):
        """设置主题模式"""
        self._is_dark_mode = is_dark
        self._update_style()
        self.update()  # 触发重绘以更新背景色
        
    def _update_style(self):
        """更新样式"""
        if self._is_dark_mode:
            self.title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #ecf0f1;
                }
            """)
        else:
            self.title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                }
            """)
        
    def paintEvent(self, event):
        """绘制卡片背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, self.width(), self.height()), 12, 12)
        
        # 设置背景颜色
        if self._is_dark_mode:
            # 暗色主题：鼠标悬停时背景变亮
            is_hovered = self.underMouse()
            base_color = 31 if is_hovered else 30
            painter.fillPath(path, QColor(base_color, base_color, base_color, 180))
        else:
            # 亮色主题：保持不变
            painter.fillPath(path, QColor(255, 255, 255, 230))
        
    def set_card_size(self, width, height):
        """手动设置卡片大小，不受默认最小尺寸限制"""
        self.setMinimumSize(0, 0)  # 清除最小尺寸限制
        self.setFixedSize(width, height)