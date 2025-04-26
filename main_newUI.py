from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QGuiApplication, Qt
from UI.windows.main_window import MainWindow
from Utils.sentry_manager import SentryManager
from Utils.config_manager import config_manager
import os
import sys
import logging
import sentry_sdk


def format_geometry(rect):
    """Format a geometry as a X11 geometry specification"""
    return "{}x{}{:+d}{:+d}".format(rect.width(), rect.height(), rect.x(), rect.y())

def screen_info(widget):
    """Format information on the screens"""
    result = ""  # Initialize result variable
    for screen in QGuiApplication.screens():
        dpi = int(screen.logicalDotsPerInchX())
        dpr = screen.devicePixelRatio()
        resolution = "{}x{}".format(screen.size().width(), screen.size().height())
        result += '"{}" {} DPI={}, DPR={}'.format(screen.name(), resolution, dpi, dpr)
    return result

def setup_logging():
    """配置日志系统"""
    # 创建日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 日志文件路径
    log_path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "debug_data.log")

    # 检查日志文件大小，如果超过10MB则清空
    try:
        if os.path.exists(log_path) and os.path.getsize(log_path) > 10 * 1024 * 1024:  # 10MB
            # 清空日志文件
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"Log file cleared at {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None, None))} because it exceeded 10MB\n")
    except Exception as e:
        print(f"Failed to check or clear log file: {str(e)}")

    # 创建文件处理器
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    # 设置 Qt 相关日志级别为 WARNING
    logging.getLogger('PySide6').setLevel(logging.WARNING)

    # 设置全局异常处理
    sys.excepthook = global_exception_handler

def global_exception_handler(exctype, value, traceback):
    """全局异常处理函数"""
    logging.error("未捕获的异常", exc_info=(exctype, value, traceback))

    # 将异常发送到Sentry
    try:
        sentry_sdk.capture_exception(value)
    except Exception as e:
        logging.error(f"Sentry捕获异常失败: {str(e)}")

if __name__ == "__main__":
    # 设置日志系统
    setup_logging()

    # 创建日志记录器
    logger = logging.getLogger(__name__)
    logger.debug("应用程序启动")

    # # 初始化Sentry
    # try:
    #     # 创建Sentry管理器
    #     sentry_manager = SentryManager(config_manager)

    #     # 初始化Sentry
    #     version = "V2.8.2"  # 应用程序版本
    #     sentry_manager.initialize(
    #         "https://cedb96910714cd07d682f1fead495553@o4507677044506624.ingest.de.sentry.io/4507677065347152",
    #         "https://c4ccce3bbe650bd9b3c897084d11c2d2@o4507677203038208.ingest.de.sentry.io/4507677302259792",
    #         version
    #     )

    #     logger.info("Sentry初始化成功")
    # except Exception as e:
    #     logger.error(f"Sentry初始化失败: {str(e)}")

    app = QApplication(sys.argv)
    # 设置应用信息
    app.setApplicationName("DBD AFK Tool Pro")
    app.setOrganizationName("DBD")

    # 设置图标
    icon_path = os.path.join(
        os.path.dirname(os.path.realpath(sys.argv[0])),
        "picture",
        "dbdwindow.ico"
    )
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    try:
        main_window = MainWindow()
        main_window.show()
        logger.debug("主窗口已显示")
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("程序运行时发生错误")
        # 直接捕获并发送到Sentry
        try:
            sentry_sdk.capture_exception(e)
        except Exception as se:
            logger.error(f"Sentry捕获异常失败: {str(se)}")
        sys.exit(1)
