# scripts/process_inbox.py
import os
import shutil
import subprocess
import sys

# A projekt gyökérkönyvtárának meghatározása
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

# Konfigurációs adatok
INBOX_DIR = "/home/viragma/frame-sync/originals" # A te rclone célmappád
IMAGE_DIR = os.path.join(PROJECT_ROOT, 'static', 'images')
PROCESSING_SCRIPT = os.path.join(PROJECT_ROOT, 'scripts', 'process_image.py')
DETECTION_SCRIPT = os.path.join(PROJECT_ROOT, 'scripts', 'detect_faces.py')
PYTHON_EXECUTABLE = os.path.join(PROJECT_ROOT, 'venv', 'bin', 'python3')

def process_new_images():
    print("--- Beérkezett képek feldolgozása indul ---")
    if not os.path.isdir(INBOX_DIR):
        print(f"HIBA: A '{INBOX_DIR}' mappa nem létezik.")
        return

    new_files_processed = 0
    for filename in os.listdir(INBOX_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            source_path = os.path.join(INBOX_DIR, filename)
            target_path = os.path.join(IMAGE_DIR, filename)
            
            print(f"Új fájl észlelve: {filename}")
            
            try:
                subprocess.run([PYTHON_EXECUTABLE, PROCESSING_SCRIPT, source_path, target_path], check=True)
                os.remove(source_path)
                print(f"-> Eredeti fájl törölve: {source_path}")
                new_files_processed += 1
            except subprocess.CalledProcessError as e:
                print(f"!!! HIBA a '{filename}' feldolgozása közben, a fájl a helyén marad: {e}")
            except Exception as e:
                print(f"!!! Váratlan hiba: {e}")

    if new_files_processed > 0:
        print(f"\n{new_files_processed} új kép feldolgozva. Arcfelismerés indítása...")
        try:
            subprocess.run([PYTHON_EXECUTABLE, DETECTION_SCRIPT], check=True)
            print("-> Arcfelismerés sikeresen lefutott.")
        except subprocess.CalledProcessError as e:
            print(f"!!! HIBA az arcfelismerés futtatása közben: {e}")
    else:
        print("Nincs új kép a feldolgozandó mappában.")

if __name__ == '__main__':
    process_new_images()