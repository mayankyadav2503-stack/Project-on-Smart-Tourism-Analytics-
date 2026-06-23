import json
import sqlite3
import random
from datetime import datetime
from config import DB_PATH

WEATHER_PROFILES = {
    "paris":     {"temp": 16, "desc": "Partly cloudy",      "icon": "02d", "humid": 65, "wind": 12},
    "tokyo":     {"temp": 22, "desc": "Clear sky",          "icon": "01d", "humid": 60, "wind": 8},
    "london":    {"temp": 12, "desc": "Light rain",         "icon": "09d", "humid": 78, "wind": 15},
    "new york":  {"temp": 20, "desc": "Sunny",              "icon": "01d", "humid": 55, "wind": 10},
    "rome":      {"temp": 24, "desc": "Clear sky",          "icon": "01d", "humid": 50, "wind": 6},
    "sydney":    {"temp": 26, "desc": "Sunny",              "icon": "01d", "humid": 52, "wind": 14},
    "dubai":     {"temp": 35, "desc": "Hot and sunny",      "icon": "01d", "humid": 25, "wind": 5},
    "bangkok":   {"temp": 32, "desc": "Humid and cloudy",   "icon": "03d", "humid": 82, "wind": 7},
    "bali":      {"temp": 29, "desc": "Partly cloudy",      "icon": "02d", "humid": 78, "wind": 9},
    "istanbul":  {"temp": 21, "desc": "Clear sky",          "icon": "01d", "humid": 58, "wind": 11},
    "barcelona": {"temp": 23, "desc": "Sunny",              "icon": "01d", "humid": 54, "wind": 8},
    "amsterdam": {"temp": 14, "desc": "Cloudy",             "icon": "04d", "humid": 72, "wind": 13},
    "delhi":     {"temp": 34, "desc": "Hazy sunshine",      "icon": "50d", "humid": 30, "wind": 6},
    "cairo":     {"temp": 33, "desc": "Clear sky",          "icon": "01d", "humid": 22, "wind": 10},
    "beijing":   {"temp": 18, "desc": "Mostly sunny",       "icon": "02d", "humid": 40, "wind": 9},
}

def get_weather(city):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT data, updated_at FROM weather_cache WHERE city=? ORDER BY updated_at DESC LIMIT 1", (city.lower(),))
    row = cur.fetchone()
    if row:
        cached = json.loads(row[0])
        ts = datetime.fromisoformat(row[1])
        if (datetime.now() - ts).total_seconds() < 1800:
            conn.close()
            return cached
    conn.close()

    key = city.lower().strip()
    profile = WEATHER_PROFILES.get(key, {"temp": 22, "desc": "Clear sky", "icon": "01d", "humid": 60, "wind": 5})
    jitter = random.randint(-3, 3)
    result = {
        "city": city,
        "temperature": profile["temp"] + jitter,
        "feels_like": profile["temp"] + jitter - 2,
        "humidity": profile["humid"],
        "description": profile["desc"],
        "icon": profile["icon"],
        "wind_speed": profile["wind"],
        "country": "",
    }

    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO weather_cache (city, data, updated_at) VALUES (?,?,?)",
                 (city.lower(), json.dumps(result), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return result
