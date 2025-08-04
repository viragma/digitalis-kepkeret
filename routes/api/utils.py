# routes/api/utils.py
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STATIC_FOLDER = os.path.join(PROJECT_ROOT, 'static')

def make_web_path(full_path):
    """
    Biztonságosan és megbízhatóan átalakít egy teljes szerver-oldali útvonalat 
    egy web-elérhető útvonallá, ami a '/static/' mappával kezdődik.
    """
    if not isinstance(full_path, str):
        return None
    
    # Biztosítjuk, hogy a fájlútvonal abszolút legyen és a projekt mappáján belülre mutasson
    abs_path = os.path.abspath(full_path)
    if not abs_path.startswith(STATIC_FOLDER):
        return None # Ha a fájl a static mappán kívül van, nem adjuk vissza

    # Létrehozzuk a relatív útvonalat a 'static' mappához képest
    relative_path = os.path.relpath(abs_path, STATIC_FOLDER)
    
    # Visszaadjuk a helyes web-útvonalat, platformfüggetlen '/' jelekkel
    return ('/static/' + relative_path).replace('\\', '/')