# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acmZKkvZB.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QCommandLinkButton, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QSpinBox,
    QToolButton, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(788, 466)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox = QGroupBox(self.centralwidget)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lw_service = QListWidget(self.groupBox)
        self.lw_service.setObjectName(u"lw_service")

        self.verticalLayout_2.addWidget(self.lw_service)

        self.pb_new_service = QPushButton(self.groupBox)
        self.pb_new_service.setObjectName(u"pb_new_service")

        self.verticalLayout_2.addWidget(self.pb_new_service)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.groupBox_2 = QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lb_service_id = QLabel(self.groupBox_2)
        self.lb_service_id.setObjectName(u"lb_service_id")

        self.gridLayout_3.addWidget(self.lb_service_id, 0, 0, 1, 1)

        self.lb_service_command = QLabel(self.groupBox_2)
        self.lb_service_command.setObjectName(u"lb_service_command")

        self.gridLayout_3.addWidget(self.lb_service_command, 2, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.pb_save_service = QPushButton(self.groupBox_2)
        self.pb_save_service.setObjectName(u"pb_save_service")
        self.pb_save_service.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.pb_save_service)

        self.pb_delete_service = QPushButton(self.groupBox_2)
        self.pb_delete_service.setObjectName(u"pb_delete_service")
        palette = QPalette()
        brush = QBrush(QColor(255, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush1)
        brush2 = QBrush(QColor(120, 120, 120, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush2)
        self.pb_delete_service.setPalette(palette)

        self.horizontalLayout_6.addWidget(self.pb_delete_service)


        self.gridLayout_3.addLayout(self.horizontalLayout_6, 6, 1, 1, 1)

        self.lb_service_wait_time = QLabel(self.groupBox_2)
        self.lb_service_wait_time.setObjectName(u"lb_service_wait_time")

        self.gridLayout_3.addWidget(self.lb_service_wait_time, 4, 0, 1, 1)

        self.lb_service_name = QLabel(self.groupBox_2)
        self.lb_service_name.setObjectName(u"lb_service_name")

        self.gridLayout_3.addWidget(self.lb_service_name, 1, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.sb_wait_time_min = QSpinBox(self.groupBox_2)
        self.sb_wait_time_min.setObjectName(u"sb_wait_time_min")
        self.sb_wait_time_min.setMaximum(2147483647)

        self.horizontalLayout_5.addWidget(self.sb_wait_time_min)

        self.lb_to = QLabel(self.groupBox_2)
        self.lb_to.setObjectName(u"lb_to")

        self.horizontalLayout_5.addWidget(self.lb_to)

        self.sb_wait_time_max = QSpinBox(self.groupBox_2)
        self.sb_wait_time_max.setObjectName(u"sb_wait_time_max")
        self.sb_wait_time_max.setMaximum(2147483647)

        self.horizontalLayout_5.addWidget(self.sb_wait_time_max)

        self.lb_second = QLabel(self.groupBox_2)
        self.lb_second.setObjectName(u"lb_second")

        self.horizontalLayout_5.addWidget(self.lb_second)


        self.gridLayout_3.addLayout(self.horizontalLayout_5, 4, 1, 1, 1)

        self.lb_service_config_key = QLabel(self.groupBox_2)
        self.lb_service_config_key.setObjectName(u"lb_service_config_key")

        self.gridLayout_3.addWidget(self.lb_service_config_key, 3, 0, 1, 1)

        self.le_service_id = QLineEdit(self.groupBox_2)
        self.le_service_id.setObjectName(u"le_service_id")
        self.le_service_id.setEnabled(True)

        self.gridLayout_3.addWidget(self.le_service_id, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 5, 1, 1, 1)

        self.le_service_name = QLineEdit(self.groupBox_2)
        self.le_service_name.setObjectName(u"le_service_name")

        self.gridLayout_3.addWidget(self.le_service_name, 1, 1, 1, 1)

        self.le_service_config_key = QLineEdit(self.groupBox_2)
        self.le_service_config_key.setObjectName(u"le_service_config_key")

        self.gridLayout_3.addWidget(self.le_service_config_key, 3, 1, 1, 1)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.le_service_command = QLineEdit(self.groupBox_2)
        self.le_service_command.setObjectName(u"le_service_command")

        self.horizontalLayout_11.addWidget(self.le_service_command)

        self.pb_service_command_help = QToolButton(self.groupBox_2)
        self.pb_service_command_help.setObjectName(u"pb_service_command_help")

        self.horizontalLayout_11.addWidget(self.pb_service_command_help)


        self.gridLayout_3.addLayout(self.horizontalLayout_11, 2, 1, 1, 1)


        self.horizontalLayout.addWidget(self.groupBox_2)


        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        self.groupBox_3 = QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.horizontalLayout_4 = QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.lw_user = QListWidget(self.groupBox_3)
        self.lw_user.setObjectName(u"lw_user")

        self.verticalLayout_3.addWidget(self.lw_user)

        self.pb_new_user = QPushButton(self.groupBox_3)
        self.pb_new_user.setObjectName(u"pb_new_user")

        self.verticalLayout_3.addWidget(self.pb_new_user)


        self.horizontalLayout_4.addLayout(self.verticalLayout_3)

        self.groupBox_4 = QGroupBox(self.groupBox_3)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_4 = QGridLayout(self.groupBox_4)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.pb_edit_user_config = QPushButton(self.groupBox_4)
        self.pb_edit_user_config.setObjectName(u"pb_edit_user_config")
        self.pb_edit_user_config.setEnabled(False)

        self.gridLayout_4.addWidget(self.pb_edit_user_config, 7, 1, 1, 1)

        self.lb_user_id = QLabel(self.groupBox_4)
        self.lb_user_id.setObjectName(u"lb_user_id")

        self.gridLayout_4.addWidget(self.lb_user_id, 0, 0, 1, 1)

        self.lb_user_config = QLabel(self.groupBox_4)
        self.lb_user_config.setObjectName(u"lb_user_config")

        self.gridLayout_4.addWidget(self.lb_user_config, 7, 0, 1, 1)

        self.pb_delete_user = QPushButton(self.groupBox_4)
        self.pb_delete_user.setObjectName(u"pb_delete_user")
        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.ButtonText, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.ButtonText, brush2)
        self.pb_delete_user.setPalette(palette1)

        self.gridLayout_4.addWidget(self.pb_delete_user, 9, 1, 1, 1)

        self.lb_user_email = QLabel(self.groupBox_4)
        self.lb_user_email.setObjectName(u"lb_user_email")

        self.gridLayout_4.addWidget(self.lb_user_email, 4, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_2, 6, 1, 1, 1)

        self.le_user_email = QLineEdit(self.groupBox_4)
        self.le_user_email.setObjectName(u"le_user_email")

        self.gridLayout_4.addWidget(self.le_user_email, 4, 1, 1, 1)

        self.le_user_id = QLineEdit(self.groupBox_4)
        self.le_user_id.setObjectName(u"le_user_id")
        self.le_user_id.setEnabled(False)

        self.gridLayout_4.addWidget(self.le_user_id, 0, 1, 1, 1)

        self.le_user_name = QLineEdit(self.groupBox_4)
        self.le_user_name.setObjectName(u"le_user_name")

        self.gridLayout_4.addWidget(self.le_user_name, 1, 1, 1, 1)

        self.lb_user_name = QLabel(self.groupBox_4)
        self.lb_user_name.setObjectName(u"lb_user_name")

        self.gridLayout_4.addWidget(self.lb_user_name, 1, 0, 1, 1)

        self.pb_save_user = QPushButton(self.groupBox_4)
        self.pb_save_user.setObjectName(u"pb_save_user")
        self.pb_save_user.setEnabled(False)

        self.gridLayout_4.addWidget(self.pb_save_user, 5, 1, 1, 1)


        self.horizontalLayout_4.addWidget(self.groupBox_4)


        self.gridLayout.addWidget(self.groupBox_3, 0, 1, 1, 1)

        self.groupBox_5 = QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_5 = QGridLayout(self.groupBox_5)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.le_email_account = QLineEdit(self.groupBox_5)
        self.le_email_account.setObjectName(u"le_email_account")

        self.gridLayout_5.addWidget(self.le_email_account, 1, 1, 1, 1)

        self.pb_save_config = QPushButton(self.groupBox_5)
        self.pb_save_config.setObjectName(u"pb_save_config")
        self.pb_save_config.setEnabled(False)

        self.gridLayout_5.addWidget(self.pb_save_config, 5, 1, 1, 1)

        self.lb_email_password = QLabel(self.groupBox_5)
        self.lb_email_password.setObjectName(u"lb_email_password")

        self.gridLayout_5.addWidget(self.lb_email_password, 2, 0, 1, 1)

        self.le_email_server = QLineEdit(self.groupBox_5)
        self.le_email_server.setObjectName(u"le_email_server")

        self.gridLayout_5.addWidget(self.le_email_server, 0, 1, 1, 1)

        self.lb_email_server = QLabel(self.groupBox_5)
        self.lb_email_server.setObjectName(u"lb_email_server")

        self.gridLayout_5.addWidget(self.lb_email_server, 0, 0, 1, 1)

        self.le_email_password = QLineEdit(self.groupBox_5)
        self.le_email_password.setObjectName(u"le_email_password")
        self.le_email_password.setEchoMode(QLineEdit.Password)

        self.gridLayout_5.addWidget(self.le_email_password, 2, 1, 1, 1)

        self.lb_email_account = QLabel(self.groupBox_5)
        self.lb_email_account.setObjectName(u"lb_email_account")

        self.gridLayout_5.addWidget(self.lb_email_account, 1, 0, 1, 1)

        self.lb_notice_type = QLabel(self.groupBox_5)
        self.lb_notice_type.setObjectName(u"lb_notice_type")

        self.gridLayout_5.addWidget(self.lb_notice_type, 3, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.rb_no_notice = QRadioButton(self.groupBox_5)
        self.rb_no_notice.setObjectName(u"rb_no_notice")
        self.rb_no_notice.setChecked(True)

        self.horizontalLayout_9.addWidget(self.rb_no_notice)

        self.rb_all_notice = QRadioButton(self.groupBox_5)
        self.rb_all_notice.setObjectName(u"rb_all_notice")
        self.rb_all_notice.setChecked(False)

        self.horizontalLayout_9.addWidget(self.rb_all_notice)

        self.rb_div_notice = QRadioButton(self.groupBox_5)
        self.rb_div_notice.setObjectName(u"rb_div_notice")
        self.rb_div_notice.setChecked(False)

        self.horizontalLayout_9.addWidget(self.rb_div_notice)


        self.gridLayout_5.addLayout(self.horizontalLayout_9, 3, 1, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_5.addItem(self.verticalSpacer_3, 4, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox_5, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_6 = QGroupBox(self.centralwidget)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox_6)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.cb_skip_wait = QCheckBox(self.groupBox_6)
        self.cb_skip_wait.setObjectName(u"cb_skip_wait")
        self.cb_skip_wait.setChecked(True)

        self.verticalLayout_4.addWidget(self.cb_skip_wait)

        self.cb_only_choose_service = QCheckBox(self.groupBox_6)
        self.cb_only_choose_service.setObjectName(u"cb_only_choose_service")
        self.cb_only_choose_service.setChecked(True)

        self.verticalLayout_4.addWidget(self.cb_only_choose_service)

        self.cb_only_choose_user = QCheckBox(self.groupBox_6)
        self.cb_only_choose_user.setObjectName(u"cb_only_choose_user")
        self.cb_only_choose_user.setChecked(True)

        self.verticalLayout_4.addWidget(self.cb_only_choose_user)

        self.cb_send_email_notice = QCheckBox(self.groupBox_6)
        self.cb_send_email_notice.setObjectName(u"cb_send_email_notice")

        self.verticalLayout_4.addWidget(self.cb_send_email_notice)

        self.pb_run_checkin = QCommandLinkButton(self.groupBox_6)
        self.pb_run_checkin.setObjectName(u"pb_run_checkin")

        self.verticalLayout_4.addWidget(self.pb_run_checkin)


        self.verticalLayout.addWidget(self.groupBox_6)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.lb_last_checkin_time_tip = QLabel(self.centralwidget)
        self.lb_last_checkin_time_tip.setObjectName(u"lb_last_checkin_time_tip")

        self.horizontalLayout_3.addWidget(self.lb_last_checkin_time_tip)

        self.lb_last_checkin_time = QLabel(self.centralwidget)
        self.lb_last_checkin_time.setObjectName(u"lb_last_checkin_time")

        self.horizontalLayout_3.addWidget(self.lb_last_checkin_time)


        self.verticalLayout.addLayout(self.horizontalLayout_3)


        self.gridLayout.addLayout(self.verticalLayout, 1, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"AutoCheckinManager - Config", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"\u7b7e\u5230\u670d\u52a1\u5217\u8868", None))
        self.pb_new_service.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u670d\u52a1", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"\u670d\u52a1\u8bbe\u7f6e", None))
        self.lb_service_id.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.lb_service_command.setText(QCoreApplication.translate("MainWindow", u"\u547d\u4ee4", None))
        self.pb_save_service.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.pb_delete_service.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664\u670d\u52a1", None))
        self.lb_service_wait_time.setText(QCoreApplication.translate("MainWindow", u"\u968f\u673a\u7b49\u5f85\u65f6\u95f4", None))
        self.lb_service_name.setText(QCoreApplication.translate("MainWindow", u"\u540d\u79f0", None))
        self.lb_to.setText(QCoreApplication.translate("MainWindow", u"\u81f3", None))
        self.lb_second.setText(QCoreApplication.translate("MainWindow", u"\u79d2", None))
        self.lb_service_config_key.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e\u6587\u4ef6\u5b57\u6bb5", None))
        self.pb_service_command_help.setText(QCoreApplication.translate("MainWindow", u"?", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"\u7528\u6237\u5217\u8868", None))
        self.pb_new_user.setText(QCoreApplication.translate("MainWindow", u"\u65b0\u5efa\u7528\u6237", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"\u7528\u6237\u8bbe\u7f6e", None))
        self.pb_edit_user_config.setText(QCoreApplication.translate("MainWindow", u"\u4f7f\u7528\u7f16\u8f91\u5668\u4fee\u6539", None))
        self.lb_user_id.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.lb_user_config.setText(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e\u6587\u4ef6", None))
        self.pb_delete_user.setText(QCoreApplication.translate("MainWindow", u"\u5220\u9664\u7528\u6237", None))
        self.lb_user_email.setText(QCoreApplication.translate("MainWindow", u"\u90ae\u4ef6\u5730\u5740", None))
        self.lb_user_name.setText(QCoreApplication.translate("MainWindow", u"\u540d\u79f0", None))
        self.pb_save_user.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"\u5176\u5b83\u8bbe\u7f6e", None))
        self.pb_save_config.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58", None))
        self.lb_email_password.setText(QCoreApplication.translate("MainWindow", u"\u90ae\u7bb1\u5bc6\u7801", None))
        self.lb_email_server.setText(QCoreApplication.translate("MainWindow", u"\u90ae\u4ef6\u670d\u52a1\u5668", None))
        self.lb_email_account.setText(QCoreApplication.translate("MainWindow", u"\u90ae\u7bb1\u8d26\u6237", None))
        self.lb_notice_type.setText(QCoreApplication.translate("MainWindow", u"\u7528\u6237\u901a\u77e5\u7c7b\u578b", None))
        self.rb_no_notice.setText(QCoreApplication.translate("MainWindow", u"\u4e0d\u901a\u77e5", None))
        self.rb_all_notice.setText(QCoreApplication.translate("MainWindow", u"\u4e00\u8d77\u901a\u77e5", None))
        self.rb_div_notice.setText(QCoreApplication.translate("MainWindow", u"\u72ec\u7acb\u901a\u77e5", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("MainWindow", u"\u6d4b\u8bd5", None))
        self.cb_skip_wait.setText(QCoreApplication.translate("MainWindow", u"\u8df3\u8fc7\u968f\u673a\u7b49\u5f85", None))
        self.cb_only_choose_service.setText(QCoreApplication.translate("MainWindow", u"\u4ec5\u6267\u884c\u5f53\u524d\u9009\u62e9\u670d\u52a1", None))
        self.cb_only_choose_user.setText(QCoreApplication.translate("MainWindow", u"\u4ec5\u6267\u884c\u5f53\u524d\u9009\u62e9\u7528\u6237", None))
        self.cb_send_email_notice.setText(QCoreApplication.translate("MainWindow", u"\u53d1\u9001\u90ae\u4ef6\u901a\u77e5", None))
        self.pb_run_checkin.setText(QCoreApplication.translate("MainWindow", u"\u7acb\u5373\u6267\u884c\u7b7e\u5230", None))
        self.lb_last_checkin_time_tip.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u6b21\u81ea\u52a8\u7b7e\u5230\u65f6\u95f4\uff1a", None))
        self.lb_last_checkin_time.setText(QCoreApplication.translate("MainWindow", u"1970-01-01 08:00:00", None))
    # retranslateUi

