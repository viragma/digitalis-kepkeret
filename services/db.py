import os
import json

CONFIG_FILE = 'data/config.json'
PERSONS_FILE = 'data/persons.json'


# --- Konfiguráció ---
def get_all_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def set_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- Személyek listája (név + születési dátum) ---
def load_persons():
    if os.path.exists(PERSONS_FILE):
        with open(PERSONS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                # régi formátum (csak nevek), konvertáljuk
                return {name: {} for name in data}
            return data
    return {}

def save_persons(data):
    os.makedirs(os.path.dirname(PERSONS_FILE), exist_ok=True)
    with open(PERSONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# --- Születésnapok (immár a persons.json-on keresztül) ---
def load_birthdays():
    persons = load_persons()
    return {
        name: info.get("birthdate", "")
        for name, info in persons.items()
    }

def save_birthdays(birthdays: dict):
    persons = load_persons()
    for name, date in birthdays.items():
        if name in persons:
            persons[name]["birthdate"] = date
    save_persons(persons)
    
# --- faces.json betöltése és mentése ---
def load_faces_json(filepath='data/faces.json'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[HIBA] faces.json betöltése: {e}")
        return []

def save_faces_json(data, filepath='data/faces.json'):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[HIBA] faces.json mentése: {e}")
        return False
