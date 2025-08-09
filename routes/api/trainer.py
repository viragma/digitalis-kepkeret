# routes/api/trainer.py
import os
import shutil
from flask import Blueprint, jsonify, send_from_directory, request
from services import data_manager, training_service, event_logger
from .utils import make_web_path

trainer_api_bp = Blueprint('trainer_api_bp', __name__, url_prefix='/api')

KNOWN_FACES_DIR_ROOT = os.path.join(os.getcwd(), 'data', 'known_faces')

@trainer_api_bp.route('/trainer/persons', methods=['GET'])
def get_trainer_persons():
    conn = data_manager.get_db_connection()
    persons_rows = conn.execute("""
        SELECT p.name, f.face_path as profile_image 
        FROM persons p
        LEFT JOIN faces f ON p.profile_face_id = f.id
        WHERE p.is_active = 1 ORDER BY p.name
    """).fetchall()
    conn.close()
    
    processed_persons = []
    for row in persons_rows:
        person_dict = dict(row)
        person_dict['profile_image'] = make_web_path(person_dict.get('profile_image'))
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
    person_dir = os.path.join(KNOWN_FACES_DIR_ROOT, person_name)
    return send_from_directory(person_dir, filename)

@trainer_api_bp.route('/trainer/confirmed_faces/<person_name>', methods=['GET'])
def get_confirmed_faces_for_person(person_name):
    conn = data_manager.get_db_connection()
    rows = conn.execute("""
        SELECT f.face_path
        FROM faces f
        JOIN persons p ON f.person_id = p.id
        WHERE p.name = ? AND f.is_confirmed = 1 AND f.is_manual = 0
        ORDER BY f.distance
        LIMIT 20
    """, (person_name,)).fetchall()
    conn.close()
    return jsonify([make_web_path(row['face_path']) for row in rows if row['face_path'] is not None])

@trainer_api_bp.route('/trainer/promote_face', methods=['POST'])
def promote_face_to_training():
    """ Átmásol egy megerősített arcképet a tanító mappába. """
    data = request.get_json()
    person_name = data.get('name')
    face_path = data.get('face_path') # Ez egy web-útvonal, pl. /static/faces/...

    if not person_name or not face_path:
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok.'}), 400

    try:
        # Visszaalakítjuk a web-útvonalat teljes szerver-oldali útvonallá
        source_full_path = os.path.join(os.getcwd(), face_path.lstrip('/\\'))
        
        target_dir = os.path.join(KNOWN_FACES_DIR_ROOT, person_name)
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.basename(source_full_path)
        target_full_path = os.path.join(target_dir, filename)

        if not os.path.exists(source_full_path):
             return jsonify({'status': 'error', 'message': 'Forrásfájl nem található.'}), 404

        if os.path.exists(target_full_path):
            return jsonify({'status': 'info', 'message': 'Ez a kép már a tanítóképek között van.'})

        shutil.copy(source_full_path, target_full_path)
        
        event_logger.log_event(f"Új tanítókép hozzáadva '{person_name}'-hez: {filename}")
        return jsonify({'status': 'success', 'message': f"Kép sikeresen hozzáadva '{person_name}' tanítóképeihez."})

    except Exception as e:
        print(f"Hiba a tanítókép hozzáadásakor: {e}")
        return jsonify({'status': 'error', 'message': 'Szerver oldali hiba történt.'}), 500