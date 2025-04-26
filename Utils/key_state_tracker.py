"""
按键状态跟踪模块 - 用于记录和恢复按键状态
"""
import logging

# 创建日志记录器
log = logging.getLogger(__name__)

# 当前按下的按键状态
_pressed_keys = set()
_pressed_mouse_buttons = set()

def press_key(key):
    """记录按键按下"""
    _pressed_keys.add(key)
    
def release_key(key):
    """记录按键释放"""
    if key in _pressed_keys:
        _pressed_keys.remove(key)
    
def press_mouse(button='left'):
    """记录鼠标按下"""
    _pressed_mouse_buttons.add(button)
    
def release_mouse(button='left'):
    """记录鼠标释放"""
    if button in _pressed_mouse_buttons:
        _pressed_mouse_buttons.remove(button)

def get_pressed_keys():
    """获取当前按下的所有按键"""
    return _pressed_keys.copy()

def get_pressed_mouse_buttons():
    """获取当前按下的所有鼠标按钮"""
    return _pressed_mouse_buttons.copy()

def clear_all_states():
    """清除所有按键和鼠标状态"""
    _pressed_keys.clear()
    _pressed_mouse_buttons.clear()

def save_key_states():
    """保存当前按键状态"""
    return {
        'keys': get_pressed_keys(),
        'mouse': get_pressed_mouse_buttons()
    }

def restore_key_states(states, game_operate_module):
    """恢复按键状态
    
    Args:
        states: 保存的状态字典
        game_operate_module: GameOperate模块，包含press_key等函数
    """
    if not states:
        return
    
    # 恢复按键状态
    for key in states['keys']:
        log.debug(f"恢复按键状态: 按下 {key}")
        game_operate_module.press_key(key)
    
    # 恢复鼠标状态
    for button in states['mouse']:
        log.debug(f"恢复鼠标状态: 按下 {button}")
        game_operate_module.press_mouse(button)
