import numpy as np
import joblib
import os
from config import MODELS_DIR

class SentimentAnalyzer:
    def __init__(self, model_name="distilbert/distilbert-base-uncased-finetuned-sst-2-english"):
        self.model_name = model_name
        self._pipe = None

    @property
    def pipe(self):
        if self._pipe is None:
            from transformers import pipeline as _pipeline
            self._pipe = _pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                truncation=True,
                max_length=512,
            )
        return self._pipe

    def analyze(self, text):
        result = self.pipe(text[:512])[0]
        label = result["label"]
        score = result["score"]
        if label == "POSITIVE":
            return {"sentiment": "positive", "score": round(float(score), 4)}
        elif label == "NEGATIVE":
            return {"sentiment": "negative", "score": round(float(1 - score), 4)}
        return {"sentiment": "neutral", "score": 0.5}

    def analyze_batch(self, texts):
        results = self.pipe([t[:512] for t in texts])
        parsed = []
        for r in results:
            label, score = r["label"], r["score"]
            if label == "POSITIVE":
                parsed.append({"sentiment": "positive", "score": round(float(score), 4)})
            else:
                parsed.append({"sentiment": "negative", "score": round(float(1 - score), 4)})
        return parsed

    def save(self, path=None):
        path = path or os.path.join(MODELS_DIR, "sentiment_model.pkl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"model_name": self.model_name}, path)

    @staticmethod
    def load(path=None):
        path = path or os.path.join(MODELS_DIR, "sentiment_model.pkl")
        data = joblib.load(path)
        return SentimentAnalyzer(model_name=data["model_name"])
