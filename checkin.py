import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from core import needsMigration, migrateFromLegacy, initDataFile, checkin

if needsMigration():
    print("检测到旧版配置文件，正在自动迁移至 data.json ...")
    migrateFromLegacy()
    print("迁移完成。")

initDataFile()
checkin()
