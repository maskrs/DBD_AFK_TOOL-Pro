"""
进程版本的主函数 - 用于多进程实现
"""
import os
import time
import logging
import multiprocessing as mp
import win32gui
from queue import Empty

from Utils.shared_state import (
    shared_state, shared_args, pause_event, stop_event,
    cmd_queue, result_queue, check_pause, process_safe_delay
)
from Utils.Client2ScreenOperate import MouseController
from Utils.GameOperate import press_key, release_key, press_mouse, release_mouse
from Utils.process_functions import (
    autospace_process, action_process, hall_tip_process,
    auto_message_process
)
from Utils.process_ocr import (
    init_ocr, starthall_process, readyhall_process,
    gameover_process, disconnect_check_process
)

# 创建日志记录器
log = logging.getLogger(__name__)

def afk_process_main():
    """多进程版本的afk主函数"""
    # 初始化进程本地变量
    hwnd = win32gui.FindWindow(None, u"DeadByDaylight  ")
    MControl = MouseController(hwnd)

    # 初始化OCR
    init_ocr(hwnd, MControl)

    # 循环计数
    circulate_number = 0

    # 进程对象
    space_process = None
    action_process_obj = None
    hall_tip_process_obj = None

    # 主循环
    log.info("AFk主进程已启动")

    try:
        while not stop_event.is_set():
            # 检查是否有暂停信号
            try:
                # 非阻塞方式检查命令队列
                cmd, data = cmd_queue.get_nowait()
                if cmd == "PREPARE_SUSPEND":
                    # 收到准备挂起信号，进入安全状态
                    log.info("收到准备挂起信号，进入安全状态")

                    # 导入按键状态跟踪模块
                    from Utils.key_state_tracker import save_key_states, clear_all_states

                    # 保存当前按键状态
                    if data and data.get("save_key_states", False):
                        key_states = save_key_states()
                        shared_state['saved_key_states'] = key_states
                        log.debug(f"已保存按键状态: {key_states}")

                    # 释放所有按键和鼠标
                    release_key('w')
                    release_key('lshift')
                    release_key('lcontrol')
                    release_mouse()

                    # 清除按键状态跟踪器中的状态
                    clear_all_states()

                    # 等待一小段时间确保资源释放
                    time.sleep(0.1)
                elif cmd == "RESUME_PROCESS":
                    # 收到恢复进程信号，恢复之前保存的按键状态
                    log.info("收到恢复进程信号，准备恢复按键状态")

                    # 导入按键状态跟踪模块
                    from Utils.key_state_tracker import restore_key_states
                    from Utils.GameOperate import press_key, press_mouse

                    # 恢复之前保存的按键状态
                    saved_states = shared_state.get('saved_key_states')
                    if saved_states:
                        # 创建一个模块对象，包含press_key和press_mouse函数
                        class GameOperateModule:
                            pass

                        game_operate = GameOperateModule()
                        game_operate.press_key = press_key
                        game_operate.press_mouse = press_mouse

                        restore_key_states(saved_states, game_operate)
                        log.debug(f"已恢复按键状态: {saved_states}")

                        # 清除保存的状态
                        shared_state.pop('saved_key_states', None)
            except Empty:
                pass

            # 检查暂停状态
            if check_pause():
                break

            # 匹配阶段
            reconnection = False
            circulate_number += 1
            matching = False
            shared_state['game_stage'] = '匹配'
            log.info(f"第{circulate_number}次脚本循环---进入匹配阶段")

            while not matching and not stop_event.is_set():
                # 检查暂停
                if check_pause():
                    break

                # 判断条件是否成立
                if starthall_process():
                    log.info(f"第{circulate_number}次脚本循环---进入匹配大厅···")

                    # 角色选择逻辑
                    if shared_args.get('rb_killer', False):
                        # 发送角色选择命令
                        cmd_queue.put(("CHARACTER_SELECTION", None))
                        # 等待角色选择完成
                        process_safe_delay(2)

                    # 开始匹配
                    while not matching and not stop_event.is_set():
                        if check_pause():
                            break

                        # 点击开始游戏按钮
                        coords = shared_args.get('开始游戏按钮的坐标', [0, 0])
                        MControl.moveclick(coords[0], coords[1], 1)
                        MControl.moveclick(20, 689, 1, 5)  # 商城上空白

                        # 检查是否已开始匹配
                        if not starthall_process():
                            matching = True
                            shared_state['game_stage'] = ""
                            log.info(f"第{circulate_number}次脚本循环---开始匹配!")

                # 检查断线
                elif disconnect_check_process():
                    # 发送断线重连命令
                    cmd_queue.put(("RECONNECT", None))
                    reconnection = True
                    matching = True
                    shared_state['game_stage'] = ""

                # 短暂延时
                process_safe_delay(0.5)

            # 重连返回值的判断
            if reconnection:
                continue

            # 准备阶段
            ready_room = shared_args.get('cb_debug', False)
            shared_state['game_stage'] = '准备'
            log.info(f"第{circulate_number}次脚本循环---进入准备阶段")

            if ready_room:
                shared_state['game_stage'] = ""

            while not ready_room and not stop_event.is_set():
                # 检查暂停
                if check_pause():
                    break

                if readyhall_process():
                    log.info(f"第{circulate_number}次脚本循环---进入准备大厅···")
                    MControl.moveclick(10, 10, 1)

                    # 点击准备按钮
                    coords = shared_args.get('准备就绪按钮的坐标', [0, 0])
                    MControl.moveclick(coords[0], coords[1], 1)
                    MControl.moveclick(20, 689, 1, 3)  # 商城上空白

                    # 检查是否已准备
                    if not readyhall_process():
                        ready_room = True
                        shared_state['game_stage'] = ""
                        log.info(f"第{circulate_number}次脚本循环---准备完成!")

                # 检查断线
                elif disconnect_check_process():
                    # 发送断线重连命令
                    cmd_queue.put(("RECONNECT", None))
                    reconnection = True
                    ready_room = True
                    shared_state['game_stage'] = ""

                # 短暂延时
                process_safe_delay(0.5)

            # 重连返回值判断
            if reconnection:
                continue

            # 游戏阶段
            if not stop_event.is_set():
                # 创建子进程
                space_process = mp.Process(
                    target=autospace_process,
                    args=(),
                    daemon=True
                )

                action_process_obj = mp.Process(
                    target=action_process,
                    args=(),
                    daemon=True
                )

                # 重置标志
                shared_state['stop_space'] = False
                shared_state['stop_action'] = False

                # 启动进程
                space_process.start()
                action_process_obj.start()

                # 游戏循环
                game = False
                log.info(f"第{circulate_number}次脚本循环---进入对局···")
                shared_state['game_stage'] = '结算'

                while not game and not stop_event.is_set():
                    # 检查暂停
                    if check_pause():
                        break

                    # 检查游戏是否结束
                    if gameover_process():
                        log.info(f"第{circulate_number}次脚本循环---游戏结束···")

                        # 停止子进程
                        shared_state['stop_space'] = True
                        shared_state['stop_action'] = True

                        # 点击操作
                        MControl.moveclick(10, 10, 1, 1)

                        # 判断是否开启留言
                        if (shared_args.get('cb_killer_do', False) and
                            shared_args.get('rb_killer', False)):
                            auto_message_process()

                        # 点击继续按钮
                        coords = shared_args.get('结算页继续按钮坐标', [0, 0])
                        MControl.moveclick(coords[0], coords[1], 0.5, 1)
                        MControl.moveclick(10, 10, 1, 3)  # 避免遮挡

                        # 检查是否已返回大厅
                        if not gameover_process():
                            game = True
                            shared_state['game_stage'] = ""
                            log.info(f"第{circulate_number}次脚本循环---正在返回匹配大厅···\n")
                        elif disconnect_check_process():
                            # 发送断线重连命令
                            cmd_queue.put(("RECONNECT", None))
                            reconnection = True
                            game = True
                            shared_state['game_stage'] = ""

                    # 检查断线
                    elif disconnect_check_process():
                        # 发送断线重连命令
                        cmd_queue.put(("RECONNECT", None))
                        reconnection = True
                        game = True
                        shared_state['game_stage'] = ""

                    # 短暂延时
                    process_safe_delay(0.5)

                # 确保子进程停止
                shared_state['stop_space'] = True
                shared_state['stop_action'] = True

                # 等待进程安全退出
                if space_process and space_process.is_alive():
                    space_process.join(timeout=1)
                    if space_process.is_alive():
                        space_process.terminate()

                if action_process_obj and action_process_obj.is_alive():
                    action_process_obj.join(timeout=1)
                    if action_process_obj.is_alive():
                        action_process_obj.terminate()

            # 重连返回值判断
            if reconnection:
                continue

            # 检查是否需要退出
            if stop_event.is_set():
                break

    except Exception as e:
        log.error(f"AFk主进程异常: {e}")
    finally:
        # 确保所有子进程都已停止
        shared_state['stop_space'] = True
        shared_state['stop_action'] = True

        if space_process and space_process.is_alive():
            space_process.terminate()

        if action_process_obj and action_process_obj.is_alive():
            action_process_obj.terminate()

        if hall_tip_process_obj and hall_tip_process_obj.is_alive():
            hall_tip_process_obj.terminate()

        log.info("AFk主进程已停止")


def start_hall_tip_process():
    """启动大厅提示进程"""
    if shared_args.get('rb_survivor', False) and shared_args.get('cb_survivor_do', False):
        hall_tip_process_obj = mp.Process(
            target=hall_tip_process,
            args=(),
            daemon=True
        )
        hall_tip_process_obj.start()
        return hall_tip_process_obj
    return None
