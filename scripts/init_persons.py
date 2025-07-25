# scripts/init_persons.py - JAVÍTOTT VERZIÓ

import sys
import os

# Hozzáadjuk a projekt gyökérkönyvtárát a Python path-hoz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# A központi moduljainkat használjuk
from services import data_manager

def sync_persons_from_folders():
    """
    Szinkronizálja a persons.json fájlt a data/known_faces/ mappák alapján.
    Csak az új személyeket adja hozzá, a régieket békén hagyja.
    """
    print("Személyek szinkronizálása a mappák alapján...")

    known_faces_path = os.path.join('data', 'known_faces')
    
    # Ellenőrizzük, hogy létezik-e a mappa
    if not os.path.isdir(known_faces_path):
        print(f"Hiba: A '{known_faces_path}' mappa nem található.")
        return

    # Betöltjük a jelenlegi személyeket
    persons_data = data_manager.get_persons()
    print(f"Jelenleg {len(persons_data)} személy van az adatbázisban.")

    # Kiolvassuk a mappaneveket, ezek lesznek a nevek
    try:
        folder_names = [name for name in os.listdir(known_faces_path) if os.path.isdir(os.path.join(known_faces_path, name))]
    except FileNotFoundError:
        print(f"Hiba: A '{known_faces_path}' mappa nem listázható.")
        return

    new_persons_count = 0
    # Végigmegyünk a talált mappákon
    for name in folder_names:
        # Ha a név még nincs a listában, hozzáadjuk
        if name not in persons_data:
            persons_data[name] = ""  # Üres születésnappal adjuk hozzá
            print(f"-> Új személy hozzáadva: {name}")
            new_persons_count += 1

    if new_persons_count > 0:
        print(f"\n{new_persons_count} új személy mentése...")
        data_manager.save_persons(persons_data)
        print("Sikeres mentés.")
    else:
        print("\nNem található új személy, nincs szükség mentésre.")

if __name__ == '__main__':
    sync_persons_from_folders()