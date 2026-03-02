import numpy as np
import pytest
from market_prediction.engine import InferenceEngine
from market_prediction.models import ModelManager
from market_prediction.preprocessor import MarketPreprocessor

def test_inference_engine_predict_action(mock_model_manager, mock_feature_vector):
    preprocessor = MarketPreprocessor(n_features=130)
    engine = InferenceEngine(mock_model_manager, preprocessor, threshold=0.5)
    
    action = engine.predict_action(mock_feature_vector)
    assert action in [0, 1]

def test_inference_engine_batch_predict(mock_model_manager):
    preprocessor = MarketPreprocessor(n_features=130)
    engine = InferenceEngine(mock_model_manager, preprocessor, threshold=0.5)
    
    batch = np.random.randn(5, 130)
    actions = engine.batch_predict(batch)
    assert actions.shape == (5,)
    assert all(a in [0, 1] for a in actions)
