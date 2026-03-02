import pytest
import pandas as pd
import numpy as np
import torch

@pytest.fixture
def mock_market_data():
    """Generates a mock dataframe for Jane Street competition."""
    n_rows = 100
    n_features = 130
    dates = np.repeat(np.arange(10), 10) # 10 trades per day for 10 days
    
    data = {
        'date': dates,
        'weight': np.random.uniform(0, 1, n_rows),
        'resp': np.random.uniform(-0.1, 0.1, n_rows),
        'ts_id': np.arange(n_rows)
    }
    
    for i in range(n_features):
        data[f'feature_{i}'] = np.random.normal(0, 1, n_rows)
        # Add some NaNs
        nan_indices = np.random.choice(n_rows, size=5, replace=False)
        data[f'feature_{i}'][nan_indices] = np.nan
        
    return pd.DataFrame(data)

@pytest.fixture
def mock_feature_vector():
    """Single 130-feature vector with NaNs."""
    vec = np.random.normal(0, 1, 130)
    vec[0] = np.nan
    return vec

@pytest.fixture
def mock_model_manager():
    from market_prediction.models import ModelManager
    return ModelManager(input_dim=136)
