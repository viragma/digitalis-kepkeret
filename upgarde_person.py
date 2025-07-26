# upgrade_persons_json.py

import sys
import os

# Hozzáadjuk a projekt gyökérkönyvtárát a Python path-hoz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import data_manager

def upgrade_structure():
    """
    Átalakítja a régi persons.json struktúrát az újra, ami már támogatja a profilképet.
    Régi: {"Név": "születésnap"}
    Új:   {"Név": {"birthday": "születésnap", "profile_image": null}}
    """
    print("persons.json struktúra frissítése...")
    persons_data = data_manager.get_persons()
    
    # Ellenőrizzük, hogy kell-e egyáltalán frissíteni
    # Veszünk egy mintát az adatokból
    first_person_value = next(iter(persons_data.values()), None)
    if isinstance(first_person_value, dict):
        print("A struktúra már naprakész, nincs teendő.")
        return

    new_persons_data = {}
    for name, birthday in persons_data.items():
        new_persons_data[name] = {
            "birthday": birthday,
            "profile_image": None  # Alapértelmezetten nincs profilkép
        }
    
    print(f"{len(new_persons_data)} személyi adat átalakítva. Mentés...")
    data_manager.save_persons(new_persons_data)
    print("Sikeresen frissítve!")

if __name__ == '__main__':
    upgrade_structure()