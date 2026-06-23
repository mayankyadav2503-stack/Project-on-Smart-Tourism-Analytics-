from flask import Blueprint, request, jsonify
import sqlite3
import numpy as np
import pandas as pd
import os
from config import DB_PATH, MODELS_DIR
import json

travel_bp = Blueprint("travel", __name__)

@travel_bp.route("/api/trends", methods=["GET"])
def trends():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT d.category, COUNT(*) as count, ROUND(AVG(d.avg_rating),2) as avg_rating
        FROM destinations d GROUP BY d.category ORDER BY count DESC
    """)
    category_dist = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT strftime('%m', cd.date) as month, ROUND(AVG(cd.predicted_crowd_level),2) as avg_crowd
        FROM crowd_data cd GROUP BY month ORDER BY month
    """)
    monthly_crowd = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT d.name, d.city, COUNT(b.id) as bookings, SUM(b.cost) as revenue
        FROM bookings b JOIN destinations d ON b.destination_id = d.id
        GROUP BY b.destination_id ORDER BY bookings DESC LIMIT 10
    """)
    top_dest = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT AVG(price_per_night) as avg_hotel_price, MIN(price_per_night) as min_price, MAX(price_per_night) as max_price FROM hotels")
    hotel_stats = dict(cur.fetchone())

    conn.close()

    return jsonify({
        "category_distribution": category_dist,
        "monthly_crowd": monthly_crowd,
        "top_destinations": top_dest,
        "hotel_stats": hotel_stats,
    })

@travel_bp.route("/api/forecast/<int:dest_id>", methods=["GET"])
def forecast(dest_id):
    days = int(request.args.get("days", 7))
    path = os.path.join(MODELS_DIR, "demand_forecast.pkl")
    if os.path.exists(path):
        from models.demand_forecast import DemandForecaster
        model = DemandForecaster.load()
        return jsonify(model.forecast(dest_id, days))
    return jsonify({"error": "Model not trained"}), 503

@travel_bp.route("/api/crowd/<int:dest_id>", methods=["GET"])
def crowd_predict(dest_id):
    days = int(request.args.get("days", 7))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT popularity_score, avg_rating, review_count FROM destinations WHERE id=?", (dest_id,))
    dest = cur.fetchone()
    conn.close()
    if not dest:
        return jsonify({"error": "Not found"}), 404

    path = os.path.join(MODELS_DIR, "crowd_prediction.pkl")
    if os.path.exists(path):
        from models.crowd_prediction import CrowdPredictor
        model = CrowdPredictor.load()
        return jsonify(model.predict_for_destination(dict(dest), days))
    return jsonify({"error": "Model not trained"}), 503

@travel_bp.route("/api/sentiment", methods=["POST"])
def analyze_sentiment():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text"}), 400

    result = _fallback_sentiment(text)

    import threading
    bert_result = [None]
    def run_bert():
        try:
            from models.sentiment_analysis import SentimentAnalyzer
            sa = SentimentAnalyzer()
            bert_result[0] = sa.analyze(text)
        except:
            pass
    t = threading.Thread(target=run_bert, daemon=True)
    t.start()
    t.join(timeout=5)
    if bert_result[0]:
        result["bert_sentiment"] = bert_result[0]["sentiment"]
        result["bert_score"] = bert_result[0]["score"]

    return jsonify(result)


def _fallback_sentiment(text):
    positive_words = {"amazing", "excellent", "great", "wonderful", "fantastic", "beautiful",
                      "love", "perfect", "awesome", "best", "good", "nice", "pleasant",
                      "enjoyed", "recommend", "favorite", "gorgeous", "breathtaking"}
    negative_words = {"terrible", "awful", "horrible", "bad", "worst", "disappointing",
                      "poor", "hate", "boring", "ugly", "dirty", "expensive", "rude",
                      "waste", "avoid", "mediocre", "overrated"}
    words = set(text.lower().split())
    pos_count = len(words & positive_words)
    neg_count = len(words & negative_words)
    if pos_count > neg_count:
        return {"sentiment": "positive", "score": round(min(1.0, pos_count / max(1, pos_count + neg_count)), 4)}
    elif neg_count > pos_count:
        return {"sentiment": "negative", "score": round(min(1.0, neg_count / max(1, pos_count + neg_count)), 4)}
    return {"sentiment": "neutral", "score": 0.5}

@travel_bp.route("/api/reviews/<int:dest_id>", methods=["GET"])
def get_reviews(dest_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, u.username FROM reviews r
        LEFT JOIN users u ON r.user_id = u.id
        WHERE r.destination_id=? ORDER BY r.created_at DESC LIMIT 50
    """, (dest_id,))
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@travel_bp.route("/api/map/destinations", methods=["GET"])
def map_destinations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT id, name, city, country, latitude, longitude, category, avg_rating, popularity_score FROM destinations WHERE latitude IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
