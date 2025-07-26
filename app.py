# app.py

from flask import Flask
import os
import json

# A blueprint objektumokat importáljuk
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp
# A többi route fájlt is ide kell majd importálni, ha blueprintekké alakulnak

def create_app():
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

    # Blueprintek regisztrálása
    # A main_bp-nek NINCS előtagja, így az övé lesz a főoldal ('/')
    app.register_blueprint(main_bp)
    # Az admin_bp-nek '/admin' az előtagja, így az ő útvonalai /admin/... alatt lesznek
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)