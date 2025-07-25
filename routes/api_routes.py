# routes/api_routes.py - BŐVÍTVE

from flask import Blueprint, request, jsonify
from services import data_manager

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/faces/unknown', methods=['GET'])
def get_unknown_faces():
    """ Csak az 'Ismeretlen' arcok listáját adja vissza. """
    all_faces = data_manager.get_faces()
    unknown_faces = [face for face in all_faces if face.get('name') == 'Ismeretlen']
    return jsonify(unknown_faces)

@api_bp.route('/persons', methods=['GET'])
def get_persons_api():
    """ Visszaadja a személyek listáját a dropdown menühöz. """
    persons_data = data_manager.get_persons()
    # A nevek listájára van szükségünk
    return jsonify(list(persons_data.keys()))

@api_bp.route('/update_face_name', methods=['POST'])
def update_face_name():
    """ Frissíti egy adott archoz tartozó nevet. (Ez változatlan) """
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
    
    # routes/api_routes.py - A FÁJL VÉGÉRE

@api_bp.route('/update_faces_batch', methods=['POST'])
def update_faces_batch():
    """ Egyszerre több arc nevét frissíti. """
    updates = request.get_json() # [{face_path: '...', new_name: '...'}, ...]
    if not isinstance(updates, list):
        return jsonify({'status': 'error', 'message': 'Hibás adatformátum'}), 400

    faces_data = data_manager.get_faces()
    
    # A gyorsabb kereséshez készítünk egy szótárat a face_path alapján
    faces_map = {face.get('face_path'): face for face in faces_data if face.get('face_path')}

    updated_count = 0
    for update in updates:
        face_path = update.get('face_path')
        new_name = update.get('new_name')
        if face_path in faces_map:
            faces_map[face_path]['name'] = new_name
            updated_count += 1
            
    if updated_count > 0:
        data_manager.save_faces(faces_data)
        return jsonify({'status': 'success', 'message': f'{updated_count} arc sikeresen frissítve'})
    else:
        return jsonify({'status': 'error', 'message': 'Nincs frissítendő arc'}), 400