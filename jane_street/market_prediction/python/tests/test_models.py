import torch
import torch.nn as nn
import numpy as np
from market_prediction.models import MarketModel, ModelManager

def test_market_model_forward():
    input_dim = 136
    model = MarketModel(input_dim)
    
    x = torch.randn(8, input_dim) # batch of 8
    out = model(x)
    assert out.shape == (8, 1)

def test_model_manager_predict():
    manager = ModelManager(input_dim=136)
    
    # Single sample (1D)
    x1 = torch.randn(136)
    out1 = manager.predict(x1)
    assert out1.shape == (1, 1)
    assert 0 <= out1.item() <= 1
    
    # Batch (2D)
    x2 = torch.randn(4, 136)
    out2 = manager.predict(x2)
    assert out2.shape == (4, 1)
    assert (out2 >= 0).all() and (out2 <= 1).all()

def test_model_manager_load_weights(tmp_path):
    manager = ModelManager(input_dim=136)
    path = tmp_path / "model.pt"
    torch.save(manager.model.state_dict(), path)
    
    # This should now succeed without unpickling error
    manager.load_weights(str(path))
