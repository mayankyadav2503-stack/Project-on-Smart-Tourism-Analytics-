import sqlite3
import numpy as np
from config import DB_PATH, MODELS_DIR
import os

class RecommendationService:
    def __init__(self):
        self.cf_model = None
        self._load_cf()

    def _load_cf(self):
        path = os.path.join(MODELS_DIR, "collab_filter.pkl")
        if os.path.exists(path):
            from models.collaborative_filtering import CollabFilterRecommender
            try:
                self.cf_model = CollabFilterRecommender.load()
            except Exception as e:
                print(f"[Rec] Failed to load CF model: {e}")

    def get_personalized(self, user_id, n=10):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT preferences, budget_min, budget_max FROM users WHERE id=?", (user_id,))
        user = cur.fetchone()
        if not user:
            conn.close()
            return self.get_popular(n)

        import json
        prefs = json.loads(user["preferences"]) if isinstance(user["preferences"], str) else user["preferences"]
        budget_min = user["budget_min"]
        budget_max = user["budget_max"]

        cur.execute("SELECT destination_id FROM user_history WHERE user_id=? ORDER BY timestamp DESC LIMIT 20", (user_id,))
        history_ids = [r["destination_id"] for r in cur.fetchall()]

        cur.execute("SELECT id, name, city, country, category, avg_rating, review_count, popularity_score, tags FROM destinations WHERE id NOT IN (0) LIMIT 50")
        all_dests = cur.fetchall()

        scores = []
        for d in all_dests:
            score = 0
            tags = d["tags"].lower() if d["tags"] else ""
            if d["id"] in history_ids:
                score -= 5
            if prefs.get("interests"):
                for interest in prefs["interests"]:
                    if interest.lower() in tags or interest.lower() in d["category"].lower():
                        score += 3
            score += d["avg_rating"] * 0.5
            score += np.log1p(d["review_count"]) * 0.3
            score += d["popularity_score"] * 0.02

            if self.cf_model:
                try:
                    cf_score = self.cf_model.predict(user_id, d["id"])
                    score += cf_score * 0.8
                except:
                    pass
            scores.append((dict(d), round(score, 2)))

        scores.sort(key=lambda x: -x[1])
        conn.close()
        return scores[:n]

    def get_popular(self, n=10):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT *, (avg_rating * 0.4 + (popularity_score/100) * 0.3 + CASE WHEN review_count > 0 THEN log10(review_count)*0.3 ELSE 0 END) as composite_score FROM destinations ORDER BY composite_score DESC LIMIT ?", (n,))
        rows = cur.fetchall()
        conn.close()
        return [(dict(r), round(r["composite_score"], 2)) for r in rows]

    def get_similar_destinations(self, dest_id, n=5):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT category, tags FROM destinations WHERE id=?", (dest_id,))
        dest = cur.fetchone()
        if not dest:
            conn.close()
            return []

        category = dest["category"]
        tags = set(dest["tags"].split(",")) if dest["tags"] else set()

        cur.execute("SELECT * FROM destinations WHERE id != ?", (dest_id,))
        all_dests = cur.fetchall()

        scored = []
        for d in all_dests:
            score = 0
            if d["category"] == category:
                score += 5
            d_tags = set(d["tags"].split(",")) if d["tags"] else set()
            overlap = len(tags & d_tags)
            score += overlap * 2
            score += d["avg_rating"] * 0.5
            scored.append((dict(d), score))

        scored.sort(key=lambda x: -x[1])
        conn.close()
        return scored[:n]

    def get_hotel_recommendations(self, destination_id, budget_max=None):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if budget_max:
            cur.execute("SELECT * FROM hotels WHERE destination_id=? AND price_per_night <= ? ORDER BY rating DESC", (destination_id, budget_max))
        else:
            cur.execute("SELECT * FROM hotels WHERE destination_id=? ORDER BY rating DESC", (destination_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_restaurant_recommendations(self, destination_id, cuisine=None):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if cuisine:
            cur.execute("SELECT * FROM restaurants WHERE destination_id=? AND cuisine LIKE ? ORDER BY rating DESC", (destination_id, f"%{cuisine}%"))
        else:
            cur.execute("SELECT * FROM restaurants WHERE destination_id=? ORDER BY rating DESC", (destination_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_activity_recommendations(self, destination_id, category=None):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if category:
            cur.execute("SELECT * FROM activities WHERE destination_id=? AND category=? ORDER BY rating DESC", (destination_id, category))
        else:
            cur.execute("SELECT * FROM activities WHERE destination_id=? ORDER BY rating DESC", (destination_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
