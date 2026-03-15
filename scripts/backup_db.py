"""Database backup utility for SmartFarm OS."""
import shutil, os
from datetime import datetime

DB_PATH = "smartfarm.db"
BACKUP_DIR = "backups"

def backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        print("No database file found.")
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(BACKUP_DIR, f"smartfarm_{ts}.db")
    shutil.copy2(DB_PATH, dest)
    print(f"✅ Database backed up to {dest}")
    # Keep only last 10 backups
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.endswith(".db")])
    for old in backups[:-10]:
        os.remove(os.path.join(BACKUP_DIR, old))
        print(f"🗑 Removed old backup: {old}")

if __name__ == "__main__":
    backup()
