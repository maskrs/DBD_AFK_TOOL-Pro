from PySide6.QtWidgets import (QWidget, QVBoxLayout,
                               QGraphicsDropShadowEffect, QScrollArea, QFrame,
                               QApplication)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QTimer
from PySide6.QtGui import QPainter, QColor, QPainterPath

class Drawer(QWidget):
    """现代化抽屉组件，从右侧滑出的次级页面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark_mode = False
        self._accent_color = None
        self._drawer_width = 520  # 恢复原始宽度
        self._slide_position = 0  # 滑动位置
        self._opacity = 0.0  # 遮罩透明度

        # 动态背景参数
        self._particles = []
        self._particle_timer = QTimer(self)
        self._particle_timer.timeout.connect(self._update_particles)
        self._particle_timer.setInterval(33)  # 30fps

        # 粒子形状类型
        self.PARTICLE_CIRCLE = 0
        self.PARTICLE_SQUARE = 1
        self.PARTICLE_DIAMOND = 2

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
        self.content_layout.setContentsMargins(16, 16, 16, 16)  # 设置适当的边距
        self.content_layout.setSpacing(12)  # 设置适当的间距

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
        # 背景淡入动画 - 增强透明度效果
        self.background_anim = QPropertyAnimation(self, b"opacity")
        self.background_anim.setDuration(300)
        self.background_anim.setStartValue(0.0)
        self.background_anim.setEndValue(0.65)  # 增强背景透明度
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
        self.update()  # 需要重绘粒子效果

    def _update_accent_color(self, accent_color):
        """更新强调色"""
        self._accent_color = accent_color
        self._update_style()
        self.update()  # 需要重绘粒子效果

    def _init_particles(self):
        """初始化粒子效果 - 只在遮罩区域生成粒子"""
        # 清空现有粒子
        self._particles.clear()

        # 获取抽屉容器的位置和大小
        drawer_rect = self.drawer_container.geometry()
        # 获取整个窗口的大小
        window_rect = self.rect()

        # 设置主题色
        if self._accent_color:
            theme_color = QColor(self._accent_color['red'], self._accent_color['green'], self._accent_color['blue'])
        else:
            theme_color = QColor("#3498db")  # 默认主题色

        # 创建粒子
        import random
        import math

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

        # 创建粒子，只在遮罩区域生成（不包括抽屉容器区域）
        for _ in range(40):  # 增加粒子数量到40个
            # 随机选择一个颜色变体
            color_variant = random.choice(color_variants)

            # 随机选择粒子形状
            shape = random.choice([self.PARTICLE_CIRCLE, self.PARTICLE_SQUARE, self.PARTICLE_DIAMOND])

            # 随机生成粒子大小
            if random.random() < 0.7:  # 70%的粒子是小粒子
                size = random.uniform(2, 6)
            else:  # 30%的粒子是大粒子
                size = random.uniform(6, 12)

            # 随机生成粒子速度
            speed_factor = random.uniform(0.3, 1.0)  # 速度因子，用于控制粒子速度
            angle = random.uniform(0, 2 * math.pi)  # 随机方向
            speed_x = math.cos(angle) * speed_factor * 0.7  # 水平速度分量
            speed_y = math.sin(angle) * speed_factor * 0.7  # 垂直速度分量

            # 随机生成粒子透明度
            opacity = random.uniform(0.1, 0.7)

            # 生成粒子位置，确保在遮罩区域内，但不在抽屉容器区域内
            valid_position = False
            max_attempts = 10  # 最大尝试次数
            attempts = 0
            x, y = 0, 0

            while not valid_position and attempts < max_attempts:
                # 在整个窗口区域内随机生成位置
                x = random.randint(0, window_rect.width())
                y = random.randint(0, window_rect.height())

                # 检查位置是否在抽屉容器区域外
                if not drawer_rect.contains(x, y):
                    valid_position = True

                attempts += 1

            # 如果找不到有效位置，则跳过这个粒子
            if not valid_position:
                continue

            # 创建粒子
            particle = {
                'x': x,
                'y': y,
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
                'rotation_speed': random.uniform(-1, 1)  # 添加旋转速度属性
            }
            self._particles.append(particle)

        # 启动粒子动画
        self._particle_timer.start()

    def _update_particles(self):
        """更新粒子位置 - 确保粒子不会进入抽屉区域"""
        # 获取抽屉容器的位置和大小
        drawer_rect = self.drawer_container.geometry()
        # 获取整个窗口的大小
        window_rect = self.rect()

        # 更新每个粒子的位置和旋转
        for particle in self._particles:
            # 保存当前位置
            old_x, old_y = particle['x'], particle['y']

            # 更新位置
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']

            # 更新旋转角度
            particle['rotation'] += particle['rotation_speed']
            if particle['rotation'] > 360:
                particle['rotation'] -= 360
            elif particle['rotation'] < 0:
                particle['rotation'] += 360

            # 检查新位置是否在抽屉容器区域内
            if drawer_rect.contains(int(particle['x']), int(particle['y'])):
                # 如果在抽屉容器区域内，则改变方向
                import random
                import math

                # 计算从抽屉容器中心指向粒子的方向
                drawer_center_x = drawer_rect.center().x()
                drawer_center_y = drawer_rect.center().y()

                # 计算方向向量
                dx = particle['x'] - drawer_center_x
                dy = particle['y'] - drawer_center_y

                # 标准化方向向量
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    dx /= length
                    dy /= length

                # 设置新的速度，使粒子离开抽屉容器
                speed_factor = random.uniform(0.5, 1.5)  # 增大速度因子，使粒子快速离开
                particle['speed_x'] = dx * speed_factor
                particle['speed_y'] = dy * speed_factor

                # 将粒子放回原来的位置
                particle['x'] = old_x
                particle['y'] = old_y

            # 如果粒子移出窗口区域，将其移动到对面的边缘
            if particle['x'] < 0:
                particle['x'] = window_rect.width()
            elif particle['x'] > window_rect.width():
                particle['x'] = 0

            if particle['y'] < 0:
                particle['y'] = window_rect.height()
            elif particle['y'] > window_rect.height():
                particle['y'] = 0

        # 重绘窗口
        self.update()

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
        """绘制事件，用于绘制遮罩和粒子"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆角遮罩路径
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 8, 8)

        # 绘制半透明黑色遮罩
        painter.fillPath(path, QColor(0, 0, 0, int(255 * self._opacity)))

        # 只在抽屉容器可见时绘制粒子
        if self.drawer_container.isVisible() and self._particles and self._opacity > 0.1:
            # 获取抽屉容器的位置和大小
            drawer_rect = self.drawer_container.geometry()

            # 创建剪切区域，只在抽屉容器区域外绘制粒子
            clip_path = QPainterPath()
            clip_path.addRect(self.rect())  # 添加整个窗口区域

            # 创建抽屉容器区域的路径
            drawer_path = QPainterPath()
            drawer_path.addRect(drawer_rect)

            # 从整个窗口区域中减去抽屉容器区域
            clip_path = clip_path.subtracted(drawer_path)

            # 设置剪切区域
            painter.setClipPath(clip_path)

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

                # 根据粒子形状绘制不同的图形
                half_size = particle['size'] / 2
                if particle['shape'] == self.PARTICLE_CIRCLE:
                    # 绘制圆形
                    painter.drawEllipse(-half_size, -half_size, particle['size'], particle['size'])
                elif particle['shape'] == self.PARTICLE_SQUARE:
                    # 绘制正方形
                    painter.drawRect(-half_size, -half_size, particle['size'], particle['size'])
                elif particle['shape'] == self.PARTICLE_DIAMOND:
                    # 绘制菱形
                    path = QPainterPath()
                    path.moveTo(0, -half_size)  # 上顶点
                    path.lineTo(half_size, 0)   # 右顶点
                    path.lineTo(0, half_size)   # 下顶点
                    path.lineTo(-half_size, 0)  # 左顶点
                    path.closeSubpath()
                    painter.drawPath(path)

                # 恢复状态
                painter.restore()

            # 清除剪切区域
            painter.setClipping(False)

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

        # 初始化粒子效果
        self._init_particles()

        # 显示抽屉
        self.show()

        # 开始动画
        self.background_anim.start()
        self.drawer_anim.start()

    def add_widget(self, widget):
        """添加部件到抽屉内容区域"""
        self.content_layout.addWidget(widget)

    def set_drawer_width(self, width):
        """设置抽屉宽度

        Args:
            width (int): 抽屉的新宽度，单位为像素
        """
        # 验证宽度是否合理
        if width < 300:
            width = 300  # 设置最小宽度为300像素
        elif width > 800:
            width = 800  # 设置最大宽度为800像素

        # 更新宽度变量
        self._drawer_width = width

        # 更新抽屉容器的宽度
        if hasattr(self, 'drawer_container'):
            self.drawer_container.setFixedWidth(width)

        # 如果抽屉已经显示，更新其位置
        if self.isVisible() and hasattr(self, 'drawer_container'):
            top_window = QApplication.activeWindow()
            if top_window:
                window_rect = top_window.frameGeometry()
                right_pos = window_rect.width() - self._drawer_width + self._slide_position
                self.drawer_container.move(right_pos, self.drawer_container.y())

        # 更新动画设置
        if hasattr(self, 'drawer_anim'):
            # 保存当前动画状态
            current_direction = self.drawer_anim.direction()
            current_state = self.drawer_anim.state()

            # 重新设置动画起始值
            self.drawer_anim.setStartValue(self._drawer_width)

            # 如果动画正在运行，重新启动它
            if current_state == QPropertyAnimation.Running:
                self.drawer_anim.stop()
                self.drawer_anim.setDirection(current_direction)
                self.drawer_anim.start()

        # 重新初始化粒子效果
        if self.isVisible() and self._particles:
            self._init_particles()

    def get_drawer_width(self):
        """获取当前抽屉宽度

        Returns:
            int: 当前抽屉宽度，单位为像素
        """
        return self._drawer_width

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
        # 停止粒子动画
        self._particle_timer.stop()
        # 关闭窗口
        self.close()

    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止粒子动画
        self._particle_timer.stop()
        super().closeEvent(event)