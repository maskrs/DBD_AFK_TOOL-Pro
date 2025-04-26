"""
进程控制模块 - 用于挂起和恢复进程
"""
import win32process
import win32api
import win32con
import logging
import time
import multiprocessing as mp
from typing import Optional

# 创建日志记录器
log = logging.getLogger(__name__)

def suspend_process(process: mp.Process) -> bool:
    """挂起进程

    Args:
        process: 要挂起的进程对象

    Returns:
        bool: 操作是否成功
    """
    if not process or not process.is_alive():
        log.warning("无法挂起进程：进程不存在或已停止")
        return False

    try:
        # 获取进程ID
        pid = process.pid

        # 打开进程
        handle = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS,
            False,
            pid
        )

        # 获取进程中的所有线程
        threads = win32process.EnumProcessThreads(handle)

        # 挂起所有线程
        for thread_id in threads:
            thread_handle = win32api.OpenThread(
                win32con.THREAD_SUSPEND_RESUME,
                False,
                thread_id
            )
            win32process.SuspendThread(thread_handle)
            win32api.CloseHandle(thread_handle)

        win32api.CloseHandle(handle)
        log.debug(f"成功挂起进程 PID: {pid}")
        return True

    except Exception as e:
        log.error(f"挂起进程时发生错误: {e}")
        return False

def resume_process(process: mp.Process) -> bool:
    """恢复进程

    Args:
        process: 要恢复的进程对象

    Returns:
        bool: 操作是否成功
    """
    if not process or not process.is_alive():
        log.warning("无法恢复进程：进程不存在或已停止")
        return False

    try:
        # 获取进程ID
        pid = process.pid

        # 打开进程
        handle = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS,
            False,
            pid
        )

        # 获取进程中的所有线程
        threads = win32process.EnumProcessThreads(handle)

        # 恢复所有线程
        for thread_id in threads:
            thread_handle = win32api.OpenThread(
                win32con.THREAD_SUSPEND_RESUME,
                False,
                thread_id
            )
            win32process.ResumeThread(thread_handle)
            win32api.CloseHandle(thread_handle)

        win32api.CloseHandle(handle)
        log.debug(f"成功恢复进程 PID: {pid}")
        return True

    except Exception as e:
        log.error(f"恢复进程时发生错误: {e}")
        return False

def safe_suspend_process(process: mp.Process, signal_queue: Optional[mp.Queue] = None) -> bool:
    """安全地挂起进程，先发送信号让进程进入安全状态

    Args:
        process: 要挂起的进程对象
        signal_queue: 可选的信号队列，用于发送准备挂起的信号

    Returns:
        bool: 操作是否成功
    """
    if not process or not process.is_alive():
        return False

    # 如果提供了信号队列，发送准备挂起的信号
    if signal_queue:
        try:
            # 发送准备挂起信号，同时请求保存按键状态
            signal_queue.put(("PREPARE_SUSPEND", {"save_key_states": True}), block=False)
            # 给进程一点时间来处理信号
            time.sleep(0.1)
        except Exception as e:
            log.warning(f"发送准备挂起信号失败: {e}")

    # 挂起进程
    return suspend_process(process)

def get_process_threads(process: mp.Process) -> list:
    """获取进程的所有线程ID

    Args:
        process: 进程对象

    Returns:
        list: 线程ID列表
    """
    if not process or not process.is_alive():
        return []

    try:
        # 获取进程ID
        pid = process.pid

        # 打开进程
        handle = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS,
            False,
            pid
        )

        # 获取进程中的所有线程
        threads = win32process.EnumProcessThreads(handle)

        win32api.CloseHandle(handle)
        return threads

    except Exception as e:
        log.error(f"获取进程线程时发生错误: {e}")
        return []

def is_process_suspended(process: mp.Process) -> bool:
    """检查进程是否被挂起

    Args:
        process: 进程对象

    Returns:
        bool: 进程是否被挂起
    """
    if not process or not process.is_alive():
        return False

    try:
        # 获取进程ID
        pid = process.pid

        # 打开进程
        handle = win32api.OpenProcess(
            win32con.PROCESS_ALL_ACCESS,
            False,
            pid
        )

        # 获取进程中的所有线程
        threads = win32process.EnumProcessThreads(handle)

        # 检查第一个线程的挂起计数
        if threads:
            thread_handle = win32api.OpenThread(
                win32con.THREAD_SUSPEND_RESUME | win32con.THREAD_QUERY_INFORMATION,
                False,
                threads[0]
            )
            # 尝试挂起线程并获取之前的挂起计数
            suspend_count = win32process.SuspendThread(thread_handle)
            # 立即恢复线程
            win32process.ResumeThread(thread_handle)
            win32api.CloseHandle(thread_handle)

            win32api.CloseHandle(handle)
            # 如果挂起计数大于0，说明线程已经被挂起
            return suspend_count > 0

        win32api.CloseHandle(handle)
        return False

    except Exception as e:
        log.error(f"检查进程挂起状态时发生错误: {e}")
        return False
