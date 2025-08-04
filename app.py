# app.py

from flask import Flask
import os
import json
from extensions import socketio

def create_app():
    """
    Ez az "Application Factory". Ennek a feladata, hogy létrehozza
    és konfigurálja a Flask alkalmazásunkat.
    """
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Konfiguráció betöltése
    config_path = os.path.join('data', 'config.json')
    try:
        with open(config_path, 'r') as f:
            app.config.update(json.load(f))
    except FileNotFoundError:
        print(f"HIBA: {config_path} nem található!")
        app.config.update(ADMIN_PASSWORD="admin")

    # A Blueprinteket a funkción belül importáljuk
    from routes.main_routes import main_bp
    from routes.admin_routes import admin_bp
    from routes.api_routes import api_bp
    from routes.api.dashboard import dashboard_api_bp
    from routes.api.gallery import gallery_api_bp
    from routes.api.faces import faces_api_bp
    from routes.api.persons import persons_api_bp
    from routes.api.slideshow import slideshow_api_bp
    from routes.api.trainer import trainer_api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_api_bp)
    app.register_blueprint(gallery_api_bp)
    app.register_blueprint(faces_api_bp)
    app.register_blueprint(persons_api_bp)
    app.register_blueprint(slideshow_api_bp)
    app.register_blueprint(trainer_api_bp)
    app.register_blueprint(api_bp)

    # Kiegészítők inicializálása
    socketio.init_app(app)

    return app

if __name__ == '__main__':
    app = create_app()
    # JAVÍTÁS: Hozzáadjuk az 'allow_unsafe_werkzeug=True' paramétert
    socketio.run(app, debug=True, host='100.109.70.114', port=5010, use_reloader=True, reloader_type='stat', allow_unsafe_werkzeug=True)