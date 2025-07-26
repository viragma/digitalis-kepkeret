# routes/main_routes.py

from flask import Blueprint, render_template, jsonify
import os
import random
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from services import data_manager

# Létrehozzuk a blueprintet URL előtag NÉLKÜL
main_bp = Blueprint('main_bp', __name__)

def get_image_metadata(image_path):
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'DateTimeOriginal':
                        return datetime.strptime(value, '%Y:%m:%d %H:%M:%S').strftime('%Y. %B')
    except Exception as e:
        print(f"Hiba az EXIF olvasásakor ({os.path.basename(image_path)}): {e}")
    return None

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
        image_filenames = [f for f in os.listdir(abs_image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        all_faces = data_manager.get_faces()
        faces_by_image = {}
        for face in all_faces:
            if face.get('image_file'):
                if face['image_file'] not in faces_by_image: faces_by_image[face['image_file']] = set()
                face_name = face.get('name')
                if face_name and face_name.strip() not in ['Ismeretlen', 'arc_nélkül']:
                    faces_by_image[face['image_file']].add(face_name.strip().title())

        detailed_image_list = []
        for filename in image_filenames:
            image_path = os.path.join(abs_image_folder_path, filename)
            detailed_image_list.append({
                "file": filename, "people": sorted(list(faces_by_image.get(filename, []))), "date": get_image_metadata(image_path)
            })

        final_playlist = []
        birthday_person = data_manager.get_todays_birthday_person()
        boost_ratio = slideshow_config.get('birthday_boost_ratio', 0)

        if birthday_person and boost_ratio > 0:
            birthday_playlist = [img for img in detailed_image_list if birthday_person in img['people']]
            other_playlist = [img for img in detailed_image_list if birthday_person not in img['people']]
            
            if not birthday_playlist:
                final_playlist = other_playlist
            elif boost_ratio == 100:
                final_playlist = birthday_playlist
            else:
                boost_percentage = boost_ratio
                other_percentage = 100 - boost_ratio
                if boost_percentage == 0 or other_percentage == 0:
                    common_divisor = 1
                else:
                    common_divisor = math.gcd(boost_percentage, other_percentage)
                bday_steps = boost_percentage // common_divisor
                other_steps = other_percentage // common_divisor
                while birthday_playlist or other_playlist:
                    for _ in range(bday_steps):
                        if birthday_playlist: final_playlist.append(birthday_playlist.pop(0))
                    for _ in range(other_steps):
                        if other_playlist: final_playlist.append(other_playlist.pop(0))
        else:
            final_playlist = detailed_image_list

        if slideshow_config.get('randomize_playlist', True):
            random.shuffle(final_playlist)
        
        return jsonify(final_playlist)

    except FileNotFoundError:
        return jsonify([])