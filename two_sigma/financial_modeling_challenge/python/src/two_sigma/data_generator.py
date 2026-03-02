import pandas as pd
import numpy as np
import os

class DataGenerator:
    """Generates synthetic data for the Two Sigma Financial Modeling Challenge."""
    
    def __init__(self, n_samples=1000, n_features=100, n_instruments=50):
        self.n_samples = n_samples
        self.n_features = n_features
        self.n_instruments = n_instruments

    def generate(self, output_path: str):
        """Generates a synthetic dataset and saves it as an HDF5 file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        timestamps = np.arange(self.n_samples // self.n_instruments)
        ids = np.arange(self.n_instruments)
        
        data = []
        for t in timestamps:
            for i in ids:
                row = {
                    'id': i,
                    'timestamp': t,
                    'y': np.random.normal(0, 0.02)
                }
                for f in range(self.n_features):
                    row[f'technical_{f}'] = np.random.normal(0, 1)
                data.append(row)
        
        df = pd.DataFrame(data)
        df.to_hdf(output_path, key='train', mode='w')
        print(f"Generated synthetic data at {output_path}")

if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate("data/train.h5")
