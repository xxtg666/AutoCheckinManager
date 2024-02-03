import os
import sys
import json
import time
import random
import threading
import webbrowser
import subprocess
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from ui_acm import Ui_MainWindow

def generateRandomID(k=8):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',k))

class NAME(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initConfig()
        self.bypass_italic = False
        self.initChangeItalic()
        self.startup_init_service = True
        self.initService()
        self.startup_init_user = True
        self.initUser()
        self.pb_run_checkin.clicked.connect(self.testCheckin)
        self.lb_last_checkin_time.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(json.load(open("last_checkin_time.json")))))
        self.show()
    
    def initChangeItalic(self):
        self.le_email_server.textChanged.connect(lambda: self.setItalic(self.lb_email_server, True, "enable_save_config"))
        self.le_email_account.textChanged.connect(lambda: self.setItalic(self.lb_email_account, True, "enable_save_config"))
        self.le_email_password.textChanged.connect(lambda: self.setItalic(self.lb_email_password, True, "enable_save_config"))
        self.rb_no_notice.toggled.connect(lambda: self.setItalic(self.lb_notice_type, True, "enable_save_config"))
        self.rb_all_notice.toggled.connect(lambda: self.setItalic(self.lb_notice_type, True, "enable_save_config"))
        self.rb_div_notice.toggled.connect(lambda: self.setItalic(self.lb_notice_type, True, "enable_save_config"))
        self.le_service_id.textChanged.connect(lambda: self.setItalic(self.lb_service_id, True, "disable_service_list"))
        self.le_service_name.textChanged.connect(lambda: self.setItalic(self.lb_service_name, True, "disable_service_list"))
        self.le_service_command.textChanged.connect(lambda: self.setItalic(self.lb_service_command, True, "disable_service_list"))
        self.le_service_config_key.textChanged.connect(lambda: self.setItalic(self.lb_service_config_key, True, "disable_service_list"))
        self.sb_wait_time_min.valueChanged.connect(lambda: self.setItalic(self.lb_service_wait_time, True, "disable_service_list"))
        self.sb_wait_time_max.valueChanged.connect(lambda: self.setItalic(self.lb_service_wait_time, True, "disable_service_list"))
        self.le_user_name.textChanged.connect(lambda: self.setItalic(self.lb_user_name, True, "disable_user_list"))
        self.le_user_email.textChanged.connect(lambda: self.setItalic(self.lb_user_email, True, "disable_user_list"))

    def initConfig(self):
        if not os.path.exists("users"):
            os.mkdir("users")
        if not os.path.exists("services.json"):
            json.dump({}, open("services.json", "w"))
        if not os.path.exists("users.json"):
            json.dump({}, open("users.json", "w"))
        if not os.path.exists("config.json"):
            json.dump({
                "email_server":"",
                "email_account":"",
                "email_password":"",
                "email_notice_type":"no"
            }, open("config.json", "w"))
        if not os.path.exists("last_checkin_time.json"):
            json.dump(0, open("last_checkin_time.json", "w"))
        config = json.load(open("config.json"))
        self.bypass_italic = True
        self.le_email_server.setText(config["email_server"])
        self.le_email_account.setText(config["email_account"])
        self.le_email_password.setText(config["email_password"])
        match config["email_notice_type"]:
            case "no":
                self.rb_no_notice.setChecked(True)
            case "all":
                self.rb_all_notice.setChecked(True)
            case "div":
                self.rb_div_notice.setChecked(True)
        self.bypass_italic = False
        self.pb_save_config.clicked.connect(self.saveConfig)
    
    def initService(self):
        self.services = json.load(open("services.json"))
        self.lw_service.clear()
        for key in self.services:
            self.lw_service.addItem(key)
        if self.startup_init_service:
            self.lw_service.itemClicked.connect(lambda: self.showService(self.lw_service.currentItem()))
            self.pb_save_service.clicked.connect(self.saveService)
            self.pb_new_service.clicked.connect(self.newService)
            self.pb_delete_service.clicked.connect(self.deleteService)
            self.pb_service_command_help.clicked.connect(lambda: QMessageBox.information(self, "提示", "使用 {config} 会填充配置文件中字段对应的值"))
            self.startup_init_service = False
    
    def showService(self, item):
        service = self.services[item.text()]
        self.bypass_italic = True
        self.le_service_id.setText(item.text())
        self.le_service_name.setText(service["name"])
        self.le_service_command.setText(service["command"])
        self.le_service_config_key.setText(service["key"])
        self.sb_wait_time_min.setValue(service["wait_time_min"])
        self.sb_wait_time_max.setValue(service["wait_time_max"])
        self.bypass_italic = False

    def saveService(self):
        service = {
            "name":self.le_service_name.text(),
            "command":self.le_service_command.text(),
            "key":self.le_service_config_key.text(),
            "wait_time_min":self.sb_wait_time_min.value(),
            "wait_time_max":self.sb_wait_time_max.value()
        }
        self.services[self.le_service_id.text()] = service
        json.dump(self.services, open("services.json", "w"))
        QMessageBox.information(self, "提示", f"服务 {self.le_service_id.text()} 保存成功！")
        self.setItalic(self.lb_service_name, False)
        self.setItalic(self.lb_service_command, False)
        self.setItalic(self.lb_service_config_key, False)
        self.setItalic(self.lb_service_wait_time, False)
        self.lw_service.setEnabled(True)
        self.pb_new_service.setEnabled(True)
        self.initService()
        self.pb_save_service.setEnabled(False)
    
    def deleteService(self):
        try:
            del self.services[self.le_service_id.text()]
            json.dump(self.services, open("services.json", "w"))
            QMessageBox.information(self, "提示", f"服务 {self.le_service_id.text()} 删除成功！")
        except:
            self.lw_service.setEnabled(True)
            self.pb_new_service.setEnabled(True)
        self.bypass_italic = True
        self.newService("")
        self.bypass_italic = False
        self.initService()
    
    def newService(self, service_id = False):
        if service_id == False:
            service_id = f"new_service_{random.randint(100,999)}"
        self.le_service_id.setText(service_id)
        self.le_service_name.setText("")
        self.le_service_command.setText("")
        self.le_service_config_key.setText("")
        self.sb_wait_time_min.setValue(0)
        self.sb_wait_time_max.setValue(0)
        self.pb_save_service.setEnabled(False)

    def saveConfig(self):
        config = {
            "email_server":self.le_email_server.text(),
            "email_account":self.le_email_account.text(),
            "email_password":self.le_email_password.text(),
            "email_notice_type":"no"
        }
        if self.rb_all_notice.isChecked():
            config["email_notice_type"] = "all"
        elif self.rb_div_notice.isChecked():
            config["email_notice_type"] = "div"
        json.dump(config, open("config.json", "w"))
        QMessageBox.information(self, "提示", "配置保存成功！")
        self.setItalic(self.lb_email_server, False)
        self.setItalic(self.lb_email_account, False)
        self.setItalic(self.lb_email_password, False)
        self.setItalic(self.lb_notice_type, False)
        self.pb_save_config.setEnabled(False)
    
    def initUser(self):
        self.users = json.load(open("users.json"))
        self.lw_user.clear()
        for key in self.users:
            self.lw_user.addItem(self.users[key]["name"])
        if self.startup_init_user:
            self.lw_user.itemClicked.connect(lambda: self.showUser(self.lw_user.currentItem()))
            self.pb_save_user.clicked.connect(self.saveUser)
            self.pb_new_user.clicked.connect(self.newUser)
            self.pb_delete_user.clicked.connect(self.deleteUser)
            self.pb_edit_user_config.clicked.connect(self.editUserConfig)
            self.startup_init_user = False
    
    def showUser(self, item):
        for key in self.users:
            if self.users[key]["name"] == item.text():
                user = self.users[key]
                self.bypass_italic = True
                self.le_user_id.setEnabled(True)
                self.le_user_id.setText(key)
                self.le_user_id.setEnabled(False)
                self.le_user_name.setText(user["name"])
                self.le_user_email.setText(user["email"])
                self.bypass_italic = False
                self.pb_edit_user_config.setEnabled(True)
                break
        
    def saveUser(self):
        for key in self.users:
            if self.users[key]["name"] == self.le_user_name.text() and key != self.le_user_id.text():
                QMessageBox.warning(self, "错误", f"用户名 {self.le_user_name.text()} 已存在！")
                return
        user = {
            "name":self.le_user_name.text(),
            "email":self.le_user_email.text()
        }
        self.users[self.le_user_id.text()] = user
        json.dump(self.users, open("users.json", "w"))
        if not os.path.exists(f"users/{self.le_user_id.text()}.json"):
            json.dump({
                "services":[],
                "config":{}
            }, open(f"users/{self.le_user_id.text()}.json", "w"))
        QMessageBox.information(self, "提示", f"用户 {user['name']} 保存成功！")
        self.setItalic(self.lb_user_name, False)
        self.setItalic(self.lb_user_email, False)
        self.lw_user.setEnabled(True)
        self.pb_new_user.setEnabled(True)
        self.initUser()
        self.pb_edit_user_config.setEnabled(True)
        self.pb_save_user.setEnabled(False)
    
    def deleteUser(self):
        try:
            del self.users[self.le_user_id.text()]
            json.dump(self.users, open("users.json", "w"))
            os.remove(f"users/{self.le_user_id.text()}.json")
            QMessageBox.information(self, "提示", f"用户 {self.le_user_name.text()} 删除成功！")
        except:
            self.lw_user.setEnabled(True)
            self.pb_new_user.setEnabled(True)
        self.bypass_italic = True
        self.newUser("")
        self.bypass_italic = False
        self.initUser()
    
    def newUser(self, user_id = False):
        if user_id == False:
            user_id = generateRandomID()
            self.lw_user.setEnabled(False)
            self.pb_new_user.setEnabled(False)
        self.le_user_id.setEnabled(True)
        self.le_user_id.setText(user_id)
        self.le_user_id.setEnabled(False)
        self.le_user_name.setText("")
        self.le_user_email.setText("")
        self.pb_edit_user_config.setEnabled(False)
        self.pb_save_user.setEnabled(False)
    
    def editUserConfig(self):
        webbrowser.open(os.path.abspath(f"users/{self.le_user_id.text()}.json"))
    
    def setItalic(self, label, status, special = None):
        if not self.bypass_italic:
            font = label.font()
            font.setItalic(status)
            label.setFont(font)
            if special:
                match special:
                    case "disable_service_list":
                        self.lw_service.setEnabled(False)
                        self.pb_new_service.setEnabled(False)
                        self.pb_save_service.setEnabled(True)
                    case "disable_user_list":
                        self.lw_user.setEnabled(False)
                        self.pb_new_user.setEnabled(False)
                        self.pb_save_user.setEnabled(True)
                    case "enable_save_config":
                        self.pb_save_config.setEnabled(True)
    
    def testCheckin(self):
        QMessageBox.information(
            self, 
            "测试签到数据输出", 
            checkin(
                True, 
                self.cb_skip_wait.isChecked(), 
                self.cb_only_choose_service.isChecked(), 
                self.cb_only_choose_user.isChecked(), 
                self.cb_send_email_notice.isChecked()
            )
        )

global_checkin_query = {}
global_checkin_query_list = []
def checkin(test_mode = False, skip_wait_time = False, only_service = False, only_user = False, email_notice = True):
    global global_checkin_query, global_checkin_query_list
    if not test_mode:
        results = {}
        delays = []
        json.dump(time.time(), open("last_checkin_time.json", "w"))
        for ukey in (users := json.load(open("users.json"))):
            user_config = json.load(open(f"users/{ukey}.json"))
            results[ukey] = {}
            for skey in (services := json.load(open("services.json"))):
                service = services[skey]
                if skey not in user_config["services"]:
                    continue
                delay = random.randint(service["wait_time_min"],service["wait_time_max"])
                delays.append(delay)
                command = service["command"].replace("{config}",user_config["config"].get(service["key"],""))
                qi = generateRandomID()
                results[ukey][skey] = qi
                threading.Thread(target=lambda: delayCommand(delay, command, qi)).start()
        time.sleep(max(delays))
        while global_checkin_query_list != []:
            time.sleep(10)
        for ukey in results:
            for skey in results[ukey]:
                results[ukey][skey] = global_checkin_query[results[ukey][skey]]
        #TODO:邮件发送格式;测试模式;直接调用签到

def delayCommand(delay, command, query_item):
    global global_checkin_query, global_checkin_query_list
    time.sleep(delay)
    output, error = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    global_checkin_query[query_item] = output.decode()
    global_checkin_query_list.remove(query_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NAME()
    sys.exit(app.exec_())