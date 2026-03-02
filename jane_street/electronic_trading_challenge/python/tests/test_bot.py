import pytest
from unittest.mock import MagicMock, patch
from etc.models import MarketState, OrderBook, BookEntry, Side
from etc.strategies import BondStrategy, AdrStrategy, EtfStrategy
from etc.bot import TradingBot
from etc.exchange import ExchangeConnection

def test_market_state_book_update():
    state = MarketState()
    state.update_book("BOND", [[999, 10], [998, 5]], [[1001, 10], [1002, 5]])
    assert state.books["BOND"].best_bid == 999
    assert state.books["BOND"].best_ask == 1001
    assert state.books["BOND"].mid_price == 1000.0

def test_bond_strategy():
    state = MarketState()
    state.update_book("BOND", [[998, 10]], [[1002, 10]])
    state.positions["BOND"] = 0
    
    strategy = BondStrategy()
    actions = strategy.execute(state)
    
    assert len(actions) == 2
    assert actions[0] == {"type": "add", "symbol": "BOND", "dir": "BUY", "price": 999, "size": 100}
    assert actions[1] == {"type": "add", "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 100}

def test_adr_strategy():
    state = MarketState()
    state.add_trade("VALBZ", 105) # 10 trades
    for _ in range(9): state.add_trade("VALBZ", 105)
    state.add_trade("VALE", 100) # 10 trades
    for _ in range(9): state.add_trade("VALE", 100)
    
    strategy = AdrStrategy()
    actions = strategy.execute(state)
    
    assert len(actions) == 3
    assert any(a["symbol"] == "VALE" and a["dir"] == "BUY" for a in actions)
    assert any(a["type"] == "convert" for a in actions)
    assert any(a["symbol"] == "VALBZ" and a["dir"] == "SELL" for a in actions)

def test_etf_strategy():
    state = MarketState()
    symbols = ["XLF", "BOND", "GS", "MS", "WFC"]
    # XLF price = 100, components = 100 each -> NAV = 300+200+300+200 = 1000. 
    # 10 * XLF = 1000. 
    # If XLF = 80, 10*80=800. 800 + 150 < 1000. (Long XLF)
    for sym in symbols:
        price = 80 if sym == "XLF" else 100
        for _ in range(25): state.add_trade(sym, price)
        
    strategy = EtfStrategy()
    actions = strategy.execute(state)
    assert len(actions) == 6
    assert actions[0]["symbol"] == "XLF"
    assert actions[0]["dir"] == "BUY"

def test_bot_handle_message():
    conn = MagicMock(spec=ExchangeConnection)
    bot = TradingBot(conn, "TEAM")
    
    # Test book message
    bot.handle_message({"type": "book", "symbol": "BOND", "bids": [[999, 10]], "asks": [[1001, 10]]})
    assert bot.state.books["BOND"].best_bid == 999
    
    # Test fill message
    bot.handle_message({"type": "fill", "symbol": "BOND", "dir": "BUY", "size": 10, "price": 999})
    assert bot.state.positions["BOND"] == 10
    assert bot.state.pnl == -9990

def test_bot_run_loop():
    conn = MagicMock(spec=ExchangeConnection)
    # Mock read to return one message then None to break loop
    conn.read.side_effect = [{"type": "book", "symbol": "BOND", "bids": [], "asks": []}, None]
    
    bot = TradingBot(conn, "TEAM")
    bot.run()
    
    conn.connect.assert_called_once()
    conn.send_hello.assert_called_with("TEAM")
    assert conn.read.call_count == 2
