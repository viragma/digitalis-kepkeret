# scripts/train_model.py
import os
import sys
import face_recognition
import numpy as np
from PIL import Image

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

KNOWN_FACES_DIR = os.path.join(PROJECT_ROOT, 'data', 'known_faces')

def train_model():
    """
    Végignézi a tanítóképeket, kiszámolja az "átlag-arcokat" (average encoding),
    és elmenti őket az adatbázisba.
    """
    print("--- Modell tanítása indul ---")
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()

    persons = cursor.execute("SELECT id, name FROM persons WHERE is_active = 1").fetchall()
    if not persons:
        print("Nincsenek személyek az adatbázisban a tanításhoz.")
        conn.close()
        return

    print(f"{len(persons)} személy betanítása következik...")
    trained_count = 0

    for person in persons:
        person_id = person['id']
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
                        # A face_recognition több arcot is találhat egy képen,
                        # de tanításkor feltételezzük, hogy csak egy van.
                        face_encodings = face_recognition.face_encodings(image)
                        if face_encodings:
                            encodings.append(face_encodings[0])
                            print(f"  - '{filename}' feldolgozva.")
                    except Exception as e:
                        print(f"  !!! Hiba a '{filename}' feldolgozása közben: {e}")

        if encodings:
            # Az összes arclenyomat átlagát számoljuk ki
            average_encoding = np.mean(encodings, axis=0)
            
            # Az adatbázis a kódolást 'bytes' formátumban várja
            cursor.execute("UPDATE persons SET average_encoding = ? WHERE id = ?", 
                           (average_encoding.tobytes(), person_id))
            print(f"  -> '{person_name}' átlag-arca sikeresen kiszámolva és elmentve.")
            trained_count += 1
        else:
            print(f"  -> '{person_name}' számára nem található érvényes tanítókép.")
    
    conn.commit()
    conn.close()
    print(f"\n--- Tanítás befejezve. {trained_count} személy lett sikeresen betanítva. ---")

if __name__ == '__main__':
    train_model()