import sqlite3
import os
from config import DB_PATH

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        preferences TEXT DEFAULT '{}',
        budget_min REAL DEFAULT 0,
        budget_max REAL DEFAULT 10000,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        city TEXT NOT NULL,
        description TEXT,
        category TEXT DEFAULT 'general',
        latitude REAL,
        longitude REAL,
        avg_rating REAL DEFAULT 0,
        review_count INTEGER DEFAULT 0,
        popularity_score REAL DEFAULT 0,
        tags TEXT DEFAULT '',
        image_url TEXT DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        price_per_night REAL,
        rating REAL DEFAULT 0,
        latitude REAL,
        longitude REAL,
        amenities TEXT DEFAULT '',
        FOREIGN KEY (destination_id) REFERENCES destinations(id)
    );

    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        cuisine TEXT DEFAULT '',
        price_range TEXT DEFAULT '$$',
        rating REAL DEFAULT 0,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY (destination_id) REFERENCES destinations(id)
    );

    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        duration_hours REAL DEFAULT 2,
        cost REAL DEFAULT 0,
        category TEXT DEFAULT 'sightseeing',
        rating REAL DEFAULT 0,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY (destination_id) REFERENCES destinations(id)
    );

    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        destination_id INTEGER DEFAULT 0,
        hotel_id INTEGER DEFAULT 0,
        restaurant_id INTEGER DEFAULT 0,
        activity_id INTEGER DEFAULT 0,
        rating INTEGER DEFAULT 5,
        text TEXT DEFAULT '',
        sentiment_score REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS user_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        destination_id INTEGER,
        hotel_id INTEGER,
        restaurant_id INTEGER,
        activity_id INTEGER,
        action_type TEXT DEFAULT 'view',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        destination_id INTEGER,
        hotel_id INTEGER,
        activity_id INTEGER,
        booking_date DATE,
        cost REAL,
        status TEXT DEFAULT 'confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS itineraries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT DEFAULT 'My Trip',
        destination_id INTEGER,
        start_date DATE,
        end_date DATE,
        budget REAL DEFAULT 0,
        total_cost REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS itinerary_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        itinerary_id INTEGER NOT NULL,
        item_type TEXT NOT NULL,
        item_id INTEGER NOT NULL,
        day_number INTEGER DEFAULT 1,
        time_slot TEXT DEFAULT 'morning',
        notes TEXT DEFAULT '',
        FOREIGN KEY (itinerary_id) REFERENCES itineraries(id)
    );

    CREATE TABLE IF NOT EXISTS crowd_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination_id INTEGER NOT NULL,
        date DATE NOT NULL,
        predicted_crowd_level REAL DEFAULT 0,
        actual_crowd_level REAL DEFAULT 0,
        day_of_week INTEGER,
        month INTEGER,
        is_holiday INTEGER DEFAULT 0,
        FOREIGN KEY (destination_id) REFERENCES destinations(id)
    );

    CREATE TABLE IF NOT EXISTS currency_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_currency TEXT DEFAULT 'USD',
        target_currency TEXT NOT NULL,
        rate REAL NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS weather_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        data TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Initialized database at {DB_PATH}")
