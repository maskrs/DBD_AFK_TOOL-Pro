from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QPropertyAnimation, Property, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QWidget, QApplication


class ModernSwitch(QWidget):
    """现代化开关组件"""
    
    toggled = Signal(bool)  # 状态改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(40, 20)
        self.setMaximumSize(45, 30)
        self.setCursor(Qt.PointingHandCursor)
        
        # 状态
        self._checked = False
        self._progress = 0  # 动画进度
        self._scale_factor = 1  # 缩放因子
        self._is_pressed = False
        self._is_dark_mode = False
        
        # 获取系统强调色和主题管理器
        self._accent_color = QApplication.instance().palette().highlight().color()
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self.theme_manager.accentColorChanged.connect(self._on_accent_color_changed)
            self._is_dark_mode = self.theme_manager.isDarkMode()
            
            # 更新强调色
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])
        
        # 颜色属性
        self._background_color_on = self._accent_color  # 开启状态背景色
        self._background_color_off = QColor(245, 245, 245)  # 关闭状态背景色
        self._thumb_color_on = QColor(255, 255, 255)  # 开启状态滑块色
        self._thumb_color_off = QColor("#D2D2D2")  # 关闭状态滑块色
        self._border_color = QColor("#D2D2D2")  # 边框色
        
        # 初始化动画
        self._progress_ani = QPropertyAnimation(self, b"progress", self)
        self._progress_ani.setDuration(150)  # 动画持续时间
        self._progress_ani.setEasingCurve(QEasingCurve.OutCubic)  # 缓动曲线
        
        self._scale_ani = QPropertyAnimation(self, b"scaleFactor", self)
        self._scale_ani.setDuration(150)
        self._scale_ani.setEasingCurve(QEasingCurve.OutCubic)
        
        # 初始化颜色
        self._init_colors()
        
    def _on_theme_changed(self, is_dark: bool):
        """主题改变时更新样式"""
        self._is_dark_mode = is_dark
        self._update_colors()
        self.update()
        
    def _on_accent_color_changed(self, accent: dict):
        """强调色改变时更新样式"""
        self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])
        self._update_colors()
        self.update()
        
    @Property(float)
    def progress(self):
        return self._progress
        
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()
        
    @Property(float)
    def scaleFactor(self):
        return self._scale_factor
        
    @scaleFactor.setter
    def scaleFactor(self, value):
        self._scale_factor = value
        self.update()
        
    def _init_colors(self):
        """初始化颜色"""
        self._update_colors()
        
    def _update_colors(self):
        """更新颜色"""
        if self._is_dark_mode:
            self._background_color_on = self._accent_color  # 开启状态背景色
            self._background_color_off = QColor(45, 40, 43)  # 关闭状态背景色
            self._thumb_color_on = QColor(231,229,225)  # 开启状态滑块色
            self._thumb_color_off = QColor(160, 160, 160)  # 关闭状态滑块色
            self._border_color = QColor(48, 48, 48)  # 边框色
        else:
            self._background_color_on = self._accent_color  # 开启状态背景色
            self._background_color_off = QColor(245, 245, 245)  # 关闭状态背景色
            self._thumb_color_on = QColor(255, 255, 255)  # 开启状态滑块色
            self._thumb_color_off = QColor("#D2D2D2")  # 关闭状态滑块色
            self._border_color = QColor("#D2D2D2")  # 边框色
            
    def _draw_track(self, painter: QPainter, rect: QRectF):
        """绘制轨道"""
        # 创建轨道路径
        track_path = QPainterPath()
        track_height = rect.height()
        track_rect = QRectF(
            rect.x() + 1,  # 左边距
            rect.y() ,  # 上边距
            rect.width() - 2,  # 右边距
            track_height -1 # 高度
        )
        track_radius = track_height / 2
        track_path.addRoundedRect(track_rect, track_radius, track_radius)
        
        # 根据进度混合颜色
        if self._progress > 0:
            bg_color = self._mix_colors(
                self._background_color_off,
                self._background_color_on,
                self._progress
            )
            painter.setBrush(bg_color)
            painter.setPen(Qt.NoPen)
        else:
            painter.setBrush(self._background_color_off)
            painter.setPen(QPen(self._border_color, 1.0))
            
        painter.drawPath(track_path)
        
    def _draw_thumb(self, painter: QPainter, rect: QRectF):
        """绘制滑块"""
        # 计算滑块大小和位置
        margin = 4  # 增加边距
        thumb_radius = (rect.height() - 2 * margin) / 2
        thumb_rect = QRectF(0, 0, thumb_radius * 2, thumb_radius * 2)
        
        # 计算滑块的水平位置
        track_width = rect.width() - thumb_rect.width() - 2 * margin
        x = margin + track_width * self._progress
        y = margin
        
        # 移动滑块到正确位置
        thumb_rect.moveTopLeft(QPointF(x, y))
        
        # 创建滑块路径
        thumb_path = QPainterPath()
        thumb_path.addEllipse(thumb_rect)
        
        # 设置滑块颜色
        thumb_color = self._mix_colors(
            self._thumb_color_off,
            self._thumb_color_on,
            self._progress
        )
        
        # 绘制滑块阴影
        shadow_color = QColor(0, 0, 0, 30)
        shadow_rect = thumb_rect.adjusted(-1, -1, 1, 1)
        shadow_path = QPainterPath()
        shadow_path.addEllipse(shadow_rect)
        painter.setBrush(shadow_color)
        painter.setPen(Qt.NoPen)
        painter.drawPath(shadow_path)
        
        # 绘制滑块
        painter.setBrush(thumb_color)
        painter.setPen(Qt.NoPen)
        painter.drawPath(thumb_path)
        
    def _mix_colors(self, color1: QColor, color2: QColor, progress: float) -> QColor:
        """混合两种颜色"""
        return QColor(
            int(color1.red() * (1 - progress) + color2.red() * progress),
            int(color1.green() * (1 - progress) + color2.green() * progress),
            int(color1.blue() * (1 - progress) + color2.blue() * progress),
            int(color1.alpha() * (1 - progress) + color2.alpha() * progress)
        )
        
    def paintEvent(self, event):
        """绘制事件"""
        # 获取设备像素比
        device_pixel_ratio = self.devicePixelRatioF()
        
        # 创建缓冲区
        buffer = QPixmap(self.size() * device_pixel_ratio)
        buffer.setDevicePixelRatio(device_pixel_ratio)
        buffer.fill(Qt.transparent)
        
        # 创建画笔
        painter = QPainter(buffer)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 获取绘制区域
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        
        # 绘制轨道和滑块
        self._draw_track(painter, rect)
        self._draw_thumb(painter, rect)
        
        # 结束缓冲区绘制
        painter.end()
        
        # 绘制到窗口
        window_painter = QPainter(self)
        window_painter.setRenderHint(QPainter.Antialiasing)
        window_painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 应用缩放动画
        if self._scale_factor != 1:
            window_painter.translate(rect.center())
            window_painter.scale(self._scale_factor, self._scale_factor)
            window_painter.translate(-rect.center())
            
        window_painter.drawPixmap(0, 0, buffer)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            self._scale_ani.setEndValue(0.95)
            self._scale_ani.start()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton and self._is_pressed:
            self._is_pressed = False
            self._scale_ani.setEndValue(1.0)
            self._scale_ani.start()
            self.setChecked(not self._checked)
            
    def enterEvent(self, event):
        """鼠标进入事件"""
        self.setCursor(Qt.PointingHandCursor)
        
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._is_pressed = False
        self._scale_factor = 1.0
        self.update()
        
    def setChecked(self, checked: bool):
        """设置选中状态"""
        if self._checked != checked:
            self._checked = checked
            self._progress_ani.setEndValue(1.0 if checked else 0.0)
            self._progress_ani.start()
            self.toggled.emit(checked)
            
    def isChecked(self) -> bool:
        """获取选中状态"""
        return self._checked 