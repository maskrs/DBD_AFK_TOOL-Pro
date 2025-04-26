from PySide6.QtWidgets import QStackedWidget, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QPoint
from PySide6.QtGui import QPainter, QPixmap, QRegion
from PySide6.QtWidgets import QApplication
import logging

logger = logging.getLogger(__name__)

class AnimatedStackedWidget(QStackedWidget):
    """带动画效果的堆叠窗口部件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 动画相关
        self._current_value = 0.0
        self._animation = QPropertyAnimation(self, b"slide_value", self)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)  # 使用平滑的缓动曲线
        self._animation.setDuration(300)

        # 缓存相关
        self._next_widget = None
        self._current_widget = None
        self._next_index = -1
        self._pixmap_cache = {}
        self._is_first_show = True  # 标记是否是首次显示

        # 连接动画完成信号
        self._animation.finished.connect(self._on_animation_finished)

    def _get_slide_value(self) -> float:
        return self._current_value

    def _set_slide_value(self, value: float):
        self._current_value = value
        # 不再需要计算当前页面的透明度，因为它会立即消失
        self.update()

    slide_value = Property(float, _get_slide_value, _set_slide_value)

    def _render_widget_to_pixmap(self, widget: QWidget) -> QPixmap:
        """将widget渲染到pixmap"""
        if not widget:
            return None

        # 记录原始可见性状态
        was_visible = widget.isVisible()

        # 使用特殊方式准备widget，避免在屏幕上显示
        # 将widget移动到屏幕外的位置进行渲染
        original_pos = widget.pos()
        widget.move(-10000, -10000)  # 移动到屏幕外
        widget.show()
        widget.updateGeometry()
        if widget.layout():
            widget.layout().activate()
        QApplication.processEvents()

        # 使用缓存的设备像素比
        device_pixel_ratio = self.devicePixelRatio()

        # 创建适当大小的pixmap
        size = widget.size()
        pixmap = QPixmap(size * device_pixel_ratio)
        pixmap.setDevicePixelRatio(device_pixel_ratio)
        pixmap.fill(Qt.transparent)

        # 使用高质量渲染
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        widget.render(painter, QPoint(), QRegion(), QWidget.DrawChildren)
        painter.end()

        # 恢复原始位置
        widget.move(original_pos)

        # 恢复原始可见性状态
        if not was_visible:
            widget.hide()

        return pixmap

    def setCurrentIndex(self, index: int):
        """重写切换页面方法"""
        if self.currentIndex() == index or index < 0:
            return

        # 停止任何正在进行的动画
        self._animation.stop()

        # 获取当前和目标页面
        current = self.currentWidget()
        next_widget = self.widget(index)

        if not next_widget:
            return

        # 立即隐藏当前页面，使其立即消失
        if current:
            current.hide()

        # 立即隐藏目标页面，防止闪现
        next_widget.hide()

        # 保存页面引用
        self._current_widget = current
        self._next_widget = next_widget
        self._next_index = index

        try:
            # 预先调整目标页面大小，避免动画过程中的大小变化
            next_widget.resize(self.size())

            # 不再需要渲染当前页面，因为它已经被隐藏了
            # 当前页面已经在前面的代码中被隐藏

            # 渲染新页面，确保在渲染过程中不会显示
            next_pixmap = self._render_widget_to_pixmap(next_widget)
            if next_pixmap:
                self._pixmap_cache['next'] = next_pixmap
            # 再次确保页面保持隐藏状态
            next_widget.hide()

            # 开始动画
            self._current_value = 0.0
            self._animation.setStartValue(0.0)
            self._animation.setEndValue(1.0)
            self._animation.start()

        except Exception:
            # 异常处理，回退到标准切换方式
            self._cleanup()
            super().setCurrentIndex(index)

    def _cleanup(self):
        """清理缓存和状态"""
        # 清理缓存
        self._pixmap_cache.clear()

        # 当前页面已经被隐藏，不需要再次隐藏
        # 新页面在动画完成时已经处理了显示

        # 重置状态
        self._current_widget = None
        self._next_widget = None
        self._next_index = -1
        self._current_value = 0.0

    def _on_animation_finished(self):
        """动画完成时的处理"""
        try:
            if self._next_index >= 0:
                # 先设置页面索引
                super().setCurrentIndex(self._next_index)
                # 确保新页面显示
                if self._next_widget:
                    self._next_widget.show()
        finally:
            self._cleanup()
            self.update()

    def paintEvent(self, event):
        """自定义绘制"""
        if not self._animation.state() == QPropertyAnimation.Running:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # 不再绘制当前页面，使其立即消失
        # 只绘制新页面的动画效果

        next_pixmap = self._pixmap_cache.get('next')
        if next_pixmap:
            # 使用垂直方向的滑动效果，但减小位移量
            height = self.height()
            # 使用较小的位移量，只有窗口高度的20%
            offset = height * 0.2 * (1 - self._current_value)
            # 使用完全不透明的新页面
            painter.setOpacity(1.0)
            painter.drawPixmap(0, int(offset), next_pixmap)

    def resizeEvent(self, event):
        """处理大小改变事件"""
        super().resizeEvent(event)
        # 调整当前页面大小
        current = self.currentWidget()
        if current:
            current.resize(event.size())
        # 如果正在动画中，也调整目标页面大小
        if self._next_widget:
            self._next_widget.resize(event.size())

    def showEvent(self, event):
        """处理首次显示事件"""
        super().showEvent(event)
        if self._is_first_show:
            self._is_first_show = False
            # 确保所有页面都已正确初始化
            self._init_all_pages()

    def _init_all_pages(self):
        """初始化所有页面"""
        current_index = self.currentIndex()

        for i in range(self.count()):
            widget = self.widget(i)
            if widget:
                # 临时显示并强制布局更新
                widget.show()
                widget.updateGeometry()
                if widget.layout():
                    widget.layout().activate()
                QApplication.processEvents()

                # 渲染一次以确保所有子控件都已正确布局
                temp_pixmap = self._render_widget_to_pixmap(widget)
                del temp_pixmap  # 释放临时pixmap

                # 如果不是当前页面，则隐藏
                if i != current_index:
                    widget.hide()