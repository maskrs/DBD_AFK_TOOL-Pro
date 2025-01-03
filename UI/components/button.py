"""Modern button component with themes"""
from PySide6.QtCore import Qt, Property, QRectF, QSize, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import (
    QPainter, QColor, QPaintEvent, 
    QMouseEvent, QEnterEvent, QIcon, QPixmap
)
from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel, QSizePolicy
from PySide6.QtSvg import QSvgRenderer
from pathlib import Path
import io
import logging

logger = logging.getLogger(__name__)

# class ModernButton(QPushButton):
    # """Modern button with themes and accent color support"""
    
    # def __init__(self, text="", use_accent=False, parent=None, wrap_text=False):
    #     """Initialize button
        
    #     Args:
    #         text: Button text
    #         use_accent: Whether to use accent color for button
    #         parent: Parent widget
    #         wrap_text: Whether to allow text wrapping
    #     """
    #     super().__init__("", parent)
    #     self._use_accent = use_accent
    #     self._wrap_text = wrap_text
    #     self._text = text
        
    #     # 创建布局
    #     self._setup_layout(text)
        
    #     # 获取theme_manager
    #     self._theme_manager = getattr(parent, 'theme_manager', None)
    #     if not self._theme_manager and parent:
    #         parent_widget = parent.parent()
    #         while parent_widget:
    #             if hasattr(parent_widget, 'theme_manager'):
    #                 self._theme_manager = parent_widget.theme_manager
    #                 break
    #             parent_widget = parent_widget.parent()
        
    #     self._init_style()
        
    #     # 如果找到了theme_manager，连接信号并立即更新颜色
    #     if self._theme_manager:
    #         self._theme_manager.themeChanged.connect(self._update_colors)
    #         if hasattr(self._theme_manager, 'accentColorChanged'):
    #             self._theme_manager.accentColorChanged.connect(self._update_colors)
    #         self._update_colors()
    #     else:
    #         logger.warning("未找到ThemeManager，使用默认样式")
            
    # def _init_style(self):
    #     """Initialize button style"""
    #     self.setStyleSheet("""
    #         QPushButton {
    #             background-color: #FFFFFF;
    #             color: #2D2932;
    #             border: none;
    #             padding: 5px 15px;
    #             border-radius: 7px;
    #         }
    #     """)
    
    # def _get_accent_color(self) -> tuple:
    #     """获取强调色，返回(r,g,b,a)元组"""
    #     try:
    #         if hasattr(self._theme_manager, 'accent_color'):
    #             accent_data = self._theme_manager.accent_color
    #         else:
    #             accent_data = self._theme_manager.accentColor()
                
    #         return (
    #             accent_data['red'],
    #             accent_data['green'],
    #             accent_data['blue'],
    #             accent_data['alpha']
    #         )
    #     except Exception as e:
    #         logger.error(f"获取强调色失败: {e}")
    #         return (0, 120, 212, 255)  # 默认蓝色
    
    # def _update_colors(self):
    #     """Update button colors based on theme and accent settings"""
    #     if not self._theme_manager:
    #         return
            
    #     try:
    #         is_dark = self._theme_manager.isDarkMode()
            
    #         if self._use_accent:
    #             # 强调色模式
    #             r, g, b, a = self._get_accent_color()
    #             # 计算hover和pressed状态的颜色
    #             hover_r = min(r + 10, 255)
    #             hover_g = min(g + 15, 255)
    #             hover_b = min(b - 10, 255)
    #             pressed_r = max(r + 20, 0)
    #             pressed_g = max(g + 35, 0)
    #             pressed_b = max(b + 0, 0)
                
    #             qss = f"""
    #             QPushButton {{
    #                 background-color: rgba({r},{g},{b},{a/255:.2f});
    #                 border: none;
    #                 border-radius: 7px;
    #             }}
    #             QPushButton:hover {{
    #                 background-color: rgba({hover_r},{hover_g},{hover_b},{a/255:.2f});
    #             }}
    #             QPushButton:pressed {{
    #                 background-color: rgba({pressed_r},{pressed_g},{pressed_b},{a/255:.2f});
    #             }}
    #             QLabel {{
    #                 color: white;
    #                 font-weight: bold;
    #                 font-size: 13px;
    #                 background: transparent;
    #             }}
    #             """
    #         else:
    #             # 普通模式 - 根据主题切换颜色
    #             if is_dark:
    #                 qss = """
    #                 QPushButton {
    #                     background-color: rgba(50, 42, 49, 0.95);
    #                     border: none;
    #                     border-radius: 7px;
    #                 }
    #                 QPushButton:hover {
    #                     background-color: rgba(67, 56, 58, 0.9);
    #                     border: 1px solid #3b3235;
    #                 }
    #                 QPushButton:pressed {
    #                     background-color: rgba(67, 56, 58, 0.6);
    #                     border: 1px solid #3b3235;
    #                 }
    #                 QLabel {
    #                     color: #DFDFDF;
    #                     font-weight: bold;
    #                     font-size: 13px;
    #                     background: transparent;
    #                 }
    #                 """
    #             else:
    #                 qss = """
    #                 QPushButton {
    #                     background-color: rgba(254, 254, 254, 0.9);
    #                     border: 1px solid #EAE2E5;
    #                     border-radius: 7px;
    #                 }
    #                 QPushButton:hover {
    #                     background-color: rgba(251, 250, 251, 0.8);
    #                     border: 1px solid #ddd9d9;
    #                 }
    #                 QPushButton:pressed {
    #                     background-color: rgba(252, 250, 251, 0.7);
    #                     border: 1px solid #EAE2E5;
    #                 }
    #                 QLabel {
    #                     color: #2D2932;
    #                     font-size: 13px;
    #                     background: transparent;
    #                 }
    #                 """
            
    #         # 应用样式表
    #         self.setStyleSheet(qss)
            
    #     except Exception as e:
    #         logger.error(f"更新按钮颜色失败: {e}")
    #         self._init_style()
    
    # def sizeHint(self):
    #     return QSize(100, 30)
    
    # def _setup_layout(self, text: str):
    #     """设置按钮布局"""
    #     layout = QHBoxLayout(self)
    #     layout.setContentsMargins(10, 6, 10, 6)
    #     layout.setSpacing(0)
        
    #     # 创建文本标签
    #     self._text_label = QLabel(text)
    #     self._text_label.setWordWrap(self._wrap_text)
        
    #     # 设置文本对齐方式
    #     if self._wrap_text:
    #         self._text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    #     else:
    #         self._text_label.setAlignment(Qt.AlignCenter)
        
    #     layout.addWidget(self._text_label)
        
    #     # 设置大小策略
    #     self.setSizePolicy(
    #         QSizePolicy.Minimum if self._wrap_text else QSizePolicy.Fixed,
    #         QSizePolicy.Minimum
    #     )
    
    # def setText(self, text: str):
    #     """重写setText方法"""
    #     super().setText(text)
    #     if hasattr(self, '_text_label'):
    #         self._text_label.setText(text)
    #         self.updateGeometry()  # 触发重新计算大小
    
    # def minimumSizeHint(self) -> QSize:
    #     """最小建议大小"""
    #     # 获取文本大小
    #     text_size = self._text_label.sizeHint()
        
    #     # 计算最小宽度（包括边距）
    #     min_width = text_size.width() + 20  # 左右各10的边距
        
    #     # 计算最小高度（包括边距）
    #     min_height = text_size.height() + 12  # 上下各6的边距
        
    #     # 确保最小尺寸
    #     min_width = max(min_width, 100)  # 最小宽度100
    #     min_height = max(min_height, 30)  # 最小高度30
        
    #     return QSize(min_width, min_height)
    
    # def sizeHint(self) -> QSize:
    #     """建议大小"""
    #     return self.minimumSizeHint()


