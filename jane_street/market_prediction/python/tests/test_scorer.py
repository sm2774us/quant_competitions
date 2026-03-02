import pandas as pd
import numpy as np
import pytest
from market_prediction.scorer import UtilityScorer

def test_calculate_utility():
    # Create simple data
    data = {
        'date': [0, 0, 1, 1],
        'weight': [1.0, 1.0, 1.0, 1.0],
        'resp': [0.1, 0.2, -0.1, 0.3],
        'action': [1, 1, 1, 1]
    }
    df = pd.DataFrame(data)
    
    # p_0 = 0.1 + 0.2 = 0.3
    # p_1 = -0.1 + 0.3 = 0.2
    # sum_p = 0.5
    # sum_p_sq = 0.3^2 + 0.2^2 = 0.09 + 0.04 = 0.13
    # t = (0.5 / sqrt(0.13)) * sqrt(250 / 2) = (0.5 / 0.3605) * 11.18 = 1.386 * 11.18 = 15.49
    # u = min(15.49, 6) * 0.5 = 6 * 0.5 = 3.0
    
    u = UtilityScorer.calculate_utility(df)
    assert np.isclose(u, 3.0)

def test_calculate_utility_zero():
    data = {
        'date': [0],
        'weight': [1.0],
        'resp': [0.1],
        'action': [0]
    }
    df = pd.DataFrame(data)
    u = UtilityScorer.calculate_utility(df)
    assert u == 0.0

def test_summary_table(mock_market_data):
    df = mock_market_data.copy()
    df['action'] = 1
    summary = UtilityScorer.summary_table(df)
    
    assert "total_profit" in summary
    assert "num_trades_executed" in summary
    assert "utility_score" in summary
    assert "participation_rate" in summary
    assert summary["participation_rate"] == 1.0
