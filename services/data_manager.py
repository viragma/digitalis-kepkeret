# services/data_manager.py

import json
import os
import shutil # Ezt a modult használjuk a biztonságos átnevezéshez

# Fájlok elérési útjai
DATA_DIR = 'data'
PERSONS_FILE = os.path.join(DATA_DIR, 'persons.json')
FACES_FILE = os.path.join(DATA_DIR, 'faces.json')

def _load_json(file_path):
    """Segédfüggvény egy JSON fájl betöltéséhez."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Ha a fájl nincs meg vagy üres/hibás, üres listát/szótárat adunk vissza
        return {} if 'persons' in file_path else []

def _save_json(file_path, data):
    """Segédfüggvény egy JSON fájl biztonságos mentéséhez (atomikus írás)."""
    temp_file_path = file_path + ".tmp"
    try:
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        # Sikeres írás után az ideiglenes fájlt átnevezzük a véglegesre
        shutil.move(temp_file_path, file_path)
    except Exception as e:
        print(f"Hiba történt a(z) {file_path} fájl mentésekor: {e}")
        # Hiba esetén a régi fájl érintetlen marad, a .tmp fájlt törölhetjük
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Személyek kezelése (Persons) ---
def get_persons():
    """Visszaadja az összes ismert személyt."""
    return _load_json(PERSONS_FILE)

def save_persons(persons_data):
    """Elmenti a személyek listáját."""
    _save_json(PERSONS_FILE, persons_data)

# --- Arcok kezelése (Faces) ---
def get_faces():
    """Visszaadja az összes felismert arc adatát."""
    return _load_json(FACES_FILE)

def save_faces(faces_data):
    """Elmenti az arcok listáját."""
    _save_json(FACES_FILE, faces_data)