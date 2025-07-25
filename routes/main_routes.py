# routes/main_routes.py - VÉGLEGES JAVÍTÁS

from flask import Blueprint, render_template, jsonify, request
from datetime import datetime
import os
import random
from services import data_manager

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/config')
def get_slideshow_config():
    config_data = data_manager.get_config()
    return jsonify(config_data.get('slideshow', {}))

@main_bp.route('/imagelist')
def get_image_list():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    birthday_story_mode = slideshow_config.get('birthday_story_mode', False)
    # ÚJ: highlight filter betöltése
    try:
        with open("data/highlight_filter.json", "r", encoding="utf-8") as f:
            highlight = json.load(f)
    except Exception:
        highlight = {"names": [], "custom_text": ""}

    try:
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
        all_files = os.listdir(abs_image_folder_path)
        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        faces = data_manager.get_faces()

        # 1. Ha highlight filter aktív → csak azokat mutassa
        if highlight["names"]:
            selected_names = [name.strip() for name in highlight["names"] if name]
            image_files = [face['image'] for face in faces
                           if 'image' in face
                           and face.get('name') and face.get('name').strip() in selected_names]
            image_files = list(set(image_files))
            if slideshow_config.get('randomize_playlist', True):
                random.shuffle(image_files)
            return jsonify({
                "images": image_files,
                "overlay_text": highlight.get("custom_text", "")
            })

        # 2. Ha birthday_story_mode aktív → csak szülinapos(oka)t mutassa
        birthday_persons = []
        if birthday_story_mode:
            birthday_persons = data_manager.get_birthday_persons()
        if birthday_persons:
            bp_names = [bp[0] for bp in birthday_persons]
            image_files = [face['image'] for face in faces
                           if 'image' in face
                           and face.get('name') in bp_names]
            image_files = list(set(image_files))
            if slideshow_config.get('randomize_playlist', True):
                random.shuffle(image_files)
        else:
            if slideshow_config.get('randomize_playlist', True):
                random.shuffle(image_files)
        return jsonify({
            "images": image_files,
            "overlay_text": ""
        })
    except FileNotFoundError:
        return jsonify({"images": [], "overlay_text": ""})
    
@main_bp.route('/birthday_info')
def get_birthday_info():
    birthday_persons = data_manager.get_birthday_persons()
    today = datetime.today()
    result = []
    for name, year in birthday_persons:
        age = today.year - year if year else ""
        result.append({"name": name, "age": age})
    return jsonify(result)