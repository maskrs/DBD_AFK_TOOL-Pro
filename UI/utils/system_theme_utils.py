"""Windows系统主题相关工具"""
import winreg
import logging

logger = logging.getLogger(__name__)

def get_system_theme() -> bool:
    """获取系统主题设置（True表示深色模式）"""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        ) as key:
            return winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0
    except Exception as e:
        logger.error(f"获取系统主题失败: {e}")
        return False

def get_system_accent_color() -> dict:
    """获取系统强调色"""
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\DWM"
        ) as key:
            color_value = winreg.QueryValueEx(key, "ColorizationColor")[0]
            return {
                "red": (color_value >> 16) & 0xFF,
                "green": (color_value >> 8) & 0xFF,
                "blue": color_value & 0xFF,
                "alpha": (color_value >> 24) & 0xFF
            }
    except Exception as e:
        logger.error(f"获取系统强调色失败: {e}")
        return {"red": 0, "green": 120, "blue": 212, "alpha": 255}