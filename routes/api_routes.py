# routes/api_routes.py
import os
import shutil
import subprocess
import sys
from flask import Blueprint, request, jsonify
from services import data_manager, event_logger, theme_engine
from datetime import datetime, date, timedelta
from extensions import socketio
from PIL import Image
import psutil

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

@api_bp.route('/active_theme', methods=['GET'])
def get_active_theme_api():
    active_themes = theme_engine.get_active_themes()
    return jsonify(active_themes)

@api_bp.route('/event_log', methods=['GET'])
def get_event_log():
    log_file_path = os.path.join(os.getcwd(), 'data', 'events.log')
    try:
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines()[:15]]
            return jsonify(lines)
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/dashboard_stats', methods=['GET'])
def get_dashboard_stats():
    try:
        config = data_manager.get_config()
        image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
        abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
        total_images = len([f for f in os.listdir(abs_image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
        persons = data_manager.get_persons()
        all_faces = data_manager.get_faces()
        known_persons = len(persons)
        recognized_faces, unknown_faces = 0, 0
        for face in all_faces:
            name = face.get('name')
            if name and name not in ['Ismeretlen', 'arc_nélkül']: recognized_faces += 1
            elif name == 'Ismeretlen': unknown_faces += 1
        latest_images = sorted([f for f in os.listdir(abs_image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))], key=lambda f: os.path.getmtime(os.path.join(abs_image_folder_path, f)), reverse=True)[:5]
        return jsonify({"total_images": total_images, "known_persons": known_persons, "recognized_faces": recognized_faces, "unknown_faces": unknown_faces, "latest_images": latest_images})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/system_stats', methods=['GET'])
def get_system_stats():
    try:
        config = data_manager.get_config()
        images_folder_path = os.path.join(os.getcwd(), config.get('UPLOAD_FOLDER', 'static/images'))
        faces_folder_path = os.path.join(os.getcwd(), 'static/faces')
        total, used, free = shutil.disk_usage("/")
        disk_percent = (used / total) * 100
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=None)
        return jsonify({
            "disk": { "percent": round(disk_percent, 1), "free_gb": round(free / (1024**3), 1) },
            "memory": { "percent": memory.percent, "total_gb": round(memory.total / (1024**3), 1) },
            "cpu": { "percent": cpu_percent },
            "images_folder_size_mb": get_folder_size_mb(images_folder_path),
            "faces_folder_size_mb": get_folder_size_mb(faces_folder_path)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_folder_size_mb(folder_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    except FileNotFoundError:
        return 0
    return round(total_size / (1024 * 1024), 1)


@api_bp.route('/run_face_detection', methods=['POST'])
def run_face_detection():
    try:
        python_executable = sys.executable
        script_path = os.path.join(os.getcwd(), 'scripts', 'detect_faces.py')
        if not os.path.exists(script_path):
            return jsonify({"status": "error", "message": "A detect_faces.py script nem található."}), 404
        subprocess.Popen([python_executable, script_path])
        event_logger.log_event("Arcfelismerési folyamat elindítva a Műszerfalról.")
        return jsonify({"status": "success", "message": "Arcfelismerés elindítva a háttérben."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@api_bp.route('/all_images', methods=['GET'])
def get_all_images():
    page = request.args.get('page', 1, type=int)
    limit = 30
    filter_person = request.args.get('person', None)
    filter_status = request.args.get('status', None)
    offset = (page - 1) * limit
    config = data_manager.get_config()
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)
    try:
        all_physical_files = sorted([f for f in os.listdir(abs_image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))], reverse=True)
        all_faces = data_manager.get_faces()
        filtered_filenames = set()
        if filter_person and filter_person != 'all':
            filtered_filenames = {face['image_file'] for face in all_faces if face.get('name') == filter_person}
        elif filter_status == 'no_faces':
            images_with_people = {face['image_file'] for face in all_faces if face.get('name') and face.get('name') not in ['Ismeretlen', 'arc_nélkül']}
            images_marked_no_face = {face['image_file'] for face in all_faces if face.get('name') == 'arc_nélkül'}
            filtered_filenames = images_marked_no_face - images_with_people
        elif filter_status == 'unknown_faces':
            filtered_filenames = {face['image_file'] for face in all_faces if face.get('name') == 'Ismeretlen'}
        else:
            filtered_filenames = set(all_physical_files)
        final_list = [f for f in all_physical_files if f in filtered_filenames]
        paginated_files = final_list[offset : offset + limit]
        return jsonify({"images": paginated_files, "page": page, "has_next": len(final_list) > offset + limit})
    except FileNotFoundError:
        return jsonify({"images": [], "page": 1, "has_next": False})

@api_bp.route('/image_details/<filename>', methods=['GET'])
def get_image_details(filename):
    all_faces = data_manager.get_faces()
    image_faces = [face for face in all_faces if face.get('image_file') == filename]
    return jsonify(image_faces)

@api_bp.route('/faces/add_manual', methods=['POST'])
def add_manual_face():
    data = request.get_json()
    filename, name, coords_percent = data.get('filename'), data.get('name'), data.get('coords')
    if not all([filename, name, coords_percent]): return jsonify({'status': 'error', 'message': 'Hiányzó adatok.'}), 400
    config = data_manager.get_config()
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    image_path = os.path.join(os.getcwd(), image_folder_name, filename)
    if not os.path.exists(image_path): return jsonify({'status': 'error', 'message': 'A képfájl nem található.'}), 404
    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            left, top, width, height = int(coords_percent['left'] * img_width), int(coords_percent['top'] * img_height), int(coords_percent['width'] * img_width), int(coords_percent['height'] * img_height)
            right, bottom = left + width, top + height
            face_location = [top, right, bottom, left]
            face_image = img.crop((left, top, right, bottom))
            face_count = len(data_manager.get_faces())
            face_filename = f"manual_{os.path.splitext(filename)[0]}_{face_count}.jpg"
            face_filepath_relative = os.path.join('static/faces', face_filename).replace('\\', '/')
            face_filepath_abs = os.path.join(os.getcwd(), face_filepath_relative)
            face_image.save(face_filepath_abs)
        all_faces = data_manager.get_faces()
        new_face_data = {"image_file": filename, "face_location": face_location, "face_path": face_filepath_relative, "name": name}
        all_faces.append(new_face_data)
        data_manager.save_faces(all_faces)
        event_logger.log_event(f"Manuális arc hozzáadva: '{name}' a '{filename}' képen.")
        return jsonify({'status': 'success', 'message': 'Új arc sikeresen mentve.', 'new_face': new_face_data})
    except Exception as e:
        print(f"Hiba a manuális arc mentésekor: {e}")
        return jsonify({'status': 'error', 'message': 'Szerver oldali hiba történt.'}), 500
        
@api_bp.route('/person/update_birthday', methods=['POST'])
def update_person_birthday():
    data = request.get_json()
    name, birthday_str = data.get('name'), data.get('birthday', '')
    if not name: return jsonify({'status': 'error', 'message': 'Hiányzó név.'}), 400
    persons_data = data_manager.get_persons()
    if name in persons_data:
        persons_data[name]['birthday'] = birthday_str.replace('-', '.') if birthday_str else ""
        data_manager.save_persons(persons_data)
        event_logger.log_event(f"'{name}' születésnapja frissítve.")
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
    event_logger.log_event(f"{len(source_names)} személy összevonva '{target_name}' név alá.")
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
    event_logger.log_event(f"{deleted_count} személy törölve: {', '.join(names_to_delete)}.")
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
        event_logger.log_event(f"Arc átnevezve: '{os.path.basename(face_path)}' -> '{new_name}'.")
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
        event_logger.log_event(f"'{person_name}' profilképe beállítva.")
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
        event_logger.log_event(f"Arc törölve: '{os.path.basename(face_path_to_delete)}'.")
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
    event_logger.log_event(f"{len(face_paths)} arc átnevezve '{target_name}' névre.")
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen átnevezve erre: {target_name}'})

@api_bp.route('/faces/delete_batch', methods=['POST'])
def delete_faces_batch():
    face_paths = request.get_json().get('face_paths', [])
    if not face_paths: return jsonify({'status': 'error', 'message': 'Nincs kiválasztott arc.'}), 400
    all_faces = data_manager.get_faces()
    updated_faces = [face for face in all_faces if face.get('face_path') not in face_paths]
    data_manager.save_faces(updated_faces)
    event_logger.log_event(f"{len(face_paths)} arc törölve.")
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen törölve.'})

@api_bp.route('/force_reload', methods=['POST'])
def force_reload_clients():
    try:
        socketio.emit('reload_clients', {'message': 'Manual refresh triggered'})
        event_logger.log_event("Manuális frissítési parancs kiküldve.")
        return jsonify({'status': 'success', 'message': 'Frissítési parancs elküldve.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500