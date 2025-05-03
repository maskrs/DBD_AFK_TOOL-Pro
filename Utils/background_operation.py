import ctypes
import pydirectinput
from ctypes import byref, sizeof
from ctypes import wintypes
from PIL import Image  # pillow == 9.3.0
from PIL import ImageGrab
from PIL import UnidentifiedImageError
from PyQt5.QtGui import QImage

# 初始化pydirectinput
pydirectinput.FAILSAFE = False

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


# 虚拟按键码映射
VkCode = {
    "tab": "tab",
    "enter": "enter", 
    "backspace": "backspace",
    "shift": "shift",
    "control": "ctrl",
    "alt": "alt", 
    "menu": "alt",
    "pause": "pause",
    "caps_lock": "capslock",
    "escape": "esc",
    "space": "space",
    "end": "end",
    "home": "home",
    "left": "left",
    "up": "up", 
    "right": "right",
    "down": "down",
    "print_screen": "printscreen",
    "insert": "insert",
    "delete": "delete",
    # 数字键盘
    "numpad0": "num0",
    "numpad1": "num1", 
    "numpad2": "num2",
    "numpad3": "num3",
    "numpad4": "num4",
    "numpad5": "num5",
    "numpad6": "num6", 
    "numpad7": "num7",
    "numpad8": "num8",
    "numpad9": "num9",
    # F键
    "f1": "f1",
    "f2": "f2",
    "f3": "f3", 
    "f4": "f4",
    "f5": "f5",
    "f6": "f6",
    "f7": "f7",
    "f8": "f8",
    "f9": "f9",
    "f10": "f10",
    "f11": "f11",
    "f12": "f12",
    # 特殊键
    "lshift": "shiftleft",
    "rshift": "shiftright", 
    "lcontrol": "ctrlleft",
    "rcontrol": "ctrlright",
    "lalt": "altleft",
    "ralt": "altright"
}

MouseCode = {
    "mouse_left": "left",     # 左键
    "mouse_right": "right",   # 右键
    "mouse_middle": "middle"  # 中键
}

def get_virtual_keycode(key: str):
    """根据按键名获取虚拟按键码
    
    Args:
        key (str): 按键名
        
    Returns:
        str: pydirectinput支持的按键名
    """
    return VkCode.get(key, key)


def get_virtual_mousecode(key: str):
    """获取鼠标按键的映射值
    Args:
        key (str): 鼠标按键名称
    Returns:
        str: pydirectinput支持的鼠标按键值
    """
    if key in MouseCode:
        return MouseCode[key]
    return "left"  # 默认返回左键


def key_down(key: str):
    """按下指定按键
    
    Args:
        key (str): 按键名
    """
    try:
        vk_code = get_virtual_keycode(key)
        pydirectinput.keyDown(vk_code)
    except Exception:
        pass


def key_up(key: str):
    """放开指定按键
    
    Args:
        key (str): 按键名
    """
    try:
        vk_code = get_virtual_keycode(key)
        pydirectinput.keyUp(vk_code)
    except Exception:
        pass

def mouse_down(key: str = "mouse_left"):
    """按下鼠标按键
    Args:
        key (str): 鼠标按键名称,默认左键
    """
    try:
        button = get_virtual_mousecode(key)
        pydirectinput.mouseDown(button=button)
    except Exception:
        pass

def mouse_up(key: str = "mouse_left"):
    """释放鼠标按键
    Args:
        key (str): 鼠标按键名称,默认左键
    """
    try:
        button = get_virtual_mousecode(key)
        pydirectinput.mouseUp(button=button)
    except Exception:
        pass


# 定义 BITMAPINFOHEADER 结构体
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]


# 定义 BITMAPINFO 结构体，只包含 BITMAPINFOHEADER
class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
    ]


def screenshot(hwnd) -> Image:
    """后台截图
    :param hwnd:窗口句柄
    :return: Image"""

    # 获取窗口的设备上下文
    hdcScreen = user32.GetDC(None)
    hdcMem = gdi32.CreateCompatibleDC(hdcScreen)
    hwndRect = wintypes.RECT()
    user32.GetWindowRect(hwnd, byref(hwndRect))
    width = hwndRect.right - hwndRect.left
    height = hwndRect.bottom - hwndRect.top

    if width <= 0 and height <= 0:
        return None

    # 创建一个与屏幕兼容的位图
    hBitmap = gdi32.CreateCompatibleBitmap(hdcScreen, width, height)
    hOldBitmap = gdi32.SelectObject(hdcMem, hBitmap)

    # 截取窗口内容
    user32.PrintWindow(hwnd, hdcMem, 0x00000002)  # PRF_CLIENT

    # 准备 BITMAPINFO 结构
    bmpInfo = BITMAPINFO()
    bmpInfo.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmpInfo.bmiHeader.biWidth = width
    bmpInfo.bmiHeader.biHeight = -height
    bmpInfo.bmiHeader.biPlanes = 1
    bmpInfo.bmiHeader.biBitCount = 32
    bmpInfo.bmiHeader.biCompression = 0  # BI_RGB 的值是 0

    # 计算所需的缓冲区大小，确保每个扫描线都是4字节对齐
    aligned_width = ((width + 3) // 4) * 4  # 对齐到最近的4的倍数
    buffer_size = aligned_width * height * 4  # 每个像素占用 4 字节

    # 为位图数据分配内存
    buffer = ctypes.create_string_buffer(buffer_size)

    # 从设备上下文复制像素数据
    gdi32.GetDIBits(hdcMem, hBitmap, 0, height, buffer, byref(bmpInfo), 0)

    # 创建 QImage 并从 buffer 中加载数据
    q_image = QImage(buffer, width, height, QImage.Format_RGB32)

    try:
        # 转换PIL.Image对象
        pillow_image = Image.fromqimage(q_image)
    except UnidentifiedImageError:
        pillow_image = ImageGrab.grab()

    # 清理资源
    gdi32.SelectObject(hdcMem, hOldBitmap)
    gdi32.DeleteObject(hBitmap)
    gdi32.DeleteDC(hdcMem)
    user32.ReleaseDC(None, hdcScreen)

    return pillow_image
