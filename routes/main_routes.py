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
def get_config():
    config = data_manager.get_config()
    return jsonify(config.get("slideshow", {}))

@main_bp.route('/imagelist')
def get_image_list():
    faces = data_manager.get_faces()
    config = data_manager.get_config()
    slideshow_config = config.get("slideshow", {})

    selected_names = slideshow_config.get("persons", [])
    birthday_story_mode = slideshow_config.get("birthday_mode", False)

    image_files = []

    # 1. Ha van kiválasztott személy(ek) ÉS nincs szülinapos mód
    if selected_names and not birthday_story_mode:
        image_files = [face['image'] for face in faces
                       if 'image' in face
                       and face.get('name') and face.get('name').strip() in selected_names]
        image_files = list(set(image_files))
        if slideshow_config.get('randomize_playlist', True):
            random.shuffle(image_files)
        return jsonify(image_files)

    # 2. Ha birthday_mode aktív: csak mai szülinaposok képei
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
            return jsonify(image_files)
        else:
            # NINCS ma szülinapos: fallback → összes kép
            image_files = [face['image'] for face in faces if 'image' in face]
            image_files = list(set(image_files))
            if slideshow_config.get('randomize_playlist', True):
                random.shuffle(image_files)
            return jsonify(image_files)

    # 3. Egyik sem: összes kép
    image_files = [face['image'] for face in faces if 'image' in face]
    image_files = list(set(image_files))
    if slideshow_config.get('randomize_playlist', True):
        random.shuffle(image_files)
    return jsonify(image_files)

@main_bp.route('/birthday_info')
def get_birthday_info():
    birthday_persons = data_manager.get_birthday_persons()
    today = datetime.today()
    result = []
    for name, year in birthday_persons:
        age = today.year - year if year else ""
        result.append({"name": name, "age": age})
    return jsonify(result)

@main_bp.route('/api/persons.json')
def get_persons():
    import json
    with open('data/persons.json', encoding='utf-8') as f:
        return jsonify(json.load(f))