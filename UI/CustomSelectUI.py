# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CustomSelectUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Custom_select(object):
    def setupUi(self, Custom_select):
        Custom_select.setObjectName("Custom_select")
        Custom_select.resize(300, 375)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Custom_select.sizePolicy().hasHeightForWidth())
        Custom_select.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Custom_select)
        self.verticalLayout.setContentsMargins(-1, 20, -1, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Custom_select)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label, 0, QtCore.Qt.AlignTop)
        self.widget = QtWidgets.QWidget(Custom_select)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 10, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pt_search = QtWidgets.QPlainTextEdit(self.widget)
        self.pt_search.setObjectName("pt_search")
        self.horizontalLayout.addWidget(self.pt_search)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(Custom_select)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pb_save = QtWidgets.QPushButton(self.widget_2)
        self.pb_save.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.pb_save.setObjectName("pb_save")
        self.horizontalLayout_2.addWidget(self.pb_save, 0, QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom)
        self.verticalLayout.addWidget(self.widget_2)
        self.widget.raise_()
        self.widget_2.raise_()
        self.label.raise_()

        self.retranslateUi(Custom_select)
        self.pb_save.clicked.connect(Custom_select.close) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Custom_select)

    def retranslateUi(self, Custom_select):
        _translate = QtCore.QCoreApplication.translate
        Custom_select.setWindowTitle(_translate("Custom_select", "配置角色名称"))
        self.label.setText(_translate("Custom_select", "<html><head/><body><p>输入你<span style=\" font-weight:600; color:#ff0000;\">想选择</span><span style=\" font-weight:600; color:#f30752;\">的</span>角色名称，<span style=\" font-size:10pt; font-weight:600; color:#f30752;\">每行一个</span>。</p><p><span style=\" font-weight:600;\">不留空行。</span></p></body></html>"))
        self.pb_save.setText(_translate("Custom_select", "保存"))