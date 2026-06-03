import os
import json
import time
import random
import shutil
import platform
import threading
import subprocess
import urllib.request
import urllib.error
import html
from resources_acm import genTelegramMessage, genTelegramUser, genTelegramService

DATA_FILE = "data.json"
BOT_POLL_INTERVAL = 3
SCHEDULER_POLL_INTERVAL = 300


class TelegramApiError(RuntimeError):
    def __init__(self, method, description, error_code=None):
        super().__init__(description)
        self.method = method
        self.description = description
        self.error_code = error_code

_EMPTY_DATA = {
    "config": {
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "telegram_proxy": "",
        "telegram_enabled": False,
        "telegram_bot_enabled": False,
        "telegram_update_offset": 0,
        "schedule_enabled": True,
        "schedule_time": "08:00",
        "schedule_skip_wait": False,
        "schedule_last_run_date": "",
        "cf_account_id": "",
        "cf_api_token": "",
        "cf_browser_keep_alive": "600000",
    },
    "services": {},
    "account": {
        "name": "默认账号",
        "services": [],
        "config": {},
    },
    "login_sessions": {},
    "last_checkin_time": 0,
}

# ── 底层读写 ──

def _loadData():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return _normalizeData(data)


def _saveData(data):
    data = _normalizeData(data)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _normalizeData(data):
    changed = False
    for key, value in _EMPTY_DATA.items():
        if key not in data:
            data[key] = json.loads(json.dumps(value))
            changed = True

    for key, value in _EMPTY_DATA["config"].items():
        if key not in data["config"]:
            data["config"][key] = value
            changed = True

    for key in ("email_server", "email_account", "email_password", "email_notice_type"):
        if key in data["config"]:
            del data["config"][key]
            changed = True

    if "account" not in data or not isinstance(data["account"], dict):
        data["account"] = json.loads(json.dumps(_EMPTY_DATA["account"]))
        changed = True

    if "users" in data and data["users"]:
        first_user = next(iter(data["users"].values()))
        data["account"] = {
            "name": first_user.get("name", "默认账号"),
            "services": first_user.get("services", []),
            "config": first_user.get("config", {}),
        }
        del data["users"]
        changed = True
    elif "users" in data:
        del data["users"]
        changed = True

    account = data["account"]
    account.setdefault("name", "默认账号")
    account.setdefault("services", [])
    account.setdefault("config", {})
    data.setdefault("login_sessions", {})

    for service in data.get("services", {}).values():
        service.setdefault("login_start_command", "")
        service.setdefault("login_poll_command", "")
        service.setdefault("login_cancel_command", "")
        service.setdefault("login_extract_command", "")
        service.setdefault("login_extractors", "[]")
        service.setdefault("credential_template", "")
        service.setdefault("expire_keywords", "")
        service.setdefault("login_enabled", False)
        service.setdefault("login_url", "")
        service.setdefault("login_cookie_domain", "")
        service.setdefault("login_origin", "")
        service.setdefault("login_cookie_names", "")
        service.setdefault("login_local_storage_names", "")
        service.setdefault("login_session_storage_names", "")

    if changed and os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return data


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
            account = {
                "name": info.get("name", "默认账号"),
                "services": [],
                "config": {},
            }
            uc_path = f"users/{uid}.json"
            if os.path.exists(uc_path):
                with open(uc_path, "r", encoding="utf-8") as f:
                    uc = json.load(f)
                account["services"] = uc.get("services", [])
                account["config"] = uc.get("config", {})
            data["account"] = account
            break

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
    data["config"].update(config)
    _saveData(data)


# ── services ──

def loadServices():
    return _loadData()["services"]


def saveServices(services):
    data = _loadData()
    data["services"] = services
    _saveData(data)


def _splitNames(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if not value:
        return []
    return [item.strip() for item in str(value).replace("\n", ",").split(",") if item.strip()]


def buildBrowserRunLoginCommands(service_id, service):
    login_url = service.get("login_url", "").strip()
    if not service.get("login_enabled") or not login_url:
        return {
            "login_start_command": "",
            "login_poll_command": "",
            "login_extract_command": "",
            "login_cancel_command": "",
        }
    adapter = "node logins/browser_run_login.mjs"
    safe_service_id = _quoteShellArg(service_id)
    safe_login_url = _quoteShellArg(login_url)
    return {
        "login_start_command": f"{adapter} start {safe_service_id} {safe_login_url}",
        "login_poll_command": "",
        "login_extract_command": f"{adapter} extract {{session}}",
        "login_cancel_command": f"{adapter} cancel {{session}}",
    }


def buildLoginExtractors(service):
    domain = service.get("login_cookie_domain", "").strip()
    origin = service.get("login_origin", "").strip() or service.get("login_url", "").strip().rstrip("/")
    extractors = []
    for name in _splitNames(service.get("login_cookie_names", "")):
        item = {"source": "cookie", "name": name, "alias": name}
        if domain:
            item["domain"] = domain
        extractors.append(item)
    for name in _splitNames(service.get("login_local_storage_names", "")):
        item = {"source": "localStorage", "name": name, "alias": name}
        if origin:
            item["origin"] = origin
        extractors.append(item)
    for name in _splitNames(service.get("login_session_storage_names", "")):
        item = {"source": "sessionStorage", "name": name, "alias": name}
        if origin:
            item["origin"] = origin
        extractors.append(item)
    return json.dumps(extractors, ensure_ascii=False)


def _quoteShellArg(value):
    text = str(value)
    return '"' + text.replace('"', '\\"') + '"'


def loadLoginSessions():
    return _loadData()["login_sessions"]


def saveLoginSessions(sessions):
    data = _loadData()
    data["login_sessions"] = sessions
    _saveData(data)


# ── account ──

def loadAccount():
    return _loadData()["account"]


def saveAccount(account):
    data = _loadData()
    data["account"] = account
    _saveData(data)


def loadAccountConfig():
    account = loadAccount()
    return {
        "services": account.get("services", []),
        "config": account.get("config", {}),
    }


def saveAccountConfig(cfg):
    data = _loadData()
    data["account"]["services"] = cfg["services"]
    data["account"]["config"] = cfg["config"]
    _saveData(data)


def setCredential(key, value):
    data = _loadData()
    data["account"]["config"][key] = value
    _saveData(data)


def loadUsers():
    account = loadAccount()
    return {"default": {"name": account["name"], "services": account["services"], "config": account["config"]}}


def saveUsers(users):
    data = _loadData()
    if users:
        first_user = next(iter(users.values()))
        data["account"] = {
            "name": first_user.get("name", "默认账号"),
            "services": first_user.get("services", []),
            "config": first_user.get("config", {}),
        }
    _saveData(data)


def loadUserConfig(user_id):
    return loadAccountConfig()


def saveUserConfig(user_id, cfg):
    saveAccountConfig(cfg)


# ── last_checkin_time ──

def loadLastCheckinTime():
    return _loadData()["last_checkin_time"]


def saveLastCheckinTime(t):
    data = _loadData()
    data["last_checkin_time"] = t
    _saveData(data)


def _parseScheduleTime(value):
    try:
        hour, minute = value.strip().split(":", 1)
        hour = int(hour)
        minute = int(minute)
    except Exception:
        raise ValueError("定时执行时间格式应为 HH:MM")
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        raise ValueError("定时执行时间必须在 00:00 到 23:59 之间")
    return hour, minute


def validateScheduleTime(value):
    _parseScheduleTime(value)


# ── 签到执行 ──

_checkin_query = {}
_checkin_query_list = []
_checkin_lock = threading.Lock()
_checkin_run_lock = threading.Lock()


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


def _openTelegram(req, timeout=30):
    config = loadConfig()
    proxy = config.get("telegram_proxy", "").strip()
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({"https": proxy, "http": proxy})
        opener = urllib.request.build_opener(proxy_handler)
        return opener.open(req, timeout=timeout)
    return urllib.request.urlopen(req, timeout=timeout)


def _h(value):
    return html.escape(str(value), quote=False)


def _telegramApi(method, body=None, timeout=30):
    config = loadConfig()
    token = config.get("telegram_bot_token", "")
    if not token:
        raise ValueError("Telegram Bot Token 未配置")
    url = f"https://api.telegram.org/bot{token}/{method}"
    payload = json.dumps(body or {}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with _openTelegram(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode("utf-8"))
        except Exception:
            data = {"ok": False, "description": str(e), "error_code": e.code}
    if not data.get("ok"):
        raise TelegramApiError(
            method,
            data.get("description", f"Telegram API {method} 调用失败"),
            data.get("error_code"),
        )
    return data.get("result")


def _retryWithoutParseMode(method, body, error):
    if not isinstance(error, TelegramApiError):
        raise error
    if error.error_code != 400 or "parse" not in error.description.lower():
        raise error
    fallback = dict(body)
    fallback.pop("parse_mode", None)
    return _telegramApi(method, fallback)


def sendTelegram(text):
    return sendTelegramMessage(text)


def sendTelegramMessage(text, reply_markup=None):
    config = loadConfig()
    token = config.get("telegram_bot_token", "")
    chat_id = config.get("telegram_chat_id", "")
    if not token or not chat_id:
        raise ValueError("Telegram Bot Token 或 Chat ID 未配置")
    body = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        body["reply_markup"] = reply_markup
    try:
        return _telegramApi("sendMessage", body)
    except Exception as e:
        return _retryWithoutParseMode("sendMessage", body, e)


def editTelegramMessage(chat_id, message_id, text, reply_markup=None):
    body = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if reply_markup:
        body["reply_markup"] = reply_markup
    try:
        return _telegramApi("editMessageText", body)
    except Exception as e:
        return _retryWithoutParseMode("editMessageText", body, e)


def answerTelegramCallback(callback_query_id, text=""):
    config = loadConfig()
    token = config.get("telegram_bot_token", "")
    if not token:
        return
    try:
        _telegramApi("answerCallbackQuery", {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": False,
        })
    except Exception:
        pass


def clearTelegramWebhook(log_callback=None):
    try:
        _telegramApi("deleteWebhook", {"drop_pending_updates": False})
        if log_callback:
            log_callback("Telegram webhook 已清理，使用 long polling 监听")
    except Exception as e:
        if log_callback:
            log_callback(f"清理 Telegram webhook 失败: {e}")


def getTelegramUpdates(offset=0):
    body = {
        "timeout": 50,
        "allowed_updates": ["message", "edited_message", "callback_query"],
    }
    if offset:
        body["offset"] = offset
    return _telegramApi("getUpdates", body, timeout=60) or []


def _mask(value):
    if not value:
        return "(未设置)"
    if len(value) <= 6:
        return "*" * len(value)
    return value[:3] + "*" * (len(value) - 6) + value[-3:]


def _serviceHelp():
    services = loadServices()
    if not services:
        return "当前没有配置签到服务。"
    lines = ["服务列表："]
    for sid, svc in services.items():
        key = svc.get("key", "")
        lines.append(f"{sid} - {svc.get('name', sid)}，凭据字段：{key or '(无)'}")
    return "\n".join(lines)


def _mainMenuText():
    config = loadConfig()
    return (
        "<b>AutoCheckinManager</b>\n\n"
        f"定时签到：{'启用' if config.get('schedule_enabled', True) else '禁用'} "
        f"{config.get('schedule_time', '08:00')}\n"
        f"Telegram 通知：{'启用' if config.get('telegram_enabled', False) else '禁用'}\n"
        f"Bot 监听：{'启用' if config.get('telegram_bot_enabled', False) else '禁用'}\n\n"
        "选择下面的菜单继续。"
    )


def _mainKeyboard():
    return [
        [
            {"text": "服务管理", "callback_data": "acm:services"},
            {"text": "账号状态", "callback_data": "acm:status"},
        ],
        [
            {"text": "执行全部签到", "callback_data": "acm:checkin"},
        ],
    ]


def _servicesKeyboard():
    services = loadServices()
    account = loadAccount()
    enabled = set(account.get("services", []))
    rows = []
    for sid, svc in services.items():
        mark = "ON" if sid in enabled else "OFF"
        rows.append([{"text": f"{mark} {svc.get('name', sid)}", "callback_data": f"acm:service:{sid}"}])
    rows.append([{"text": "返回主菜单", "callback_data": "acm:menu"}])
    return rows


def _servicesText():
    services = loadServices()
    if not services:
        return "<b>服务管理</b>\n\n当前没有配置服务，请先在 TUI 中添加服务。"
    return "<b>服务管理</b>\n\n选择一个服务查看详情、启用/禁用、签到或更新登录。"


def _serviceText(sid):
    account = loadAccount()
    services = loadServices()
    sessions = loadLoginSessions()
    svc = services.get(sid)
    if not svc:
        return f"服务 {_h(sid)} 不存在。"
    key = svc.get("key", "")
    credential = account.get("config", {}).get(key, "") if key else ""
    lines = [
        f"<b>{_h(svc.get('name', sid))}</b>",
        f"ID：<code>{_h(sid)}</code>",
        f"状态：{'已启用' if sid in account.get('services', []) else '已禁用'}",
        f"凭据字段：<code>{_h(key or '(无)')}</code>",
        f"凭据：{_h(_mask(credential))}",
        f"远程登录：{'已配置' if svc.get('login_enabled') and svc.get('login_start_command') else '未配置'}",
    ]
    session = sessions.get(sid)
    if session:
        lines.extend([
            "",
            "<b>登录会话</b>",
            f"Session：<code>{_h(session.get('session', ''))}</code>",
            f"状态：{_h(session.get('status', 'waiting'))}",
        ])
        if session.get("pending_preview"):
            lines.append(_h(session["pending_preview"]))
    return "\n".join(lines)


def _serviceKeyboard(sid):
    account = loadAccount()
    services = loadServices()
    sessions = loadLoginSessions()
    svc = services.get(sid, {})
    enabled = sid in account.get("services", [])
    session = sessions.get(sid)
    rows = []
    rows.append([
        {"text": "禁用服务" if enabled else "启用服务", "callback_data": f"acm:disable:{sid}" if enabled else f"acm:enable:{sid}"},
        {"text": "立即签到", "callback_data": f"acm:checkin:{sid}"},
    ])
    if session:
        if session.get("status") == "pending_confirm":
            rows.append([
                {"text": "确认保存", "callback_data": f"acm:login_save:{sid}"},
                {"text": "重新提取", "callback_data": f"acm:login_done:{sid}"},
            ])
        else:
            rows.append([
                {"text": "登录完成", "callback_data": f"acm:login_done:{sid}"},
                {"text": "继续登录页", "callback_data": f"acm:login_continue:{sid}"},
            ])
        rows.append([{"text": "取消登录会话", "callback_data": f"acm:login_cancel:{sid}"}])
    elif svc.get("login_enabled") and svc.get("login_start_command"):
        rows.append([{"text": "更新登录", "callback_data": f"acm:login:{sid}"}])
    rows.append([
        {"text": "刷新", "callback_data": f"acm:service:{sid}"},
        {"text": "返回服务列表", "callback_data": "acm:services"},
    ])
    rows.append([{"text": "主菜单", "callback_data": "acm:menu"}])
    return rows


def _telegramResult(text, keyboard=None, prefer_edit=True):
    if keyboard:
        return {"text": text, "reply_markup": {"inline_keyboard": keyboard}, "prefer_edit": prefer_edit}
    return text


def _sendTelegramResult(result, callback=None):
    if not result:
        return
    if isinstance(result, dict):
        if callback and result.get("prefer_edit", True):
            message = callback.get("message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            message_id = message.get("message_id")
            if chat_id and message_id:
                try:
                    editTelegramMessage(chat_id, message_id, result.get("text", ""), result.get("reply_markup"))
                    return
                except TelegramApiError as e:
                    if e.error_code == 400 and (
                        "message is not modified" in e.description.lower()
                        or "message to edit not found" in e.description.lower()
                    ):
                        return
                except Exception:
                    pass
        sendTelegramMessage(result.get("text", ""), result.get("reply_markup"))
    else:
        sendTelegram(result)


def _runJsonCommand(command, context=None, timeout=120):
    if not command:
        raise ValueError("服务未配置登录适配器命令")
    context = context or {}
    for key, value in context.items():
        command = command.replace("{" + key + "}", str(value))
    config = loadConfig()
    env = os.environ.copy()
    if config.get("cf_account_id"):
        env["CF_ACCOUNT_ID"] = config["cf_account_id"]
    if config.get("cf_api_token"):
        env["CF_API_TOKEN"] = config["cf_api_token"]
    if config.get("cf_browser_keep_alive"):
        env["CF_BROWSER_KEEP_ALIVE"] = str(config["cf_browser_keep_alive"])
    process = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    output = (process.stdout or "").strip()
    if process.returncode != 0:
        error = (process.stderr or output or f"命令退出码 {process.returncode}").strip()
        raise RuntimeError(error)
    if not output:
        return {}
    try:
        return json.loads(output)
    except json.JSONDecodeError as e:
        raise ValueError(f"登录适配器未输出合法 JSON: {e}") from e


def _parseJsonList(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    return json.loads(value)


def _getStorageValue(storage, origin, key):
    if isinstance(storage, dict):
        if origin and isinstance(storage.get(origin), dict):
            return storage[origin].get(key, "")
        return storage.get(key, "")
    if isinstance(storage, list):
        for item in storage:
            if origin and item.get("origin") != origin:
                continue
            values = item.get("values", item)
            if isinstance(values, dict) and key in values:
                return values[key]
    return ""


def _extractCredential(extracted, extractors, template):
    values = {}
    parts = []
    cookies = extracted.get("cookies", [])
    local_storage = extracted.get("localStorage", extracted.get("local_storage", {}))
    session_storage = extracted.get("sessionStorage", extracted.get("session_storage", {}))

    for item in extractors:
        source = item.get("source", "cookie")
        name = item.get("name", "")
        alias = item.get("alias", name)
        domain = item.get("domain", "")
        origin = item.get("origin", "")
        value = ""
        if source == "cookie":
            for cookie in cookies:
                if cookie.get("name") != name:
                    continue
                if domain and domain not in cookie.get("domain", ""):
                    continue
                value = cookie.get("value", "")
                break
            if value:
                parts.append(f"{name}={value}")
        elif source == "localStorage":
            value = _getStorageValue(local_storage, origin, name)
        elif source == "sessionStorage":
            value = _getStorageValue(session_storage, origin, name)
        values[alias] = value

    if template:
        credential = template
        for key, value in values.items():
            credential = credential.replace("{" + key + "}", str(value))
        return credential
    if parts:
        return "; ".join(parts)
    return json.dumps(values, ensure_ascii=False)


def _credentialPreview(credential):
    text = str(credential)
    if len(text) <= 24:
        masked = _mask(text)
    else:
        masked = text[:10] + "*" * min(24, max(6, len(text) - 20)) + text[-10:]
    return f"长度：{len(text)}\n预览：{masked}"


def _saveLoginSession(sid, session):
    sessions = loadLoginSessions()
    sessions[sid] = session
    saveLoginSessions(sessions)


def _removeLoginSession(sid):
    sessions = loadLoginSessions()
    if sid in sessions:
        del sessions[sid]
        saveLoginSessions(sessions)


def startServiceLogin(sid):
    services = loadServices()
    if sid not in services:
        return _telegramResult(f"服务 {sid} 不存在。\n\n{_serviceHelp()}", _mainKeyboard())
    svc = services[sid]
    try:
        result = _runJsonCommand(svc.get("login_start_command", ""), {
            "service_id": sid,
            "service_name": svc.get("name", sid),
        })
    except Exception as e:
        return _telegramResult(f"启动登录失败：{e}", _serviceKeyboard(sid))

    session_id = result.get("session") or generateRandomID()
    _saveLoginSession(sid, {
        "session": session_id,
        "started_at": time.time(),
        "status": "waiting",
        "live_url": result.get("live_url") or result.get("url") or "",
        "message": result.get("message", ""),
    })

    lines = [f"{svc.get('name', sid)} 登录会话已创建。"]
    lines.append(f"Session：<code>{_h(session_id)}</code>")
    if result.get("message"):
        lines.append(_h(result["message"]))
    live_url = result.get("live_url") or result.get("url")
    if live_url:
        lines.append(f"\n打开链接完成登录：\n{_h(live_url)}")
    lines.append("\n完成后点下面的“登录完成”。")
    return _telegramResult("\n".join(lines), _serviceKeyboard(sid))


def finishServiceLogin(sid):
    services = loadServices()
    sessions = loadLoginSessions()
    if sid not in services:
        return _telegramResult(f"服务 {sid} 不存在。", _mainKeyboard())
    if sid not in sessions:
        return _telegramResult("没有正在进行的登录会话，请先点“更新登录”。", _serviceKeyboard(sid))

    svc = services[sid]
    session = sessions[sid]
    context = {
        "service_id": sid,
        "service_name": svc.get("name", sid),
        "session": session.get("session", ""),
        "live_url": session.get("live_url", ""),
    }

    try:
        poll_result = {}
        if svc.get("login_poll_command"):
            poll_result = _runJsonCommand(svc["login_poll_command"], context)
            status = poll_result.get("status", "")
            if status and status not in ("ok", "done", "confirmed", "success"):
                return _telegramResult(poll_result.get("message", "登录尚未完成。"), _serviceKeyboard(sid))

        if svc.get("login_extract_command"):
            extracted = _runJsonCommand(svc["login_extract_command"], context)
        else:
            extracted = poll_result

        credential = extracted.get("credential", "")
        if not credential:
            extractors = _parseJsonList(svc.get("login_extractors", "[]"))
            credential = _extractCredential(extracted, extractors, svc.get("credential_template", ""))
        if not credential:
            return _telegramResult("没有提取到登录凭据，请检查服务的提取配置。", _serviceKeyboard(sid))

        if not svc.get("key"):
            return _telegramResult("服务没有配置凭据字段 key，无法保存。", _serviceKeyboard(sid))

        sessions = loadLoginSessions()
        session = sessions.get(sid, {})
        session["status"] = "pending_confirm"
        session["pending_credential"] = credential
        session["pending_preview"] = _credentialPreview(credential)
        sessions[sid] = session
        saveLoginSessions(sessions)

        return _telegramResult(
            _serviceText(sid),
            _serviceKeyboard(sid),
        )
    except Exception as e:
        return _telegramResult(f"完成登录失败：{e}", _serviceKeyboard(sid))


def savePendingCredential(sid):
    services = loadServices()
    sessions = loadLoginSessions()
    if sid not in services:
        return _telegramResult(f"服务 {sid} 不存在。", _mainKeyboard())
    session = sessions.get(sid, {})
    credential = session.get("pending_credential", "")
    if not credential:
        return _telegramResult("没有等待确认的凭据，请先完成登录并提取。", _serviceKeyboard(sid))

    svc = services[sid]
    key = svc.get("key")
    if not key:
        return _telegramResult("服务没有配置凭据字段 key，无法保存。", _serviceKeyboard(sid))
    setCredential(key, credential)
    account = loadAccount()
    if sid not in account["services"]:
        account["services"].append(sid)
        saveAccount(account)
    _removeLoginSession(sid)
    return _telegramResult(_serviceText(sid), _serviceKeyboard(sid))


def continueServiceLogin(sid):
    services = loadServices()
    sessions = loadLoginSessions()
    if sid not in services:
        return _telegramResult(f"服务 {sid} 不存在。", _mainKeyboard())
    session = sessions.get(sid)
    if not session:
        return _telegramResult("没有正在进行的登录会话，请先点“更新登录”。", _serviceKeyboard(sid))
    live_url = session.get("live_url", "")
    if live_url:
        return _telegramResult(
            f"Session：<code>{_h(session.get('session', ''))}</code>\n\n继续在这个页面完成登录：\n{_h(live_url)}\n\n完成后点“登录完成”。",
            _serviceKeyboard(sid),
        )
    return _telegramResult("当前登录会话没有可打开的 Live View 链接。", _serviceKeyboard(sid))


def cancelServiceLogin(sid):
    services = loadServices()
    svc = services.get(sid, {})
    sessions = loadLoginSessions()
    session = sessions.get(sid, {})
    if svc.get("login_cancel_command") and session:
        try:
            _runJsonCommand(svc["login_cancel_command"], {
                "service_id": sid,
                "service_name": svc.get("name", sid),
                "session": session.get("session", ""),
                "live_url": session.get("live_url", ""),
            }, timeout=30)
        except Exception:
            pass
    _removeLoginSession(sid)
    return _telegramResult(_serviceText(sid), _serviceKeyboard(sid))


def serviceStatusText(sid=None):
    account = loadAccount()
    services = loadServices()
    sessions = loadLoginSessions()
    if sid:
        svc = services.get(sid)
        if not svc:
            return f"服务 {sid} 不存在。"
        key = svc.get("key", "")
        credential = account.get("config", {}).get(key, "") if key else ""
        lines = [
            f"服务：{svc.get('name', sid)} ({sid})",
            f"启用：{'是' if sid in account.get('services', []) else '否'}",
            f"凭据字段：{key or '(无)'}",
            f"凭据：{_mask(credential)}",
        ]
        if sid in sessions:
            lines.append("登录会话：进行中")
        return "\n".join(lines)

    enabled = account.get("services", [])
    lines = [f"账号：{account.get('name', '默认账号')}", "启用服务：" + (", ".join(enabled) if enabled else "(无)")]
    for item_sid in enabled:
        svc = services.get(item_sid, {})
        key = svc.get("key")
        if key:
            lines.append(f"{item_sid} 凭据：{_mask(account.get('config', {}).get(key, ''))}")
    if sessions:
        lines.append("登录会话：" + ", ".join(sessions.keys()))
    return "\n".join(lines)


def _splitKeywords(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if not value:
        return []
    return [item.strip() for item in str(value).replace("\n", ",").split(",") if item.strip()]


def handleTelegramCommand(text):
    parts = text.strip().split(maxsplit=2)
    command = parts[0].split("@", 1)[0].lower() if parts else ""
    account = loadAccount()
    services = loadServices()

    if command in ("/start", "/help"):
        return _telegramResult(_mainMenuText(), _mainKeyboard())

    if command == "/services":
        return _telegramResult(_servicesText(), _servicesKeyboard())

    if command == "/status":
        sid = parts[1] if len(parts) >= 2 else None
        return _telegramResult(_serviceText(sid) if sid else serviceStatusText(), _serviceKeyboard(sid) if sid else _mainKeyboard())

    if command in ("/enable", "/disable"):
        if len(parts) < 2:
            return f"用法：{command} <服务ID>"
        sid = parts[1]
        if sid not in services:
            return f"服务 {sid} 不存在。\n\n{_serviceHelp()}"
        enabled = account.setdefault("services", [])
        if command == "/enable" and sid not in enabled:
            enabled.append(sid)
        if command == "/disable" and sid in enabled:
            enabled.remove(sid)
        saveAccount(account)
        return _telegramResult(_serviceText(sid), _serviceKeyboard(sid))

    if command == "/set":
        if len(parts) < 3:
            return "用法：/set <服务ID> <凭据>"
        sid, value = parts[1], parts[2]
        if sid not in services:
            return f"服务 {sid} 不存在。\n\n{_serviceHelp()}"
        key = services[sid].get("key")
        if not key:
            return f"服务 {sid} 没有配置凭据字段。"
        setCredential(key, value)
        account = loadAccount()
        if sid not in account["services"]:
            account["services"].append(sid)
            saveAccount(account)
        return _telegramResult(f"已更新 {services[sid].get('name', sid)} 的登录凭据，并启用该服务。", _serviceKeyboard(sid))

    if command == "/setkey":
        if len(parts) < 3:
            return "用法：/setkey <字段名> <凭据>"
        setCredential(parts[1], parts[2])
        return _telegramResult(f"已更新字段 <code>{_h(parts[1])}</code>。", _mainKeyboard())

    if command == "/login":
        if len(parts) < 2:
            return _telegramResult("用法：/login <服务ID>", _mainKeyboard())
        return startServiceLogin(parts[1])

    if command == "/done":
        if len(parts) < 2:
            return _telegramResult("用法：/done <服务ID>", _mainKeyboard())
        return finishServiceLogin(parts[1])

    if command == "/confirm-login":
        if len(parts) < 2:
            return _telegramResult("用法：/confirm-login <服务ID>", _mainKeyboard())
        return savePendingCredential(parts[1])

    if command == "/cancel-login":
        if len(parts) < 2:
            return _telegramResult("用法：/cancel-login <服务ID>", _mainKeyboard())
        return cancelServiceLogin(parts[1])

    if command == "/checkin":
        only_service = parts[1] if len(parts) >= 2 else None
        if only_service and only_service not in services:
            return f"服务 {only_service} 不存在。\n\n{_serviceHelp()}"
        threading.Thread(
            target=checkin,
            kwargs={"skip_wait_time": True, "only_service": only_service, "telegram_notice": True},
            daemon=True,
        ).start()
        return _telegramResult("已开始执行签到，完成后会发送 Telegram 通知。", _serviceKeyboard(only_service) if only_service else _mainKeyboard())

    return _telegramResult("未知命令。发送 /help 查看可用命令。", _mainKeyboard())


def handleTelegramCallback(data):
    parts = data.split(":")
    if len(parts) < 2 or parts[0] != "acm":
        return None
    action = parts[1]
    sid = parts[2] if len(parts) >= 3 else None
    if action == "status":
        return _telegramResult(_serviceText(sid) if sid else serviceStatusText(), _serviceKeyboard(sid) if sid else _mainKeyboard())
    if action == "menu":
        return _telegramResult(_mainMenuText(), _mainKeyboard())
    if action == "services":
        return _telegramResult(_servicesText(), _servicesKeyboard())
    if action == "service" and sid:
        return _telegramResult(_serviceText(sid), _serviceKeyboard(sid))
    if action in ("enable", "disable") and sid:
        services = loadServices()
        if sid not in services:
            return _telegramResult(f"服务 {_h(sid)} 不存在。", _servicesKeyboard())
        account = loadAccount()
        enabled = account.setdefault("services", [])
        if action == "enable" and sid not in enabled:
            enabled.append(sid)
        if action == "disable" and sid in enabled:
            enabled.remove(sid)
        saveAccount(account)
        return _telegramResult(_serviceText(sid), _serviceKeyboard(sid))
    if action == "login" and sid:
        return startServiceLogin(sid)
    if action == "login_done" and sid:
        return finishServiceLogin(sid)
    if action == "login_save" and sid:
        return savePendingCredential(sid)
    if action == "login_continue" and sid:
        return continueServiceLogin(sid)
    if action == "login_cancel" and sid:
        return cancelServiceLogin(sid)
    if action == "checkin":
        if sid and sid not in loadServices():
            return _telegramResult(f"服务 {sid} 不存在。", _mainKeyboard())
        threading.Thread(
            target=checkin,
            kwargs={"skip_wait_time": True, "only_service": sid, "telegram_notice": True},
            daemon=True,
        ).start()
        return _telegramResult("已开始执行签到，完成后会发送 Telegram 通知。", _serviceKeyboard(sid) if sid else _mainKeyboard())
    return _telegramResult("这个按钮动作暂不支持。", _mainKeyboard())


_bot_thread = None
_bot_stop_event = threading.Event()


def startTelegramBot(log_callback=None):
    global _bot_thread
    if _bot_thread and _bot_thread.is_alive():
        return False
    _bot_stop_event.clear()
    clearTelegramWebhook(log_callback)
    _bot_thread = threading.Thread(target=_telegramBotLoop, args=(log_callback,), daemon=True)
    _bot_thread.start()
    return True


def stopTelegramBot():
    _bot_stop_event.set()


def telegramBotRunning():
    return bool(_bot_thread and _bot_thread.is_alive())


def _telegramBotLoop(log_callback=None):
    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    log("Telegram Bot 命令监听已启动")
    while not _bot_stop_event.is_set():
        config = loadConfig()
        if not config.get("telegram_bot_enabled", False):
            time.sleep(BOT_POLL_INTERVAL)
            continue
        try:
            offset = int(config.get("telegram_update_offset", 0) or 0)
            updates = getTelegramUpdates(offset)
            for update in updates:
                update_id = update.get("update_id", 0)
                saveConfig({"telegram_update_offset": update_id + 1})
                callback = update.get("callback_query") or {}
                if callback:
                    message = callback.get("message") or {}
                    chat = message.get("chat") or {}
                    chat_id = str(chat.get("id", ""))
                    allowed_chat_id = str(config.get("telegram_chat_id", ""))
                    if allowed_chat_id and chat_id != allowed_chat_id:
                        continue
                    answerTelegramCallback(callback.get("id", ""), "处理中")
                    reply = handleTelegramCallback(callback.get("data", ""))
                    _sendTelegramResult(reply, callback=callback)
                    continue
                message = update.get("message") or update.get("edited_message") or {}
                chat = message.get("chat") or {}
                chat_id = str(chat.get("id", ""))
                allowed_chat_id = str(config.get("telegram_chat_id", ""))
                if allowed_chat_id and chat_id != allowed_chat_id:
                    continue
                text = message.get("text", "")
                if not text.startswith("/"):
                    continue
                reply = handleTelegramCommand(text)
                _sendTelegramResult(reply)
        except TelegramApiError as e:
            desc = e.description or str(e)
            if e.error_code == 409:
                log(
                    "Telegram Bot 监听冲突：getUpdates 被另一个实例或 webhook 占用。"
                    "请确认服务器上只运行一个 AutoCheckinManager，或等待 webhook 清理后重试。"
                )
                time.sleep(30)
                continue
            if e.error_code == 400:
                log(f"Telegram Bot 请求格式错误 ({e.method}): {desc}")
                if "webhook" in desc.lower():
                    clearTelegramWebhook(log_callback)
                time.sleep(10)
                continue
            log(f"Telegram Bot API 错误 ({e.method}/{e.error_code}): {desc}")
            time.sleep(10)
        except Exception as e:
            log(f"Telegram Bot 监听错误: {e}")
            time.sleep(10)
    log("Telegram Bot 命令监听已停止")


_scheduler_thread = None
_scheduler_stop_event = threading.Event()
_scheduler_checkin_lock = threading.Lock()


def startScheduler(log_callback=None):
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        return False
    _scheduler_stop_event.clear()
    _scheduler_thread = threading.Thread(target=_schedulerLoop, args=(log_callback,), daemon=True)
    _scheduler_thread.start()
    return True


def stopScheduler():
    _scheduler_stop_event.set()


def schedulerRunning():
    return bool(_scheduler_thread and _scheduler_thread.is_alive())


def startDaemon(log_callback=None):
    config = loadConfig()
    if config.get("telegram_bot_enabled", False):
        startTelegramBot(log_callback=log_callback)
    return startScheduler(log_callback=log_callback)


def stopDaemon():
    stopScheduler()
    stopTelegramBot()


def _runScheduledCheckin(skip_wait_time, log_callback=None):
    checkin(skip_wait_time=skip_wait_time, telegram_notice=True, log_callback=log_callback)


def _schedulerLoop(log_callback=None):
    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    log("定时签到调度器已启动")
    while not _scheduler_stop_event.is_set():
        try:
            config = loadConfig()
            if config.get("schedule_enabled", True):
                schedule_time = config.get("schedule_time", "08:00")
                hour, minute = _parseScheduleTime(schedule_time)
                now = time.localtime()
                today = time.strftime("%Y-%m-%d", now)
                last_run_date = config.get("schedule_last_run_date", "")
                if (now.tm_hour, now.tm_min) >= (hour, minute) and last_run_date != today:
                    saveConfig({"schedule_last_run_date": today})
                    log(f"到达定时签到时间 {schedule_time}，开始执行")
                    threading.Thread(
                        target=_runScheduledCheckin,
                        args=(config.get("schedule_skip_wait", False), log_callback),
                        daemon=True,
                    ).start()
            time.sleep(SCHEDULER_POLL_INTERVAL)
        except Exception as e:
            log(f"定时签到调度器错误: {e}")
            time.sleep(10)
    log("定时签到调度器已停止")


def checkin(skip_wait_time=False, only_service=None, telegram_notice=True, log_callback=None, **kwargs):
    global _checkin_query, _checkin_query_list

    def log(msg):
        print(msg)
        if log_callback:
            log_callback(msg)

    if not _checkin_run_lock.acquire(blocking=False):
        log("已有签到任务正在执行，本次请求已跳过")
        return

    try:
        config = loadConfig()
        results = {}
        delays = []
        account = loadAccount()
        account_config = loadAccountConfig()
        services = loadServices()

        with _checkin_lock:
            _checkin_query = {}
            _checkin_query_list = []

        results["default"] = {}
        for skey in services:
            if only_service and skey != only_service:
                continue
            service = services[skey]
            if skey not in account_config["services"]:
                continue
            delay = 0 if skip_wait_time else random.randint(service["wait_time_min"], service["wait_time_max"])
            delays.append(delay)
            command = service["command"].replace("{config}", account_config["config"].get(service["key"], ""))
            qi = generateRandomID()
            results["default"][skey] = qi
            with _checkin_lock:
                _checkin_query_list.append(qi)
            log(f"[{account['name']}] 启动服务 {service['name']}，等待 {delay} 秒")
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

        expired_services = []
        for ukey in results:
            for skey in results[ukey]:
                output = _checkin_query[results[ukey][skey]]
                keywords = _splitKeywords(services[skey].get("expire_keywords", ""))
                if keywords and any(keyword in output for keyword in keywords):
                    expired_services.append(skey)
                    log(f"服务 {services[skey]['name']} 可能登录过期")

        if telegram_notice and config.get("telegram_enabled", False):
            try:
                tg_body = ""
                for ukey in results:
                    tg_body += genTelegramUser(account['name'])
                    for skey in results[ukey]:
                        output = _checkin_query[results[ukey][skey]]
                        tg_body += genTelegramService(services[skey]["name"], output)
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
                tg_text = genTelegramMessage(dt, tg_body)
                if len(tg_text) > 4000:
                    tg_text = tg_text[:4000] + "\n\n<i>... 内容过长已截断</i>"
                sendTelegram(tg_text)
                log("已发送 Telegram 通知")
                for skey in expired_services:
                    sendTelegramMessage(
                        f"{services[skey]['name']} 的登录凭据可能已过期，请更新登录。",
                        {"inline_keyboard": _serviceKeyboard(skey)},
                    )
            except Exception as e:
                log(f"Telegram 通知发送失败: {e}")
    finally:
        _checkin_run_lock.release()
