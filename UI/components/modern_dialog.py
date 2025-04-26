from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QHBoxLayout, QApplication, QDialog, QSizePolicy
from PySide6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QSize, QPoint, QTimer
from PySide6.QtGui import QPainter, QColor, QPixmap, QPainterPath, QPen, QBrush, QLinearGradient, QFont, QFontMetrics
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QFile
import math

from .modern_button import ModernButton

class ModernDialog(QDialog):
    """现代化模态对话框组件 - 动态背景风格"""

    # 按钮类型
    OK = "ok"
    CANCEL = "cancel"
    YES = "yes"
    NO = "no"

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self._content = None
        self._result = None
        self._is_dark_mode = False
        self._dialog_width = 460  # 对话框宽度
        self._accent_color = None  # 添加强调色属性

        # 布局参数
        self.body_padding_h = 40
        self.content_padding_v = 32
        self.button_padding_v = 24
        self.corner_radius = 12  # 圆角

        # 动态背景参数
        self._particles = []
        self._particle_timer = QTimer(self)
        self._particle_timer.timeout.connect(self._update_particles)
        self._particle_timer.setInterval(33)  # 30fps

        # 粒子形状类型
        self.PARTICLE_CIRCLE = 0
        self.PARTICLE_SQUARE = 1
        self.PARTICLE_DIAMOND = 2
        self.PARTICLE_STAR = 3

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self.set_dark_mode)
            self.theme_manager.accentColorChanged.connect(self._update_accent_color)
            self._is_dark_mode = self.theme_manager.isDarkMode()
            self._accent_color = self.theme_manager.accent_color

        # 先创建UI
        self._setup_ui()

        # 设置最小宽度，但不设置最大宽度限制
        self.dialog_container.setMinimumWidth(self._dialog_width)
        self._update_style()

        # 初始化动画
        self._setup_animations()

        # 安装事件过滤器
        self.dialog_container.installEventFilter(self)

    def _setup_animations(self):
        """设置动画效果"""
        # 背景淡入动画
        self.background_anim = QPropertyAnimation(self, b"windowOpacity")
        self.background_anim.setDuration(250)
        self.background_anim.setStartValue(0.0)
        self.background_anim.setEndValue(1.0)
        self.background_anim.setEasingCurve(QEasingCurve.OutCubic)

        # 对话框淡入动画
        self.dialog_anim = QPropertyAnimation(self.dialog_container, b"windowOpacity")
        self.dialog_anim.setDuration(250)
        self.dialog_anim.setStartValue(0.0)
        self.dialog_anim.setEndValue(1.0)
        self.dialog_anim.setEasingCurve(QEasingCurve.OutCubic)

        # 创建动画组
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.background_anim)
        self.anim_group.addAnimation(self.dialog_anim)

    def _setup_ui(self):
        """初始化UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建一个覆盖整个窗口的背景widget
        self.background_widget = QWidget()
        self.background_widget.setObjectName("background_widget")
        self.background_widget.setProperty("opacity", 0.5)
        self.background_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 背景widget的布局
        self.background_layout = QVBoxLayout(self.background_widget)
        self.background_layout.setContentsMargins(0, 0, 0, 0)
        self.background_layout.setSpacing(0)

        # 对话框容器（包含实际内容）
        self.dialog_container = QWidget()
        self.dialog_container.setObjectName("dialog_container")
        self.dialog_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.MinimumExpanding)
        self.dialog_container.setFixedWidth(self._dialog_width)
        self.dialog_container.setMinimumHeight(200)  # 设置最小高度

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self.dialog_container)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 8)
        self.dialog_container.setGraphicsEffect(shadow)

        # 对话框内部布局
        self.dialog_layout = QVBoxLayout(self.dialog_container)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)
        self.dialog_layout.setSpacing(0)

        # 内容区域
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(self.body_padding_h, self.content_padding_v,
                                             self.body_padding_h, self.content_padding_v // 2)  # 减小底部内边距
        self.content_layout.setSpacing(24)

        # 内容左侧（图标）
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.icon_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # 内容右侧（文本区域）
        self.text_container = QWidget()
        self.text_layout = QVBoxLayout(self.text_container)
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.text_layout.setSpacing(12)

        # 标题
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("title_label")
        self.text_layout.addWidget(self.title_label)

        # 添加到内容布局
        self.content_layout.addWidget(self.icon_label)
        self.content_layout.addWidget(self.text_container, 1)

        # 按钮区域
        self.button_widget = QWidget()
        self.button_widget.setObjectName("button_widget")
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.setContentsMargins(self.body_padding_h, self.button_padding_v // 2,  # 减小顶部内边距
                                            self.body_padding_h, self.button_padding_v)
        self.button_layout.setSpacing(12)
        self.button_layout.addStretch()

        # 创建分割线
        self.separator = QWidget()
        self.separator.setObjectName("separator")
        self.separator.setFixedHeight(2)  # 增加分割线高度

        # 创建分割线容器，添加上下间距
        separator_container = QWidget()
        separator_layout = QVBoxLayout(separator_container)
        separator_layout.setContentsMargins(0, 2, 0, 2)  # 进一步减小上下间距，确保文字能完整显示
        separator_layout.addWidget(self.separator)

        # 将内容、分割线容器和按钮添加到对话框布局
        self.dialog_layout.addWidget(self.content_widget)
        self.dialog_layout.addWidget(separator_container)
        self.dialog_layout.addWidget(self.button_widget)

        # 将对话框容器添加到背景布局中央
        self.background_layout.addStretch()
        self.background_layout.addWidget(self.dialog_container, 0, Qt.AlignCenter)
        self.background_layout.addStretch()

        # 将背景widget添加到主布局
        self.main_layout.addWidget(self.background_widget)

    def _update_style(self):
        """更新样式"""
        # 主题色（使用系统强调色）
        if self._accent_color:
            theme_color = QColor(self._accent_color['red'], self._accent_color['green'], self._accent_color['blue'])
            theme_color_str = f"rgb({theme_color.red()}, {theme_color.green()}, {theme_color.blue()})"
            theme_color_hover = QColor(
                max(0, min(255, theme_color.red() - 10)),
                max(0, min(255, theme_color.green() - 10)),
                max(0, min(255, theme_color.blue() - 10))
            )
            theme_color_hover_str = f"rgb({theme_color_hover.red()}, {theme_color_hover.green()}, {theme_color_hover.blue()})"
            theme_color_pressed = QColor(
                max(0, min(255, theme_color.red() - 20)),
                max(0, min(255, theme_color.green() - 20)),
                max(0, min(255, theme_color.blue() - 20))
            )
            theme_color_pressed_str = f"rgb({theme_color_pressed.red()}, {theme_color_pressed.green()}, {theme_color_pressed.blue()})"
        else:
            theme_color_str = "#3498db"  # 默认主题色
            theme_color_hover_str = "#2980b9"  # 默认悬停色
            theme_color_pressed_str = "#2472a4"  # 默认按下色

        # 背景色 - 使用更精致的半透明效果
        if self._is_dark_mode:
            bg_color = "rgba(25, 25, 30, 0.92)"  # 稍微带蓝色的深色
            # 增强按钮区域背景与内容区域的对比
            button_area_bg = "rgba(35, 35, 45, 0.95)"
        else:
            bg_color = "rgba(250, 250, 255, 0.92)"  # 稍微带蓝色的浅色
            # 增强按钮区域背景与内容区域的对比
            button_area_bg = "rgba(235, 235, 240, 0.95)"

        # 文字色 - 更精致的颜色
        text_color = "#f0f0f0" if self._is_dark_mode else "#303035"  # 更亮/更深的文本颜色
        subtitle_color = "#b0b0b0" if self._is_dark_mode else "#606065"  # 次要文本颜色
        title_color = theme_color_str  # 标题使用主题色

        # 按钮颜色 - 更精致的颜色
        if self._is_dark_mode:
            button_bg = "rgba(45, 45, 50, 0.8)"  # 半透明按钮背景
            button_hover = "rgba(55, 55, 60, 0.9)"
            button_pressed = "rgba(65, 65, 70, 1.0)"
        else:
            button_bg = "rgba(230, 230, 235, 0.8)"  # 半透明按钮背景
            button_hover = "rgba(220, 220, 225, 0.9)"
            button_pressed = "rgba(210, 210, 215, 1.0)"

        # 设置字体
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        self.title_label.setFont(title_font)

        self.setStyleSheet(f"""
            QDialog {{
                background: transparent;
            }}
            QWidget#background_widget {{
                background-color: rgba(0, 0, 0, {0.7 * self.background_widget.property("opacity")});
            }}
            QWidget#dialog_container {{
                background: {bg_color};
                border-radius: {self.corner_radius}px;
            }}
            QWidget#content_widget {{
                background: transparent;
            }}
            QWidget#separator {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(150, 150, 150, 0.01),
                    stop:0.3 rgba({theme_color.red()}, {theme_color.green()}, {theme_color.blue()}, 0.3),
                    stop:0.5 rgba({theme_color.red()}, {theme_color.green()}, {theme_color.blue()}, 0.4),
                    stop:0.7 rgba({theme_color.red()}, {theme_color.green()}, {theme_color.blue()}, 0.3),
                    stop:1 rgba(150, 150, 150, 0.01)
                );  /* 使用主题色渐变作为分割线颜色 */
                margin: 0px {self.body_padding_h // 2}px;
            }}

            QWidget#button_widget {{
                background: {button_area_bg};
                border-bottom-left-radius: {self.corner_radius}px;
                border-bottom-right-radius: {self.corner_radius}px;
            }}
            QLabel {{
                color: {text_color};
                font-size: 14px;
                font-family: "Segoe UI";
                letter-spacing: 0.3px;
            }}
            QLabel#title_label {{
                color: {title_color};
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QLabel.subtitle {{
                color: {subtitle_color};
                font-size: 13px;
            }}
            QPushButton {{
                background-color: {button_bg};
                color: {text_color};
                border: none;
                border-radius: 18px;
                padding: 0 24px;
                height: 36px;
                font-size: 14px;
                font-family: "Segoe UI";
                letter-spacing: 0.3px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_pressed};
            }}
            QPushButton[primary=true] {{
                background-color: {theme_color_str};
                color: white;
                font-weight: bold;
            }}
            QPushButton[primary=true]:hover {{
                background-color: {theme_color_hover_str};
            }}
            QPushButton[primary=true]:pressed {{
                background-color: {theme_color_pressed_str};
            }}
        """)

    def _init_particles(self):
        """初始化增强的粒子效果"""
        # 清空现有粒子
        self._particles.clear()

        # 获取对话框容器的位置和大小
        rect = self.dialog_container.geometry()

        # 设置主题色
        if self._accent_color:
            theme_color = QColor(self._accent_color['red'], self._accent_color['green'], self._accent_color['blue'])
        else:
            theme_color = QColor("#3498db")  # 默认主题色

        # 创建更丰富的主题色变体颜色
        color_variants = [
            theme_color,  # 原始主题色
            QColor(min(255, theme_color.red() + 30),
                   min(255, theme_color.green() + 30),
                   min(255, theme_color.blue() + 30)),  # 亮一点的变体
            QColor(max(0, theme_color.red() - 30),
                   max(0, theme_color.green() - 30),
                   max(0, theme_color.blue() - 30)),   # 暗一点的变体
            QColor(min(255, theme_color.red() + 40),
                   min(255, theme_color.green() + 10),
                   min(255, theme_color.blue() + 20)),  # 暖色变体
            QColor(max(0, theme_color.red() - 10),
                   max(0, theme_color.green() - 5),
                   min(255, theme_color.blue() + 40))   # 冷色变体
        ]

        # 创建粒子
        import random
        import math

        for _ in range(25):  # 减少粒子数量到25个
            # 随机选择一个颜色变体
            color_variant = random.choice(color_variants)

            # 随机选择粒子形状
            shape = random.choice([self.PARTICLE_CIRCLE, self.PARTICLE_SQUARE, self.PARTICLE_DIAMOND, self.PARTICLE_STAR])

            # 随机生成粒子大小
            if random.random() < 0.7:  # 70%的粒子是小粒子
                size = random.uniform(3, 8)
            else:  # 30%的粒子是大粒子
                size = random.uniform(8, 15)

            # 随机生成粒子速度
            speed_factor = random.uniform(0.3, 1.0)  # 速度因子，用于控制粒子速度
            angle = random.uniform(0, 2 * math.pi)  # 随机方向
            speed_x = math.cos(angle) * speed_factor * 0.7  # 水平速度分量
            speed_y = math.sin(angle) * speed_factor * 0.7  # 垂直速度分量

            # 随机生成粒子透明度
            opacity = random.uniform(0.1, 0.7)

            # 创建粒子
            particle = {
                'x': random.randint(rect.left() - 100, rect.right() + 100),
                'y': random.randint(rect.top() - 100, rect.bottom() + 100),
                'size': size,
                'speed_x': speed_x,
                'speed_y': speed_y,
                'opacity': opacity,
                'color': QColor(
                    color_variant.red(),
                    color_variant.green(),
                    color_variant.blue(),
                    int(opacity * 150)  # 透明度范围更大
                ),
                'shape': shape,  # 添加形状属性
                'rotation': random.uniform(0, 360),  # 添加旋转角度属性
                'rotation_speed': random.uniform(-1, 1),  # 添加旋转速度属性
                'pulse_factor': random.uniform(0.8, 1.2),  # 添加脉动因子
                'pulse_speed': random.uniform(0.01, 0.05)  # 添加脉动速度
            }
            self._particles.append(particle)

        # 启动粒子动画
        self._particle_timer.start()

    def _update_particles(self):
        """更新粒子位置和属性"""
        # 获取对话框容器的位置和大小
        rect = self.dialog_container.geometry()
        rect_expanded = rect.adjusted(-150, -150, 150, 150)  # 扩大区域，让粒子可以在对话框周围更广泛地移动

        # 更新每个粒子的位置和属性
        for particle in self._particles:
            # 更新位置
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']

            # 更新旋转角度
            particle['rotation'] += particle['rotation_speed']
            if particle['rotation'] > 360:
                particle['rotation'] -= 360
            elif particle['rotation'] < 0:
                particle['rotation'] += 360

            # 更新脉动因子
            particle['pulse_factor'] += particle['pulse_speed']
            if particle['pulse_factor'] > 1.2:
                particle['pulse_speed'] = -abs(particle['pulse_speed'])
            elif particle['pulse_factor'] < 0.8:
                particle['pulse_speed'] = abs(particle['pulse_speed'])

            # 如果粒子移出扩展区域，将其重新放置在区域边缘
            if particle['x'] < rect_expanded.left():
                particle['x'] = rect_expanded.right()
            elif particle['x'] > rect_expanded.right():
                particle['x'] = rect_expanded.left()

            if particle['y'] < rect_expanded.top():
                particle['y'] = rect_expanded.bottom()
            elif particle['y'] > rect_expanded.bottom():
                particle['y'] = rect_expanded.top()

        # 重绘窗口
        self.update()

    def paintEvent(self, event):
        """绘制事件，用于绘制增强的粒子效果"""
        super().paintEvent(event)

        # 只在对话框容器可见时绘制粒子
        if not self.dialog_container.isVisible() or not self._particles:
            return

        # 创建QPainter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制每个粒子
        for particle in self._particles:
            painter.setPen(Qt.NoPen)
            painter.setBrush(particle['color'])

            # 保存当前状态
            painter.save()

            # 移动到粒子中心点
            painter.translate(particle['x'], particle['y'])

            # 应用旋转
            painter.rotate(particle['rotation'])

            # 应用脉动缩放
            pulse_scale = particle['pulse_factor']
            painter.scale(pulse_scale, pulse_scale)

            # 计算实际大小
            actual_size = particle['size']
            half_size = actual_size / 2

            # 根据粒子形状绘制不同的图形
            if particle['shape'] == self.PARTICLE_CIRCLE:
                # 绘制圆形
                painter.drawEllipse(-half_size, -half_size, actual_size, actual_size)
            elif particle['shape'] == self.PARTICLE_SQUARE:
                # 绘制正方形
                painter.drawRect(-half_size, -half_size, actual_size, actual_size)
            elif particle['shape'] == self.PARTICLE_DIAMOND:
                # 绘制菱形
                path = QPainterPath()
                path.moveTo(0, -half_size)  # 上顶点
                path.lineTo(half_size, 0)   # 右顶点
                path.lineTo(0, half_size)   # 下顶点
                path.lineTo(-half_size, 0)  # 左顶点
                path.closeSubpath()
                painter.drawPath(path)
            elif particle['shape'] == self.PARTICLE_STAR:
                # 绘制五角星
                path = QPainterPath()
                outer_radius = half_size
                inner_radius = outer_radius * 0.4

                for i in range(5):
                    # 外部点
                    angle = i * 72 - 90  # 从顶部开始，每72度一个点
                    x = outer_radius * math.cos(math.radians(angle))
                    y = outer_radius * math.sin(math.radians(angle))
                    if i == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)

                    # 内部点
                    angle += 36  # 内部点在外部点之间
                    x = inner_radius * math.cos(math.radians(angle))
                    y = inner_radius * math.sin(math.radians(angle))
                    path.lineTo(x, y)

                path.closeSubpath()
                painter.drawPath(path)

            # 恢复状态
            painter.restore()

    def adjustSize(self):
        """调整对话框大小"""
        # 调整内容容器大小
        self.text_container.adjustSize()
        self.content_widget.adjustSize()
        self.button_widget.adjustSize()

        # 获取内容区域的实际高度
        content_height = self.content_widget.sizeHint().height()
        button_height = self.button_widget.sizeHint().height()

        # 确保内容区域最小高度
        content_height = max(content_height, 120)

        # 计算总高度
        total_height = content_height + button_height

        # 确保总高度不小于最小高度
        total_height = max(total_height, 200)

        # 调整对话框容器大小
        self.dialog_container.setFixedHeight(total_height)

        super().adjustSize()

    def _show_dialog_internal(self):
        """显示对话框并覆盖整个父窗口"""
        # 获取顶级窗口
        top_window = QApplication.activeWindow()

        # 确保所有内容都正确调整大小
        self.adjustSize()

        if top_window:
            # 使用frameGeometry获取完整的窗口大小（包括边框）
            window_rect = top_window.frameGeometry()
            # 设置对话框大小和位置
            self.setFixedSize(window_rect.size())
            self.move(window_rect.topLeft())
        else:
            # 如果没有顶级窗口，则使用屏幕大小
            screen = QApplication.primaryScreen().availableGeometry()
            self.setFixedSize(screen.size())
            self.move(screen.topLeft())

        # 设置初始透明度
        self.setWindowOpacity(0.0)
        self.dialog_container.setWindowOpacity(0.0)

        # 初始化粒子效果
        self._init_particles()

        # 显示对话框
        self.show()

        # 开始动画
        self.anim_group.start()

        self.exec()

    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止粒子动画
        self._particle_timer.stop()
        super().closeEvent(event)

    @classmethod
    def show_dialog(cls, parent, title, message, buttons=[OK], icon_name=None, button_texts=None):
        """显示对话框
        Args:
            parent: 父窗口
            title: 对话框标题
            message: 对话框消息内容
            buttons: 按钮类型列表
            icon_name: 只需要Fluent图标名称
            button_texts: 按钮文本字典，格式为 {按钮类型: 按钮文本}，例如 {OK: "确认", CANCEL: "关闭"}
        """
        dialog = cls(title, parent)

        # 设置内容
        content = QLabel(message)
        content.setWordWrap(True)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        content.setStyleSheet("""
            QLabel {
                font-size: 14px;
                min-height: 20px;
                padding: 0px;
                font-family: "Segoe UI";
            }
        """)

        # 计算文本所需的宽度
        available_width = dialog._dialog_width - 2 * dialog.body_padding_h - 64 - 24  # 减去左右padding、图标宽度(64px)和间距
        # 计算文本布局
        content.fontMetrics().boundingRect(
            0, 0, available_width, 1000,  # 最大宽度为可用宽度，高度1000作为充分大的值
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter,
            message
        )

        # 设置内容标签的固定宽度，让它自动调整高度
        content.setFixedWidth(available_width)

        # 添加到布局
        dialog.text_layout.addWidget(content)

        # 设置图标
        if icon_name:
            dialog.set_icon(icon_name)

        # 创建按钮
        button_map = {
            cls.OK: ("确定", True),
            cls.CANCEL: ("取消", False),
            cls.YES: ("是", True),
            cls.NO: ("否", False)
        }

        # 清空现有按钮布局
        while dialog.button_layout.count():
            item = dialog.button_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 添加按钮
        dialog.button_layout.addStretch()  # 将按钮推到右侧
        for button_type in buttons:
            if button_type in button_map:
                default_text, is_primary = button_map[button_type]
                # 使用自定义文本（如果提供），否则使用默认文本
                text = button_texts.get(button_type, default_text) if button_texts else default_text
                button = ModernButton(dialog, highlight=is_primary)
                button.setText(text)
                button.setMinimumWidth(100)  # 设置最小宽度
                button.clicked.connect(lambda _=None, b=button_type: dialog._handle_button_click(b))
                dialog.button_layout.addWidget(button)

        # 调整所有组件的大小
        dialog.adjustSize()

        # 显示对话框
        dialog._show_dialog_internal()

        return dialog

    def set_icon(self, icon_name):
        """设置图标
        Args:
            icon_name: Fluent图标名称，例如 'ic_fluent_info_regular'
        """
        try:
            # 构建资源路径
            icon_path = f":/resources/{icon_name}.svg"

            # 从Qt资源系统读取SVG
            file = QFile(icon_path)
            if file.open(QFile.ReadOnly | QFile.Text):
                svg_content = str(file.readAll().data(), encoding='utf-8')
                file.close()

                # 替换颜色
                if self._accent_color:
                    theme_color = QColor(self._accent_color['red'], self._accent_color['green'], self._accent_color['blue'])
                    color = f"rgb({theme_color.red()}, {theme_color.green()}, {theme_color.blue()})"
                else:
                    color = "#ffffff" if self._is_dark_mode else "#333333"

                svg_content = svg_content.replace('currentColor', color)

                # 创建SVG渲染器
                renderer = QSvgRenderer()
                renderer.load(svg_content.encode('utf-8'))

                # 创建Pixmap
                size = 64  # 基础大小为64像素
                if self.window():
                    # 考虑DPI缩放
                    device_pixel_ratio = self.window().devicePixelRatio()
                    size = int(size * device_pixel_ratio)

                pixmap = QPixmap(size, size)
                pixmap.fill(Qt.transparent)

                # 渲染SVG
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                renderer.render(painter)
                painter.end()

                if self.window():
                    pixmap.setDevicePixelRatio(device_pixel_ratio)

                # 设置图标
                self.icon_label.setPixmap(pixmap)
                self.icon_label.setFixedSize(64, 64)  # 固定显示大小为64x64像素

        except Exception as e:
            print(f"设置图标失败: {str(e)}")
            self.icon_label.clear()

    def set_dark_mode(self, is_dark):
        """设置主题模式"""
        self._is_dark_mode = is_dark
        self._update_style()
        self.update()

    def get_result(self):
        """获取对话框结果"""
        return self._result

    def _handle_button_click(self, result):
        """处理按钮点击"""
        self._result = result
        self.accept()

    def eventFilter(self, obj, event):
        """事件过滤器，用于处理缩放效果"""
        if obj == self.dialog_container and event.type() == QEvent.Paint:
            opacity = obj.windowOpacity()
            if opacity < 1.0:
                painter = QPainter(obj)
                painter.setOpacity(opacity)

        return super().eventFilter(obj, event)

    def _update_accent_color(self, accent_color):
        """更新强调色"""
        self._accent_color = accent_color
        self._update_style()
        self.update()  # 需要重绘粒子效果