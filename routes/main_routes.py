# routes/main_routes.py - VÉGLEGES JAVÍTÁS

from flask import Blueprint, render_template, jsonify
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
    
    try:
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
        all_files = os.listdir(abs_image_folder_path)
        
        # --- VÁLTOZÁS ---
        # Most már véglegesen csak a fájlneveket adjuk vissza.
        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if slideshow_config.get('randomize_playlist', True):
            random.shuffle(image_files)
            
        return jsonify(image_files)
    except FileNotFoundError:
        return jsonify([])