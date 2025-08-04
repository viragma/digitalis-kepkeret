# scripts/train_model.py
import os
import sys
import face_recognition
import numpy as np
import pickle
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

KNOWN_FACES_DIR = os.path.join(PROJECT_ROOT, 'data', 'known_faces')
ENCODINGS_CACHE = os.path.join(PROJECT_ROOT, 'data', 'known_encodings.pkl')

def train_model():
    """
    Végignézi a tanítóképeket, kiszámolja a kódolásokat, és elmenti őket
    a gyorsítótárba, valamint az adatbázisba (az average_encoding még nincs implementálva).
    """
    print("--- Modell tanítása indul ---")
    
    # Régi cache fájl törlése a tiszta tanításhoz
    if os.path.exists(ENCODINGS_CACHE):
        os.remove(ENCODINGS_CACHE)
        print("Régi tanítási gyorsítótár törölve.")

    known_encodings = {"names": [], "encodings": []}
    print("Tanító adatbázis építése (ez eltarthat egy ideig)...")
    
    conn = data_manager.get_db_connection()
    persons = conn.execute("SELECT id, name FROM persons WHERE is_active = 1").fetchall()
    conn.close()

    if not persons:
        print("Nincsenek személyek az adatbázisban a tanításhoz.")
        return

    print(f"{len(persons)} személy betanítása következik...")
    trained_count = 0

    for person in persons:
        person_name = person['name']
        person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
        
        encodings = []
        if os.path.isdir(person_dir):
            print(f"\n-> '{person_name}' tanítása...")
            for filename in os.listdir(person_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(person_dir, filename)
                    try:
                        image = face_recognition.load_image_file(image_path)
                        face_encodings = face_recognition.face_encodings(image)
                        if face_encodings:
                            encodings.append(face_encodings[0])
                            known_encodings["names"].append(person_name)
                            known_encodings["encodings"].append(face_encodings[0])
                            print(f"  - '{filename}' feldolgozva.")
                    except Exception as e:
                        print(f"  !!! Hiba a '{filename}' feldolgozása közben: {e}")

        if encodings:
            # TODO: Az "átlag-arc" számítását ide kell majd beépíteni
            trained_count += 1
        else:
            print(f"  -> '{person_name}' számára nem található érvényes tanítókép.")
    
    with open(ENCODINGS_CACHE, 'wb') as f:
        pickle.dump(known_encodings, f)
    print("\nÚj tanítási gyorsítótár sikeresen létrehozva.")
    print(f"--- Tanítás befejezve. {trained_count} személy lett sikeresen betanítva. ---")

if __name__ == '__main__':
    train_model()