import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from config import MODELS_DIR

class CrowdPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        self.feature_cols = ["day_of_week", "month", "is_holiday", "popularity_score",
                             "avg_rating", "review_count"]

    def fit(self, df):
        X = df[self.feature_cols]
        y = df["crowd_level"]
        self.model.fit(X, y)
        return self

    def predict(self, df):
        X = df[self.feature_cols]
        return self.model.predict(X)

    def predict_for_destination(self, dest_data, days_ahead=7):
        from datetime import datetime, timedelta
        today = datetime.now()
        results = []
        for i in range(days_ahead):
            d = today + timedelta(days=i)
            row = pd.DataFrame({
                "day_of_week": [d.weekday()],
                "month": [d.month],
                "is_holiday": [1 if d.weekday() >= 5 else 0],
                "popularity_score": [dest_data.get("popularity_score", 50)],
                "avg_rating": [dest_data.get("avg_rating", 4.0)],
                "review_count": [dest_data.get("review_count", 100)],
            })
            pred = self.model.predict(row)[0]
            level = "High" if pred > 3.5 else ("Medium" if pred > 2.0 else "Low")
            results.append({"date": d.strftime("%Y-%m-%d"), "crowd_level": round(float(pred), 1), "level": level})
        return results

    def save(self, path=None):
        path = path or os.path.join(MODELS_DIR, "crowd_prediction.pkl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path=None):
        path = path or os.path.join(MODELS_DIR, "crowd_prediction.pkl")
        return joblib.load(path)
