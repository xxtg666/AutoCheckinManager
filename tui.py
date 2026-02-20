import os
import time
import threading
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, TabbedContent, TabPane,
    ListView, ListItem, Label, Input, Button,
    RadioSet, RadioButton, Checkbox, RichLog, Static,
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
        self.query_one("#service-wait-min", Input).value = "0"
        self.query_one("#service-wait-max", Input).value = "0"

    def _save_service(self) -> None:
        sid = self.query_one("#service-id", Input).value.strip()
        if not sid:
            self.app.notify("服务ID不能为空", severity="error")
            return
        services = core.loadServices()
        services[sid] = {
            "name": self.query_one("#service-name", Input).value,
            "command": self.query_one("#service-command", Input).value,
            "key": self.query_one("#service-config-key", Input).value,
            "wait_time_min": int(self.query_one("#service-wait-min", Input).value or 0),
            "wait_time_max": int(self.query_one("#service-wait-max", Input).value or 0),
        }
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


class UserConfigScreen(ModalScreen):
    """用户配置编辑界面：勾选启用的服务 + 填写每个服务的配置值"""

    CSS = """
    UserConfigScreen {
        align: center middle;
    }
    #ucfg-dialog {
        width: 70;
        max-height: 80%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #ucfg-title {
        text-style: bold;
        margin-bottom: 1;
    }
    #ucfg-scroll {
        height: 1fr;
        margin-bottom: 1;
    }
    .ucfg-service-block {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
    }
    .ucfg-config-label {
        margin-left: 4;
        color: $text-muted;
    }
    .ucfg-config-input {
        margin-left: 4;
    }
    .ucfg-buttons {
        height: 3;
        align: right middle;
    }
    .ucfg-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, user_id: str, user_name: str) -> None:
        super().__init__()
        self.user_id = user_id
        self.user_name = user_name

    def compose(self) -> ComposeResult:
        services = core.loadServices()
        user_config = core.loadUserConfig(self.user_id)
        enabled = user_config.get("services", [])
        config_vals = user_config.get("config", {})

        with Vertical(id="ucfg-dialog"):
            yield Label(f"编辑用户配置 - {self.user_name}", id="ucfg-title")
            with VerticalScroll(id="ucfg-scroll"):
                if not services:
                    yield Label("没有可用的签到服务，请先创建服务。")
                for sid, svc in services.items():
                    with Vertical(classes="ucfg-service-block"):
                        yield Checkbox(
                            f"{svc['name']}  ({sid})",
                            value=(sid in enabled),
                            id=f"ucfg-cb-{sid}",
                        )
                        if svc.get("key"):
                            yield Label(
                                f"配置字段 [{svc['key']}]（填入命令中 {{config}} 的值）",
                                classes="ucfg-config-label",
                            )
                            yield Input(
                                value=config_vals.get(svc["key"], ""),
                                placeholder=f"输入 {svc['key']} 的值",
                                id=f"ucfg-input-{sid}",
                                classes="ucfg-config-input",
                            )
            with Horizontal(classes="ucfg-buttons"):
                yield Button("保存", id="ucfg-save", variant="success")
                yield Button("取消", id="ucfg-cancel", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ucfg-save":
            self._save()
        elif event.button.id == "ucfg-cancel":
            self.dismiss(False)

    def _save(self) -> None:
        services = core.loadServices()
        enabled = []
        config_vals = {}
        for sid, svc in services.items():
            cb = self.query_one(f"#ucfg-cb-{sid}", Checkbox)
            if cb.value:
                enabled.append(sid)
            if svc.get("key"):
                try:
                    inp = self.query_one(f"#ucfg-input-{sid}", Input)
                    val = inp.value
                except Exception:
                    val = ""
                if val:
                    config_vals[svc["key"]] = val
        user_config = {"services": enabled, "config": config_vals}
        core.saveUserConfig(self.user_id, user_config)
        self.app.notify(f"用户 {self.user_name} 的配置已保存")
        self.dismiss(True)


class UserTab(TabPane):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="user-list-panel"):
                yield Label("用户列表", classes="panel-title")
                yield ListView(id="user-list")
                yield Button("新建用户", id="btn-new-user", variant="primary")
            with VerticalScroll(id="user-edit-panel"):
                yield Label("用户设置", classes="panel-title")
                yield Label("ID")
                yield Input(id="user-id", placeholder="用户ID", disabled=True)
                yield Label("名称")
                yield Input(id="user-name", placeholder="用户名称")
                yield Label("邮件地址")
                yield Input(id="user-email", placeholder="用户邮箱")
                with Horizontal(classes="button-row"):
                    yield Button("保存", id="btn-save-user", variant="success")
                    yield Button("删除", id="btn-delete-user", variant="error")
                    yield Button("编辑配置", id="btn-edit-user-config", variant="default")

    def on_mount(self) -> None:
        self._refresh_list()

    def _refresh_list(self) -> None:
        lv = self.query_one("#user-list", ListView)
        lv.clear()
        users = core.loadUsers()
        for key in users:
            lv.append(ListItem(Label(users[key]["name"]), name=key))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        uid = event.item.name
        users = core.loadUsers()
        if uid not in users:
            return
        u = users[uid]
        self.query_one("#user-id", Input).value = uid
        self.query_one("#user-name", Input).value = u["name"]
        self.query_one("#user-email", Input).value = u["email"]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-new-user":
            self._new_user()
        elif event.button.id == "btn-save-user":
            self._save_user()
        elif event.button.id == "btn-delete-user":
            self._delete_user()
        elif event.button.id == "btn-edit-user-config":
            self._edit_user_config()

    def _new_user(self) -> None:
        self.query_one("#user-id", Input).value = core.generateRandomID()
        self.query_one("#user-name", Input).value = ""
        self.query_one("#user-email", Input).value = ""

    def _save_user(self) -> None:
        uid = self.query_one("#user-id", Input).value.strip()
        name = self.query_one("#user-name", Input).value.strip()
        email = self.query_one("#user-email", Input).value.strip()
        if not name:
            self.app.notify("用户名不能为空", severity="error")
            return
        users = core.loadUsers()
        for key in users:
            if users[key]["name"] == name and key != uid:
                self.app.notify(f"用户名 {name} 已存在", severity="error")
                return
        if uid in users:
            users[uid]["name"] = name
            users[uid]["email"] = email
        else:
            users[uid] = {"name": name, "email": email, "services": [], "config": {}}
        core.saveUsers(users)
        self._refresh_list()
        self.app.notify(f"用户 {name} 保存成功")

    def _delete_user(self) -> None:
        uid = self.query_one("#user-id", Input).value.strip()
        if not uid:
            return
        users = core.loadUsers()
        if uid in users:
            name = users[uid]["name"]
            del users[uid]
            core.saveUsers(users)
            self._refresh_list()
            self._new_user()
            self.app.notify(f"用户 {name} 已删除")
        else:
            self.app.notify("用户不存在", severity="error")

    def _edit_user_config(self) -> None:
        uid = self.query_one("#user-id", Input).value.strip()
        if not uid:
            self.app.notify("请先选择或新建用户", severity="warning")
            return
        users = core.loadUsers()
        if uid not in users:
            self.app.notify("请先保存用户", severity="warning")
            return
        self.app.push_screen(UserConfigScreen(uid, users[uid]["name"]))


class EmailTab(TabPane):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("邮件配置", classes="panel-title")
            yield Label("SMTP 服务器")
            yield Input(id="email-server", placeholder="例如 smtp.example.com")
            yield Label("邮箱账户")
            yield Input(id="email-account", placeholder="your@email.com")
            yield Label("邮箱密码")
            yield Input(id="email-password", placeholder="密码/授权码", password=True)
            yield Label("通知方式")
            yield RadioSet(
                RadioButton("不通知", id="radio-no"),
                RadioButton("一起通知", id="radio-all"),
                RadioButton("独立通知", id="radio-div"),
                id="notice-type",
            )
            yield Button("保存配置", id="btn-save-config", variant="success")

    def on_mount(self) -> None:
        config = core.loadConfig()
        self.query_one("#email-server", Input).value = config.get("email_server", "")
        self.query_one("#email-account", Input).value = config.get("email_account", "")
        self.query_one("#email-password", Input).value = config.get("email_password", "")
        notice = config.get("email_notice_type", "no")
        radio_map = {"no": 0, "all": 1, "div": 2}
        rs = self.query_one("#notice-type", RadioSet)
        idx = radio_map.get(notice, 0)
        rs._selected = idx
        for i, btn in enumerate(rs.query(RadioButton)):
            btn.value = (i == idx)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-config":
            self._save_config()

    def _save_config(self) -> None:
        rs = self.query_one("#notice-type", RadioSet)
        notice_type = "no"
        for i, btn in enumerate(rs.query(RadioButton)):
            if btn.value:
                notice_type = ["no", "all", "div"][i]
                break
        config = {
            "email_server": self.query_one("#email-server", Input).value,
            "email_account": self.query_one("#email-account", Input).value,
            "email_password": self.query_one("#email-password", Input).value,
            "email_notice_type": notice_type,
        }
        core.saveConfig(config)
        self.app.notify("配置保存成功")


class TelegramTab(TabPane):
    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Label("Telegram 配置", classes="panel-title")
            yield Checkbox("启用 Telegram 通知", id="tg-enabled")
            yield Label("Bot Token")
            yield Input(id="tg-bot-token", placeholder="从 @BotFather 获取")
            yield Label("Chat ID")
            yield Input(id="tg-chat-id", placeholder="目标聊天/群组 ID")
            yield Label("代理地址")
            yield Input(id="tg-proxy", placeholder="例如 http://127.0.0.1:7890（留空不使用）")
            yield Static("提示：仅支持「一起通知」模式，所有用户的签到结果\n合并为一条消息发送到指定聊天。", classes="tg-hint")
            with Horizontal(classes="button-row"):
                yield Button("保存配置", id="btn-save-telegram", variant="success")
                yield Button("发送测试", id="btn-test-telegram", variant="primary")

    def on_mount(self) -> None:
        config = core.loadConfig()
        self.query_one("#tg-enabled", Checkbox).value = config.get("telegram_enabled", False)
        self.query_one("#tg-bot-token", Input).value = config.get("telegram_bot_token", "")
        self.query_one("#tg-chat-id", Input).value = config.get("telegram_chat_id", "")
        self.query_one("#tg-proxy", Input).value = config.get("telegram_proxy", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-save-telegram":
            self._save_config()
        elif event.button.id == "btn-test-telegram":
            self._test_send()

    def _save_config(self) -> None:
        config = {
            "telegram_enabled": self.query_one("#tg-enabled", Checkbox).value,
            "telegram_bot_token": self.query_one("#tg-bot-token", Input).value,
            "telegram_chat_id": self.query_one("#tg-chat-id", Input).value,
            "telegram_proxy": self.query_one("#tg-proxy", Input).value,
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


class CheckinTab(TabPane):
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("签到选项", classes="panel-title")
            with Horizontal(classes="option-row"):
                yield Checkbox("跳过随机等待", id="opt-skip-wait", value=True)
                yield Checkbox("发送邮件通知", id="opt-email-notice")
                yield Checkbox("发送Telegram通知", id="opt-tg-notice")
            yield Label("仅执行指定服务（留空=全部）")
            yield Input(id="opt-only-service", placeholder="服务ID（留空执行全部）")
            yield Label("仅执行指定用户（留空=全部）")
            yield Input(id="opt-only-user", placeholder="用户ID（留空执行全部）")
            with Horizontal(classes="button-row"):
                yield Button("执行签到", id="btn-run-checkin", variant="warning")
            yield Label("", id="last-checkin-time")
            yield RichLog(id="checkin-log", wrap=True, markup=True)

    def on_mount(self) -> None:
        self._update_last_time()

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

    def _run_checkin(self) -> None:
        log_widget = self.query_one("#checkin-log", RichLog)
        log_widget.clear()
        btn = self.query_one("#btn-run-checkin", Button)
        btn.disabled = True

        skip_wait = self.query_one("#opt-skip-wait", Checkbox).value
        email_notice = self.query_one("#opt-email-notice", Checkbox).value
        telegram_notice = self.query_one("#opt-tg-notice", Checkbox).value
        only_service = self.query_one("#opt-only-service", Input).value.strip() or None
        only_user = self.query_one("#opt-only-user", Input).value.strip() or None

        def log_callback(msg):
            self.app.call_from_thread(log_widget.write, msg)

        def run():
            try:
                core.checkin(
                    skip_wait_time=skip_wait,
                    only_service=only_service,
                    only_user=only_user,
                    email_notice=email_notice,
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
    #service-list-panel, #user-list-panel {
        width: 1fr;
        max-width: 40;
        height: 100%;
    }
    #service-edit-panel, #user-edit-panel {
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
            with UserTab("用户管理"):
                pass
            with EmailTab("邮件配置"):
                pass
            with TelegramTab("Telegram"):
                pass
            with CheckinTab("执行签到"):
                pass
        yield Footer()

    def on_mount(self) -> None:
        core.initDataFile()
