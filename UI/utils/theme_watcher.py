from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication
from PySide6.QtWidgets import QApplication
import ctypes
from .system_theme_utils import get_system_theme, get_system_accent_color

class ThemeWatcher(QAbstractNativeEventFilter):
    """Windows主题变化监听器"""
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self._current_accent = get_system_accent_color()
        
        # 注册事件过滤器
        QApplication.instance().installNativeEventFilter(self)
    
    def nativeEventFilter(self, eventType, message):
        """处理原生事件"""
        try:
            if eventType == b"windows_generic_MSG":
                msg = ctypes.wintypes.MSG.from_address(message.__int__())
                
                # WM_SETTINGCHANGE
                if msg.message == 0x001A:
                    if msg.lParam:
                        setting = ctypes.wstring_at(msg.lParam)
                        
                        # 主题变化
                        if setting == "ImmersiveColorSet":
                            new_theme = get_system_theme()
                            if new_theme != self.theme_manager._dark_mode:
                                self.theme_manager.setDarkMode(new_theme)
                        
                        # 强调色变化
                        elif setting == "WindowsThemeElement" or setting == "ImmersiveColorSet":
                            new_accent = get_system_accent_color()
                            if (new_accent['red'] != self._current_accent['red'] or
                                new_accent['green'] != self._current_accent['green'] or
                                new_accent['blue'] != self._current_accent['blue']):
                                self._current_accent = new_accent
                                self.theme_manager._accent_color = new_accent
                                self.theme_manager.accentColorChanged.emit(new_accent)
                                
                # WM_DWMCOLORIZATIONCOLORCHANGED
                elif msg.message == 0x0320:
                    # wParam 包含新的强调色
                    color_value = msg.wParam
                    new_accent = {
                        "red": (color_value >> 16) & 0xFF,
                        "green": (color_value >> 8) & 0xFF,
                        "blue": color_value & 0xFF,
                        "alpha": (color_value >> 24) & 0xFF
                    }
                    if (new_accent['red'] != self._current_accent['red'] or
                        new_accent['green'] != self._current_accent['green'] or
                        new_accent['blue'] != self._current_accent['blue']):
                        self._current_accent = new_accent
                        self.theme_manager._accent_color = new_accent
                        self.theme_manager.accentColorChanged.emit(new_accent)
                        
        except Exception as e:
            pass  # 忽略错误，保持事件过滤器运行
            
        return False, 0
    