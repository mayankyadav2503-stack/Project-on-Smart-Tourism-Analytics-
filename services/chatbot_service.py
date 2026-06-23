import re
import json
import sqlite3
from datetime import datetime
from config import DB_PATH

class TourismChatbot:
    def __init__(self):
        self.context = {}

    def process_message(self, message, user_id=None):
        msg = message.lower().strip()
        self.context["user_id"] = user_id

        if any(greet in msg for greet in ["hello", "hi ", "hey", "good morning", "good evening"]):
            return self._greet()
        if any(w in msg for w in ["recommend", "suggest", "where should i go", "best place"]):
            return self._recommend(user_id)
        if "weather" in msg:
            return self._weather(msg)
        if any(w in msg for w in ["budget", "cost", "spend", "cheap", "expensive", "price"]):
            return self._budget(msg, user_id)
        if any(w in msg for w in ["itinerary", "plan", "trip plan", "schedule"]):
            return self._itinerary(user_id)
        if any(w in msg for w in ["hotel", "stay", "accommodation", "room"]):
            return self._hotel(msg)
        if any(w in msg for w in ["restaurant", "food", "eat", "cuisine", "dining"]):
            return self._restaurant(msg)
        if any(w in msg for w in ["activity", "thing to do", "attraction", "tour", "sightseeing"]):
            return self._activity(msg)
        if "currency" in msg or "exchange" in msg or "convert" in msg:
            return self._currency(msg)
        if "crowd" in msg or "busy" in msg or "crowded" in msg:
            return self._crowd(msg)
        if any(w in msg for w in ["help", "what can you do", "capabilities"]):
            return self._help()
        if "thank" in msg:
            return {"reply": "You're welcome! Have a great trip! 🌍", "type": "chat"}

        return {"reply": self._fallback(), "type": "chat"}

    def _greet(self):
        return {
            "reply": "Hello! 👋 I'm your Smart Travel Assistant. I can help you with:\n"
                     "• Destination recommendations 🌍\n• Weather forecasts 🌤\n• Budget planning 💰\n"
                     "• Itinerary generation 📋\n• Hotel & restaurant suggestions 🏨🍽\n"
                     "• Currency conversion 💱\n• Crowd predictions 📊\n\n"
                     "What would you like help with?",
            "type": "chat"
        }

    def _recommend(self, user_id):
        from services.recommendation_service import RecommendationService
        recs = RecommendationService()
        if user_id:
            results = recs.get_personalized(user_id, 5)
        else:
            results = recs.get_popular(5)

        if not results:
            return {"reply": "I couldn't find any recommendations right now.", "type": "chat"}

        reply = "Here are my top recommendations for you:\n\n"
        for d, score in results:
            reply += f"⭐ {d['name']} ({d['city']}, {d['country']}) - Rating: {d['avg_rating']}/5\n"
        reply += "\nWould you like details on any of these? Just ask!"
        return {"reply": reply, "type": "chat", "data": [d for d, _ in results]}

    def _weather(self, msg):
        city = self._extract_city(msg)
        if not city:
            return {"reply": "Which city would you like the weather for?", "type": "chat", "ask_city": True}
        from services.weather_service import get_weather
        w = get_weather(city)
        return {
            "reply": f"🌤 Weather in {w['city']}:\n🌡 Temperature: {w['temperature']}°C (feels like {w['feels_like']}°C)\n"
                     f"☁ {w['description'].title()}\n💧 Humidity: {w['humidity']}%\n💨 Wind: {w['wind_speed']} m/s",
            "type": "weather",
            "data": w
        }

    def _budget(self, msg, user_id):
        if not user_id:
            return {"reply": "Please log in to get personalized budget recommendations.", "type": "chat"}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT budget_min, budget_max FROM users WHERE id=?", (user_id,))
        user = cur.fetchone()
        conn.close()
        if user:
            return {
                "reply": f"Your travel budget range: ${user['budget_min']:.0f} - ${user['budget_max']:.0f}\n\n"
                         f"💡 Tips:\n• For budget-friendly stays, look for hostels or B&Bs\n"
                         f"• Book flights 2-3 months in advance for best prices\n"
                         f"• Consider visiting during shoulder season (Spring/Fall)\n"
                         f"• Street food and local markets save money on meals",
                "type": "budget",
                "data": {"budget_min": user["budget_min"], "budget_max": user["budget_max"]}
            }
        return {"reply": "I couldn't find your budget info. Please update your profile.", "type": "chat"}

    def _itinerary(self, user_id):
        if not user_id:
            return {"reply": "Please log in to generate itineraries.", "type": "chat"}
        from services.itinerary_service import ItineraryService
        its = ItineraryService()
        itineraries = its.get_user_itineraries(user_id)
        if itineraries:
            reply = "Your saved itineraries:\n\n"
            for i in itineraries:
                reply += f"📋 {i['name']} - {i['destination_name']} ({i['start_date']} to {i['end_date']})\n"
            reply += "\nWant to create a new one? Tell me your destination and dates!"
            return {"reply": reply, "type": "chat", "data": itineraries}
        return {"reply": "You don't have any itineraries yet. Tell me a destination and dates to create one!", "type": "chat"}

    def _hotel(self, msg):
        city = self._extract_city(msg)
        if not city:
            return {"reply": "Which city are you looking for hotels in?", "type": "chat", "ask_city": True}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT h.*, d.name as dest_name FROM hotels h
            JOIN destinations d ON h.destination_id = d.id
            WHERE d.city LIKE ? OR d.name LIKE ?
            ORDER BY h.rating DESC LIMIT 5
        """, (f"%{city}%", f"%{city}%"))
        hotels = cur.fetchall()
        conn.close()
        if hotels:
            reply = f"🏨 Hotels in {city.title()}:\n\n"
            for h in hotels:
                reply += f"• {h['name']} - ${h['price_per_night']}/night ⭐ {h['rating']}\n"
            return {"reply": reply, "type": "chat", "data": [dict(h) for h in hotels]}
        return {"reply": f"Sorry, I couldn't find hotels in {city}. Try another city!", "type": "chat"}

    def _restaurant(self, msg):
        city = self._extract_city(msg)
        cuisine = self._extract_cuisine(msg)
        if not city:
            return {"reply": "Which city are you looking for restaurants in?", "type": "chat", "ask_city": True}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if cuisine:
            cur.execute("""
                SELECT r.*, d.name as dest_name FROM restaurants r
                JOIN destinations d ON r.destination_id = d.id
                WHERE (d.city LIKE ? OR d.name LIKE ?) AND r.cuisine LIKE ?
                ORDER BY r.rating DESC LIMIT 5
            """, (f"%{city}%", f"%{city}%", f"%{cuisine}%"))
        else:
            cur.execute("""
                SELECT r.*, d.name as dest_name FROM restaurants r
                JOIN destinations d ON r.destination_id = d.id
                WHERE d.city LIKE ? OR d.name LIKE ?
                ORDER BY r.rating DESC LIMIT 5
            """, (f"%{city}%", f"%{city}%"))
        restaurants = cur.fetchall()
        conn.close()
        if restaurants:
            reply = f"🍽 Restaurants in {city.title()}:\n\n"
            for r in restaurants:
                reply += f"• {r['name']} - {r['cuisine']} ({r['price_range']}) ⭐ {r['rating']}\n"
            return {"reply": reply, "type": "chat", "data": [dict(r) for r in restaurants]}
        return {"reply": f"Sorry, no restaurants found in {city}.", "type": "chat"}

    def _activity(self, msg):
        city = self._extract_city(msg)
        if not city:
            return {"reply": "Which city would you like activity suggestions for?", "type": "chat", "ask_city": True}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT a.*, d.name as dest_name FROM activities a
            JOIN destinations d ON a.destination_id = d.id
            WHERE d.city LIKE ? OR d.name LIKE ?
            ORDER BY a.rating DESC LIMIT 5
        """, (f"%{city}%", f"%{city}%"))
        activities = cur.fetchall()
        conn.close()
        if activities:
            reply = f"🎯 Activities in {city.title()}:\n\n"
            for a in activities:
                cost_str = f"${a['cost']:.0f}" if a['cost'] > 0 else "Free"
                reply += f"• {a['name']} - {cost_str} ({a['duration_hours']}h) ⭐ {a['rating']}\n"
            return {"reply": reply, "type": "chat", "data": [dict(a) for a in activities]}
        return {"reply": f"Sorry, no activities found in {city}.", "type": "chat"}

    def _currency(self, msg):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT target_currency, rate FROM currency_rates WHERE base_currency='USD'")
        rates = cur.fetchall()
        conn.close()
        reply = "💱 USD Exchange Rates:\n\n"
        for r in rates:
            reply += f"• 1 USD = {r['rate']} {r['target_currency']}\n"
        return {"reply": reply, "type": "currency", "data": {r["target_currency"]: r["rate"] for r in rates}}

    def _crowd(self, msg):
        city = self._extract_city(msg)
        if not city:
            return {"reply": "Which city would you like crowd predictions for?", "type": "chat", "ask_city": True}
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT cd.date, cd.predicted_crowd_level, d.name, d.city
            FROM crowd_data cd
            JOIN destinations d ON cd.destination_id = d.id
            WHERE d.city LIKE ? OR d.name LIKE ?
            ORDER BY cd.date LIMIT 7
        """, (f"%{city}%", f"%{city}%"))
        rows = cur.fetchall()
        conn.close()
        if rows:
            reply = f"📊 Crowd Predictions for {city.title()}:\n\n"
            for r in rows:
                level = "🔴 High" if r["predicted_crowd_level"] > 3.5 else ("🟡 Medium" if r["predicted_crowd_level"] > 2.0 else "🟢 Low")
                reply += f"• {r['date']}: {level} ({r['predicted_crowd_level']}/5)\n"
            return {"reply": reply, "type": "chat", "data": [dict(r) for r in rows]}
        return {"reply": f"Sorry, no crowd data for {city}.", "type": "chat"}

    def _help(self):
        return {
            "reply": "🤖 I can help you with:\n\n"
                     "🌍 **Destinations** - 'Recommend places', 'Best places in Paris'\n"
                     "🌤 **Weather** - 'Weather in Tokyo'\n"
                     "🏨 **Hotels** - 'Hotels in Rome'\n"
                     "🍽 **Restaurants** - 'Restaurants in Bangkok'\n"
                     "🎯 **Activities** - 'Things to do in Dubai'\n"
                     "💰 **Budget** - 'Budget planning', 'Cheap destinations'\n"
                     "📋 **Itineraries** - 'Plan a trip', 'My itineraries'\n"
                     "💱 **Currency** - 'Exchange rates'\n"
                     "📊 **Crowds** - 'Crowd prediction Paris'\n\n"
                     "Just ask me anything about travel!",
            "type": "chat"
        }

    def _fallback(self):
        return ("I'm not sure I understand. I can help with travel recommendations, weather, "
                "hotels, restaurants, activities, budget planning, and more! Type 'help' to see what I can do.")

    def _extract_city(self, msg):
        words = msg.split()
        for word in words:
            w = word.strip(",.?!")
            if w.title() in [
                "Paris", "Tokyo", "New York", "London", "Rome", "Sydney", "Dubai",
                "Bali", "Agra", "Beijing", "Cairo", "Bangkok", "Istanbul", "Barcelona",
                "Amsterdam", "Berlin", "Mumbai", "Delhi", "Singapore", "Kuala Lumpur",
                "Seoul", "Osaka", "Kyoto", "Florence", "Venice", "Santorini", "Cusco",
                "Arizona", "Machu Picchu"
            ]:
                return w
        return ""

    def _extract_cuisine(self, msg):
        cuisines = ["italian", "chinese", "japanese", "indian", "mexican", "french",
                     "thai", "korean", "vietnamese", "mediterranean", "american", "seafood"]
        for c in cuisines:
            if c in msg:
                return c
        return ""
