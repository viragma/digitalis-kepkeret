# routes/main_routes.py - VÉGLEGES JAVÍTÁS

from flask import Blueprint, render_template, jsonify
import os
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
    config_data = data_manager.get_config()
    image_folder_path = config_data.get('UPLOAD_FOLDER', 'static/images')
    
    try:
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_path)
        all_files = os.listdir(abs_image_folder_path)
        
        # --- VÁLTOZÁS ---
        # Most már TÉNYLEG csak a fájlneveket adjuk vissza a listában.
        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return jsonify(image_files)
    except FileNotFoundError:
        return jsonify([])