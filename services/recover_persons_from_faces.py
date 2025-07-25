# scripts/recover_persons_from_faces.py
import json
from collections import defaultdict

faces_path = "data/faces.json"
output_path = "data/person.json"

persons = defaultdict(dict)

with open(faces_path, "r", encoding="utf-8") as f:
    faces = json.load(f)

for face in faces:
    name = face.get("name")
    if name and name.upper() != "UNKNOWN":
        if name not in persons:
            persons[name] = {"birthday": ""}

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(persons, f, indent=2, ensure_ascii=False)

print(f"✅ Visszaállított persons.json {len(persons)} névvel.")
