import pandas as pd
import numpy as np
from .interfaces import IPreprocessor, IDataLoader

class TwoSigmaDataLoader(IDataLoader):
    def load_market_data(self, path: str) -> pd.DataFrame:
        if path.endswith('.pkl'):
            return pd.read_pickle(path)
        return pd.read_csv(path)

    def load_news_data(self, path: str) -> pd.DataFrame:
        if path.endswith('.pkl'):
            return pd.read_pickle(path)
        return pd.read_csv(path)

class TwoSigmaPreprocessor(IPreprocessor):
    def __init__(self, train_cutoff: str = '2010-01-01'):
        self.train_cutoff = pd.to_datetime(train_cutoff)

    def process(self, market_df: pd.DataFrame, news_df: pd.DataFrame) -> pd.DataFrame:
        # Market Processing
        market_df = market_df.copy()
        market_df['time'] = pd.to_datetime(market_df['time'])
        
        # Outlier handling
        market_df['dailychange'] = market_df['close'] / market_df['open']
        market_df.loc[market_df['dailychange'] < 0.33, 'open'] = market_df['close']
        market_df.loc[market_df['dailychange'] > 2.0, 'close'] = market_df['open']
        
        # Filter by cutoff
        market_df = market_df[market_df['time'] >= self.train_cutoff].reset_index(drop=True)
        
        # News Processing
        news_df = news_df.copy()
        news_df['time'] = pd.to_datetime(news_df['time'])
        
        # Vectorized news aggregation (by day and assetName)
        # Assuming assetNames are shared
        news_agg = news_df.groupby(['time', 'assetName']).agg({
            'sentimentNegative': 'mean',
            'sentimentNeutral': 'mean',
            'sentimentPositive': 'mean',
            'relevance': 'mean',
            'wordCount': 'mean'
        }).reset_index()
        
        # Merge
        merged = pd.merge(market_df, news_agg, on=['time', 'assetName'], how='left')
        merged = merged.fillna(0)
        
        return merged
