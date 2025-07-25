# --- admin_routes.py ---
from flask import Flask, render_template, request, redirect, url_for
import os
import json
from PIL import Image

app = Flask(__name__)

FACES_JSON = 'faces.json'
IMAGES_DIR = 'static/images'
KNOWN_DIR = 'known_faces'
CROP_DIR = 'static/cropped'

# Segédfüggvény: ismert nevek lekérdezése
def get_known_people():
    return sorted([d for d in os.listdir(KNOWN_DIR) if os.path.isdir(os.path.join(KNOWN_DIR, d))])

# Segédfüggvény: arc kivágása a képről
def crop_face(image_path, location):
    image = Image.open(image_path)
    top, right, bottom, left = location
    return image.crop((left, top, right, bottom))

# --- Admin felület: képek listája ---
@app.route('/admin')
def admin():
    with open(FACES_JSON, 'r') as f:
        data = json.load(f)

    unrecognized = {
        file: [face for face in faces if face['name'] is None]
        for file, faces in data.items()
        if any(face['name'] is None for face in faces)
    }
    return render_template('admin.html', data=unrecognized, known=get_known_people())

# --- Admin címkézés beküldése ---
@app.route('/admin/label', methods=['POST'])
def label_face():
    file = request.form['file']
    index = int(request.form['index'])
    name = request.form['name']

    # Update faces.json
    with open(FACES_JSON, 'r') as f:
        data = json.load(f)

    data[file][index]['name'] = name

    with open(FACES_JSON, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Create directory if needed
    person_dir = os.path.join(KNOWN_DIR, name)
    os.makedirs(person_dir, exist_ok=True)

    # Save cropped face
    image_path = os.path.join(IMAGES_DIR, file)
    location = data[file][index]['location']
    cropped = crop_face(image_path, location)
    cropped_filename = f"{name}_{len(os.listdir(person_dir))+1}.jpg"
    cropped.save(os.path.join(person_dir, cropped_filename))

    return redirect(url_for('admin'))

# --- Indítás ---
if __name__ == '__main__':
    app.run(debug=True)
