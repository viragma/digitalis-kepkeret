# services/data_manager.py
import sqlite3
import os
import json
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'database.db')

def get_db_connection():
    """Létrehoz egy kapcsolatot az adatbázissal."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Ez lehetővé teszi, hogy oszlopnevek szerint hivatkozzunk az adatokra
    return conn

# --- persons tábla funkciói ---

def get_persons():
    """Visszaadja az összes személyt az adatbázisból, szótár formátumban."""
    conn = get_db_connection()
    persons_list = conn.execute('SELECT * FROM persons WHERE is_active = 1').fetchall()
    conn.close()
    
    # Átalakítjuk a kimenetet a program többi része által várt formátumra
    persons_dict = {row['name']: dict(row) for row in persons_list}
    return persons_dict

def save_persons(persons_data):
    """Elmenti a személyek teljes listáját. A meglévőket frissíti, az újakat beszúrja."""
    conn = get_db_connection()
    cursor = conn.cursor()
    for name, data in persons_data.items():
        cursor.execute("""
            INSERT INTO persons (name, birthday, profile_face_id, notes, relationship, is_active, color_tag, display_name) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                birthday=excluded.birthday,
                profile_face_id=excluded.profile_face_id,
                notes=excluded.notes,
                relationship=excluded.relationship,
                is_active=excluded.is_active,
                color_tag=excluded.color_tag,
                display_name=excluded.display_name
        """, (
            name, data.get('birthday'), data.get('profile_face_id'), data.get('notes'), 
            data.get('relationship'), data.get('is_active', 1), data.get('color_tag'), data.get('display_name')
        ))
    conn.commit()
    conn.close()

# --- faces tábla funkciói ---

def get_faces():
    """Visszaadja az összes arc adatát az adatbázisból."""
    conn = get_db_connection()
    # Összekapcsoljuk a táblákat, hogy a személy nevét is megkapjuk
    faces_list = conn.execute("""
        SELECT f.*, p.name as person_name, i.filename as image_file
        FROM faces f
        JOIN images i ON f.image_id = i.id
        LEFT JOIN persons p ON f.person_id = p.id
    """).fetchall()
    conn.close()
    
    # Visszaalakítjuk a régi, JSON-szerű formátumra
    faces_dict_list = []
    for row in faces_list:
        face_dict = dict(row)
        # A program a 'name' kulcsot várja, nem a 'person_name'-t
        face_dict['name'] = row['person_name'] if row['person_name'] else "Ismeretlen"
        faces_dict_list.append(face_dict)
        
    return faces_dict_list

def save_faces(faces_data):
    """Elmenti az arcok teljes listáját. (Ez egy bonyolultabb művelet, ritkán használjuk)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Ez a funkció most már inkább csak frissítésre szolgál, az új arcok hozzáadása máshol történik
    # A biztonság kedvéért egyelőre üresen hagyjuk, hogy elkerüljük a véletlen adatvesztést
    # A jövőben itt lehetne implementálni a tömeges frissítést, ha szükséges.
    
    conn.commit()
    conn.close()


# --- config és egyéb funkciók (ezek maradhatnak a JSON fájlban, mert ritkán változnak) ---
CONFIG_JSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'config.json')

def get_config():
    try:
        with open(CONFIG_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_config(config_data):
    with open(CONFIG_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)


# --- Születésnap-ellenőrző, ami már az adatbázist használja ---
def get_todays_birthday_person():
    persons = get_persons()
    today = datetime.now().date()
    
    for name, data in persons.items():
        birthday_str = data.get("birthday")
        if not birthday_str: continue
        
        try:
            birth_date = datetime.strptime(birthday_str.strip(), '%Y.%m.%d').date()
            if birth_date.month == today.month and birth_date.day == today.day:
                return name.strip().title()
        except ValueError:
            continue
            
    return None