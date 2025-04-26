from PySide6.QtWidgets import QTextEdit, QWidget, QApplication
from PySide6.QtCore import Qt, Signal, QRectF, QEvent
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen, QCursor
from UI.resources import resources_rc

class ModernSimpleTextEdit(QTextEdit):
    """基础文本编辑框组件"""

    onFocus = Signal(bool)
    textChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_dark_mode = False
        self._text_color = QColor("#2D2932")
        self._accent_color = parent.palette().highlight().color() if parent else QColor("#0078d4")
        self._corner_radius = 4

        # 初始化样式
        self.setFont(QFont("Segoe UI", 10))
        self.setCursor(Qt.IBeamCursor)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setFrameShape(QTextEdit.NoFrame)  # 关闭默认框架

        # 连接原生信号到自定义信号
        super().textChanged.connect(self.textChanged)

        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self._is_dark_mode = parent.theme_manager.isDarkMode()
            self._update_colors()

    def _update_colors(self):
        """更新颜色"""
        if hasattr(self, 'theme_manager'):
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])

        if self._is_dark_mode:
            self._text_color = QColor("#DFDFDF")
            self._background_color = QColor(50, 42, 49, 240)
        else:
            self._text_color = QColor("#2D2932")
            self._background_color = QColor(254, 254, 254)

        # 创建一个半透明的选择背景色
        self._selection_color = QColor(self._text_color)
        self._selection_color.setAlpha(40)

        # 设置基本样式
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                color: {self._text_color.name()};
                border: none;
                padding: 6px;
                selection-background-color: {self._selection_color.name(QColor.HexArgb)};
            }}
        """)
        self.update()

    def _on_theme_changed(self, is_dark: bool):
        """主题改变时更新样式"""
        self._is_dark_mode = is_dark
        self._update_colors()

    def focusInEvent(self, event):
        """获取焦点事件"""
        super().focusInEvent(event)
        self.onFocus.emit(True)
        self.update()

    def focusOutEvent(self, event):
        """失去焦点事件"""
        super().focusOutEvent(event)
        self.onFocus.emit(False)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)

        # 设置裁剪区域
        painter.setClipPath(path)

        # 绘制背景
        painter.fillPath(path, self._background_color)

        # 绘制底部边框
        line_margin = 2  # 线条两端的间距
        line_y = self.height() - 1  # 统一线条位置

        # 根据焦点状态设置颜色和粗细
        if self.hasFocus():
            pen = QPen(self._accent_color)  # 使用主题色
            pen.setWidth(2)  # 聚焦时线条加粗
        else:
            pen = QPen(self._accent_color)
            pen.setWidth(1)  # 非聚焦时使用标准粗细

        painter.setPen(pen)
        painter.drawLine(line_margin, line_y, self.width() - line_margin, line_y)

        # 绘制文本
        painter.setClipping(False)
        super().paintEvent(event)


class ModernWidget(QWidget):
    """现代化组件基类，提供统一的样式和主题支持"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._corner_radius = 6  # 圆角半径
        self._is_dark_mode = False

        # 初始化颜色
        self._accent_color = parent.palette().highlight().color() if parent else QColor("#0078d4")
        self._background_color = QColor(254, 254, 254)

        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
            self.theme_manager.themeChanged.connect(self._on_theme_changed)
            self._is_dark_mode = parent.theme_manager.isDarkMode()

    def _init_colors(self):
        """初始化颜色 - 在子类完成自己的初始化后调用"""
        self._update_colors()

    def _update_colors(self):
        """更新颜色"""
        if hasattr(self, 'theme_manager'):
            accent = self.theme_manager.accent_color
            self._accent_color = QColor(accent['red'], accent['green'], accent['blue'])

        if self._is_dark_mode:
            self._background_color = QColor(50, 42, 49, 240)
            self._text_color = QColor("#DFDFDF")
        else:
            self._background_color = QColor(254, 254, 254)
            self._text_color = QColor("#2D2932")

        self.update()

    def _on_theme_changed(self, is_dark: bool):
        """主题改变时更新样式"""
        self._is_dark_mode = is_dark
        self._update_colors()


class ModernTextEdit(ModernWidget):
    """现代化文本编辑框组件"""

    textChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 80)  # 文本编辑框默认高度更大

        # 创建文本编辑框
        self._text_edit = ModernSimpleTextEdit(self)
        self._text_edit._corner_radius = self._corner_radius
        self._text_edit.textChanged.connect(self._on_text_changed)
        self._text_edit.onFocus.connect(self._on_focus_changed)

        # 安装事件过滤器
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

        # 初始化颜色 - 移到组件创建之后
        self._init_colors()

    def _update_colors(self):
        super()._update_colors()
        if hasattr(self, '_text_edit'):
            self._text_edit._update_colors()

    def _on_theme_changed(self, is_dark: bool):
        super()._on_theme_changed(is_dark)
        if hasattr(self, '_text_edit'):
            self._text_edit._is_dark_mode = is_dark

    def _on_text_changed(self):
        self.textChanged.emit()

    def _on_focus_changed(self, has_focus: bool):
        # has_focus参数用于标记是否获得焦点
        self.update()

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                if hasattr(self, '_text_edit'):
                    self._text_edit.clearFocus()
        return super().eventFilter(watched, event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if hasattr(self, '_text_edit'):
            self._text_edit.clearFocus()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_text_edit'):
            self._text_edit.resize(self.width(), self.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)

        # 设置裁剪区域
        painter.setClipPath(path)

        # 绘制背景（背景色由ModernSimpleTextEdit处理）
        painter.fillPath(path, Qt.transparent)

        # 绘制子控件
        painter.setClipping(False)
        super().paintEvent(event)

    def toPlainText(self):
        if hasattr(self, '_text_edit'):
            return self._text_edit.toPlainText()
        return ""

    def setPlainText(self, text: str):
        if hasattr(self, '_text_edit'):
            self._text_edit.setPlainText(text)

    def setText(self, text: str):
        """设置文本内容，兼容LineEdit的API"""
        if hasattr(self, '_text_edit'):
            self._text_edit.setPlainText(text)

    def toHtml(self):
        if hasattr(self, '_text_edit'):
            return self._text_edit.toHtml()
        return ""

    def setHtml(self, html: str):
        if hasattr(self, '_text_edit'):
            self._text_edit.setHtml(html)

    def setPlaceholderText(self, text: str):
        if hasattr(self, '_text_edit'):
            self._text_edit.setPlaceholderText(text)

    def setReadOnly(self, read_only: bool):
        if hasattr(self, '_text_edit'):
            self._text_edit.setReadOnly(read_only)

    def isReadOnly(self):
        if hasattr(self, '_text_edit'):
            return self._text_edit.isReadOnly()
        return False

    def clear(self):
        if hasattr(self, '_text_edit'):
            self._text_edit.clear()

    def document(self):
        if hasattr(self, '_text_edit'):
            return self._text_edit.document()
        return None

    def setDocument(self, document):
        if hasattr(self, '_text_edit'):
            self._text_edit.setDocument(document)

    def appendPlainText(self, text: str):
        if hasattr(self, '_text_edit'):
            self._text_edit.appendPlainText(text)

    def appendHtml(self, html: str):
        if hasattr(self, '_text_edit'):
            self._text_edit.appendHtml(html)

    def setTextInteractionFlags(self, flags):
        if hasattr(self, '_text_edit'):
            self._text_edit.setTextInteractionFlags(flags)

    def textInteractionFlags(self):
        if hasattr(self, '_text_edit'):
            return self._text_edit.textInteractionFlags()
        return Qt.NoTextInteraction
