# routes/main_routes.py - BŐVÍTVE A RANDOM SORREND LOGIKÁVAL

from flask import Blueprint, render_template, jsonify
import os
import random # <-- ÚJ IMPORT
from services import data_manager

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/config')
def get_slideshow_config():
    config_data = data_manager.get_config()
    # A config.json teljes 'slideshow' részét visszaadjuk
    return jsonify(config_data.get('slideshow', {}))

@main_bp.route('/imagelist')
def get_image_list():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    
    try:
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
        all_files = os.listdir(abs_image_folder_path)
        
        image_urls = [f'/{image_folder_name}/{f}'.replace('\\', '/') 
                      for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # --- ÚJ LOGIKA ---
        # Ha a beállítás aktív, megkeverjük a listát
        if slideshow_config.get('randomize_playlist', True): # Alapértelmezetten bekapcsolva
            random.shuffle(image_urls)
            
        return jsonify(image_urls)
    except FileNotFoundError:
        return jsonify([])