import ctypes
import time
import pydirectinput
import random
import numpy as np

# 初始化pydirectinput
pydirectinput.FAILSAFE = False

# 定义Windows API函数
ClientToScreen = ctypes.windll.user32.ClientToScreen
ScreenToClient = ctypes.windll.user32.ScreenToClient
GetWindowRect = ctypes.windll.user32.GetClientRect

# RECT结构体
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

# POINT结构体
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

def factorial(n):
    """计算阶乘"""
    if n == 0:
        return 1
    return n * factorial(n - 1)

def comb(n, k):
    """计算组合数 C(n,k)"""
    return factorial(n) // (factorial(k) * factorial(n - k))

def bezier_curve(start_pos, end_pos, control_points, steps):
    """
    生成贝塞尔曲线路径
    :param start_pos: 起始位置 (x, y)
    :param end_pos: 结束位置 (x, y)
    :param control_points: 控制点列表 [(x1,y1), (x2,y2),...]
    :param steps: 路径点数量
    :return: 路径点列表
    """
    points = [start_pos] + control_points + [end_pos]
    n = len(points) - 1
    
    def bernstein(i, n, t):
        return comb(n, i) * t**i * (1-t)**(n-i)
    
    path = []
    for t in np.linspace(0, 1, steps):
        x = sum(point[0] * bernstein(i, n, t) for i, point in enumerate(points))
        y = sum(point[1] * bernstein(i, n, t) for i, point in enumerate(points))
        path.append((int(x), int(y)))
    return path

class MouseController:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def get_window_rect(self):
        rect = RECT()
        if GetWindowRect(self.hwnd, ctypes.byref(rect)):
            return rect
        return None

    def client_to_screen(self, relative_x, relative_y):
        """
        将窗口相对坐标转换为屏幕坐标
        :param relative_x: 相对窗口的x坐标
        :param relative_y: 相对窗口的y坐标
        :return: 屏幕坐标
        """
        pt = POINT(relative_x, relative_y)
        if ClientToScreen(self.hwnd, ctypes.byref(pt)):
            return pt.x, pt.y
        return relative_x, relative_y

    def screen_to_client(self, screen_x, screen_y):
        """
        将屏幕坐标转换为窗口相对坐标
        :param screen_x: 屏幕的x坐标
        :param screen_y: 屏幕的y坐标
        :return: 窗口相对坐标
        """
        pt = POINT(screen_x, screen_y)
        if ScreenToClient(self.hwnd, ctypes.byref(pt)):
            return pt.x, pt.y
        return screen_x, screen_y

    def _smooth_move(self, start_x, start_y, end_x, end_y):
        """
        平滑移动鼠标
        :param start_x: 起始x坐标
        :param start_y: 起始y坐标
        :param end_x: 目标x坐标
        :param end_y: 目标y坐标
        """
        try:
            # 生成1-2个随机控制点
            num_control_points = random.randint(1, 2)
            control_points = []
            
            # 计算控制点的范围
            min_x = min(start_x, end_x)
            max_x = max(start_x, end_x)
            min_y = min(start_y, end_y)
            max_y = max(start_y, end_y)
            
            # 生成随机控制点
            for _ in range(num_control_points):
                ctrl_x = random.randint(min_x - 50, max_x + 50)
                ctrl_y = random.randint(min_y - 50, max_y + 50)
                control_points.append((ctrl_x, ctrl_y))
            
            # 生成贝塞尔曲线路径
            steps = random.randint(10, 20)  # 减少步数
            path = bezier_curve(
                (start_x, start_y),
                (end_x, end_y),
                control_points,
                steps
            )
            
            # 执行移动
            for point in path:
                x, y = int(point[0]), int(point[1])
                pydirectinput.moveTo(x, y, _pause=False)  # 添加_pause=False参数
                time.sleep(random.uniform(0.001, 0.002))  # 减小延迟
                
        except Exception as e:
            print(f"移动鼠标时出错: {e}")
            pydirectinput.moveTo(end_x, end_y)  # 直接移动到目标位置

    def moveto(self, relative_x, relative_y):
        """
        移动鼠标到窗口内的相对坐标
        :param relative_x: 相对窗口的x坐标
        :param relative_y: 相对窗口的y坐标
        """
        screen_x, screen_y = self.client_to_screen(relative_x, relative_y)
        if screen_x is not None and screen_y is not None:
            try:
                # 获取当前鼠标位置
                current_x, current_y = pydirectinput.position()
                # 使用平滑移动
                self._smooth_move(current_x, current_y, screen_x, screen_y)
            except Exception:
                pydirectinput.moveTo(0, 0)

    def moveclick(self, relative_x, relative_y, delay: float = 0, click_delay: float = 0, times: int = 1, interval: float = 0.0):
        """
        在窗口内的相对坐标点击鼠标
        """
        screen_x, screen_y = self.client_to_screen(relative_x, relative_y)
        if screen_x is not None and screen_y is not None:
            try:
                # 获取当前鼠标位置
                current_x, current_y = pydirectinput.position()
                # 使用平滑移动
                self._smooth_move(current_x, current_y, screen_x, screen_y)
            except Exception:
                pydirectinput.moveTo(0, 0)
            time.sleep(delay)
            for _ in range(times):
                pydirectinput.click()
                if interval > 0 and _ < times - 1:
                    time.sleep(interval)
            time.sleep(click_delay)

    @staticmethod
    def get_mouse_position():
        """
        获取当前鼠标在屏幕上的坐标
        """
        return pydirectinput.position()

