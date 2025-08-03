# routes/api/faces.py
import os
import json
from flask import Blueprint, request, jsonify
from services import data_manager, event_logger
from PIL import Image

faces_api_bp = Blueprint('faces_api_bp', __name__, url_prefix='/api')

@faces_api_bp.route('/faces/unknown', methods=['GET'])
def get_unknown_faces():
    """ Visszaadja az összes ismeretlen arcot az adatbázisból. """
    conn = data_manager.get_db_connection()
    unknown_faces_rows = conn.execute("""
        SELECT f.id, f.face_path, i.filename as image_file 
        FROM faces f
        JOIN images i ON f.image_id = i.id
        WHERE f.person_id IS NULL
        ORDER BY f.id DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(row) for row in unknown_faces_rows])

@faces_api_bp.route('/faces/by_person/<name>', methods=['GET'])
def get_faces_by_person(name):
    """ Visszaadja egy adott személyhez tartozó arcokat, lapozható formában. """
    page = request.args.get('page', 1, type=int)
    limit = 30
    offset = (page - 1) * limit
    
    conn = data_manager.get_db_connection()
    person = conn.execute('SELECT id FROM persons WHERE name = ?', (name,)).fetchone()
    if not person:
        conn.close()
        return jsonify({"faces": [], "total": 0})
        
    person_id = person['id']
    
    total_faces = conn.execute('SELECT COUNT(id) FROM faces WHERE person_id = ?', (person_id,)).fetchone()[0]
    
    faces_rows = conn.execute("""
        SELECT f.face_path 
        FROM faces f
        JOIN images i ON f.image_id = i.id
        WHERE f.person_id = ?
        ORDER BY i.taken_at DESC, f.id DESC
        LIMIT ? OFFSET ?
    """, (person_id, limit, offset)).fetchall()
    
    conn.close()
    
    return jsonify({
        "faces": [dict(row) for row in faces_rows],
        "total": total_faces
    })
    
@faces_api_bp.route('/faces/add_manual', methods=['POST'])
def add_manual_face():
    """ Manuálisan hozzáad egy új arcot egy képhez. """
    data = request.get_json()
    filename, name, coords_percent = data.get('filename'), data.get('name'), data.get('coords')
    if not all([filename, name, coords_percent]): 
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok.'}), 400
    
    config = data_manager.get_config()
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    image_path = os.path.join(os.getcwd(), image_folder_name, filename)

    if not os.path.exists(image_path): 
        return jsonify({'status': 'error', 'message': 'A képfájl nem található.'}), 404

    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
            left = int(coords_percent['left'] * img_width)
            top = int(coords_percent['top'] * img_height)
            width = int(coords_percent['width'] * img_width)
            height = int(coords_percent['height'] * img_height)
            right, bottom = left + width, top + height
            face_location = [top, right, bottom, left]

            face_image = img.crop((left, top, right, bottom))
            
            conn = data_manager.get_db_connection()
            face_count = conn.execute('SELECT COUNT(id) FROM faces').fetchone()[0]
            conn.close()

            face_filename = f"manual_{os.path.splitext(filename)[0]}_{face_count}.jpg"
            face_filepath_relative = os.path.join('static/faces', face_filename).replace('\\', '/')
            face_filepath_abs = os.path.join(os.getcwd(), face_filepath_relative)
            face_image.save(face_filepath_abs)

        conn = data_manager.get_db_connection()
        cursor = conn.cursor()
        
        image_row = cursor.execute('SELECT id FROM images WHERE filename = ?', (filename,)).fetchone()
        image_id = image_row['id'] if image_row else None
        
        person_row = cursor.execute('SELECT id FROM persons WHERE name = ?', (name,)).fetchone()
        person_id = person_row['id'] if person_row else None

        if image_id and person_id:
            cursor.execute("""
                INSERT INTO faces (image_id, person_id, face_location, face_path, is_manual, is_confirmed)
                VALUES (?, ?, ?, ?, 1, 1)
            """, (image_id, person_id, json.dumps(face_location), face_filepath_relative))
            conn.commit()
            
            new_face_id = cursor.lastrowid
            new_face_data = dict(cursor.execute('SELECT * FROM faces WHERE id = ?', (new_face_id,)).fetchone())

            conn.close()
            event_logger.log_event(f"Manuális arc hozzáadva: '{name}' a '{filename}' képen.")
            return jsonify({'status': 'success', 'message': 'Új arc sikeresen mentve.', 'new_face': new_face_data})
        else:
            conn.close()
            return jsonify({'status': 'error', 'message': 'A kép vagy a személy nem található az adatbázisban.'}), 404

    except Exception as e:
        print(f"Hiba a manuális arc mentésekor: {e}")
        return jsonify({'status': 'error', 'message': 'Szerver oldali hiba történt.'}), 500

@faces_api_bp.route('/update_face_name', methods=['POST'])
def update_face_name():
    """ Egyetlen arcot átnevez (vagy Ismeretlenre állít). """
    data = request.get_json()
    face_path, new_name = data.get('face_path'), data.get('new_name')
    if not face_path or new_name is None: 
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    new_person_id = None
    if new_name != 'Ismeretlen':
        person_row = cursor.execute('SELECT id FROM persons WHERE name = ?', (new_name,)).fetchone()
        if person_row:
            new_person_id = person_row['id']
        else:
            conn.close()
            return jsonify({'status': 'error', 'message': f'A(z) "{new_name}" személy nem található.'}), 404

    cursor.execute('UPDATE faces SET person_id = ?, is_confirmed = 1 WHERE face_path = ?', (new_person_id, face_path))
    conn.commit()
    conn.close()
    
    event_logger.log_event(f"Arc átnevezve: '{os.path.basename(face_path)}' -> '{new_name}'.")
    return jsonify({'status': 'success', 'message': f'Arc frissítve: {new_name}'})

@faces_api_bp.route('/faces/delete', methods=['POST'])
def delete_face():
    """ Töröl egy arcot az adatbázisból és a fájlrendszerből is. """
    data = request.get_json()
    face_path_to_delete = data.get('face_path')
    if not face_path_to_delete: 
        return jsonify({'status': 'error', 'message': 'Hiányzó face_path'}), 400

    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM faces WHERE face_path = ?', (face_path_to_delete,))
    conn.commit()
    
    if cursor.rowcount > 0:
        try:
            os.remove(os.path.join(os.getcwd(), face_path_to_delete))
        except OSError as e:
            print(f"Hiba a face képfájl törlésekor: {e}")
            
        conn.close()
        event_logger.log_event(f"Arc törölve: '{os.path.basename(face_path_to_delete)}'.")
        return jsonify({'status': 'success', 'message': 'Arc sikeresen törölve.'})
    else:
        conn.close()
        return jsonify({'status': 'error', 'message': 'A törlendő arc nem található'}), 404

@faces_api_bp.route('/faces/reassign_batch', methods=['POST'])
def reassign_faces_batch():
    """ Több arcot átnevez egy cél személyre. """
    data = request.get_json()
    face_paths, target_name = data.get('face_paths', []), data.get('target_name')
    if not face_paths or not target_name: 
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok.'}), 400
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    target_person_row = cursor.execute('SELECT id FROM persons WHERE name = ?', (target_name,)).fetchone()
    if not target_person_row:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Cél személy nem található'}), 404
    target_person_id = target_person_row['id']
    
    # A '?' placeholder-ek számát dinamikusan generáljuk
    placeholders = ', '.join('?' for _ in face_paths)
    query = f'UPDATE faces SET person_id = ?, is_confirmed = 1 WHERE face_path IN ({placeholders})'
    
    params = [target_person_id] + face_paths
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    event_logger.log_event(f"{len(face_paths)} arc átnevezve '{target_name}' névre.")
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen átnevezve erre: {target_name}'})

@faces_api_bp.route('/faces/delete_batch', methods=['POST'])
def delete_faces_batch():
    """ Több arcot töröl egyszerre. """
    face_paths = request.get_json().get('face_paths', [])
    if not face_paths: 
        return jsonify({'status': 'error', 'message': 'Nincs kiválasztott arc.'}), 400
        
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    placeholders = ', '.join('?' for _ in face_paths)
    query = f'DELETE FROM faces WHERE face_path IN ({placeholders})'
    cursor.execute(query, face_paths)
    conn.commit()
    conn.close()
    
    for path in face_paths:
        try:
            os.remove(os.path.join(os.getcwd(), path))
        except OSError as e:
            print(f"Hiba a face képfájl törlésekor: {e}")
            
    event_logger.log_event(f"{len(face_paths)} arc törölve.")
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen törölve.'})