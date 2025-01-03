from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QPushButton, QHBoxLayout, QApplication, QDialog, QSizePolicy, QGraphicsOpacityEffect
from PySide6.QtCore import Qt,  QEvent, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
from PySide6.QtGui import QPainter, QColor, QPixmap
from PySide6.QtSvg import QSvgRenderer
import os

class ModernDialog(QDialog):
    """现代化模态对话框组件"""
    
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
        self.body_padding_h = 43
        self.theme_padding_h = 26
        self.content_padding_v = 32
        self.button_padding_v = 24
        self.theme_label_top_height = 2
        self.theme_label_bottom_height = 0
        
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
        self.background_anim.setDuration(200)
        self.background_anim.setStartValue(0.0)
        self.background_anim.setEndValue(1.0)
        self.background_anim.setEasingCurve(QEasingCurve.InOutCubic)
        
        # 对话框淡入动画
        self.dialog_anim = QPropertyAnimation(self.dialog_container, b"windowOpacity")
        self.dialog_anim.setDuration(200)
        self.dialog_anim.setStartValue(0.0)
        self.dialog_anim.setEndValue(1.0)
        self.dialog_anim.setEasingCurve(QEasingCurve.InOutCubic)
        
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
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.dialog_container.setGraphicsEffect(shadow)
        
        # 对话框内部布局
        self.dialog_layout = QVBoxLayout(self.dialog_container)
        self.dialog_layout.setContentsMargins(0, 0, 0, 0)
        self.dialog_layout.setSpacing(0)
        
        # 主题指示条
        self.theme_label = QLabel()
        self.theme_label.setObjectName("theme_label")
        self.theme_label.setFixedHeight(4)
        self.theme_label.setFixedWidth(int(self._dialog_width * 0.8))
        # 创建一个容器来居中放置指示条
        theme_container = QWidget()
        theme_container.setObjectName("theme_container")
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setContentsMargins(0, 0, 0, 0)  # 只保留顶部间距
        theme_layout.setSpacing(0)
        theme_layout.addStretch()
        theme_layout.addWidget(self.theme_label)
        theme_layout.addStretch()
        self.dialog_layout.addWidget(theme_container)
        
        # 内容区域
        self.body_content_label = QLabel()
        self.body_content_label.setObjectName("body_content_label")
        self.dialog_layout.addWidget(self.body_content_label)
        
        # 按钮区域
        self.body_button_label = QLabel()
        self.body_button_label.setObjectName("body_button_label")
        self.dialog_layout.addWidget(self.body_button_label)
        
        # 内容容器
        self.content_container = QWidget(self.body_content_label)
        self.content_container.setObjectName("content_container")
        content_container_layout = QVBoxLayout(self.content_container)
        content_container_layout.setContentsMargins(0, 0, 0, 0)
        content_container_layout.setSpacing(0)
        self.content_container.setMinimumHeight(200)  # 设置内容区域最小高度
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout(self.content_widget)  # 水平布局
        self.content_layout.setContentsMargins(self.body_padding_h, self.content_padding_v, 
                                             self.body_padding_h, self.content_padding_v)
        self.content_layout.setSpacing(20)
        
        # 内容左侧（图标）
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.icon_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # 内容右侧（文本区域）
        self.text_container = QWidget()
        self.text_layout = QVBoxLayout(self.text_container)
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.text_layout.setSpacing(4)  # 将间距从8减小到4
        
        # 标题
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("title_label")
        self.text_layout.addWidget(self.title_label)
        
        # 添加到内容布局
        self.content_layout.addWidget(self.icon_label)
        self.content_layout.addWidget(self.text_container, 1)  # 1表示可伸展
        
        # 将内容添加到内容容器
        content_container_layout.addWidget(self.content_widget)
        
        # 按钮容器
        self.button_container = QWidget(self.body_button_label)
        button_container_layout = QVBoxLayout(self.button_container)
        button_container_layout.setContentsMargins(0, 0, 0, 0)
        button_container_layout.setSpacing(0)
        
        # 按钮区域
        self.button_widget = QWidget()
        self.button_layout = QHBoxLayout(self.button_widget)
        self.button_layout.setContentsMargins(self.body_padding_h, self.button_padding_v,
                                            self.body_padding_h, self.button_padding_v)
        self.button_layout.setSpacing(8)
        
        # 将按钮区域添加到按钮容器
        button_container_layout.addWidget(self.button_widget)
        
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
        
        # 背景色
        bg_color = "#1e1e1e" if self._is_dark_mode else "#ffffff"
        bg_color_darker = "#333333" if self._is_dark_mode else "#f5f5f5"
        
        # 边框色
        border_color = "rgba(255, 255, 255, 0.15)" if self._is_dark_mode else "rgba(0, 0, 0, 0.08)"
        
        # 文字色
        text_color = "#ffffff" if self._is_dark_mode else "#292C30"
        text_color_secondary = "#cccccc" if self._is_dark_mode else "#666666"
        
        # 按钮颜色
        button_bg = "#2c2c2c" if self._is_dark_mode else "#f0f0f0"
        button_hover = "#353535" if self._is_dark_mode else "#e5e5e5"
        button_pressed = "#404040" if self._is_dark_mode else "#d0d0d0"
        
        self.setStyleSheet(f"""
            QDialog {{
                background: transparent;
            }}
            QWidget#background_widget {{
                background-color: rgba(0, 0, 0, {0.6 * self.background_widget.property("opacity")});
            }}
            QWidget#dialog_container {{
                background: {bg_color};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
            QWidget#theme_container {{
                background: transparent;
            }}
            QWidget#theme_label {{
                background: {theme_color_str};
                border-radius: 2px;
                margin: 0px;
            }}
            QWidget#body_content_label {{
                background: transparent;
            }}
            QWidget#content_container {{
                background: transparent;
            }}
            QWidget#body_button_label {{
                background: {bg_color_darker};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
                border-top: 1px solid {border_color};
            }}
            QLabel {{
                color: {text_color};
                font-size: 14px;
            }}
            QLabel#title_label {{
                color: {text_color};
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {button_bg};
                color: {text_color};
                border: none;
                border-radius: 4px;
                padding: 0 16px;
                height: 32px;
                font-size: 14px;
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
        
    def _adjust_color(self, color, amount):
        """调整颜色亮度"""
        if color.startswith('#'):
            color = color[1:]
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
    def adjustSize(self):
        """调整对话框大小"""
        # 调整内容容器大小
        self.text_container.adjustSize()
        self.content_widget.adjustSize()
        self.content_container.adjustSize()
        self.button_widget.adjustSize()
        self.button_container.adjustSize()
        
        # 获取内容和按钮的实际高度
        content_height = max(self.content_container.sizeHint().height(), 200)  # 确保内容区域最小高度
        button_height = self.button_container.sizeHint().height()
        
        # 设置内容和按钮区域的大小
        self.body_content_label.setFixedHeight(content_height)
        self.body_button_label.setFixedHeight(button_height)
        
        # 计算总高度
        total_height = (
            self.theme_label.height() +  # 主题指示条高度
            content_height +             # 内容区域高度
            button_height               # 按钮区域高度
        )
        
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
        
        # 显示对话框
        self.show()
        
        # 开始动画
        self.anim_group.start()
        
        self.exec()
        
    @classmethod
    def show_dialog(cls, parent, title, message, buttons=[OK], icon_name=None):
        """显示对话框"""
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
            }
        """)
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
        
        # 计算每个按钮的宽度
        button_count = len([b for b in buttons if b in button_map])
        if button_count > 0:
            button_width = (dialog._dialog_width - 2 * dialog.body_padding_h - (button_count - 1) * 8) // button_count
            
        # 添加按钮
        for button_type in buttons:
            if button_type in button_map:
                text, is_primary = button_map[button_type]
                button = QPushButton(text)
                button.setProperty("primary", is_primary)
                button.setFixedWidth(button_width)  # 设置固定宽度
                button.clicked.connect(lambda checked, b=button_type: dialog._handle_button_click(b))
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
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图标路径
        icon_path = os.path.join(current_dir, '..', 'icons', 'fluent', f'{icon_name}.svg')
        
        if os.path.exists(icon_path):
            # 读取SVG文件内容
            with open(icon_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # 替换颜色
            color = "#ffffff" if self._is_dark_mode else "#292C30"
            svg_content = svg_content.replace('currentColor', color)
            
            # 创建临时文件来存储修改后的SVG
            temp_path = os.path.join(current_dir, '..', 'icons', 'fluent', 'temp.svg')
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            # 渲染SVG
            renderer = QSvgRenderer(temp_path)
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            renderer.render(painter)
            painter.end()
            
            # 删除临时文件
            os.remove(temp_path)
            
            # 设置图标
            self.icon_label.setPixmap(pixmap)
            
            # 设置图标透明度
            opacity_effect = QGraphicsOpacityEffect(self.icon_label)
            opacity_effect.setOpacity(0.6)  # 设置60%不透明度
            self.icon_label.setGraphicsEffect(opacity_effect)
        else:
            print(f"图标文件不存在: {icon_path}")
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
        