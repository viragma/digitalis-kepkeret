from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import json
import os
import shutil
from datetime import datetime
from PIL import Image

from services.face_backup import list_backups, restore_faces_json
from services.db import get_all_config, set_config, load_persons, save_persons, load_faces_json, save_faces_json
from services.stats import generate_stats

from services.reencoder import reencode_known_faces
from services.quality import is_good_training_image

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Admin dashboard ---
@admin_bp.route('/')
def admin_index():
    config = get_all_config()
    persons = load_persons()
    backups = list_backups()
    stats = generate_stats()

    faces = []
    faces_by_image = {}
    try:
        with open('data/faces.json', 'r', encoding='utf-8') as f:
            all_faces = json.load(f)
            # Csak azokat az arcokat jelenítjük meg, amik még nincsenek elnevezve vagy nem ignoráltak
            faces = [face for face in all_faces if face.get("status") != "labeled" and face.get("status") != "ignored"]
            for face in faces:
                image = face["image"]
                if image not in faces_by_image:
                    faces_by_image[image] = {"image": image, "faces": []}
                faces_by_image[image]["faces"].append(face)
    except Exception as e:
        print(f"Hiba a faces.json betöltésekor: {e}")

    return render_template(
        'admin.html',
        config=config,
        persons=persons,
        backups=backups,
        stats=stats,
        faces=list(faces_by_image.values()),
        known_names=persons.keys() if persons else []
    )


# --- Konfiguráció mentése ---
@admin_bp.route('/save_config', methods=['POST'])
def save_config_route():
    try:
        config_data = request.form.to_dict()
        set_config(config_data)
        flash("Konfiguráció mentve.", "success")
    except Exception as e:
        flash(f"Hiba a konfiguráció mentésekor: {str(e)}", "danger")
    return redirect(url_for('admin.admin_index'))

# --- Person lista frissítése ---
@admin_bp.route('/save_persons', methods=['POST'])
def save_persons_route():
    try:
        raw_data = request.form.to_dict(flat=False)
        updated_persons = {}

        # Kinyerjük a birthdays mezőket
        birthdays = raw_data.get('birthdays', {})
        if isinstance(birthdays, dict):
            for name, birthday in birthdays.items():
                updated_persons[name] = {"birthday": birthday}
        else:
            for key, values in raw_data.items():
                if key.startswith("birthdays[") and key.endswith("]"):
                    name = key[10:-1]
                    updated_persons[name] = {"birthday": values[0] if isinstance(values, list) else values}

        # Védelem: ha nincs adat, ne írjuk felül a fájlt
        if not updated_persons:
            flash("⚠️ Nem érkezett menthető születésnap – nem történt mentés.", "warning")
            return redirect(url_for('admin.admin_index'))

        # Automatikus backup
        backup_path = f"data/backups/persons_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        shutil.copy("data/persons.json", backup_path)

        save_persons(updated_persons)
        flash("✅ Születésnapok mentve.", "success")
        return redirect(url_for('admin.admin_index'))

    except Exception as e:
        flash(f"❌ Hiba a mentés során: {str(e)}", "danger")
        return redirect(url_for('admin.admin_index'))



# --- faces.json visszaállítása ---
@admin_bp.route('/restore_faces', methods=['POST'])
def restore_faces_route():
    backup_file = request.form.get('backup')
    try:
        if restore_faces_json(backup_file):
            flash("faces.json visszaállítva.", "success")
        else:
            flash("Nem sikerült a visszaállítás.", "danger")
    except Exception as e:
        flash(f"Hiba: {str(e)}", "danger")
    return redirect(url_for('admin.admin_index'))

# --- Újratanítás indítása ---
@admin_bp.route('/retrain', methods=['POST'])
def retrain_faces_route():
    try:
        reencode_known_faces()
        flash("Újratanítás sikeres!", "success")
    except Exception as e:
        flash(f"Hiba az újratanítás során: {str(e)}", "danger")
    return redirect(url_for('admin.admin_index'))

# --- Egyedi arc mentése tanítóképnek + státusz frissítés ---
@admin_bp.route('/save_face', methods=['POST'])
def save_face():
    data = request.json
    name = data['name']
    image_filename = data['image']
    face_id = data['face_id']

    # Frissítsük a faces.json-t
    faces = load_faces_json()
    updated = False
    for face in faces:
        if face['image'] == image_filename and face['face_id'] == face_id:
            face['name'] = name
            face['manual'] = True
            face['status'] = "ignored" if name.upper() == "UNKNOWN" else "labeled"
            updated = True
            break

    if updated:
        save_faces_json(faces)
    else:
        return jsonify({"error": "Nem található az adott arc."}), 404

    if name.upper() != "UNKNOWN":
        # Tanítókép mentése csak ha jó minőségű
        src_face_path = os.path.join('static', 'faces', f"{image_filename.rsplit('.', 1)[0]}_{face_id}.jpg")
        if os.path.exists(src_face_path) and is_good_training_image(src_face_path):
            dst_dir = os.path.join('data', 'known_faces', name)
            os.makedirs(dst_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dst_path = os.path.join(dst_dir, f"{name}_{timestamp}.jpg")
            shutil.copyfile(src_face_path, dst_path)
            return jsonify({"status": "ok", "message": f"✅ Arc elmentve és tanítókép készült: {dst_path}"})
        else:
            return jsonify({"status": "ok", "message": f"ℹ️ Arc elmentve, de nem elég jó tanítóképnek."})
    else:
        return jsonify({"status": "ok", "message": f"ℹ️ Arc figyelmen kívül hagyva."})
