from PySide6.QtWidgets import QRadioButton
from PySide6.QtCore import Qt, Property, QRectF, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont

class ModernRadioButton(QRadioButton):
    """现代化单选框组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化基本属性
        self._is_dark_mode = False
        self._is_hovered = False
        self._animation_progress = 0.0
        self._check_progress = 0.0
        
        # 指示器属性
        self._indicator_radius = 9
        self._indicator_border = 2
        self._indicator_spacing = 8
        self._inner_radius = 5
        
        # 初始化颜色
        self._accent_color = QColor("#0078d4")  # 默认强调色
        self._text_color = QColor("#2D2932")
        self._border_color = QColor("#ddd9d9")
        self._background_color = QColor(254, 254, 254)
        
        # 初始化样式
        self.setFont(QFont("Segoe UI", 10))
        
        # 设置悬停动画
        self._hover_animation = QPropertyAnimation(self, b"animation_progress", self)
        self._hover_animation.setDuration(150)
        self._hover_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # 设置选中动画
        self._check_animation = QPropertyAnimation(self, b"check_progress", self)
        self._check_animation.setDuration(200)
        self._check_animation.setEasingCurve(QEasingCurve.OutQuad)
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self.theme_manager.accentColorChanged.connect(self._on_accent_color_changed)
            self._is_dark_mode = self.theme_manager.isDarkMode()
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])
            self._update_colors()
        
    def _update_colors(self):
        """更新颜色"""
        if hasattr(self, 'theme_manager'):
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])
            
        if self._is_dark_mode:
            self._text_color = QColor("#DFDFDF")
            self._border_color = QColor("#3b3235")
            self._background_color = QColor(50, 42, 49)
        else:
            self._text_color = QColor("#2D2932")
            self._border_color = QColor("#ddd9d9")
            self._background_color = QColor(254, 254, 254)
        

        font = self.font()
        if self._is_dark_mode:
            font.setWeight(QFont.Normal)  # 暗色模式下使用粗体
        else:
            font.setWeight(QFont.Normal)  # 亮色模式下使用正常字重
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
        
    def nextCheckState(self):
        """重写选中状态切换，添加动画"""
        super().nextCheckState()  # 恢复父类的状态切换逻辑
        # 开始选中动画
        self._check_animation.setStartValue(0.0 if self.isChecked() else 1.0)
        self._check_animation.setEndValue(1.0 if self.isChecked() else 0.0)
        self._check_animation.start()
        
    def setChecked(self, checked: bool):
        """重写设置选中状态方法"""
        was_checked = self.isChecked()
        super().setChecked(checked)
        # 只有当状态真正改变时才触发动画
        if was_checked != checked:
            self._check_animation.setStartValue(0.0 if checked else 1.0)
            self._check_animation.setEndValue(1.0 if checked else 0.0)
            self._check_animation.start()
        
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self._is_hovered = True
        self._hover_animation.setStartValue(self._animation_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self._is_hovered = False
        self._hover_animation.setStartValue(self._animation_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
    def sizeHint(self) -> QSize:
        """推荐尺寸"""
        # 获取文本度量
        fm = self.fontMetrics()
        
        # 计算文本区域大小
        text_rect = fm.boundingRect(
            0, 0, 1000, 1000,  # 提供足够大的初始区域
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter,
            self.text()
        )
        
        # 计算所需的总宽度（指示器 + 间距 + 文本）
        total_width = (self._indicator_radius * 2) + self._indicator_spacing + text_rect.width()
        
        # 计算所需的总高度（取文本高度和指示器高度的较大值）
        total_height = max(text_rect.height(), self._indicator_radius * 2)
        
        # 添加一些边距
        total_width += 10  # 左右各5px边距
        total_height += 10  # 上下各5px边距
        
        return QSize(total_width, total_height)
        
    def paintEvent(self, event):
        """绘制单选框"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取绘制区域
        rect = self.rect()
        
        # 计算指示器位置
        indicator_x = 5
        indicator_y = (rect.height() - self._indicator_radius * 2) / 2
        indicator_rect = QRectF(
            indicator_x, indicator_y,
            self._indicator_radius * 2, self._indicator_radius * 2
        )
        
        # 绘制悬停效果
        if self._animation_progress > 0:
            hover_path = QPainterPath()
            hover_rect = indicator_rect.adjusted(-1, -1, 1, 1)
            hover_path.addEllipse(hover_rect)
            hover_color = QColor(self._accent_color)
            hover_color.setAlpha(int(150 * self._animation_progress))  # 降低最大透明度
            painter.setPen(Qt.NoPen)
            painter.fillPath(hover_path, hover_color)
            
        # 绘制外圈
        if self.isChecked():
            painter.setPen(self._accent_color)
        else:
            painter.setPen(self._border_color)
        painter.setBrush(self._background_color)
        painter.drawEllipse(indicator_rect)
        
        # 绘制选中状态
        if self._check_progress > 0:
            # 计算内圈位置
            inner_rect = QRectF(
                indicator_x + (self._indicator_radius - self._inner_radius),
                indicator_y + (self._indicator_radius - self._inner_radius),
                self._inner_radius * 2, self._inner_radius * 2
            )
            
            # 绘制内圈
            painter.setPen(Qt.NoPen)
            accent_color = QColor(self._accent_color)
            accent_color.setAlpha(int(255 * self._check_progress))
            painter.setBrush(accent_color)
            painter.drawEllipse(inner_rect)
            
        # 绘制文本
        painter.setPen(self._text_color)
        text_x = indicator_x + self._indicator_radius * 2 + self._indicator_spacing
        text_y = rect.height() / 2 + painter.fontMetrics().height() / 3
        painter.drawText(text_x, text_y, self.text()) 