# routes/main_routes.py

from flask import Blueprint, render_template

from services import data_manager

main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)

@main_bp.route('/')
def index():
    persons_data = data_manager.get_persons()
    faces_data = data_manager.get_faces()
    

    person_counts = {person: 0 for person in persons_data}
    total_faces = len(faces_data)
    known_faces = 0
    unknown_faces = 0

    for face in faces_data:
        if face.get('name') and face['name'] != 'Ismeretlen':
            if face['name'] in person_counts:
                person_counts[face['name']] += 1
            known_faces += 1
        else:
            unknown_faces += 1
    
    return render_template('index.html', 
                           person_counts=person_counts, 
                           total_faces=total_faces, 
                           known_faces=known_faces, 
                           unknown_faces=unknown_faces,
                           persons_data=persons_data)