# app.py - JAVÍTVA BLUEPRINTEK HASZNÁLATÁHOZ

from flask import Flask
import os
import json

# --- VÁLTOZÁS ---
# A blueprint objektumokat importáljuk, nem a teljes fájlt
from routes.main_routes import main_bp
from routes.admin_routes import admin_bp
# A többi routes fájlt is hasonlóan kell majd átalakítani és importálni

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Konfiguráció betöltése
    try:
        with open('config.json', 'r') as f:
            app.config.update(json.load(f))
    except FileNotFoundError:
        print("HIBA: config.json nem található!")
        app.config.update(ADMIN_PASSWORD="admin")

    # --- VÁLTOZÁS ---
    # Regisztráljuk a blueprinteket az alkalmazáson
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app

app = create_app()

# --- VÁLTOZÁS ---
# A régi "from routes import *" sorokat töröljük, mert már a create_app-ban regisztrálunk
# from routes.main_routes import *
# from routes.admin_routes import *
# ...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)