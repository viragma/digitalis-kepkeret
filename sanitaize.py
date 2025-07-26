# sanitize_data.py

import sys
import os
import re # Reguláris kifejezésekhez szükséges modul

# Hozzáadjuk a projekt gyökérkönyvtárát a Python path-hoz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import data_manager

def sanitize_name(name):
    """
    Eltávolít minden karaktert a névből, ami nem magyar betű vagy szám.
    A title() biztosítja a nagy kezdőbetűt.
    """
    if not isinstance(name, str):
        return name
    
    # Csak a magyar ábécé betűit és a számokat hagyjuk meg
    # A ^ jelenti a negációt, tehát "minden, ami nem ez"
    sanitized = re.sub(r'[^a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜŰ]', '', name)
    return sanitized.strip().title()

def run_sanitizer():
    """
    Végigmegy a faces.json fájlon, megtisztítja a neveket, és visszaírja a tiszta adatokat.
    """
    print("Adattisztító indítása a faces.json fájlon...")
    
    all_faces = data_manager.get_faces()
    if not all_faces:
        print("A faces.json üres vagy nem található.")
        return

    changes_made = 0
    for face in all_faces:
        original_name = face.get('name')
        if original_name and isinstance(original_name, str):
            sanitized_name = sanitize_name(original_name)
            if original_name != sanitized_name:
                print(f"-> Név javítva: '{original_name}' -> '{sanitized_name}'")
                face['name'] = sanitized_name
                changes_made += 1
    
    if changes_made > 0:
        print(f"\nÖsszesen {changes_made} név javítva. Változások mentése...")
        data_manager.save_faces(all_faces)
        print("A faces.json sikeresen frissítve a tiszta adatokkal.")
    else:
        print("\nNem volt szükség javításra, minden név tiszta formátumú.")

if __name__ == '__main__':
    run_sanitizer()