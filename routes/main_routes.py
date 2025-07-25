# routes/main_routes.py - BŐVÍTVE

from flask import Blueprint, render_template, jsonify
import os
from services import data_manager

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    # Ez a rész változatlan
    return render_template('index.html')

# --- ÚJ ÚTVONALAK A VETÍTŐHÖZ ---

@main_bp.route('/config')
def get_slideshow_config():
    """ Kiadja a vetítés beállításait a frontendnek. """
    config_data = data_manager.get_config()
    return jsonify(config_data.get('slideshow', {})) # Csak a 'slideshow' részt adjuk vissza

@main_bp.route('/imagelist')
def get_image_list():
    """ Kiadja a vetítendő képek listáját. """
    config_data = data_manager.get_config()
    image_folder_path = config_data.get('UPLOAD_FOLDER', 'static/images')
    
    try:
        # Létrehozzuk a képek relatív URL-jeinek listáját
        all_files = os.listdir(image_folder_path)
        image_files = [os.path.join(image_folder_path, f).replace('\\', '/') 
                       for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return jsonify(image_files)
    except FileNotFoundError:
        return jsonify([]) # Ha a mappa nem létezik, üres listát adunk vissza