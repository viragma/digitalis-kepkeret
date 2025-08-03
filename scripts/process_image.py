# scripts/process_image.py
import sys
from PIL import Image

def process_image(source_path, target_path):
    """
    Ez a te egyedi képfeldolgozó logikád helye.
    A script beolvas egy képet, átméretezi, elforgatja, majd elmenti a cél útvonalra.
    """
    try:
        with Image.open(source_path) as img:
            # Automatikus elforgatás az EXIF adatok alapján
            # (Ez megoldja a telefonnal készült, oldalt álló képek problémáját)
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif:
                    orientation = exif.get(0x0112)
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)

            # Átméretezés (opcionális, de javasolt a tárhely miatt)
            # A képkeret felbontásához igazítjuk, pl. 1920x1080
            img.thumbnail((1920, 1080))
            
            # Mentés a cél mappába
            img.save(target_path, "JPEG", quality=100, optimize=True)
            print(f"-> Kép sikeresen feldolgozva és mentve ide: {target_path}")

    except Exception as e:
        print(f"!!! Hiba a képfeldolgozás során ({source_path}): {e}")
        # Hiba esetén a scriptnek hibakóddal kell kilépnie
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Használat: python process_image.py <forrás_fájl> <cél_fájl>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    target_file = sys.argv[2]
    process_image(source_file, target_file)