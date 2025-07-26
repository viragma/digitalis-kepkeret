# scripts/detect_faces.py - ÚJ, INTELLIGENS VERZIÓ

import sys
import os
import face_recognition
from PIL import Image
import pickle # A tanult adatok mentéséhez

# Hozzáadjuk a projekt gyökérkönyvtárát a Python path-hoz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services import data_manager

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
KNOWN_FACES_DIR = os.path.join(PROJECT_ROOT, 'data', 'known_faces')
ENCODINGS_CACHE_PATH = os.path.join(PROJECT_ROOT, 'data', 'known_encodings.pkl')

def train_known_faces(force_retrain=False):
    """
    Betanítja a rendszert az ismert arcokra a known_faces mappából.
    Gyorsítótárat használ a gyorsabb működés érdekében.
    """
    if not force_retrain and os.path.exists(ENCODINGS_CACHE_PATH):
        print("-> Gyorsítótárból betöltöm a tanult arcokat...")
        with open(ENCODINGS_CACHE_PATH, 'rb') as f:
            return pickle.load(f)

    print("-> Tanulási fázis indul (ez eltarthat egy ideig)...")
    known_face_encodings = []
    known_face_names = []

    for name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, name)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                image_path = os.path.join(person_dir, filename)
                try:
                    image = face_recognition.load_image_file(image_path)
                    # Fontos: feltételezzük, hogy minden tanítóképen csak egy arc van
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        known_face_encodings.append(encodings[0])
                        known_face_names.append(name)
                        print(f"   - '{name}' arca betanítva a '{filename}' képből.")
                except Exception as e:
                    print(f"!!! Hiba a '{filename}' tanítókép feldolgozásakor: {e}")

    # Elmentjük a tanult adatokat a gyorsítótárba
    with open(ENCODINGS_CACHE_PATH, 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)
    
    print("-> Tanulás befejezve, gyorsítótár elmentve.")
    return known_face_encodings, known_face_names

def scan_and_recognize_faces():
    """
    Végigpásztázza a képeket, és megpróbálja felismerni az arcokat.
    """
    # 1. Tanulás vagy gyorsítótár betöltése
    known_encodings, known_names = train_known_faces()
    if not known_encodings:
        print("!!! Nincsenek tanult arcok, a felismerés nem lehetséges. !!!")
        return

    print("\n--- Új képek pásztázása és arcfelismerés ---")
    all_faces_db = data_manager.get_faces()
    config = data_manager.get_config()
    
    processed_images = {face['image_file'] for face in all_faces_db if 'image_file' in face}
    print(f"Eddig {len(processed_images)} kép lett feldolgozva.")

    image_folder = os.path.join(PROJECT_ROOT, config.get('UPLOAD_FOLDER', 'static/images'))
    faces_folder = os.path.join(PROJECT_ROOT, 'static/faces')
    new_faces_count = 0

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
                all_faces_db.append({"image_file": filename, "name": "arc_nélkül"})
                continue

            # Arckódolások generálása a képen talált arcokhoz
            unknown_encodings = face_recognition.face_encodings(image, face_locations)
            
            pil_image = Image.open(image_path)

            for i, (top, right, bottom, left) in enumerate(face_locations):
                # 2. Összehasonlítás
                matches = face_recognition.compare_faces(known_encodings, unknown_encodings[i])
                name = "Ismeretlen"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    print(f"   - Találat! Ez valószínűleg: {name}")

                # 3. Mentés
                face_image = pil_image.crop((left, top, right, bottom))
                face_filename = f"{os.path.splitext(filename)[0]}_face_{i}.jpg"
                face_filepath_relative = os.path.join('static/faces', face_filename).replace('\\', '/')
                face_filepath_abs = os.path.join(PROJECT_ROOT, face_filepath_relative)
                
                face_image.save(face_filepath_abs)

                all_faces_db.append({
                    "image_file": filename,
                    "face_location": [top, right, bottom, left],
                    "face_path": face_filepath_relative,
                    "name": name
                })
                new_faces_count += 1
        except Exception as e:
            print(f"!!! Hiba történt a(z) {filename} feldolgozása közben: {e}")

    if new_faces_count > 0:
        print(f"\nÖsszesen {new_faces_count} új arc mentése az adatbázisba...")
        data_manager.save_faces(all_faces_db)
        print("Adatbázis sikeresen frissítve.")
    else:
        print("\nNem található új, feldolgozandó kép.")

if __name__ == '__main__':
    scan_and_recognize_faces()