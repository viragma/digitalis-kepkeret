# scripts/cluster_faces.py
import os
import sys
from sklearn.cluster import DBSCAN
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from services import data_manager

def cluster_unknown_faces():
    """
    Végzi az ismeretlen arcok intelligens csoportosítását (clustering).
    """
    print("--- Ismeretlen arcok intelligens csoportosítása indul ---")
    
    # 1. Lekérdezzük az összes, még nem csoportosított ismeretlen arcot és a kódolásukat
    unclustered_faces = data_manager.get_unclustered_unknown_faces()

    if len(unclustered_faces) < 2:
        print("Nincs elég új, ismeretlen arc a csoportosításhoz.")
        return

    print(f"{len(unclustered_faces)} új arc kerül csoportosításra...")
    
    # Kinyerjük a kódolásokat és az ID-kat a további feldolgozáshoz
    encodings = [face['encoding'] for face in unclustered_faces]
    face_ids = [face['id'] for face in unclustered_faces]

    # 2. A DBSCAN algoritmus futtatása a kódolásokon
    # Az 'eps' a tolerancia: mekkora "távolság" számít egy csoportnak.
    # Ezt később a beállításokból is olvashatjuk.
    clt = DBSCAN(metric="euclidean", n_jobs=-1, eps=0.4)
    clt.fit(encodings)

    # 3. Az eredmények feldolgozása és visszaírása az adatbázisba
    # A '-1' címke a "zaj", vagyis azokat az arcokat jelöli, amik egyik csoporthoz sem illenek.
    
    # Először a legnagyobb meglévő cluster_id-t kérdezzük le, hogy onnan folytassuk a számozást
    conn = data_manager.get_db_connection()
    max_cluster_id_row = conn.execute("SELECT MAX(cluster_id) FROM faces").fetchone()
    conn.close()
    next_cluster_id = (max_cluster_id_row[0] or 0) + 1

    label_ids = set(clt.labels_)
    num_clusters = len(label_ids) - (1 if -1 in label_ids else 0)
    print(f"-> {num_clusters} új csoportot találtunk.")

    for label in label_ids:
        if label == -1: # A zajt egyelőre nem jelöljük
            continue

        # Az új, egyedi cluster ID
        cluster_id = next_cluster_id + label
        
        # Megkeressük az összes arcot, ami ehhez a címkéhez tartozik
        idxs = np.where(clt.labels_ == label)[0]
        
        print(f"  - Csoport #{cluster_id}: {len(idxs)} arc.")
        
        # Frissítjük az adatbázisban a cluster_id-t minden archoz
        for i in idxs:
            data_manager.update_face_cluster_id(face_ids[i], cluster_id)
            
    print("--- Csoportosítás befejezve. ---")

if __name__ == '__main__':
    cluster_unknown_faces()