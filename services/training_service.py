# services/training_service.py
import os
import face_recognition
import numpy as np
from PIL import Image, ImageDraw
import cv2 # ÚJ IMPORT
from . import data_manager

KNOWN_FACES_DIR = os.path.join(os.getcwd(), 'data', 'known_faces')

def analyze_training_image(image_path):
    """
    Elemzi egy tanítókép minőségét (élesség, fényerő).
    Visszaad egy szótárat az elemzés eredményével.
    """
    try:
        # OpenCV-vel olvassuk be a képet a részletes elemzéshez
        img = cv2.imread(image_path)
        if img is None:
            return {"error": "A kép nem olvasható"}

        # 1. Élesség vizsgálata (Laplacian variancia)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # 2. Fényerő vizsgálata (átlagos pixel érték)
        brightness = np.mean(gray)

        return {
            "sharpness": round(laplacian_var, 2),
            "brightness": round(brightness, 2)
        }
    except Exception as e:
        return {"error": str(e)}

def get_all_known_encodings():
    """ Összegyűjti az összes személyhez tartozó "átlag-arc" kódolást. """
    conn = data_manager.get_db_connection()
    persons_rows = conn.execute('SELECT id, name, average_encoding FROM persons WHERE is_active = 1').fetchall()
    conn.close()

    known_data = {"ids": [], "names": [], "encodings": []}
    for row in persons_rows:
        if row['average_encoding']:
            known_data["ids"].append(row['id'])
            known_data["names"].append(row['name'])
            known_data["encodings"].append(np.frombuffer(row['average_encoding']))
            
    return known_data

def generate_average_face_image(name):
    """ Legenerálja egy személy "átlag-arc" képét. """
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if not os.path.isdir(person_dir): return None

    images = []
    for filename in os.listdir(person_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img = Image.open(os.path.join(person_dir, filename)).resize((200, 200)).convert("RGBA")
                images.append(img)
            except Exception as e:
                print(f"Hiba a tanítókép betöltésekor: {filename}, {e}")

    if not images: return None

    avg_image = Image.new('RGBA', (200, 200))
    for i, img in enumerate(images):
        alpha = 1.0 / (i + 1)
        avg_image = Image.blend(avg_image, img, alpha)
    
    temp_dir = os.path.join(os.getcwd(), 'static', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    avg_face_filename = f"avg_{name}.png"
    avg_face_path = os.path.join(temp_dir, avg_face_filename)
    avg_image.save(avg_face_path)

    return f'/static/temp/{avg_face_filename}'