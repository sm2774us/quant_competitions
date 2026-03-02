import pandas as pd
import numpy as np
from sklearn.metrics import r2_score

class Observation:
    """Represents a single observation in the financial modeling challenge."""
    def __init__(self, train, target, features):
        self.train = train
        self.target = target
        self.features = features

class Environment:
    """Mimics the Kaggle environment for the Two Sigma challenge."""
    
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.timestamp = 0
        self.fullset = pd.read_hdf(data_path, 'train')
        self.unique_timestamps = self.fullset['timestamp'].unique()
        
        # Split data: first half for training, second half for testing
        n = len(self.unique_timestamps)
        self.split_idx = n // 2
        self.current_idx = self.split_idx
        
        self.train = self.fullset[self.fullset['timestamp'] < self.unique_timestamps[self.split_idx]]
        self.test = self.fullset[self.fullset['timestamp'] >= self.unique_timestamps[self.split_idx]]
        
        self.y_test_full = self.test['y'].values
        self.y_pred_full = []
        self.temp_test_y = None

    def reset(self):
        """Resets the environment and returns the first observation."""
        self.current_idx = self.split_idx
        self.y_pred_full = []
        return self._get_observation()

    def step(self, target_df):
        """Submits predictions and returns the next observation, reward, done, and info."""
        if self.current_idx >= len(self.unique_timestamps):
            return None, 0, True, {"public_score": self._calculate_score()}

        # Store predictions
        self.y_pred_full.extend(target_df['y'].values)
        
        # Move to next timestamp
        self.current_idx += 1
        
        done = self.current_idx >= len(self.unique_timestamps)
        reward = 0  # Placeholder for step-wise reward if needed
        
        if done:
            info = {"public_score": self._calculate_score()}
            return None, reward, True, info
        
        observation = self._get_observation()
        return observation, reward, False, {}

    def _get_observation(self):
        """Internal helper to create an Observation object for the current timestamp."""
        ts = self.unique_timestamps[self.current_idx]
        subset = self.test[self.test['timestamp'] == ts]
        
        target = subset.loc[:, ['id', 'y']].copy().reset_index(drop=True)
        self.temp_test_y = target['y'].values
        target['y'] = 0.0  # Reset target for submission
        
        features = subset.drop(columns=['y']).reset_index(drop=True)
        return Observation(self.train, target, features)

    def _calculate_score(self):
        """Calculates the R-score evaluation metric."""
        if not self.y_pred_full:
            return 0
        
        y_true = self.y_test_full[:len(self.y_pred_full)]
        y_pred = np.array(self.y_pred_full)
        
        r2 = r2_score(y_true, y_pred)
        return np.sign(r2) * np.sqrt(np.abs(r2))

def make(data_path: str):
    """Factory function to create the environment."""
    return Environment(data_path)
