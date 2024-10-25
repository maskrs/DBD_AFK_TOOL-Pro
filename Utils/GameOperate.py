#  -*- This file contains some functions for game operation -- key. -*-

import random
import time
from Utils.background_operation import key_down, key_up, mouse_down, mouse_up


def press_key(key) -> None:
    """按下按键
    :param key: 按键"""
    key_down(key)


def release_key(key) -> None:
    """释放按键
    :param key: 按键"""
    key_up(key)


def press_mosue(mouse_button='左键') -> None:
    """按下鼠标
    :param mouse_button: 鼠标按键，'left' 或 'right'"""
    button = ''
    if mouse_button == '左键' or mouse_button == 'left':
        button = 'mouse_left'
    elif mouse_button == '右键' or mouse_button == 'right':
        button = 'mouse_right'
    elif mouse_button == '中键' or mouse_button == 'middle':
        button = "mouse_middle"
    mouse_down(button)


def release_mouse(mouse_button='左键') -> None:
    """释放鼠标
    :param mouse_button: 鼠标按键，'left' 或 'right'"""
    button = ''
    if mouse_button == '左键' or mouse_button == 'left':
        button = 'mouse_left'
    elif mouse_button == '右键' or mouse_button == 'right':
        button = 'mouse_right'
    elif mouse_button == '中键' or mouse_button == 'middle':
        button = "mouse_middle"
    mouse_up(button)


def delay(seconds) -> None:
    """延时
    :param seconds: 秒数"""
    time.sleep(seconds)


def random_movement(weights=None) -> str:
    """
    随机移动方向，根据给定的权重返回一个键。

    :param weights: 一个字典，键是 'w', 'a', 's', 'd'，值是相应键的权重。
                    eg: {'w': 2, 'd': 1, 'a': 1, 's': 1}
    """
    # 使用 random.choices 根据权重选择方向
    if weights is None:
        weights = {'w': 2, 'a': 1, 's': 1, 'd': 1}

    direction = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    return direction


def random_direction(weights=None) -> str:
    """
    随机转向方向，根据提供的权重字典选择。

    :param weights: 一个字典，键是转向键（如 'left', 'right'），值是相应键的权重。
                               eg: {'left': 1, 'right': 1}
    """
    if weights is None:
        weights = {'left': 1, 'right': 1}

    # 使用 random.choices 根据权重选择方向
    direction = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
    return direction


def random_movetime(min: float = 1.1, max: float = 2.0) -> float:
    """随机移动时间
    :param min: 浮点数，最小时间
    :param max: 浮点数，最大时间
    :return: float"""
    rn = round(random.uniform(min, max), 3)
    return rn


def random_veertime(min: float = 0.275, max: float = 0.4) -> float:
    """随机转向时间
    :param min: 浮点数，最小时间
    :param max: 浮点数，最大时间
    :return: float"""
    rn = round(random.uniform(min, max), 3)
    return rn


def random_move(move_time: float) -> None:
    """随机移动动作
    :param move_time: 行走时间"""
    act_move = random_movement()
    key_down(act_move)
    time.sleep(move_time)
    key_up(act_move)


def random_veer(veer_time: float) -> None:
    """随机转向动作
    :param veer_time: 旋转时间"""
    act_direction = random_direction()
    key_down(act_direction)
    time.sleep(veer_time)
    key_up(act_direction)


def killer_ctrl(skill_key: str = 'lcontrol', skill_time: float = 4.3) -> None:
    """杀手ctrl技能释放
    :param skill_time: 技能释放时间
    :param skill_key: 释放技能的按键，默认 'lcontrol'"""
    key_down(skill_key)
    time.sleep(skill_time)
    key_up(skill_key)


def killer_skillclick(skill_key: str = 'lcontrol') -> None:
    """杀手右键+左键技能释放
    :param skill_key: 释放技能的按键，默认 'lcontrol'"""
    mouse_down("mouse_right")
    time.sleep(3)
    mouse_down()
    mouse_up()
    mouse_up("mouse_right")
    time.sleep(2)
    key_down(skill_key)
    key_up(skill_key)


def killer_skill(skill_key: str = 'lcontrol') -> None:
    """杀手右键技能释放
    :param skill_key: 释放技能的按键，默认 'lcontrol'"""
    mouse_down("mouse_right")
    time.sleep(3)
    key_down(skill_key)
    key_up(skill_key)
    mouse_up("mouse_right")
