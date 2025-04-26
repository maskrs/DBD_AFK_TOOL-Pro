"""
进程版本的OCR函数 - 用于多进程实现
"""
import os
import time
import tempfile
import pytesseract
import win32gui
import logging
from PIL import Image

from Utils.shared_state import shared_args, check_pause
from Utils.background_operation import screenshot
from Utils.Client2ScreenOperate import MouseController

# 创建日志记录器
log = logging.getLogger(__name__)

# 全局变量
hwnd = 0
MControl = None

def init_ocr(game_hwnd, mouse_controller):
    """初始化OCR相关变量"""
    global hwnd, MControl
    hwnd = game_hwnd
    MControl = mouse_controller


def img_ocr_process(x1, y1, x2, y2, sum=128, lang="chi_sim+eng") -> str:
    """进程版本的OCR识别函数"""
    global hwnd, MControl
    
    if hwnd == 0:
        log.warning('未检测到游戏窗口！')
        return ""
    
    result = ""
    image = screenshot(hwnd)
    if image is None:
        log.warning(f"截图失败，无效的截图区域！")
        return result
    
    screen_x1, screen_y1 = MControl.client_to_screen(x1, y1)
    screen_x2, screen_y2 = MControl.client_to_screen(x2, y2)
    
    # 按区域裁剪
    cropped_pixmap = image.crop((screen_x1, screen_y1, screen_x2, screen_y2))
    # 转换为灰度图
    grayscale_image = cropped_pixmap.convert('L')
    # 二值化
    binary_image = grayscale_image.point(lambda x: 255 if x > sum else 0, '1')
    
    custom_config = r'--oem 3 --psm 6'  # ocr识别模式
    
    try:
        # 创建一个临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_path = temp_file.name
            # 将二值化后的图像保存到临时文件
            binary_image.save(temp_path, format='JPEG')
            try:
                # 使用Tesseract OCR引擎识别图像中的文本
                result_unprocessed = pytesseract.image_to_string(temp_path, config=custom_config, lang=lang)
                if result_unprocessed:
                    result = "".join(result_unprocessed.split())
            except pytesseract.TesseractError:
                result = ""
    finally:
        # 确保临时文件被删除，防止内存泄露和磁盘空间占用
        os.unlink(temp_path)
    
    log.debug(f"OCR识别内容为：{result}")
    return result


def ocr_check_process(identification_key, capture_range, min_sum_name, name) -> bool:
    """进程版本的OCR检查函数"""
    # 获取坐标和阈值
    x1, y1, x2, y2 = shared_args.get(capture_range, [0, 0, 0, 0])
    threshold = shared_args.get(min_sum_name, [120, 130, 0])[0]
    keywords = shared_args.get(identification_key, [])
    
    # 调用OCR函数
    ocr_result = img_ocr_process(x1, y1, x2, y2, sum=threshold)
    
    # 检查结果是否包含关键字
    return any(keyword in ocr_result for keyword in keywords)


def starthall_process() -> bool:
    """进程版本的开始大厅检查函数"""
    return ocr_check_process('匹配大厅识别关键字', '匹配阶段的识别范围', '匹配大厅二值化阈值', "play")


def readyhall_process() -> bool:
    """进程版本的准备大厅检查函数"""
    return ocr_check_process('准备大厅识别关键字', '准备阶段的识别范围', '准备房间二值化阈值', "ready")


def gameover_process() -> bool:
    """进程版本的游戏结束检查函数"""
    return ocr_check_process('结算页识别关键字', '结算页的识别范围', '结算页二值化阈值', "gameover")


def disconnect_check_process() -> bool:
    """进程版本的断线检查函数"""
    return ocr_check_process('断线检测识别关键字', '断线检测的识别范围', '断线检测二值化阈值', "disconnect")
