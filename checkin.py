import os
import time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from core import needsMigration, migrateFromLegacy, initDataFile, startDaemon, stopDaemon, loadConfig


def log(msg, level="INFO"):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


if needsMigration():
    log("检测到旧版配置文件，正在自动迁移至 data.json ...")
    migrateFromLegacy()
    log("迁移完成。")

initDataFile()


config = loadConfig()
log("AutoCheckinManager 准备进入常驻模式")
log(f"定时签到：{'启用' if config.get('schedule_enabled', True) else '禁用'}，时间 {config.get('schedule_time', '08:00')}，调度检查间隔 5 分钟")
log(f"Telegram 通知：{'启用' if config.get('telegram_enabled', False) else '禁用'}")
log(f"Telegram Bot：{'启用' if config.get('telegram_bot_enabled', False) else '禁用'}")
log(f"Browser Run：{'已配置' if config.get('cf_account_id') and config.get('cf_api_token') else '未完整配置'}")


try:
    started = startDaemon(log_callback=log)
    log("定时调度器已启动" if started else "定时调度器已在运行")
    log("AutoCheckinManager 已进入常驻模式。按 Ctrl+C 停止。")
except Exception as e:
    log(f"启动失败：{e}", level="ERROR")
    raise

try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    log("收到停止信号，正在停止 AutoCheckinManager ...")
    stopDaemon()
    log("AutoCheckinManager 已停止")
except Exception as e:
    log(f"常驻运行异常：{e}", level="ERROR")
    stopDaemon()
    raise
