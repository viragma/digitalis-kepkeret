# routes/api/trainer.py
import os
from flask import Blueprint, jsonify, send_from_directory
from services import data_manager, training_service

trainer_api_bp = Blueprint('trainer_api_bp', __name__, url_prefix='/api')

KNOWN_FACES_DIR_ROOT = os.path.join(os.getcwd(), 'data', 'known_faces')

@trainer_api_bp.route('/trainer/persons', methods=['GET'])
def get_trainer_persons():
    conn = data_manager.get_db_connection()
    persons_rows = conn.execute("""
        SELECT p.name, f.face_path as profile_image 
        FROM persons p
        LEFT JOIN faces f ON p.profile_face_id = f.id
        WHERE p.is_active = 1
        ORDER BY p.name
    """).fetchall()
    conn.close()
    
    processed_persons = []
    for row in persons_rows:
        person_dict = dict(row)
        if person_dict.get('profile_image'):
             try:
                # A make_web_path logikáját ide helyezzük a tisztább kódért
                path = person_dict['profile_image'].replace('\\', '/')
                person_dict['profile_image'] = '/' + path.split('static/', 1)[1]
             except (IndexError, AttributeError):
                person_dict['profile_image'] = None
        processed_persons.append(person_dict)
        
    return jsonify(processed_persons)

@trainer_api_bp.route('/trainer/person_details/<name>', methods=['GET'])
def get_person_training_details(name):
    person_dir = os.path.join(KNOWN_FACES_DIR_ROOT, name)
    training_images_data = []
    if os.path.isdir(person_dir):
        for filename in os.listdir(person_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(person_dir, filename)
                analysis = training_service.analyze_training_image(full_path)
                training_images_data.append({
                    "path": f'/api/trainer/training_image/{name}/{filename}',
                    "analysis": analysis
                })

    average_face_url = training_service.generate_average_face_image(name)
    
    return jsonify({
        "training_images": training_images_data,
        "average_face_image": average_face_url,
        "suggestions": ["A javaslatok generálása a következő lépés."] 
    })

@trainer_api_bp.route('/trainer/training_image/<person_name>/<filename>')
def serve_training_image(person_name, filename):
    """Biztonságosan kiszolgál egy tanítóképet a 'data/known_faces' mappából."""
    person_dir = os.path.join(KNOWN_FACES_DIR_ROOT, person_name)
    return send_from_directory(person_dir, filename)