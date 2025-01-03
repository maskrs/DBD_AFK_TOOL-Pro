from PySide6.QtWidgets import QPushButton, QWidget
from PySide6.QtCore import Qt, Property, Signal, QRectF, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPaintEvent, QFont, QFontMetrics, QLinearGradient
from .tooltip import ToolTip

class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, parent: QWidget = None, highlight: bool = False):
        super().__init__(parent)
        self._highlight = highlight
        self._init_properties()
        self._init_style()
        self._setup_animations()
        
        # 图标相关
        self._icon_size = QSize(16, 16)  # 默认图标大小
        self._icon_spacing = 8  # 图标与文字间距
        
        # 初始化tooltip
        self._tooltip_enabled = False
        self._tooltip = None
        self._tooltip_text = ""
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self._show_tooltip)
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            # 连接主题切换信号
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self.theme_manager.accentColorChanged.connect(self._on_accent_color_changed)
            # 初始化主题
            self._is_dark_mode = self.theme_manager.isDarkMode()
            self._update_colors()
        
    def _init_properties(self):
        """初始化属性"""
        self._scale_factor = 1.0
        self._is_dark_mode = False
        self._is_hovered = False
        self._is_pressed = False
        self._animation_progress = 0.0
        self._press_animation_progress = 1.0  # 按压缩放动画进度
        
        # 边框属性
        self._border_radius = 7
        self._border_width = 1
        
        # 初始化颜色（后续会被主题更新）
        self._update_colors()
        
    def _update_colors(self):
        """更新颜色"""
        if hasattr(self, 'theme_manager'):
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])
        else:
            self._accent_color = QColor("#a681bf")
            
        if self._highlight:
            # 高亮模式
            self._text_color = QColor("#FFFFFF")
            self._background_color = self._accent_color
            self._hover_color = QColor(
                min(self._accent_color.red() + 20, 255),
                min(self._accent_color.green() + 20, 255),
                min(self._accent_color.blue() + 20, 255),
                255
            )
            self._pressed_color = QColor(
                max(self._accent_color.red() - 20, 0),
                max(self._accent_color.green() - 20, 0),
                max(self._accent_color.blue() - 20, 0),
                255
            )
        else:
            # 普通模式
            if self._is_dark_mode:
                self._text_color = QColor("#DFDFDF")
                self._background_color = QColor(50, 42, 49, 242)  # 95% 透明度
                self._hover_color = QColor(67, 56, 58, 230)      # 90% 透明度
                self._pressed_color = QColor(67, 56, 58, 153)    # 60% 透明度
                self._border_color = QColor("#3b3235")
            else:
                self._text_color = QColor("#2D2932")
                self._background_color = QColor(254, 254, 254, 230)  # 90% 透明度
                self._hover_color = QColor(251, 250, 251, 220)       # 更明显的hover效果
                self._pressed_color = QColor(252, 250, 251, 220)     # 更明显的pressed效果
                self._border_color = QColor("#EAE2E5")
        
        # 设置字体粗细
        font = self.font()
        if self._is_dark_mode:
            font.setWeight(QFont.Bold)  # 暗色模式下使用粗体
        else:
            font.setWeight(QFont.Normal)  # 亮色模式下使用正常字重
        self.setFont(font)
        
        self.update()
        
    def _init_style(self):
        """初始化样式"""
        self.setFont(QFont("Segoe UI", 11))
        self.setMinimumSize(36, 36)  # 设置最小尺寸为正方形
        
    def _setup_animations(self):
        """设置动画效果"""
        # 悬停动画
        self._hover_animation = QPropertyAnimation(self, b"animation_progress", self)
        self._hover_animation.setDuration(150)  # 减少动画时长，让颜色变化更快
        self._hover_animation.setEasingCurve(QEasingCurve.OutQuad)  # 使用更快的缓动曲线
        
        # 按压动画
        self._press_animation = QPropertyAnimation(self, b"press_animation_progress", self)
        self._press_animation.setDuration(100)
        self._press_animation.setEasingCurve(QEasingCurve.OutCubic)
        
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
    def press_animation_progress(self) -> float:
        return self._press_animation_progress
        
    @press_animation_progress.setter
    def press_animation_progress(self, value: float):
        self._press_animation_progress = value
        self.update()
        
    def set_highlight(self, highlight: bool):
        """设置高亮模式"""
        if self._highlight != highlight:
            self._highlight = highlight
            self._update_colors()
            
    def setIcon(self, icon):
        """设置图标"""
        super().setIcon(icon)
        self.update()
        
    def setIconSize(self, size: QSize):
        """设置图标大小"""
        self._icon_size = size
        self.update()
        
    def paintEvent(self, event):
        """绘制按钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算缩放后的矩形
        scale = 0.97 + 0.03 * self._press_animation_progress  # 缩放范围：0.97-1.0
        
        # 保存当前状态
        painter.save()
        
        # 设置整体缩放
        painter.translate(self.rect().center())
        painter.scale(scale, scale)
        painter.translate(-self.rect().center())
        
        # 绘制背景
        path = QPainterPath()
        rect = QRectF(self._border_width, self._border_width,
                     self.width() - 2 * self._border_width,
                     self.height() - 2 * self._border_width)
        path.addRoundedRect(rect, self._border_radius, self._border_radius)
        
        # 绘制底色
        painter.fillPath(path, self._background_color)
        
        # 绘制边框（仅普通模式）
        if not self._highlight:
            pen = painter.pen()
            pen.setColor(self._border_color)
            pen.setWidth(self._border_width)
            painter.setPen(pen)
            painter.drawPath(path)
        
        # 绘制悬停/按压效果
        if self._is_pressed:
            painter.fillPath(path, self._pressed_color)
        elif self._animation_progress > 0:
            hover_color = QColor(self._hover_color)
            if not self._highlight:
                # 普通模式下，同时更新边框颜色
                pen = painter.pen()
                if self._is_dark_mode:
                    pen.setColor(QColor("#3b3235"))
                else:
                    pen.setColor(QColor("#ddd9d9"))
                painter.setPen(pen)
                painter.drawPath(path)
            painter.fillPath(path, hover_color)
            
        # 计算文本和图标的位置
        painter.setPen(self._text_color)
            
        # 获取文本尺寸
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(self.text())
        text_height = fm.height()
        
        # 计算总宽度（图标 + 间距 + 文本）
        total_width = text_width
        if not self.icon().isNull():
            total_width += self._icon_size.width()
            if self.text():  # 只有同时有图标和文字时才添加间距
                total_width += self._icon_spacing
            
        # 计算起始x坐标（居中）
        x = (rect.width() - total_width) / 2 + rect.left()
        y = (rect.height() - max(text_height, self._icon_size.height())) / 2 + rect.top()
        
        # 绘制图标
        if not self.icon().isNull():
            icon_y = y + (max(text_height, self._icon_size.height()) - self._icon_size.height()) / 2
            self.icon().paint(painter, QRect(int(x), int(icon_y), 
                                           self._icon_size.width(), self._icon_size.height()))
            if self.text():  # 只有同时有图标和文字时才添加间距
                x += self._icon_size.width() + self._icon_spacing
            
        # 绘制文本
        if self.text():
            text_y = y + (max(text_height, self._icon_size.height()) - text_height) / 2
            painter.drawText(int(x), int(text_y + fm.ascent()), self.text())
        
        # 恢复状态
        painter.restore()
        
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self._is_hovered = True
        self._hover_animation.setStartValue(self._animation_progress)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.start()
        
        # 延迟显示tooltip
        if self._tooltip_enabled:
            self._tooltip_timer.start(500)  # 500ms延迟
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self._is_hovered = False
        self._hover_animation.setStartValue(self._animation_progress)
        self._hover_animation.setEndValue(0.0)
        self._hover_animation.start()
        
        # 取消tooltip显示并隐藏
        self._tooltip_timer.stop()
        self._hide_tooltip()
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            # 开始按压动画
            self._press_animation.setStartValue(self._press_animation_progress)
            self._press_animation.setEndValue(0.0)
            self._press_animation.start()
            self.update()
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._is_pressed = False
            # 开始释放动画
            self._press_animation.setStartValue(self._press_animation_progress)
            self._press_animation.setEndValue(1.0)
            self._press_animation.start()
            self.update()
        super().mouseReleaseEvent(event)
        
    def sizeHint(self) -> QSize:
        """推荐尺寸"""
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text())
        text_height = fm.height()
        
        # 计算内容宽度
        content_width = text_width
        if not self.icon().isNull():
            content_width += self._icon_size.width()
            if self.text():  # 只有同时有图标和文字时才添加间距
                content_width += self._icon_spacing
                
        # 计算最小宽度（确保是最小高度的倍数）
        min_width = max(36, content_width + 30)
        
        # 返回尺寸（确保是正方形或水平矩形）
        return QSize(min_width, 36)
        
    def setTooltip(self, text: str):
        """设置工具提示文本"""
        self._tooltip_text = text
        self._tooltip_enabled = bool(text)
        
        # 如果已经创建了tooltip，更新文本
        if self._tooltip:
            self._tooltip.setText(text)
            
    def _ensure_tooltip(self):
        """确保tooltip已创建"""
        if not self._tooltip and self._tooltip_enabled:
            self._tooltip = ToolTip(self)
            if hasattr(self, 'theme_manager'):
                self._tooltip.theme_manager = self.theme_manager
            self._tooltip.setText(self._tooltip_text)
            
    def _show_tooltip(self):
        """显示工具提示"""
        if self._tooltip_enabled and self._is_hovered:
            self._ensure_tooltip()
            self._tooltip.show()
            
    def _hide_tooltip(self):
        """隐藏工具提示"""
        if self._tooltip:
            self._tooltip.hide() 

class ModernLongPressButton(ModernButton):
    """现代化长按按钮组件"""
    
    # 长按完成信号
    longPressed = Signal()
    
    def __init__(self, parent: QWidget = None, highlight: bool = False):
        # 设置红色系颜色（在父类初始化前）
        self._button_color = QColor("#932A48")  # 基础红色
        self._hover_color = QColor("#973855")   # 深红色
        self._pressed_color = QColor("#973855") # 深红色
        
        super().__init__(parent, highlight)
        
        # 长按状态
        self._is_long_pressing = False
        self._progress = 0.0  # 长按进度
        
        # 长按动画
        self._progress_animation = QPropertyAnimation(self, b"progress", self)
        self._progress_animation.setDuration(100)
        self._progress_animation.setEasingCurve(QEasingCurve.Linear)
        
        # 长按计时器
        self._press_timer = QTimer(self)
        self._press_timer.setInterval(16)  # 60fps
        self._press_timer.timeout.connect(self._update_progress)
        
        # 重置计时器
        self._reset_timer = QTimer(self)
        self._reset_timer.setSingleShot(True)
        self._reset_timer.setInterval(500)
        self._reset_timer.timeout.connect(self._reset_progress)
        
    def _update_colors(self):
        """更新颜色"""
        self._text_color = QColor("#FFFFFF")
        
        if self._is_dark_mode:
            self._background_color = self._button_color
            self._hover_color = QColor("#973855")
            self._pressed_color = QColor("#973855")
            self._border_color = QColor("#922B21")
        else:
            self._background_color = QColor("#B4325A")  # 更亮的基础色
            self._hover_color = QColor("#c03965")       # 更亮的悬停色
            self._pressed_color = QColor("#c03965")     # 更亮的按压色
            self._border_color = QColor("#CB4335")
        
                # 设置字体粗细
        font = self.font()
        if self._is_dark_mode:
            font.setWeight(QFont.Bold)  # 暗色模式下使用粗体
        else:
            font.setWeight(QFont.Normal)  # 亮色模式下使用正常字重
        self.setFont(font)

        self.update()
        
    def paintEvent(self, event):
        """绘制按钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算缩放后的矩形
        scale = 0.97 + 0.03 * self._press_animation_progress  # 缩放范围：0.97-1.0
        
        # 保存当前状态
        painter.save()
        
        # 设置整体缩放
        painter.translate(self.rect().center())
        painter.scale(scale, scale)
        painter.translate(-self.rect().center())
        
        # 绘制背景
        path = QPainterPath()
        rect = QRectF(self._border_width, self._border_width,
                     self.width() - 2 * self._border_width,
                     self.height() - 2 * self._border_width)
        path.addRoundedRect(rect, self._border_radius, self._border_radius)
        
        # 绘制底色
        painter.fillPath(path, self._background_color)
        
        # 绘制边框
        pen = painter.pen()
        pen.setColor(self._border_color)
        pen.setWidth(self._border_width)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 绘制悬停/按压效果
        if self._is_pressed:
            painter.fillPath(path, self._pressed_color)
        elif self._animation_progress > 0:
            hover_color = QColor(self._hover_color)
            painter.fillPath(path, hover_color)
            
        # 绘制进度
        if self._progress > 0:
            # 计算渐变位置
            progress_width = rect.width() * self._progress
            gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
            
            # 设置渐变颜色（半透明）
            if self._is_dark_mode:
                progress_color = QColor(215,65,108, 160)  
            else:
                progress_color = QColor(215,65,108, 210) 
                
            gradient.setColorAt(progress_width / rect.width() - 0.001, progress_color)
            gradient.setColorAt(progress_width / rect.width(), Qt.transparent)
            
            # 绘制进度
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.fillPath(path, gradient)
            
        # 绘制文字（最后绘制，确保在最上层）
        painter.setPen(self._text_color)
        painter.drawText(rect, Qt.AlignCenter, self.text())
        
        # 恢复状态
        painter.restore()
        
    @Property(float)
    def progress(self) -> float:
        return self._progress
        
    @progress.setter
    def progress(self, value: float):
        self._progress = max(0.0, min(value, 1.0))
        self.update()
        
    def _update_progress(self):
        """更新长按进度"""
        step = (1.0 - self._progress) / 16 + 0.001
        self.progress = self._progress + step
        
        if self._progress >= 1.0:
            self._press_timer.stop()
            self._reset_timer.stop()
            self.longPressed.emit()
            self._reset_progress(200)
            
    def _reset_progress(self, delay: int = 0):
        """重置进度"""
        self._progress_animation.setStartValue(self._progress)
        self._progress_animation.setEndValue(0.0)
        self._progress_animation.setDuration(200)
        QTimer.singleShot(delay, self._progress_animation.start)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._is_long_pressing = True
            if not self._press_timer.isActive():
                self._press_timer.start()
                self._reset_timer.stop()
                
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self._is_long_pressing = False
            self._press_timer.stop()
            if self._progress < 1.0:
                self._reset_timer.start()
                
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor)
        if self._progress > 0:
            self._reset_progress()
