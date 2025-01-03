from PySide6.QtWidgets import QLineEdit, QWidget, QApplication, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QSize, QRectF, Property, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen, QIcon, QCursor, QIntValidator, QDoubleValidator

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
        
    def paintEvent(self, event):
        """默认绘制方法，提供圆角背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)
        
        # 设置裁剪区域
        painter.setClipPath(path)
        
        # 绘制背景
        painter.fillPath(path, self._background_color)
        
        # 绘制子控件
        painter.setClipping(False)
        super().paintEvent(event)


class ModernSimpleLineEdit(QLineEdit):
    """基础输入框组件"""
    
    onFocus = Signal(bool)
    
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
        self.setFrame(False)  # 关闭默认框架
        
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
            QLineEdit {{
                background-color: transparent;
                color: {self._text_color.name()};
                border: none;
                padding: 0 6px;
                selection-background-color: {self._selection_color.name(QColor.HexArgb)};
            }}
        """)
        self.update()
        
    def _on_theme_changed(self, is_dark: bool):
        """主题改变时更新样式"""
        self._is_dark_mode = is_dark
        self._update_colors()
        
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.onFocus.emit(True)
        self.update()
        
    def focusOutEvent(self, event):
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


class ModernLineEdit(ModernWidget):
    """现代化输入框组件"""
    
    textChanged = Signal(str)
    editingFinished = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 36)
        
        # 创建输入框
        self._line_edit = ModernSimpleLineEdit(self)
        self._line_edit._corner_radius = self._corner_radius
        self._line_edit.textChanged.connect(self._on_text_changed)
        self._line_edit.onFocus.connect(self._on_focus_changed)
        self._line_edit.editingFinished.connect(self.editingFinished)
        self._line_edit.setTextMargins(5, 0, 0, 0)
        
        # 安装事件过滤器
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
            
        # 初始化颜色 - 移到组件创建之后
        self._init_colors()
        
    def _update_colors(self):
        super()._update_colors()
        self._line_edit._update_colors()
        
    def _on_theme_changed(self, is_dark: bool):
        super()._on_theme_changed(is_dark)
        self._line_edit._is_dark_mode = is_dark
        
    def _on_text_changed(self, text: str):
        self.textChanged.emit(text)
        
    def _on_focus_changed(self, has_focus: bool):
        self.update()
        
    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                self._line_edit.clearFocus()
        return super().eventFilter(watched, event)
        
    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._line_edit.clearFocus()
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._line_edit.resize(self.width(), self.height())
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)
        
        # 设置裁剪区域
        painter.setClipPath(path)
        
        # 绘制背景（背景色由ModernSimpleLineEdit处理）
        painter.fillPath(path, Qt.transparent)
        
        # 绘制子控件
        painter.setClipping(False)
        super().paintEvent(event)
        
    def text(self):
        return self._line_edit.text()
        
    def setText(self, text: str):
        self._line_edit.setText(text)
        
    def setPlaceholderText(self, text: str):
        self._line_edit.setPlaceholderText(text)
        
    def setTextMargins(self, left: int, top: int, right: int, bottom: int):
        """设置文本边距"""
        self._line_edit.setTextMargins(left, top, right, bottom)
        
    def setValidator(self, validator):
        """设置验证器"""
        self._line_edit.setValidator(validator)
        
    def validator(self):
        """获取验证器"""
        return self._line_edit.validator()
        
    def clear(self):
        """清空文本"""
        self._line_edit.clear()
        
    def setAlignment(self, alignment):
        """设置对齐方式"""
        self._line_edit.setAlignment(alignment)
        
    def alignment(self):
        """获取对齐方式"""
        return self._line_edit.alignment()
        
    def setReadOnly(self, readonly: bool):
        """设置只读状态"""
        self._line_edit.setReadOnly(readonly)
        
    def isReadOnly(self):
        """获取只读状态"""
        return self._line_edit.isReadOnly()
        
    def setMaxLength(self, length: int):
        """设置最大长度"""
        self._line_edit.setMaxLength(length)
        
    def maxLength(self):
        """获取最大长度"""
        return self._line_edit.maxLength()
        
    def hasAcceptableInput(self):
        """检查输入是否有效"""
        return self._line_edit.hasAcceptableInput()


class ModernLineEditWithClear(ModernWidget):
    """带清除按钮的现代化输入框组件"""
    
    textChanged = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 36)
        
        # 创建输入框
        self._line_edit = ModernLineEdit(self)
        self._line_edit._corner_radius = self._corner_radius
        self._line_edit.textChanged.connect(self._on_text_changed)
        
        # 创建清除按钮
        self._clear_button = ModernClearButton(self)
        self._clear_button.clicked.connect(self.clear)
        
        # 更新布局
        self._update_layout()
        self.setFocusProxy(self._line_edit)
            
    def _update_colors(self):
        super()._update_colors()
        self._line_edit._update_colors()
        
    def _on_theme_changed(self, is_dark: bool):
        super()._on_theme_changed(is_dark)
        self._line_edit._is_dark_mode = is_dark
        
    def _update_layout(self):
        self._line_edit.setGeometry(0, 0, self.width(), self.height())
        button_size = min(self.height() - 8, 22)  # 调整按钮大小
        self._clear_button.resize(button_size + 16, button_size + 8)  # 扩大按钮区域以容纳悬停效果
        self._clear_button.move(
            self.width() - self._clear_button.width() - 4,  # 调整位置以确保悬停效果可见
            (self.height() - self._clear_button.height()) // 2
        )
        self._line_edit.setTextMargins(5, 0, self._clear_button.width() + 8, 0)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_layout()
        
    def _on_text_changed(self, text: str):
        self._clear_button.setVisible(bool(text))
        self.textChanged.emit(text)
        
    def clear(self):
        self._line_edit.clear()
        
    def text(self):
        return self._line_edit.text()
        
    def setText(self, text: str):
        self._line_edit.setText(text)
        
    def setPlaceholderText(self, text: str):
        self._line_edit.setPlaceholderText(text)


class ModernSpinButton(ModernWidget):
    """现代化数字输入框按钮"""
    
    clicked = Signal()
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self._is_up = text == "∧"  # 判断是否为上按钮
        self._is_hovered = False
        self._is_pressed = False
        # 使用相对路径
        self._icon = QIcon("./UI/images/up_arrow.svg" if self._is_up else "./UI/images/down_arrow.svg")
        self.setCursor(Qt.PointingHandCursor)
        
    def _update_colors(self):
        super()._update_colors()
        if self._is_dark_mode:
            self._hover_color = QColor(255, 255, 255, 20)
            self._press_color = QColor(255, 255, 255, 30)
        else:
            self._hover_color = QColor(0, 0, 0, 10)
            self._press_color = QColor(0, 0, 0, 20)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算图标区域 - 保持在中心
        icon_size = min(self.width(), self.height()) - 9 # 固定边距
        icon_rect = QRectF(
            (self.width() - icon_size) / 2, 
            (self.height() - icon_size) / 2,
            icon_size,
            icon_size
        )
        
        # 绘制背景 - 确保在可视范围内
        hover_rect = QRectF(
            1,  # 左边距
            0,  # 上边距
            self.width()-1,  # 右边距
            self.height()-1 # 下边距
        )
        
        if self._is_pressed:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._press_color)
            painter.drawRoundedRect(hover_rect, 4, 4)
        elif self._is_hovered:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._hover_color)
            painter.drawRoundedRect(hover_rect, 4, 4)
        
        # 绘制图标
        if self._icon and not self._icon.isNull():
            self._icon.paint(painter, icon_rect.toRect(), Qt.AlignCenter, QIcon.Normal, QIcon.Off)
        
    def enterEvent(self, event):
        super().enterEvent(event)
        self._is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._is_hovered = False
        self._is_pressed = False
        self.update()
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            self.update()
            
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and self._is_pressed:
            self._is_pressed = False
            self.clicked.emit()
        self.update()


class ModernSpinBox(ModernWidget):
    """现代化数字输入框基类"""
    
    valueChanged = Signal(float)  # 使用float以兼容整数和浮点数
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 36)
        self._value = 0
        self._minimum = 0
        self._maximum = 99
        self._step = 1
        
        # 创建输入框
        self._line_edit = ModernLineEdit(self)
        self._line_edit._corner_radius = self._corner_radius
        self._line_edit.editingFinished.connect(self._on_editing_finished)
        
        # 创建增减按钮，使用新的符号
        self._up_button = ModernSpinButton("∧", self)
        self._down_button = ModernSpinButton("∨", self)
        self._up_button.clicked.connect(self.stepUp)
        self._down_button.clicked.connect(self.stepDown)
        
        # 更新布局
        self._update_layout()
        
        # 初始化颜色
        self._init_colors()
            
    def _update_colors(self):
        super()._update_colors()
        self._line_edit._update_colors()
        self._up_button._update_colors()
        self._down_button._update_colors()
        
    def _on_theme_changed(self, is_dark: bool):
        super()._on_theme_changed(is_dark)
        self._line_edit._is_dark_mode = is_dark
        self._up_button._is_dark_mode = is_dark
        self._down_button._is_dark_mode = is_dark
            
    def _update_layout(self):
        """更新布局"""
        button_size = min(self.height() - 8, 20)  # 增加按钮基础大小
        
        # 设置按钮位置和大小，考虑悬停效果的溢出
        self._up_button.resize(button_size + 4, button_size + 4)  # 增加按钮尺寸以容纳悬停效果
        self._down_button.resize(button_size + 4, button_size + 4)
        
        # 水平布局按钮，靠右对齐并紧密排列
        self._up_button.move(
            self.width() - (button_size + 2) - 8,  # 右边的按钮
            (self.height() - button_size) // 2
        )
        self._down_button.move(
            self.width() - 2 * (button_size + 3)  - 4,  # 左边的按钮，减小间距
            (self.height() - button_size) // 2
        )
        
        # 设置输入框位置和大小
        self._line_edit.setGeometry(0, 0, self.width(), self.height())
        self._line_edit.setTextMargins(5, 0, 2 * button_size + 12, 0)  # 调整右边距
        
    def resizeEvent(self, event):
        """大小改变时更新布局"""
        super().resizeEvent(event)
        self._update_layout()
        
    def _on_editing_finished(self):
        try:
            value = float(self._line_edit.text())
            self.setValue(value)
        except ValueError:
            self._line_edit.setText(str(self._value))
            
    def stepUp(self):
        self.setValue(self._value + self._step)
        
    def stepDown(self):
        self.setValue(self._value - self._step)
        
    def setValue(self, value):
        value = min(max(value, self._minimum), self._maximum)
        if value != self._value:
            self._value = value
            self._line_edit.setText(str(value))
            self.valueChanged.emit(value)
            
    def value(self):
        return self._value
        
    def setRange(self, minimum, maximum):
        self._minimum = minimum
        self._maximum = maximum
        self.setValue(self._value)  # 确保当前值在范围内
        
    def setSingleStep(self, step):
        self._step = step


class ModernIntSpinBox(ModernSpinBox):
    """现代化整数输入框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_edit.setValidator(QIntValidator())
        self._step = 1
        self.setValue(0)
        
    def setValue(self, value):
        super().setValue(int(value))
        
    def value(self):
        return int(super().value())


class ModernDoubleSpinBox(ModernSpinBox):
    """现代化浮点数输入框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_edit.setValidator(QDoubleValidator())
        self._step = 0.1
        self.setValue(0.0)
        
    def setValue(self, value):
        # 处理浮点数精度问题
        value = round(value, 10)
        super().setValue(value)


class ModernClearButton(ModernWidget):
    """现代化清除按钮组件"""
    
    clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_hovered = False
        self._is_pressed = False
        self._icon = QIcon("UI/images/clear.svg")
        self._hover_color = QColor(0, 0, 0, 10)  # 初始化颜色
        self._press_color = QColor(0, 0, 0, 20)  # 初始化颜色
        self._icon_alpha = 120  # 初始化透明度
        self.setCursor(Qt.PointingHandCursor)
        self.hide()
        
    def _update_colors(self):
        super()._update_colors()
        if self._is_dark_mode:
            self._hover_color = QColor(255, 255, 255, 20)
            self._press_color = QColor(255, 255, 255, 30)
            self._icon_alpha = 180 if self._is_pressed else 160 if self._is_hovered else 140
        else:
            self._hover_color = QColor(0, 0, 0, 10)
            self._press_color = QColor(0, 0, 0, 20)
            self._icon_alpha = 160 if self._is_pressed else 140 if self._is_hovered else 120
            
    def enterEvent(self, event):
        super().enterEvent(event)
        self._is_hovered = True
        self.update()
        
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._is_hovered = False
        self._is_pressed = False
        self.update()
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._is_pressed = True
            self.update()
            
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and self._is_pressed:
            self._is_pressed = False
            self.clicked.emit()
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算图标区域 - 保持在中心
        icon_size = min(self.width() - 16, self.height() - 8) - 2  # 考虑悬停区域的边距
        icon_rect = QRectF(
            (self.width() - icon_size) / 2 + 4, 
            (self.height() - icon_size) / 2,
            icon_size,
            icon_size
        )
        
        # 绘制背景 - 确保在可视范围内
        hover_rect = QRectF(
            8,  # 左边距
            2,  # 上边距
            self.width() - 8,  # 右边距
            self.height() - 4   # 下边距
        )
        
        if self._is_pressed:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._press_color)
            painter.drawRoundedRect(hover_rect, 4, 4)
        elif self._is_hovered:
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._hover_color)
            painter.drawRoundedRect(hover_rect, 4, 4)
        
        # 绘制图标
        if self._icon:
            self._icon.paint(painter, icon_rect.toRect(), Qt.AlignCenter, QIcon.Normal, QIcon.Off) 