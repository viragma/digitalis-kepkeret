import os
import json
from PIL import Image

FACES_JSON_PATH = "data/faces.json"
KNOWN_FACES_DIR = "data/known_faces"
IMAGES_DIR = "static/images"


def load_faces_json():
    try:
        with open(FACES_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_faces_json(data):
    os.makedirs(os.path.dirname(FACES_JSON_PATH), exist_ok=True)
    with open(FACES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def crop_face(image_path, location):
    image = Image.open(image_path)
    top, right, bottom, left = location
    return image.crop((left, top, right, bottom))


def save_cropped_face(file: str, index: int, name: str) -> str:
    data = load_faces_json()
    if file not in data or index >= len(data[file]):
        raise ValueError("Érvénytelen fájl vagy index a faces.json-ben")

    location = data[file][index]["location"]
    data[file][index]["name"] = name
    save_faces_json(data)

    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(person_dir, exist_ok=True)

    image_path = os.path.join(IMAGES_DIR, file)
    cropped = crop_face(image_path, location)

    count = len(os.listdir(person_dir)) + 1
    filename = f"{name}_{count}.jpg"
    save_path = os.path.join(person_dir, filename)
    cropped.save(save_path)

    return filename


def get_known_people_stats():
    result = {}
    if not os.path.exists(KNOWN_FACES_DIR):
        return result

    for person in os.listdir(KNOWN_FACES_DIR):
        person_path = os.path.join(KNOWN_FACES_DIR, person)
        if os.path.isdir(person_path):
            count = len([
                f for f in os.listdir(person_path)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))
            ])
            result[person] = count
    return result
