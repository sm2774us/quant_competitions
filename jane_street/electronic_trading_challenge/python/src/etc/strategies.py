import numpy as np
from typing import List, Optional
from .models import MarketState, Side

class Strategy:
    def execute(self, state: MarketState) -> List[dict]:
        raise NotImplementedError

class BondStrategy(Strategy):
    """Simple market making for BOND at 1000."""
    def execute(self, state: MarketState) -> List[dict]:
        actions = []
        book = state.books.get("BOND")
        if not book:
            return actions

        # Basic market making: buy at 999, sell at 1001
        current_pos = state.positions.get("BOND", 0)
        limit = 100
        
        if current_pos < limit:
            actions.append({"type": "add", "symbol": "BOND", "dir": "BUY", "price": 999, "size": limit - current_pos})
        if current_pos > -limit:
            actions.append({"type": "add", "symbol": "BOND", "dir": "SELL", "price": 1001, "size": limit + current_pos})
            
        return actions

class AdrStrategy(Strategy):
    """VALE/VALBZ ADR Arbitrage."""
    def execute(self, state: MarketState) -> List[dict]:
        actions = []
        valbz_history = state.last_trades.get("VALBZ", [])
        vale_history = state.last_trades.get("VALE", [])

        if len(valbz_history) < 10 or len(vale_history) < 10:
            return actions

        valbz_mean = np.mean(valbz_history[-10:])
        vale_mean = np.mean(vale_history[-10:])
        
        # If VALBZ is significantly higher than VALE
        if valbz_mean - vale_mean >= 2:
            actions.append({"type": "add", "symbol": "VALE", "dir": "BUY", "price": int(vale_mean) + 1, "size": 10})
            actions.append({"type": "convert", "symbol": "VALE", "dir": "SELL", "size": 10})
            actions.append({"type": "add", "symbol": "VALBZ", "dir": "SELL", "price": int(valbz_mean) - 1, "size": 10})
            
        return actions

class EtfStrategy(Strategy):
    """XLF ETF Arbitrage."""
    def execute(self, state: MarketState) -> List[dict]:
        actions = []
        symbols = ["XLF", "BOND", "GS", "MS", "WFC"]
        for sym in symbols:
            if len(state.last_trades.get(sym, [])) < 25:
                return actions

        means = {sym: np.mean(state.last_trades[sym][-25:]) for sym in symbols}
        
        nav = 3 * means["BOND"] + 2 * means["GS"] + 3 * means["MS"] + 2 * means["WFC"]
        xlf_price = 10 * means["XLF"]
        
        # Long ETF Arbitrage
        if xlf_price + 150 < nav:
            actions.append({"type": "add", "symbol": "XLF", "dir": "BUY", "price": int(means["XLF"]) + 1, "size": 100})
            actions.append({"type": "convert", "symbol": "XLF", "dir": "SELL", "size": 100})
            actions.append({"type": "add", "symbol": "BOND", "dir": "SELL", "price": int(means["BOND"]) - 1, "size": 30})
            actions.append({"type": "add", "symbol": "GS", "dir": "SELL", "price": int(means["GS"]) - 1, "size": 20})
            actions.append({"type": "add", "symbol": "MS", "dir": "SELL", "price": int(means["MS"]) - 1, "size": 30})
            actions.append({"type": "add", "symbol": "WFC", "dir": "SELL", "price": int(means["WFC"]) - 1, "size": 20})

        # Short ETF Arbitrage
        elif xlf_price - 150 > nav:
            actions.append({"type": "add", "symbol": "BOND", "dir": "BUY", "price": int(means["BOND"]) + 1, "size": 30})
            actions.append({"type": "add", "symbol": "GS", "dir": "BUY", "price": int(means["GS"]) + 1, "size": 20})
            actions.append({"type": "add", "symbol": "MS", "dir": "BUY", "price": int(means["MS"]) + 1, "size": 30})
            actions.append({"type": "add", "symbol": "WFC", "dir": "BUY", "price": int(means["WFC"]) + 1, "size": 20})
            actions.append({"type": "convert", "symbol": "XLF", "dir": "BUY", "size": 100})
            actions.append({"type": "add", "symbol": "XLF", "dir": "SELL", "price": int(means["XLF"]) - 1, "size": 100})

        return actions
