import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from core import needsMigration, migrateFromLegacy, initDataFile

if needsMigration():
    print("检测到旧版配置文件（config.json / services.json / users.json / users/ / last_checkin_time.json）")
    print("需要迁移至新格式 data.json，迁移后旧文件将被删除。")
    choice = input("是否立即迁移？(y/n) ").strip().lower()
    if choice == "y":
        migrateFromLegacy()
        print("迁移完成。")
    else:
        print("取消迁移，退出程序。")
        raise SystemExit()

initDataFile()

from tui import ACMApp
app = ACMApp()
app.run()
