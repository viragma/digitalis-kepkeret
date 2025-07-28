# services/weather_service.py

import requests
from . import data_manager

BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

def get_current_weather():
    """
    Lekérdezi az aktuális időjárást az OpenWeatherMap API-ról.
    """
    config = data_manager.get_config()
    api_key = config.get("WEATHER_API_KEY")
    city = config.get("WEATHER_CITY", "Budapest,HU")

    # Eltávolítottuk a hibás ellenőrzést, mert a 401-es hiba kezelése már elég.
    if not api_key or "IDE_MASOLD" in api_key:
        print("!!! FIGYELMEZTETÉS: OpenWeatherMap API kulcs nincs (vagy hibásan van) beállítva a config.json-ban.")
        return None

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "hu"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status() # Ez a sor kezeli a 401-es (hibás kulcs) és egyéb hibákat.
        data = response.json()
        
        weather_main = data.get("weather", [{}])[0].get("main")
        print(f"--- Időjárás Adat Sikeresen Lekérve: {weather_main} ---")
        return weather_main

    except requests.exceptions.RequestException as e:
        print(f"!!! HIBA az időjárás API lekérdezésekor: {e}")
        return None