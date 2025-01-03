"""Windows DWM effects module"""
import ctypes
from ctypes import wintypes, Structure, c_int, POINTER, sizeof, byref, cast
import sys
from enum import IntEnum
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Windows API Constants
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_MICA_EFFECT = 1029
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMWA_WINDOW_CORNER_PREFERENCE = 33
WCA_ACCENT_POLICY = 19

class BackdropType(IntEnum):
    """系统背景效果类型"""
    NONE = 1
    MICA = 2
    ACRYLIC = 3
    AUTO = 4

class CornerPreference(IntEnum):
    """窗口圆角首选项"""
    DEFAULT = 0
    DONT_ROUND = 1
    ROUND = 2
    SMALL_ROUND = 3

class AccentState(IntEnum):
    """窗口特效状态"""
    DISABLED = 0
    ENABLE_GRADIENT = 1
    ENABLE_TRANSPARENTGRADIENT = 2
    ENABLE_BLURBEHIND = 3
    ENABLE_ACRYLICBLURBEHIND = 4
    INVALID_STATE = 5

class AccentPolicy(Structure):
    _fields_ = [
        ("AccentState", c_int),
        ("AccentFlags", c_int),
        ("GradientColor", c_int),
        ("AnimationId", c_int)
    ]

class WindowCompositionAttribute(Structure):
    _fields_ = [
        ("Attribute", c_int),
        ("Data", POINTER(c_int)),
        ("SizeOfData", wintypes.DWORD)
    ]

class MARGINS(Structure):
    _fields_ = [
        ("cxLeftWidth", c_int),
        ("cxRightWidth", c_int),
        ("cyTopHeight", c_int),
        ("cyBottomHeight", c_int)
    ]

class DWMEffect:
    """DWM窗口特效管理器"""
    
    def __init__(self):
        self.dwm = ctypes.WinDLL("dwmapi")
        self.user32 = ctypes.WinDLL("user32")
        
        # 设置API原型
        self._setup_function_prototypes()
        self._cached_win_version = None

    def _setup_function_prototypes(self):
        """设置Windows API函数原型"""
        self.dwm.DwmSetWindowAttribute.argtypes = [
            wintypes.HWND, wintypes.DWORD,
            POINTER(c_int), wintypes.DWORD
        ]
        self.dwm.DwmSetWindowAttribute.restype = wintypes.LONG
        
        self.dwm.DwmExtendFrameIntoClientArea.argtypes = [
            wintypes.HWND, POINTER(MARGINS)
        ]
        self.dwm.DwmExtendFrameIntoClientArea.restype = wintypes.LONG
        
        # SetWindowCompositionAttribute是未公开API
        try:
            self.user32.SetWindowCompositionAttribute.argtypes = [
                wintypes.HWND, POINTER(WindowCompositionAttribute)
            ]
            self.user32.SetWindowCompositionAttribute.restype = c_int
        except AttributeError:
            logger.warning("SetWindowCompositionAttribute not found")
    
    @property
    def windows_version(self) -> tuple:
        """获取Windows版本 (major, minor, build)"""
        if self._cached_win_version is None:
            version = sys.getwindowsversion()
            self._cached_win_version = (version.major, version.minor, version.build)
        return self._cached_win_version

    def _set_window_attribute(self, hwnd: int, attr: int, value: int) -> bool:
        """设置DWM窗口属性"""
        try:
            val = c_int(value)
            ret = self.dwm.DwmSetWindowAttribute(
                hwnd, attr, byref(val), sizeof(val)
            )
            return ret == 0
        except Exception as e:
            logger.error(f"设置窗口属性失败: {e}")
            return False

    def _apply_mica(self, hwnd: int) -> bool:
        """应用Mica效果"""
        build = self.windows_version[2]
        
        if build >= 22000:  # Windows 11 21H2+
            return self._set_window_attribute(
                hwnd,
                DWMWA_SYSTEMBACKDROP_TYPE,
                BackdropType.MICA.value
            )
        elif build >= 21996:  # Windows 11 初始版本
            return self._set_window_attribute(
                hwnd,
                DWMWA_MICA_EFFECT,
                1
            )
        return False

    def _apply_acrylic(self, hwnd: int) -> bool:
        """应用Acrylic效果"""
        try:
            # 扩展窗口框架
            margins = MARGINS(-1, -1, -1, -1)
            self.dwm.DwmExtendFrameIntoClientArea(hwnd, byref(margins))
            
            # 配置Acrylic效果
            accent = AccentPolicy()
            accent.AccentState = AccentState.ENABLE_ACRYLICBLURBEHIND.value
            accent.GradientColor = 0x00CCCCCC  # 半透明灰色
            
            comp_attr = WindowCompositionAttribute()
            comp_attr.Attribute = WCA_ACCENT_POLICY
            comp_attr.SizeOfData = sizeof(accent)
            comp_attr.Data = cast(byref(accent), POINTER(c_int))
            
            return bool(self.user32.SetWindowCompositionAttribute(hwnd, byref(comp_attr)))
        except Exception as e:
            logger.error(f"应用Acrylic效果失败: {e}")
            return False

    def set_backdrop(self, hwnd: int, backdrop_type: BackdropType) -> bool:
        """设置窗口背景效果"""
        logger.info(f"设置背景效果: {backdrop_type.name}")
        
        if backdrop_type == BackdropType.MICA:
            return self._apply_mica(hwnd)
        elif backdrop_type == BackdropType.ACRYLIC:
            return self._apply_acrylic(hwnd)
        elif backdrop_type == BackdropType.AUTO:
            # 优先尝试Mica，失败则尝试Acrylic
            return self._apply_mica(hwnd) or self._apply_acrylic(hwnd)
        return True

    def set_dark_mode(self, hwnd: int, enable: bool) -> bool:
        """设置深色模式"""
        return self._set_window_attribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            1 if enable else 0
        )

    def set_corner_preference(self, hwnd: int, preference: CornerPreference) -> bool:
        """设置窗口圆角样式"""
        return self._set_window_attribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            preference.value
        )

    def setup_window_theme(self, hwnd: int, dark_mode: bool = False) -> bool:
        """设置窗口主题相关属性"""
        try:
            # 设置深色模式
            self.set_dark_mode(hwnd, dark_mode)
            
            # Windows 11自动设置圆角
            if self.windows_version[2] >= 22000:
                self.set_corner_preference(hwnd, CornerPreference.ROUND)
            
            # 扩展框架
            margins = MARGINS(-1, -1, -1, -1)
            self.dwm.DwmExtendFrameIntoClientArea(hwnd, byref(margins))
            
            return True
        except Exception as e:
            logger.error(f"设置窗口主题失败: {e}")
            return False

# 全局实例
dwm_effect = DWMEffect()
