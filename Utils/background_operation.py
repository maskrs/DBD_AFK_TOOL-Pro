import ctypes
import pynput
from ctypes import byref, sizeof
from ctypes import wintypes
from PIL import Image  # pillow == 9.3.0
from PIL import ImageGrab
from PIL import UnidentifiedImageError
from PyQt5.QtGui import QImage

keyboard = pynput.keyboard.Controller()
mouse = pynput.mouse.Controller()
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


VkCode = {
    "tab": pynput.keyboard.Key.tab,  # 0x09
    "enter": pynput.keyboard.Key.enter,  # 0x0D
    "backspace": pynput.keyboard.Key.backspace,  # 0x08
    "shift": pynput.keyboard.Key.shift,  # 0x10
    "control": pynput.keyboard.Key.ctrl,  # 0x11
    "alt": pynput.keyboard.Key.alt,  # 0x12
    "menu": pynput.keyboard.Key.menu,  # 0x12
    "pause": pynput.keyboard.Key.pause,  # 0x13
    "caps_lock": pynput.keyboard.Key.caps_lock,  # 0x14
    "escape": pynput.keyboard.Key.esc,  # 0x1B
    "space": pynput.keyboard.Key.space,  # 0x20
    "end": pynput.keyboard.Key.end,  # 0x23
    "home": pynput.keyboard.Key.home,  # 0x24
    "left": pynput.keyboard.Key.left,  # 0x25
    "up": pynput.keyboard.Key.up,  # 0x26
    "right": pynput.keyboard.Key.right,  # 0x27
    "down": pynput.keyboard.Key.down,  # 0x28
    "print_screen": pynput.keyboard.Key.print_screen,  # 0x2C
    "insert": pynput.keyboard.Key.insert,  # 0x2D
    "delete": pynput.keyboard.Key.delete,  # 0x2E
    "numpad0": pynput.keyboard.KeyCode.from_vk(96),  # 0x60
    "numpad1": pynput.keyboard.KeyCode.from_vk(97),  # 0x61
    "numpad2": pynput.keyboard.KeyCode.from_vk(98),  # 0x62
    "numpad3": pynput.keyboard.KeyCode.from_vk(99),  # 0x63
    "numpad4": pynput.keyboard.KeyCode.from_vk(100),  # 0x64
    "numpad5": pynput.keyboard.KeyCode.from_vk(101),  # 0x65
    "numpad6": pynput.keyboard.KeyCode.from_vk(102),  # 0x66
    "numpad7": pynput.keyboard.KeyCode.from_vk(103),  # 0x67
    "numpad8": pynput.keyboard.KeyCode.from_vk(104),  # 0x68
    "numpad9": pynput.keyboard.KeyCode.from_vk(105),  # 0x69
    "f1": pynput.keyboard.KeyCode.from_vk(112),  # 0x70
    "f2": pynput.keyboard.KeyCode.from_vk(113),  # 0x71
    "f3": pynput.keyboard.KeyCode.from_vk(114),  # 0x72
    "f4": pynput.keyboard.KeyCode.from_vk(115),  # 0x73
    "f5": pynput.keyboard.KeyCode.from_vk(116),  # 0x74
    "f6": pynput.keyboard.KeyCode.from_vk(117),  # 0x75
    "f7": pynput.keyboard.KeyCode.from_vk(118),  # 0x76
    "f8": pynput.keyboard.KeyCode.from_vk(119),  # 0x77
    "f9": pynput.keyboard.KeyCode.from_vk(120),  # 0x78
    "f10": pynput.keyboard.KeyCode.from_vk(121),  # 0x79
    "f11": pynput.keyboard.KeyCode.from_vk(122),  # 0x7A
    "f12": pynput.keyboard.KeyCode.from_vk(123),  # 0x7B
    "lshift": pynput.keyboard.Key.shift_l,  # 0xA0
    "rshift": pynput.keyboard.Key.shift_r,  # 0xA1
    "lcontrol": pynput.keyboard.Key.ctrl_l,  # 0xA2
    "rcontrol": pynput.keyboard.Key.ctrl_r,  # 0xA3
    "lalt": pynput.keyboard.Key.alt_l,  # 0xA4
    "ralt": pynput.keyboard.Key.alt_r,  # 0xA5
}

MouseCode = {
    "mouse_left": pynput.mouse.Button.left,
    "mouse_right": pynput.mouse.Button.right,
    "mouse_middle": pynput.mouse.Button.middle
}


def get_virtual_keycode(key: str):
    """根据按键名获取虚拟按键码

    Args:
        key (str): 按键名

    Returns:
        int: 虚拟按键码
    """
    if key in VkCode:
        return VkCode[key]
    else:
        return key


def get_virtual_mousecode(key: str):
    if key in MouseCode:
        return MouseCode[key]
    else:
        return None


def key_down(key: str):
    """按下指定按键

    Args:
        key (str): 按键名
    """
    try:
        vk_code = get_virtual_keycode(key)
        keyboard.press(vk_code)
    except AttributeError:
        pass


def key_up(key: str):
    """放开指定按键

    Args:
        key (str): 按键名
    """
    try:
        vk_code = get_virtual_keycode(key)
        keyboard.release(vk_code)
    except AttributeError:
        pass

def mouse_down(key: str = "mouse_left"):
    try:
        mosue_code = get_virtual_mousecode(key)
        mouse.press(mosue_code)
    except AttributeError:
        pass

def mouse_up(key: str = "mouse_left"):
    try:
        mosue_code = get_virtual_mousecode(key)
        mouse.release(mosue_code)
    except AttributeError:
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
