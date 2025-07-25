# scripts/admin.py - JAVÍTOTT VERZIÓ

import sys
import os
import argparse

# Hozzáadjuk a projekt gyökérkönyvtárát a Python path-hoz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# A központi moduljainkat használjuk
from services import data_manager

def assign_name_to_unknown_faces(image_filename, new_name):
    """
    Egy adott képfájlhoz tartozó összes 'Ismeretlen' arcot átnevezi a megadott névre.
    """
    print(f"Arcok átnevezése a(z) '{image_filename}' képen '{new_name}' névre...")

    faces_data = data_manager.get_faces()
    
    updated_count = 0
    # Végigmegyünk az összes arc adaton
    for face in faces_data:
        # Ha a képfájl megegyezik és a név 'Ismeretlen'
        if face.get('image_file') == image_filename and face.get('name') == 'Ismeretlen':
            face['name'] = new_name
            updated_count += 1
    
    if updated_count > 0:
        print(f"{updated_count} arc sikeresen átnevezve.")
        print("Változtatások mentése...")
        data_manager.save_faces(faces_data)
        print("Sikeres mentés.")
    else:
        print(f"Nem található 'Ismeretlen' arc a(z) '{image_filename}' képen.")

def main():
    """
    Parancssori argumentumokat kezelő fő funkció.
    """
    parser = argparse.ArgumentParser(description="Adminisztrációs scriptek a képkerethez.")
    subparsers = parser.add_subparsers(dest='command', help='Elérhető parancsok')

    # Parancs: 'assign_name'
    parser_assign = subparsers.add_parser('assign_name', help="Arcok átnevezése egy képen.")
    parser_assign.add_argument('image_filename', type=str, help="A képfájl neve (pl. 'img_0001.jpg')")
    parser_assign.add_argument('new_name', type=str, help="Az új név, amire cserélni kell (pl. 'Anya')")

    args = parser.parse_args()

    if args.command == 'assign_name':
        assign_name_to_unknown_faces(args.image_filename, args.new_name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()