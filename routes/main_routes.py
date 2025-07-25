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
    try:
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
        all_files = os.listdir(abs_image_folder_path)
        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # Történet mód: csak a születésnapos személy(ek) képei
        birthday_persons = []
        if birthday_story_mode:
            birthday_persons = data_manager.get_birthday_persons()
        if birthday_persons:
            # faces.json alapján csak azokat a képeket, ahol az ünnepelt szerepel
            faces = data_manager.get_faces()
            bp_names = [bp[0] for bp in birthday_persons]
            image_files = [face['image_file'] for face in faces if 'image_file' in face and face.get('name') in bp_names]
            # csak egyszer szerepeljen egy kép
            image_files = list(set(image_files))
            if slideshow_config.get('randomize_playlist', True):
                random.shuffle(image_files)
        else:
            if slideshow_config.get('randomize_playlist', True):
                random.shuffle(image_files)
        return jsonify(image_files)
    except FileNotFoundError:
        return jsonify([])
    
@main_bp.route('/birthday_info')
def get_birthday_info():
    birthday_persons = data_manager.get_birthday_persons()
    today = datetime.today()
    result = []
    for name, year in birthday_persons:
        age = today.year - year if year else ""
        result.append({"name": name, "age": age})
    return jsonify(result)