from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QHBoxLayout, QSizePolicy
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, Property, QSize, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor
from .tooltip import ToolTip

class ModernCard(QWidget):
    """现代化卡片组件

    这是一个现代风格的卡片组件，支持水平和垂直两种布局方式，具有阴影效果和主题切换功能。

    主要特性：
        1. 支持水平和垂直两种布局方式
        2. 自适应内容大小
        3. 可自定义标题字体样式
        4. 可调整内容容器宽度
        5. 支持亮色/暗色主题切换
        6. 鼠标悬停时有阴影动画效果

    基本用法：
        ```python
        # 创建卡片
        card = ModernCard("卡片标题", parent)

        # 设置内容
        content = QWidget()
        card.set_content(content)
        ```

    布局控制：
        1. 设置布局方向：
           ```python
           card.set_content_direction(True)  # True为水平布局，False为垂直布局
           ```

        2. 设置标题和内容间距：水平设置下被弹簧占据，调整不明显
           ```python
           card.set_title_content_spacing(40)  # 设置间距为40像素
           ```

        3. 设置内容容器宽度（仅水平布局有效）：
           ```python
           card.set_content_container_width(200)  # 设置内容容器宽度为200像素
           ```

    字体样式：
        可以自定义标题的字体样式：
        ```python
        # 设置单个属性
        card.set_title_font(size=16)  # 只设置字体大小
        card.set_title_font(color="#FF0000")  # 只设置颜色

        # 设置多个属性
        card.set_title_font(
            size=16,          # 字体大小（像素）
            weight="bold",    # 字体粗细
            family="Arial",   # 字体族
            color="#333333"   # 字体颜色
        )
        ```

    主题切换：
        组件会自动跟随父组件的主题管理器切换主题。
        如果父组件有theme_manager属性，卡片会自动连接并响应主题变化。

    注意事项：
        1. 水平布局时，卡片高度固定为60像素
        2. 垂直布局时，卡片高度会自适应内容
        3. 设置内容后，原有内容会被自动删除
        4. 主题切换会自动处理标题颜色
    """

    def _create_ensure_tooltip(self):
        """创建ensure_tooltip方法"""
        def _ensure_tooltip():
            """确保tooltip已创建"""
            if not self._tooltip and self._tooltip_enabled:
                self._tooltip = ToolTip(self)
                if hasattr(self, 'theme_manager') and self.theme_manager is not None:
                    self._tooltip.theme_manager = self.theme_manager
                self._tooltip.setText(self._tooltip_text)
        return _ensure_tooltip

    def _create_show_tooltip(self):
        """创建show_tooltip方法"""
        def _show_tooltip():
            """显示工具提示"""
            if self._tooltip_enabled and self.underMouse():
                self._ensure_tooltip()
                self._tooltip.show()
        return _show_tooltip

    def _create_hide_tooltip(self):
        """创建hide_tooltip方法"""
        def _hide_tooltip():
            """隐藏工具提示"""
            if self._tooltip:
                self._tooltip.hide()
        return _hide_tooltip

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self._content = None
        self._title_content_spacing = 20  # 默认间距

        # 初始化属性
        self._is_dark_mode = False
        self._shadow_strength = 20

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

        # 移除固定尺寸设置，改为最小尺寸
        self.setMinimumSize(200, 100)

        # 初始化tooltip
        self._tooltip_enabled = False
        self._tooltip = None
        self._tooltip_text = ""
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)

        # 定义并连接tooltip方法
        self._show_tooltip = self._create_show_tooltip()
        self._hide_tooltip = self._create_hide_tooltip()
        self._ensure_tooltip = self._create_ensure_tooltip()
        self._tooltip_timer.timeout.connect(self._show_tooltip)

        self._update_style()

    def _setup_ui(self):
        """初始化UI"""
        # 创建主布局
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 12)  # 减小外边距
        self.layout.setSpacing(0)  # 移除主布局的间距，由container_layout控制

        # 创建可以水平或垂直的容器
        self.container = QWidget()
        self._is_horizontal = False  # 默认为垂直布局
        self._setup_container_layout()
        self.layout.addWidget(self.container)

    def _setup_container_layout(self):
        """设置容器布局"""
        # 移除旧布局（如果存在）
        if hasattr(self, 'container_layout') and self.container_layout:
            # 从旧布局中移除部件（但不删除它们）
            if hasattr(self, 'title_label'):
                self.container_layout.removeWidget(self.title_label)
            if hasattr(self, 'content_widget'):
                self.container_layout.removeWidget(self.content_widget)

            # 删除旧布局
            QWidget().setLayout(self.container_layout)

        # 创建或重用标题标签
        if not hasattr(self, 'title_label'):
            self.title_label = QLabel(self.title)
            self.title_label.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    font-family: "Segoe UI";
                    color: #2c3e50;
                }
            """)

        # 创建或重用内容容器
        if not hasattr(self, 'content_widget'):
            self.content_widget = QWidget()
            self.content_layout = QVBoxLayout(self.content_widget)
            self.content_layout.setContentsMargins(0, 0, 0, 0)  # 移除内容容器的边距
            self.content_layout.setSpacing(8)

        # 创建新布局
        if self._is_horizontal:
            # 创建主容器布局
            self.container_layout = QHBoxLayout(self.container)
            self.container_layout.setContentsMargins(0, 0, 20, 0)  # 只保留右边距
            self.container_layout.setSpacing(self._title_content_spacing)

            # 设置标题固定宽度
            self.title_label.setFixedWidth(70)  # 减小标题宽度
            # 设置固定高度
            self.setFixedHeight(60)  # 减小卡片高度

            # 创建内容容器，用于放置内容并控制位置
            content_container = QWidget()
            content_container.setFixedWidth(200)  # 默认宽度为200
            content_layout = QHBoxLayout(content_container)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
            content_layout.addWidget(self.content_widget, 0, Qt.AlignLeft)

            # 添加标题和内容容器到主布局
            self.container_layout.addWidget(self.title_label)
            self.container_layout.addStretch(1)  # 添加弹性空间
            self.container_layout.addWidget(content_container)

            # 设置对齐方式
            self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            self.container_layout = QVBoxLayout(self.container)
            self.container_layout.setContentsMargins(0, 0, 0, 0)
            self.container_layout.setSpacing(self._title_content_spacing)

            # 重置标题宽度限制
            self.title_label.setMinimumWidth(0)
            self.title_label.setMaximumWidth(16777215)  # 取消最大宽度限制
            # 重置卡片高度限制
            self.setMinimumHeight(0)  # 移除最小高度限制
            self.setMaximumHeight(16777215)  # 取消最大高度限制

            # 添加标题和内容到布局
            self.container_layout.addWidget(self.title_label)
            self.container_layout.addWidget(self.content_widget)

            # 设置对齐方式
            self.container_layout.setAlignment(Qt.AlignTop)
            self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

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

        # 延迟显示tooltip
        if self._tooltip_enabled:
            self._tooltip_timer.start(500)  # 500ms延迟

        super().enterEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        if not self._is_dark_mode:
            # 亮色主题下恢复阴影
            self._shadow_animation.setEndValue(30)
            self._shadow_animation.start()
        self.update()  # 触发重绘以更新背景色

        # 取消tooltip显示并隐藏
        self._tooltip_timer.stop()
        self._hide_tooltip()

        super().leaveEvent(event)

    def set_content(self, widget):
        """设置卡片内容"""
        if self._content:
            self.content_layout.removeWidget(self._content)
            self._content.deleteLater()
        self._content = widget
        self.content_layout.addWidget(widget)
        # 调整大小以适应新内容
        self.updateGeometry()  # 通知布局系统大小发生变化
        self.adjustSize()

    def set_dark_mode(self, is_dark):
        """设置主题模式"""
        self._is_dark_mode = is_dark
        self._update_style()
        self.update()  # 触发重绘以更新背景色

    def _update_style(self):
        """更新样式"""
        # 根据主题更新标题颜色
        color = "#ecf0f1" if self._is_dark_mode else "#2c3e50"
        self.set_title_font(color=color)  # 只更新颜色，保持其他字体设置不变

    def _create_ensure_tooltip(self):
        """创建ensure_tooltip方法"""
        def _ensure_tooltip():
            """确保tooltip已创建"""
            if not self._tooltip and self._tooltip_enabled:
                self._tooltip = ToolTip(self)
                if hasattr(self, 'theme_manager') and self.theme_manager is not None:
                    self._tooltip.theme_manager = self.theme_manager
                self._tooltip.setText(self._tooltip_text)
        return _ensure_tooltip

    def _create_show_tooltip(self):
        """创建show_tooltip方法"""
        def _show_tooltip():
            """显示工具提示"""
            if self._tooltip_enabled and self.underMouse():
                self._ensure_tooltip()
                self._tooltip.show()
        return _show_tooltip

    def _create_hide_tooltip(self):
        """创建hide_tooltip方法"""
        def _hide_tooltip():
            """隐藏工具提示"""
            if self._tooltip:
                self._tooltip.hide()
        return _hide_tooltip

    def setTooltip(self, text: str):
        """设置工具提示文本"""
        self._tooltip_text = text
        self._tooltip_enabled = bool(text)

        # 如果已经创建了tooltip，更新文本
        if self._tooltip:
            self._tooltip.setText(text)

    def paintEvent(self, event):
        """绘制卡片背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRect(0, 0, self.width(), self.height()), 6, 6)

        # 设置背景颜色
        if self._is_dark_mode:
            # 暗色主题：鼠标悬停时背景变亮
            is_hovered = self.underMouse()
            base_color = 40 if is_hovered else 38
            painter.fillPath(path, QColor(base_color, base_color, base_color, 170))
        else:
            # 亮色主题：保持不变
            painter.fillPath(path, QColor(255, 255, 255, 230))

    def sizeHint(self):
        """返回建议的组件大小"""
        if self._is_horizontal:
            return QSize(200, 60)  # 水平布局使用固定大小
        else:
            # 获取内容区域所需的大小
            content_size = self.content_widget.sizeHint()

            # 计算标题所需的高度
            title_height = self.title_label.sizeHint().height()

            # 计算总大小（考虑边距）
            total_width = max(200, content_size.width() + 32)  # 左右各16px边距
            total_height = title_height + self._title_content_spacing + content_size.height() + 24  # 考虑间距和边距

            return QSize(total_width, total_height)

    def resizeEvent(self, event):
        """处理大小调整事件"""
        super().resizeEvent(event)
        # 确保重绘阴影
        self.update()

    def set_title_content_spacing(self, spacing):
        """设置标题和内容之间的间距
        Args:
            spacing: 间距大小（像素）
        """
        self._title_content_spacing = spacing
        if hasattr(self, 'container_layout') and not self._is_horizontal:
            self.container_layout.setSpacing(spacing)
        self.adjustSize()  # 调整卡片大小以适应新的间距

    def set_content_direction(self, horizontal: bool):
        """设置内容布局方向
        Args:
            horizontal: True为水平布局，False为垂直布局
        """
        if self._is_horizontal != horizontal:
            self._is_horizontal = horizontal
            self._setup_container_layout()
            self.adjustSize()  # 调整卡片大小以适应新的布局

    def set_content_container_width(self, width: int):
        """设置内容容器的宽度（仅在水平布局模式下生效）
        Args:
            width: 容器宽度（像素）
        """
        if self._is_horizontal and hasattr(self, 'container_layout'):
            # 找到内容容器并设置宽度
            for i in range(self.container_layout.count()):
                item = self.container_layout.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # 检查是否是内容容器（最后一个widget）
                    if i == self.container_layout.count() - 1:
                        widget.setFixedWidth(width)
                        self.adjustSize()  # 调整卡片大小
                        break

    def set_title_font(self, size=None, weight=None, family=None, color=None):
        """设置标题字体相关参数
        Args:
            size: 字体大小（像素）
            weight: 字体粗细（例如：QFont.Normal, QFont.Bold）
            family: 字体族（例如："Segoe UI"）
            color: 字体颜色（例如："#2c3e50"）
        """
        # 构建样式表
        style_parts = []
        style_parts.append("QLabel {")

        # 设置字体大小
        if size is not None:
            style_parts.append(f"    font-size: {size}px;")
        else:
            style_parts.append("    font-size: 15px;")  # 默认大小

        # 设置字体族
        if family is not None:
            style_parts.append(f'    font-family: "{family}";')
        else:
            style_parts.append('    font-family: "Segoe UI";')  # 默认字体

        # 设置字体粗细
        if weight is not None:
            style_parts.append(f"    font-weight: {weight};")

        # 设置字体颜色
        if color is not None:
            style_parts.append(f"    color: {color};")
        else:
            # 使用主题相关的默认颜色
            color = "#ecf0f1" if self._is_dark_mode else "#2c3e50"
            style_parts.append(f"    color: {color};")

        style_parts.append("}")

        # 应用样式表
        self.title_label.setStyleSheet("\n".join(style_parts))