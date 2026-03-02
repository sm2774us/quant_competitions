import pytest
from unittest.mock import MagicMock, patch
from trading_bot.models import Direction, Order, BookUpdate, FillUpdate
from trading_bot.strategy import Strategy
from trading_bot.exchange import Exchange
from trading_bot.bot import TradingBot

# Tests for models
def test_order_model():
    order = Order(1, "BOND", Direction::BUY, 999, 10)
    assert order.order_id == 1
    assert order.symbol == "BOND"
    assert order.dir == Direction::BUY
    assert order.price == 999
    assert order.size == 10

# Tests for strategy
def test_strategy_on_hello():
    strategy = Strategy()
    strategy.on_hello([{"symbol": "BOND", "position": 10}])
    assert strategy.positions["BOND"] == 10

def test_strategy_on_fill():
    strategy = Strategy()
    strategy.positions["BOND"] = 10
    fill = FillUpdate(1, "BOND", Direction::BUY, 999, 5)
    strategy.on_fill(fill)
    assert strategy.positions["BOND"] == 15
    
    fill_sell = FillUpdate(2, "BOND", Direction::SELL, 1001, 3)
    strategy.on_fill(fill_sell)
    assert strategy.positions["BOND"] == 12

def test_bond_strategy_buy():
    strategy = Strategy()
    strategy.positions["BOND"] = 0
    # Someone selling BOND for 998 (we should buy)
    book = BookUpdate(symbol="BOND", sell=[(998, 5)], buy=[])
    orders = strategy.decide(book)
    
    # Orders will include the buy at 998 AND the passive orders
    buy_orders = [o for o in orders if o.price == 998]
    assert len(buy_orders) == 1
    assert buy_orders[0].dir == Direction::BUY
    assert buy_orders[0].size == 5

def test_bond_strategy_sell():
    strategy = Strategy()
    strategy.positions["BOND"] = 0
    # Someone buying BOND for 1002 (we should sell)
    book = BookUpdate(symbol="BOND", sell=[], buy=[(1002, 5)])
    orders = strategy.decide(book)
    
    sell_orders = [o for o in orders if o.price == 1002]
    assert len(sell_orders) == 1
    assert sell_orders[0].dir == Direction::SELL
    assert sell_orders[0].size == 5

def test_bond_strategy_passive():
    strategy = Strategy()
    strategy.positions["BOND"] = 0
    book = BookUpdate(symbol="BOND", sell=[], buy=[])
    orders = strategy.decide(book)
    
    # Should place passive buy at 999 and sell at 1001
    assert any(o.price == 999 and o.dir == Direction::BUY for o in orders)
    assert any(o.price == 1001 and o.dir == Direction::SELL for o in orders)

# Tests for Exchange
@patch('socket.socket')
def test_exchange_connect(mock_socket):
    exchange = Exchange("localhost", 25000)
    exchange.connect()
    mock_socket.return_value.connect.assert_called_with(("localhost", 25000))

@patch('socket.socket')
def test_exchange_send(mock_socket):
    exchange = Exchange("localhost", 25000)
    exchange.socket = mock_socket
    exchange.send({"type": "hello"})
    mock_socket.sendall.assert_called()

# Tests for Bot
@patch('trading_bot.bot.Exchange')
def test_bot_handle_message_hello(mock_exchange_class):
    bot = TradingBot("localhost", 25000, "TEAM")
    bot.handle_message({"type": "hello", "symbols": [{"symbol": "BOND", "position": 0}]})
    assert bot.strategy.positions["BOND"] == 0

@patch('trading_bot.bot.Exchange')
def test_bot_handle_message_book(mock_exchange_class):
    bot = TradingBot("localhost", 25000, "TEAM")
    mock_exchange = mock_exchange_class.return_value
    
    # Mock strategy to return one order
    bot.strategy.decide = MagicMock(return_value=[Order(1, "BOND", Direction::BUY, 999, 1)])
    
    bot.handle_message({"type": "book", "symbol": "BOND", "buy": [], "sell": []})
    
    # Check if exchange.send was called with the order
    mock_exchange.send.assert_called()
    sent_msg = mock_exchange.send.call_args[0][0]
    assert sent_msg["type"] == "add"
    assert sent_msg["price"] == 999

@patch('trading_bot.bot.Exchange')
def test_bot_handle_message_fill(mock_exchange_class):
    bot = TradingBot("localhost", 25000, "TEAM")
    bot.strategy.positions["BOND"] = 0
    bot.handle_message({
        "type": "fill", 
        "order_id": 1, 
        "symbol": "BOND", 
        "dir": "BUY", 
        "price": 999, 
        "size": 10
    })
    assert bot.strategy.positions["BOND"] == 10
