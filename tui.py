import os
import time
import threading
from urllib.parse import urlparse
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, TabbedContent, TabPane,
    ListView, ListItem, Label, Input, Button,
    Checkbox, RichLog, Static,
)
from textual.binding import Binding
import core


class ServiceTab(TabPane):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="service-list-panel"):
                yield Label("服务列表", classes="panel-title")
                yield ListView(id="service-list")
                yield Button("新建服务", id="btn-new-service", variant="primary")
            with VerticalScroll(id="service-edit-panel"):
                yield Label("服务设置", classes="panel-title")
                yield Label("ID")
                yield Input(id="service-id", placeholder="服务ID")
                yield Label("名称")
                yield Input(id="service-name", placeholder="服务名称")
                yield Label("命令 (使用 {config} 填充配置值)")
                yield Input(id="service-command", placeholder="签到命令")
                yield Label("配置文件字段")
                yield Input(id="service-config-key", placeholder="配置键名")
                yield Label("远程登录", classes="panel-title")
                yield Checkbox("启用 Browser Run 交互式登录", id="service-login-enabled")
                yield Static(
                    "工作方式：Telegram 中点击服务登录后，程序会在 Cloudflare Browser Run 打开登录页，并把远程浏览器链接发给你。你在手机上完成登录，回 Telegram 点“登录完成”，程序会提取 Cookie / localStorage / sessionStorage，先显示掩码摘要，确认后才保存。",
                    classes="help-text",
                )
                yield Label("登录页 URL")
                yield Input(id="service-login-url", placeholder="https://example.com/login")
                yield Label("Cookie 域名")
                yield Input(id="service-login-cookie-domain", placeholder=".example.com（可留空）")
                yield Label("存储 Origin")
                yield Input(id="service-login-origin", placeholder="https://example.com（留空则由登录 URL 推断）")
                yield Label("要提取的 Cookie 名称")
                yield Input(id="service-login-cookie-names", placeholder="多个用逗号分隔，例如 sid, session")
                yield Label("要提取的 localStorage 键")
                yield Input(id="service-login-local-storage", placeholder="多个用逗号分隔，例如 token, userInfo")
                yield Label("要提取的 sessionStorage 键")
                yield Input(id="service-login-session-storage", placeholder="多个用逗号分隔，例如 csrf")
                yield Label("凭据模板")
                yield Input(id="service-credential-template", placeholder="例如 sid={sid}; token={token}；留空则自动拼 Cookie 或保存 JSON")
                yield Label("过期关键词")
                yield Input(id="service-expire-keywords", placeholder="用逗号分隔，例如 登录过期,401,unauthorized")
                yield Label("随机等待时间（秒）")
                with Horizontal(classes="wait-time-row"):
                    yield Input(id="service-wait-min", placeholder="最小", type="integer")
                    yield Label(" 至 ", classes="wait-time-label")
                    yield Input(id="service-wait-max", placeholder="最大", type="integer")
                with Horizontal(classes="button-row"):
                    yield Button("保存", id="btn-save-service", variant="success")
                    yield Button("删除", id="btn-delete-service", variant="error")

    def on_mount(self) -> None:
        self._refresh_list()

    def _refresh_list(self) -> None:
        lv = self.query_one("#service-list", ListView)
        lv.clear()
        services = core.loadServices()
        for key in services:
            lv.append(ListItem(Label(f"{key} - {services[key]['name']}"), name=key))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        sid = event.item.name
        services = core.loadServices()
        if sid not in services:
            return
        s = services[sid]
        self.query_one("#service-id", Input).value = sid
        self.query_one("#service-name", Input).value = s["name"]
        self.query_one("#service-command", Input).value = s["command"]
        self.query_one("#service-config-key", Input).value = s["key"]
        self.query_one("#service-login-enabled", Checkbox).value = s.get("login_enabled", False)
        self.query_one("#service-login-url", Input).value = s.get("login_url", "")
        self.query_one("#service-login-cookie-domain", Input).value = s.get("login_cookie_domain", "")
        self.query_one("#service-login-origin", Input).value = s.get("login_origin", "")
        self.query_one("#service-login-cookie-names", Input).value = s.get("login_cookie_names", "")
        self.query_one("#service-login-local-storage", Input).value = s.get("login_local_storage_names", "")
        self.query_one("#service-login-session-storage", Input).value = s.get("login_session_storage_names", "")
        self.query_one("#service-credential-template", Input).value = s.get("credential_template", "")
        self.query_one("#service-expire-keywords", Input).value = s.get("expire_keywords", "")
        self.query_one("#service-wait-min", Input).value = str(s["wait_time_min"])
        self.query_one("#service-wait-max", Input).value = str(s["wait_time_max"])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-new-service":
            self._new_service()
        elif event.button.id == "btn-save-service":
            self._save_service()
        elif event.button.id == "btn-delete-service":
            self._delete_service()

    def _new_service(self) -> None:
        import random
        self.query_one("#service-id", Input).value = f"new_service_{random.randint(100, 999)}"
        self.query_one("#service-name", Input).value = ""
        self.query_one("#service-command", Input).value = ""
        self.query_one("#service-config-key", Input).value = ""
        self.query_one("#service-login-enabled", Checkbox).value = False
        self.query_one("#service-login-url", Input).value = ""
        self.query_one("#service-login-cookie-domain", Input).value = ""
        self.query_one("#service-login-origin", Input).value = ""
        self.query_one("#service-login-cookie-names", Input).value = ""
        self.query_one("#service-login-local-storage", Input).value = ""
        self.query_one("#service-login-session-storage", Input).value = ""
        self.query_one("#service-credential-template", Input).value = ""
        self.query_one("#service-expire-keywords", Input).value = ""
        self.query_one("#service-wait-min", Input).value = "0"
        self.query_one("#service-wait-max", Input).value = "0"

    def _save_service(self) -> None:
        sid = self.query_one("#service-id", Input).value.strip()
        if not sid:
            self.app.notify("服务ID不能为空", severity="error")
            return
        login_url = self.query_one("#service-login-url", Input).value.strip()
        login_enabled = self.query_one("#service-login-enabled", Checkbox).value
        if login_enabled:
            if not login_url:
                self.app.notify("启用远程登录时必须填写登录页 URL", severity="error")
                return
            parsed = urlparse(login_url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                self.app.notify("登录页 URL 必须是完整的 http/https 地址", severity="error")
                return

        services = core.loadServices()
        service = {
            "name": self.query_one("#service-name", Input).value,
            "command": self.query_one("#service-command", Input).value,
            "key": self.query_one("#service-config-key", Input).value,
            "login_enabled": login_enabled,
            "login_url": login_url,
            "login_cookie_domain": self.query_one("#service-login-cookie-domain", Input).value,
            "login_origin": self.query_one("#service-login-origin", Input).value,
            "login_cookie_names": self.query_one("#service-login-cookie-names", Input).value,
            "login_local_storage_names": self.query_one("#service-login-local-storage", Input).value,
            "login_session_storage_names": self.query_one("#service-login-session-storage", Input).value,
            "credential_template": self.query_one("#service-credential-template", Input).value,
            "expire_keywords": self.query_one("#service-expire-keywords", Input).value,
            "wait_time_min": int(self.query_one("#service-wait-min", Input).value or 0),
            "wait_time_max": int(self.query_one("#service-wait-max", Input).value or 0),
        }
        service.update(core.buildBrowserRunLoginCommands(sid, service))
        service["login_extractors"] = core.buildLoginExtractors(service)
        if login_enabled:
            config = core.loadConfig()
            missing = []
            if not config.get("cf_account_id"):
                missing.append("Cloudflare Account ID")
            if not config.get("cf_api_token"):
                missing.append("Cloudflare API Token")
            if missing:
                self.app.notify("远程登录已启用，但还未配置：" + "、".join(missing), severity="warning")
        services[sid] = service
        core.saveServices(services)
        self._refresh_list()
        self.app.notify(f"服务 {sid} 保存成功")

    def _delete_service(self) -> None:
        sid = self.query_one("#service-id", Input).value.strip()
        if not sid:
            return
        services = core.loadServices()
        if sid in services:
            del services[sid]
            core.saveServices(services)
            self._refresh_list()
            self._new_service()
            self.app.notify(f"服务 {sid} 已删除")
        else:
            self.app.notify(f"服务 {sid} 不存在", severity="error")


class AccountTab(TabPane):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("账号设置", classes="panel-title")
            yield Label("账号名称")
            yield Input(id="account-name", placeholder="默认账号")
            yield Static("Telegram Bot 可使用 /set <服务ID> <凭据> 或 /setkey <字段名> <凭据> 修改下方登录凭据。", classes="tg-hint")
            yield Label("服务与登录凭据", classes="panel-title")
            services = core.loadServices()
            account = core.loadAccount()
            enabled = account.get("services", [])
            config_vals = account.get("config", {})
            if not services:
                yield Label("没有可用的签到服务，请先创建服务。")
            for sid, svc in services.items():
                with Vertical(classes="account-service-block"):
                    yield Checkbox(
                        f"{svc['name']}  ({sid})",
                        value=(sid in enabled),
                        id=f"account-cb-{sid}",
                    )
                    if svc.get("key"):
                        yield Label(
                            f"配置字段 [{svc['key']}]（填入命令中 {{config}} 的值）",
                            classes="account-config-label",
                        )
                        yield Input(
                            value=config_vals.get(svc["key"], ""),
                            placeholder=f"输入 {svc['key']} 的值",
                            id=f"account-input-{sid}",
                            classes="account-config-input",
                        )
            yield Button("保存账号配置", id="btn-save-account", variant="success")

    def on_mount(self) -> None:
        account = core.loadAccount()
        self.query_one("#account-name", Input).value = account.get("name", "默认账号")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-account":
            self._save_account()

    def _save_account(self) -> None:
        name = self.query_one("#account-name", Input).value.strip()
        if not name:
            self.app.notify("账号名称不能为空", severity="error")
            return
        services = core.loadServices()
        enabled = []
        config_vals = {}
        for sid, svc in services.items():
            cb = self.query_one(f"#account-cb-{sid}", Checkbox)
            if cb.value:
                enabled.append(sid)
            if svc.get("key"):
                inp = self.query_one(f"#account-input-{sid}", Input)
                if inp.value:
                    config_vals[svc["key"]] = inp.value
        core.saveAccount({"name": name, "services": enabled, "config": config_vals})
        self.app.notify("账号配置保存成功")


class TelegramTab(TabPane):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("Telegram 配置", classes="panel-title")
            yield Checkbox("启用 Telegram 通知", id="tg-enabled")
            yield Checkbox("启用 Bot 命令监听", id="tg-bot-enabled")
            yield Label("Bot Token")
            yield Input(id="tg-bot-token", placeholder="从 @BotFather 获取")
            yield Label("Chat ID")
            yield Input(id="tg-chat-id", placeholder="目标聊天/群组 ID")
            yield Label("代理地址")
            yield Input(id="tg-proxy", placeholder="例如 http://127.0.0.1:7890（留空不使用）")
            yield Label("远程浏览器登录", classes="panel-title")
            yield Static(
                "用于 Telegram 的交互式登录。服务启用 Browser Run 登录后，Bot 会创建远程浏览器并发送可操作链接；登录完成后会提取 Cookie / localStorage / sessionStorage，并在确认后保存。",
                classes="help-text",
            )
            yield Label("Cloudflare Account ID")
            yield Input(id="cf-account-id", placeholder="Cloudflare Account ID")
            yield Label("Cloudflare API Token")
            yield Input(id="cf-api-token", placeholder="需要 Browser Run 权限", password=True)
            yield Label("浏览器会话保持时间（毫秒）")
            yield Input(id="cf-keep-alive", placeholder="默认 600000，即 10 分钟", type="integer")
            yield Static("Bot 命令：/help /status /services /login /done /confirm-login /checkin。常用操作会通过按钮出现。", classes="tg-hint")
            with Horizontal(classes="button-row"):
                yield Button("保存配置", id="btn-save-telegram", variant="success")
                yield Button("发送测试", id="btn-test-telegram", variant="primary")
                yield Button("启动监听", id="btn-start-bot", variant="warning")
                yield Button("停止监听", id="btn-stop-bot", variant="default")
            yield RichLog(id="telegram-log", wrap=True, markup=True)

    def on_mount(self) -> None:
        config = core.loadConfig()
        self.query_one("#tg-enabled", Checkbox).value = config.get("telegram_enabled", False)
        self.query_one("#tg-bot-enabled", Checkbox).value = config.get("telegram_bot_enabled", False)
        self.query_one("#tg-bot-token", Input).value = config.get("telegram_bot_token", "")
        self.query_one("#tg-chat-id", Input).value = config.get("telegram_chat_id", "")
        self.query_one("#tg-proxy", Input).value = config.get("telegram_proxy", "")
        self.query_one("#cf-account-id", Input).value = config.get("cf_account_id", "")
        self.query_one("#cf-api-token", Input).value = config.get("cf_api_token", "")
        self.query_one("#cf-keep-alive", Input).value = str(config.get("cf_browser_keep_alive", "600000"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-telegram":
            self._save_config()
        elif event.button.id == "btn-test-telegram":
            self._test_send()
        elif event.button.id == "btn-start-bot":
            self._start_bot()
        elif event.button.id == "btn-stop-bot":
            self._stop_bot()

    def _save_config(self) -> None:
        config = {
            "telegram_enabled": self.query_one("#tg-enabled", Checkbox).value,
            "telegram_bot_enabled": self.query_one("#tg-bot-enabled", Checkbox).value,
            "telegram_bot_token": self.query_one("#tg-bot-token", Input).value,
            "telegram_chat_id": self.query_one("#tg-chat-id", Input).value,
            "telegram_proxy": self.query_one("#tg-proxy", Input).value,
            "cf_account_id": self.query_one("#cf-account-id", Input).value,
            "cf_api_token": self.query_one("#cf-api-token", Input).value,
            "cf_browser_keep_alive": self.query_one("#cf-keep-alive", Input).value or "600000",
        }
        core.saveConfig(config)
        self.app.notify("Telegram 配置保存成功")

    def _test_send(self) -> None:
        self._save_config()
        try:
            core.sendTelegram("✅ <b>AutoCheckinManager</b>\n\nTelegram 通知功能测试成功！")
            self.app.notify("测试消息发送成功")
        except Exception as e:
            self.app.notify(f"发送失败: {e}", severity="error")

    def _start_bot(self) -> None:
        self._save_config()
        log_widget = self.query_one("#telegram-log", RichLog)

        def log_callback(msg):
            self.app.call_from_thread(log_widget.write, msg)

        started = core.startTelegramBot(log_callback=log_callback)
        if started:
            self.app.notify("Telegram Bot 监听已启动")
        else:
            self.app.notify("Telegram Bot 监听已在运行")

    def _stop_bot(self) -> None:
        core.stopTelegramBot()
        self.app.notify("Telegram Bot 监听停止请求已发送")


class CheckinTab(TabPane):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("定时运行", classes="panel-title")
            with Horizontal(classes="option-row"):
                yield Checkbox("启用每日定时签到", id="schedule-enabled")
                yield Checkbox("定时签到跳过随机等待", id="schedule-skip-wait")
            yield Label("每日执行时间")
            yield Input(id="schedule-time", placeholder="HH:MM，例如 08:00")
            with Horizontal(classes="button-row"):
                yield Button("保存定时配置", id="btn-save-schedule", variant="success")
                yield Button("启动常驻调度", id="btn-start-scheduler", variant="warning")
                yield Button("停止常驻调度", id="btn-stop-scheduler", variant="default")
            yield Label("签到选项", classes="panel-title")
            with Horizontal(classes="option-row"):
                yield Checkbox("跳过随机等待", id="opt-skip-wait", value=True)
                yield Checkbox("发送Telegram通知", id="opt-tg-notice")
            yield Label("仅执行指定服务（留空=全部）")
            yield Input(id="opt-only-service", placeholder="服务ID（留空执行全部）")
            with Horizontal(classes="button-row"):
                yield Button("执行签到", id="btn-run-checkin", variant="warning")
            yield Label("", id="last-checkin-time")
            yield RichLog(id="checkin-log", wrap=True, markup=True)

    def on_mount(self) -> None:
        self._load_schedule()
        self._update_last_time()

    def _load_schedule(self) -> None:
        config = core.loadConfig()
        self.query_one("#schedule-enabled", Checkbox).value = config.get("schedule_enabled", True)
        self.query_one("#schedule-skip-wait", Checkbox).value = config.get("schedule_skip_wait", False)
        self.query_one("#schedule-time", Input).value = config.get("schedule_time", "08:00")

    def _update_last_time(self) -> None:
        t = core.loadLastCheckinTime()
        if t > 0:
            text = f"上次签到时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))}"
        else:
            text = "上次签到时间：从未执行"
        self.query_one("#last-checkin-time", Label).update(text)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run-checkin":
            self._run_checkin()
        elif event.button.id == "btn-save-schedule":
            self._save_schedule()
        elif event.button.id == "btn-start-scheduler":
            self._start_scheduler()
        elif event.button.id == "btn-stop-scheduler":
            self._stop_scheduler()

    def _save_schedule(self) -> bool:
        schedule_time = self.query_one("#schedule-time", Input).value.strip()
        try:
            core.validateScheduleTime(schedule_time)
        except Exception as e:
            self.app.notify(str(e), severity="error")
            return False
        core.saveConfig({
            "schedule_enabled": self.query_one("#schedule-enabled", Checkbox).value,
            "schedule_skip_wait": self.query_one("#schedule-skip-wait", Checkbox).value,
            "schedule_time": schedule_time,
        })
        self.app.notify("定时配置保存成功")
        return True

    def _start_scheduler(self) -> None:
        if not self._save_schedule():
            return
        log_widget = self.query_one("#checkin-log", RichLog)

        def log_callback(msg):
            self.app.call_from_thread(log_widget.write, msg)

        started = core.startScheduler(log_callback=log_callback)
        if started:
            self.app.notify("常驻调度已启动")
        else:
            self.app.notify("常驻调度已在运行")

    def _stop_scheduler(self) -> None:
        core.stopScheduler()
        self.app.notify("常驻调度停止请求已发送")

    def _run_checkin(self) -> None:
        log_widget = self.query_one("#checkin-log", RichLog)
        log_widget.clear()
        btn = self.query_one("#btn-run-checkin", Button)
        btn.disabled = True

        skip_wait = self.query_one("#opt-skip-wait", Checkbox).value
        telegram_notice = self.query_one("#opt-tg-notice", Checkbox).value
        only_service = self.query_one("#opt-only-service", Input).value.strip() or None

        def log_callback(msg):
            self.app.call_from_thread(log_widget.write, msg)

        def run():
            try:
                core.checkin(
                    skip_wait_time=skip_wait,
                    only_service=only_service,
                    telegram_notice=telegram_notice,
                    log_callback=log_callback,
                )
            except Exception as e:
                self.app.call_from_thread(log_widget.write, f"[bold red]错误：{e}[/bold red]")
            finally:
                self.app.call_from_thread(self._on_checkin_done)

        threading.Thread(target=run, daemon=True).start()

    def _on_checkin_done(self) -> None:
        self.query_one("#btn-run-checkin", Button).disabled = False
        self._update_last_time()


class ACMApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    #service-list-panel {
        width: 1fr;
        max-width: 40;
        height: 100%;
    }
    #service-edit-panel {
        width: 2fr;
        height: 100%;
        padding: 0 1;
    }
    .panel-title {
        text-style: bold;
        margin-bottom: 1;
    }
    .wait-time-row {
        height: 3;
    }
    .wait-time-label {
        width: 5;
        content-align: center middle;
    }
    .button-row {
        height: 3;
        margin-top: 1;
    }
    .button-row Button {
        margin-right: 1;
    }
    .option-row {
        height: 3;
    }
    .option-row Checkbox {
        margin-right: 2;
    }
    #checkin-log {
        height: 1fr;
        border: solid $accent;
        margin-top: 1;
    }
    .tg-hint {
        color: $text-muted;
        margin-top: 1;
    }
    .account-service-block {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
    }
    .account-config-label {
        margin-left: 4;
        color: $text-muted;
    }
    .account-config-input {
        margin-left: 4;
    }
    #telegram-log {
        height: 1fr;
        border: solid $accent;
        margin-top: 1;
    }
    ListView {
        height: 1fr;
    }
    """

    TITLE = "AutoCheckinManager"
    BINDINGS = [
        Binding("q", "quit", "退出"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with ServiceTab("签到服务"):
                pass
            with AccountTab("账号配置"):
                pass
            with TelegramTab("Telegram"):
                pass
            with CheckinTab("执行签到"):
                pass
        yield Footer()

    def on_mount(self) -> None:
        core.initDataFile()
