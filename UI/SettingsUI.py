# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SettingsUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SettingDialog(object):
    def setupUi(self, SettingDialog):
        SettingDialog.setObjectName("SettingDialog")
        SettingDialog.resize(215, 220)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SettingDialog.sizePolicy().hasHeightForWidth())
        SettingDialog.setSizePolicy(sizePolicy)
        SettingDialog.setMinimumSize(QtCore.QSize(215, 215))
        self.gridLayout = QtWidgets.QGridLayout(SettingDialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(SettingDialog)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName("tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(20, 8, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout_2.addItem(spacerItem, 3, 0, 1, 1)
        self.pb_customcommand = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_customcommand.sizePolicy().hasHeightForWidth())
        self.pb_customcommand.setSizePolicy(sizePolicy)
        self.pb_customcommand.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pb_customcommand.setFocusPolicy(QtCore.Qt.NoFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/customcommand/picture/create.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_customcommand.setIcon(icon)
        self.pb_customcommand.setIconSize(QtCore.QSize(18, 18))
        self.pb_customcommand.setObjectName("pb_customcommand")
        self.gridLayout_2.addWidget(self.pb_customcommand, 1, 1, 1, 1)
        self.pb_showlog = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_showlog.sizePolicy().hasHeightForWidth())
        self.pb_showlog.setSizePolicy(sizePolicy)
        self.pb_showlog.setFocusPolicy(QtCore.Qt.NoFocus)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/log/picture/paper.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_showlog.setIcon(icon1)
        self.pb_showlog.setIconSize(QtCore.QSize(18, 18))
        self.pb_showlog.setObjectName("pb_showlog")
        self.gridLayout_2.addWidget(self.pb_showlog, 0, 1, 1, 1)
        self.pb_advanced = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_advanced.sizePolicy().hasHeightForWidth())
        self.pb_advanced.setSizePolicy(sizePolicy)
        self.pb_advanced.setMinimumSize(QtCore.QSize(0, 0))
        self.pb_advanced.setFocusPolicy(QtCore.Qt.NoFocus)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/advanced/picture/gears.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_advanced.setIcon(icon2)
        self.pb_advanced.setIconSize(QtCore.QSize(20, 20))
        self.pb_advanced.setObjectName("pb_advanced")
        self.gridLayout_2.addWidget(self.pb_advanced, 0, 0, 1, 1)
        self.pb_debug_tool = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_debug_tool.sizePolicy().hasHeightForWidth())
        self.pb_debug_tool.setSizePolicy(sizePolicy)
        self.pb_debug_tool.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pb_debug_tool.setFocusPolicy(QtCore.Qt.NoFocus)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/debug/picture/tool.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_debug_tool.setIcon(icon3)
        self.pb_debug_tool.setIconSize(QtCore.QSize(18, 18))
        self.pb_debug_tool.setObjectName("pb_debug_tool")
        self.gridLayout_2.addWidget(self.pb_debug_tool, 1, 0, 1, 1)
        self.pb_coordinate_transformation = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_coordinate_transformation.sizePolicy().hasHeightForWidth())
        self.pb_coordinate_transformation.setSizePolicy(sizePolicy)
        self.pb_coordinate_transformation.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pb_coordinate_transformation.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pb_coordinate_transformation.setStyleSheet("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/setting/picture/refresh.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_coordinate_transformation.setIcon(icon4)
        self.pb_coordinate_transformation.setIconSize(QtCore.QSize(18, 18))
        self.pb_coordinate_transformation.setObjectName("pb_coordinate_transformation")
        self.gridLayout_2.addWidget(self.pb_coordinate_transformation, 2, 0, 1, 1)
        self.pb_crashreport = QtWidgets.QPushButton(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_crashreport.sizePolicy().hasHeightForWidth())
        self.pb_crashreport.setSizePolicy(sizePolicy)
        self.pb_crashreport.setFocusPolicy(QtCore.Qt.NoFocus)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/setting/picture/crash.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_crashreport.setIcon(icon5)
        self.pb_crashreport.setIconSize(QtCore.QSize(19, 19))
        self.pb_crashreport.setObjectName("pb_crashreport")
        self.gridLayout_2.addWidget(self.pb_crashreport, 2, 1, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_2.sizePolicy().hasHeightForWidth())
        self.tab_2.setSizePolicy(sizePolicy)
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_2 = QtWidgets.QFrame(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lb_chat = QtWidgets.QLabel(self.frame_2)
        self.lb_chat.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lb_chat.setObjectName("lb_chat")
        self.gridLayout_3.addWidget(self.lb_chat, 0, 0, 1, 1)
        self.pb_qqchat = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_qqchat.sizePolicy().hasHeightForWidth())
        self.pb_qqchat.setSizePolicy(sizePolicy)
        self.pb_qqchat.setMinimumSize(QtCore.QSize(25, 25))
        self.pb_qqchat.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pb_qqchat.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pb_qqchat.setStyleSheet("QPushButton {  \n"
"    border: none; /* 移除默认边框 */  \n"
"    border-radius: 10px; /* 设置圆角半径，根据需要调整 */  \n"
"    background-color: rgb(240, 240, 240); /* 设置背景颜色 */  \n"
"}")
        self.pb_qqchat.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/setting/picture/comments.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_qqchat.setIcon(icon6)
        self.pb_qqchat.setIconSize(QtCore.QSize(27, 27))
        self.pb_qqchat.setObjectName("pb_qqchat")
        self.gridLayout_3.addWidget(self.pb_qqchat, 0, 1, 1, 1)
        self.pb_help = QtWidgets.QPushButton(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pb_help.sizePolicy().hasHeightForWidth())
        self.pb_help.setSizePolicy(sizePolicy)
        self.pb_help.setMinimumSize(QtCore.QSize(25, 25))
        self.pb_help.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pb_help.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.pb_help.setStyleSheet("QPushButton {  \n"
"    border: none; /* 移除默认边框 */  \n"
"    border-radius: 10px; /* 设置圆角半径，根据需要调整 */  \n"
"    background-color: rgb(240, 240, 240); /* 设置背景颜色 */  \n"
"}")
        self.pb_help.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/setting/picture/document.gif"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pb_help.setIcon(icon7)
        self.pb_help.setIconSize(QtCore.QSize(27, 27))
        self.pb_help.setObjectName("pb_help")
        self.gridLayout_3.addWidget(self.pb_help, 1, 1, 1, 1)
        self.lb_doc = QtWidgets.QLabel(self.frame_2)
        self.lb_doc.setObjectName("lb_doc")
        self.gridLayout_3.addWidget(self.lb_doc, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 2, 0, 1, 1)
        self.lb_version = QtWidgets.QLabel(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lb_version.sizePolicy().hasHeightForWidth())
        self.lb_version.setSizePolicy(sizePolicy)
        self.lb_version.setMinimumSize(QtCore.QSize(25, 25))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lb_version.setFont(font)
        self.lb_version.setStyleSheet("QLabel {  \n"
"    border: none; /* 移除默认边框 */  \n"
"    border-radius: 10px; /* 设置圆角半径，根据需要调整 */  \n"
"    background-color: rgb(240, 240, 240); /* 设置背景颜色 */  \n"
"}")
        self.lb_version.setObjectName("lb_version")
        self.gridLayout_3.addWidget(self.lb_version, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame = QtWidgets.QFrame(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label = QtWidgets.QLabel(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label.setFrameShadow(QtWidgets.QFrame.Raised)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label.setWordWrap(True)
        self.label.setIndent(-1)
        self.label.setOpenExternalLinks(False)
        self.label.setObjectName("label")
        self.gridLayout_4.addWidget(self.label, 1, 0, 1, 1)
        self.line = QtWidgets.QFrame(self.frame)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_4.addWidget(self.line, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(SettingDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(SettingDialog)

    def retranslateUi(self, SettingDialog):
        _translate = QtCore.QCoreApplication.translate
        SettingDialog.setWindowTitle(_translate("SettingDialog", "更多设置"))
        self.pb_customcommand.setText(_translate("SettingDialog", "编写动作"))
        self.pb_showlog.setText(_translate("SettingDialog", "显示日志"))
        self.pb_advanced.setText(_translate("SettingDialog", "高级选项"))
        self.pb_debug_tool.setText(_translate("SettingDialog", "调试工具"))
        self.pb_coordinate_transformation.setToolTip(_translate("SettingDialog", "<html><head/><body><p>根据本机分辨率进行适应性调整</p></body></html>"))
        self.pb_coordinate_transformation.setText(_translate("SettingDialog", "坐标转换"))
        self.pb_crashreport.setText(_translate("SettingDialog", "崩溃报告"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("SettingDialog", "设置"))
        self.lb_chat.setText(_translate("SettingDialog", "交流频道："))
        self.pb_help.setToolTip(_translate("SettingDialog", "<html><head/><body><p><span style=\" font-family:\'宋体\';\">工具的帮助教程</span></p></body></html>"))
        self.lb_doc.setText(_translate("SettingDialog", "说明文档："))
        self.label_2.setText(_translate("SettingDialog", "软件版本："))
        self.lb_version.setText(_translate("SettingDialog", "     v2.7.5"))
        self.label.setText(_translate("SettingDialog", "<html><head/><body><p><span style=\" font-size:10pt;\">Copyright </span><span style=\" font-size:16pt;\">© </span><span style=\" font-size:10pt;\">2024 WKhistory&amp;MasKrs, Inc. All rights reserved.</span></p><p><span style=\" font-size:7pt;\">Icons by </span><a href=\"https://icons8.com\"><span style=\" font-size:7pt; text-decoration: underline; color:#0000ff;\">Icons8</span></a></p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("SettingDialog", "关于"))
import pictures_rc