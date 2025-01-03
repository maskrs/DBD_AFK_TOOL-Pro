from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from UI.components.modern_button import ModernButton, ModernLongPressButton
from UI.components.modern_card import ModernCard
from UI.components.radio_group import ModernRadioGroup
from UI.components.switch import ModernSwitch
from UI.components.modern_checkbox import ModernCheckBox
from UI.components.modern_dialog import ModernDialog

class HomePage(QWidget):
    """主页"""
    
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        
        self._setup_ui()

    def _setup_ui(self):
        """创建UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # 创建阵营选择卡片
        self.card_select_camp = ModernCard("选择阵营", self)
        
        # 创建单选框组
        self.camp_radio_group = ModernRadioGroup([
            (1, "人类"),
            (2, "屠夫")
        ], parent=self)
        
        # 设置卡片内容
        self.card_select_camp.set_content(self.camp_radio_group)
        layout.addWidget(self.card_select_camp)
        
        
        # 主题切换按钮
        theme_btn = ModernButton(self, True)
        theme_btn.setText("切换主题")
        theme_btn.setTooltip("切换主题")
        theme_btn.setIcon(QIcon(r"D:\Project\DBD_AFK_TOOL\UI\images\dark_mode.svg"))
        theme_btn.clicked.connect(self.theme_manager.toggleTheme)
        layout.addWidget(theme_btn)
        message_btn = ModernButton(self)
        message_btn.setText("模态窗口")
        message_btn.clicked.connect(self.show_message_dialog)
        layout.addWidget(message_btn)
        
        # 长按测试按钮
        long_press_btn = ModernLongPressButton(self)
        long_press_btn.setText("长按测试")
        long_press_btn.setTooltip("长按以确认")
        long_press_btn.longPressed.connect(lambda: print("长按完成！"))
        layout.addWidget(long_press_btn)


        # 对话框测试
    def show_message_dialog(self):
        ModernDialog.show_dialog(self, "提示", "测试文本本本测试文本本本测试文本试文本本本测试文本试文本本本测试文本试文本本本测试文本试文本本本测试文本试文本测试文本本测试文本", [ModernDialog.CANCEL, ModernDialog.OK], 
                                 "ic_fluent_warning_regular")



        
