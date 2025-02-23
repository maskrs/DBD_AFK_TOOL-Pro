from PySide6.QtWidgets import QWidget, QLabel,  QApplication, QGraphicsDropShadowEffect, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, Signal, QObject,  QSize, QDateTime
from PySide6.QtGui import QPainter, QColor,  QPixmap, QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
from UI.resources import resources_rc
from PySide6.QtCore import QFile

class NotificationContent(QWidget):
    """通知内容组件"""
    
    clicked = Signal()
    
    def __init__(self, message, level, parent=None):
        super().__init__(parent)
        self._theme_wing_width = 32
        
        # 创建背景层
        self.background = QLabel(self)
        self.background.setStyleSheet("border-radius: 6px; border-top-right-radius: 8px")
        
        # 创建面板层
        self.panel = QLabel(self)
        self.panel.setStyleSheet("border-radius: 6px; border-top-left-radius: 2px")
        
        # 创建图标
        self.theme_icon = QSvgWidget(self)
        self.theme_icon.resize(32, 32)
        self.theme_icon.setFixedSize(20, 20)
        
        # 创建内容容器
        self.container = QWidget(self)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(12, 8, 12, 8)
        self.container_layout.setSpacing(0)
        
        # 创建消息标签
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setMinimumWidth(200)  # 设置最小宽度以确保合理换行
        self.message_label.adjustSize()  # 让标签根据内容调整大小
        self.container_layout.addWidget(self.message_label)
        
        # 创建关闭按钮
        self.close_button = QPushButton(self)
        # 根据内容高度动态设置按钮大小
        button_size = min(32, self.height())  # 取高度和32的较小值
        self.close_button.setFixedSize(button_size, button_size)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 4px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
            }
        """)
        self.close_button.clicked.connect(self.parent().hide)
        
        self._update_style(level)
        
    def _update_style(self, level):
        """更新样式"""
        # 获取颜色
        bg_color, accent_color = self.getColor(level)
        icon_path = self.getIcon(level)
        text_color = "#2D2932"
        border_color = "rgba(0, 0, 0, 0.06)"
            
        # 设置背景层样式
        self.background.setStyleSheet(f"""
            QLabel {{
                background-color: {accent_color};
                border-radius: 6px;
                border-top-right-radius: 8px;
                border: none;
            }}
        """)
        
        # 设置面板层样式
        self.panel.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                border-radius: 6px;
                border-top-left-radius: 2px;
                border: 1px solid {border_color};
            }}
        """)
        
        # 设置图标
        icon_path = self.getIcon(level)
        file = QFile(icon_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            svg_content = str(file.readAll().data(), encoding='utf-8')
            file.close()
            svg_content = svg_content.replace('currentColor', text_color)
            self.theme_icon.load(bytes(svg_content, 'utf-8'))
            
        # 设置消息文本样式
        self.message_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-family: 'Segoe UI';
                background: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }}
        """)
        
        # 设置关闭按钮图标颜色
        close_icon_path = ':resources/ic_fluent_checkmark_regular.svg'  # 改为对号图标
        file = QFile(close_icon_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            svg_content = str(file.readAll().data(), encoding='utf-8')
            file.close()
            svg_content = svg_content.replace('currentColor', text_color)
            
            # 创建高分辨率的 pixmap
            device_pixel_ratio = self.devicePixelRatio()
            renderer = QSvgRenderer(bytes(svg_content, 'utf-8'))
            size = self.close_button.size() * device_pixel_ratio
            pixmap = QPixmap(size)
            pixmap.fill(Qt.transparent)
            
            # 使用高质量渲染
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            renderer.render(painter)
            painter.end()
            
            # 设置设备像素比
            pixmap.setDevicePixelRatio(device_pixel_ratio)
            self.close_button.setIcon(QIcon(pixmap))
            self.close_button.setIconSize(QSize(20, 20))
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        size = event.size()
        
        # 调整各层大小和位置
        self.background.resize(size)
        
        # 设置面板位置和大小
        self.panel.setGeometry(
            self._theme_wing_width, 0,
            size.width() - self._theme_wing_width,
            size.height()
        )
        
        # 设置图标位置，考虑高 DPI
        device_pixel_ratio = self.devicePixelRatio()
        icon_size = int(20 * device_pixel_ratio)
        self.theme_icon.setFixedSize(icon_size, icon_size)
        self.theme_icon.move(
            6,
            (size.height() - icon_size) // 2
        )
        
        # 设置内容容器位置和大小
        self.container.setGeometry(
            self._theme_wing_width + 8, 0,
            size.width() - self._theme_wing_width - 48,
            size.height()
        )
        
        # 动态调整关闭按钮大小和位置
        button_size = min(32, size.height() - 8)  # 保留4px边距
        self.close_button.setFixedSize(button_size, button_size)
        icon_size = max(16, int(button_size * 0.6))  # 图标大小为按钮的60%，最小16px
        self.close_button.setIconSize(QSize(icon_size, icon_size))
        
        # 设置关闭按钮位置
        self.close_button.move(
            size.width() - button_size - 4,  # 右边留4px边距
            (size.height() - button_size) // 2  # 垂直居中
        )
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self.parent().fold_timer.stop()
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.parent().fold_timer.start()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
        
    @staticmethod
    def getColor(level):
        """获取不同级别通知的颜色"""
        colors = {
            'info': ['rgba(238, 243, 226, 0.98)', '#90c606'],     # 浅绿背景，绿色主题
            'warning': ['rgba(255, 239, 216, 0.98)', '#ff9924'],  # 浅橙背景，橙色主题
            'error': ['rgba(248, 232, 232, 0.98)', '#d23232'],    # 浅红背景，红色主题
            'success': ['rgba(226, 243, 233, 0.98)', '#06c67b']   # 浅青背景，青色主题
        }
        return colors.get(level, colors['info'])
            
    @staticmethod
    def getIcon(level):
        """获取不同级别的图标"""
        icon_map = {
            'info': ':resources/ic_fluent_info_filled.svg',
            'warning': ':resources/ic_fluent_warning_filled.svg',
            'error': ':resources/ic_fluent_dismiss_circle_filled.svg',
            'success': ':resources/ic_fluent_checkmark_circle_filled.svg'
        }
        return icon_map.get(level, icon_map['info'])
        
    def sizeHint(self):
        """重写sizeHint以提供基于内容的建议大小"""
        # 获取消息文本的大小
        text_rect = self.message_label.fontMetrics().boundingRect(
            0, 0, 300, 1000,  # 最大宽度300，高度1000作为充分大的值
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter,
            self.message_label.text()
        )
        
        # 计算所需的最小宽度和高度
        width = self._theme_wing_width + text_rect.width() + 80  # 80为右侧空间（按钮+边距）
        height = max(64, text_rect.height() + 24)  # 24为上下边距的总和
        
        return QSize(width, height)

class NotificationWidget(QWidget):
    """通知窗口组件"""
    
    closed = Signal()
    clicked = Signal()
    
    def __init__(self, message, level, parent=None):
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 创建内容
        self.content = NotificationContent(message, level, self)
        self.content.clicked.connect(self.clicked.emit)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)  # 添加边距以容纳阴影
        layout.addWidget(self.content)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        self.content.setGraphicsEffect(shadow)  # 将阴影效果应用到内容组件而不是窗口
        
        # 设置最小尺寸
        self.setMinimumSize(340, 100)  # 增加尺寸以容纳阴影和边距
        
        # 创建自动关闭定时器
        self.fold_timer = QTimer(self)
        self.fold_timer.setSingleShot(True)
        self.fold_timer.setInterval(3000)
        self.fold_timer.timeout.connect(self.hide)
        
        # 设置位置和动画
        self._setup_position()
        self._setup_animations()
        
    def _setup_position(self):
        """设置窗口位置"""
        screen = QApplication.primaryScreen()
        if screen:
            available_geometry = screen.availableGeometry()
            screen_width = available_geometry.width()
            screen_height = available_geometry.height()
        else:
            screen_width = 1920
            screen_height = 1080
            
        # 获取内容建议的大小并设置窗口大小
        content_size = self.content.sizeHint()
        width = max(340, min(600, content_size.width() + 40))  # 40为左右边距
        height = max(100, min(200, content_size.height() + 36))  # 36为上下边距的总和
        self.setFixedSize(width, height)
        
        # 计算位置（屏幕上方居中）
        x = int((screen_width - width) / 2)
        y = int(screen_height * 0.1)  # 屏幕高度的10%处
        self.move(x, y)
        
    def _setup_animations(self):
        """设置动画效果"""
        # 位置动画
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(300)
        self.pos_animation.setEasingCurve(QEasingCurve.OutBack)  # 使用OutBack效果使动画更生动
        
        # 不透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def show(self):
        """重写show方法，添加动画效果"""
        super().show()
        # 设置起始位置（从上方20像素处开始）
        start_y = self.y() - 20
        self.pos_animation.setStartValue(QPoint(self.x(), start_y))
        self.pos_animation.setEndValue(self.pos())
        
        # 设置不透明度动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        
        # 开始动画
        self.pos_animation.start()
        self.opacity_animation.start()
        
        # 启动自动关闭定时器
        self.fold_timer.start()
        
    def hide(self):
        """重写hide方法，添加消失动画"""
        # 设置不透明度动画
        self.opacity_animation.setStartValue(self.windowOpacity())
        self.opacity_animation.setEndValue(0.0)
        
        # 设置位置动画（向上消失）
        end_y = self.y() - 20
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(self.x(), end_y))
        
        # 连接动画完成信号
        self.opacity_animation.finished.connect(super().hide)
        self.opacity_animation.finished.connect(lambda: self.closed.emit())
        
        # 开始动画
        self.pos_animation.start()
        self.opacity_animation.start()
        
    def paintEvent(self, event):
        """重写绘制事件以确保正确的窗口区域"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 清空背景
        painter.fillRect(self.rect(), Qt.transparent)
        painter.end()

class NotificationManager(QObject):
    """通知管理器"""
    
    showNotificationSignal = Signal(str, str, int)
    notificationClicked = Signal()
    
    def __init__(self):
        super().__init__()
        self.current_notification = None
        self.notification_queue = []  # 通知队列
        self.is_showing = False  # 是否正在显示通知
        self.last_message = None  # 上一条消息内容
        self.last_time = 0  # 上一次显示时间
        self.last_source = None  # 上一个消息来源
        self.throttle_interval = 1000  # 节流时间间隔（毫秒）
        self.default_duration = 3000  # 默认显示时间（毫秒）
        self.showNotificationSignal.connect(self.showNotification)
        
    def setDefaultDuration(self, duration):
        """设置默认显示时间
        Args:
            duration: 显示时长(毫秒)
        """
        self.default_duration = duration
        
    def showNotification(self, message, level="info", duration=None, source=None):
        """显示通知
        Args:
            message: 通知消息
            level: 通知级别 (info/warning/error/success)
            duration: 显示时长(毫秒)，如果为None则使用默认时长
            source: 消息来源标识，用于区分不同来源的消息
        """
        current_time = QDateTime.currentMSecsSinceEpoch()
        
        # 如果是新的消息来源，清除当前通知和队列
        if source is not None and source != self.last_source:
            self.closeAllNotifications()
            self.last_source = source
            self.last_message = None  # 重置上一条消息
            self.last_time = 0  # 重置时间
        # 如果消息相同且在节流时间内，且来源相同，则忽略
        elif (message == self.last_message and 
              current_time - self.last_time < self.throttle_interval and
              source == self.last_source):
            return
            
        # 更新最后一次消息信息
        self.last_message = message
        self.last_time = current_time
        
        # 使用指定的显示时间，如果未指定则使用默认时间
        actual_duration = duration if duration is not None else self.default_duration
        
        # 将新通知添加到队列
        self.notification_queue.append((message, level, actual_duration))
        
        # 如果当前没有显示通知，则显示队列中的第一个
        if not self.is_showing:
            self._showNext()
            
    def _showNext(self):
        """显示队列中的下一个通知"""
        if not self.notification_queue:
            self.is_showing = False
            return
            
        # 获取队列中的下一个通知
        message, level, duration = self.notification_queue.pop(0)
        
        # 创建并显示新通知
        self.current_notification = NotificationWidget(message, level)
        self.current_notification.closed.connect(self._onNotificationClosed)
        self.current_notification.clicked.connect(self.notificationClicked.emit)
        self.current_notification.fold_timer.setInterval(duration)
        self.current_notification.show()
        self.is_showing = True
        
    def _onNotificationClosed(self):
        """通知关闭时的处理"""
        if self.current_notification:
            self.current_notification.deleteLater()
            self.current_notification = None
            # 显示队列中的下一个通知
            QTimer.singleShot(100, self._showNext)
        
    def closeAllNotifications(self):
        """关闭所有通知"""
        self.notification_queue.clear()
        if self.current_notification:
            self.current_notification.hide()
            
    def showMessage(self, message, level="info", duration=None):
        """显示消息的便捷方法
        Args:
            message: 消息内容
            level: 通知级别 (info/warning/error/success)
            duration: 显示时长(毫秒)，如果为None则使用默认时长
        """
        self.showNotificationSignal.emit(message, level, duration if duration is not None else self.default_duration) 
        
    def setThrottleInterval(self, interval):
        """设置节流时间间隔
        Args:
            interval: 时间间隔（毫秒）
        """
        self.throttle_interval = interval 