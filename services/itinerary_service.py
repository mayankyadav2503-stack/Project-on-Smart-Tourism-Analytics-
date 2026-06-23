import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH
from services.recommendation_service import RecommendationService

class ItineraryService:
    def _get_budget_suggestions(self, destination_id, budget):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        recs = RecommendationService()
        hotels = recs.get_hotel_recommendations(destination_id, budget * 0.5 if budget else None)
        activities = recs.get_activity_recommendations(destination_id)
        restaurants = recs.get_restaurant_recommendations(destination_id)

        conn.close()
        return hotels[:3], restaurants[:3], activities[:5]

    def generate_itinerary(self, user_id, destination_id, start_date, end_date, budget=None):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM destinations WHERE id=?", (destination_id,))
        row = cur.fetchone()
        dest = dict(row) if row else None
        if not dest:
            conn.close()
            return None

        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        num_days = (end_date - start_date).days + 1

        if not budget:
            cur.execute("SELECT budget_max FROM users WHERE id=?", (user_id,))
            u = cur.fetchone()
            budget = u["budget_max"] if u else 2000

        hotels, restaurants, activities = self._get_budget_suggestions(destination_id, budget)

        hotel_cost = (hotels[0]["price_per_night"] * num_days) if hotels else 0
        activity_cost = sum(a["cost"] for a in activities)
        total_estimated = hotel_cost + activity_cost

        cur.execute(
            "INSERT INTO itineraries (user_id, name, destination_id, start_date, end_date, budget, total_cost) VALUES (?,?,?,?,?,?,?)",
            (user_id, f"Trip to {dest['name']}", destination_id, start_date.strftime("%Y-%m-%d"),
             end_date.strftime("%Y-%m-%d"), budget, total_estimated),
        )
        itinerary_id = cur.lastrowid

        day_items = {"morning": [], "afternoon": [], "evening": []}
        for day in range(num_days):
            current_date = start_date + timedelta(days=day)

            if day < len(activities):
                act = activities[day]
                cur.execute(
                    "INSERT INTO itinerary_items (itinerary_id, item_type, item_id, day_number, time_slot) VALUES (?,?,?,?,?)",
                    (itinerary_id, "activity", act["id"], day + 1, "morning"),
                )
                day_items["morning"].append(act["name"])

            if day < len(restaurants):
                rest = restaurants[day]
                cur.execute(
                    "INSERT INTO itinerary_items (itinerary_id, item_type, item_id, day_number, time_slot) VALUES (?,?,?,?,?)",
                    (itinerary_id, "restaurant", rest["id"], day + 1, "afternoon"),
                )
                day_items["afternoon"].append(rest["name"])

        if hotels:
            cur.execute(
                "INSERT INTO itinerary_items (itinerary_id, item_type, item_id, day_number, time_slot, notes) VALUES (?,?,?,?,?,?)",
                (itinerary_id, "hotel", hotels[0]["id"], 1, "evening", f"Staying at {hotels[0]['name']}"),
            )

        conn.commit()

        result = {
            "itinerary_id": itinerary_id,
            "destination": dest["name"],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_budget": budget,
            "estimated_cost": total_estimated,
            "hotel": hotels[0] if hotels else None,
            "activities": activities,
            "restaurants": restaurants,
            "daily_plan": [{"day": i + 1, "date": (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
                            "morning": day_items["morning"][i] if i < len(day_items["morning"]) else "Free time",
                            "afternoon": day_items["afternoon"][i] if i < len(day_items["afternoon"]) else "Lunch break",
                            "evening": f"Stay at {hotels[0]['name']}" if hotels else "Free evening"}
                           for i in range(num_days)],
        }
        conn.close()
        return result

    def get_user_itineraries(self, user_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT i.*, d.name as destination_name, d.city, d.country
            FROM itineraries i
            JOIN destinations d ON i.destination_id = d.id
            WHERE i.user_id=?
            ORDER BY i.created_at DESC
        """, (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_budget_analysis(self, user_id):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT d.name as destination, d.country, d.city,
                   COUNT(b.id) as visit_count, SUM(b.cost) as total_spent
            FROM bookings b
            JOIN destinations d ON b.destination_id = d.id
            WHERE b.user_id=?
            GROUP BY b.destination_id
        """, (user_id,))
        bookings_data = [dict(r) for r in cur.fetchall()]

        cur.execute("""
            SELECT d.category, ROUND(AVG(h.price_per_night), 2) as avg_hotel_cost,
                   ROUND(AVG(a.cost), 2) as avg_activity_cost
            FROM bookings b
            JOIN destinations d ON b.destination_id = d.id
            LEFT JOIN hotels h ON h.destination_id = d.id
            LEFT JOIN activities a ON a.destination_id = d.id
            WHERE b.user_id=?
            GROUP BY d.category
        """, (user_id,))
        category_costs = [dict(r) for r in cur.fetchall()]

        cur.execute("SELECT SUM(cost) as total, COUNT(*) as trips FROM bookings WHERE user_id=?", (user_id,))
        summary = dict(cur.fetchone())

        conn.close()
        return {
            "bookings": bookings_data,
            "category_costs": category_costs,
            "summary": {"total_spent": summary.get("total", 0) or 0, "total_trips": summary.get("trips", 0) or 0},
        }
