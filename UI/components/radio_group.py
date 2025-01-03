from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QButtonGroup
from PySide6.QtCore import Qt, Signal
from .radio_button import ModernRadioButton

class ModernRadioGroup(QWidget):
    """现代化单选框组"""
    
    # 选择改变信号
    selectionChanged = Signal(int, str)  # 发送选中项的ID和文本
    
    def __init__(self, options=None, horizontal=True, parent=None):
        """
        初始化单选框组
        :param options: 选项列表，每项为(id, text)元组
        :param horizontal: 是否水平排列
        :param parent: 父组件
        """
        super().__init__(parent)
        self._options = []
        self._radio_buttons = {}  # id -> ModernRadioButton
        
        # 获取主题管理器
        if hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
        
        # 创建布局
        self.layout = QHBoxLayout() if horizontal else QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        
        # 创建按钮组
        self.button_group = QButtonGroup(self)
        self.button_group.idClicked.connect(self._on_button_clicked)
        
        # 添加选项
        if options:
            for option_id, text in options:
                self.add_option(option_id, text)
                
    def add_option(self, option_id, text):
        """
        添加单选框选项
        :param option_id: 选项ID
        :param text: 选项文本
        """
        if option_id in self._radio_buttons:
            return
            
        radio = ModernRadioButton(self)
        radio.setText(text)
        
        self.button_group.addButton(radio, option_id)
        self.layout.addWidget(radio)
        self._radio_buttons[option_id] = radio
        self._options.append((option_id, text))
        
    def get_selected(self):
        """获取选中项的(id, text)"""
        button = self.button_group.checkedButton()
        if button:
            option_id = self.button_group.id(button)
            return option_id, button.text()
        return None
        
    def set_selected(self, option_id):
        """设置选中项"""
        if option_id in self._radio_buttons:
            self._radio_buttons[option_id].setChecked(True)
            
    def _on_button_clicked(self, option_id):
        """按钮点击事件"""
        button = self.button_group.button(option_id)
        if button:
            self.selectionChanged.emit(option_id, button.text()) 