from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from config import SECRET_KEY
from routes import register_routes
from routes.socket_events import register_socket_events

app = Flask(__name__)
app.secret_key = SECRET_KEY

# WebSocket + CORS
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# SocketIO hozzáférhető legyen máshol is
app.socketio = socketio

# Route-ok és WebSocket események regisztrálása
register_routes(app, socketio)
register_socket_events(socketio)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5050)
