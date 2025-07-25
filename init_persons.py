import os
import json

KNOWN_FACES_DIR = 'data/known_faces'
PERSONS_FILE = 'data/persons.json'

def generate_persons_from_folders():
    if os.path.exists(PERSONS_FILE):
        with open(PERSONS_FILE, 'r', encoding='utf-8') as f:
            persons = json.load(f)
    else:
        persons = {}

    updated = False

    for person_name in os.listdir(KNOWN_FACES_DIR):
        person_path = os.path.join(KNOWN_FACES_DIR, person_name)
        if os.path.isdir(person_path) and person_name not in persons:
            persons[person_name] = {}
            updated = True
            print(f"[ADD] Hozzáadva: {person_name}")

    if updated:
        with open(PERSONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(persons, f, indent=2, ensure_ascii=False)
        print(f"✅ Frissítve: {PERSONS_FILE}")
    else:
        print("ℹ️ Nem történt változás, minden név szerepel már.")

if __name__ == "__main__":
    generate_persons_from_folders()
