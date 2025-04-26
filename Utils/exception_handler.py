"""
异常处理模块 - 用于处理全局异常
"""
import logging
import sentry_sdk
from Utils.shared_state import shared_state, stop_event

def global_exception_handler(exctype, value, traceback):
    """全局异常处理函数
    
    Args:
        exctype: 异常类型
        value: 异常值
        traceback: 异常追踪信息
    """
    # 如果是键盘中断异常，尝试安全退出
    if exctype is KeyboardInterrupt:
        logging.info("接收到键盘中断信号，正在安全退出...")
        # 设置停止事件
        stop_event.set()
        # 设置共享状态
        if 'begin_state' in shared_state:
            shared_state['begin_state'] = False
        return
    
    # 记录异常信息
    logging.error("未捕获的异常", exc_info=(exctype, value, traceback))
    
    # 发送异常到Sentry
    try:
        sentry_sdk.capture_exception(value)
    except Exception as e:
        logging.error(f"Sentry捕获异常失败: {e}")
