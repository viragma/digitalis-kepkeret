# routes/api/gallery.py
import os
import json
from flask import Blueprint, request, jsonify
from services import data_manager

gallery_api_bp = Blueprint('gallery_api_bp', __name__, url_prefix='/api')

@gallery_api_bp.route('/all_images', methods=['GET'])
def get_all_images():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 30, type=int)
    filter_person = request.args.get('person', None)
    filter_status = request.args.get('status', None)
    offset = (page - 1) * limit

    config = data_manager.get_config()
    image_folder_name = config.get('UPLOAD_FOLDER', 'static/images')
    abs_image_folder_path = os.path.join(os.getcwd(), image_folder_name)

    try:
        all_physical_files = sorted(
            [f for f in os.listdir(abs_image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))],
            reverse=True
        )
        
        conn = data_manager.get_db_connection()
        
        if filter_person and filter_person != 'all':
            images_with_person_rows = conn.execute("""
                SELECT DISTINCT i.filename FROM images i
                JOIN faces f ON f.image_id = i.id
                JOIN persons p ON f.person_id = p.id
                WHERE p.name = ?
            """, (filter_person,)).fetchall()
            filtered_filenames = {row['filename'] for row in images_with_person_rows}
        
        elif filter_status == 'no_faces':
            images_with_faces_rows = conn.execute("SELECT DISTINCT i.filename FROM images i JOIN faces f ON i.id = f.image_id").fetchall()
            images_with_faces = {row['filename'] for row in images_with_faces_rows}
            all_images_set = set(all_physical_files)
            filtered_filenames = all_images_set - images_with_faces

        elif filter_status == 'unknown_faces':
            images_with_unknowns_rows = conn.execute("""
                SELECT DISTINCT i.filename FROM images i
                JOIN faces f ON f.image_id = i.id
                WHERE f.person_id IS NULL
            """).fetchall()
            filtered_filenames = {row['filename'] for row in images_with_unknowns_rows}
        else:
            filtered_filenames = set(all_physical_files)

        conn.close()

        final_list = [f for f in all_physical_files if f in filtered_filenames]
        paginated_files = final_list[offset : offset + limit]
        
        return jsonify({
            "images": paginated_files,
            "page": page,
            "has_next": len(final_list) > offset + limit
        })

    except Exception as e:
        print(f"Hiba az all_images lekérdezésekor: {e}")
        return jsonify({"images": [], "page": 1, "has_next": False})


@gallery_api_bp.route('/image_details/<filename>', methods=['GET'])
def get_image_details(filename):
    conn = data_manager.get_db_connection()
    # JAVÍTÁS: Csak a szükséges, JSON-barát oszlopokat kérdezzük le
    faces_rows = conn.execute("""
        SELECT f.id, f.image_id, f.person_id, f.face_location, f.face_path, f.distance, p.name 
        FROM faces f
        JOIN images i ON f.image_id = i.id
        LEFT JOIN persons p ON f.person_id = p.id
        WHERE i.filename = ?
    """, (filename,)).fetchall()
    conn.close()
    
    faces = []
    for row in faces_rows:
        face_dict = dict(row)
        if face_dict.get('face_location'):
            try:
                face_dict['face_location'] = json.loads(face_dict['face_location'])
            except (json.JSONDecodeError, TypeError):
                face_dict['face_location'] = None
        faces.append(face_dict)
        
    return jsonify(faces)