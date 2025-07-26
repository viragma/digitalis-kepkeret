# routes/api_routes.py
from flask import Blueprint, request, jsonify
from services import data_manager
from datetime import datetime

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/persons/gallery_data', methods=['GET'])
def get_persons_gallery_data():
    persons = data_manager.get_persons()
    gallery_data = [{"name": name, "data": data} for name, data in persons.items()]
    return jsonify(gallery_data)

@api_bp.route('/faces/by_person/<name>', methods=['GET'])
def get_faces_by_person(name):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    offset = (page - 1) * limit
    all_faces = data_manager.get_faces()
    person_faces = [face for face in all_faces if face.get('name') == name]
    paginated_faces = person_faces[offset : offset + limit]
    return jsonify({"faces": paginated_faces, "total": len(person_faces)})

@api_bp.route('/persons/set_profile_image', methods=['POST'])
def set_profile_image():
    data = request.get_json()
    person_name = data.get('name')
    face_path = data.get('face_path')
    if not person_name or not face_path:
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400
    persons_data = data_manager.get_persons()
    if person_name in persons_data:
        persons_data[person_name]['profile_image'] = face_path
        data_manager.save_persons(persons_data)
        return jsonify({'status': 'success', 'message': 'Profilkép beállítva!'})
    return jsonify({'status': 'error', 'message': 'Személy nem található'}), 404
# ... a többi meglévő API végpont (birthday_info, faces/unknown, stb.) változatlan ...

@api_bp.route('/birthday_info', methods=['GET'])
def get_birthday_info():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    
    if not slideshow_config.get('birthday_boost', False):
        return jsonify({})

    birthday_person_name = data_manager.get_todays_birthday_person()
    
    if birthday_person_name:
        persons = data_manager.get_persons()
        birthday_str = persons.get(birthday_person_name)
        try:
            birthday = datetime.strptime(birthday_str.replace('.', '').strip(), '%Y%m%d')
            age = datetime.now().year - birthday.year
            message = slideshow_config.get('birthday_message', 'Boldog Születésnapot!')
            return jsonify({"name": birthday_person_name, "age": age, "message": message})
        except (ValueError, TypeError):
             return jsonify({})
            
    return jsonify({})

@api_bp.route('/faces/unknown', methods=['GET'])
def get_unknown_faces():
    all_faces = data_manager.get_faces()
    unknown_faces = [face for face in all_faces if face.get('name') == 'Ismeretlen']
    return jsonify(unknown_faces)

@api_bp.route('/persons', methods=['GET'])
def get_persons_api():
    persons_data = data_manager.get_persons()
    return jsonify(list(persons_data.keys()))

@api_bp.route('/update_face_name', methods=['POST'])
def update_face_name():
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

@api_bp.route('/update_faces_batch', methods=['POST'])
def update_faces_batch():
    updates = request.get_json()
    if not isinstance(updates, list):
        return jsonify({'status': 'error', 'message': 'Hibás adatformátum'}), 400

    faces_data = data_manager.get_faces()
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