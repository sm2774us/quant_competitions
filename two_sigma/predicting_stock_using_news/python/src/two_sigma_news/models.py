import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from .interfaces import IModel, IEvaluator

class TwoSigmaModel(IModel):
    def __init__(self, alpha: float = 1.0):
        self.model = Ridge(alpha=alpha)

    def train(self, X: np.ndarray, y: np.ndarray):
        # Flatten time series windows if necessary or assume features are already processed
        # For simplicity, we assume X is (n_samples, n_features)
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        # Predict confidence values (-1 to 1)
        # Ridge.predict returns continuous values
        preds = self.model.predict(X)
        # Normalize/clip to [-1, 1]
        return np.clip(preds, -1, 1)

class TwoSigmaEvaluator(IEvaluator):
    def evaluate(self, predictions: np.ndarray, targets: np.ndarray, universe: np.ndarray) -> float:
        """
        Score = mean(daily_return) / std(daily_return)
        daily_return = sum(confidence * target * universe)
        """
        # Here we need the daily aggregation. If we have a single day, std is 0.
        # This evaluator assumes predictions, targets, and universe are aligned and potentially multi-day.
        # To calculate the daily score, we'd need time indices.
        # For a simplified version, we return the ratio of weighted returns.
        
        weighted_returns = predictions * targets * universe
        if len(weighted_returns) == 0:
            return 0.0
            
        # Simplified: if we don't have time indices, we treat each sample as a day
        # In real scenario, we'd group by day.
        mu = np.mean(weighted_returns)
        sigma = np.std(weighted_returns)
        
        if sigma == 0:
            return mu if mu == 0 else (mu / 1e-6)
            
        return mu / sigma

    def evaluate_with_time(self, df: pd.DataFrame, pred_col: str, target_col: str, universe_col: str) -> float:
        # Daily weighted return: x_t = sum_i(C_it * R_it * U_it)
        df['x_t'] = df[pred_col] * df[target_col] * df[universe_col]
        daily_returns = df.groupby('time')['x_t'].sum()
        
        mu = daily_returns.mean()
        sigma = daily_returns.std()
        
        if sigma == 0 or np.isnan(sigma):
            return 0.0
            
        return mu / sigma
