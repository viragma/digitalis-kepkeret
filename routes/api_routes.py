# routes/api_routes.py
import os
import shutil
from flask import Blueprint, request, jsonify
from services import data_manager
from datetime import datetime, date, timedelta
from extensions import socketio

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/all_images', methods=['GET'])
def get_all_images():
    """ Visszaadja az összes kép listáját, lapozható formában. """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    offset = (page - 1) * limit

    config = data_manager.get_config()
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)

    try:
        all_files = sorted(
            [f for f in os.listdir(abs_image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
            reverse=True # Legújabbak elöl
        )
        paginated_files = all_files[offset : offset + limit]
        
        return jsonify({
            "images": paginated_files,
            "page": page,
            "has_next": len(all_files) > offset + limit
        })
    except FileNotFoundError:
        return jsonify({"images": [], "page": 1, "has_next": False})

# ... Itt következik az összes többi, már meglévő API végpont ...

@api_bp.route('/person/update_birthday', methods=['POST'])
def update_person_birthday():
    data = request.get_json()
    name = data.get('name')
    birthday_str = data.get('birthday', '')
    if not name: return jsonify({'status': 'error', 'message': 'Hiányzó név.'}), 400
    persons_data = data_manager.get_persons()
    if name in persons_data:
        persons_data[name]['birthday'] = birthday_str.replace('-', '.') if birthday_str else ""
        data_manager.save_persons(persons_data)
        return jsonify({'status': 'success', 'message': f'{name} születésnapja frissítve.'})
    return jsonify({'status': 'error', 'message': 'Személy nem található'}), 404

@api_bp.route('/upcoming_birthdays', methods=['GET'])
def get_upcoming_birthdays():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    if not slideshow_config.get('show_upcoming_birthdays', True): return jsonify([])
    limit_days = slideshow_config.get('upcoming_days_limit', 30)
    persons = data_manager.get_persons()
    today = date.today()
    upcoming = []
    for name, data in persons.items():
        birthday_str = data.get("birthday")
        if not birthday_str: continue
        try:
            birth_date = datetime.strptime(birthday_str.strip(), '%Y.%m.%d').date()
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today: next_birthday = next_birthday.replace(year=today.year + 1)
            days_left = (next_birthday - today).days
            if 0 <= days_left <= limit_days: upcoming.append({"name": name, "days_left": days_left})
        except (ValueError, TypeError): continue
    upcoming.sort(key=lambda x: x['days_left'])
    return jsonify(upcoming)

@api_bp.route('/persons/gallery_data', methods=['GET'])
def get_persons_gallery_data():
    persons = data_manager.get_persons()
    all_faces = data_manager.get_faces()
    face_counts = {name: 0 for name in persons.keys()}
    for face in all_faces:
        name = face.get('name')
        if name and name in face_counts: face_counts[name] += 1
    gallery_data = [{"name": name, "data": data, "face_count": face_counts.get(name, 0)} for name, data in persons.items()]
    return jsonify(gallery_data)

@api_bp.route('/persons/reassign_batch', methods=['POST'])
def reassign_persons_batch():
    data = request.get_json()
    source_names, target_name = data.get('source_names', []), data.get('target_name')
    if not source_names or not target_name: return jsonify({'status': 'error', 'message': 'Hiányzó forrás- vagy célnevek.'}), 400
    persons_data, all_faces = data_manager.get_persons(), data_manager.get_faces()
    for face in all_faces:
        if face.get('name') in source_names: face['name'] = target_name
    for name in source_names:
        if name in persons_data:
            del persons_data[name]
            person_dir = os.path.join('data', 'known_faces', name)
            if os.path.isdir(person_dir): shutil.rmtree(person_dir)
    data_manager.save_persons(persons_data)
    data_manager.save_faces(all_faces)
    return jsonify({'status': 'success', 'message': f'{len(source_names)} személy sikeresen átnevezve erre: {target_name}'})

@api_bp.route('/persons/delete_batch', methods=['POST'])
def delete_persons_batch():
    names_to_delete = request.get_json().get('names', [])
    if not names_to_delete: return jsonify({'status': 'error', 'message': 'Nincs kiválasztott személy.'}), 400
    persons_data, all_faces = data_manager.get_persons(), data_manager.get_faces()
    deleted_count = 0
    for name in names_to_delete:
        if name in persons_data:
            del persons_data[name]
            deleted_count += 1
            person_dir = os.path.join('data', 'known_faces', name)
            if os.path.isdir(person_dir): shutil.rmtree(person_dir)
    for face in all_faces:
        if face.get('name') in names_to_delete: face['name'] = 'Ismeretlen'
    data_manager.save_persons(persons_data)
    data_manager.save_faces(all_faces)
    return jsonify({'status': 'success', 'message': f'{deleted_count} személy sikeresen törölve.'})

@api_bp.route('/birthday_info', methods=['GET'])
def get_birthday_info():
    config = data_manager.get_config()
    slideshow_config = config.get('slideshow', {})
    if not slideshow_config.get('birthday_boost_ratio', 0) > 0: return jsonify({})
    birthday_person_name = data_manager.get_todays_birthday_person()
    if birthday_person_name:
        persons = data_manager.get_persons()
        birthday_str = persons.get(birthday_person_name, {}).get('birthday')
        try:
            birthday = datetime.strptime(birthday_str.replace('.', '').strip(), '%Y%m%d')
            age = datetime.now().year - birthday.year
            message = slideshow_config.get('birthday_message', 'Boldog Születésnapot!')
            return jsonify({"name": birthday_person_name, "age": age, "message": message})
        except (ValueError, TypeError): return jsonify({})
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
    face_path, new_name = data.get('face_path'), data.get('new_name')
    if not face_path or new_name is None: return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400
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
    return jsonify({'status': 'error', 'message': 'A megadott arc nem található'}), 404

@api_bp.route('/faces/by_person/<name>', methods=['GET'])
def get_faces_by_person(name):
    page = request.args.get('page', 1, type=int)
    limit = 30
    offset = (page - 1) * limit
    all_faces = data_manager.get_faces()
    person_faces = [face for face in all_faces if face.get('name') == name]
    paginated_faces = person_faces[offset : offset + limit]
    return jsonify({"faces": paginated_faces, "total": len(person_faces)})

@api_bp.route('/persons/set_profile_image', methods=['POST'])
def set_profile_image():
    data = request.get_json()
    person_name, face_path = data.get('name'), data.get('face_path')
    if not person_name or not face_path: return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400
    persons_data = data_manager.get_persons()
    if person_name in persons_data:
        persons_data[person_name]['profile_image'] = face_path
        data_manager.save_persons(persons_data)
        return jsonify({'status': 'success', 'message': 'Profilkép beállítva!'})
    return jsonify({'status': 'error', 'message': 'Személy nem található'}), 404

@api_bp.route('/faces/delete', methods=['POST'])
def delete_face():
    data = request.get_json()
    face_path_to_delete = data.get('face_path')
    if not face_path_to_delete: return jsonify({'status': 'error', 'message': 'Hiányzó face_path'}), 400
    all_faces = data_manager.get_faces()
    updated_faces = [face for face in all_faces if face.get('face_path') != face_path_to_delete]
    if len(updated_faces) < len(all_faces):
        data_manager.save_faces(updated_faces)
        return jsonify({'status': 'success', 'message': 'Arc sikeresen törölve.'})
    return jsonify({'status': 'error', 'message': 'A törlendő arc nem található'}), 404

@api_bp.route('/faces/reassign_batch', methods=['POST'])
def reassign_faces_batch():
    data = request.get_json()
    face_paths, target_name = data.get('face_paths', []), data.get('target_name')
    if not face_paths or not target_name: return jsonify({'status': 'error', 'message': 'Hiányzó adatok.'}), 400
    all_faces = data_manager.get_faces()
    for face in all_faces:
        if face.get('face_path') in face_paths: face['name'] = target_name
    data_manager.save_faces(all_faces)
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen átnevezve erre: {target_name}'})

@api_bp.route('/faces/delete_batch', methods=['POST'])
def delete_faces_batch():
    face_paths = request.get_json().get('face_paths', [])
    if not face_paths: return jsonify({'status': 'error', 'message': 'Nincs kiválasztott arc.'}), 400
    all_faces = data_manager.get_faces()
    updated_faces = [face for face in all_faces if face.get('face_path') not in face_paths]
    data_manager.save_faces(updated_faces)
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen törölve.'})