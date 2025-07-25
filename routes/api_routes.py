from flask import Blueprint, jsonify, request, current_app
import os
import json

from services.stats import generate_stats
from services.face_backup import backup_faces_json
from services.db import get_all_config, set_config
from services.reencoder import reencode_known_faces

api_bp = Blueprint('api', __name__, url_prefix='/api')

# --- Fájlok elérési útjai ---
IMAGE_FOLDER = 'static/images'
FACES_JSON = 'data/faces.json'
CONFIG_FILE = 'data/config.json'
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')


# --- Képek listázása ---
@api_bp.route('/images')
def get_images():
    try:
        files = sorted([
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ])
        return jsonify({"images": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Konfiguráció olvasása ---
@api_bp.route('/config', methods=['GET'])
def get_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Konfiguráció frissítése ---
@api_bp.route('/config', methods=['POST'])
def update_config():
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Érvénytelen formátum"}), 400

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # később SocketIO értesítés itt (ha van)
        return jsonify({"status": "updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Arcok listázása ---
@api_bp.route('/faces')
def get_faces():
    try:
        with open(FACES_JSON, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Arc címkézése ---
@api_bp.route('/label', methods=['POST'])
def label_face_api():
    try:
        data = request.get_json()
        file = data['file']
        index = int(data['index'])
        name = data['name']

        with open(FACES_JSON, 'r', encoding='utf-8') as f:
            faces_data = json.load(f)

        if file not in faces_data or index >= len(faces_data[file]):
            return jsonify({"error": "Érvénytelen fájl vagy index"}), 400

        # Biztonsági mentés előtte
        backup_faces_json()

        # Frissítés
        faces_data[file][index]['name'] = name

        with open(FACES_JSON, 'w', encoding='utf-8') as f:
            json.dump(faces_data, f, indent=2, ensure_ascii=False)

        # később ide kerülhet websocket trigger is
        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Újratanítás indítása ---
@api_bp.route('/retrain', methods=['POST'])
def retrain_faces():
    try:
        result = reencode_all_faces()
        return jsonify({"status": "ok", "summary": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
