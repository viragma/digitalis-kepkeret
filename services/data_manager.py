# services/data_manager.py - BŐVÍTVE

import json
import os
import shutil
from datetime import datetime

# --- VÁLTOZÁS ---
# A gyökérkönyvtárat meghatározzuk, hogy bárhonnan fusson a kód
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PERSONS_FILE = os.path.join(DATA_DIR, 'persons.json')
FACES_FILE = os.path.join(DATA_DIR, 'faces.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json') # Új konstans

def _load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if 'persons' in file_path or 'config' in file_path else []

def _save_json(file_path, data):
    # ... (ez a függvény változatlan)
    temp_file_path = file_path + ".tmp"
    try:
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        shutil.move(temp_file_path, file_path)
    except Exception as e:
        print(f"Hiba történt a(z) {file_path} fájl mentésekor: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- ÚJ FUNKCIÓ ---
def get_config():
    """Visszaadja a konfigurációs beállításokat."""
    return _load_json(CONFIG_FILE)

# --- Személyek kezelése (Persons) ---
def get_persons():
    return _load_json(PERSONS_FILE)

def save_persons(persons_data):
    _save_json(PERSONS_FILE, persons_data)

# --- Arcok kezelése (Faces) ---
def get_faces():
    return _load_json(FACES_FILE)

def save_faces(faces_data):
    _save_json(FACES_FILE, faces_data)

    # services/data_manager.py - A FÁJL VÉGÉRE

def save_config(config_data):
    """Elmenti a konfigurációs beállításokat."""
    _save_json(CONFIG_FILE, config_data)


def get_birthday_persons():
    persons = get_persons()
    today = datetime.today()
    birthday_names = []
    for name, birthdate in persons.items():
        if not birthdate:
            continue
        try:
            bdate = datetime.strptime(birthdate, "%Y-%m-%d")
            if bdate.month == today.month and bdate.day == today.day:
                birthday_names.append((name, bdate.year))
        except Exception:
            continue
    return birthday_names