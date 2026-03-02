import numpy as np
import pandas as pd
from typing import List, Dict

class UtilityScorer:
    """
    Implements the Jane Street Utility Score calculation.
    """
    @staticmethod
    def calculate_utility(df: pd.DataFrame) -> float:
        """
        Calculates the utility score from a DataFrame containing:
        - date: unique date IDs
        - weight: trade weight
        - resp: trade return
        - action: binary decision (0 or 1)
        """
        # Calculate daily profit: p_i = sum(weight * resp * action)
        df['profit'] = df['weight'] * df['resp'] * df['action']
        p_i = df.groupby('date')['profit'].sum()
        
        # Calculate t statistic
        sum_p_i = p_i.sum()
        sum_p_i_sq = (p_i ** 2).sum()
        num_dates = p_i.nunique()
        
        if sum_p_i_sq == 0:
            return 0.0
            
        t = (sum_p_i / np.sqrt(sum_p_i_sq)) * np.sqrt(250 / num_dates)
        
        # Calculate final utility
        u = min(max(t, 0), 6) * sum_p_i
        
        return float(u)

    @staticmethod
    def summary_table(df: pd.DataFrame) -> Dict[str, float]:
        """
        Returns a summary of trading performance.
        """
        profit = (df['weight'] * df['resp'] * df['action']).sum()
        num_trades = df['action'].sum()
        utility = UtilityScorer.calculate_utility(df)
        
        return {
            "total_profit": profit,
            "num_trades_executed": num_trades,
            "utility_score": utility,
            "participation_rate": num_trades / len(df) if len(df) > 0 else 0
        }
