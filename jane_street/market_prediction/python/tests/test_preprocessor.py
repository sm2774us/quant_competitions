import numpy as np
import pytest
from market_prediction.preprocessor import MarketPreprocessor

def test_preprocessor_init():
    prep = MarketPreprocessor(n_features=10, window_size=5)
    assert prep.n_features == 10
    assert prep.window_size == 5
    assert len(prep.window) == 0

def test_preprocessor_transform(mock_feature_vector):
    prep = MarketPreprocessor(n_features=130, window_size=10)
    
    # First transform
    res1 = prep.transform(mock_feature_vector)
    assert not np.isnan(res1).any()
    assert len(res1) == 136 # 130 + 6 interactions
    assert len(prep.window) == 1
    
    # Second transform (updates stats)
    res2 = prep.transform(mock_feature_vector)
    assert not np.isnan(res2).any()
    assert len(res2) == 136
    assert len(prep.window) == 2

def test_nan_handling():
    # Must use at least 123 features because interactions use index 122
    n_feat = 130
    prep = MarketPreprocessor(n_features=n_feat, window_size=5)
    # Set initial medians
    prep.medians = np.zeros((2, n_feat))
    prep.medians[0, 1] = 20.0 # side -1, feature 1
    
    prep.scaler_mean = np.zeros(n_feat - 1 + 6)
    prep.scaler_scale = np.ones(n_feat - 1 + 6)
    
    x = np.full(n_feat, 0.0)
    x[0] = -1.0
    x[1] = np.nan
    
    res = prep.transform(x)
    
    # The nan should have been replaced by the median (20.0)
    assert res[0] == -1.0
    # res[1] is normalized (20.0 - 0) / (1.0 + 1e-8) = 19.9999998...
    assert np.allclose(res[1], 20.0)
    assert len(res) == 136

def test_preprocessor_persistence():
    prep = MarketPreprocessor(n_features=130)
    # Use a real path or mock
    import os
    dummy_path = "dummy_params.json"
    prep.save_state(dummy_path)
    try:
        prep.load_state(dummy_path)
    finally:
        if os.path.exists(dummy_path):
            os.remove(dummy_path)
