# services/theme_engine.py

from datetime import date
from . import data_manager

def get_active_theme():
    """
    Meghatározza az aktuálisan aktív témát a prioritási sorrend alapján.
    Prioritás: Születésnap > Ünnepnap > Időjárás (jövőbeli) > Alapértelmezett.
    Visszaad egy szótárat a téma nevével és beállításaival.
    """
    config = data_manager.get_config()
    themes_config = config.get('themes', {})
    
    # 1. Ellenőrizzük, hogy a tematizálás be van-e kapcsolva
    if not themes_config.get('enabled', False):
        return {"name": "none"}

    today = date.today()
    
    # 2. Prioritás: Születésnap
    birthday_person = data_manager.get_todays_birthday_person()
    if birthday_person:
        return {
            "name": "birthday",
            "settings": themes_config.get('birthday', {})
        }
        
    # 3. Prioritás: Karácsony (Dec 24-26)
    if today.month == 12 and today.day in [24, 25, 26]:
        return {
            "name": "christmas",
            "settings": themes_config.get('christmas', {})
        }
        
    # 4. Prioritás: Időjárás (jövőbeli fejlesztés helye)
    # Itt lehetne lekérdezni az időjárást és visszaadni pl. {"name": "rain", ...}
    
    # 5. Alapértelmezett eset: nincs különleges téma
    return {"name": "none"}