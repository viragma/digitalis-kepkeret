# services/theme_engine.py

from datetime import date, datetime, timedelta
from dateutil.easter import easter
from astral import LocationInfo
from astral.sun import sun
from . import data_manager
from . import weather_service

def get_active_theme():
    """
    Meghatározza az aktuálisan aktív témát a prioritási sorrend alapján.
    """
    config = data_manager.get_config()
    themes_config = config.get('themes', {})
    
    # 0. Prioritás: Manuális teszt felülbírálás
    debug_theme = config.get('debug_theme', 'none')
    if debug_theme != 'none':
        theme_name = debug_theme
        settings = themes_config.get(theme_name, {})
        if theme_name in ['rain', 'snow', 'clear', 'clouds', 'atmosphere', 'thunderstorm']:
             settings = {}
        return {"name": theme_name, "settings": settings}

    if not themes_config.get('enabled', False):
        return {"name": "none"}

    now = datetime.now()
    today = now.date()
    
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
        current_weather = weather_service.get_current_weather() # Pl. "Rain", "Snow", "Thunderstorm"
        if current_weather and weather_themes_settings.get(current_weather, {}).get('enabled', True):
            theme_name = current_weather.lower()
            if theme_name == "drizzle": theme_name = "rain"
            if theme_name in ["mist", "smoke", "haze", "dust", "fog", "sand", "ash", "squall", "tornado"]:
                theme_name = "atmosphere"
            return { "name": theme_name, "settings": {} }
    
    # 4. Prioritás: Napszak
    try:
        city = LocationInfo("Kecskemét", "Hungary", "Europe/Budapest", 46.906, 19.691)
        s = sun(city.observer, date=today, tzinfo=city.timezone)
        
        if now < s['sunrise']: return {"name": "night"}
        if now < s['sunrise'] + timedelta(hours=2): return {"name": "sunrise"}
        if now < s['sunset'] - timedelta(hours=2): return {"name": "daytime"}
        if now < s['sunset']: return {"name": "sunset"}
        return {"name": "night"}
        
    except Exception as e:
        print(f"Hiba a napszak meghatározásakor: {e}")

    return {"name": "none"}