# services/theme_engine.py

from datetime import date, datetime, timedelta
from dateutil.easter import easter
from astral import LocationInfo
from astral.sun import sun
from . import data_manager
from . import weather_service

def get_active_themes():
    """
    Meghatározza az aktuálisan aktív háttér- és esemény-témát.
    Visszaad egy szótárat, ami mindkét réteg állapotát tartalmazza.
    """
    config = data_manager.get_config()
    themes_config = config.get('themes', {})
    
    # Alapértelmezett kimenet
    active_themes = {
        "ambient_theme": "none",
        "event_theme": {"name": "none", "settings": {}}
    }

    # Ha a tematizálás ki van kapcsolva, üres témákat adunk vissza
    if not themes_config.get('enabled', False):
        return active_themes

    now = datetime.now()
    today = now.date()
    
    # --- ESEMÉNY TÉMA MEGHATÁROZÁSA (magasabb prioritású) ---
    event_theme_name = "none"
    event_theme_settings = {}

    # 1. Születésnap
    birthday_person = data_manager.get_todays_birthday_person()
    if birthday_person:
        event_theme_name = "birthday"
        event_theme_settings = themes_config.get('birthday', {})
    
    # 2. Fix Ünnepek (csak akkor, ha nincs szülinap)
    elif today.month == 12 and today.day in [24, 25, 26]:
        event_theme_name = "christmas"
        event_theme_settings = themes_config.get('christmas', {})
    elif today.month == 12 and today.day == 31:
        event_theme_name = "new_year_eve"
        event_theme_settings = themes_config.get('new_year_eve', {})
    elif today == easter(today.year) or today == easter(today.year) + timedelta(days=1):
        event_theme_name = "easter"
        event_theme_settings = themes_config.get('easter', {})
    
    # 3. Időjárás (csak akkor, ha nincs ünnep vagy szülinap)
    else:
        weather_themes_settings = themes_config.get('weather', {})
        if weather_themes_settings.get('enabled', True):
            current_weather = weather_service.get_current_weather()
            if current_weather and weather_themes_settings.get(current_weather, {}).get('enabled', True):
                theme_name = current_weather.lower()
                if theme_name == "drizzle": theme_name = "rain"
                if theme_name in ["mist", "smoke", "haze", "dust", "fog", "sand", "ash", "squall", "tornado"]:
                    theme_name = "atmosphere"
                event_theme_name = theme_name

    active_themes["event_theme"] = {"name": event_theme_name, "settings": event_theme_settings}


    # --- HÁTTÉR HANGULAT (NAPSZAK) MEGHATÁROZÁSA (mindig fut) ---
    day_cycle_settings = themes_config.get('day_cycle', {})
    if day_cycle_settings.get('enabled', True):
        try:
            city = LocationInfo("Kecskemét", "Hungary", "Europe/Budapest", 46.906, 19.691)
            s = sun(city.observer, date=today, tzinfo=city.timezone)
            now_aware = now.astimezone(city.tzinfo)

            if day_cycle_settings.get('night', {}).get('enabled', True) and (now_aware < s['sunrise'] or now_aware > s['sunset']):
                active_themes["ambient_theme"] = "night"
            elif day_cycle_settings.get('sunrise', {}).get('enabled', True) and s['sunrise'] <= now_aware < s['sunrise'] + timedelta(hours=2):
                active_themes["ambient_theme"] = "sunrise"
            elif day_cycle_settings.get('sunset', {}).get('enabled', True) and s['sunset'] - timedelta(hours=2) <= now_aware < s['sunset']:
                 active_themes["ambient_theme"] = "sunset"
            else:
                active_themes["ambient_theme"] = "daytime"
            
        except Exception as e:
            print(f"Hiba a napszak meghatározásakor: {e}")
            active_themes["ambient_theme"] = "daytime"

    # Manuális teszt felülbírálás (mindent felülír)
    debug_theme = config.get('debug_theme', 'none')
    if debug_theme != 'none':
        if debug_theme in ['sunrise', 'daytime', 'sunset', 'night']:
            active_themes["ambient_theme"] = debug_theme
            active_themes["event_theme"] = {"name": "none", "settings": {}} # Töröljük az eseményt, ha napszakot tesztelünk
        else:
            active_themes["event_theme"] = {"name": debug_theme, "settings": themes_config.get(debug_theme, {})}

    return active_themes