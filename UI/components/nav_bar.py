from PySide6.QtCore import Qt, Property, QRectF, QSize, Signal, QPropertyAnimation, QEasingCurve, QFile
from PySide6.QtGui import (
    QPainter, QColor, QPaintEvent, 
    QMouseEvent, QEnterEvent, QIcon, QPixmap
)
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QWidget, QVBoxLayout
from PySide6.QtSvg import QSvgRenderer
from pathlib import Path
import UI.resources.resources_rc
import logging

logger = logging.getLogger(__name__)


class NavButton(QPushButton):
    """导航按钮"""
    
    clicked = Signal(str)  # 发送页面标识信号
    
    def __init__(self, icon_name: str, text: str, page_id: str, parent=None):
        super().__init__(text, parent)
        self._page_id = page_id
        self._is_selected = False
        self._icon_name = icon_name
        
        # 状态管理
        self._hover_state = False
        self._press_state = False
        
        # 获取theme_manager
        self._theme_manager = getattr(parent, 'theme_manager', None)
        if not self._theme_manager and parent:
            # 尝试从父级链获取
            parent_widget = parent.parent()
            while parent_widget:
                if hasattr(parent_widget, 'theme_manager'):
                    self._theme_manager = parent_widget.theme_manager
                    break
                parent_widget = parent_widget.parent()
        
        # 创建布局
        self._setup_layout(text)
        
        # 设置属性
        self.setAttribute(Qt.WA_Hover)
        self.setFlat(True)
        
        # 初始化样式
        self._init_style()
        
        # 连接信号
        self.clicked.connect(self._on_button_clicked)
        
        # 如果找到了theme_manager，连接信号并立即更新颜色
        if self._theme_manager:
            self._theme_manager.themeChanged.connect(self._update_colors)
            if hasattr(self._theme_manager, 'accentColorChanged'):
                self._theme_manager.accentColorChanged.connect(self._update_colors)
                self._theme_manager.accentColorChanged.connect(self.update_icon)  # 添加图标更新
            self._update_colors()
        else:
            logger.warning("NavButton: 未找到ThemeManager，使用默认样式")
        
        # 添加指示条动画属性
        self._indicator_height = 0.0  # 指示条高度的动画属性
        self._indicator_animation = QPropertyAnimation(self, b"indicator_height", self)
        self._indicator_animation.setDuration(350)  # 动画持续时间
        self._indicator_animation.setEasingCurve(QEasingCurve.OutCubic)  # 弹性曲线
    
    def _setup_layout(self, text: str):
        """设置按钮布局"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(15)
        
        # 创建图标
        self._icon_label = QLabel()
        self._icon_label.setMinimumSize(16, 16)
        self.update_icon()
        layout.addWidget(self._icon_label)
        
        # 创建文本标签
        self._text_label = QLabel(text)
        layout.addWidget(self._text_label)
        
        layout.addStretch()
    
    def _find_theme_manager(self):
        """查找主题管理器"""
        parent_widget = self.parent()
        while parent_widget:
            if hasattr(parent_widget, 'theme_manager'):
                return parent_widget.theme_manager
            parent_widget = parent_widget.parent()
        return None
    
    def _init_style(self):
        """初始化样式"""
        self.setStyleSheet("""
            NavButton {
                border: none;
                border-radius: 7px;
                background-color: transparent;
            }
            QLabel {
                background: transparent;
            }
        """)
    
    def _on_button_clicked(self):
        """处理按钮点击"""
        # 重置状态
        self._hover_state = False
        self._press_state = False
        
        # 通知父级处理选中状态
        if hasattr(self.parent(), 'setCurrentPage'):
            self.parent().setCurrentPage(self._page_id)
    
    def _update_colors(self):
        """更新按钮颜色"""
        if not self._theme_manager:
            return
            
        try:
            is_dark = self._theme_manager.isDarkMode()
            
            # 根据主题设置颜色
            if is_dark:
                self._bg_color = QColor("transparent")
                self._text_color = QColor("#F8F8F8")
                self._hover_color = QColor(41,41,41,200)
                self._hovered_color = QColor(42,39,47,180)
                self._press_color = QColor(46,43,51,220)
                self._font_weight = "normal"
            else:
                self._bg_color = QColor("transparent")
                self._text_color = QColor("#2D2932")
                self._hover_color = QColor(235,233,240,190)
                self._hovered_color = QColor(237,236,243,190)
                self._press_color = QColor(238,238,239,140)
                self._font_weight = "normal"
            
            # 更新文本颜色
            self._text_label.setStyleSheet(f"""
                QLabel {{
                    color: {self._text_color.name()};
                    font-size: 13px;
                    font-family: "Segoe UI";
                    font-weight: {self._font_weight};
                    background: transparent;
                }}
            """)
            
            # 强制重绘
            self.update()
            
        except Exception as e:
            logger.error(f"更新NavButton颜色失败: {e}")
            self._init_colors()  # 使用默认颜色
    
    def paintEvent(self, event: QPaintEvent):
        """自定义绘制"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 确定背景色
        if self._is_selected:
            if self._press_state:
                bg_color = QColor(self._press_color)
            elif self._hover_state:
                bg_color = QColor(self._hovered_color)
            else:
                # 选中状态固定背景色
                bg_color = QColor("#2E2B33" if self._theme_manager and self._theme_manager.isDarkMode() else QColor(235,233,240,180))
        else:
            # 非选中状态
            bg_color = QColor(self._bg_color)
            
            # 处理悬停和按压状态
            if self._press_state:
                bg_color = QColor(self._press_color)
            elif self._hover_state:
                bg_color = QColor(self._hover_color)
        
        # 绘制背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(self.rect(), 4, 4)
        
        # 绘制指示条
        if self._indicator_height > 0:
            if self._theme_manager:
                accent = self._theme_manager.accent_color
                indicator_color = QColor(accent['red'], accent['green'], accent['blue'])
            else:
                indicator_color = QColor("#6843d1")  # 默认颜色
            
            # 计算指示条的矩形
            total_height = self.height() * 0.50  # 指示条最大高度为按钮高度的%
            current_height = total_height * self._indicator_height
            y_offset = (self.height() - current_height) / 2
            
            indicator_rect = QRectF(
                3,  # x位置
                y_offset,  # y位置
                3,  # 宽度
                current_height  # 当前高度
            )
            
            # 绘制指示条
            painter.setBrush(indicator_color)
            painter.drawRoundedRect(indicator_rect, 1.5, 1.5)
        
        painter.end()
    
    def enterEvent(self, event: QEnterEvent):
        """鼠标进入事件"""
        self._hover_state = True
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hover_state = False
        self._press_state = False
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self._press_state = True
            self.update()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self._press_state = False
            
            # 如果在按钮区域内释放，触发点击
            if self.rect().contains(event.pos()):
                self.clicked.emit(self._page_id)
            
            self.update()
        super().mouseReleaseEvent(event)
    
    def setSelected(self, selected: bool):
        """设置选中状态"""
        if self._is_selected != selected:
            self._is_selected = selected
            self._hover_state = False
            self._press_state = False
            
            # 设置动画
            self._indicator_animation.stop()
            if selected:
                self._indicator_animation.setStartValue(0.0)
                self._indicator_animation.setEndValue(1.0)
            else:
                self._indicator_animation.setStartValue(1.0)
                self._indicator_animation.setEndValue(0.0)
            self._indicator_animation.start()
            
            self.update()
    
    def isSelected(self) -> bool:
        """获取选中状态"""
        return self._is_selected
    
    def update_icon(self):
        """更新图标"""
        if not self._icon_name:
            return
        
        try:
            # 构建资源路径
            icon_path = f":/resources/{self._icon_name}.svg"
            
            # 获取设备像素比
            device_pixel_ratio = self.window().devicePixelRatio() if self.window() else 1.0
            # 计算实际需要的像素大小
            pixel_size = int(20 * device_pixel_ratio)  # 基础大小 * 设备像素比
            
            # 获取颜色 - 根据选中状态使用不同颜色
            if self._theme_manager:
                accent = self._theme_manager.accent_color
                color = f"#{accent['red']:02x}{accent['green']:02x}{accent['blue']:02x}"
            else:
                color = "#000000"
            
            # 从Qt资源系统读取SVG
            file = QFile(icon_path)
            if file.open(QFile.ReadOnly | QFile.Text):
                svg_content = str(file.readAll().data(), encoding='utf-8')
                file.close()
                
                # 替换颜色
                svg_content = svg_content.replace('currentColor', color)
                # 替换原始的 width 和 height
                svg_content = svg_content.replace('width="24"', f'width="{pixel_size}"')
                svg_content = svg_content.replace('height="24"', f'height="{pixel_size}"')
                
                # 创建SVG渲染器
                renderer = QSvgRenderer()
                renderer.load(svg_content.encode('utf-8'))
                
                # 创建更大的pixmap以适应高DPI
                pixmap = QPixmap(pixel_size, pixel_size)
                pixmap.fill(Qt.transparent)
                
                # 使用高质量渲染
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                painter.setRenderHint(QPainter.TextAntialiasing, True)
                renderer.render(painter)
                painter.end()
                
                # 设置设备像素比
                pixmap.setDevicePixelRatio(device_pixel_ratio)
                self._icon_label.setPixmap(pixmap)
                
        except Exception as e:
            logger.error(f"更新图标失败: {str(e)}")
    
    def sizeHint(self):
        """建议大小"""
        return QSize(160, 35)
    
    # 添加属性getter和setter
    def _get_indicator_height(self) -> float:
        return self._indicator_height
    
    def _set_indicator_height(self, height: float):
        self._indicator_height = height
        self.update()  # 触发重绘
    
    # 定义动画属性
    indicator_height = Property(float, _get_indicator_height, _set_indicator_height)


class NavBar(QWidget):
    """导航栏组件"""
    
    pageChanged = Signal(str)  # 页面切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = {}  # 存储按钮
        self._current_page = None
        self._page_indices = {}  # 存储页面索引
        
        # 获取theme_manager
        self.theme_manager = getattr(parent, 'theme_manager', None)
        
        # 创建内容区域
        self._content = QWidget()
        self._content.setAutoFillBackground(False)
        self._content.setMinimumWidth(160)
        self._content.setContentsMargins(5, 10, 10, 0)
        
        # 创建布局
        self._layout = QVBoxLayout(self._content)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(5)
        self._layout.addStretch()
        
        # 设置主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._content)
        
        # 设置样式表确保透明
        self.setStyleSheet("""
            NavBar, QWidget {
                background-color: transparent;
                border: none;
            }
        """)
    
    def addPage(self, icon_name: str, text: str, page_id: str):
        """添加页面
        Args:
            icon_name: 图标名称,例如 'ic_fluent_home_regular'
            text: 按钮文本
            page_id: 页面标识
        """
        if page_id not in self._buttons:
            # 创建按钮
            button = NavButton(icon_name, text, page_id, self)
            button.clicked.connect(self._on_button_clicked)
            self._buttons[page_id] = button
            
            # 记录页面索引
            self._page_indices[page_id] = len(self._buttons) - 1
            
            # 添加到布局
            self._layout.insertWidget(self._layout.count() - 1, button)
            
            # 如果是第一个按钮，设置为当前页面
            if len(self._buttons) == 1:
                self.setCurrentPage(page_id)
    
    def _on_button_clicked(self, page_id: str):
        """按钮点击处理"""
        self.setCurrentPage(page_id)
    
    def setCurrentPage(self, page_id: str):
        """设置当前页面"""
        if page_id != self._current_page and page_id in self._buttons:
            # 取消之前的选中状态
            if self._current_page and self._current_page in self._buttons:
                self._buttons[self._current_page].setSelected(False)
            
            # 设置新的选中状态
            self._current_page = page_id
            self._buttons[page_id].setSelected(True)
            
            # 发送页面切换信号
            self.pageChanged.emit(page_id)
    
    def currentPage(self) -> str:
        """获取当前页面ID"""
        return self._current_page
    
    def get_page_index(self, page_id: str) -> int:
        """获取页面索引"""
        return self._page_indices.get(page_id, -1)
