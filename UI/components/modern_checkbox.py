from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Property, QRectF, QSize, QPropertyAnimation, QEasingCurve, Signal
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtSvg import QSvgRenderer
from io import BytesIO

class ModernCheckBox(QWidget):
    """现代化多选框组件"""
    
    # 状态改变信号
    toggled = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化基本属性
        self._is_dark_mode = False
        self._is_hovered = False
        self._is_checked = False
        self._animation_progress = 0.0
        self._check_progress = 0.0
        
        # 指示器属性
        self._indicator_size = 20
        self._indicator_border = 2
        self._indicator_spacing = 8
        self._indicator_radius = 4
        
        # 初始化颜色
        self._accent_color = QColor("#0078d4")
        self._text_color = QColor("#2D2932")
        self._border_color = QColor("#ddd9d9")
        self._background_color = QColor(254, 254, 254)
        
        # 初始化样式
        self.setFont(QFont("Segoe UI", 10))
        
        # 设置悬停动画
        self._hover_animation = QPropertyAnimation(self, b"animation_progress", self)
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 设置选中动画
        self._check_animation = QPropertyAnimation(self, b"check_progress", self)
        self._check_animation.setDuration(200)
        self._check_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # 加载勾选图标
        self._check_icon = QSvgRenderer()
        self._check_icon.load(self._get_check_icon_data())
        
        # 设置鼠标追踪
        self.setMouseTracking(True)
        
        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self.theme_manager.accentColorChanged.connect(self._on_accent_color_changed)
            self._is_dark_mode = self.theme_manager.isDarkMode()
            self._update_colors()
        
    def _get_check_icon_data(self) -> bytes:
        """获取勾选图标SVG数据"""
        svg_data = '''<?xml version="1.0" encoding="UTF-8"?>
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 507.506 507.506">
            <path d="M163.865,436.934c-14.406,0.006-28.222-5.72-38.4-15.915L9.369,304.966c-12.492-12.496-12.492-32.752,0-45.248l0,0
            c12.496-12.492,32.752-12.492,45.248,0l109.248,109.248L452.889,79.942c12.496-12.492,32.752-12.492,45.248,0l0,0
            c12.492,12.496,12.492,32.752,0,45.248L202.265,421.019C192.087,431.214,178.271,436.94,163.865,436.934z" 
            fill="#FFFFFF"/>
        </svg>'''
        return svg_data.encode()
        
    def _update_colors(self):
        """更新颜色"""
        if hasattr(self, 'theme_manager'):
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])
            
        if self._is_dark_mode:
            self._text_color = QColor("#DFDFDF")
            self._border_color = QColor("#3b3235")
            self._background_color = QColor(50, 42, 49)
            # 设置暗色模式下的字体
            font = self.font()
            font.setWeight(QFont.Bold)  # 使用粗体
            self.setFont(font)
        else:
            self._text_color = QColor("#2D2932")
            self._border_color = QColor("#ddd9d9") 
            self._background_color = QColor(254, 254, 254)
            # 恢复正常字体
            font = self.font()
            font.setWeight(QFont.Normal)
            self.setFont(font)
            
        self.update()
        
    def _on_theme_changed(self, is_dark: bool):
        """主题切换响应"""
        self._is_dark_mode = is_dark
        self._update_colors()
        
    def _on_accent_color_changed(self, accent_color: dict):
        """强调色变化响应"""
        self._update_colors()
        
    @Property(float)
    def animation_progress(self) -> float:
        return self._animation_progress
        
    @animation_progress.setter
    def animation_progress(self, value: float):
        self._animation_progress = value
        self.update()
        
    @Property(float)
    def check_progress(self) -> float:
        return self._check_progress
        
    @check_progress.setter
    def check_progress(self, value: float):
        self._check_progress = value
        self.update()
        
    def text(self) -> str:
        """获取文本"""
        return self._text
        
    def setText(self, text: str):
        """设置文本"""
        self._text = text
        self.updateGeometry()
        
    def isChecked(self) -> bool:
        """获取选中状态"""
        return self._is_checked
        
    def setChecked(self, checked: bool):
        """设置选中状态"""
        if self._is_checked != checked:
            self._is_checked = checked
            self._check_animation.setStartValue(0.0 if checked else 1.0)
            self._check_animation.setEndValue(1.0 if checked else 0.0)
            self._check_animation.start()
            self.toggled.emit(checked)
            
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._is_checked)
            
    def enterEvent(self, event):
        """鼠标进入事件"""
        self._is_hovered = True
        self._hover_animation.setStartValue(self._animation_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._is_hovered = False
        self._hover_animation.setStartValue(self._animation_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
    def sizeHint(self) -> QSize:
        """推荐尺寸"""
        fm = self.fontMetrics()
        text_width = fm.horizontalAdvance(self._text if hasattr(self, '_text') else "")
        text_height = fm.height()
        return QSize(
            self._indicator_size + self._indicator_spacing + text_width + 4,  # 添加4像素的右边距
            max(self._indicator_size, text_height) + 4  # 添加4像素的垂直边距
        )
        
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)  # 添加文字抗锯齿
        
        # 获取绘制区域
        rect = self.rect()
        
        # 计算指示器位置
        indicator_y = (rect.height() - self._indicator_size) // 2
        indicator_rect = QRectF(2, indicator_y, self._indicator_size, self._indicator_size)
        
        # 绘制边框和背景
        border_color = self._accent_color if self._is_checked else self._border_color
        if self._animation_progress > 0 and not self._is_checked:
            # 在hover状态下，如果未选中，则边框颜色向accent color过渡
            border_color = QColor(
                int(self._border_color.red() + (self._accent_color.red() - self._border_color.red()) * self._animation_progress),
                int(self._border_color.green() + (self._accent_color.green() - self._border_color.green()) * self._animation_progress),
                int(self._border_color.blue() + (self._accent_color.blue() - self._border_color.blue()) * self._animation_progress)
            )
        
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(self._accent_color if self._is_checked else self._background_color)
        painter.drawRoundedRect(indicator_rect, self._indicator_radius, self._indicator_radius)
        
        # 绘制勾选图标（从中心缩放）
        if self._check_progress > 0:
            painter.save()
            
            # 计算中心点
            center_x = indicator_rect.x() + indicator_rect.width() / 2
            center_y = indicator_rect.y() + indicator_rect.height() / 2
            
            # 移动到中心点
            painter.translate(center_x, center_y)
            
            # 应用缩放
            painter.scale(self._check_progress, self._check_progress)
            
            # 移回原位置（考虑缩放后的偏移）
            icon_rect = QRectF(-6, -6, 12, 12)  # 12x12的图标区域，中心点为原点
            
            self._check_icon.render(painter, icon_rect)
            painter.restore()
            
        # 绘制文本
        if hasattr(self, '_text'):
            text_rect = QRectF(
                self._indicator_size + self._indicator_spacing + 2,
                2,
                rect.width() - self._indicator_size - self._indicator_spacing - 4,
                rect.height() - 4
            )
            
            # 设置文字渲染选项
            font = painter.font()
            font.setHintingPreference(QFont.PreferFullHinting)  # 使用完整字体微调
            painter.setFont(font)
            
            painter.setPen(self._text_color)
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft | Qt.TextDontClip, self._text)
        
    def setDarkMode(self, is_dark: bool):
        """设置暗色模式"""
        if self._is_dark_mode != is_dark:
            self._is_dark_mode = is_dark
            self._update_colors() 