# routes/api/faces.py
import os
import json
from flask import Blueprint, request, jsonify
from services import data_manager, event_logger
from PIL import Image
from .utils import make_web_path # ÚJ IMPORT

faces_api_bp = Blueprint('faces_api_bp', __name__, url_prefix='/api')

@faces_api_bp.route('/faces/unknown', methods=['GET'])
def get_unknown_faces():
    conn = data_manager.get_db_connection()
    unknown_faces_rows = conn.execute("""
        SELECT f.id, f.face_path, i.filename as image_file 
        FROM faces f
        JOIN images i ON f.image_id = i.id
        WHERE f.person_id IS NULL AND f.face_path IS NOT NULL
        ORDER BY f.id DESC
    """).fetchall()
    conn.close()
    
    processed_faces = []
    for row in unknown_faces_rows:
        face_dict = dict(row)
        face_dict['face_path'] = make_web_path(face_dict['face_path'])
        processed_faces.append(face_dict)
        
    return jsonify(processed_faces)

@faces_api_bp.route('/faces/by_person/<name>', methods=['GET'])
def get_faces_by_person(name):
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
        SELECT f.face_path, f.distance 
        FROM faces f
        JOIN images i ON f.image_id = i.id
        WHERE f.person_id = ? AND f.face_path IS NOT NULL
        ORDER BY i.taken_at DESC, f.id DESC
        LIMIT ? OFFSET ?
    """, (person_id, limit, offset)).fetchall()
    conn.close()
    
    processed_faces = []
    for row in faces_rows:
        face_dict = dict(row)
        face_dict['face_path'] = make_web_path(face_dict['face_path'])
        processed_faces.append(face_dict)
        
    return jsonify({"faces": processed_faces, "total": total_faces})

@faces_api_bp.route('/update_face_name', methods=['POST'])
def update_face_name():
    data = request.get_json()
    face_path, new_name = data.get('face_path'), data.get('new_name')
    if not face_path or new_name is None: return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400
    
    db_face_path_pattern = '%' + face_path.strip('/')

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
    cursor.execute('UPDATE faces SET person_id = ?, is_confirmed = 1 WHERE face_path LIKE ?', (new_person_id, db_face_path_pattern))
    conn.commit()
    conn.close()
    event_logger.log_event(f"Arc átnevezve: '{os.path.basename(face_path)}' -> '{new_name}'.")
    return jsonify({'status': 'success', 'message': f'Arc frissítve: {new_name}'})

@faces_api_bp.route('/faces/reassign_batch', methods=['POST'])
def reassign_faces_batch():
    data = request.get_json()
    face_paths, target_name = data.get('face_paths', []), data.get('target_name')
    if not face_paths or not target_name: return jsonify({'status': 'error', 'message': 'Hiányzó adatok.'}), 400
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    target_person_row = cursor.execute('SELECT id FROM persons WHERE name = ?', (target_name,)).fetchone()
    if not target_person_row:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Cél személy nem található'}), 404
    target_person_id = target_person_row['id']
    
    db_face_paths = ['%' + p.strip('/') for p in face_paths]
    query_parts = ['face_path LIKE ?' for _ in db_face_paths]
    query = f"UPDATE faces SET person_id = ?, is_confirmed = 1 WHERE {' OR '.join(query_parts)}"
    params = [target_person_id] + db_face_paths
    
    cursor.execute(query, params)
    conn.commit()
    conn.close()
    
    event_logger.log_event(f"{len(face_paths)} arc átnevezve '{target_name}' névre.")
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen átnevezve erre: {target_name}'})

@faces_api_bp.route('/faces/delete_batch', methods=['POST'])
def delete_faces_batch():
    face_paths = request.get_json().get('face_paths', [])
    if not face_paths: return jsonify({'status': 'error', 'message': 'Nincs kiválasztott arc.'}), 400
        
    db_face_paths = ['%' + p.strip('/') for p in face_paths]
    full_paths_to_delete = []

    conn = data_manager.get_db_connection()
    cursor = conn.cursor()

    query_parts = ['face_path LIKE ?' for _ in db_face_paths]
    rows = cursor.execute(f"SELECT face_path FROM faces WHERE {' OR '.join(query_parts)}", db_face_paths).fetchall()
    for row in rows:
        if row['face_path']:
            full_paths_to_delete.append(os.path.join(os.getcwd(), row['face_path'].lstrip('/\\')))
            
    query = f"DELETE FROM faces WHERE {' OR '.join(query_parts)}"
    cursor.execute(query, db_face_paths)
    conn.commit()
    conn.close()
    
    for path in full_paths_to_delete:
        try:
            os.remove(path)
        except OSError as e:
            print(f"Hiba a face képfájl törlésekor: {e}")
            
    event_logger.log_event(f"{len(face_paths)} arc törölve.")
    return jsonify({'status': 'success', 'message': f'{len(face_paths)} arc sikeresen törölve.'})