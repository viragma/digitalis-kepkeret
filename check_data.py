# check_data.py

import json
from collections import defaultdict

FACES_FILE = 'data/faces.json'

def check_names_in_faces():
    """
    Ez a script beolvassa a faces.json fájlt, és kigyűjti,
    hogy melyik név hány képen szerepel.
    """
    names_found = defaultdict(set)
    
    print(f"'{FACES_FILE}' ellenőrzése...")
    try:
        with open(FACES_FILE, 'r', encoding='utf-8') as f:
            all_faces = json.load(f)
    except Exception as e:
        print(f"Hiba a fájl olvasásakor: {e}")
        return

    for face in all_faces:
        name = face.get('name')
        image = face.get('image_file')
        
        if name and image and name not in ['Ismeretlen', 'arc_nélkül']:
            normalized_name = name.strip().title()
            names_found[normalized_name].add(image)

    if not names_found:
        print("\nNem található egyetlen névhez rendelt arc sem a fájlban.")
        print("Minden arc 'Ismeretlen' vagy 'arc_nélkül' állapotban van.")
    else:
        print("\nA program a következő neveket találta a képekhez rendelve:")
        for name, images in sorted(names_found.items()):
            print(f"- '{name}': {len(images)} képen szerepel.")
            
    print("\nEllenőrzés vége.")

if __name__ == '__main__':
    check_names_in_faces()