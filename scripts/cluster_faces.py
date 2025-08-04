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
    A DBSCAN algoritmust használja, ami a sűrűség alapján találja meg a csoportokat.
    """
    print("--- Ismeretlen arcok intelligens csoportosítása indul ---")
    
    conn = data_manager.get_db_connection()
    cursor = conn.cursor()
    
    # 1. Lekérdezzük az összes, még nem csoportosított ismeretlen arcot
    # (A face_encoding-ot a tanításhoz kellene elmenteni, egyelőre a fájlból olvassuk)
    # Ez a rész egy jövőbeli fejlesztés alapja, most a koncepciót építjük meg.
    # A valós implementációhoz a 'detect_faces.py'-nak el kellene mentenie a kódolásokat.
    
    # Ideiglenes megoldás: a meglévő arc-adatokból dolgozunk
    # A valóságban itt egy komplexebb, tanító-adatbázisra épülő rendszer lenne.
    
    print("Ez a funkció egy jövőbeli fejlesztés része, amihez az arclenyomatok adatbázisban való tárolása szükséges.")
    print("A jelenlegi lépésben a vázat építjük meg a későbbi intelligens funkciókhoz.")
    
    # Példa logika, ami a jövőben élesedne:
    # unknown_faces = cursor.execute("SELECT id, encoding FROM faces WHERE person_id IS NULL AND cluster_id IS NULL").fetchall()
    # encodings = [np.frombuffer(face['encoding']) for face in unknown_faces]
    
    # if len(encodings) > 1:
    #     clt = DBSCAN(metric="euclidean", n_jobs=-1, eps=0.4) # eps: a tolerancia
    #     clt.fit(encodings)
        
    #     # Eredmények visszaírása az adatbázisba
    #     # ...
    #     print(f"{len(set(clt.labels_))} új csoportot találtunk.")

    conn.close()
    print("--- Csoportosítás befejezve (szimuláció) ---")

if __name__ == '__main__':
    cluster_unknown_faces()