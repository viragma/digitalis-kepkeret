# scripts/detect_faces.py
import os
import sys
import face_recognition
import pickle
import json
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

KNOWN_FACES_DIR = os.path.join(PROJECT_ROOT, 'data', 'known_faces')
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'static', 'images')
FACES_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'static', 'faces')
ENCODINGS_CACHE = os.path.join(PROJECT_ROOT, 'data', 'known_encodings.pkl')

def get_known_encodings(force_retrain=False):
    if not force_retrain and os.path.exists(ENCODINGS_CACHE):
        print("-> Gyorsítótárból betöltöm a tanult arcokat...")
        with open(ENCODINGS_CACHE, 'rb') as f:
            return pickle.load(f)

    known_encodings = {"names": [], "encodings": []}
    print("Tanító adatbázis építése...")
    for name in os.listdir(KNOWN_FACES_DIR):
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
    print(f"Felismerési tolerancia beállítva: {recognition_tolerance}")
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    processed_images_rows = cursor.execute('SELECT filename FROM images WHERE id IN (SELECT DISTINCT image_id FROM faces)').fetchall()
    processed_images = {row[0] for row in processed_images_rows}
    all_images = {f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))}
    
    images_to_process = all_images - processed_images

    print(f"{len(images_to_process)} új kép vár feldolgozásra.")
    if not images_to_process:
        print("--- Ciklus vége: Nincs új kép. ---")
        conn.close()
        return

    for filename in images_to_process:
        print(f"\nFeldolgozás alatt: {filename}")
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        
        try:
            image_record = cursor.execute('SELECT id FROM images WHERE filename = ?', (filename,)).fetchone()
            if not image_record:
                cursor.execute('INSERT INTO images (filename) VALUES (?)', (filename,))
                conn.commit()
                image_id = cursor.lastrowid
            else:
                image_id = image_record[0]

            image_data = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image_data)
            face_encodings = face_recognition.face_encodings(image_data, face_locations)

            if not face_encodings:
                print("- Nem található arc.")
                cursor.execute('INSERT OR IGNORE INTO faces (image_id) VALUES (?)', (image_id,))
                conn.commit()
                continue
            
            print(f"- {len(face_encodings)} arc található.")
            for i, face_encoding in enumerate(face_encodings):
                distances = face_recognition.face_distance(known_data["encodings"], face_encoding)
                
                person_id = None
                min_distance = 1.0

                if len(distances) > 0:
                    min_distance = min(distances)
                    if min_distance < recognition_tolerance:
                        best_match_index = list(distances).index(min_distance)
                        name = known_data["names"][best_match_index]
                        person_row = cursor.execute('SELECT id FROM persons WHERE name = ?', (name,)).fetchone()
                        person_id = person_row[0] if person_row else None
                        print(f"  - Arc #{i+1}: Felismerve mint '{name}', távolság: {min_distance:.2f}")
                    else:
                        print(f"  - Arc #{i+1}: Ismeretlen, legkisebb távolság: {min_distance:.2f}")
                else:
                    print(f"  - Arc #{i+1}: Ismeretlen, nincsenek tanított arcok.")

                top, right, bottom, left = face_locations[i]
                face_image = Image.fromarray(image_data[top:bottom, left:right])
                face_filename = f"{os.path.splitext(filename)[0]}_face_{i}.jpg"
                face_path = os.path.join(FACES_OUTPUT_DIR, face_filename).replace('\\', '/')
                face_image.save(face_path)

                cursor.execute("""
                    INSERT INTO faces (image_id, person_id, face_location, face_path, distance)
                    VALUES (?, ?, ?, ?, ?)
                """, (image_id, person_id, json.dumps(face_locations[i]), face_path, min_distance))
                conn.commit()

        except Exception as e:
            print(f"!!! Hiba a '{filename}' feldolgozása közben: {e}")

    conn.close()
    print("\n--- Arcfelismerési ciklus befejezve. ---")

if __name__ == '__main__':
    detect_new_faces()