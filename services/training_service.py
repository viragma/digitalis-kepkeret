# services/training_service.py
import os
import face_recognition
import numpy as np
from PIL import Image, ImageDraw
from . import data_manager

KNOWN_FACES_DIR = os.path.join(os.getcwd(), 'data', 'known_faces')

def get_all_known_encodings():
    """
    Összegyűjti az összes személyhez tartozó, adatbázisban tárolt
    "átlag-arc" kódolást.
    """
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
    """
    Legenerálja egy személy "átlag-arc" képét a tanítóképek alapján.
    Ez egy vizuális reprezentáció, nem a tényleges kódolás.
    """
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if not os.path.isdir(person_dir):
        return None

    images = []
    for filename in os.listdir(person_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img = Image.open(os.path.join(person_dir, filename)).resize((200, 200)).convert("RGBA")
                images.append(img)
            except Exception as e:
                print(f"Hiba a tanítókép betöltésekor: {filename}, {e}")

    if not images:
        return None

    # Létrehozunk egy alapot, amire átlagoljuk a képeket
    avg_image = Image.new('RGBA', (200, 200))
    
    for i, img in enumerate(images):
        # Az első képet teljes átlátszósággal, a többit egyre csökkenővel adjuk hozzá
        alpha = 1.0 / (i + 1)
        avg_image = Image.blend(avg_image, img, alpha)
    
    # Elmentjük a képet egy ideiglenes helyre, hogy a böngésző elérje
    # A legjobb, ha a static mappán belül egy 'temp' mappába mentjük
    temp_dir = os.path.join(os.getcwd(), 'static', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    avg_face_filename = f"avg_{name}.png"
    avg_face_path = os.path.join(temp_dir, avg_face_filename)
    avg_image.save(avg_face_path)

    return f'/static/temp/{avg_face_filename}'