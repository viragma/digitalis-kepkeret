# scripts/detect_faces.py - JAVÍTOTT VERZIÓ 2.0

import sys
import os
import json
import face_recognition
from PIL import Image

# Hozzáadjuk a projekt gyökérkönyvtárát a Python path-hoz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# A központi data_manager-t használjuk
from services import data_manager

# --- JAVÍTÁS 1: Abszolút útvonalak használata ---
# Meghatározzuk a projekt gyökerét, és ehhez képest adjuk meg a fájlok útvonalát
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def load_config():
    """Betölti a konfigurációt a data/config.json fájlból."""
    config_path = os.path.join(PROJECT_ROOT, 'data', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("HIBA: config.json nem található! Alapértelmezett értékek használata.")
        return {"UPLOAD_FOLDER": "static/images"}

def scan_images_for_faces():
    """
    Végigpásztázza a képeket új arcokért, és frissíti a faces.json-t.
    """
    print("Arcfelismerő script elindítva...")

    all_faces = data_manager.get_faces()
    config = load_config()
    
    # --- JAVÍTÁS 2: Hibatűrő adatelemzés ---
    # Csak azokat a bejegyzéseket vesszük figyelembe, amikben biztosan van 'image_file' kulcs.
    processed_images = {face['image_file'] for face in all_faces if 'image_file' in face}
    print(f"Eddig {len(processed_images)} kép lett feldolgozva.")

    image_folder = os.path.join(PROJECT_ROOT, config.get('UPLOAD_FOLDER', 'static/images'))
    faces_folder = os.path.join(PROJECT_ROOT, 'static/faces')
    new_faces_found = 0

    if not os.path.exists(faces_folder):
        os.makedirs(faces_folder)

    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    for filename in image_files:
        if filename in processed_images:
            continue

        print(f"-> Kép feldolgozása: {filename}")
        image_path = os.path.join(image_folder, filename)

        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                print(f"   Nem található arc a képen: {filename}")
                all_faces.append({
                    "image_file": filename,
                    "face_locations": [],
                    "name": "arc_nélkül"
                })
                continue

            print(f"   {len(face_locations)} arc található.")
            pil_image = Image.open(image_path)
            pil_image.verify() # Ellenőrizzük, hogy a kép nem sérült-e
            pil_image = Image.open(image_path) # Újra meg kell nyitni a verify() után

            for i, (top, right, bottom, left) in enumerate(face_locations):
                face_image = pil_image.crop((left, top, right, bottom))
                face_filename = f"{os.path.splitext(filename)[0]}_face_{i}.jpg"
                face_filepath = os.path.join('static/faces', face_filename) # Relatív útvonal a webes eléréshez
                
                # Mentés abszolút útvonallal
                face_image.save(os.path.join(PROJECT_ROOT, face_filepath))

                all_faces.append({
                    "image_file": filename,
                    "face_location": [top, right, bottom, left],
                    "face_path": face_filepath.replace('\\', '/'), # Egységesítjük a mappaelválasztót
                    "name": "Ismeretlen"
                })
                new_faces_found += 1

        except (IOError, SyntaxError) as e:
            print(f"!!! Hiba: A(z) {filename} képfájl sérült vagy nem olvasható. Kihagyom. Hiba: {e}")
        except Exception as e:
            print(f"!!! Általános hiba történt a(z) {filename} feldolgozása közben: {e}")

    if new_faces_found > 0:
        print(f"\nÖsszesen {new_faces_found} új arc mentése...")
        data_manager.save_faces(all_faces)
        print("Adatbázis sikeresen frissítve.")
    else:
        print("\nNem található új, feldolgozandó kép.")

if __name__ == '__main__':
    scan_images_for_faces()