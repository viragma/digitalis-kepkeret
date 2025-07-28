# services/weather_service.py

import requests
from . import data_manager

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_current_weather():
    """
    Lekérdezi az aktuális időjárást az OpenWeatherMap API-ról.
    Visszaad egy egyszerűsített időjárás-kódot (pl. 'Rain', 'Snow', 'Clear').
    """
    config = data_manager.get_config()
    api_key = config.get("WEATHER_API_KEY")
    city = config.get("WEATHER_CITY", "Kecskemét,HU")

    if not api_key or api_key == "c5e81b9586100bf64f941c234ee685b1":
        print("!!! HIBA: OpenWeatherMap API kulcs nincs beállítva a config.json-ban.")
        return None

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "hu"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status() # Hiba dobása, ha a kérés sikertelen (pl. 401, 404)
        data = response.json()
        
        # Az API által visszaadott fő kategóriát használjuk
        weather_main = data.get("weather", [{}])[0].get("main")
        return weather_main # Pl. "Clouds", "Rain", "Snow", "Clear", "Thunderstorm"

    except requests.exceptions.RequestException as e:
        print(f"!!! HIBA az időjárás API lekérdezésekor: {e}")
        return None