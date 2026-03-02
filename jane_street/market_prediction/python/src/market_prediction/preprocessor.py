import numpy as np
import json
import os
from typing import Optional, Dict

class MarketPreprocessor:
    """
    Handles imputation, normalization, and interaction feature computation.
    Optimized for streaming/online processing.
    """
    def __init__(self, n_features: int = 130, window_size: int = 100):
        self.n_features = n_features
        self.window_size = window_size
        self.means = np.zeros(n_features)
        self.stds = np.ones(n_features)
        
        # Pre-trained params
        self.medians = np.zeros((2, n_features))
        self.scaler_mean = np.zeros(n_features - 1 + 6) # f1-f129 + 6 interactions
        self.scaler_scale = np.ones(n_features - 1 + 6)
        
        self.window = []
        
    def transform(self, x: np.ndarray) -> np.ndarray:
        """
        Transforms raw feature vector: handles NaNs, adds interactions, and normalizes.
        :param x: 1D numpy array of 130 features.
        :return: Processed 1D numpy array of 136 features.
        """
        # 1. Imputation
        side = x[0]
        side_id = 0 if side == -1 else 1
        
        # Use provided medians for initial imputation if window is empty
        if len(self.window) == 0:
            imputed = self.medians[side_id]
        else:
            imputed = np.nanmedian(np.array(self.window), axis=0)
            
        x_imputed = np.where(np.isnan(x), imputed, x)
        
        # 2. Interactions (6 specific features from competition.py)
        interactions = np.array([
            x_imputed[3] * x_imputed[45],
            x_imputed[10] * x_imputed[122],
            x_imputed[14] * x_imputed[58],
            x_imputed[22] * x_imputed[42],
            x_imputed[35] * x_imputed[20],
            x_imputed[45] * x_imputed[47],
        ])
        
        features_extended = np.concatenate([x_imputed, interactions])
        
        # 3. Normalization (skips f0, normalizes f1-f135)
        f0 = features_extended[0]
        f_rest = features_extended[1:]
        
        f_norm = (f_rest - self.scaler_mean) / (self.scaler_scale + 1e-8)
        
        final_features = np.concatenate([[f0], f_norm])
        
        # 4. Update rolling statistics (online update)
        self._update_stats(x_imputed)
        
        return final_features

    def _update_stats(self, x: np.ndarray):
        """Updates global moving stats with a new observation."""
        self.window.append(x)
        if len(self.window) > self.window_size:
            self.window.pop(0)
            
    def save_state(self, path: str):
        """Saves preprocessor state for persistence."""
        state = {
            "medians": self.medians.tolist(),
            "scaler_mean": self.scaler_mean.tolist(),
            "scaler_scale": self.scaler_scale.tolist()
        }
        with open(path, 'w') as f:
            json.dump(state, f)
        
    def load_state(self, path: str):
        """Loads pre-trained stats from a JSON file."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                state = json.load(f)
                self.medians = np.array(state.get("medians", self.medians.tolist()))
                self.scaler_mean = np.array(state.get("scaler_mean", self.scaler_mean.tolist()))
                self.scaler_scale = np.array(state.get("scaler_scale", self.scaler_scale.tolist()))
