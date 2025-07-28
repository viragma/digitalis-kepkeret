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
            # Az OpenWeatherMap fő kategóriáit kezeljük
            # Pl. a "Mist", "Fog", "Haze" mind "Atmosphere"-ként jön
            if weather_themes_settings.get(current_weather, {}).get('enabled', True):
                 return { "name": current_weather.lower(), "settings": {} }
    
    # 4. Alapértelmezett eset: nincs különleges téma
    return {"name": "none"}