import numpy as np
import pandas as pd
from xgboost import XGBRegressor
import joblib
import os
from config import MODELS_DIR

class DemandForecaster:
    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, verbosity=0
        )
        self.feature_cols = ["day_of_week", "month", "is_holiday", "destination_popularity",
                             "prev_day_demand", "week_avg_demand"]

    def _build_features(self, df):
        features = pd.DataFrame()
        features["day_of_week"] = df["day_of_week"]
        features["month"] = df["month"]
        features["is_holiday"] = df["is_holiday"]
        features["destination_popularity"] = df.get("popularity_score", 0)
        if "destination_id" in df.columns:
            features["prev_day_demand"] = df.groupby("destination_id")["demand"].shift(1).fillna(df["demand"].mean())
            features["week_avg_demand"] = df.groupby("destination_id")["demand"].transform(
                lambda x: x.rolling(7, min_periods=1).mean().fillna(x.mean())
            )
        else:
            features["prev_day_demand"] = df["demand"]
            features["week_avg_demand"] = df["demand"]
        return features

    def fit(self, df):
        X = self._build_features(df)
        y = df["demand"].values
        self.model.fit(X[self.feature_cols], y)
        return self

    def predict(self, df):
        X = self._build_features(df)
        return self.model.predict(X[self.feature_cols])

    def forecast(self, destination_id, days_ahead=7):
        import sqlite3
        from config import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT popularity_score FROM destinations WHERE id=?", (destination_id,))
        row = cur.fetchone()
        pop = row[0] if row else 50
        conn.close()

        from datetime import datetime, timedelta
        today = datetime.now()
        results = []
        for i in range(days_ahead):
            d = today + timedelta(days=i)
            pred_df = pd.DataFrame({
                "day_of_week": [d.weekday()],
                "month": [d.month],
                "is_holiday": [1 if d.weekday() >= 5 else 0],
                "popularity_score": [pop],
                "demand": [pop * 0.5],
            })
            pred_df["prev_day_demand"] = pop * 0.5
            pred_df["week_avg_demand"] = pop * 0.5
            X_pred = self._build_features(pred_df)
            val = self.model.predict(X_pred[self.feature_cols])[0]
            results.append({"date": d.strftime("%Y-%m-%d"), "forecasted_demand": round(float(val), 1)})
        return results

    def save(self, path=None):
        path = path or os.path.join(MODELS_DIR, "demand_forecast.pkl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path=None):
        path = path or os.path.join(MODELS_DIR, "demand_forecast.pkl")
        return joblib.load(path)
