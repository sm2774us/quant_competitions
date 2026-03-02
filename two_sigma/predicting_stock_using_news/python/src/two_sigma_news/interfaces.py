from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class IDataLoader(ABC):
    @abstractmethod
    def load_market_data(self, path: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def load_news_data(self, path: str) -> pd.DataFrame:
        pass

class IPreprocessor(ABC):
    @abstractmethod
    def process(self, market_df: pd.DataFrame, news_df: pd.DataFrame) -> pd.DataFrame:
        pass

class IModel(ABC):
    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray):
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        pass

class IEvaluator(ABC):
    @abstractmethod
    def evaluate(self, predictions: np.ndarray, targets: np.ndarray, universe: np.ndarray) -> float:
        pass
