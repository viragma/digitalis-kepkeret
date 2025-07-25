# routes/api_routes.py - JAVÍTVA BLUEPRINTTÉ

from flask import Blueprint, request, jsonify
from services import data_manager

# --- VÁLTOZÁS ---
# Létrehozzuk az API blueprintet '/api' előtaggal
api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/faces', methods=['GET'])
def get_all_faces():
    """ Visszaadja az összes arc adatait JSON formátumban. """
    faces_data = data_manager.get_faces()
    return jsonify(faces_data)

@api_bp.route('/update_face_name', methods=['POST'])
def update_face_name():
    """ Frissíti egy adott archoz tartozó nevet. """
    data = request.get_json()
    face_path = data.get('face_path')
    new_name = data.get('new_name')

    if not face_path or new_name is None:
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400

    faces_data = data_manager.get_faces()
    
    face_found = False
    for face in faces_data:
        if face.get('face_path') == face_path:
            face['name'] = new_name
            face_found = True
            break
    
    if face_found:
        data_manager.save_faces(faces_data)
        return jsonify({'status': 'success', 'message': f'Arc frissítve: {new_name}'})
    else:
        return jsonify({'status': 'error', 'message': 'A megadott arc nem található'}), 404