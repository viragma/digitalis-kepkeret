# scripts/detect_faces.py
import os
import sys
import face_recognition
import json
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager, training_service

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'images')
FACES_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'static', 'faces')

def detect_new_faces():
    print("\n--- Új arcfelismerési ciklus indul ---")
    
    known_data = training_service.get_all_known_encodings()
    if not known_data["encodings"]:
        print("!!! Figyelem: Nincsenek tanított arcok az adatbázisban. A felismerés nem fog működni.")
        # Itt dönthetünk úgy, hogy leállítjuk a scriptet, de egyelőre csak figyelmeztetünk.

    config = data_manager.get_config()
    recognition_tolerance = config.get('slideshow', {}).get('recognition_tolerance', 0.6)
    print(f"Felismerési tolerancia beállítva: {recognition_tolerance}")
    
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
            face_locations = face_recognition.face_locations(image_data)
            face_encodings = face_recognition.face_encodings(image_data, face_locations)

            if not face_encodings:
                print("- Nem található arc.")
                data_manager.add_no_face_record(image_id)
                continue
            
            print(f"- {len(face_encodings)} arc található.")
            for i, face_encoding in enumerate(face_encodings):
                person_id, min_distance = None, 1.0

                if known_data["encodings"]:
                    distances = face_recognition.face_distance(known_data["encodings"], face_encoding)
                    min_distance = min(distances)
                    if min_distance < recognition_tolerance:
                        best_match_index = list(distances).index(min_distance)
                        person_id = known_data["ids"][best_match_index]
                        name = known_data["names"][best_match_index]
                        print(f"  - Arc #{i+1}: Felismerve mint '{name}', távolság: {min_distance:.2f}")
                    else:
                        print(f"  - Arc #{i+1}: Ismeretlen, legkisebb távolság: {min_distance:.2f}")
                else:
                    print(f"  - Arc #{i+1}: Ismeretlen (nincs tanító adat).")

                top, right, bottom, left = face_locations[i]
                face_image = Image.fromarray(image_data[top:bottom, left:right])
                face_filename = f"{os.path.splitext(filename)[0]}_face_{i}.jpg"
                face_path = os.path.join(FACES_OUTPUT_DIR, face_filename).replace('\\', '/')
                
                # Ellenőrizzük, hogy a fájl már létezik-e, mielőtt mentenénk
                if not os.path.exists(face_path):
                    face_image.save(face_path)

                data_manager.add_face_to_db(image_id, person_id, face_locations[i], face_path, min_distance)

        except Exception as e:
            print(f"!!! Hiba a '{filename}' feldolgozása közben: {e}")

    conn.close()
    print("\n--- Arcfelismerési ciklus befejezve. ---")

if __name__ == '__main__':
    detect_new_faces()