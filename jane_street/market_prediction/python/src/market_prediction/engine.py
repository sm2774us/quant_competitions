import numpy as np
import torch
from .models import ModelManager
from .preprocessor import MarketPreprocessor
from typing import Optional, Dict

class InferenceEngine:
    """
    Main engine for market prediction.
    Coordinates preprocessing and model inference.
    """
    def __init__(self, 
                 model_manager: ModelManager, 
                 preprocessor: MarketPreprocessor,
                 threshold: float = 0.5):
        self.model_manager = model_manager
        self.preprocessor = preprocessor
        self.threshold = threshold

    def predict_action(self, features: np.ndarray) -> int:
        """
        Receives raw features and returns a binary action.
        :param features: 1D numpy array of 130 features.
        :return: 0 (pass) or 1 (trade).
        """
        # 1. Preprocess (Imputation + Normalization)
        processed_features = self.preprocessor.transform(features)
        
        # 2. Model Inference
        # Convert to torch tensor
        features_tensor = torch.from_numpy(processed_features).float()
        
        # 3. Predict Action
        prob = self.model_manager.predict(features_tensor)
        
        return 1 if prob.item() >= self.threshold else 0

    def batch_predict(self, features_batch: np.ndarray) -> np.ndarray:
        """
        Batch inference for higher throughput.
        :param features_batch: 2D numpy array (batch_size, 130).
        :return: 1D numpy array of actions.
        """
        # Note: Preprocessor handles 1D. For batch, we'd ideally vectorize it too.
        # For simplicity in this OOP example, we'll iterate or provide a vectorized preprocessor.
        processed_batch = np.array([self.preprocessor.transform(f) for f in features_batch])
        features_tensor = torch.from_numpy(processed_batch).float()
        probs = self.model_manager.predict(features_tensor)
        return (probs >= self.threshold).int().cpu().numpy().flatten()
