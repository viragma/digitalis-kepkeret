# routes/main_routes.py - VÉGLEGESEN JAVÍTVA

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
    # A config.json-ban relatív útvonalnak kell lennie, pl. "static/images"
    image_folder_name = config_data.get('UPLOAD_FOLDER', 'static/images')
    
    try:
        # A projekt gyökeréhez képest keressük meg a mappát
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
        all_files = os.listdir(abs_image_folder_path)
        
        # --- VÁLTOZÁS ---
        # Teljes, böngésző által értelmezhető URL-t generálunk
        image_urls = [f'/{image_folder_name}/{f}'.replace('\\', '/') 
                      for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return jsonify(image_urls)
    except FileNotFoundError:
        return jsonify([])