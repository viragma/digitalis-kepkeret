import face_recognition
import os
import json
import shutil
import argparse
import hashlib
import pickle
from PIL import Image

# --- Beállítások ---
KNOWN_FACES_DIR = 'data/known_faces'
IMAGES_DIR = 'static/images'
FACES_DIR = 'static/faces'
OUTPUT_FILE = 'data/faces.json'
ENCODINGS_CACHE = 'data/known_encodings.pkl'
CROP_MARGIN = 20

# --- Beállítások config.json-ból ---
CONFIG_PATH = 'data/config.json'
DEFAULT_TOLERANCE = 0.5
DEFAULT_MANUAL_MODE = False

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        TOLERANCE = float(config_data.get("tolerance", DEFAULT_TOLERANCE))
        MANUAL_MODE = bool(config_data.get("manual_mode", DEFAULT_MANUAL_MODE))
except Exception as e:
    print(f"⚠️ Hiba a config.json olvasásakor: {e}")
    TOLERANCE = DEFAULT_TOLERANCE
    MANUAL_MODE = DEFAULT_MANUAL_MODE

print(f"🎯 Tolerancia beállítva: {TOLERANCE}")
print(f"🛠️  Manuális mód aktív: {MANUAL_MODE}")


# --- Parancssori argumentum: --full vagy -f ---
parser = argparse.ArgumentParser()
parser.add_argument('--full', '-f', action='store_true', help='Minden képet újra feldolgoz')
args = parser.parse_args()

# --- Előző faces.json betöltése ---
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        previous_faces = json.load(f)
else:
    previous_faces = []

# Már feldolgozott arcok nyilvántartása
existing_faces = set()
for face in previous_faces:
    if 'image' in face and 'face_id' in face:
        existing_faces.add((face['image'], face['face_id']))

# --- Ismert arcok betöltése ---
print("✅ Ismert arcok betöltése és fájlok átnevezése...")

known_encodings = []
known_names = []

for person_name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
    if not os.path.isdir(person_dir):
        continue

    file_hashes = set()
    counter = 1
    for filename in sorted(os.listdir(person_dir)):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        path = os.path.join(person_dir, filename)

        # Duplikációs ellenőrzés (hash alapján)
        with open(path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        if file_hash in file_hashes:
            os.remove(path)
            print(f"  🗑️ Duplikált törölve: {filename}")
            continue
        file_hashes.add(file_hash)

        # Arc beolvasás
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(person_name)
            # Fájl átnevezés
            new_name = f"{person_name}_{counter}.jpg"
            new_path = os.path.join(person_dir, new_name)
            os.rename(path, new_path)
            counter += 1

# --- Vetített képek feldolgozása ---
print("🔎 Vetített képek feldolgozása...")

new_faces = []
face_id_counter = 0

for image_name in sorted(os.listdir(IMAGES_DIR)):
    if not image_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    image_path = os.path.join(IMAGES_DIR, image_name)
    image = face_recognition.load_image_file(image_path)
    locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, locations)

    for i, (location, encoding) in enumerate(zip(locations, encodings)):
        face_id = f"{image_name}_{i}"

        if not args.full and (image_name, face_id) in existing_faces:
            continue  # már létezik, kihagyjuk

        # Egyezés ismert arcokkal (pontosabb: face_distance alapján)
        name = None
        if not MANUAL_MODE and known_encodings:
            distances = face_recognition.face_distance(known_encodings, encoding)
            best_match_index = distances.argmin()
        if distances[best_match_index] < TOLERANCE:
            name = known_names[best_match_index]
        else:
            name = None


        top, right, bottom, left = location
        top = max(0, top - CROP_MARGIN)
        left = max(0, left - CROP_MARGIN)
        bottom = min(image.shape[0], bottom + CROP_MARGIN)
        right = min(image.shape[1], right + CROP_MARGIN)

        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        cropped_name = f"{face_id}.jpg"
        cropped_path = os.path.join(FACES_DIR, cropped_name)
        pil_image.save(cropped_path)

        new_faces.append({
            "image": image_name,
            "face_id": face_id,
            "name": name,
            "location": [top, right, bottom, left]
        })

# --- Mentés faces.json-ba ---
all_faces = []

# Meglévő arcokat megtartjuk, kivéve ha újrafeldolgozás van
if not args.full:
    all_faces.extend(previous_faces)

# Új arcokat hozzáadjuk
all_faces.extend(new_faces)

# Duplikációk kiszűrése
unique_faces = {(f["image"], f["face_id"]): f for f in all_faces}
final_faces = list(unique_faces.values())

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(final_faces, f, indent=2, ensure_ascii=False)

print(f"✅ Mentve: {OUTPUT_FILE} ({len(final_faces)} arc)")
