import os
import pickle
import face_recognition

KNOWN_FACES_DIR = 'data/known_faces'
ENCODINGS_CACHE = 'data/known_encodings.pkl'

def reencode_known_faces():
    print("🔄 Ismert arcok újraépítése...")

    known_encodings = []
    known_names = []

    for person_name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, person_name)
        if not os.path.isdir(person_dir):
            continue

        for filename in os.listdir(person_dir):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            path = os.path.join(person_dir, filename)
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person_name)

    with open(ENCODINGS_CACHE, 'wb') as f:
        pickle.dump((known_encodings, known_names), f)

    print(f"✅ Elmentve: {ENCODINGS_CACHE} ({len(known_encodings)} kód)")
