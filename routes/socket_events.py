from flask_socketio import SocketIO
import os

# Itt nem Blueprint van, hanem eseményregisztráló függvény
def register_socket_events(socketio: SocketIO):

    @socketio.on('connect')
    def handle_connect():
        print('🔌 WebSocket kapcsolat létrejött')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('❌ WebSocket kapcsolat megszűnt')

    # Backendről hívható események
    # Például új kép érkezett → frontend frissítheti
    def emit_new_image(image_name: str):
        socketio.emit('new_image', {'image': image_name})

    def emit_config_update():
        socketio.emit('config_updated')

    def emit_faces_updated():
        socketio.emit('faces_updated')

    # Ezeket elérhetővé tesszük más moduloknak
    socketio.emit_new_image = emit_new_image
    socketio.emit_config_update = emit_config_update
    socketio.emit_faces_updated = emit_faces_updated
