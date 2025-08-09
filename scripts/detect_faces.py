# scripts/detect_faces.py
import os
import sys
import face_recognition
import pickle
import json
from PIL import Image
import numpy as np
import traceback

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

KNOWN_FACES_DIR = os.path.join(PROJECT_ROOT, 'data', 'known_faces')
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'images')
FACES_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'static', 'faces')
ENCODINGS_CACHE = os.path.join(PROJECT_ROOT, 'data', 'known_encodings.pkl')

def get_known_encodings(force_retrain=False):
    if not force_retrain and os.path.exists(ENCODINGS_CACHE):
        try:
            with open(ENCODINGS_CACHE, 'rb') as f:
                data = pickle.load(f)
                if isinstance(data, dict) and "names" in data and "encodings" in data:
                    print("-> Gyorsítótárból betöltöm a tanult arcokat...")
                    return data
        except Exception: pass
    
    known_encodings = {"names": [], "encodings": []}
    print("Tanító adatbázis építése...")
    persons = data_manager.get_persons()
    for name in persons.keys():
        person_dir = os.path.join(KNOWN_FACES_DIR, name)
        if os.path.isdir(person_dir):
            for filename in os.listdir(person_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    try:
                        image = face_recognition.load_image_file(os.path.join(person_dir, filename))
                        encodings = face_recognition.face_encodings(image)
                        if encodings:
                            known_encodings["names"].append(name)
                            known_encodings["encodings"].append(encodings[0])
                    except Exception as e:
                        print(f"!!! Hiba a tanítókép feldolgozása közben: {filename}, {e}")
    
    with open(ENCODINGS_CACHE, 'wb') as f:
        pickle.dump(known_encodings, f)
    print("Tanító adatbázis gyorsítótárazva.")
    return known_encodings

def detect_new_faces():
    print("\n--- Új arcfelismerési ciklus indul ---")
    
    known_data = get_known_encodings()
    config = data_manager.get_config()
    recognition_tolerance = config.get('slideshow', {}).get('recognition_tolerance', 0.6)
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    processed_images_rows = cursor.execute('SELECT filename FROM images WHERE id IN (SELECT DISTINCT image_id FROM faces)').fetchall()
    processed_images = {row['filename'] for row in processed_images_rows}
    all_images_in_folder = {f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))}
    
    images_to_process = all_images_in_folder - processed_images

    print(f"{len(images_to_process)} új kép vár feldolgozásra.")
    if not images_to_process:
        print("--- Ciklus vége: Nincs új kép. ---")
        conn.close()
        return

    for filename in images_to_process:
        print(f"\nFeldolgozás alatt: {filename}")
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            image_id = data_manager.get_or_create_image_id(filename)
            image_data = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image_data, model="cnn")
            face_encodings = face_recognition.face_encodings(image_data, face_locations)

            if not face_encodings:
                print("- Nem található arc.")
                data_manager.add_no_face_record(image_id)
                continue
            
            print(f"- {len(face_encodings)} arc található.")
            for i, face_encoding in enumerate(face_encodings):
                top, right, bottom, left = face_locations[i]
                face_image = Image.fromarray(image_data[top:bottom, left:right])
                face_filename = f"{os.path.splitext(filename)[0]}_face_{i}.jpg"
                face_path = os.path.join(FACES_OUTPUT_DIR, face_filename).replace('\\', '/')
                
                # Ellenőrizzük, hogy ez az arckép-fájl már létezik-e az adatbázisban
                existing_face = cursor.execute('SELECT id FROM faces WHERE face_path = ?', (face_path,)).fetchone()
                if existing_face:
                    print(f"  - Arc #{i+1}: Már létezik az adatbázisban, átugorva.")
                    continue

                person_id, min_distance = None, 1.0

                if known_data["encodings"]:
                    distances = face_recognition.face_distance(known_data["encodings"], face_encoding)
                    min_distance = min(distances)
                    if min_distance < recognition_tolerance:
                        best_match_index = list(distances).index(min_distance)
                        name = known_data["names"][best_match_index]
                        person_id = data_manager.get_person_id_by_name(name)
                        print(f"  - Arc #{i+1}: Felismerve mint '{name}', távolság: {min_distance:.2f}")
                    else:
                        print(f"  - Arc #{i+1}: Ismeretlen, legkisebb távolság: {min_distance:.2f}")
                else:
                    print(f"  - Arc #{i+1}: Ismeretlen.")

                if not os.path.exists(face_path):
                    face_image.save(face_path)

                # Az arclenyomatot byte-okká alakítjuk az adatbázis számára
                encoding_bytes = face_encoding.tobytes()
                
                data_manager.add_face_to_db(image_id, person_id, face_locations[i], face_path, min_distance, encoding_bytes)

        except Exception:
            print(f"!!! RÉSZLETES HIBA a '{filename}' feldolgozása közben: !!!")
            traceback.print_exc()

    conn.close()
    print("\n--- Arcfelismerési ciklus befejezve. ---")

if __name__ == '__main__':
    detect_new_faces()