import sqlite3
from config import DB_PATH

def search_places(query, category=None, limit=20):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    q = f"%{query}%"
    if category:
        cur.execute("""
            SELECT d.*, 'destination' as place_type FROM destinations d
            WHERE (d.name LIKE ? OR d.city LIKE ? OR d.country LIKE ?) AND d.category=?
            LIMIT ?
        """, (q, q, q, category, limit))
    else:
        cur.execute("""
            SELECT d.*, 'destination' as place_type FROM destinations d
            WHERE d.name LIKE ? OR d.city LIKE ? OR d.country LIKE ?
            LIMIT ?
        """, (q, q, q, limit))

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_nearby_places(lat, lng, radius_km=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT *, 'destination' as place_type,
               (6371 * acos(cos(radians(?)) * cos(radians(latitude)) *
               cos(radians(longitude) - radians(?)) + sin(radians(?)) *
               sin(radians(latitude)))) AS distance
        FROM destinations
        HAVING distance < ?
        ORDER BY distance
        LIMIT 20
    """, (lat, lng, lat, radius_km))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]
