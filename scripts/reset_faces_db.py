# scripts/reset_faces_db.py
import os
import sys

# A projekt gyökérkönyvtárának meghatározása
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

def reset_faces_table():
    """
    Figyelem: Ez a script törli az ÖSSZES bejegyzést a 'faces' táblából!
    A személyek és a képek megmaradnak.
    """
    confirm = input("Biztosan törölni szeretnéd az összes felismert arc adatát? Ez nem vonható vissza. (igen/nem): ")
    if confirm.lower() != 'igen':
        print("Művelet megszakítva.")
        return

    print("Arcok adatbázisának törlése...")
    try:
        conn = data_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM faces")
        conn.commit()
        conn.close()
        print("A 'faces' tábla sikeresen kiürítve.")
    except Exception as e:
        print(f"!!! Hiba a törlés során: {e}")

if __name__ == '__main__':
    reset_faces_table()