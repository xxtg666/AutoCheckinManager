#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { chromium } from "playwright-core";

const STATE_DIR = path.resolve(".login_sessions");
const API_BASE = "https://api.cloudflare.com/client/v4/accounts";

function jsonOut(value) {
  process.stdout.write(JSON.stringify(value, null, 2));
}

function fail(message) {
  jsonOut({ ok: false, error: String(message) });
  process.exit(1);
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    fail(`缺少环境变量 ${name}`);
  }
  return value;
}

function statePath(session) {
  return path.join(STATE_DIR, `${session}.json`);
}

function saveState(session, value) {
  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.writeFileSync(statePath(session), JSON.stringify(value, null, 2), "utf8");
}

function loadState(session) {
  const file = statePath(session);
  if (!fs.existsSync(file)) {
    fail(`找不到登录会话 ${session}`);
  }
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

async function browserRunFetch(accountId, token, endpoint, init = {}) {
  const resp = await fetch(`${API_BASE}/${accountId}/browser-rendering${endpoint}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok || data.success === false) {
    throw new Error(data?.errors?.[0]?.message || data?.error || `HTTP ${resp.status}`);
  }
  return data.result ?? data;
}

async function createSession() {
  const accountId = requireEnv("CF_ACCOUNT_ID");
  const token = requireEnv("CF_API_TOKEN");
  const keepAlive = Number(process.env.CF_BROWSER_KEEP_ALIVE || "600000");
  return await browserRunFetch(accountId, token, `/devtools/browser?keep_alive=${keepAlive}&targets=true`, {
    method: "POST",
  });
}

async function closeSession(sessionId) {
  const accountId = requireEnv("CF_ACCOUNT_ID");
  const token = requireEnv("CF_API_TOKEN");
  await browserRunFetch(accountId, token, `/devtools/browser/${sessionId}`, { method: "DELETE" });
}

async function connect(wsEndpoint) {
  if (!wsEndpoint) {
    fail("Browser Run 会话没有 webSocketDebuggerUrl");
  }
  return await chromium.connectOverCDP(wsEndpoint, {
    headers: {
      Authorization: `Bearer ${requireEnv("CF_API_TOKEN")}`,
    },
  });
}

async function getPage(browser, loginUrl = "") {
  const context = browser.contexts()[0] || await browser.newContext();
  let page = context.pages()[0];
  if (!page) {
    page = await context.newPage();
  }
  if (loginUrl) {
    await page.goto(loginUrl, { waitUntil: "domcontentloaded", timeout: 60000 });
  }
  return page;
}

async function start(serviceId, loginUrl) {
  if (!serviceId || !loginUrl) {
    fail("用法：browser_run_login.mjs start <service_id> <login_url>");
  }
  const result = await createSession();
  const sessionId = result.sessionId || result.id || result.session_id;
  const wsEndpoint = result.webSocketDebuggerUrl || result.webSocketDebuggerURL || result.wsEndpoint;
  const target = Array.isArray(result.targets) ? result.targets[0] : {};
  const liveUrl = target?.devtoolsFrontendUrl || result.devtoolsFrontendUrl || result.devtoolsUrl || result.liveViewUrl || result.live_url;

  const browser = await connect(wsEndpoint);
  await getPage(browser, loginUrl);
  await browser.close();

  saveState(sessionId, {
    serviceId,
    sessionId,
    loginUrl,
    wsEndpoint,
    liveUrl,
    createdAt: Date.now(),
  });

  jsonOut({
    ok: true,
    session: sessionId,
    live_url: liveUrl,
    message: "请在远程浏览器中完成登录。登录完成后回到 Telegram 点“登录完成”。",
  });
}

async function extract(sessionId) {
  const state = loadState(sessionId);
  const browser = await connect(state.wsEndpoint);
  const page = await getPage(browser);
  const context = page.context();
  const cookies = await context.cookies();
  const storage = await page.evaluate(() => {
    const local = {};
    const session = {};
    for (let i = 0; i < localStorage.length; i += 1) {
      const key = localStorage.key(i);
      local[key] = localStorage.getItem(key);
    }
    for (let i = 0; i < sessionStorage.length; i += 1) {
      const key = sessionStorage.key(i);
      session[key] = sessionStorage.getItem(key);
    }
    return {
      origin: location.origin,
      localStorage: local,
      sessionStorage: session,
      href: location.href,
      title: document.title,
    };
  });
  await browser.close();

  jsonOut({
    ok: true,
    status: "success",
    url: storage.href,
    title: storage.title,
    cookies,
    localStorage: {
      [storage.origin]: storage.localStorage,
    },
    sessionStorage: {
      [storage.origin]: storage.sessionStorage,
    },
  });
}

async function cancel(sessionId) {
  const state = loadState(sessionId);
  await closeSession(state.sessionId);
  fs.rmSync(statePath(sessionId), { force: true });
  jsonOut({ ok: true, status: "cancelled" });
}

async function main() {
  const [command, ...args] = process.argv.slice(2);
  if (command === "start") {
    await start(args[0], args[1]);
    return;
  }
  if (command === "extract" || command === "poll") {
    await extract(args[0]);
    return;
  }
  if (command === "cancel") {
    await cancel(args[0]);
    return;
  }
  fail("用法：browser_run_login.mjs start|extract|poll|cancel ...");
}

main().catch((error) => fail(error.message || error));
