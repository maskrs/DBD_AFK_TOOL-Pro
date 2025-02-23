from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QPushButton, QLabel, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from UI.components.modern_button import ModernButton
from UI.components.modern_card import ModernCard
from UI.components.notification import NotificationManager
from UI.components.radio_group import ModernRadioGroup
from UI.components.drawer import Drawer
from UI.pages.base_page import BasePage
from Utils.config_manager import config_manager
from UI.resources import resources_rc

class HomePage(BasePage):
    """主页"""
    
    def __init__(self, theme_manager, parent=None):
        self.theme_manager = theme_manager
        self.theme_btn = None
        self.notification_manager = NotificationManager()
        super().__init__(parent)
        # 连接主题管理器的信号
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        # 从配置加载主题状态
        config_manager.load_configs()  # 确保加载最新配置
        is_dark = str(self.get_config_value('THEME', 'dark_mode')).lower() == 'true'
        if is_dark != self.theme_manager._dark_mode:  # 如果当前状态与配置不一致，则切换
            print("切换主题模式")
            self.theme_manager.toggleTheme()

    def _setup_ui(self):
        """创建UI"""
        # 主布局已由基类创建，直接使用 self._layout
        self._layout.setSpacing(20)
        self._layout.setContentsMargins(20, 10, 20, 10)
        
        # 顶部布局
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignRight)
        
        # 主题切换按钮
        self.theme_btn = QPushButton(self)
        self.theme_btn.setFixedSize(32, 32)  # 设置固定大小
        self.theme_btn.clicked.connect(self.theme_manager.toggleTheme)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 16px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 0.1);
            }
        """)
        self._update_theme_icon()  # 初始化图标
        top_layout.addWidget(self.theme_btn)
        
        # 创建四个卡片
        card_select_camp = ModernCard("选择阵营", self)
        card_select_camp.set_content_direction(True)
        self._setup_camp_card(card_select_camp)
        
        card_select_action = ModernCard("选择行为", self)
        card_select_action.set_content_direction(True)
        self._setup_action_card(card_select_action)
        
        card_select_role = ModernCard("选择角色", self)
        card_select_role.set_content_direction(True)
        card_select_role.set_content_container_width(125)
        self.drawer_select_character = Drawer(self)
        self._setup_role_card(card_select_role)
        
        # 创建网格布局
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(0, 0, 0, 0)  # 移除网格布局的外边距
        
        # 创建运行信息卡片和按钮的布局
        card_run_info = ModernCard("运行信息", self)
        card_run_info.setContentsMargins(0, 0, 0, 0)  # 移除卡片的外边距
        self._setup_info_card(card_run_info)
        
        # 创建按钮的垂直布局
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # 设置左对齐
        button_layout.setContentsMargins(10, 0, 0, 0)  # 只添加左侧内边距
        
        # 添加三个按钮到垂直布局
        btn_start = ModernButton(self, True)
        btn_start.setText("开始")
        btn_start.setMinimumSize(80, 30)
        btn_start.clicked.connect(self._show_notification)
        btn_stop = ModernButton(self)
        btn_stop.setText("停止")
        btn_stop.setMinimumSize(80, 30)
        btn_stop.clicked.connect(self._show_notification)
        btn_pause = ModernButton(self)
        btn_pause.setText("暂停")
        btn_pause.setMinimumSize(80, 30)
        btn_pause.clicked.connect(self._show_notification)
        
        button_layout.addWidget(btn_start)
        button_layout.addWidget(btn_stop)
        button_layout.addWidget(btn_pause)
        
        # 将卡片和按钮布局添加到网格布局
        grid_layout.addWidget(card_run_info, 0, 0)
        grid_layout.addLayout(button_layout, 0, 1)
        grid_layout.setColumnStretch(0, 2)  # 让卡片占据更多空间
        grid_layout.setColumnStretch(1, 1)  # 按钮占据较少空间

        # 将所有布局和部件添加到主布局
        self._layout.addLayout(top_layout)
        self._layout.addWidget(card_select_camp)
        self._layout.addWidget(card_select_action)
        self._layout.addWidget(card_select_role)
        self._layout.addLayout(grid_layout)
        self._layout.addStretch(1)  # 添加弹性空间
        self._layout.addSpacing(10)  # 底部留出一些间距

    def _setup_camp_card(self, card: ModernCard):
        """设置阵营选择卡片"""
        # 创建单选按钮组
        camp_group = ModernRadioGroup(horizontal=True, parent=self)
        
        # 添加选项
        camp_group.add_option(1, "逃生者")
        camp_group.add_option(2, "杀手")
        
        # 从配置加载状态
        if self.get_config_value('CPCI', 'rb_survivor'):
            camp_group.set_selected(1)
        elif self.get_config_value('CPCI', 'rb_killer'):
            camp_group.set_selected(2)
            
        # 连接信号
        camp_group.selectionChanged.connect(self._on_camp_changed)
        
        # 添加到卡片
        card.set_content(camp_group)
        
    def _setup_action_card(self, card: ModernCard):
        """设置行为选择卡片"""
        # 创建单选按钮组
        action_group = ModernRadioGroup(horizontal=True, parent=self)
        
        # 添加选项
        action_group.add_option(1, "血点模式")
        action_group.add_option(2, "裂隙模式")
        
        # 从配置加载状态
        if self.get_config_value('CPCI', 'rb_fixed_mode'):
            action_group.set_selected(1)
        elif self.get_config_value('CPCI', 'rb_random_mode'):
            action_group.set_selected(2)
            
        # 连接信号
        action_group.selectionChanged.connect(self._on_action_changed)
        
        # 添加到卡片
        card.set_content(action_group)
        
    def _setup_role_card(self, card: ModernCard):
        """设置角色选择卡片"""
        
        # 设置标题和内容的间距
        card.set_title_content_spacing(0)  # 增加到20像素
        
        # 创建容器widget和布局来实现居中
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignCenter)  # 设置居中对齐
        
        btn_select_character = ModernButton(self, True)
        btn_select_character.set_color("#423A8C")
        btn_select_character.setText("选择角色")
        btn_select_character.setMaximumSize(100, 30)
        btn_select_character.clicked.connect(self.drawer_select_character.show_drawer)
        
        # 将按钮添加到容器布局
        container_layout.addWidget(btn_select_character)
        
        # 添加抽屉内容
        title_label = QLabel("选择角色")
        title_label.setObjectName("drawer_title")
        title_label.setStyleSheet("""
            QLabel#drawer_title {
                font-size: 20px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        self.drawer_select_character.add_widget(title_label)
        
        # 添加一些示例角色选项
        role_group = ModernRadioGroup(horizontal=False, parent=self)
        role_group.add_option(1, "幸存者 - 米凯拉")
        role_group.add_option(2, "幸存者 - 克劳黛特")
        role_group.add_option(3, "幸存者 - 杰克")
        role_group.add_option(4, "幸存者 - 梅格")
        
        self.drawer_select_character.add_widget(role_group)
        
        # 添加容器到卡片（而不是直接添加按钮）
        card.set_content(container)
        
    def _setup_info_card(self, card: ModernCard):
        """设置运行信息卡片"""
        # TODO: 添加运行状态信息显示
        pass
        
    def _on_camp_changed(self, option_id: int, text: str):
        """阵营选择改变"""
        # 只更新内存中的配置
        self.save_config_value('CPCI', 'rb_survivor', option_id == 1)
        self.save_config_value('CPCI', 'rb_killer', option_id == 2)
        
    def _on_action_changed(self, option_id: int, text: str):
        """行为模式选择改变"""
        # 只更新内存中的配置
        self.save_config_value('CPCI', 'rb_fixed_mode', option_id == 1)
        self.save_config_value('CPCI', 'rb_random_mode', option_id == 2)

    def _on_theme_changed(self):
        """主题改变时更新图标"""
        self._update_theme_icon()
        # 保存主题状态到配置
        self.save_config_value('THEME', 'dark_mode', self.theme_manager._dark_mode)
        # 立即保存配置到文件
        config_manager.save_configs()
        
    def _update_theme_icon(self):
        """根据当前主题更新图标"""
        if self.theme_manager._dark_mode:
            self.theme_btn.setIcon(QIcon(":/resources/light_mode.svg"))
        else:
            self.theme_btn.setIcon(QIcon(":/resources/dark_mode.svg"))

    def _show_notification(self):
        """显示通知"""
        source = self.sender().text()
        if source == "开始":
            # 保存所有配置
            config_manager.save_configs()
            self.notification_manager.showNotification("脚本已启动！正在运行中···", "success", source=source)
        elif source == "停止":
            self.notification_manager.showNotification("脚本已停止！", "success", source=source)
        elif source == "暂停":
            self.notification_manager.showNotification("脚本已暂停！", "success", source=source)
        


        
