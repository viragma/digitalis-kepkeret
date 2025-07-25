import os
import shutil
import time

FACES_JSON = 'data/faces.json'
BACKUP_DIR = 'data/backups'

def backup_faces_json():
    """Készít egy időbélyegzett biztonsági mentést a faces.json fájlról."""
    if not os.path.exists(FACES_JSON):
        return False

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"faces_backup_{timestamp}.json")
    shutil.copy2(FACES_JSON, backup_file)
    return True

def list_backups():
    """Listázza az elérhető backup fájlokat (csak fájlnév)."""
    if not os.path.exists(BACKUP_DIR):
        return []
    return sorted([
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith("faces_backup_") and f.endswith(".json")
    ], reverse=True)

def restore_faces_json(filename):
    """Visszaállítja a megadott backup fájlt a faces.json helyére."""
    backup_path = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, FACES_JSON)
        return True
    return False
