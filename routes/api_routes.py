# routes/api_routes.py - JAVÍTOTT VERZIÓ

from flask import request, jsonify
from app import app  # Feltételezzük, hogy a fő app objektum itt érhető el

# --- VÁLTOZÁS ---
from services import data_manager

@app.route('/api/faces', methods=['GET'])
def get_all_faces():
    """ Visszaadja az összes arc adatait JSON formátumban. """
    faces_data = data_manager.get_faces()
    return jsonify(faces_data)


@app.route('/api/update_face_name', methods=['POST'])
def update_face_name():
    """
    Frissíti egy adott archoz tartozó nevet.
    A frontendtől egy JSON objektumot vár, ami tartalmazza
    a 'face_path'-t és a 'new_name'-et.
    """
    data = request.get_json()
    face_path = data.get('face_path')
    new_name = data.get('new_name')

    if not face_path or new_name is None:
        return jsonify({'status': 'error', 'message': 'Hiányzó adatok: face_path vagy new_name'}), 400

    # --- VÁLTOZÁS ---
    # A data_manager segítségével olvassuk be és írjuk felül az adatokat
    faces_data = data_manager.get_faces()
    
    face_found = False
    for face in faces_data:
        # A face_path alapján keressük meg a módosítandó arcot
        if face.get('face_path') == face_path:
            face['name'] = new_name
            face_found = True
            break
    
    if face_found:
        # Biztonságos mentés a data_manager-rel
        data_manager.save_faces(faces_data)
        return jsonify({'status': 'success', 'message': f'Arc frissítve: {new_name}'})
    else:
        return jsonify({'status': 'error', 'message': 'A megadott arc nem található'}), 404

# Ide jöhetnek a jövőben a további API végpontok...