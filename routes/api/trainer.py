# routes/api/trainer.py
import os
from flask import Blueprint, jsonify, send_from_directory
from services import data_manager

trainer_api_bp = Blueprint('trainer_api_bp', __name__, url_prefix='/api')

KNOWN_FACES_DIR_ROOT = os.path.join(os.getcwd(), 'data', 'known_faces')

@trainer_api_bp.route('/trainer/persons', methods=['GET'])
def get_trainer_persons():
    """Visszaadja a személyek listáját a tanító felülethez."""
    conn = data_manager.get_db_connection()
    # Módosítva, hogy a profilkép útvonalát is visszaadja
    persons_rows = conn.execute("""
        SELECT p.name, f.face_path as profile_image 
        FROM persons p
        LEFT JOIN faces f ON p.profile_face_id = f.id
        WHERE p.is_active = 1
        ORDER BY p.name
    """).fetchall()
    conn.close()
    
    # A profilkép útvonalakat web-kompatibilissé tesszük
    processed_persons = []
    for row in persons_rows:
        person_dict = dict(row)
        if person_dict.get('profile_image'):
             person_dict['profile_image'] = '/' + person_dict['profile_image'].replace('\\', '/').split('static/', 1)[-1]
        processed_persons.append(person_dict)
        
    return jsonify(processed_persons)

@trainer_api_bp.route('/trainer/person_details/<name>', methods=['GET'])
def get_person_training_details(name):
    """Visszaadja egy személy tanítóképeit és a javaslatokat."""
    person_dir = os.path.join(KNOWN_FACES_DIR_ROOT, name)
    training_images = []
    if os.path.isdir(person_dir):
        for filename in os.listdir(person_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                # JAVÍTÁS: A helyes, új útvonalat generáljuk le
                training_images.append(f'/api/trainer/training_image/{name}/{filename}')

    return jsonify({
        "training_images": training_images,
        "average_face_image": None,
        "suggestions": [
            "A pontosság javításához tölts fel több, különböző szögből készült képet.",
            "Egy tanítókép enyhén elmosódott."
        ] 
    })

@trainer_api_bp.route('/trainer/training_image/<person_name>/<filename>')
def serve_training_image(person_name, filename):
    """Biztonságosan kiszolgál egy tanítóképet a 'data/known_faces' mappából."""
    person_dir = os.path.join(KNOWN_FACES_DIR_ROOT, person_name)
    return send_from_directory(person_dir, filename)