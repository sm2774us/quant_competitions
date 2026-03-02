import pytest
from unittest.mock import MagicMock
from citadel_bot.strategies import ExchangeArbitrage, IndexArbitrage, ShockHandler
from citadel_bot.models import OrderBook, OrderBookEntry, Security, News

@pytest.fixture
def mock_api():
    return MagicMock()

def test_exchange_arbitrage_market(mock_api):
    arb = ExchangeArbitrage(mock_api)
    
    mbook = OrderBook(ticker="WMT-M", bids=[OrderBookEntry(price=100.5, quantity=1000, quantity_filled=0)], asks=[OrderBookEntry(price=101.0, quantity=1000, quantity_filled=0)])
    abook = OrderBook(ticker="WMT-A", bids=[OrderBookEntry(price=99.5, quantity=1000, quantity_filled=0)], asks=[OrderBookEntry(price=100.0, quantity=1000, quantity_filled=0)])
    
    mock_api.get_order_book.side_effect = [mbook, abook]
    
    # mbid (100.5) - aask (100.0) = 0.5
    # TAKER_FEE = (0.0065 + 0.005) * 2 = 0.023
    # 0.5 > 0.023 + 0.02 (BUFFER*2)
    
    arb.run("WMT-M", "WMT-A")
    
    assert mock_api.post_order.call_count >= 2
    mock_api.post_order.assert_any_call("WMT-M", "MARKET", "SELL", 1000)
    mock_api.post_order.assert_any_call("WMT-A", "MARKET", "BUY", 1000)

def test_index_arbitrage_etf_sell(mock_api):
    arb = IndexArbitrage(mock_api)
    
    securities = {
        "ETF": Security(ticker="ETF", position=0, vwap=0, nlv=0, last=300, bid=305, bid_size=100, ask=306, ask_size=100, unrealized=0, realized=0),
        "WMT-M": Security(ticker="WMT-M", position=0, vwap=0, nlv=0, last=100, bid=99, bid_size=100, ask=100, ask_size=100, unrealized=0, realized=0),
        "WMT-A": Security(ticker="WMT-A", position=0, vwap=0, nlv=0, last=100, bid=99, bid_size=100, ask=100, ask_size=100, unrealized=0, realized=0),
        "MMM-M": Security(ticker="MMM-M", position=0, vwap=0, nlv=0, last=100, bid=99, bid_size=100, ask=100, ask_size=100, unrealized=0, realized=0),
        "MMM-A": Security(ticker="MMM-A", position=0, vwap=0, nlv=0, last=100, bid=99, bid_size=100, ask=100, ask_size=100, unrealized=0, realized=0),
        "CAT-M": Security(ticker="CAT-M", position=0, vwap=0, nlv=0, last=100, bid=99, bid_size=100, ask=100, ask_size=100, unrealized=0, realized=0),
        "CAT-A": Security(ticker="CAT-A", position=0, vwap=0, nlv=0, last=100, bid=99, bid_size=100, ask=100, ask_size=100, unrealized=0, realized=0),
    }
    mock_api.get_securities.return_value = securities
    
    # etf.bid (305) - composite_ask (100+100+100=300) = 5
    # TAKER4 + BUFFER = 0.0065 * 5 + 0.01 = 0.0425
    
    arb.run(["WMT", "MMM", "CAT"])
    
    assert mock_api.post_order.call_count >= 4
    mock_api.post_order.assert_any_call("ETF", "MARKET", "SELL", 100)

def test_shock_handler_buy(mock_api):
    handler = ShockHandler(mock_api)
    
    news = [News(tick=10, ticker="WMT", headline="WMT stock jump $10.00", body="")]
    mock_api.get_news.return_value = news
    
    handler.run(11) # elapsed = 1
    
    assert mock_api.post_order.call_count == 2
    mock_api.post_order.assert_any_call("WMT-M", "MARKET", "BUY", 50000)
    mock_api.post_order.assert_any_call("WMT-A", "MARKET", "BUY", 50000)

def test_shock_handler_sell_reversal(mock_api):
    handler = ShockHandler(mock_api)
    
    news = [News(tick=10, ticker="WMT", headline="WMT stock jump $10.00", body="")]
    mock_api.get_news.return_value = news
    
    handler.run(12) # elapsed = 2
    
    assert mock_api.post_order.call_count == 2
    mock_api.post_order.assert_any_call("WMT-M", "MARKET", "SELL", 50000)
    mock_api.post_order.assert_any_call("WMT-A", "MARKET", "SELL", 50000)
