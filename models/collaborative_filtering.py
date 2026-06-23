import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.decomposition import NMF
import joblib
import os
from config import MODELS_DIR

class CollabFilterRecommender:
    def __init__(self, n_factors=20):
        self.n_factors = n_factors
        self.model = None
        self.user_map = {}
        self.item_map = {}
        self.reverse_user_map = {}
        self.reverse_item_map = {}
        self.user_means = {}

    def build_matrix(self, reviews_df):
        users = reviews_df["user_id"].unique()
        items = reviews_df["item_id"].unique()
        self.user_map = {u: i for i, u in enumerate(users)}
        self.item_map = {it: i for i, it in enumerate(items)}
        self.reverse_user_map = {i: u for u, i in self.user_map.items()}
        self.reverse_item_map = {i: it for it, i in self.item_map.items()}

        matrix = np.zeros((len(users), len(items)))
        for _, row in reviews_df.iterrows():
            u = self.user_map[row["user_id"]]
            it = self.item_map[row["item_id"]]
            matrix[u, it] = row["rating"]
        return matrix

    def fit(self, reviews_df):
        matrix = self.build_matrix(reviews_df)
        mask = matrix > 0
        self.user_means = {i: matrix[i][mask[i]].mean() if mask[i].sum() > 0 else 3.0 for i in range(matrix.shape[0])}
        matrix_centered = matrix.copy().astype(np.float64)
        for i in range(matrix.shape[0]):
            matrix_centered[i][mask[i]] -= self.user_means[i]
        matrix_centered[matrix_centered < 0] = 0

        self.model = NMF(n_components=self.n_factors, init="random", random_state=42, max_iter=500)
        self.W = self.model.fit_transform(matrix_centered)
        self.H = self.model.components_
        return self

    def predict(self, user_id, item_id):
        if user_id not in self.user_map or item_id not in self.item_map:
            return self.user_means.get(self.user_map.get(user_id, -1), 3.0) if user_id in self.user_map else 3.0
        u = self.user_map[user_id]
        it = self.item_map[item_id]
        pred = self.W[u, :].dot(self.H[:, it]) + self.user_means[u]
        return max(1, min(5, pred))

    def recommend(self, user_id, item_ids, n=10):
        scored = []
        for it in item_ids:
            score = self.predict(user_id, it)
            scored.append((it, score))
        scored.sort(key=lambda x: -x[1])
        return scored[:n]

    def save(self, path=None):
        path = path or os.path.join(MODELS_DIR, "collab_filter.pkl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)

    @staticmethod
    def load(path=None):
        path = path or os.path.join(MODELS_DIR, "collab_filter.pkl")
        return joblib.load(path)
