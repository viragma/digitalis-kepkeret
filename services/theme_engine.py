# services/theme_engine.py

from datetime import date
from dateutil.easter import easter # ÚJ IMPORT
from . import data_manager

def get_active_theme():
    """
    Meghatározza az aktuálisan aktív témát a prioritási sorrend alapján.
    """
    config = data_manager.get_config()
    themes_config = config.get('themes', {})
    
    if not themes_config.get('enabled', False):
        return {"name": "none"}

    today = date.today()
    
    # 1. Prioritás: Születésnap
    birthday_person = data_manager.get_todays_birthday_person()
    if birthday_person:
        return { "name": "birthday", "settings": themes_config.get('birthday', {}) }
        
    # 2. Prioritás: Fix Ünnepek
    # Karácsony
    if today.month == 12 and today.day in [24, 25, 26]:
        return { "name": "christmas", "settings": themes_config.get('christmas', {}) }
    
    # Szilveszter
    if today.month == 12 and today.day == 31:
        return { "name": "new_year_eve", "settings": themes_config.get('new_year_eve', {}) }
        
    # Húsvét
    easter_date = easter(today.year)
    if today == easter_date or today == easter_date + timedelta(days=1): # Húsvétvasárnap és -hétfő
        return { "name": "easter", "settings": themes_config.get('easter', {}) }
    
    # 3. Prioritás: Időjárás (jövőbeli)
    
    return {"name": "none"}