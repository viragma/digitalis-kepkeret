# scripts/create_database.py
import sqlite3
import os

# A projekt gyökérkönyvtárának meghatározása
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'database.db')

def create_database():
    """
    Létrehozza az SQLite adatbázist a szükséges táblákkal,
    ha az adatbázis fájl még nem létezik.
    """
    if os.path.exists(DB_PATH):
        print(f"Az adatbázis már létezik itt: {DB_PATH}")
        return

    print("Adatbázis létrehozása...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # --- persons tábla ---
        cursor.execute('''
        CREATE TABLE persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT,
            birthday TEXT,
            profile_face_id INTEGER,
            notes TEXT,
            relationship TEXT,
            is_active BOOLEAN DEFAULT 1,
            color_tag TEXT,
            average_encoding BLOB,
            custom_tolerance REAL,
            FOREIGN KEY (profile_face_id) REFERENCES faces (id)
        )
        ''')
        print("- 'persons' tábla létrehozva.")

        # --- images tábla ---
        cursor.execute('''
        CREATE TABLE images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            taken_at DATETIME,
            is_favorite BOOLEAN DEFAULT 0,
            camera_make TEXT,
            camera_model TEXT,
            width INTEGER,
            height INTEGER,
            gps_lat REAL,
            gps_lon REAL,
            clarity_score INTEGER,
            tags TEXT,
            view_count INTEGER DEFAULT 0,
            blur_hash TEXT
        )
        ''')
        print("- 'images' tábla létrehozva.")

        # --- faces tábla ---
        cursor.execute('''
        CREATE TABLE faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER NOT NULL,
            person_id INTEGER,
            face_location TEXT,
            face_path TEXT UNIQUE,
            distance REAL,
            is_manual BOOLEAN DEFAULT 0,
            is_confirmed BOOLEAN DEFAULT 0,
            cluster_id INTEGER,
            FOREIGN KEY (image_id) REFERENCES images (id),
            FOREIGN KEY (person_id) REFERENCES persons (id)
        )
        ''')
        print("- 'faces' tábla létrehozva.")

        conn.commit()
        conn.close()
        print("\nAdatbázis és táblák sikeresen létrehozva.")

    except Exception as e:
        print(f"!!! Hiba az adatbázis létrehozása közben: {e}")

if __name__ == '__main__':
    create_database()