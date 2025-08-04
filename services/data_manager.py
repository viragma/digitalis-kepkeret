# services/data_manager.py
import sqlite3
import os
import json
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'database.db')
CONFIG_JSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'config.json')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row 
    return conn

# --- Olvasó Funkciók ---
def get_persons():
    conn = get_db_connection()
    persons_rows = conn.execute('SELECT * FROM persons WHERE is_active = 1 ORDER BY name').fetchall()
    conn.close()
    return {row['name']: dict(row) for row in persons_rows}

def get_faces():
    conn = get_db_connection()
    faces_rows = conn.execute("""
        SELECT f.id, f.image_id, f.person_id, f.face_location, f.face_path, f.distance,
               p.name, i.filename as image_file
        FROM faces f
        JOIN images i ON f.image_id = i.id
        LEFT JOIN persons p ON f.person_id = p.id
    """).fetchall()
    conn.close()
    faces_list = []
    for row in faces_rows:
        face_dict = dict(row)
        try:
            if face_dict.get('face_location'):
                face_dict['face_location'] = json.loads(face_dict['face_location'])
        except (json.JSONDecodeError, TypeError):
            face_dict['face_location'] = None
        faces_list.append(face_dict)
    return faces_list

def get_config():
    try:
        with open(CONFIG_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError): return {}

def get_todays_birthday_person():
    conn = get_db_connection()
    persons = conn.execute("SELECT name, birthday FROM persons WHERE is_active = 1").fetchall()
    conn.close()
    today = datetime.now().date()
    for person in persons:
        birthday_str = person['birthday']
        if not birthday_str: continue
        try:
            birth_date = datetime.strptime(birthday_str.strip(), '%Y.%m.%d').date()
            if birth_date.month == today.month and birth_date.day == today.day:
                return person['name'].strip().title()
        except ValueError:
            continue
    return None

# --- Arcfelismerő Segédfüggvények ---
def get_processed_images():
    """Visszaadja a már feldolgozott képek fájlneveinek halmazát."""
    conn = get_db_connection()
    rows = conn.execute('SELECT filename FROM images WHERE id IN (SELECT DISTINCT image_id FROM faces)').fetchall()
    conn.close()
    return {row['filename'] for row in rows}

def get_or_create_image_id(filename):
    """Lekérdezi egy kép ID-ját, vagy létrehozza, ha még nem létezik."""
    conn = get_db_connection()
    cursor = conn.cursor()
    image_record = cursor.execute('SELECT id FROM images WHERE filename = ?', (filename,)).fetchone()
    if image_record:
        image_id = image_record['id']
    else:
        cursor.execute('INSERT INTO images (filename) VALUES (?)', (filename,))
        conn.commit()
        image_id = cursor.lastrowid
    conn.close()
    return image_id

def get_person_id_by_name(name):
    """Lekérdezi egy személy ID-ját a neve alapján."""
    conn = get_db_connection()
    person_row = conn.execute('SELECT id FROM persons WHERE name = ?', (name,)).fetchone()
    conn.close()
    return person_row['id'] if person_row else None

def add_face_to_db(image_id, person_id, location, path, distance, encoding_bytes):
    """Elment egyetlen új arcot az adatbázisba, az arclenyomattal együtt."""
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO faces (image_id, person_id, face_location, face_path, distance, face_encoding)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (image_id, person_id, json.dumps(location), path, distance, encoding_bytes))
    conn.commit()
    conn.close()

def add_no_face_record(image_id):
    """Bejegyzést hoz létre arról, hogy egy képen nem található arc."""
    conn = get_db_connection()
    conn.execute('INSERT OR IGNORE INTO faces (image_id) VALUES (?)', (image_id,))
    conn.commit()
    conn.close()

# --- Író Funkciók (Admin felülethez) ---
def save_config(config_data):
    with open(CONFIG_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)