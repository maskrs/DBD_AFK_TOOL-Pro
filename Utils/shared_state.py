"""
共享状态管理模块 - 用于多进程间通信
"""
import multiprocessing as mp
from multiprocessing import Manager, Event, Queue
from queue import Empty
import time
import logging

# 创建进程管理器
manager = Manager()

# 共享状态字典
shared_state = manager.dict({
    'begin_state': False,
    'pause': False,
    'stop_space': False,
    'stop_action': False,
    'index': 0,
    'game_stage': "",
})

# 共享事件
pause_event = Event()
pause_event.set()  # 初始状态为运行
stop_event = Event()

# 命令队列
cmd_queue = Queue()
result_queue = Queue()

# 共享的self_defined_args
shared_args = manager.dict()

def init_shared_args(original_args):
    """初始化共享参数字典"""
    for key, value in original_args.items():
        shared_args[key] = value

def get_shared_arg(key, default=None):
    """获取共享参数"""
    return shared_args.get(key, default)

def update_shared_arg(key, value):
    """更新共享参数"""
    shared_args[key] = value

def check_pause():
    """检查是否暂停（兼容旧代码）

    注意：此函数已不再使用检查点机制，而是使用进程挂起/恢复功能
    """
    # 只检查停止事件
    return stop_event.is_set()

def process_safe_delay(seconds):
    """进程安全的延时函数（兼容旧代码）

    注意：此函数已不再使用检查点机制，而是使用进程挂起/恢复功能
    """
    # 简单延时，不再检查暂停状态
    time.sleep(seconds)
    # 只检查停止事件
    return stop_event.is_set()
