from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QGraphicsDropShadowEffect, QVBoxLayout, QPushButton, QHBoxLayout, QFrame, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve, pyqtSignal, QObject, QSize, QDateTime, QPointF, QParallelAnimationGroup
from PyQt5.QtGui import QPainter, QColor, QPixmap, QIcon, QFont, QPen, QPolygonF, QFontMetrics
from PyQt5.QtSvg import QSvgWidget, QSvgRenderer
from UI.resources import pyqt_resources_rc
from PyQt5.QtCore import QFile
import math
import random

# 获取设备像素比例的帮助函数
def get_device_pixel_ratio():
    """获取当前设备的像素比例"""
    try:
        # 尝试获取应用程序实例
        app = QApplication.instance()
        if app is None:
            return 1.0

        # 获取主屏幕
        screen = app.primaryScreen()
        if screen is None:
            return 1.0

        # 返回设备像素比例
        return screen.devicePixelRatio()
    except Exception as e:
        print(f"Error getting device pixel ratio: {e}")
        return 1.0

# 根据设备像素比例缩放尺寸的帮助函数
def scale_by_dpi(size):
    """根据设备像素比例缩放尺寸"""
    dpi_scale = get_device_pixel_ratio()
    return int(size * dpi_scale)

class FloatingElement(QWidget):
    """浮动装饰元素"""

    def __init__(self, parent=None, size=10, color="#FFFFFF", opacity=0.5):
        super().__init__(parent)
        self.size = size
        self.color = QColor(color)
        self.color.setAlphaF(opacity)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # 形状渐变参数
        # 增加各种形状的初始概率
        # 当前形状: 0=圆形, 1=方形, 2=三角形, 3=六边形, 4=五角星, 5=梯形
        shape_choices = [0, 1, 2, 3, 3, 4, 5]  # 包含所有形状，六边形有额外权重
        self.current_shape = random.choice(shape_choices)

        # 目标形状也增加六边形的权重
        self.target_shape = random.choice(shape_choices)   # 目标形状
        # 确保目标形状与当前形状不同
        while self.target_shape == self.current_shape:
            self.target_shape = random.choice(shape_choices)
        self.shape_morph_progress = 0.0           # 形状渐变进度 (0.0 - 1.0)
        self.shape_morph_speed = random.uniform(0.002, 0.005)  # 增加渐变速度，使变化更明显

        # 预计算所有形状的点
        self._precalculate_shapes()

        # 形状渐变定时器
        self.morph_timer = QTimer(self)
        self.morph_timer.setInterval(50)  # 50毫秒更新一次
        self.morph_timer.timeout.connect(self._update_shape_morph)

        # 动画参数
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(random.randint(3000, 6000))
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.finished.connect(self._restart_animation)

    def _precalculate_shapes(self):
        """预计算所有形状的点"""
        # 定义圆形的点
        self.circle_points = []
        circle_sides = 12  # 使用12个点表示圆形
        for i in range(circle_sides):
            angle = 2 * math.pi * i / circle_sides
            x = self.size / 2 + (self.size / 2 - 1) * math.cos(angle)
            y = self.size / 2 + (self.size / 2 - 1) * math.sin(angle)
            self.circle_points.append(QPointF(x, y))

        # 定义方形的点
        self.square_points = []
        # 方形四个角点
        half_size = self.size / 2 - 1
        self.square_points.append(QPointF(self.size / 2 - half_size, self.size / 2 - half_size))  # 左上
        self.square_points.append(QPointF(self.size / 2 + half_size, self.size / 2 - half_size))  # 右上
        self.square_points.append(QPointF(self.size / 2 + half_size, self.size / 2 + half_size))  # 右下
        self.square_points.append(QPointF(self.size / 2 - half_size, self.size / 2 + half_size))  # 左下

        # 定义三角形的点
        self.triangle_points = []
        sides = 3
        rotation_offset = math.pi / 2  # 旋转使其平底向下
        for i in range(sides):
            angle = 2 * math.pi * i / sides + rotation_offset
            x = self.size / 2 + (self.size / 2 - 1) * math.cos(angle)
            y = self.size / 2 + (self.size / 2 - 1) * math.sin(angle)
            self.triangle_points.append(QPointF(x, y))

        # 定义六边形的点 - 确保是正六边形
        self.hexagon_points = []
        sides = 6
        # 使用稍大一点的半径，使六边形更明显
        radius = self.size / 2 - 0.5  # 减少缩进量，使六边形更大
        # 旋转六边形，使其有两个水平边
        rotation_offset = math.pi / 6  # 30度旋转
        for i in range(sides):
            angle = 2 * math.pi * i / sides + rotation_offset
            x = self.size / 2 + radius * math.cos(angle)
            y = self.size / 2 + radius * math.sin(angle)
            self.hexagon_points.append(QPointF(x, y))

        # 定义五角星的点
        self.star_points = []
        outer_radius = self.size / 2 - 0.5  # 外圈半径
        inner_radius = outer_radius * 0.4  # 内圈半径，调整这个值可以改变星形的尖锐程度
        points = 5  # 五角星
        rotation_offset = -math.pi / 2  # 旋转使一个角朝上

        for i in range(points * 2):
            # 交替使用外圈和内圈半径
            radius = outer_radius if i % 2 == 0 else inner_radius
            angle = math.pi * i / points + rotation_offset
            x = self.size / 2 + radius * math.cos(angle)
            y = self.size / 2 + radius * math.sin(angle)
            self.star_points.append(QPointF(x, y))

        # 定义梯形的点
        self.trapezoid_points = []
        width = self.size - 1  # 总宽度
        height = self.size - 1  # 总高度
        top_width = width * 0.6  # 上边宽度
        bottom_width = width  # 下边宽度

        # 左上角
        self.trapezoid_points.append(QPointF(self.size/2 - top_width/2, 0.5))
        # 右上角
        self.trapezoid_points.append(QPointF(self.size/2 + top_width/2, 0.5))
        # 右下角
        self.trapezoid_points.append(QPointF(self.size/2 + bottom_width/2, height - 0.5))
        # 左下角
        self.trapezoid_points.append(QPointF(self.size/2 - bottom_width/2, height - 0.5))

    def _update_shape_morph(self):
        """更新形状渐变进度"""
        self.shape_morph_progress += self.shape_morph_speed

        # 当渐变完成时，切换到新形状并重置进度
        if self.shape_morph_progress >= 1.0:
            self.current_shape = self.target_shape
            # 增加各种形状的概率
            # 形状: 0=圆形, 1=方形, 2=三角形, 3=六边形, 4=五角星, 5=梯形
            shape_choices = [0, 1, 2, 3, 3, 4, 5, 4, 5]  # 给新形状也增加一些权重
            self.target_shape = random.choice(shape_choices)
            # 确保新目标不同于当前形状
            while self.target_shape == self.current_shape:
                self.target_shape = random.choice(shape_choices)
            self.shape_morph_progress = 0.0
            # 随机调整渐变速度，增大速度使变化更明显
            self.shape_morph_speed = random.uniform(0.002, 0.005)

        # 触发重绘
        self.update()

    def _restart_animation(self):
        """重新开始动画"""
        if self.parent():
            # 获取父窗口大小
            parent_rect = self.parent().rect()

            # 增加安全边距，确保元素不会太靠近边缘
            margin = 10  # 增加到10像素

            # 计算有效范围，确保安全边距
            max_x = max(margin * 2, parent_rect.width() - self.size - margin * 2)
            max_y = max(margin * 2, parent_rect.height() - self.size - margin * 2)

            # 限制目标位置在更安全的范围内
            safe_min_x = margin * 2
            safe_max_x = max_x - margin
            safe_min_y = margin * 2
            safe_max_y = max_y - margin

            # 确保范围有效
            if safe_max_x <= safe_min_x:
                safe_max_x = safe_min_x + 1
            if safe_max_y <= safe_min_y:
                safe_max_y = safe_min_y + 1

            target_x = random.randint(safe_min_x, safe_max_x)
            target_y = random.randint(safe_min_y, safe_max_y)

            # 确保当前位置在有效范围内
            current_pos = self.pos()
            valid_x = max(safe_min_x, min(safe_max_x, current_pos.x()))
            valid_y = max(safe_min_y, min(safe_max_y, current_pos.y()))

            # 移动到有效位置
            self.move(valid_x, valid_y)

            # 设置动画
            self.animation.setStartValue(QPoint(valid_x, valid_y))
            self.animation.setEndValue(QPoint(target_x, target_y))
            self.animation.setDuration(random.randint(3000, 6000))
            self.animation.start()

            # 确保形状渐变定时器在运行
            if not self.morph_timer.isActive():
                self.morph_timer.start()

    def start_animation(self):
        """开始动画"""
        if self.parent():
            # 获取父窗口大小
            parent_rect = self.parent().rect()

            # 增加安全边距，确保元素不会太靠近边缘
            margin = 5  # 增加到8像素

            # 计算有效范围，确保安全边距
            max_x = max(margin * 2, parent_rect.width() - self.size - margin * 2)
            max_y = max(margin * 2, parent_rect.height() - self.size - margin * 2)

            # 限制目标位置在更安全的范围内
            safe_min_x = margin * 2
            safe_max_x = max_x - margin
            safe_min_y = margin * 2
            safe_max_y = max_y - margin

            # 确保范围有效
            if safe_max_x <= safe_min_x:
                safe_max_x = safe_min_x + 1
            if safe_max_y <= safe_min_y:
                safe_max_y = safe_min_y + 1

            # 随机生成起始和目标位置，确保在安全范围内
            start_x = random.randint(safe_min_x, safe_max_x)
            start_y = random.randint(safe_min_y, safe_max_y)
            target_x = random.randint(safe_min_x, safe_max_x)
            target_y = random.randint(safe_min_y, safe_max_y)

            # 设置初始位置
            self.move(start_x, start_y)

            # 设置动画
            self.animation.setStartValue(QPoint(start_x, start_y))
            self.animation.setEndValue(QPoint(target_x, target_y))
            self.animation.start()

            # 启动形状渐变定时器
            self.morph_timer.start()

            # 随机设置初始渐变进度，避免所有元素同步变化
            self.shape_morph_progress = random.uniform(0.0, 0.5)

    def paintEvent(self, event):
        """自定义绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 事件参数使用以避免警告
        _ = event

        # 创建剪切区域，限制绘制在元素边界内
        painter.setClipRect(self.rect())

        # 计算安全的绘制区域，确保完全在元素内
        padding = 1  # 添加内边距
        draw_size = max(1, self.size - padding * 2)  # 确保至少有1像素
        draw_x = padding
        draw_y = padding
        center_x = draw_x + draw_size / 2
        center_y = draw_y + draw_size / 2

        # 设置绘制属性
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.color)

        # 根据渐变进度混合当前形状和目标形状
        progress = self.shape_morph_progress

        # 如果当前形状和目标形状相同，直接绘制当前形状
        if self.current_shape == self.target_shape:
            self._draw_shape(painter, self.current_shape, draw_x, draw_y, draw_size, center_x, center_y)
        else:
            # 使用形状插值实现真正的形状渐变
            self._draw_morphed_shape(painter, self.current_shape, self.target_shape, progress,
                                     draw_x, draw_y, draw_size, center_x, center_y)

    def _draw_shape(self, painter, shape_type, draw_x, draw_y, draw_size, center_x, center_y):
        """绘制指定形状"""
        if shape_type == 0:  # 圆形
            # 使用多边形绘制圆形，以便于形状渐变
            scaled_polygon = QPolygonF()
            scale_factor = draw_size / self.size

            for point in self.circle_points:
                # 计算相对于中心的偏移
                dx = point.x() - self.size / 2
                dy = point.y() - self.size / 2
                # 应用缩放并移动到新中心
                new_x = center_x + dx * scale_factor
                new_y = center_y + dy * scale_factor
                scaled_polygon.append(QPointF(new_x, new_y))

            painter.drawPolygon(scaled_polygon)
        elif shape_type == 1:  # 方形
            # 使用多边形绘制方形，以便于形状渐变
            scaled_polygon = QPolygonF()
            scale_factor = draw_size / self.size

            for point in self.square_points:
                # 计算相对于中心的偏移
                dx = point.x() - self.size / 2
                dy = point.y() - self.size / 2
                # 应用缩放并移动到新中心
                new_x = center_x + dx * scale_factor
                new_y = center_y + dy * scale_factor
                scaled_polygon.append(QPointF(new_x, new_y))

            painter.drawPolygon(scaled_polygon)
        elif shape_type == 2:  # 三角形
            # 创建缩放后的三角形
            scaled_polygon = QPolygonF()
            scale_factor = draw_size / self.size

            for point in self.triangle_points:
                # 计算相对于中心的偏移
                dx = point.x() - self.size / 2
                dy = point.y() - self.size / 2
                # 应用缩放并移动到新中心
                new_x = center_x + dx * scale_factor
                new_y = center_y + dy * scale_factor
                scaled_polygon.append(QPointF(new_x, new_y))

            painter.drawPolygon(scaled_polygon)
        elif shape_type == 3:  # 六边形
            # 创建缩放后的六边形
            scaled_polygon = QPolygonF()
            scale_factor = draw_size / self.size

            for point in self.hexagon_points:
                # 计算相对于中心的偏移
                dx = point.x() - self.size / 2
                dy = point.y() - self.size / 2
                # 应用缩放并移动到新中心
                new_x = center_x + dx * scale_factor
                new_y = center_y + dy * scale_factor
                scaled_polygon.append(QPointF(new_x, new_y))

            painter.drawPolygon(scaled_polygon)
        elif shape_type == 4:  # 五角星
            # 创建缩放后的五角星
            scaled_polygon = QPolygonF()
            scale_factor = draw_size / self.size

            for point in self.star_points:
                # 计算相对于中心的偏移
                dx = point.x() - self.size / 2
                dy = point.y() - self.size / 2
                # 应用缩放并移动到新中心
                new_x = center_x + dx * scale_factor
                new_y = center_y + dy * scale_factor
                scaled_polygon.append(QPointF(new_x, new_y))

            painter.drawPolygon(scaled_polygon)
        else:  # 梯形 (shape_type == 5)
            # 创建缩放后的梯形
            scaled_polygon = QPolygonF()
            scale_factor = draw_size / self.size

            for point in self.trapezoid_points:
                # 计算相对于中心的偏移
                dx = point.x() - self.size / 2
                dy = point.y() - self.size / 2
                # 应用缩放并移动到新中心
                new_x = center_x + dx * scale_factor
                new_y = center_y + dy * scale_factor
                scaled_polygon.append(QPointF(new_x, new_y))

            painter.drawPolygon(scaled_polygon)

    def _draw_morphed_shape(self, painter, from_shape, to_shape, progress, draw_x, draw_y, draw_size, center_x, center_y):
        """绘制形状渐变效果"""
        # 获取起始形状和目标形状的点
        if from_shape == 0:
            from_points = self.circle_points
        elif from_shape == 1:
            from_points = self.square_points
        elif from_shape == 2:
            from_points = self.triangle_points
        elif from_shape == 3:
            from_points = self.hexagon_points
        elif from_shape == 4:
            from_points = self.star_points
        else:  # from_shape == 5
            from_points = self.trapezoid_points

        if to_shape == 0:
            to_points = self.circle_points
        elif to_shape == 1:
            to_points = self.square_points
        elif to_shape == 2:
            to_points = self.triangle_points
        elif to_shape == 3:
            to_points = self.hexagon_points
        elif to_shape == 4:
            to_points = self.star_points
        else:  # to_shape == 5
            to_points = self.trapezoid_points

        # 处理不同形状点数不同的情况
        # 将点数较少的形状扩展到与点数较多的形状相同
        from_count = len(from_points)
        to_count = len(to_points)

        # 创建插值后的多边形
        morphed_polygon = QPolygonF()
        scale_factor = draw_size / self.size

        # 使用较多点数的形状作为参考
        if from_count >= to_count:
            reference_count = from_count
            # 扩展目标形状的点
            expanded_to_points = self._expand_points(to_points, reference_count)
            expanded_from_points = from_points
        else:
            reference_count = to_count
            # 扩展起始形状的点
            expanded_from_points = self._expand_points(from_points, reference_count)
            expanded_to_points = to_points

        # 对每个点进行插值
        # 首先创建一个临时多边形，用于计算边界
        temp_polygon = QPolygonF()

        for i in range(reference_count):
            # 计算插值点
            from_x = expanded_from_points[i].x()
            from_y = expanded_from_points[i].y()
            to_x = expanded_to_points[i].x()
            to_y = expanded_to_points[i].y()

            # 线性插值
            morphed_x = from_x + (to_x - from_x) * progress
            morphed_y = from_y + (to_y - from_y) * progress

            # 添加到临时多边形
            temp_polygon.append(QPointF(morphed_x, morphed_y))

        # 计算多边形的边界矩形
        bound_rect = temp_polygon.boundingRect()

        # 计算当前形状的大小
        shape_width = bound_rect.width()
        shape_height = bound_rect.height()

        # 计算中心点
        center_point_x = bound_rect.x() + shape_width / 2
        center_point_y = bound_rect.y() + shape_height / 2

        # 计算需要的最小尺寸
        min_size = self.size * 0.9

        # 计算额外的缩放因子，确保形状不会小于最小尺寸
        extra_scale_x = 1.0
        extra_scale_y = 1.0

        if shape_width < min_size:
            extra_scale_x = min_size / shape_width

        if shape_height < min_size:
            extra_scale_y = min_size / shape_height

        # 使用较大的缩放因子，保持形状比例
        extra_scale = max(extra_scale_x, extra_scale_y)

        # 应用额外缩放并创建最终多边形
        for i in range(reference_count):
            morphed_x = temp_polygon[i].x()
            morphed_y = temp_polygon[i].y()

            # 应用额外缩放，相对于形状中心
            if extra_scale > 1.0:
                dx = morphed_x - center_point_x
                dy = morphed_y - center_point_y

                morphed_x = center_point_x + dx * extra_scale
                morphed_y = center_point_y + dy * extra_scale

            # 计算相对于中心的偏移
            dx = morphed_x - self.size / 2
            dy = morphed_y - self.size / 2

            # 应用缩放并移动到新中心
            new_x = center_x + dx * scale_factor
            new_y = center_y + dy * scale_factor

            morphed_polygon.append(QPointF(new_x, new_y))

        # 绘制渐变后的形状
        painter.drawPolygon(morphed_polygon)

    def _expand_points(self, points, target_count):
        """扩展点数组以匹配目标数量"""
        if len(points) == target_count:
            return points

        result = []
        original_count = len(points)

        # 如果原始点数为0，返回空列表
        if original_count == 0:
            return result

        # 计算每个原始点应该生成多少新点
        ratio = float(target_count) / original_count

        for i in range(target_count):
            # 计算对应的原始点索引
            original_index = int(i / ratio)
            next_index = (original_index + 1) % original_count

            # 计算在两个原始点之间的插值比例
            local_progress = (i / ratio) - original_index

            # 插值计算新点
            from_x = points[original_index].x()
            from_y = points[original_index].y()
            to_x = points[next_index].x()
            to_y = points[next_index].y()

            new_x = from_x + (to_x - from_x) * local_progress
            new_y = from_y + (to_y - from_y) * local_progress

            result.append(QPointF(new_x, new_y))

        return result


class ArtisticNotificationContent(QWidget):
    """艺术风格通知内容组件"""

    clicked = pyqtSignal()

    def __init__(self, message, level, parent=None, enable_floating_elements=True):
        super().__init__(parent)
        self.level = level
        self.message = message
        self._floating_elements = []
        self.enable_floating_elements = enable_floating_elements  # 控制浮动元素的开关

        # 创建主布局
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 创建背景层
        self.background = QWidget(self)
        self.background.setObjectName("background")
        self.main_layout.addWidget(self.background, 0, 0)

        # 创建内容层
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("content")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(12)
        self.main_layout.addWidget(self.content_widget, 0, 0)

        # 创建标题行
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(10)

        # 创建图标
        self.icon = QSvgWidget()
        self.icon.setFixedSize(24, 24)
        self.header_layout.addWidget(self.icon)

        # 创建标题
        self.title = QLabel(self.getTitleText(level))
        title_font = QFont("Segoe UI", 11)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.header_layout.addWidget(self.title)

        # 添加弹性空间
        self.header_layout.addStretch(1)

        # 创建关闭按钮
        self.close_button = QPushButton()
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(Qt.PointingHandCursor)
        # 使用父窗口的hide方法，确保使用我们修改后的动画
        self.close_button.clicked.connect(lambda: self.parent().hide())
        self.header_layout.addWidget(self.close_button)

        # 添加标题行到内容布局
        self.content_layout.addWidget(self.header_widget)

        # 创建分隔线
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFixedHeight(1)
        self.content_layout.addWidget(self.separator)

        # 创建消息文本
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        message_font = QFont("Segoe UI", 10)
        self.message_label.setFont(message_font)
        self.content_layout.addWidget(self.message_label)
        # 添加弹性空间
        self.content_layout.addStretch(1)

        # 创建浮动装饰元素
        self._create_floating_elements()

        # 应用样式
        self._update_style()

    def _create_floating_elements(self):
        """创建浮动装饰元素"""
        # 如果浮动元素功能关闭，直接返回
        if not self.enable_floating_elements:
            return

        main_color, _, _, _, _ = self.getColor(self.level)

        # 创建浮动元素个数
        num_elements = random.randint(10, 12)

        # 确保形状多样性，强制至少有一个每种形状
        shape_distribution = [0, 1, 2, 3, 4, 5]  # 圆形、方形、三角形、六边形、五角星、梯形
        random.shuffle(shape_distribution)  # 打乱形状分配

        # 创建不同大小和透明度的元素
        for i in range(num_elements):
            # 设置适当的元素大小，使形状更容易辨识
            size = random.randint(8, 10)  # 增大元素尺寸，使形状更明显

            # 强制创建至少一个特殊形状
            if i == 0:
                # 第一个元素随机选择一个特殊形状
                special_shapes = [3, 4, 5]  # 六边形、五角星、梯形
                shape_type = random.choice(special_shapes)

                if shape_type == 3:  # 六边形
                    size = 10  # 六边形特意设置为最大尺寸
                    opacity = random.uniform(0.30, 0.45)  # 增加不透明度，使六边形更明显
                elif shape_type == 4:  # 五角星
                    size = 10  # 五角星特意设置为最大尺寸
                    opacity = random.uniform(0.28, 0.40)  # 五角星的不透明度
                else:  # 梯形 (shape_type == 5)
                    size = 9  # 梯形稍小一点
                    opacity = random.uniform(0.22, 0.35)  # 梯形的不透明度
            # 为不同形状设置不同的透明度范围
            elif i < len(shape_distribution):
                # 使用预定的形状分配
                shape_type = shape_distribution[i-1]  # 偏移1，因为第一个已经分配了
                # 根据形状调整透明度
                if shape_type == 0:  # 圆形稍微不透明
                    opacity = random.uniform(0.25, 0.30)
                elif shape_type == 1:  # 方形稍微透明一点
                    opacity = random.uniform(0.21, 0.25)
                elif shape_type == 2:  # 三角形比较透明
                    opacity = random.uniform(0.18, 0.23)
                elif shape_type == 3:  # 六边形的透明度
                    opacity = random.uniform(0.30, 0.45)  # 显著增加六边形的不透明度
                elif shape_type == 4:  # 五角星的透明度
                    opacity = random.uniform(0.28, 0.40)  # 五角星较高的不透明度
                else:  # 梯形的透明度 (shape_type == 5)
                    opacity = random.uniform(0.22, 0.35)  # 梯形中等不透明度
            else:
                # 如果元素数量超过预定形状，随机选择
                shape_type = random.randint(0, 5)  # 包括所有形状
                # 根据形状类型调整透明度和大小
                if shape_type == 3:  # 六边形
                    opacity = random.uniform(0.30, 0.45)
                    size = 10  # 六边形特意设置为最大尺寸
                elif shape_type == 4:  # 五角星
                    opacity = random.uniform(0.28, 0.40)
                    size = 10  # 五角星特意设置为最大尺寸
                elif shape_type == 5:  # 梯形
                    opacity = random.uniform(0.22, 0.35)
                    size = 9  # 梯形稍小一点
                else:  # 其他形状
                    opacity = random.uniform(0.1, 0.25)

            # 创建元素并指定形状
            element = FloatingElement(self, size, main_color, opacity)
            element.current_shape = shape_type  # 显式设置形状类型
            self._floating_elements.append(element)
            element.show()

    def start_animations(self):
        """开始所有动画"""
        # 如果浮动元素功能关闭或没有浮动元素，直接返回
        if not self.enable_floating_elements or not self._floating_elements:
            return

        for element in self._floating_elements:
            element.start_animation()

    def set_floating_elements_enabled(self, enabled):
        """设置浮动元素是否启用"""
        # 如果状态没有变化，直接返回
        if self.enable_floating_elements == enabled:
            return

        self.enable_floating_elements = enabled

        # 如果禁用浮动元素，隐藏并清除现有元素
        if not enabled:
            for element in self._floating_elements:
                element.hide()
            self._floating_elements.clear()
        else:
            # 如果启用浮动元素，创建新的元素
            self._create_floating_elements()
            self.start_animations()

    def _update_style(self):
        """更新样式"""
        # 获取颜色
        main_color, _, text_color, bg_color, border_color = self.getColor(self.level)
        icon_path = self.getIcon(level=self.level)

        # 设置背景样式
        self.background.setStyleSheet(f"""
            QWidget#background {{
                background-color: {bg_color};
                border-radius: 16px;
                border: 1px solid {border_color};
            }}
        """)

        # 设置内容层样式
        self.content_widget.setStyleSheet(f"""
            QWidget#content {{
                background-color: transparent;
            }}
        """)

        # 设置标题样式
        self.title.setStyleSheet(f"""
            QLabel {{
                color: {main_color};
                font-size: 16px;
                font-family: 'Segoe UI';
            }}
        """)

        # 设置分隔线样式
        self.separator.setStyleSheet(f"""
            QFrame {{
                background-color: {border_color};
            }}
        """)

        # 设置消息文本样式
        self.message_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 14px;
                font-family: 'Segoe UI';
            }}
        """)

        # 设置关闭按钮样式
        self.close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.15);
            }}
        """)

        # 设置图标
        try:
            file = QFile(icon_path)
            if file.open(QFile.ReadOnly | QFile.Text):
                svg_content = str(file.readAll().data(), encoding='utf-8')
                file.close()
                svg_content = svg_content.replace('currentColor', main_color)
                self.icon.load(bytes(svg_content, 'utf-8'))
        except Exception as e:
            print(f"Error setting icon: {e}")
            # 如果加载图标失败，创建一个简单的备用图标
            self._create_fallback_icon(main_color)

        # 设置关闭按钮图标 - 使用SVG图标和备用方法
        try:
            # 先尝试使用资源文件中的SVG图标
            close_icon_path = ':/resources/ic_fluent_dismiss_regular.svg'

            if QFile.exists(close_icon_path):
                # 使用SVG文件
                file = QFile(close_icon_path)
                if file.open(QFile.ReadOnly | QFile.Text):
                    svg_content = str(file.readAll().data(), encoding='utf-8')
                    file.close()

                    # 替换颜色
                    svg_content = svg_content.replace('currentColor', text_color)

                    # 创建SVG渲染器
                    renderer = QSvgRenderer(bytes(svg_content, 'utf-8'))

                    # 创建高分辨率的图标
                    pixmap = QPixmap(48, 48)  # 使用更高的分辨率支持高DPI
                    pixmap.fill(Qt.transparent)

                    painter = QPainter(pixmap)
                    painter.setRenderHint(QPainter.Antialiasing)
                    renderer.render(painter)
                    painter.end()

                    # 设置图标
                    self.close_button.setIcon(QIcon(pixmap))
                    self.close_button.setIconSize(QSize(16, 16))
                else:
                    # 如果无法打开文件，使用备用方法
                    self._create_fallback_close_icon(text_color)
            else:
                # 如果文件不存在，使用备用方法
                self._create_fallback_close_icon(text_color)
        except Exception as e:
            print(f"Error setting close button icon: {e}")
            # 出错时使用备用方法
            self._create_fallback_close_icon(text_color)

    def _create_fallback_icon(self, color):
        """创建备用的信息图标"""
        # 创建一个简单的信息图标
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置画笔颜色和宽度
        pen = QPen(QColor(color))
        pen.setWidth(2)
        painter.setPen(pen)

        # 绘制圆形
        painter.drawEllipse(2, 2, 20, 20)

        # 绘制感叹号
        painter.drawLine(12, 7, 12, 14)
        painter.drawEllipse(12, 17, 2, 2)

        painter.end()

        # 设置图标
        self.icon.load(pixmap.toImage())

    def _create_fallback_close_icon(self, color):
        """创建备用的关闭图标"""
        # 创建一个简单的X形状图标
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置画笔颜色和宽度
        pen = QPen(QColor(color))
        pen.setWidth(2)
        painter.setPen(pen)

        # 绘制X形状
        painter.drawLine(6, 6, 18, 18)
        painter.drawLine(6, 18, 18, 6)
        painter.end()

        # 设置图标
        self.close_button.setIcon(QIcon(pixmap))
        self.close_button.setIconSize(QSize(16, 16))

    def paintEvent(self, event):
        """自定义绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 事件参数使用以避免警告
        _ = event

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 发送点击信号
            self.clicked.emit()

        super().mousePressEvent(event)

    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        self.parent().fold_timer.stop()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        self.parent().fold_timer.start()

    @staticmethod
    def getColor(level):
        """获取不同级别通知的颜色"""
        colors = {
            'info': ['#4361EE', '#4CC9F0', '#111827', '#F9FAFB', '#E5E7EB'],      # 蓝色
            'warning': ['#F59E0B', '#FBBF24', '#111827', '#FFFBEB', '#FEF3C7'],   # 橙色
            'error': ['#EF4444', '#F87171', '#111827', '#FEF2F2', '#FEE2E2'],     # 红色
            'success': ['#10B981', '#34D399', '#111827', '#ECFDF5', '#D1FAE5']    # 绿色
        }
        return colors.get(level, colors['info'])

    @staticmethod
    def getTitleText(level):
        """获取不同级别的标题文本"""
        titles = {
            'info': '信息通知',
            'warning': '警告通知',
            'error': '错误通知',
            'success': '成功通知'
        }
        return titles.get(level, titles['info'])

    @staticmethod
    def getIcon(level):
        """获取不同级别的图标"""
        icon_map = {
            'info': ':/resources/ic_fluent_info_filled.svg',
            'warning': ':/resources/ic_fluent_warning_filled.svg',
            'error': ':/resources/ic_fluent_dismiss_circle_filled.svg',
            'success': ':/resources/ic_fluent_checkmark_circle_filled.svg'
        }
        return icon_map.get(level, icon_map['info'])

    def sizeHint(self):
        """重写sizeHint以提供基于内容的建议大小"""
        # 计算消息文本所需的高度
        fm = QFontMetrics(self.message_label.font())
        text_width = 300  # 假设最大宽度为300
        text_rect = fm.boundingRect(
            0, 0, text_width, 1000,
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop,
            self.message
        )

        # 计算总高度 (标题行 + 分隔线 + 消息文本 + 边距)
        height = 24 + 1 + text_rect.height() + 40 + 40  # 标题高度 + 分隔线 + 文本高度 + 上下边距

        # 确保最小高度
        height = max(height, 140)

        return QSize(360, height)


class ArtisticNotificationWidget(QWidget):
    """艺术风格通知窗口组件"""

    closed = pyqtSignal()
    clicked = pyqtSignal()

    def __init__(self, message, level, parent=None, enable_floating_elements=True):
        super().__init__(parent)
        self.level = level
        self.enable_floating_elements = enable_floating_elements

        # 设置窗口属性
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_NoSystemBackground)

        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # 创建内容
        self.content = ArtisticNotificationContent(message, level, self, enable_floating_elements)
        self.content.clicked.connect(self.clicked.emit)
        self.main_layout.addWidget(self.content)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 10)
        self.content.setGraphicsEffect(shadow)

        # 设置最小尺寸
        self.setMinimumSize(400, 180)

        # 创建自动关闭定时器
        self.fold_timer = QTimer(self)
        self.fold_timer.setSingleShot(True)
        self.fold_timer.setInterval(5000)  # 5秒后自动关闭
        self.fold_timer.timeout.connect(self.hide)

        # 设置位置和动画
        self._setup_position()
        self._setup_animations()

    def _setup_position(self):
        """设置窗口位置"""
        desktop = QApplication.desktop()
        if desktop:
            available_geometry = desktop.availableGeometry()
            screen_width = available_geometry.width()
            screen_height = available_geometry.height()
        else:
            screen_width = 1920
            screen_height = 1080

        # 设置安全边距
        margin = 20

        # 获取内容建议的大小并设置窗口大小 - 限制最大尺寸
        content_size = self.content.sizeHint()
        width = max(400, min(screen_width - margin * 2, content_size.width() + 40))
        height = max(180, min(screen_height - margin * 2, content_size.height() + 40))
        self.setFixedSize(width, height)

        # 计算位置（屏幕右上角） - 确保不超出屏幕边界
        x = max(margin, min(screen_width - width - margin, int(screen_width - width - margin)))
        y = max(margin, min(screen_height - height - margin, int(screen_height * 0.1)))
        self.move(x, y)

    def _setup_animations(self):
        """设置动画效果"""
        # 位置动画 - 先短促有力后缓慢的渐入动画
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(400)  # 缩短时间使动画更加短促
        self.pos_animation.setEasingCurve(QEasingCurve.OutQuint)  # 先快后慢的曲线

        # 不透明度动画
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutCubic)

        # 隐藏动画 - 快速渐出
        self.hide_animation = QPropertyAnimation(self, b"windowOpacity")
        self.hide_animation.setDuration(150)  # 进一步缩短时间使渐出更快
        self.hide_animation.setEasingCurve(QEasingCurve.InQuad)  # 快速渐出的曲线

        # 隐藏时的位置动画 - 由左向右移出
        self.hide_pos_animation = QPropertyAnimation(self, b"pos")
        self.hide_pos_animation.setDuration(150)  # 与透明度动画同步，减少时间
        self.hide_pos_animation.setEasingCurve(QEasingCurve.InQuad)

    def show(self):
        """重写show方法，添加动画效果"""
        # 先调用_setup_position确保窗口位置正确
        self._setup_position()

        super().show()

        # 计算安全的起始位置（从右向左滑入）
        desktop = QApplication.desktop()
        if desktop:
            available_geometry = desktop.availableGeometry()
            screen_width = available_geometry.width()
        else:
            screen_width = 1920

        # 确保起始位置不超出屏幕
        margin = 20
        # 从右向左滑入，起始位置在当前位置右侧100像素
        start_x = min(self.x() + 100, screen_width - margin)

        self.pos_animation.setStartValue(QPoint(start_x, self.y()))
        self.pos_animation.setEndValue(self.pos())

        # 设置不透明度动画
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)

        # 创建动画组，同时运行位置和透明度动画
        animation_group = QParallelAnimationGroup(self)
        animation_group.addAnimation(self.pos_animation)
        animation_group.addAnimation(self.opacity_animation)
        animation_group.start()

        # 启动自动关闭定时器
        self.fold_timer.start()

        # 启动浮动元素动画
        self.content.start_animations()

    def hide(self):
        """重写hide方法，添加消失动画"""
        # 设置不透明度动画 - 快速渐出
        self.hide_animation.setStartValue(self.windowOpacity())
        self.hide_animation.setEndValue(0.0)

        # 设置位置动画 - 由左向右移出
        # 计算目标位置（往右移动15像素）
        target_pos = QPoint(self.x() + 15, self.y())  # 向右移动，减小距离
        self.hide_pos_animation.setStartValue(self.pos())
        self.hide_pos_animation.setEndValue(target_pos)

        # 创建动画组，同时运行位置和透明度动画
        animation_group = QParallelAnimationGroup(self)
        animation_group.addAnimation(self.hide_animation)
        animation_group.addAnimation(self.hide_pos_animation)

        # 连接动画完成信号
        animation_group.finished.connect(super().hide)
        animation_group.finished.connect(lambda: self.closed.emit())

        # 开始动画
        animation_group.start()

    def paintEvent(self, event):
        """重写绘制事件以确保正确的窗口区域"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.end()

        # 事件参数使用以避免警告
        _ = event


class NotificationManager(QObject):
    """通知管理器"""

    showNotificationSignal = pyqtSignal(str, str, int, object)  # message, level, duration, source
    notificationClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_notification = None
        self.notification_queue = []
        self.is_showing = False
        self.last_message = None
        self.last_time = 0
        self.last_source = None
        self.throttle_interval = 1000
        self.default_duration = 3000  # 默认显示时间
        self.enable_floating_elements = True  # 浮动元素开关，默认开启
        self.is_shutting_down = False  # 标记程序是否正在关闭
        # 连接信号到通知显示方法，使用lambda以支持新的参数格式
        self.showNotificationSignal.connect(
            lambda message, level, duration, source: self.showNotification(message, level, duration, source)
        )

    def setDefaultDuration(self, duration):
        self.default_duration = duration

    def showNotification(self, message, level="info", duration=None, source=None):
        # 如果程序正在关闭，不再显示新的通知
        if self.is_shutting_down:
            return

        current_time = QDateTime.currentMSecsSinceEpoch()

        if source is not None and source != self.last_source:
            self.closeAllNotifications()
            self.last_source = source
            self.last_message = None
            self.last_time = 0
        elif (message == self.last_message and
              current_time - self.last_time < self.throttle_interval and
              source == self.last_source):
            return

        self.last_message = message
        self.last_time = current_time

        actual_duration = duration if duration is not None else self.default_duration

        self.notification_queue.append((message, level, actual_duration))

        if not self.is_showing:
            self._showNext()

    def _showNext(self):
        # 如果程序正在关闭或没有通知在队列中，不再显示新的通知
        if self.is_shutting_down or not self.notification_queue:
            self.is_showing = False
            return

        message, level, duration = self.notification_queue.pop(0)

        try:
            # 创建通知窗口，使用当前的浮动元素设置
            self.current_notification = ArtisticNotificationWidget(message, level, enable_floating_elements=self.enable_floating_elements)
            self.current_notification.closed.connect(self._onNotificationClosed)
            self.current_notification.clicked.connect(self.notificationClicked.emit)
            self.current_notification.fold_timer.setInterval(duration)
            self.current_notification.show()
            self.is_showing = True
        except Exception as e:
            # 如果创建通知窗口时出错，可能是因为程序正在关闭
            print(f"Error showing notification: {e}")
            self.is_showing = False

    def _onNotificationClosed(self):
        # 如果程序正在关闭，不再显示新的通知
        if self.is_shutting_down:
            if self.current_notification:
                self.current_notification.deleteLater()
                self.current_notification = None
            return

        if self.current_notification:
            try:
                self.current_notification.deleteLater()
                self.current_notification = None
                # 使用安全的定时器显示下一个通知
                QTimer.singleShot(100, self._showNext)
            except Exception as e:
                # 如果删除通知窗口时出错，可能是因为程序正在关闭
                print(f"Error closing notification: {e}")
                self.current_notification = None

    def closeAllNotifications(self):
        """关闭所有通知"""
        self.notification_queue.clear()
        if self.current_notification:
            try:
                self.current_notification.hide()
            except Exception as e:
                # 如果隐藏通知窗口时出错，可能是因为程序正在关闭
                print(f"Error hiding notification: {e}")
                if self.current_notification:
                    self.current_notification.deleteLater()
                    self.current_notification = None

    def showMessage(self, message, level="info", duration=None, source=None):
        """显示消息的便捷方法
        Args:
            message: 消息内容
            level: 通知级别 (info/warning/error/success)
            duration: 显示时长(毫秒)，如果为None则使用默认时长
            source: 消息来源标识，用于区分不同来源的消息
        """
        self.showNotificationSignal.emit(
            message,
            level,
            duration if duration is not None else self.default_duration,
            source
        )

    def setThrottleInterval(self, interval):
        self.throttle_interval = interval

    def setFloatingElementsEnabled(self, enabled):
        """设置浮动元素是否启用"""
        self.enable_floating_elements = enabled

        # 如果当前有显示的通知，也更新其浮动元素设置
        if self.current_notification:
            self.current_notification.content.set_floating_elements_enabled(enabled)

    def isFloatingElementsEnabled(self):
        """获取浮动元素是否启用"""
        return self.enable_floating_elements

    def shutdown(self):
        """安全关闭通知管理器，应在程序关闭前调用"""
        # 标记程序正在关闭
        self.is_shutting_down = True

        # 清空通知队列
        self.notification_queue.clear()

        # 安全关闭当前通知
        if self.current_notification:
            try:
                # 断开信号连接，避免回调触发新的通知
                if self.current_notification.closed.receivers() > 0:
                    self.current_notification.closed.disconnect()

                # 尝试先隐藏通知，这样可以触发动画
                self.current_notification.hide()

                # 等待一小段时间后删除通知
                QTimer.singleShot(200, lambda: self._finalCleanup())
            except Exception as e:
                # 如果出错，直接删除通知
                print(f"Error during notification shutdown: {e}")
                self._finalCleanup()

    def _finalCleanup(self):
        """最终清理通知资源"""
        if self.current_notification:
            try:
                self.current_notification.deleteLater()
            except Exception:
                pass  # 忽略清理过程中的错误
            self.current_notification = None

        # 断开所有信号连接
        try:
            self.showNotificationSignal.disconnect()
        except Exception:
            pass  # 忽略断开信号连接时的错误


# 测试代码
if __name__ == "__main__":
    import sys

    # 启用高DPI缩放
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # 创建通知管理器
    manager = NotificationManager()

    # 创建一个简单的测试窗口
    test_window = QWidget()
    test_window.setWindowTitle("通知组件测试")
    test_window.resize(600, 400)

    layout = QVBoxLayout(test_window)

    # 创建测试按钮
    info_btn = QPushButton("显示信息通知")
    warning_btn = QPushButton("显示警告通知")
    error_btn = QPushButton("显示错误通知")
    success_btn = QPushButton("显示成功通知")
    toggle_btn = QPushButton("切换浮动元素")
    multi_btn = QPushButton("显示多个通知")
    exit_btn = QPushButton("安全关闭测试")

    # 设置按钮字体大小
    font = QFont()
    font.setPointSize(10)
    info_btn.setFont(font)
    warning_btn.setFont(font)
    error_btn.setFont(font)
    success_btn.setFont(font)
    toggle_btn.setFont(font)
    multi_btn.setFont(font)
    exit_btn.setFont(font)

    # 连接按钮信号
    info_btn.clicked.connect(lambda: manager.showMessage("这是一条信息通知，用于展示一般性的信息。", "info"))
    warning_btn.clicked.connect(lambda: manager.showMessage("这是一条警告通知，用于提醒用户注意某些问题。", "warning"))
    error_btn.clicked.connect(lambda: manager.showMessage("这是一条错误通知，用于提示用户发生了错误。", "error"))
    success_btn.clicked.connect(lambda: manager.showMessage("这是一条成功通知，用于提示用户操作成功。", "success"))

    # 浮动元素开关
    toggle_btn.clicked.connect(lambda: manager.setFloatingElementsEnabled(not manager.isFloatingElementsEnabled()))

    # 显示多个通知
    def show_multiple_notifications():
        manager.showMessage("第一条通知", "info", 3000)
        QTimer.singleShot(500, lambda: manager.showMessage("第二条通知", "warning", 3000))
        QTimer.singleShot(1000, lambda: manager.showMessage("第三条通知", "error", 3000))
        QTimer.singleShot(1500, lambda: manager.showMessage("第四条通知", "success", 3000))

    multi_btn.clicked.connect(show_multiple_notifications)

    # 安全关闭测试
    def safe_exit():
        # 先安全关闭通知管理器
        print("正在安全关闭通知管理器...")
        manager.shutdown()
        # 等待一小段时间后关闭程序
        QTimer.singleShot(300, app.quit)

    exit_btn.clicked.connect(safe_exit)

    # 添加按钮到布局
    layout.addWidget(info_btn)
    layout.addWidget(warning_btn)
    layout.addWidget(error_btn)
    layout.addWidget(success_btn)
    layout.addWidget(multi_btn)
    layout.addWidget(toggle_btn)
    layout.addWidget(exit_btn)
    layout.addStretch(1)

    # 显示当前设备像素比例
    dpi_label = QLabel(f"当前设备像素比例: {get_device_pixel_ratio():.2f}")
    dpi_label.setFont(font)
    layout.addWidget(dpi_label)

    # 在窗口关闭时安全关闭通知管理器
    test_window.closeEvent = lambda event: (manager.shutdown(), event.accept())

    # 显示测试窗口
    test_window.show()

    # 显示一条欢迎通知
    QTimer.singleShot(500, lambda: manager.showMessage("欢迎使用PyQt5通知组件！\n\n这个通知组件支持高DPI屏幕，可以在不同分辨率的屏幕上正常显示。\n\n点击下方按钮测试不同类型的通知。", "info", 8000))

    sys.exit(app.exec_())

