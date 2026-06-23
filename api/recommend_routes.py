from flask import Blueprint, request, jsonify
import sqlite3
from config import DB_PATH
from services.recommendation_service import RecommendationService
from services.itinerary_service import ItineraryService
from services.weather_service import get_weather
from services.currency_service import get_currency_rates, convert_currency

recommend_bp = Blueprint("recommend", __name__)
rec_service = RecommendationService()
it_service = ItineraryService()

@recommend_bp.route("/api/recommendations/popular", methods=["GET"])
def popular():
    n = int(request.args.get("limit", 10))
    results = rec_service.get_popular(n)
    return jsonify([{"destination": d, "score": s} for d, s in results])

@recommend_bp.route("/api/recommendations/personalized/<int:user_id>", methods=["GET"])
def personalized(user_id):
    n = int(request.args.get("limit", 10))
    results = rec_service.get_personalized(user_id, n)
    return jsonify([{"destination": d, "score": s} for d, s in results])

@recommend_bp.route("/api/recommendations/similar/<int:dest_id>", methods=["GET"])
def similar(dest_id):
    results = rec_service.get_similar_destinations(dest_id)
    return jsonify([{"destination": d, "score": s} for d, s in results])

@recommend_bp.route("/api/destinations", methods=["GET"])
def list_destinations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM destinations ORDER BY popularity_score DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@recommend_bp.route("/api/destinations/<int:dest_id>", methods=["GET"])
def get_destination(dest_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM destinations WHERE id=?", (dest_id,))
    dest = cur.fetchone()
    if not dest:
        conn.close()
        return jsonify({"error": "Not found"}), 404
    result = dict(dest)
    cur.execute("SELECT * FROM hotels WHERE destination_id=?", (dest_id,))
    result["hotels"] = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT * FROM restaurants WHERE destination_id=?", (dest_id,))
    result["restaurants"] = [dict(r) for r in cur.fetchall()]
    cur.execute("SELECT * FROM activities WHERE destination_id=?", (dest_id,))
    result["activities"] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(result)

@recommend_bp.route("/api/hotels", methods=["GET"])
def list_hotels():
    dest_id = request.args.get("destination_id")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if dest_id:
        cur.execute("SELECT * FROM hotels WHERE destination_id=? ORDER BY rating DESC", (dest_id,))
    else:
        cur.execute("SELECT * FROM hotels ORDER BY rating DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@recommend_bp.route("/api/restaurants", methods=["GET"])
def list_restaurants():
    dest_id = request.args.get("destination_id")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if dest_id:
        cur.execute("SELECT * FROM restaurants WHERE destination_id=? ORDER BY rating DESC", (dest_id,))
    else:
        cur.execute("SELECT * FROM restaurants ORDER BY rating DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@recommend_bp.route("/api/activities", methods=["GET"])
def list_activities():
    dest_id = request.args.get("destination_id")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if dest_id:
        cur.execute("SELECT * FROM activities WHERE destination_id=? ORDER BY rating DESC", (dest_id,))
    else:
        cur.execute("SELECT * FROM activities ORDER BY rating DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@recommend_bp.route("/api/weather", methods=["GET"])
def weather():
    city = request.args.get("city", "Paris")
    return jsonify(get_weather(city))

@recommend_bp.route("/api/currency", methods=["GET"])
def currency():
    base = request.args.get("base", "USD")
    return jsonify(get_currency_rates(base))

@recommend_bp.route("/api/currency/convert", methods=["GET"])
def convert():
    amount = float(request.args.get("amount", 1))
    from_cur = request.args.get("from", "USD").upper()
    to_cur = request.args.get("to", "EUR").upper()
    return jsonify({"amount": amount, "from": from_cur, "to": to_cur, "result": convert_currency(amount, from_cur, to_cur)})

@recommend_bp.route("/api/itinerary/generate", methods=["POST"])
def generate_itinerary():
    data = request.json
    result = it_service.generate_itinerary(
        data["user_id"], data["destination_id"],
        data["start_date"], data["end_date"],
        data.get("budget"),
    )
    if result:
        return jsonify(result)
    return jsonify({"error": "Generation failed"}), 400

@recommend_bp.route("/api/itinerary/user/<int:user_id>", methods=["GET"])
def user_itineraries(user_id):
    return jsonify(it_service.get_user_itineraries(user_id))

@recommend_bp.route("/api/budget/<int:user_id>", methods=["GET"])
def budget_analysis(user_id):
    return jsonify(it_service.get_budget_analysis(user_id))

@recommend_bp.route("/api/search", methods=["GET"])
def search():
    q = request.args.get("q", "")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    like = f"%{q}%"
    cur.execute("""
        SELECT id, name, city, country, category, 'destination' as type FROM destinations
        WHERE name LIKE ? OR city LIKE ? OR country LIKE ?
        LIMIT 10
    """, (like, like, like))
    results = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify(results)
