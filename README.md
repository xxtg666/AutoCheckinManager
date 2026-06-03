# AutoCheckinManager

AutoCheckinManager 是一个常驻运行的自动签到管理器，支持 Telegram Bot 控制、每日定时签到，以及通过远程浏览器完成交互式登录后自动提取登录凭据。

## 常驻运行

```powershell
python checkin.py
```

程序会启动内置调度器。启用 Telegram Bot 命令监听后，也会同时响应 Telegram 消息和按钮。

## Telegram 登录流程

1. 在 Telegram 中发送 `/help`，或点击 Bot 回复中的服务按钮。
2. 点击某个服务的“登录”。
3. Bot 会创建远程登录会话，并发送 Live View 链接。
4. 用手机打开链接，在远程浏览器中完成登录。
5. 回到 Telegram，点击“登录完成”。
6. 程序提取 cookies、localStorage、sessionStorage，并发送掩码摘要。
7. 确认无误后点击“确认保存”。
8. Bot 保存凭据，并可立即点击“验证签到”。

## 服务登录配置

每个服务支持这些登录字段：

- `login_start_command`：创建远程登录会话，输出 `session`、`live_url`、`message`。
- `login_poll_command`：可选，用于判断登录是否完成。
- `login_extract_command`：提取 cookies、localStorage、sessionStorage。
- `login_cancel_command`：可选，用于关闭远程浏览器会话。
- `login_extractors`：声明式提取规则。
- `credential_template`：把提取结果拼成最终凭据。
- `expire_keywords`：签到输出命中这些关键词时，Bot 会提示更新登录。

适配器命令可以使用占位符：

```text
{service_id}
{service_name}
{session}
{live_url}
```

## 提取规则示例

```json
[
  {
    "source": "cookie",
    "name": "sid",
    "domain": ".example.com",
    "alias": "sid"
  },
  {
    "source": "localStorage",
    "origin": "https://example.com",
    "name": "token",
    "alias": "token"
  },
  {
    "source": "sessionStorage",
    "origin": "https://example.com",
    "name": "csrf",
    "alias": "csrf"
  }
]
```

凭据模板：

```text
sid={sid}; token={token}; csrf={csrf}
```

如果不写模板，Cookie 会自动拼成 `name=value; name2=value2`。如果只提取 localStorage/sessionStorage，则会保存为 JSON。

## Cloudflare Browser Run 适配器

项目内置了通用适配器：

```text
logins/browser_run_login.mjs
```

需要安装 Node 依赖：

```powershell
npm install playwright-core
```

可以在 TUI 的 Telegram/远程浏览器登录配置里填写：

- Cloudflare Account ID
- Cloudflare API Token
- 浏览器会话保持时间（毫秒，默认 `600000`）

程序执行登录适配器时会自动把它们注入为环境变量：

```text
CF_ACCOUNT_ID
CF_API_TOKEN
CF_BROWSER_KEEP_ALIVE
```

服务配置示例：

```json
{
  "name": "Example",
  "command": "python example_checkin.py \"{config}\"",
  "key": "example_credential",
  "wait_time_min": 0,
  "wait_time_max": 30,
  "login_enabled": true,
  "login_url": "https://example.com/login",
  "login_cookie_domain": ".example.com",
  "login_origin": "https://example.com",
  "login_cookie_names": "sid",
  "login_local_storage_names": "token",
  "login_session_storage_names": "",
  "login_extractors": "[{\"source\":\"cookie\",\"name\":\"sid\",\"domain\":\".example.com\",\"alias\":\"sid\"},{\"source\":\"localStorage\",\"origin\":\"https://example.com\",\"name\":\"token\",\"alias\":\"token\"}]",
  "credential_template": "sid={sid}; token={token}",
  "expire_keywords": "登录过期,401,unauthorized"
}
```

保存服务时，TUI 会自动生成内部的 `login_start_command`、`login_extract_command` 和 `login_cancel_command`，通常不需要手写这些命令。

适配器会：

1. 创建 Browser Run 会话。
2. 打开登录页。
3. 返回 Live View 链接。
4. 等你在远程浏览器中登录完成。
5. 提取当前页面 origin 下的 localStorage/sessionStorage，以及浏览器上下文 cookies。

注意：不同服务登录成功后的页面、域名和存储键不同，需要按服务实际情况配置 `origin`、cookie 名和模板。
