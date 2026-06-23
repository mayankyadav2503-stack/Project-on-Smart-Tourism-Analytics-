import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "tourism.db")
MODELS_DIR = os.path.join(BASE_DIR, "models_saved")
DATA_DIR = os.path.join(BASE_DIR, "data")

SECRET_KEY = os.environ.get("SECRET_KEY", "stap-dev-key-2026")

SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"

WEATHER_CACHE_TTL = 1800
CURRENCY_CACHE_TTL = 3600
