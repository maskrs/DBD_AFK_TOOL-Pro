"""
配置管理器模块 - 处理应用程序设置和持久化
"""
import json
import os
from typing import Any, Dict
from threading import Lock
from configparser import ConfigParser

class ConfigManager:
    """线程安全的配置管理器"""
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            # 配置文件路径
            self.cfg_path = os.path.join(self.base_dir, "cfg.cfg")
            self.sdargs_path = os.path.join(self.base_dir, "SDargs.json")
            self.custom_killer_path = os.path.join(self.base_dir, "custom_killer.txt")
            self.custom_command_path = os.path.join(self.base_dir, "custom_command.txt")

            # OCR相关路径
            self.check_path = os.path.join(self.base_dir, "tesseract-ocr")
            self.ocr_path = os.path.join(self.base_dir, "tesseract-ocr", "tesseract.exe")
            self.tessdata_prefix = os.path.join(self.base_dir, "tesseract-ocr", "tessdata")

            # 日志路径
            self.log_path = os.path.join(self.base_dir, "debug_data.log")

            # 配置数据
            self._config = ConfigParser()
            self._user_config = {}
            self._ui_config = self._get_default_ui_config()

            # 确保配置文件存在
            if not os.path.exists(self.cfg_path):
                # 创建默认配置
                for section, values in self._ui_config.items():
                    if not self._config.has_section(section):
                        self._config.add_section(section)
                    for key, value in values.items():
                        self._config.set(section, key, str(value))
                # 保存默认配置
                with open(self.cfg_path, 'w', encoding='utf-8') as f:
                    self._config.write(f)

            # 加载配置
            self.load_configs()

    def load_configs(self):
        """加载所有配置文件"""
        with self._lock:
            # 加载系统配置
            if os.path.exists(self.cfg_path):
                self._config.read(self.cfg_path, encoding='utf-8')
                # 从配置文件加载到UI配置字典
                for section in ['CPCI', 'SEKI', 'CUCOM', 'UPDATE', 'CUSSEC', 'PIV', 'THEME']:
                    if self._config.has_section(section):
                        if section not in self._ui_config:
                            self._ui_config[section] = {}
                        for key, value in self._config.items(section):
                            # 特殊处理的配置项
                            if section == 'PIV' and key == 'piv_key':
                                # PIV_KEY 保持原始字符串值
                                self._ui_config[section][key.upper()] = value
                            elif section == 'THEME' and key in ['accent_color_r', 'accent_color_g', 'accent_color_b']:
                                # 强调色RGB值转换为整数
                                try:
                                    self._ui_config[section][key] = int(value)
                                except ValueError:
                                    # 如果转换失败，使用默认值
                                    default_values = {'accent_color_r': 52, 'accent_color_g': 152, 'accent_color_b': 219}
                                    self._ui_config[section][key] = default_values[key]
                            elif section == 'THEME' and key == 'auto_accent_color':
                                # auto_accent_color 转换为布尔值
                                try:
                                    self._ui_config[section][key] = self._config.getboolean(section, key)
                                except ValueError:
                                    self._ui_config[section][key] = True  # 默认为自动模式
                            else:
                                # 其他转换为布尔值
                                try:
                                    self._ui_config[section][key] = self._config.getboolean(section, key)
                                except ValueError:
                                    self._ui_config[section][key] = False

            # 加载用户自定义参数
            if os.path.exists(self.sdargs_path):
                with open(self.sdargs_path, 'r', encoding='utf-8') as f:
                    self._user_config = json.load(f)
            else:
                self._user_config = self._get_default_user_config()

    def save_configs(self):
        """保存所有配置文件"""
        with self._lock:
            # 保存系统配置
            for section, components in self._ui_config.items():
                if not self._config.has_section(section):
                    self._config.add_section(section)
                for key, value in components.items():
                    # 特殊处理的配置项
                    if section == 'PIV' and key == 'PIV_KEY':
                        # PIV_KEY 保持原始值
                        self._config.set(section, key.lower(), str(value))
                    elif section == 'THEME' and key in ['accent_color_r', 'accent_color_g', 'accent_color_b']:
                        # 强调色RGB值保持数字
                        self._config.set(section, key, str(int(value)))
                    elif section == 'THEME' and key == 'auto_accent_color':
                        # auto_accent_color 保持布尔值
                        self._config.set(section, key, str(bool(value)).lower())
                    else:
                        # 其他转换为布尔值
                        self._config.set(section, key, str(bool(value)).lower())

            # 保存到文件
            with open(self.cfg_path, 'w', encoding='utf-8') as f:
                self._config.write(f)

            # 保存用户自定义参数
            with open(self.sdargs_path, 'w', encoding='utf-8') as f:
                json.dump(self._user_config, f, indent=4, ensure_ascii=False)

    def get_config_value(self, section, key, default=None):
        """获取配置值"""
        with self._lock:
            return self._ui_config.get(section, {}).get(key, default)

    def save_config_value(self, section, key, value):
        """保存配置值"""
        with self._lock:
            if section not in self._ui_config:
                self._ui_config[section] = {}
            self._ui_config[section][key] = value
            self.update_ui_states({section: {key: value}})

    def get_ui_config(self) -> Dict[str, Dict[str, Any]]:
        """获取UI配置"""
        with self._lock:
            return self._ui_config

    def update_ui_states(self, ui_states: Dict[str, Dict[str, Any]]):
        """从UI组件更新UI状态"""
        with self._lock:
            for section, components in ui_states.items():
                if section in self._ui_config:
                    self._ui_config[section].update(components)
                    # 同时更新ConfigParser中的值
                    if not self._config.has_section(section):
                        self._config.add_section(section)
                    for key, value in components.items():
                        # 特殊处理的配置项
                        if section == 'PIV' and key == 'PIV_KEY':
                            # PIV_KEY 保持原始值
                            self._config.set(section, key.lower(), str(value))
                        elif section == 'THEME' and key in ['accent_color_r', 'accent_color_g', 'accent_color_b']:
                            # 强调色RGB值保持数字
                            self._config.set(section, key, str(int(value)))
                        elif section == 'THEME' and key == 'auto_accent_color':
                            # auto_accent_color 保持布尔值
                            self._config.set(section, key, str(bool(value)).lower())
                        else:
                            # 其他转换为布尔值
                            self._config.set(section, key, str(bool(value)).lower())
            self.save_configs()

    def _get_default_ui_config(self) -> Dict[str, Dict[str, Any]]:
        """获取默认UI配置"""
        # CPCI (Control Panel Configuration Items)
        cpci_keys = [
            "rb_survivor", "cb_survivor_do", "rb_killer", "cb_killer_do",
            "rb_fixed_mode", "rb_random_mode"
        ]
        cpci_dict = {key: False for key in cpci_keys}

        # SEKI (Select Window Configuration Items)
        seki_keys = [
            "usefile", "search_fix", "autoselect",
            "rb_pz1", "rb_pz2", "rb_pz3",
        ]
        seki_dict = {key: False for key in seki_keys}

        # CUCOM (Custom Command Configuration)
        cucom_dict = {"cb_customcommand": False}

        # UPDATE Configuration
        update_dict = {
            "cb_autocheck": True,
            "rb_chinese": True,
            "rb_english": False
        }

        # THEME Configuration
        theme_dict = {
            "dark_mode": False,
            "auto_accent_color": True,  # 是否自动获取系统强调色
            "accent_color_r": 52,  # 自定义强调色R通道
            "accent_color_g": 152,  # 自定义强调色G通道
            "accent_color_b": 219   # 自定义强调色B通道
        }

        # CUSSEC (Custom Section Configuration)
        killer_list = [
            "jiage", "dingdang", "dianjv", "hushi", "tuzi", "maishu", "linainai",
            "laoyang", "babu", "fulaidi", "zhuzhu", "xiaochou", "lingmei", "juntuan",
            "wenyi", "guimian", "mowang", "guiwushi", "qiangshou", "sanjiaotou",
            "kumo", "liantiying", "gege", "zhuizhui", "dingzitou", "niaojie",
            "zhenzi", "yingmo", "weishu", "eqishi", "baigu", "jidian", "yixing",
            "qiaji", "ewu", "wuyao", "degula"
        ]
        cussec_dict = {f"cb_{key}": False for key in killer_list}

        # PIV Configuration
        piv_dict = {"PIV_KEY": ''}

        return {
            "CPCI": cpci_dict,
            "SEKI": seki_dict,
            "CUCOM": cucom_dict,
            "UPDATE": update_dict,
            "THEME": theme_dict,
            "CUSSEC": cussec_dict,
            "PIV": piv_dict
        }

    def get_user_config(self, key, default=None):
        """获取用户配置"""
        with self._lock:
            return self._user_config.get(key, default)

    def set_user_config(self, key, value):
        """设置用户配置"""
        with self._lock:
            self._user_config[key] = value
            self.save_configs()

    def _get_default_user_config(self) -> dict:
        """获取默认用户配置"""
        return {
            '赛后发送消息': 'DBD-AFK League',
            '人类发送消息': 'AFK',
            '开始快捷键': ['alt+home'],
            '暂停快捷键': ['f9'],
            '停止快捷键': ['alt+end'],
            '角色选择按钮坐标': [139, 93],
            '第一个角色坐标': [366, 402],
            '搜索输入框坐标': [666, 254],
            '装备配置按钮坐标': [140, 200],
            '装备配置1的坐标': [900, 60],
            '装备配置2的坐标': [950, 60],
            '装备配置3的坐标': [1000, 60],
            '匹配阶段的识别范围': [1446, 771, 1920, 1080],
            '匹配大厅二值化阈值': [120, 130, 0],
            '匹配大厅识别关键字': ["开始游戏", "PLAY"],
            '开始游戏按钮的坐标': [1742, 931],
            '准备阶段的识别范围': [1446, 771, 1920, 1080],
            '准备房间二值化阈值': [120, 130, 0],
            '准备大厅识别关键字': ["准备就绪", "READY"],
            '准备就绪按钮的坐标': [1742, 931],
            '结算页的识别范围': [56, 46, 370, 172],
            '结算页二值化阈值': [70, 130, 0],
            '结算页识别关键字': ["比赛", "得分", "你的", "MATCH", "SCORE"],
            '结算页继续按钮坐标': [1761, 1009],
            '结算页每日祭礼的识别范围': [106, 267, 430, 339],
            '结算页每日祭礼二值化阈值': [120, 130, 0],
            '结算页每日祭礼识别关键字': ["每日", "DAILY RITUALS"],
            '结算页祭礼完成坐标': [396, 718, 140, 880],
            '段位重置的识别范围': [192, 194, 426, 291],
            '段位重置二值化阈值': [120, 130, 0],
            '段位重置识别关键字': ["重置", "RESET"],
            '段位重置按钮的坐标': [1468, 843],
            '断线检测的识别范围': [457, 530, 1488, 796],
            '断线检测二值化阈值': [110, 130, 0],
            '断线检测识别关键字': ["好的", "关闭", "CLOSE", "继续", "CONTINUE"],
            '断线确认关键字': ["好", "关", "继", "K", "C"],
            '断线确认偏移量': [0, 0],
            '主界面的每日祭礼识别范围': [441, 255, 666, 343],
            '主页面每日祭礼二值化阈值': [120, 130, 0],
            '主页面每日祭礼识别关键字': ["每日", "DAILY RITUALS"],
            '主页面祭礼关闭坐标': [545, 880],
            '主页面的识别范围': [203, 78, 365, 135],
            '主页面二值化阈值': [120, 130, 0],
            '主页面识别关键字': ["开始", "PLAY"],
            '主页面开始坐标': [320, 100],
            '主页面逃生者坐标': [339, 320],
            '主页面杀手坐标': [328, 224],
            '新内容的识别范围': [548, 4, 1476, 256],
            '新内容二值化阈值': [120, 130, 0],
            '新内容识别关键字': ["新内容", "NEW CONTENT"],
            '新内容关闭坐标': [1413, 992],
            '坐标转换开关': 0,
            'event_rewards': ["-"],
        }


# 全局实例
config_manager = ConfigManager()
