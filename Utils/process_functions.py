"""
进程版本的操作函数 - 用于多进程实现
"""
import time
import random
import win32gui
import pyautogui as py
import pyperclip
import logging
import ctypes
from operator import eq, gt, ge, ne

from Utils.shared_state import shared_state, shared_args, pause_event, stop_event, cmd_queue, check_pause, process_safe_delay
from Utils.GameOperate import press_key, release_key, press_mouse, release_mouse, random_direction, random_movement
from Utils.Client2ScreenOperate import MouseController

# 创建日志记录器
log = logging.getLogger(__name__)

class ProcessInputChinese:
    """进程安全版本的InputChinese类"""
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.codes_list = []

    def vkey_to_scan_code(self, key_code):
        return self.user32.MapVirtualKeyA(key_code, 0)

    def key_down(self, key_code, ext=False):
        scan_code = self.vkey_to_scan_code(key_code)
        self.user32.keybd_event(key_code, scan_code, 0, 0)

    def key_up(self, key_code, ext=False):
        scan_code = self.vkey_to_scan_code(key_code)
        self.user32.keybd_event(key_code, scan_code, 2, 0)

    def num_key_press(self, digit):
        key_code = {
            '0': 0x60, '1': 0x61, '2': 0x62, '3': 0x63,
            '4': 0x64, '5': 0x65, '6': 0x66, '7': 0x67,
            '8': 0x68, '9': 0x69, '+': 0x6B
        }.get(digit)

        if key_code is None:
            raise ValueError(f"Invalid digit: {digit}")
        self.key_down(key_code)
        self.key_up(key_code)

    def type_alt_code(self, code):
        try:
            self.key_down(0xA4)  # 模拟Alt键按下
            for digit in str(code):
                self.num_key_press(digit)  # 模拟数字小键盘按键
                time.sleep(0.001)  # 按键间隔
        finally:
            self.key_up(0xA4)  # 模拟Alt键释放

    def str_to_codes(self, string, encode):
        for char in string:
            char_bytes = char.encode(encode)
            self.codes_list.append(int.from_bytes(char_bytes, 'big'))

    def press_codes_with_alt(self, string, encode):
        self.str_to_codes(string, encode)
        for code in self.codes_list:
            self.type_alt_code(code)
        self.codes_list.clear()


def is_edcs_only(content: str):
    """检查字符串是否只包含英文、数字和常见符号"""
    import re
    pattern = re.compile(r'^[A-Za-z0-9\s,.?!\"*/+\'()-]+$')
    return bool(pattern.match(content))


def auto_message_process(message_key='赛后发送消息'):
    """进程版本的自动留言函数"""
    py.press('enter')
    input_str = shared_args.get(message_key, '')
    if is_edcs_only(input_str):
        py.typewrite(input_str)
    else:
        input_cn = ProcessInputChinese()
        input_cn.press_codes_with_alt(input_str, 'gbk')
    py.press('enter')
    process_safe_delay(0.5)


def autospace_process():
    """进程版本的自动按空格函数"""
    log.info("自动空格进程已启动")
    while not shared_state['stop_space'] and not stop_event.is_set():
        if check_pause():
            break

        press_key('space')
        if process_safe_delay(5):  # 如果返回True表示收到停止信号
            break
        release_key('space')

    # 确保按键释放
    release_key('space')
    log.info("自动空格进程已停止")


def survivor_action_process():
    """进程版本的幸存者动作函数"""
    # 检查是否使用自定义命令
    if shared_args.get('cb_customcommand', False):
        # 这里需要特殊处理自定义命令
        cmd_queue.put(("CUSTOM_COMMAND", "逃生者"))
        return

    press_key('w')
    press_key('lshift')
    act_direction = random_direction()
    for i in range(10):
        if check_pause():
            break

        press_key(act_direction)
        if process_safe_delay(0.05):
            break
        release_key(act_direction)
        if process_safe_delay(0.7):
            break

    press_mouse()
    if process_safe_delay(2):
        pass
    release_mouse()
    release_key('lshift')
    release_key('w')


def killer_action_process():
    """进程版本的杀手动作函数"""
    # 随版本更改，适配不同的屠夫
    ctrl_lst_cn = ["医生", "梦魇", "小丑", "魔王", "连体婴", "影魔", "白骨商人", "好孩子", "未知恶物", "巫妖"]
    need_lst_cn = ["门徒", "魔王", "死亡枪手", "骗术师", "NEMESIS", "地狱修士", "艺术家", "影魔", "奇点", "操纵者",
                   "好孩子", "未知恶物", "巫妖", "黑暗之主"]
    ctrl_lst_en = ["DOCTOR", "NIGHTMARE", "CLOWN", "DEMOGORGON", "TWINS", "DREDGE", "SKULL MERCHANT", "GOOD GUY",
                   "UNKNOWN", "LICH"]
    need_lst_en = ["PIG", "DEMOGORGON", "DEATHSLINGER", "TRICKSTER", "NEMESIS",
                   "CENOBITE", "ARTIST", "DREDGE", "SINGULARITY", "MASTERMIND", "GOOD GUY", "UNKNOWN",
                   "LICH", "DARK LORD"]

    # 根据语言选择列表
    if shared_args.get('rb_chinese', True):
        ctrl_lst = ctrl_lst_cn
        need_lst = need_lst_cn
    else:
        ctrl_lst = ctrl_lst_en
        need_lst = need_lst_en

    # 获取当前杀手
    killer_lst = shared_args.get('select_killer_lst', [])
    if not killer_lst:
        return

    # 防止下标越界
    killer_num = len(killer_lst)
    index = shared_state.get('index', 0)
    if ge(index - 1, 0):
        killer_num = index - 1
    else:
        killer_num -= 1

    try:
        # 检查是否使用自定义命令
        if shared_args.get('cb_customcommand', False):
            # 这里需要特殊处理自定义命令
            cmd_queue.put(("CUSTOM_COMMAND", killer_lst[killer_num]))
            return

        press_key('w')
        if eq(killer_lst[killer_num], "枯萎者") or eq(killer_lst[killer_num], "BLIGHT"):
            release_key('w')
            for _ in range(5):
                if check_pause():
                    break

                act_move = random_movement()
                press_key(act_move)
                act_direction = random_direction()
                press_mouse('right')
                if process_safe_delay(0.05):
                    break
                release_mouse('right')
                if process_safe_delay(0.7):
                    break
                press_key(act_direction)
                if process_safe_delay(0.3):
                    break
                release_key(act_direction)
                release_key(act_move)
        elif eq(killer_lst[killer_num], "怨灵") or eq(killer_lst[killer_num], "SPIRIT"):
            release_key('w')
            act_move = random_movement()
            press_key(act_move)
            act_direction = random_direction()
            press_mouse('right')
            if process_safe_delay(3):
                pass
            press_key(act_direction)
            if process_safe_delay(0.3):
                pass
            release_key(act_direction)
            if process_safe_delay(5):
                pass
            release_key(act_move)
            release_mouse('right')
        elif killer_lst[killer_num] in need_lst:
            act_direction = random_direction()
            for _ in range(5):
                if check_pause():
                    break

                press_key(act_direction)
                if process_safe_delay(0.05):
                    break
                release_key(act_direction)
                if process_safe_delay(0.7):
                    break

            # 技能释放
            press_mouse('right')
            if process_safe_delay(3):
                pass
            press_mouse()
            if process_safe_delay(0.1):
                pass
            release_mouse()
            release_mouse('right')
            if process_safe_delay(2):
                pass
            press_key('lcontrol')
            release_key('lcontrol')

            if killer_lst[killer_num] in ctrl_lst:
                press_key('lcontrol')
                if process_safe_delay(4.3):
                    pass
                release_key('lcontrol')
        else:
            act_direction = random_direction()
            for _ in range(5):
                if check_pause():
                    break

                press_key(act_direction)
                if process_safe_delay(0.05):
                    break
                release_key(act_direction)
                if process_safe_delay(0.7):
                    break

            # 技能释放
            press_mouse('right')
            if process_safe_delay(3):
                pass
            press_key('lcontrol')
            release_key('lcontrol')
            release_mouse('right')

            if killer_lst[killer_num] in ctrl_lst:
                press_key('lcontrol')
                if process_safe_delay(4.3):
                    pass
                release_key('lcontrol')
        release_key('w')

    except IndexError:
        log.error(f"下标越界···{killer_num}")
    except Exception as e:
        log.error(f"杀手动作执行错误: {e}")


def killer_fixed_act_process():
    """进程版本的杀手固定动作函数"""
    # 获取当前杀手
    killer_lst = shared_args.get('select_killer_lst', [])
    if not killer_lst:
        return

    # 防止下标越界
    killer_num = len(killer_lst)
    index = shared_state.get('index', 0)
    if ge(index - 1, 0):
        killer_num = index - 1
    else:
        killer_num -= 1

    try:
        # 检查是否使用自定义命令
        if shared_args.get('cb_customcommand', False):
            # 这里需要特殊处理自定义命令
            cmd_queue.put(("CUSTOM_COMMAND", killer_lst[killer_num]))
            return

        press_key('w')
        # 技能释放
        press_key('lcontrol')
        if process_safe_delay(4.3):
            pass
        release_key('lcontrol')

        for _ in range(4):
            if check_pause():
                break

            move_time = round(random.uniform(1.5, 5.0), 3)
            # 随机移动
            act_move = random_movement()
            press_key(act_move)
            if process_safe_delay(move_time):
                break
            release_key(act_move)

            veertime = round(random.uniform(0.285, 0.6), 3)
            # 随机转向
            act_direction = random_direction()
            press_key(act_direction)
            if process_safe_delay(veertime):
                break
            release_key(act_direction)

            press_mouse('right')
            if process_safe_delay(4):
                break
            release_mouse('right')
            if process_safe_delay(0.3):
                break

        press_mouse()
        if process_safe_delay(2):
            pass
        release_mouse()
        release_key('w')

    except IndexError:
        log.error(f"下标越界···{killer_num}")
    except Exception as e:
        log.error(f"杀手固定动作执行错误: {e}")


def action_process():
    """进程版本的动作函数"""
    log.info("动作进程已启动")
    # 获取配置
    rb_survivor = shared_args.get('rb_survivor', False)
    rb_fixed_mode = shared_args.get('rb_fixed_mode', False)
    rb_random_mode = shared_args.get('rb_random_mode', False)
    rb_killer = shared_args.get('rb_killer', False)

    while not shared_state['stop_action'] and not stop_event.is_set():
        if check_pause():
            break

        # 根据角色类型执行相应的动作
        if rb_survivor:
            survivor_action_process()
        elif rb_fixed_mode and rb_killer:
            killer_fixed_act_process()
        elif rb_random_mode and rb_killer:
            killer_action_process()

        # 动作间隔
        if process_safe_delay(0.5):
            break

    log.info("动作进程已停止")


def hall_tip_process():
    """进程版本的大厅提示函数"""
    log.info("大厅提示进程已启动")

    # 导入必要的函数
    from Utils.process_ocr import readyhall_process

    while not stop_event.is_set():
        if check_pause():
            break

        if readyhall_process():
            for _ in range(3):
                if stop_event.is_set():
                    break

                if check_pause():
                    break

                py.press('space')
                py.hotkey('ctrl', 'a')
                py.press('delete')
                input_str = shared_args.get('人类发送消息', 'AFK')
                if is_edcs_only(input_str):
                    py.typewrite(input_str)
                else:
                    input_cn = ProcessInputChinese()
                    input_cn.press_codes_with_alt(input_str, 'gbk')
                py.press('enter')

                if process_safe_delay(15):
                    break
        else:
            # 不在准备大厅时，短暂延时后再次检查
            if process_safe_delay(1):
                break

    log.info("大厅提示进程已停止")
