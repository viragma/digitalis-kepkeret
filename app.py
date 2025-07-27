# app.py

from flask import Flask
import os
import json
from extensions import socketio # VÁLTOZÁS: Innen importálunk

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    config_path = os.path.join('data', 'config.json')
    try:
        with open(config_path, 'r') as f:
            app.config.update(json.load(f))
    except FileNotFoundError:
        print(f"HIBA: {config_path} nem található!")
        app.config.update(ADMIN_PASSWORD="admin")

    # Blueprintek regisztrálása
    from routes.main_routes import main_bp
    from routes.admin_routes import admin_bp
    from routes.api_routes import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # A SocketIO inicializálása az app-pal
    socketio.init_app(app)
    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5050)