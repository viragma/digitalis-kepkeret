# scripts/find_duplicates.py
import os
from PIL import Image
import imagehash
from collections import defaultdict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
IMAGE_DIR = os.path.join(PROJECT_ROOT, 'static', 'images')

def find_visual_duplicates():
    """
    Vizuálisan hasonló képeket keres a mappában perceptuális hash segítségével,
    és felajánlja a duplikátumok törlését.
    """
    print("Vizuális duplikátumok keresése indul (ez eltarthat egy ideig)...")
    
    hashes = {}
    # 1. Lépés: Hash generálása minden képhez
    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            file_path = os.path.join(IMAGE_DIR, filename)
            try:
                with Image.open(file_path) as img:
                    img_hash = imagehash.phash(img)
                    hashes[file_path] = img_hash
            except Exception as e:
                print(f"Hiba a '{filename}' feldolgozása közben: {e}")

    # 2. Lépés: Hasonló képek csoportosítása
    duplicates = []
    processed_files = set()
    
    filenames = list(hashes.keys())
    for i in range(len(filenames)):
        if filenames[i] in processed_files:
            continue

        current_file = filenames[i]
        similar_group = [current_file]
        processed_files.add(current_file)

        for j in range(i + 1, len(filenames)):
            if filenames[j] in processed_files:
                continue
            
            other_file = filenames[j]
            
            # A 5-ös küszöb egy jó kiindulási pont a nagyon hasonló képekhez.
            if hashes[current_file] - hashes[other_file] <= 5:
                similar_group.append(other_file)
                processed_files.add(other_file)
        
        if len(similar_group) > 1:
            duplicates.append(similar_group)

    # 3. Lépés: Eredmények megjelenítése és törlési script generálása
    print("\n--- Eredmények ---")
    if not duplicates:
        print("Nem található vizuálisan hasonló duplikált kép.")
    else:
        files_to_delete = []
        for group in duplicates:
            # A csoporton belül a legjobb minőségű (legnagyobb felbontású) képet tartjuk meg
            group.sort(key=lambda x: Image.open(x).size[0] * Image.open(x).size[1], reverse=True)
            original = group[0]
            dups_in_group = group[1:]
            
            print(f"\nHasonló képek csoportja ({len(group)} db):")
            print(f"  [MEGTARTVA - Legjobb minőség] {os.path.basename(original)}")
            for dup_path in dups_in_group:
                print(f"  [TÖRÖLENDŐ] {os.path.basename(dup_path)}")
                files_to_delete.append(dup_path)

        if files_to_delete:
            print(f"\nÖsszesen {len(files_to_delete)} törlésre javasolt fájl.")
            generate_script = input("Szeretnéd létrehozni a 'delete_duplicates.sh' törlési parancsfájlt? (igen/nem): ")
            if generate_script.lower() == 'igen':
                script_path = os.path.join(PROJECT_ROOT, 'delete_duplicates.sh')
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write("#!/bin/bash\n# Futtatás előtt győződj meg a tartalmáról!\n\n")
                    for file_path in files_to_delete:
                        f.write(f'rm "{file_path}"\n')
                print(f"\nA '{script_path}' fájl sikeresen létrehozva.")
                print("Futtatáshoz add ki a 'bash delete_duplicates.sh' parancsot a terminálban.")
            else:
                print("Nem lett létrehozva törlési script.")

    print("\nKeresés befejezve.")

if __name__ == '__main__':
    find_visual_duplicates()