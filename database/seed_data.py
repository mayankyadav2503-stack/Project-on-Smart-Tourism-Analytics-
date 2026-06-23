import sqlite3
import random
import hashlib
from datetime import datetime, timedelta
from database.schema import get_connection

DESTINATIONS = [
    {"name": "Eiffel Tower", "country": "France", "city": "Paris", "category": "landmark", "lat": 48.8584, "lng": 2.2945, "tags": "iconic,romance,landmark"},
    {"name": "Louvre Museum", "country": "France", "city": "Paris", "category": "museum", "lat": 48.8606, "lng": 2.3376, "tags": "art,museum,culture"},
    {"name": "Tokyo Tower", "country": "Japan", "city": "Tokyo", "category": "landmark", "lat": 35.6586, "lng": 139.7454, "tags": "iconic,view,landmark"},
    {"name": "Senso-ji Temple", "country": "Japan", "city": "Tokyo", "category": "temple", "lat": 35.7148, "lng": 139.7967, "tags": "temple,culture,history"},
    {"name": "Times Square", "country": "USA", "city": "New York", "category": "landmark", "lat": 40.7580, "lng": -73.9855, "tags": "iconic,nightlife,shopping"},
    {"name": "Central Park", "country": "USA", "city": "New York", "category": "park", "lat": 40.7829, "lng": -73.9654, "tags": "park,nature,relaxation"},
    {"name": "Taj Mahal", "country": "India", "city": "Agra", "category": "landmark", "lat": 27.1751, "lng": 78.0421, "tags": "iconic,history,wonder"},
    {"name": "Sydney Opera House", "country": "Australia", "city": "Sydney", "category": "landmark", "lat": -33.8568, "lng": 151.2153, "tags": "iconic,architecture,culture"},
    {"name": "Colosseum", "country": "Italy", "city": "Rome", "category": "landmark", "lat": 41.8902, "lng": 12.4922, "tags": "history,ancient,landmark"},
    {"name": "Great Wall of China", "country": "China", "city": "Beijing", "category": "landmark", "lat": 40.4319, "lng": 116.5704, "tags": "history,wonder,landmark"},
    {"name": "Machu Picchu", "country": "Peru", "city": "Cusco", "category": "landmark", "lat": -13.1631, "lng": -72.5450, "tags": "history,ruins,wonder"},
    {"name": "Grand Canyon", "country": "USA", "city": "Arizona", "category": "nature", "lat": 36.1069, "lng": -112.1129, "tags": "nature,canyon,hiking"},
    {"name": "Santorini", "country": "Greece", "city": "Santorini", "category": "island", "lat": 36.3932, "lng": 25.4615, "tags": "island,romance,beach"},
    {"name": "Dubai Mall", "country": "UAE", "city": "Dubai", "category": "shopping", "lat": 25.1986, "lng": 55.2796, "tags": "shopping,modern,luxury"},
    {"name": "Bali Beach", "country": "Indonesia", "city": "Bali", "category": "beach", "lat": -8.4095, "lng": 115.1889, "tags": "beach,relaxation,nature"},
]

HOTELS = [
    {"dest": 0, "name": "Hotel Eiffel View", "price": 250, "amenities": "wifi,pool,gym,restaurant"},
    {"dest": 0, "name": "Le Parisien Boutique", "price": 180, "amenities": "wifi,breakfast,ac"},
    {"dest": 2, "name": "Tokyo Central Hotel", "price": 200, "amenities": "wifi,onsen,gym,restaurant"},
    {"dest": 2, "name": "Shinjuku Business Inn", "price": 120, "amenities": "wifi,breakfast,laundry"},
    {"dest": 4, "name": "Manhattan Grand", "price": 350, "amenities": "wifi,pool,gym,spa,restaurant"},
    {"dest": 4, "name": "Times Square Hostel", "price": 80, "amenities": "wifi,breakfast,lockers"},
    {"dest": 6, "name": "Taj View Hotel", "price": 150, "amenities": "wifi,pool,restaurant,ac"},
    {"dest": 6, "name": "Agra Heritage Inn", "price": 60, "amenities": "wifi,breakfast,ac"},
    {"dest": 8, "name": "Roman Palace Hotel", "price": 220, "amenities": "wifi,pool,restaurant,ac"},
    {"dest": 8, "name": "Colosseum B&B", "price": 100, "amenities": "wifi,breakfast,ac"},
    {"dest": 12, "name": "Santorini Blue Resort", "price": 400, "amenities": "wifi,pool,spa,restaurant,oceanview"},
    {"dest": 13, "name": "Dubai Luxury Tower", "price": 500, "amenities": "wifi,pool,gym,spa,restaurant,shopping"},
    {"dest": 14, "name": "Bali Beach Resort", "price": 180, "amenities": "wifi,pool,spa,restaurant,beachaccess"},
    {"dest": 1, "name": "Louvre Central Hotel", "price": 300, "amenities": "wifi,ac,restaurant,concierge"},
    {"dest": 10, "name": "Machu Picchu Lodge", "price": 130, "amenities": "wifi,breakfast,guidedtours"},
]

RESTAURANTS = [
    {"dest": 0, "name": "Le Bistrot Parisien", "cuisine": "French", "price": "$$$"},
    {"dest": 0, "name": "Café de la Tour", "cuisine": "French,Cafe", "price": "$$"},
    {"dest": 2, "name": "Sakura Sushi Bar", "cuisine": "Japanese,Sushi", "price": "$$$"},
    {"dest": 2, "name": "Ramen Street Tokyo", "cuisine": "Japanese,Ramen", "price": "$"},
    {"dest": 4, "name": "Broadway Diner", "cuisine": "American", "price": "$$"},
    {"dest": 4, "name": "NYC Pizza Slice", "cuisine": "Italian,American", "price": "$"},
    {"dest": 6, "name": "Mughlai Palace", "cuisine": "Indian,Mughlai", "price": "$$"},
    {"dest": 6, "name": "Agra Street Food Corner", "cuisine": "Indian,Street", "price": "$"},
    {"dest": 8, "name": "Trattoria Romana", "cuisine": "Italian", "price": "$$$"},
    {"dest": 12, "name": "Sunset Taverna", "cuisine": "Greek,Mediterranean", "price": "$$$"},
    {"dest": 13, "name": "Al Habibi Grill", "cuisine": "Arabic,International", "price": "$$$"},
    {"dest": 14, "name": "Bali Bay Cafe", "cuisine": "Indonesian,Seafood", "price": "$$"},
    {"dest": 1, "name": "Musée Café", "cuisine": "French,Cafe", "price": "$$"},
    {"dest": 9, "name": "Beijing Noodle House", "cuisine": "Chinese,Noodles", "price": "$$"},
    {"dest": 11, "name": "Canyon Grill", "cuisine": "American,Grill", "price": "$$"},
]

ACTIVITIES = [
    {"dest": 0, "name": "Eiffel Tower Summit Tour", "duration": 2, "cost": 30, "category": "sightseeing", "lat": 48.8584, "lng": 2.2945},
    {"dest": 1, "name": "Louvre Museum Guided Tour", "duration": 3, "cost": 25, "category": "culture", "lat": 48.8606, "lng": 2.3376},
    {"dest": 2, "name": "Tokyo Night Walking Tour", "duration": 2, "cost": 20, "category": "sightseeing", "lat": 35.6586, "lng": 139.7454},
    {"dest": 3, "name": "Senso-ji Temple Visit", "duration": 1.5, "cost": 0, "category": "culture", "lat": 35.7148, "lng": 139.7967},
    {"dest": 4, "name": "Broadway Show Night", "duration": 3, "cost": 150, "category": "entertainment", "lat": 40.7580, "lng": -73.9855},
    {"dest": 5, "name": "Central Park Bike Ride", "duration": 2, "cost": 15, "category": "outdoor", "lat": 40.7829, "lng": -73.9654},
    {"dest": 6, "name": "Taj Mahal Sunrise Tour", "duration": 3, "cost": 15, "category": "sightseeing", "lat": 27.1751, "lng": 78.0421},
    {"dest": 7, "name": "Opera House Backstage Tour", "duration": 2, "cost": 40, "category": "culture", "lat": -33.8568, "lng": 151.2153},
    {"dest": 8, "name": "Roman Forum Walk", "duration": 2, "cost": 20, "category": "history", "lat": 41.8902, "lng": 12.4922},
    {"dest": 9, "name": "Great Wall Hiking Day", "duration": 5, "cost": 50, "category": "outdoor", "lat": 40.4319, "lng": 116.5704},
    {"dest": 10, "name": "Machu Picchu Guided Trek", "duration": 6, "cost": 100, "category": "adventure", "lat": -13.1631, "lng": -72.5450},
    {"dest": 11, "name": "Grand Canyon Helicopter Tour", "duration": 2, "cost": 200, "category": "adventure", "lat": 36.1069, "lng": -112.1129},
    {"dest": 12, "name": "Santorini Sunset Cruise", "duration": 3, "cost": 80, "category": "entertainment", "lat": 36.3932, "lng": 25.4615},
    {"dest": 13, "name": "Dubai Desert Safari", "duration": 4, "cost": 120, "category": "adventure", "lat": 25.1986, "lng": 55.2796},
    {"dest": 14, "name": "Bali Surfing Lesson", "duration": 3, "cost": 35, "category": "adventure", "lat": -8.4095, "lng": 115.1889},
]

REVIEW_TEMPLATES = [
    (5, "Amazing experience! Highly recommend visiting."),
    (4, "Very good overall. Some minor issues but worth it."),
    (3, "It was okay, nothing special."),
    (5, "Absolutely fantastic! Would visit again."),
    (2, "Disappointing. Expected much more."),
    (4, "Great place with beautiful views."),
    (1, "Terrible experience. Would not recommend."),
    (4, "Nice location but crowded."),
    (5, "Perfect destination for families!"),
    (3, "Average experience, decent value for money."),
]

def seed_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] > 0:
        print("[Seed] Database already seeded")
        conn.close()
        return

    for i in range(20):
        pw = hashlib.sha256(f"pass{i}".encode()).hexdigest()
        cur.execute(
            "INSERT INTO users (username, email, password_hash, preferences, budget_min, budget_max) VALUES (?,?,?,?,?,?)",
            (f"user{i}", f"user{i}@test.com", pw, '{"interests":["travel","food"]}', random.randint(0, 200), random.randint(500, 5000)),
        )

    for d in DESTINATIONS:
        cur.execute(
            "INSERT INTO destinations (name, country, city, category, latitude, longitude, avg_rating, review_count, popularity_score, tags) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (d["name"], d["country"], d["city"], d["category"], d["lat"], d["lng"],
             round(random.uniform(3.5, 5.0), 1), random.randint(50, 500),
             round(random.uniform(1, 100), 1), d["tags"]),
        )

    for h in HOTELS:
        cur.execute(
            "INSERT INTO hotels (destination_id, name, price_per_night, rating, amenities) VALUES (?,?,?,?,?)",
            (h["dest"] + 1, h["name"], h["price"], round(random.uniform(3.0, 5.0), 1), h["amenities"]),
        )

    for r in RESTAURANTS:
        cur.execute(
            "INSERT INTO restaurants (destination_id, name, cuisine, price_range, rating) VALUES (?,?,?,?,?)",
            (r["dest"] + 1, r["name"], r["cuisine"], r["price"], round(random.uniform(3.0, 5.0), 1)),
        )

    for a in ACTIVITIES:
        cur.execute(
            "INSERT INTO activities (destination_id, name, duration_hours, cost, category, rating, latitude, longitude) VALUES (?,?,?,?,?,?,?,?)",
            (a["dest"] + 1, a["name"], a["duration"], a["cost"], a["category"], round(random.uniform(3.0, 5.0), 1), a["lat"], a["lng"]),
        )

    for uid in range(1, 21):
        for did in range(1, 16):
            if random.random() < 0.4:
                rating, text = random.choice(REVIEW_TEMPLATES)
                sentiment = rating / 5.0
                cur.execute(
                    "INSERT INTO reviews (user_id, destination_id, rating, text, sentiment_score) VALUES (?,?,?,?,?)",
                    (uid, did, rating, text, sentiment),
                )
        for hid in range(1, 16):
            if random.random() < 0.3:
                rating, text = random.choice(REVIEW_TEMPLATES)
                cur.execute(
                    "INSERT INTO reviews (user_id, hotel_id, rating, text, sentiment_score) VALUES (?,?,?,?,?)",
                    (uid, hid, rating, text, rating / 5.0),
                )

    for uid in range(1, 21):
        for _ in range(random.randint(3, 10)):
            did = random.randint(1, 15)
            cur.execute(
                "INSERT INTO user_history (user_id, destination_id, action_type) VALUES (?,?,?)",
                (uid, did, random.choice(["view", "bookmark", "search"])),
            )

    today = datetime.now()
    for did in range(1, 16):
        for day_offset in range(-30, 30):
            d = today + timedelta(days=day_offset)
            dow = d.weekday()
            month = d.month
            base = random.uniform(1, 5)
            if dow >= 5:
                base += random.uniform(1, 3)
            if month in [6, 7, 8, 12]:
                base += random.uniform(1, 4)
            cur.execute(
                "INSERT INTO crowd_data (destination_id, date, predicted_crowd_level, actual_crowd_level, day_of_week, month, is_holiday) VALUES (?,?,?,?,?,?,?)",
                (did, d.strftime("%Y-%m-%d"), round(base, 1), round(base + random.uniform(-0.5, 0.5), 1), dow, month, 1 if dow >= 5 else 0),
            )

    currencies = [("USD", "EUR", 0.92), ("USD", "GBP", 0.79), ("USD", "JPY", 149.50), ("USD", "INR", 83.20), ("USD", "CNY", 7.24), ("USD", "AUD", 1.54), ("USD", "BRL", 4.97), ("USD", "AED", 3.67)]
    for base, target, rate in currencies:
        cur.execute("INSERT INTO currency_rates (base_currency, target_currency, rate) VALUES (?,?,?)", (base, target, rate))

    conn.commit()
    conn.close()
    print("[Seed] Database seeded successfully with sample data")

if __name__ == "__main__":
    from database.schema import init_db
    init_db()
    seed_database()
