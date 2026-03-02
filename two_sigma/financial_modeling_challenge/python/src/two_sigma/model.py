import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.impute import SimpleImputer
import joblib

class FeatureEngineering(BaseEstimator, TransformerMixin):
    """Custom transformer for feature engineering in financial modeling."""
    
    def __init__(self):
        self.median_values = None
        self.feature_columns = None

    def fit(self, X, y=None):
        """Fits the transformer on the training data."""
        self.feature_columns = [col for col in X.columns if col not in ['id', 'timestamp', 'y']]
        self.median_values = X[self.feature_columns].median()
        return self

    def transform(self, X):
        """Transforms the data using learned feature engineering logic."""
        X_out = X[self.feature_columns].copy()
        
        # Simple feature engineering: null count
        X_out['null_count'] = X_out.isnull().sum(axis=1)
        
        # Fill missing values with median
        X_out = X_out.fillna(self.median_values)
        
        return X_out

class FinancialModel:
    """Robust, OOP-style predictive model for Two Sigma Financial Modeling."""
    
    def __init__(self, alpha=1.0):
        self.pipeline = Pipeline([
            ('engineering', FeatureEngineering()),
            ('imputer', SimpleImputer(strategy='median')),
            ('regressor', Ridge(alpha=alpha))
        ])

    def train(self, train_df: pd.DataFrame):
        """Trains the model on a provided training dataframe."""
        X = train_df.drop(columns=['y'])
        y = train_df['y']
        
        self.pipeline.fit(X, y)
        print("Model training complete.")

    def predict(self, test_df: pd.DataFrame) -> np.ndarray:
        """Generates predictions for a given test dataframe."""
        return self.pipeline.predict(test_df)

    def save(self, path: str):
        """Saves the trained model to a file."""
        joblib.dump(self.pipeline, path)
        print(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str):
        """Loads a trained model from a file."""
        model = cls()
        model.pipeline = joblib.load(path)
        return model
