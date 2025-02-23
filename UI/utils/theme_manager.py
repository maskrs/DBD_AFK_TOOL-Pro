import sys
from ctypes import windll, c_int, byref, sizeof
from enum import Enum, auto
from PySide6.QtCore import QObject, Signal, Property, Qt, QTimer
from PySide6.QtGui import QPalette, QColor, QPainter, QRadialGradient
from PySide6.QtWidgets import QWidget, QGraphicsBlurEffect
import logging
from win32mica import ApplyMica, MicaTheme, MicaStyle
from .theme_watcher import ThemeWatcher
from .system_theme_utils import get_system_theme, get_system_accent_color

logger = logging.getLogger(__name__)

class BackdropType(Enum):
    """背景效果类型"""
    NONE = auto()
    MICA = auto()
    ACRYLIC = auto()
    AUTO = auto()

class ThemeManager(QObject):
    """主题管理器"""
    themeChanged = Signal(bool)  # 主题变化信号
    accentColorChanged = Signal(dict)  # 强调色变化信号
    backdropChanged = Signal(BackdropType)  # 背景效果变化信号

    def __init__(self):
        super().__init__()
        self._window = None
        self._backdrop_type = BackdropType.AUTO
        self._dark_mode = get_system_theme()
        self._accent_color = get_system_accent_color()
        self._supports_mica = sys.getwindowsversion().build >= 22000
        
        # 创建主题监听器
        self._theme_watcher = ThemeWatcher(self)
        
        # 连接强调色变化信号到背景更新
        self.accentColorChanged.connect(self._on_accent_color_changed)
    
    def _on_accent_color_changed(self, new_accent):
        """处理强调色变化"""
        if self._window:
            # 更新窗口效果
            self._apply_current_backdrop()
            
            # 更新所有使用强调色的控件
            self._update_accent_color_widgets(self._window)
    
    def _update_accent_color_widgets(self, parent_widget):
        """递归更新所有使用强调色的控件"""
        for child in parent_widget.findChildren(QWidget):
            # 检查是否有更新颜色的方法
            if hasattr(child, '_update_colors'):
                child._update_colors()
            # 检查是否有更新图标的方法
            if hasattr(child, 'update_icon'):
                child.update_icon()

    def setWindow(self, window):
        """设置窗口"""
        self._window = window
        if window:
            self._apply_current_backdrop()
            # 先发送主题信号，确保所有组件都能收到初始主题状态
            self.themeChanged.emit(self._dark_mode)
            self.accentColorChanged.emit(self._accent_color)
            # 然后设置主题模式
            self.setDarkMode(self._dark_mode)

    def isDarkMode(self) -> bool:
        """获取当前主题模式"""
        return self._dark_mode

    def setDarkMode(self, dark: bool):
        """设置主题模式"""
        if self._dark_mode != dark:
            self._dark_mode = dark
            if self._window:
                # 先应用背景效果
                QTimer.singleShot(100, self._apply_current_backdrop)
                # 再发送信号
                self.themeChanged.emit(dark)

    def toggleTheme(self):
        """切换主题"""
        self.setDarkMode(not self._dark_mode)

    @property
    def accent_color(self) -> dict:
        """获取当前强调色"""
        return self._accent_color

    def accentColor(self) -> dict:
        """@deprecated 使用 accent_color 属性代替"""
        return self.accent_color

    def _apply_current_backdrop(self):
        """应用当前背景效果"""
        if not self._window:
            return

        try:
            hwnd = int(self._window.winId())
            
            # 设置窗口属性
            if self._backdrop_type in [BackdropType.MICA, BackdropType.AUTO] and self._supports_mica:
                # 启用透明和Mica效果
                self._window.setAttribute(Qt.WA_TranslucentBackground)
                self._window.setAutoFillBackground(False)
                
                # 应用Mica效果
                theme = MicaTheme.DARK if self._dark_mode else MicaTheme.LIGHT
                ApplyMica(hwnd, theme, MicaStyle.DEFAULT)
            else:
                # 禁用透明，使用纯色背景
                self._window.setAttribute(Qt.WA_TranslucentBackground, False)
                self._window.setAutoFillBackground(False)
                
                # 设置背景色
                palette = self._window.palette()
                if self._dark_mode:
                    palette.setColor(QPalette.Window, QColor(32, 32, 32))
                else:
                    palette.setColor(QPalette.Window, QColor(240, 240, 240))
                self._window.setPalette(palette)
                
                # 设置标题栏颜色
                try:
                    accent = self.accent_color
                    title_bar_color = (accent['blue'] << 16) | (accent['green'] << 8) | accent['red']
                    windll.dwmapi.DwmSetWindowAttribute(
                        hwnd,
                        35,  # DWMWA_CAPTION_COLOR
                        byref(c_int(title_bar_color)),
                        sizeof(c_int)
                    )
                except Exception as e:
                    logger.error(f"设置标题栏颜色失败: {e}")

        except Exception as e:
            logger.error(f"应用背景效果失败: {e}")

    def _apply_gradient_backdrop(self):
        """Apply gradient backdrop effect using Qt native painting"""
        class GradientWidget(QWidget):
            def __init__(self, parent=None, dark_mode=False):
                super().__init__(parent)
                self.dark_mode = dark_mode
                self.opacity = 0.22 if dark_mode else 0.15  # 增加亮色模式的不透明度
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setAutoFillBackground(False)
                
                # 添加模糊效果
                self.blur = QGraphicsBlurEffect()
                self.blur.setBlurRadius(30)
                self.setGraphicsEffect(self.blur)
                
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # 创建基础颜色和渐变颜色
                if self.dark_mode:
                    base_color = QColor(32, 32, 32)
                    # 深色模式：鲜艳的渐变色
                    color1 = QColor(255, 100, 100)  # 鲜艳的红色
                    color2 = QColor(100, 150, 255)  # 鲜艳的蓝色
                    color3 = QColor(200, 100, 255)  # 鲜艳的紫色
                    color4 = QColor(100, 255, 180)  # 鲜艳的青色
                else:
                    base_color = QColor(255, 255, 255)
                    # 亮色模式：增加饱和度的渐变色
                    color1 = QColor(255, 130, 130)  # 更鲜艳的粉红
                    color2 = QColor(130, 180, 255)  # 更鲜艳的天蓝
                    color3 = QColor(200, 130, 255)  # 更鲜艳的紫色
                    color4 = QColor(130, 255, 170)  # 更鲜艳的青绿
                
                painter.fillRect(self.rect(), base_color)
                
                # 创建更丰富的渐变点
                gradients = [
                    # 主要渐变
                    (0.85, 0.15, color1, 0.9, 0.8),  # 右上
                    (0.15, 0.85, color2, 0.9, 0.8),  # 左下
                    # 中心渐变
                    (0.5, 0.5, color3, 0.7, 0.5),
                    # 角落渐变
                    (0.9, 0.1, color1, 0.5, 0.3),
                    (0.1, 0.9, color2, 0.5, 0.3),
                    (0.1, 0.1, color4, 0.5, 0.3),
                    (0.9, 0.9, color3, 0.5, 0.3),
                    # 补充渐变
                    (0.7, 0.3, color3, 0.4, 0.2),
                    (0.3, 0.7, color4, 0.4, 0.2),
                    (0.3, 0.3, color1, 0.4, 0.2),
                    (0.7, 0.7, color2, 0.4, 0.2),
                ]
                
                for x, y, color, size_factor, intensity in gradients:
                    gradient = QRadialGradient(
                        x * self.width(),
                        y * self.height(),
                        max(self.width(), self.height()) * size_factor
                    )
                    
                    # 创建更平滑的颜色过渡
                    current_opacity = self.opacity * intensity
                    gradient.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 
                                                int(255 * current_opacity)))
                    gradient.setColorAt(0.3, QColor(color.red(), color.green(), color.blue(), 
                                                  int(255 * current_opacity * 0.8)))
                    gradient.setColorAt(0.6, QColor(color.red(), color.green(), color.blue(), 
                                                  int(255 * current_opacity * 0.4)))
                    gradient.setColorAt(0.8, QColor(color.red(), color.green(), color.blue(), 
                                                  int(255 * current_opacity * 0.2)))
                    gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
                    
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    painter.fillRect(self.rect(), gradient)
                    
            def resizeEvent(self, event):
                # 调整模糊效果
                blur_radius = min(30, max(10, min(self.width(), self.height()) / 30))
                self.blur.setBlurRadius(blur_radius)
                self.update()
                super().resizeEvent(event)
                
            def update_theme(self, dark_mode):
                """Update widget theme"""
                self.dark_mode = dark_mode
                self.opacity = 0.22 if dark_mode else 0.15
                self.update()
        
        # 清除现有的渐变小部件
        for child in self._window.findChildren(GradientWidget):
            child.deleteLater()
            
        # 创建新的渐变背景小部件
        gradient_widget = GradientWidget(self._window, self.isDarkMode())
        gradient_widget.lower()
        gradient_widget.resize(self._window.size())
        gradient_widget.show()
        
        # 连接主题变化信号
        self.themeChanged.connect(gradient_widget.update_theme)
        
        # 连接窗口大小变化信号
        self._window.resizeEvent = lambda event: (
            gradient_widget.resize(event.size()),
            super(type(self._window), self._window).resizeEvent(event)
        )
        
        # 设置标题栏颜色
        try:
            # 获取窗口句柄
            hwnd = self._window.winId()
            
            # 获取当前的强调色
            accent = self.accentColor()
            title_bar_color = (accent['blue'] << 16) | (accent['green'] << 8) | accent['red']
            
            # 设置标题栏颜色
            DWMWA_CAPTION_COLOR = 35  # Windows 11 22H2 及更高版本支持
            windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_CAPTION_COLOR,
                byref(c_int(title_bar_color)),
                sizeof(c_int)
            )
        except Exception as e:
            print(f"设置标题栏颜色失败: {e}")

    darkMode = Property(bool, isDarkMode, setDarkMode, notify=themeChanged)
