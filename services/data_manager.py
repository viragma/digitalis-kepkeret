# services/data_manager.py
import json
import os
import shutil
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PERSONS_FILE = os.path.join(DATA_DIR, 'persons.json')
FACES_FILE = os.path.join(DATA_DIR, 'faces.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

def _load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {} if 'persons' in file_path or 'config' in file_path else []

def _save_json(file_path, data):
    temp_file_path = file_path + ".tmp"
    try:
        with open(temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        shutil.move(temp_file_path, file_path)
    except Exception as e:
        print(f"Hiba történt a(z) {file_path} fájl mentésekor: {e}")
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def get_config(): return _load_json(CONFIG_FILE)
def save_config(config_data): _save_json(CONFIG_FILE, config_data)
def get_persons(): return _load_json(PERSONS_FILE)
def save_persons(persons_data): _save_json(PERSONS_FILE, persons_data)
def get_faces(): return _load_json(FACES_FILE)
def save_faces(faces_data): _save_json(FACES_FILE, faces_data)

def get_todays_birthday_person():
    persons = get_persons()
    today = datetime.now()
    
    for name, birthday_str in persons.items():
        if not birthday_str: continue
        
        cleaned_birthday_str = birthday_str.replace('.', '').replace('-', '').replace(' ', '')
        try:
            birthday = datetime.strptime(cleaned_birthday_str, '%Y%m%d')
            if birthday.month == today.month and birthday.day == today.day:
                # --- JAVÍTÁS ---
                # A nevet "normalizálva" adjuk vissza
                return name.strip().title()
        except ValueError:
            continue
            
    return None