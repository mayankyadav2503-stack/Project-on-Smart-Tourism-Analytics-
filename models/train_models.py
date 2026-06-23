import numpy as np
import pandas as pd
import sqlite3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH, MODELS_DIR
from database.schema import init_db
from database.seed_data import seed_database

def train_all():
    os.makedirs(MODELS_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    print("[Train] Training collaborative filtering model...")
    reviews_df = pd.read_sql("SELECT id, user_id, rating, destination_id as item_id, 'destination' as item_type FROM reviews WHERE destination_id > 0 UNION ALL SELECT id, user_id, rating, hotel_id as item_id, 'hotel' as item_type FROM reviews WHERE hotel_id > 0", conn)
    if len(reviews_df) > 0:
        from models.collaborative_filtering import CollabFilterRecommender
        cf = CollabFilterRecommender(n_factors=15)
        cf.fit(reviews_df)
        cf.save()
        print(f"[Train] CF model trained with {len(reviews_df)} reviews")
    else:
        print("[Train] No reviews found, skipping CF model")

    print("[Train] Training demand forecasting model...")
    bookings_df = pd.read_sql("SELECT b.*, d.popularity_score FROM bookings b JOIN destinations d ON b.destination_id = d.id", conn)
    if len(bookings_df) > 0:
        bookings_df["booking_date"] = pd.to_datetime(bookings_df["booking_date"])
        bookings_df["day_of_week"] = bookings_df["booking_date"].dt.dayofweek
        bookings_df["month"] = bookings_df["booking_date"].dt.month
        bookings_df["is_holiday"] = (bookings_df["day_of_week"] >= 5).astype(int)

        daily_demand = bookings_df.groupby(["destination_id", "booking_date"]).size().reset_index(name="demand")
        daily_demand = daily_demand.merge(
            bookings_df[["destination_id", "popularity_score"]].drop_duplicates(),
            on="destination_id"
        )
        daily_demand["day_of_week"] = pd.to_datetime(daily_demand["booking_date"]).dt.dayofweek
        daily_demand["month"] = pd.to_datetime(daily_demand["booking_date"]).dt.month
        daily_demand["is_holiday"] = (daily_demand["day_of_week"] >= 5).astype(int)

        from models.demand_forecast import DemandForecaster
        df_model = DemandForecaster()
        df_model.fit(daily_demand)
        df_model.save()
        print(f"[Train] Demand model trained with {len(daily_demand)} records")
    else:
        print("[Train] No bookings found, using synthetic demand data")
        crowd_df = pd.read_sql("SELECT cd.*, d.popularity_score FROM crowd_data cd JOIN destinations d ON cd.destination_id = d.id", conn)
        if len(crowd_df) > 0:
            crowd_df["demand"] = crowd_df["predicted_crowd_level"] * 10
            from models.demand_forecast import DemandForecaster
            df_model = DemandForecaster()
            df_model.fit(crowd_df)
            df_model.save()
            print(f"[Train] Demand model trained with synthetic data ({len(crowd_df)} records)")

    print("[Train] Training crowd prediction model...")
    crowd_df_all = pd.read_sql("SELECT cd.*, d.popularity_score, d.avg_rating, d.review_count FROM crowd_data cd JOIN destinations d ON cd.destination_id = d.id", conn)
    if len(crowd_df_all) > 0:
        crowd_df_all["crowd_level"] = crowd_df_all["predicted_crowd_level"]
        from models.crowd_prediction import CrowdPredictor
        cp = CrowdPredictor()
        cp.fit(crowd_df_all)
        cp.save()
        print(f"[Train] Crowd model trained with {len(crowd_df_all)} records")
    else:
        print("[Train] No crowd data found, skipping")

    print("[Train] Saving sentiment analysis model reference...")
    from models.sentiment_analysis import SentimentAnalyzer
    sa = SentimentAnalyzer()
    sa.save()
    print("[Train] Sentiment model reference saved (loads from HuggingFace on demand)")

    conn.close()
    print("[Train] All models trained and saved successfully")

if __name__ == "__main__":
    print("=" * 50)
    print("Smart Tourism Analytics Platform - Model Training")
    print("=" * 50)
    init_db()
    seed_database()
    train_all()
