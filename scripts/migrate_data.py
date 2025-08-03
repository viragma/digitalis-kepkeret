# scripts/migrate_data.py
import sqlite3
import json
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'database.db')
PERSONS_JSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'persons.json')
FACES_JSON_PATH = os.path.join(PROJECT_ROOT, 'data', 'faces.json')

def migrate_data():
    """
    Áttölti az adatokat a régi .json fájlokból az új SQLite adatbázisba.
    """
    if not os.path.exists(DB_PATH):
        print("HIBA: Az adatbázis nem létezik. Kérlek, futtasd először a 'create_database.py' scriptet.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. Személyek áttöltése ---
    print("Személyek (persons.json) áttöltése...")
    try:
        with open(PERSONS_JSON_PATH, 'r', encoding='utf-8') as f:
            persons_data = json.load(f)
        
        for name, data in persons_data.items():
            cursor.execute("INSERT OR IGNORE INTO persons (name, birthday, profile_face_id) VALUES (?, ?, ?)",
                           (name, data.get('birthday'), None)) # profile_face_id-t később frissítjük
        conn.commit()
        print(f"{len(persons_data)} személy áttöltve.")
    except Exception as e:
        print(f"!!! Hiba a persons.json feldolgozása közben: {e}")

    # --- 2. Képek és arcok áttöltése ---
    print("\nKépek és arcok (faces.json) áttöltése...")
    try:
        with open(FACES_JSON_PATH, 'r', encoding='utf-8') as f:
            faces_data = json.load(f)

        # Gyorsítótár a már beillesztett képeknek és személyeknek
        image_map = {}
        person_map = {name: id for id, name in cursor.execute("SELECT id, name FROM persons").fetchall()}
        
        for face in faces_data:
            filename = face.get('image_file')
            if not filename:
                continue

            # Kép beillesztése, ha még nem létezik
            if filename not in image_map:
                cursor.execute("INSERT OR IGNORE INTO images (filename) VALUES (?)", (filename,))
                image_map[filename] = cursor.lastrowid if cursor.lastrowid != 0 else cursor.execute("SELECT id FROM images WHERE filename = ?", (filename,)).fetchone()[0]

            image_id = image_map[filename]
            person_name = face.get('name')
            person_id = person_map.get(person_name) if person_name not in ['Ismeretlen', 'arc_nélkül'] else None
            
            cursor.execute("""
            INSERT INTO faces (image_id, person_id, face_location, face_path)
            VALUES (?, ?, ?, ?)
            """, (image_id, person_id, json.dumps(face.get('face_location')), face.get('face_path')))

        conn.commit()
        print(f"{len(faces_data)} arc áttöltve.")
    except Exception as e:
        print(f"!!! Hiba a faces.json feldolgozása közben: {e}")

    conn.close()
    print("\nAdatmigráció befejezve.")

if __name__ == '__main__':
    migrate_data()