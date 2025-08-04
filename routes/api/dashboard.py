# routes/api/dashboard.py
import os
import shutil
import subprocess
import sys
import psutil
import pickle
from flask import Blueprint, jsonify
from services import data_manager, event_logger
from extensions import socketio
from datetime import datetime

dashboard_api_bp = Blueprint('dashboard_api_bp', __name__, url_prefix='/api')

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

@dashboard_api_bp.route('/event_log', methods=['GET'])
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

@dashboard_api_bp.route('/dashboard_stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = data_manager.get_db_connection()
        total_images = conn.execute('SELECT COUNT(id) FROM images').fetchone()[0]
        known_persons = conn.execute('SELECT COUNT(id) FROM persons WHERE is_active = 1').fetchone()[0]
        recognized_faces = conn.execute('SELECT COUNT(id) FROM faces WHERE person_id IS NOT NULL').fetchone()[0]
        unknown_faces = conn.execute('SELECT COUNT(id) FROM faces WHERE person_id IS NULL').fetchone()[0]
        
        latest_images_rows = conn.execute('SELECT filename FROM images ORDER BY id DESC LIMIT 5').fetchall()
        
        known_faces_dir = os.path.join(os.getcwd(), 'data', 'known_faces')
        total_training_images = sum([len(files) for r, d, files in os.walk(known_faces_dir)])
        
        encodings_cache_path = os.path.join(os.getcwd(), 'data', 'known_encodings.pkl')
        last_training_time = None
        if os.path.exists(encodings_cache_path):
            last_training_time = datetime.fromtimestamp(os.path.getmtime(encodings_cache_path)).strftime('%Y-%m-%d %H:%M:%S')

        confidence_rows = conn.execute("""
            SELECT p.name, AVG(f.distance) as avg_distance, COUNT(f.id) as face_count
            FROM persons p
            JOIN faces f ON p.id = f.person_id
            WHERE p.is_active = 1 AND f.distance IS NOT NULL AND f.is_manual = 0
            GROUP BY p.name
        """).fetchall()
        
        conn.close()

        confidence_data = []
        for row in confidence_rows:
            confidence = max(0, round((1 - (row['avg_distance'] / 0.7)) * 100))
            confidence_data.append({
                "name": row['name'],
                "confidence": confidence,
                "face_count": row['face_count']
            })

        latest_images = [row['filename'] for row in latest_images_rows]

        return jsonify({
            "total_images": total_images,
            "known_persons": known_persons,
            "recognized_faces": recognized_faces,
            "unknown_faces": unknown_faces,
            "latest_images": latest_images,
            "model_stats": {
                "total_training_images": total_training_images,
                "last_training_time": last_training_time,
                "confidence_data": sorted(confidence_data, key=lambda x: x['confidence'], reverse=True)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_api_bp.route('/system_stats', methods=['GET'])
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

@dashboard_api_bp.route('/run_face_detection', methods=['POST'])
def run_face_detection():
    try:
        python_executable = sys.executable
        script_path = os.path.join(os.getcwd(), 'scripts', 'detect_faces.py')
        if not os.path.exists(script_path): return jsonify({"status": "error", "message": "A detect_faces.py script nem található."}), 404
        subprocess.Popen([python_executable, script_path])
        event_logger.log_event("Arcfelismerési folyamat elindítva a Műszerfalról.")
        return jsonify({"status": "success", "message": "Arcfelismerés elindítva a háttérben."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
        
@dashboard_api_bp.route('/force_reload', methods=['POST'])
def force_reload_clients():
    try:
        socketio.emit('reload_clients', {'message': 'Manual refresh triggered'})
        event_logger.log_event("Manuális frissítési parancs kiküldve.")
        return jsonify({'status': "success", 'message': 'Frissítési parancs elküldve.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500