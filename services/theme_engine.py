# services/theme_engine.py

from datetime import date, timedelta
from dateutil.easter import easter
from . import data_manager
from . import weather_service

def get_active_theme():
    """
    Meghatározza az aktuálisan aktív témát a prioritási sorrend alapján.
    """
    config = data_manager.get_config()
    themes_config = config.get('themes', {})
    
    # --- JAVÍTÁS: Először a manuális teszt beállítást ellenőrizzük ---
    debug_theme = config.get('debug_theme', 'none')
    if debug_theme != 'none':
        # Ha van teszt téma beállítva, minden mást felülbírálunk
        # Az 'if' feltétel biztosítja, hogy a settings létezzen
        if themes_config.get(debug_theme):
             return { "name": debug_theme, "settings": themes_config.get(debug_theme, {}) }
        else: # Kezeli az időjárás témákat is
             return { "name": debug_theme, "settings": {} }


    # Ha nincs teszt, a normál logikával megyünk tovább
    if not themes_config.get('enabled', False):
        return {"name": "none"}

    today = date.today()
    
    # 1. Prioritás: Születésnap
    birthday_person = data_manager.get_todays_birthday_person()
    if birthday_person:
        return { "name": "birthday", "settings": themes_config.get('birthday', {}) }
        
    # 2. Prioritás: Fix Ünnepek
    if today.month == 12 and today.day in [24, 25, 26]:
        return { "name": "christmas", "settings": themes_config.get('christmas', {}) }
    
    if today.month == 12 and today.day == 31:
        return { "name": "new_year_eve", "settings": themes_config.get('new_year_eve', {}) }
        
    easter_date = easter(today.year)
    if today == easter_date or today == easter_date + timedelta(days=1):
        return { "name": "easter", "settings": themes_config.get('easter', {}) }
    
    # 3. Prioritás: Időjárás
    weather_themes_settings = themes_config.get('weather', {})
    if weather_themes_settings.get('enabled', True):
        current_weather = weather_service.get_current_weather()
        if current_weather:
            theme_name = current_weather.lower()
            if weather_themes_settings.get(current_weather, {}).get('enabled', True):
                 return { "name": theme_name, "settings": {} }
    
    # 4. Alapértelmezett eset
    return {"name": "none"}