import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')
IMAGE_FOLDER = 'static/images'
image_list = []


def load_images():
    global image_list
    try:
        if not os.path.exists(IMAGE_FOLDER):
            os.makedirs(IMAGE_FOLDER)
        image_list = sorted([
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ])
    except Exception as e:
        print("❌ Hiba a képek betöltésekor:", e)
        image_list = []


class ImageFolderHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.lower().endswith(IMAGE_EXTENSIONS):
            print(f"🆕 Új kép érkezett: {event.src_path}")
            load_images()

            # WebSocket emit (ha van socketio)
            from flask import current_app
            if hasattr(current_app, 'socketio'):
                filename = os.path.basename(event.src_path)
                current_app.socketio.emit_new_image(filename)


def start_watcher():
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    load_images()

    observer = Observer()
    event_handler = ImageFolderHandler()
    observer.schedule(event_handler, IMAGE_FOLDER, recursive=False)
    observer.start()

    def watch():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    threading.Thread(target=watch, daemon=True).start()


def get_image_list():
    if not image_list:
        load_images()
    return image_list
