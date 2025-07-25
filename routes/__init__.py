from .main_routes import main_bp
from .admin_routes import admin_bp
from .api_routes import api_bp
from .socket_events import register_socket_events

def register_routes(app, socketio):
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    register_socket_events(socketio)
