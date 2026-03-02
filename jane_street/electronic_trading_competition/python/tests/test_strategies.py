import pytest
from trading_bot.strategies import BondStrategy, ADRStrategy, MACDStrategy
from trading_bot.models import BookMessage

def test_bond_strategy_buy():
    strat = BondStrategy()
    book = BookMessage(type="book", symbol="BOND", buy=[], sell=[[998, 10]])
    orders = strat.update_book(book, 1)
    assert any(o.dir == "BUY" and o.price == 998 for o in orders)

def test_bond_strategy_sell():
    strat = BondStrategy()
    book = BookMessage(type="book", symbol="BOND", buy=[[1002, 10]], sell=[])
    orders = strat.update_book(book, 1)
    assert any(o.dir == "SELL" and o.price == 1002 for o in orders)

def test_bond_strategy_pennying():
    strat = BondStrategy()
    book = BookMessage(type="book", symbol="BOND", buy=[], sell=[])
    orders = strat.update_book(book, 1)
    assert any(o.dir == "BUY" and o.price == 999 for o in orders)
    assert any(o.dir == "SELL" and o.price == 1001 for o in orders)

def test_adr_strategy_no_orders():
    strat = ADRStrategy()
    assert strat.calculate_orders(1) == []

def test_adr_strategy_arbitrage():
    strat = ADRStrategy()
    vale_book = BookMessage(type="book", symbol="VALE", buy=[], sell=[[4000, 10]])
    valbz_book = BookMessage(type="book", symbol="VALBZ", buy=[[4015, 10]], sell=[])
    strat.update_book_vale(vale_book)
    strat.update_book_valbz(valbz_book)
    orders = strat.calculate_orders(1)
    assert len(orders) == 3
    assert orders[0].symbol == "VALE" and orders[0].dir == "BUY"
    assert orders[1].type == "convert"
    assert orders[2].symbol == "VALBZ" and orders[2].dir == "SELL"

def test_macd_strategy():
    strat = MACDStrategy("AAPL")
    # Simulate a rising trend
    for i in range(100, 125):
        orders = strat.update_price(i, 1)
    assert len(orders) > 0
    assert orders[0].dir == "BUY"
