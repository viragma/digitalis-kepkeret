# scripts/reset_faces_db.py
import os
import sys
import shutil

# A projekt gyökérkönyvtárának meghatározása
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

FACES_DIR = os.path.join(PROJECT_ROOT, 'static', 'faces')

def reset_faces_data():
    """
    Figyelem: Ez a script törli az ÖSSZES bejegyzést a 'faces' táblából,
    ÉS az összes fájlt a 'static/faces' mappából!
    """
    confirm = input("Biztosan törölni szeretnéd az összes felismert arc adatát és képfájlját? Ez nem vonható vissza. (igen/nem): ")
    if confirm.lower() != 'igen':
        print("Művelet megszakítva.")
        return

    # 1. Adatbázis tábla kiürítése
    print("Arcok adatbázisának törlése...")
    try:
        conn = data_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faces")
        conn.commit()
        conn.close()
        print("A 'faces' tábla sikeresen kiürítve.")
    except Exception as e:
        print(f"!!! Hiba az adatbázis törlése során: {e}")

    # 2. 'static/faces' mappa kiürítése
    print("\n'static/faces' mappa tisztítása...")
    try:
        for filename in os.listdir(FACES_DIR):
            file_path = os.path.join(FACES_DIR, filename)
            # A biztonság kedvéért a .gitignore fájlt nem töröljük, ha van
            if filename.lower() != '.gitignore':
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        print("A 'static/faces' mappa sikeresen kiürítve.")
    except Exception as e:
        print(f"!!! Hiba a 'static/faces' mappa tisztítása során: {e}")
    
    print("\nReset befejezve. Most futtathatod a 'detect_faces.py' scriptet az újrafeldolgozáshoz.")


if __name__ == '__main__':
    reset_faces_data()