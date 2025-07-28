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

    # A Blueprinteket a funkción belül importáljuk, hogy elkerüljük a körkörös hivatkozásokat
    from routes.main_routes import main_bp
    from routes.admin_routes import admin_bp
    from routes.api_routes import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Itt kötjük össze a kiegészítőket az alkalmazással
    socketio.init_app(app)

    return app

# Az alkalmazást csak akkor hozzuk létre és futtatjuk, ha ezt a fájlt
# közvetlenül indítjuk el, nem pedig importálással.
if __name__ == '__main__':
    app = create_app()
    # Az `allow_unsafe_werkzeug=True` paraméter szükséges lehet egyes rendszereken
    # a `debug=True` stabil működéséhez a Socket.IO-val.
    socketio.run(app, debug=True, host='0.0.0.0', port=5050, allow_unsafe_werkzeug=True)