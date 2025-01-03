from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QGuiApplication, Qt
from UI.windows.main_window import MainWindow
import os
import sys
import logging


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
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # 设置 Qt 相关日志级别为 WARNING
    logging.getLogger('PySide6').setLevel(logging.WARNING)

if __name__ == "__main__":
    # 设置日志系统
    setup_logging()
    app = QApplication(sys.argv)
    # 设置应用信息
    app.setApplicationName("DBD AFK Tool Pro")
    app.setOrganizationName("DBD")
    # 创建日志记录器
    logger = logging.getLogger(__name__)
    logger.debug("应用程序启动")
    
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
        sys.exit(1)
