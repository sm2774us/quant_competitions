import torch
import torch.nn as nn
import os
from typing import List, Optional

class MarketModel(nn.Module):
    """
    Highly optimized multi-layer perceptron for market prediction.
    Aligned with TrendClassifier from old_code.
    """
    def __init__(self, input_dim: int):
        super().__init__()
        hidden_size = input_dim * 2
        
        self.network = nn.Sequential(
            nn.BatchNorm1d(input_dim),
            nn.Linear(input_dim, hidden_size),
            nn.LeakyReLU(0.01),
            nn.Dropout(0.35),
            
            nn.BatchNorm1d(hidden_size),
            nn.Linear(hidden_size, hidden_size),
            nn.LeakyReLU(0.01),
            nn.Dropout(0.4),
            
            nn.BatchNorm1d(hidden_size),
            nn.Linear(hidden_size, hidden_size),
            nn.LeakyReLU(0.01),
            nn.Dropout(0.45),
            
            nn.Linear(hidden_size, 1)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class ModelManager:
    """
    Manager for loading, saving, and managing market models.
    """
    def __init__(self, input_dim: int = 136):
        self.model = MarketModel(input_dim)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    def predict(self, features: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            features = features.to(self.device)
            # Ensure 2D tensor for BatchNorm1d
            if features.ndim == 1:
                features = features.unsqueeze(0)
            logits = self.model(features)
            return torch.sigmoid(logits)

    def load_weights(self, path: str):
        """Loads model weights from a file."""
        if path and os.path.exists(path):
            checkpoint = torch.load(path, map_location=self.device)
            # Handle both state_dict and full checkpoint
            if "state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["state_dict"])
            else:
                self.model.load_state_dict(checkpoint)
            self.model.eval()
