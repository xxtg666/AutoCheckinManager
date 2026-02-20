import os
import json
import time
import random
import shutil
import platform
import threading
import subprocess
from smtplib import SMTP_SSL
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from resources_acm import genMailBody, genMailUser, genMailService

DATA_FILE = "data.json"

_EMPTY_DATA = {
    "config": {
        "email_server": "",
        "email_account": "",
        "email_password": "",
        "email_notice_type": "no",
    },
    "services": {},
    "users": {},
    "last_checkin_time": 0,
}

# ── 底层读写 ──

def _loadData():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _saveData(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── 迁移 ──

_LEGACY_FILES = ["config.json", "services.json", "users.json", "last_checkin_time.json"]


def needsMigration():
    return any(os.path.exists(f) for f in _LEGACY_FILES)


def migrateFromLegacy():
    data = json.loads(json.dumps(_EMPTY_DATA))

    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            data["config"] = json.load(f)

    if os.path.exists("services.json"):
        with open("services.json", "r", encoding="utf-8") as f:
            data["services"] = json.load(f)

    if os.path.exists("last_checkin_time.json"):
        with open("last_checkin_time.json", "r", encoding="utf-8") as f:
            data["last_checkin_time"] = json.load(f)

    if os.path.exists("users.json"):
        with open("users.json", "r", encoding="utf-8") as f:
            old_users = json.load(f)
        for uid, info in old_users.items():
            user = {
                "name": info["name"],
                "email": info["email"],
                "services": [],
                "config": {},
            }
            uc_path = f"users/{uid}.json"
            if os.path.exists(uc_path):
                with open(uc_path, "r", encoding="utf-8") as f:
                    uc = json.load(f)
                user["services"] = uc.get("services", [])
                user["config"] = uc.get("config", {})
            data["users"][uid] = user

    _saveData(data)

    for f in _LEGACY_FILES:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists("users") and os.path.isdir("users"):
        shutil.rmtree("users")


# ── 初始化 ──

def initDataFile():
    if not os.path.exists(DATA_FILE):
        _saveData(json.loads(json.dumps(_EMPTY_DATA)))


# ── 工具 ──

def generateRandomID(k=8):
    return ''.join(random.sample(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k))


# ── config ──

def loadConfig():
    return _loadData()["config"]


def saveConfig(config):
    data = _loadData()
    data["config"] = config
    _saveData(data)


# ── services ──

def loadServices():
    return _loadData()["services"]


def saveServices(services):
    data = _loadData()
    data["services"] = services
    _saveData(data)


# ── users ──

def loadUsers():
    return _loadData()["users"]


def saveUsers(users):
    data = _loadData()
    data["users"] = users
    _saveData(data)


def loadUserConfig(user_id):
    user = _loadData()["users"].get(user_id, {})
    return {
        "services": user.get("services", []),
        "config": user.get("config", {}),
    }


def saveUserConfig(user_id, cfg):
    data = _loadData()
    if user_id in data["users"]:
        data["users"][user_id]["services"] = cfg["services"]
        data["users"][user_id]["config"] = cfg["config"]
        _saveData(data)


# ── last_checkin_time ──

def loadLastCheckinTime():
    return _loadData()["last_checkin_time"]


def saveLastCheckinTime(t):
    data = _loadData()
    data["last_checkin_time"] = t
    _saveData(data)


# ── 签到执行 ──

_checkin_query = {}
_checkin_query_list = []
_checkin_lock = threading.Lock()


def _delayCommand(delay, command, query_item):
    global _checkin_query, _checkin_query_list
    time.sleep(delay)
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    process.wait()
    output, error = process.communicate()
    result = output.decode(encoding=("gbk" if (platform.system() == "Windows") else "utf8"))
    with _checkin_lock:
        _checkin_query[query_item] = result
        _checkin_query_list.remove(query_item)
    print("任务 " + query_item + " 执行完成")


def sendMail(receiver, subject, body):
    config = loadConfig()
    msg = MIMEMultipart()
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = config["email_account"]
    msg['To'] = ";".join(receiver)
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    smtp = SMTP_SSL(config["email_server"])
    smtp.login(config["email_account"], config["email_password"])
    smtp.sendmail(config["email_account"], receiver, msg.as_string())
    smtp.quit()


def checkin(skip_wait_time=False, only_service=None, only_user=None, email_notice=True, log_callback=None):
    global _checkin_query, _checkin_query_list

    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    config = loadConfig()
    results = {}
    delays = []
    users = loadUsers()
    services = loadServices()

    for ukey in users:
        if only_user and ukey != only_user:
            continue
        user_config = loadUserConfig(ukey)
        results[ukey] = {}
        for skey in services:
            if only_service and skey != only_service:
                continue
            service = services[skey]
            if skey not in user_config["services"]:
                continue
            delay = 0 if skip_wait_time else random.randint(service["wait_time_min"], service["wait_time_max"])
            delays.append(delay)
            command = service["command"].replace("{config}", user_config["config"].get(service["key"], ""))
            qi = generateRandomID()
            results[ukey][skey] = qi
            with _checkin_lock:
                _checkin_query_list.append(qi)
            log(f"[{users[ukey]['name']}] 启动服务 {service['name']}，等待 {delay} 秒")
            threading.Thread(target=_delayCommand, args=(delay, command, qi)).start()

    if not delays:
        log("没有需要执行的签到任务")
        return

    time.sleep(max(delays))
    while True:
        with _checkin_lock:
            if not _checkin_query_list:
                break
        time.sleep(10)

    t = time.time()
    saveLastCheckinTime(t)
    log(f"签到完成，时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}")

    if email_notice and config["email_notice_type"] == "all":
        mail_body = ""
        for ukey in results:
            mail_body += genMailUser(users[ukey]['name'])
            for skey in results[ukey]:
                output = _checkin_query[results[ukey][skey]]
                mail_body += genMailService(services[skey]["name"], output)
        d = time.strftime("%Y-%m-%d", time.localtime(t))
        mail_body = genMailBody(d, mail_body)
        sendMail([users[ukey]["email"] for ukey in users], "自动签到通知 " + d, mail_body)
        log("已发送合并通知邮件")

    if email_notice and config["email_notice_type"] == "div":
        for ukey in results:
            mail_body = genMailUser(users[ukey]['name'])
            for skey in results[ukey]:
                output = _checkin_query[results[ukey][skey]]
                mail_body += genMailService(services[skey]["name"], output)
            d = time.strftime("%Y-%m-%d", time.localtime(t))
            mail_body = genMailBody(d, mail_body)
            sendMail([users[ukey]["email"]], "自动签到通知 " + d, mail_body)
        log("已发送独立通知邮件")
