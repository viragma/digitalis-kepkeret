from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
import os
import json
from config import ADMIN_PASSWORD

main_bp = Blueprint('main', __name__)

IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')
IMAGE_FOLDER = 'static/images'
CONFIG_FILE = 'data/config.json'


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin.admin_page'))
        return render_template('login.html', error='Hibás jelszó')
    return render_template('login.html')


@main_bp.route('/config')
def get_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/imagelist')
def imagelist():
    try:
        files = sorted([
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ])
        return jsonify(files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
