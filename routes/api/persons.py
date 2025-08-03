# routes/api/persons.py
from flask import Blueprint, request, jsonify
from services import data_manager, event_logger
import os, shutil

persons_api_bp = Blueprint('persons_api_bp', __name__, url_prefix='/api')

@persons_api_bp.route('/persons', methods=['GET'])
def get_persons_api():
    """ Visszaadja az összes személy nevét egy egyszerű listában. """
    conn = data_manager.get_db_connection()
    persons_rows = conn.execute('SELECT name FROM persons WHERE is_active = 1 ORDER BY name').fetchall()
    conn.close()
    return jsonify([row['name'] for row in persons_rows])

@persons_api_bp.route('/persons/gallery_data', methods=['GET'])
def get_persons_gallery_data():
    """ Visszaadja a személyek listáját a galéria nézethez, képek számával. """
    conn = data_manager.get_db_connection()
    persons_rows = conn.execute("""
        SELECT p.name, p.birthday, p.profile_image, COUNT(f.id) as face_count
        FROM persons p
        LEFT JOIN faces f ON p.id = f.person_id
        WHERE p.is_active = 1
        GROUP BY p.id
        ORDER BY p.name
    """).fetchall()
    conn.close()
    
    gallery_data = []
    for row in persons_rows:
        gallery_data.append({
            "name": row['name'],
            "data": {
                "birthday": row['birthday'],
                "profile_image": row['profile_image']
            },
            "face_count": row['face_count']
        })
    return jsonify(gallery_data)

@persons_api_bp.route('/persons/set_profile_image', methods=['POST'])
def set_profile_image():
    data = request.get_json()
    person_name, face_path = data.get('name'), data.get('face_path')
    if not person_name or not face_path: return jsonify({'status': 'error', 'message': 'Hiányzó adatok'}), 400
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE persons SET profile_face_id = (SELECT id FROM faces WHERE face_path = ?) WHERE name = ?', (face_path, person_name))
    conn.commit()
    conn.close()
    
    event_logger.log_event(f"'{person_name}' profilképe beállítva.")
    return jsonify({'status': 'success', 'message': 'Profilkép beállítva!'})

@persons_api_bp.route('/person/update_birthday', methods=['POST'])
def update_person_birthday():
    data = request.get_json()
    name, birthday_str = data.get('name'), data.get('birthday', '')
    if not name: return jsonify({'status': 'error', 'message': 'Hiányzó név.'}), 400
    
    birthday_to_store = birthday_str.replace('-', '.') if birthday_str else ""
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE persons SET birthday = ? WHERE name = ?', (birthday_to_store, name))
    conn.commit()
    conn.close()
    
    event_logger.log_event(f"'{name}' születésnapja frissítve.")
    return jsonify({'status': 'success', 'message': f'{name} születésnapja frissítve.'})

@persons_api_bp.route('/persons/reassign_batch', methods=['POST'])
def reassign_persons_batch():
    data = request.get_json()
    source_names, target_name = data.get('source_names', []), data.get('target_name')
    if not source_names or not target_name: return jsonify({'status': 'error', 'message': 'Hiányzó forrás- vagy célnevek.'}), 400
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    target_person_row = cursor.execute('SELECT id FROM persons WHERE name = ?', (target_name,)).fetchone()
    if not target_person_row:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Cél személy nem található'}), 404
    target_person_id = target_person_row['id']
    
    # Arcok átnevezése
    placeholders = ', '.join('?' for _ in source_names)
    cursor.execute(f'UPDATE faces SET person_id = ? WHERE person_id IN (SELECT id FROM persons WHERE name IN ({placeholders}))', [target_person_id] + source_names)

    # Forrás személyek törlése
    cursor.execute(f'DELETE FROM persons WHERE name IN ({placeholders})', source_names)
    conn.commit()
    conn.close()

    for name in source_names:
        person_dir = os.path.join('data', 'known_faces', name)
        if os.path.isdir(person_dir): shutil.rmtree(person_dir)
        
    event_logger.log_event(f"{len(source_names)} személy összevonva '{target_name}' név alá.")
    return jsonify({'status': 'success', 'message': f'{len(source_names)} személy sikeresen átnevezve erre: {target_name}'})

@persons_api_bp.route('/persons/delete_batch', methods=['POST'])
def delete_persons_batch():
    names_to_delete = request.get_json().get('names', [])
    if not names_to_delete: return jsonify({'status': 'error', 'message': 'Nincs kiválasztott személy.'}), 400

    conn = data_manager.get_db_connection()
    cursor = conn.cursor()

    placeholders = ', '.join('?' for _ in names_to_delete)
    # Az érintett arcokat visszaállítjuk "Ismeretlen"-re (person_id = NULL)
    cursor.execute(f'UPDATE faces SET person_id = NULL WHERE person_id IN (SELECT id FROM persons WHERE name IN ({placeholders}))', names_to_delete)
    # Töröljük a személyeket
    cursor.execute(f'DELETE FROM persons WHERE name IN ({placeholders})', names_to_delete)
    conn.commit()
    conn.close()
    
    for name in names_to_delete:
        person_dir = os.path.join('data', 'known_faces', name)
        if os.path.isdir(person_dir): shutil.rmtree(person_dir)

    event_logger.log_event(f"{len(names_to_delete)} személy törölve: {', '.join(names_to_delete)}.")
    return jsonify({'status': 'success', 'message': f'{len(names_to_delete)} személy sikeresen törölve.'})