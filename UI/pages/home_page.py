from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QPushButton, QLabel, QWidget, QVBoxLayout, QButtonGroup, QFrame, QScrollArea
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QIcon, QColor, QPainter, QPen, QBrush, QConicalGradient
from UI.components.modern_dialog import ModernDialog
from UI.components.modern_button import ModernButton
from UI.components.modern_card import ModernCard
from UI.components.modern_notification import NotificationManager
from UI.components.radio_group import ModernRadioGroup
from UI.components.modern_checkbox import ModernCheckBox
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
        # 连接主题管理器的信号，使用延迟连接以避免重复刷新
        self.theme_manager.themeChanged.connect(self._on_theme_changed)
        # 从配置加载主题状态
        config_manager.load_configs()  # 确保加载最新配置

        # 加载暗色模式设置
        is_dark = str(self.get_config_value('THEME', 'dark_mode')).lower() == 'true'
        if is_dark != self.theme_manager._dark_mode:  # 如果当前状态与配置不一致，则切换
            # 静默切换主题，不触发颜色闪烁
            self.theme_manager._dark_mode = is_dark
            self.theme_manager._apply_current_backdrop()
            self._update_theme_icon()

        # 加载强调色设置
        is_auto = str(self.get_config_value('THEME', 'auto_accent_color', 'true')).lower() == 'true'
        if not is_auto:
            # 使用自定义强调色
            try:
                r = int(self.get_config_value('THEME', 'accent_color_r', '52'))
                g = int(self.get_config_value('THEME', 'accent_color_g', '152'))
                b = int(self.get_config_value('THEME', 'accent_color_b', '219'))
                custom_accent = {
                    'red': r,
                    'green': g,
                    'blue': b,
                    'alpha': 255
                }
                self.theme_manager._accent_color = custom_accent
                self.theme_manager.accentColorChanged.emit(custom_accent)
            except Exception as e:
                print(f"加载自定义强调色失败: {e}")

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
        self.theme_btn.clicked.connect(self._toggle_theme)  # 使用自定义切换方法
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
        # 设置抽屉组件的主题管理器
        if hasattr(self, 'theme_manager'):
            self.drawer_select_character.theme_manager = self.theme_manager

        # 从配置中加载抽屉宽度
        drawer_width = int(self.get_config_value('UI', 'drawer_width', 520))
        self.drawer_select_character.set_drawer_width(drawer_width)
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

        # 直接在底部添加强调色选择器
        accent_color_widget = self._create_accent_color_widget()
        self._layout.addWidget(accent_color_widget)

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
        container_layout.setContentsMargins(0, 0, 0, 2)
        container_layout.setAlignment(Qt.AlignCenter)  # 设置居中对齐

        btn_select_character = ModernButton(self, True)
        btn_select_character.setText("选择角色")
        btn_select_character.setMaximumSize(100, 30)
        btn_select_character.clicked.connect(self.drawer_select_character.show_drawer)

        # 将按钮添加到容器布局
        container_layout.addWidget(btn_select_character)

        # 设置抽屉内容
        self._setup_drawer_content()

        # 添加容器到卡片（而不是直接添加按钮）
        card.set_content(container)

    def _setup_drawer_content(self):
        """设置抽屉内容"""
        # 清空现有内容
        for i in reversed(range(self.drawer_select_character.content_layout.count())):
            widget = self.drawer_select_character.content_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setObjectName("drawer_scroll_area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 设置滚动区域样式，考虑主题切换
        is_dark = self.theme_manager.isDarkMode() if hasattr(self, 'theme_manager') else False
        scroll_bar_bg = "#2c2c2c" if is_dark else "#f0f0f0"
        scroll_bar_handle = "#404040" if is_dark else "#c0c0c0"
        scroll_bar_handle_hover = "#4f4f4f" if is_dark else "#a0a0a0"

        scroll_area.setStyleSheet(f"""
            QScrollArea#drawer_scroll_area {{
                border: none;
                background-color: transparent;
            }}

            QScrollBar:vertical {{
                background: {scroll_bar_bg};
                width: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {scroll_bar_handle};
                min-height: 30px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {scroll_bar_handle_hover};
            }}

            QScrollBar::add-line:vertical {{
                height: 0px;
            }}

            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # 创建内容容器
        content_widget = QWidget()
        content_widget.setObjectName("content_widget")  # 设置对象名便于应用样式
        # 设置背景色
        bg_color = "#1e1e1e" if is_dark else "#ffffff"
        content_widget.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px;")
        # 获取设备像素比例，用于计算相对边距
        device_pixel_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 1.0
        base_margin = int(16 * device_pixel_ratio / 1.5)  # 基础边距，考虑DPI缩放
        base_spacing = int(12 * device_pixel_ratio / 1.5)  # 基础间距，考虑DPI缩放

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(base_margin, base_margin, base_margin, base_margin)  # 使用相对边距
        content_layout.setSpacing(base_spacing)  # 使用相对间距

        # ===== 上部分：选项设置 =====
        top_widget = QWidget()
        top_widget.setStyleSheet("background-color: transparent;")
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        # 第一行：从外部文件选择 + 编辑外部文件按钮
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(10)

        # 创建左侧容器来存放复选框
        file_container = QWidget()
        file_container.setStyleSheet("background-color: transparent;")
        file_layout = QHBoxLayout(file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(0)

        # 从外部文件选择复选框
        cb_use_file = ModernCheckBox(self)
        cb_use_file.setText("从外部文件选择")
        cb_use_file.setChecked(self.get_config_value('SEKI', 'usefile', False))
        cb_use_file.toggled.connect(lambda checked: self.save_config_value('SEKI', 'usefile', checked))
        cb_use_file.setMinimumWidth(150)  # 设置最小宽度确保文字能完整显示

        # 设置主题管理器
        if hasattr(self, 'theme_manager'):
            cb_use_file.theme_manager = self.theme_manager

        # 添加复选框到容器
        file_layout.addWidget(cb_use_file)

        # 创建右侧容器来存放按钮
        btn_container = QWidget()
        btn_container.setStyleSheet("background-color: transparent;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        # 编辑外部文件按钮
        btn_edit_external = ModernButton(self)
        btn_edit_external.setText("编辑外部文件")
        # 计算按钮尺寸，考虑DPI缩放
        button_width = max(120, int(120 * device_pixel_ratio / 1.5))
        button_height = max(30, int(30 * device_pixel_ratio / 1.5))
        btn_edit_external.setMinimumSize(button_width, button_height)
        btn_edit_external.clicked.connect(self._on_edit_external_file)

        # 添加按钮到容器
        btn_layout.addWidget(btn_edit_external)

        # 添加容器到第一行布局
        row1.addWidget(file_container)
        row1.addStretch(1)
        row1.addWidget(btn_container)

        # 第二行：搜索框输入乱码 - 使用与第一行相同的模式
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(10)

        # 创建左侧容器来存放复选框
        search_container = QWidget()
        search_container.setStyleSheet("background-color: transparent;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        cb_search_fix = ModernCheckBox(self)
        cb_search_fix.setText("搜索框输入乱码")
        cb_search_fix.setChecked(self.get_config_value('SEKI', 'search_fix', False))
        cb_search_fix.toggled.connect(lambda checked: self.save_config_value('SEKI', 'search_fix', checked))
        cb_search_fix.setMinimumWidth(150)  # 设置最小宽度确保文字能完整显示

        # 设置主题管理器
        if hasattr(self, 'theme_manager'):
            cb_search_fix.theme_manager = self.theme_manager

        # 添加复选框到容器
        search_layout.addWidget(cb_search_fix)

        # 添加容器到第二行布局
        row2.addWidget(search_container)
        row2.addStretch(1)

        # 第三行：自动选择装备配置 + 单选按钮组 - 使用与第一行相同的模式
        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 0, 0, 0)
        row3.setSpacing(10)

        # 创建左侧容器来存放复选框
        auto_equip_container = QWidget()
        auto_equip_container.setStyleSheet("background-color: transparent;")
        auto_equip_layout = QHBoxLayout(auto_equip_container)
        auto_equip_layout.setContentsMargins(0, 0, 0, 0)
        auto_equip_layout.setSpacing(0)

        # 自动选择装备配置复选框
        cb_auto_equip = ModernCheckBox(self)
        cb_auto_equip.setText("自动选择装备配置")
        cb_auto_equip.setChecked(self.get_config_value('SEKI', 'auto_equip', False))
        cb_auto_equip.toggled.connect(lambda checked: self.save_config_value('SEKI', 'auto_equip', checked))
        cb_auto_equip.setMinimumWidth(150)  # 设置最小宽度确保文字能完整显示

        # 设置主题管理器
        if hasattr(self, 'theme_manager'):
            cb_auto_equip.theme_manager = self.theme_manager

        # 添加复选框到容器
        auto_equip_layout.addWidget(cb_auto_equip)

        # 创建右侧容器来存放单选按钮组
        radio_container = QWidget()
        radio_container.setStyleSheet("background-color: transparent;")
        radio_layout = QHBoxLayout(radio_container)
        radio_layout.setContentsMargins(0, 0, 0, 0)
        radio_layout.setSpacing(0)

        # 单选按钮组
        radio_group = ModernRadioGroup(horizontal=True, parent=self)
        radio_group.add_option(1, "1")
        radio_group.add_option(2, "2")
        radio_group.add_option(3, "3")

        # 从配置加载状态
        radio_option = int(self.get_config_value('SEKI', 'radio_option', 1))
        radio_group.set_selected(radio_option)
        radio_group.selectionChanged.connect(lambda option_id, _: self.save_config_value('SEKI', 'radio_option', option_id))

        # 添加单选按钮组到容器
        radio_layout.addWidget(radio_group)

        # 添加容器到第三行布局
        row3.addWidget(auto_equip_container)
        row3.addStretch(1)
        row3.addWidget(radio_container)

        # 添加所有行到上部布局
        top_layout.addLayout(row1)  # 第一行
        top_layout.addLayout(row2)  # 第二行
        top_layout.addLayout(row3)  # 第三行

        # ===== 中部分：反选和全选按钮 =====
        mid_widget = QWidget()
        mid_widget.setStyleSheet("background-color: transparent;")
        mid_layout = QHBoxLayout(mid_widget)
        mid_layout.setContentsMargins(0, 0, 0, 0)
        mid_layout.setSpacing(10)

        # 反选按钮
        btn_invert = ModernButton(self)
        btn_invert.setText("反选")
        # 计算按钮尺寸，考虑DPI缩放
        small_button_width = max(80, int(80 * device_pixel_ratio / 1.5))
        small_button_height = max(30, int(30 * device_pixel_ratio / 1.5))
        btn_invert.setMinimumSize(small_button_width, small_button_height)
        btn_invert.clicked.connect(self._on_invert_selection)

        # 全选按钮
        btn_select_all = ModernButton(self)
        btn_select_all.setText("全选")
        btn_select_all.setMinimumSize(small_button_width, small_button_height)
        btn_select_all.clicked.connect(self._on_select_all)

        # 添加按钮到中部布局
        mid_layout.addWidget(btn_invert)
        mid_layout.addWidget(btn_select_all)
        mid_layout.addStretch(1)

        # ===== 下部分：角色复选框列表 =====
        bottom_widget = QWidget()
        bottom_widget.setStyleSheet("background-color: transparent;")
        bottom_layout = QGridLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)  # 设置适当的间距

        # 角色列表 - 按照图片中的布局排列
        killer_mapping = {
            "cb_jiage": "设陷者",
            "cb_dingdang": "幽灵",
            "cb_dianjv": "农场主",
            "cb_hushi": "护士",
            "cb_tuzi": "女猎手",
            "cb_maishu": "迈克尔·迈尔斯",
            "cb_linainai": "妖巫",
            "cb_laoyang": "医生",
            "cb_babu": "食人魔",
            "cb_fulaidi": "梦魇",
            "cb_zhuzhu": "门徒",
            "cb_xiaochou": "小丑",
            "cb_lingmei": "怨灵",
            "cb_juntuan": "军团",
            "cb_wenyi": "瘟疫",
            "cb_guimian": "鬼面",
            "cb_mowang": "魔王",
            "cb_guiwushi": "鬼武士",
            "cb_qiangshou": "枪手",
            "cb_sanjiaotou": "处刑者",
            "cb_kumo": "枯萎者",
            "cb_liantiying": "连体婴",
            "cb_gege": "骗术师",
            "cb_zhuizhui": "追击者",
            "cb_dingzitou": "钉子头",
            "cb_niaojie": "艺术家",
            "cb_zhenzi": "贞子",
            "cb_yingmo": "影魔",
            "cb_weishu": "操纵者",
            "cb_eqishi": "恶骑士",
            "cb_baigu": "白骨商人",
            "cb_jidian": "奇点",
            "cb_yixing": "异形",
            "cb_qiaji": "好孩子",
            "cb_ewu": "未知恶物",
            "cb_wuyao": "巫妖",
            "cb_degula": "黑暗之主"
        }

        # 存储所有复选框的引用
        self.character_checkboxes = {}

        # 计算每个复选框的最小宽度
        # 获取当前抽屉宽度
        drawer_width = self.drawer_select_character.get_drawer_width() if hasattr(self.drawer_select_character, 'get_drawer_width') else 520
        # 考虑内容边距和列间距
        available_width = drawer_width - 2 * base_margin - 3 * base_spacing  # 可用宽度
        # 计算每列的宽度，根据抽屉宽度动态调整列数
        columns = 4  # 默认为4列
        if drawer_width < 450:  # 窄抽屉
            columns = 3
        elif drawer_width > 700:  # 宽抽屉
            columns = 5

        # 计算每列的宽度
        column_width = max(110, available_width // columns - 5)  # 确保最小宽度为110

        # 按照动态列数布局添加角色复选框
        row, col = 0, 0
        for key, value in killer_mapping.items():
            cb = ModernCheckBox(self)
            cb.setText(value)
            cb.setChecked(self.get_config_value('CUSSEC', key, False))
            cb.toggled.connect(lambda checked, k=key: self.save_config_value('CUSSEC', k, checked))
            # 使用计算出的列宽度
            cb.setMinimumWidth(column_width)

            # 设置主题管理器
            if hasattr(self, 'theme_manager'):
                cb.theme_manager = self.theme_manager

            bottom_layout.addWidget(cb, row, col)
            self.character_checkboxes[key] = cb

            col += 1
            if col >= columns:  # 动态列数
                col = 0
                row += 1

        # ===== 添加分隔线和各部分到主布局 =====
        # 添加上部分
        content_layout.addWidget(top_widget)

        # 添加第一条分隔线
        separator1 = QFrame()
        separator1.setObjectName("drawer_separator1")  # 设置对象名便于样式应用
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setFixedHeight(2)

        # 设置分隔线的初始颜色
        if hasattr(self, 'theme_manager') and self.theme_manager._accent_color:
            self._update_separator_color(separator1)
        else:
            # 默认颜色
            separator1.setStyleSheet("""
                QFrame#drawer_separator1 {
                    background-color: #ff5a5f;
                    border: none;
                    min-height: 2px;
                    max-height: 2px;
                }
            """)

        content_layout.addWidget(separator1)

        # 连接主题变化信号，更新分隔线颜色
        if hasattr(self, 'theme_manager'):
            self.theme_manager.themeChanged.connect(lambda _: self._update_separator_color(separator1))
            self.theme_manager.accentColorChanged.connect(lambda _: self._update_separator_color(separator1))

        # 添加中部分
        content_layout.addWidget(mid_widget)

        # 添加下部分
        content_layout.addWidget(bottom_widget)

        # 添加底部按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        button_layout.setSpacing(10)

        btn_confirm = ModernButton(self, True)
        btn_confirm.setText("确认")
        # 计算确认按钮尺寸，考虑DPI缩放
        confirm_button_width = max(100, int(100 * device_pixel_ratio / 1.5))
        confirm_button_height = max(36, int(36 * device_pixel_ratio / 1.5))
        btn_confirm.setMinimumSize(confirm_button_width, confirm_button_height)
        btn_confirm.clicked.connect(self.drawer_select_character.close_drawer)

        # 添加到底部按钮布局
        button_layout.addStretch(1)
        button_layout.addWidget(btn_confirm)

        # 添加布局到内容布局
        content_layout.addLayout(button_layout)

        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        self.drawer_select_character.add_widget(scroll_area)

        # 修改Drawer类的show_drawer方法，在显示时更新滚动区域样式
        original_show_drawer = self.drawer_select_character.show_drawer

        def custom_show_drawer():
            # 调用原始方法
            original_show_drawer()
            # 更新滚动区域样式
            self._update_scroll_area_style()

        # 替换方法
        self.drawer_select_character.show_drawer = custom_show_drawer

        # 监听抽屉宽度变化，更新内容布局
        if hasattr(self.drawer_select_character, 'set_drawer_width'):
            # 保存原始方法
            original_set_drawer_width = self.drawer_select_character.set_drawer_width

            # 创建新的方法
            def custom_set_drawer_width(width):
                # 调用原始方法
                original_set_drawer_width(width)
                # 更新内容布局
                self._update_drawer_content()

            # 替换方法
            self.drawer_select_character.set_drawer_width = custom_set_drawer_width

    def _update_drawer_content(self):
        """更新抽屉内容布局，在抽屉宽度变化时调用"""
        # 如果没有角色复选框或抽屉组件，则返回
        if not hasattr(self, 'character_checkboxes') or not hasattr(self, 'drawer_select_character'):
            return

        # 获取当前抽屉宽度
        drawer_width = self.drawer_select_character.get_drawer_width()

        # 获取设备像素比例
        device_pixel_ratio = self.devicePixelRatio() if hasattr(self, 'devicePixelRatio') else 1.0
        base_margin = int(16 * device_pixel_ratio / 1.5)  # 基础边距
        base_spacing = int(12 * device_pixel_ratio / 1.5)  # 基础间距

        # 计算可用宽度和列数
        available_width = drawer_width - 2 * base_margin - 3 * base_spacing
        columns = 4  # 默认为4列
        if drawer_width < 450:  # 窄抽屉
            columns = 3
        elif drawer_width > 700:  # 宽抽屉
            columns = 5

        # 计算每列的宽度
        column_width = max(110, available_width // columns - 5)

        # 更新所有复选框的宽度
        for checkbox in self.character_checkboxes.values():
            checkbox.setMinimumWidth(column_width)

        # 获取底部布局
        bottom_layout = None
        for i in range(self.drawer_select_character.content_layout.count()):
            widget = self.drawer_select_character.content_layout.itemAt(i).widget()
            if isinstance(widget, QScrollArea):
                scroll_content = widget.widget()
                if scroll_content:
                    for j in range(scroll_content.layout().count()):
                        item = scroll_content.layout().itemAt(j)
                        if item.widget() and hasattr(item.widget(), 'layout') and isinstance(item.widget().layout(), QGridLayout):
                            bottom_layout = item.widget().layout()
                            break
            if bottom_layout:
                break

        # 如果找到底部布局，重新布局复选框
        if bottom_layout:
            # 清除当前布局
            for i in reversed(range(bottom_layout.count())):
                item = bottom_layout.itemAt(i)
                if item.widget():
                    bottom_layout.removeItem(item)

            # 重新添加复选框
            row, col = 0, 0
            for checkbox in self.character_checkboxes.values():
                bottom_layout.addWidget(checkbox, row, col)
                col += 1
                if col >= columns:  # 动态列数
                    col = 0
                    row += 1

    def _on_invert_selection(self):
        """反选所有角色"""
        for key, checkbox in self.character_checkboxes.items():
            checkbox.setChecked(not checkbox.isChecked())

    def _on_select_all(self):
        """全选所有角色"""
        all_checked = all(checkbox.isChecked() for checkbox in self.character_checkboxes.values())
        for checkbox in self.character_checkboxes.values():
            checkbox.setChecked(not all_checked)

    def _on_edit_external_file(self):
        """编辑外部文件"""
        import os

        # 获取外部文件路径
        custom_killer_path = os.path.join(os.getcwd(), "custom_killer.txt")

        # 确保文件存在
        if not os.path.exists(custom_killer_path):
            with open(custom_killer_path, 'w', encoding="utf-8") as f:
                f.write("")

        # 打开系统默认的文本编辑器
        try:
            if os.name == 'nt':  # Windows
                os.startfile(custom_killer_path)
        except Exception as e:
            from UI.components.modern_dialog import ModernDialog
            ModernDialog.show_dialog(self, "错误", f"无法打开文件: {e}", [ModernDialog.OK])

    def _setup_info_card(self, card: 'ModernCard'):
        """设置运行信息卡片"""
        # TODO: 添加运行状态信息显示
        # 使用card参数避免未使用警告
        if card:
            pass

    def _create_accent_color_widget(self):
        """创建强调色选择器组件"""
        # 创建一个水平布局的容器
        container = QWidget()
        container.setFixedHeight(40)  # 减小高度

        # 添加细线分隔线
        separator = QWidget(container)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e0e0e0;")
        if self.theme_manager._dark_mode:
            separator.setStyleSheet("background-color: #333333;")

        # 创建布局
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 5, 0, 0)  # 设置小的上下内边距
        layout.setSpacing(5)

        # 添加分隔线
        layout.addWidget(separator)

        # 创建颜色选择器布局
        color_layout = QHBoxLayout()
        color_layout.setContentsMargins(10, 0, 10, 0)  # 设置左右内边距
        color_layout.setSpacing(8)  # 减小间距

        # 添加简洁的标签
        label = QLabel("主题色:")
        label.setStyleSheet("font-size: 13px;")
        color_layout.addWidget(label)

        # 创建按钮组
        self.color_button_group = QButtonGroup(self)
        self.color_button_group.setExclusive(True)  # 互斥选择
        self.color_button_group.buttonClicked.connect(self._on_color_button_clicked)

        # 添加自动选项
        auto_button = self._create_color_button(None, True)
        auto_button.setFixedSize(24, 24)  # 设置更小的按钮大小
        color_layout.addWidget(auto_button)
        self.color_button_group.addButton(auto_button)

        # 预设颜色列表
        preset_colors = [
            QColor("#3498db"),  # 蓝色
            QColor("#e74c3c"),  # 红色
            QColor("#2ecc71"),  # 绿色
            QColor("#f39c12"),  # 橙色
            QColor("#9b59b6"),  # 紫色
            QColor("#1abc9c"),  # 青色
            QColor("#34495e")   # 深蓝灰色
        ]

        # 添加颜色按钮
        for color in preset_colors:
            button = self._create_color_button(color)
            button.setFixedSize(24, 24)  # 设置更小的按钮大小
            color_layout.addWidget(button)
            self.color_button_group.addButton(button)

        # 添加弹性空间，使按钮靠左对齐
        color_layout.addStretch(1)

        # 添加颜色选择器布局到主布局
        layout.addLayout(color_layout)

        # 从配置加载强调色设置
        is_auto = str(self.get_config_value('THEME', 'auto_accent_color', 'true')).lower() == 'true'
        if is_auto:
            # 选中自动按钮
            auto_button.setChecked(True)
        else:
            # 尝试从配置加载自定义强调色
            try:
                r = int(self.get_config_value('THEME', 'accent_color_r', '52'))
                g = int(self.get_config_value('THEME', 'accent_color_g', '152'))
                b = int(self.get_config_value('THEME', 'accent_color_b', '219'))
                target_color = QColor(r, g, b)

                # 查找最接近的颜色按钮
                closest_button = None
                min_distance = float('inf')

                for button in self.color_button_group.buttons():
                    if hasattr(button, 'color') and button.color is not None:
                        # 计算颜色距离
                        distance = (
                            (button.color.red() - target_color.red()) ** 2 +
                            (button.color.green() - target_color.green()) ** 2 +
                            (button.color.blue() - target_color.blue()) ** 2
                        )

                        if distance < min_distance:
                            min_distance = distance
                            closest_button = button

                if closest_button:
                    closest_button.setChecked(True)
                else:
                    auto_button.setChecked(True)
            except:
                # 如果加载失败，使用自动模式
                auto_button.setChecked(True)

        # 连接主题变化信号，更新分隔线颜色
        if hasattr(self, 'theme_manager'):
            self.theme_manager.themeChanged.connect(lambda is_dark:
                separator.setStyleSheet("background-color: #333333;" if is_dark else "background-color: #e0e0e0;"))

        return container

    def _create_color_button(self, color=None, is_auto=False):
        """创建颜色按钮 - 简洁版本"""
        button = QPushButton(self)
        button.setCheckable(True)  # 设置为可选中
        button.setFixedSize(24, 24)  # 设置更小的固定大小
        button.setFlat(True)  # 设置为平面按钮

        # 存储颜色和自动模式标志
        button.color = color
        button.is_auto = is_auto

        # 设置样式
        button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 0.1);
            }
        """)

        # 重写绘制方法
        original_paint_event = button.paintEvent

        def custom_paint_event(event):
            # 调用原始绘制方法
            original_paint_event(event)

            # 自定义绘制
            painter = QPainter(button)
            painter.setRenderHint(QPainter.Antialiasing)

            # 获取按钮尺寸
            rect = button.rect()
            width = rect.width()
            height = rect.height()

            # 计算圆形区域 - 更小的内边距
            circle_size = min(width, height) - 4  # 减小内边距从6像素到4像素
            circle_rect = QRect(
                (width - circle_size) // 2,
                (height - circle_size) // 2,
                circle_size,
                circle_size
            )

            # 绘制圆形
            if button.is_auto:
                # 自动选项绘制为渐变色圆环
                gradient = QConicalGradient(circle_rect.center(), 0)
                gradient.setColorAt(0.0, QColor(255, 0, 0))
                gradient.setColorAt(0.2, QColor(255, 165, 0))
                gradient.setColorAt(0.4, QColor(255, 255, 0))
                gradient.setColorAt(0.6, QColor(0, 128, 0))
                gradient.setColorAt(0.8, QColor(0, 0, 255))
                gradient.setColorAt(1.0, QColor(128, 0, 128))

                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(circle_rect)

                # 绘制内部白色/黑色圆形
                inner_circle_size = circle_size - 6  # 减小内圆与外圆的间距
                inner_circle_rect = QRect(
                    (width - inner_circle_size) // 2,
                    (height - inner_circle_size) // 2,
                    inner_circle_size,
                    inner_circle_size
                )

                inner_color = QColor("#FFFFFF") if not self.theme_manager._dark_mode else QColor("#1A1A1A")
                painter.setBrush(QBrush(inner_color))
                painter.drawEllipse(inner_circle_rect)

                # 绘制"A"字母 - 更小的字体
                font = painter.font()
                font.setPointSize(7)  # 减小字体大小
                font.setBold(True)
                painter.setFont(font)

                text_color = QColor("#1A1A1A") if not self.theme_manager._dark_mode else QColor("#FFFFFF")
                painter.setPen(QPen(text_color))
                painter.drawText(inner_circle_rect, Qt.AlignCenter, "A")
            else:
                # 普通颜色按钮
                painter.setBrush(QBrush(button.color))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(circle_rect)

            # 如果被选中，绘制选中指示器 - 更精细的指示器
            if button.isChecked():
                # 绘制外环
                pen = QPen(QColor("#FFFFFF") if self.theme_manager._dark_mode else QColor("#000000"))
                pen.setWidth(1)  # 更细的边框
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                outer_circle_rect = circle_rect.adjusted(-1, -1, 1, 1)  # 更小的选中指示器
                painter.drawEllipse(outer_circle_rect)

        # 替换绘制方法
        button.paintEvent = custom_paint_event

        return button

    def _on_color_button_clicked(self, button):
        """颜色按钮点击处理"""
        if button.is_auto:
            # 自动模式
            self._on_accent_color_changed(None, True)
        else:
            # 固定颜色模式
            self._on_accent_color_changed(button.color, False)

    def _on_camp_changed(self, option_id: int, _: str):
        """阵营选择改变"""
        # 只更新内存中的配置
        self.save_config_value('CPCI', 'rb_survivor', option_id == 1)
        self.save_config_value('CPCI', 'rb_killer', option_id == 2)

    def _on_action_changed(self, option_id: int, _: str):
        """行为模式选择改变"""
        # 只更新内存中的配置
        self.save_config_value('CPCI', 'rb_fixed_mode', option_id == 1)
        self.save_config_value('CPCI', 'rb_random_mode', option_id == 2)

    def _on_theme_changed(self):
        """主题改变时更新图标和滚动区域样式"""
        # 更新图标
        self._update_theme_icon()

        # 更新滚动区域样式
        self._update_scroll_area_style()

    def _toggle_theme(self):
        """自定义主题切换方法，避免闪烁"""
        # 先更新图标，再切换主题
        new_dark_mode = not self.theme_manager._dark_mode
        self.theme_manager._dark_mode = new_dark_mode
        self._update_theme_icon()
        # 应用背景效果
        self.theme_manager._apply_current_backdrop()
        # 发送信号通知其他组件
        self.theme_manager.themeChanged.emit(new_dark_mode)
        # 保存主题状态到配置
        self.save_config_value('THEME', 'dark_mode', new_dark_mode)
        config_manager.save_configs()

    def _update_theme_icon(self):
        """根据当前主题更新图标"""
        if self.theme_manager._dark_mode:
            self.theme_btn.setIcon(QIcon(":/resources/light_mode.svg"))
        else:
            self.theme_btn.setIcon(QIcon(":/resources/dark_mode.svg"))

    def _update_scroll_area_style(self):
        """更新滚动区域样式以适应当前主题"""
        # 如果没有创建或显示抽屉，则返回
        if not hasattr(self, 'drawer_select_character') or not self.drawer_select_character.isVisible():
            return

        # 查找滚动区域
        scroll_area = None
        for i in range(self.drawer_select_character.content_layout.count()):
            widget = self.drawer_select_character.content_layout.itemAt(i).widget()
            if isinstance(widget, QScrollArea) and widget.objectName() == "drawer_scroll_area":
                scroll_area = widget
                break

        if not scroll_area:
            return

        # 设置滚动区域样式，考虑主题切换
        is_dark = self.theme_manager.isDarkMode() if hasattr(self, 'theme_manager') else False
        scroll_bar_bg = "#2c2c2c" if is_dark else "#f0f0f0"
        scroll_bar_handle = "#404040" if is_dark else "#c0c0c0"
        scroll_bar_handle_hover = "#4f4f4f" if is_dark else "#a0a0a0"

        # 获取内容容器
        content_widget = scroll_area.widget()
        if content_widget:
            # 设置背景色
            bg_color = "#1e1e1e" if is_dark else "#ffffff"
            content_widget.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px;")

            # 确保所有子容器都是透明的，但保留分隔线的样式
            for child in content_widget.findChildren(QWidget):
                if not isinstance(child, (ModernCheckBox, ModernButton, ModernRadioGroup)):
                    # 如果是分隔线，保留其样式
                    if isinstance(child, QFrame) and child.frameShape() == QFrame.HLine:
                        # 更新分隔线颜色
                        self._update_separator_color(child)
                    else:
                        child.setStyleSheet("background-color: transparent;")

        scroll_area.setStyleSheet(f"""
            QScrollArea#drawer_scroll_area {{
                border: none;
                background-color: transparent;
            }}

            QScrollBar:vertical {{
                background: {scroll_bar_bg};
                width: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {scroll_bar_handle};
                min-height: 30px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {scroll_bar_handle_hover};
            }}

            QScrollBar::add-line:vertical {{
                height: 0px;
            }}

            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # 更新抽屉组件的主题状态
        if hasattr(self, 'drawer_select_character') and hasattr(self, 'theme_manager'):
            # 更新样式
            self.drawer_select_character._update_style()
            # 触发重绘以更新粒子效果
            self.drawer_select_character.update()

    def _show_notification(self):
        """显示通知"""
        source = self.sender().text()
        if source == "开始":
            # 保存所有配置
            config_manager.save_configs()
            # 等待连接后台
            self.notification_manager.showMessage("脚本已启动！正在运行中···", "success", source=source)
        elif source == "停止":
            self.notification_manager.showMessage("脚本已停止！", "error", source=source)
        elif source == "暂停":
            self.notification_manager.showMessage("脚本已暂停！", "warning", source=source)

    def _on_accent_color_changed(self, color, is_auto):
        """强调色变化处理"""
        if is_auto:
            # 使用系统强调色
            config_manager.get_ui_config()['THEME']['auto_accent_color'] = True
            # 重置主题管理器的强调色为系统强调色
            from UI.utils.system_theme_utils import get_system_accent_color
            system_accent = get_system_accent_color()
            self.theme_manager._accent_color = system_accent
            self.theme_manager.accentColorChanged.emit(system_accent)
        else:
            # 使用自定义强调色
            config_manager.get_ui_config()['THEME']['auto_accent_color'] = False
            config_manager.get_ui_config()['THEME']['accent_color_r'] = color.red()
            config_manager.get_ui_config()['THEME']['accent_color_g'] = color.green()
            config_manager.get_ui_config()['THEME']['accent_color_b'] = color.blue()

            # 更新主题管理器的强调色
            custom_accent = {
                'red': color.red(),
                'green': color.green(),
                'blue': color.blue(),
                'alpha': 255
            }
            self.theme_manager._accent_color = custom_accent
            self.theme_manager.accentColorChanged.emit(custom_accent)

        # 保存配置
        config_manager.save_configs()

    def _update_separator_color(self, separator):
        """更新分隔线颜色"""
        if hasattr(self, 'theme_manager') and self.theme_manager._accent_color:
            theme_color = QColor(
                self.theme_manager._accent_color['red'],
                self.theme_manager._accent_color['green'],
                self.theme_manager._accent_color['blue']
            )
            # 增强分隔线的可见度
            separator.setFixedHeight(2)  # 确保高度为2像素
            # 使用更强的样式表达式
            separator.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba({theme_color.red()}, {theme_color.green()}, {theme_color.blue()}, 0.9);
                    border: none;
                    min-height: 2px;
                    max-height: 2px;
                }}
            """)

    def _adjust_drawer_width(self):
        """调整抽屉宽度"""
        if not hasattr(self, 'drawer_select_character'):
            return

        # 获取当前宽度，用于调试信息
        _ = self.drawer_select_character.get_drawer_width()

        # 创建对话框
        from UI.components.modern_dialog import ModernDialog

        # 定义宽度选项
        width_options = [
            (400, "窄 (400px)"),
            (520, "标准 (520px)"),
            (650, "宽 (650px)"),
            (750, "超宽 (750px)")
        ]

        # 创建自定义按钮类型
        WIDTH_400 = "width_400"
        WIDTH_520 = "width_520"
        WIDTH_650 = "width_650"
        WIDTH_750 = "width_750"

        # 按钮类型映射
        width_button_map = {
            WIDTH_400: width_options[0][1],
            WIDTH_520: width_options[1][1],
            WIDTH_650: width_options[2][1],
            WIDTH_750: width_options[3][1]
        }

        # 创建按钮列表
        buttons = [WIDTH_400, WIDTH_520, WIDTH_650, WIDTH_750, ModernDialog.CANCEL]

        # 显示对话框
        dialog = ModernDialog.show_dialog(
            self,
            "调整抽屉宽度",
            "请选择抽屉的宽度：",
            buttons,
            button_texts=width_button_map
        )

        # 获取结果
        result = dialog.get_result()

        # 如果用户选择了宽度选项
        if result == WIDTH_400:
            width = 400
        elif result == WIDTH_520:
            width = 520
        elif result == WIDTH_650:
            width = 650
        elif result == WIDTH_750:
            width = 750
        else:
            # 用户取消或关闭对话框
            return

        # 设置新宽度
        self.drawer_select_character.set_drawer_width(width)

        # 保存到配置
        self.save_config_value('UI', 'drawer_width', width)
        config_manager.save_configs()
