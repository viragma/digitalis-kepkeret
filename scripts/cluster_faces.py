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
    
    config = data_manager.get_config()
    clustering_tolerance = config.get('slideshow', {}).get('clustering_tolerance', 0.45)
    print(f"Csoportosítási tolerancia beállítva (az admin felületről): {clustering_tolerance}")

    unclustered_faces = data_manager.get_unclustered_unknown_faces()

    if len(unclustered_faces) < 2:
        print("Nincs elég új, ismeretlen arc a csoportosításhoz.")
        return

    print(f"{len(unclustered_faces)} új arc kerül csoportosításra...")
    
    encodings = [face['encoding'] for face in unclustered_faces]
    face_ids = [face['id'] for face in unclustered_faces]

    clt = DBSCAN(metric="euclidean", n_jobs=-1, eps=clustering_tolerance)
    clt.fit(encodings)

    conn = data_manager.get_db_connection()
    max_cluster_id_row = conn.execute("SELECT MAX(cluster_id) FROM faces").fetchone()
    conn.close()
    next_cluster_id = (max_cluster_id_row[0] or 0) + 1

    label_ids = set(clt.labels_)
    num_clusters = len(label_ids) - (1 if -1 in label_ids else 0)
    print(f"-> {num_clusters} új csoportot találtunk.")

    for label in label_ids:
        if label == -1:
            continue

        cluster_id = int(next_cluster_id + label)
        idxs = np.where(clt.labels_ == label)[0]
        
        print(f"  - Csoport #{cluster_id}: {len(idxs)} arc.")
        
        for i in idxs:
            data_manager.update_face_cluster_id(face_ids[i], cluster_id)
            
    print("--- Csoportosítás befejezve. ---")

if __name__ == '__main__':
    cluster_unknown_faces()