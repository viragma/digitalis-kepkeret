import json
import os
from collections import Counter

FACES_FILE = os.path.join("data", "faces.json")

def generate_stats():
    print("[DEBUG] generate_stats() hívva")

    if not os.path.exists(FACES_FILE):
        print("[ERROR] Nem található a faces.json:", FACES_FILE)
        return {}

    try:
        with open(FACES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"[DEBUG] ✅ Sikeres betöltés: {len(data)} arc bejegyzés")

        counter = Counter()
        total_faces = 0
        unknown_faces = 0
        labeled_faces = 0
        ignored_faces = 0

        for face in data:
            if isinstance(face, dict):
                total_faces += 1
                name = face.get("name")
                status = face.get("status", "")
                if not name or name == "unknown":
                    unknown_faces += 1
                elif status == "labeled":
                    labeled_faces += 1
                    counter[name] += 1
                elif status == "ignored":
                    ignored_faces += 1
            else:
                print(f"[DEBUG] ⚠️ Kihagyva nem dict face: {face}")

        print(f"[DEBUG] 👥 Nevek listája: {list(counter.keys())}")

        return {
            "Összes arc": total_faces,
            "Ismeretlen arcok": unknown_faces,
            "Elnevezett arcok (labeled)": labeled_faces,
            "Ignorált arcok": ignored_faces,
            "Különböző nevek száma": len(counter)
        }

    except Exception as e:
        print("[ERROR] generate_stats() kivétel:", str(e))
        return {}
