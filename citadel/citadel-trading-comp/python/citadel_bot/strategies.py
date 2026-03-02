from typing import Dict, List, Tuple
import logging
from .models import Security, OrderBook, News, OrderResponse
from .api import TradingApi

logger = logging.getLogger(__name__)

# Constants from template
MAIN_TAKER = 0.0065
MAIN_MAKER = 0.002
ALT_TAKER = 0.005
ALT_MAKER = 0.0035
TAKER_FEE = (MAIN_TAKER + ALT_TAKER) * 2
BUFFER = 0.01
TAKER4 = MAIN_TAKER * 5
MAX_QUANTITY = 50000

class ExchangeArbitrage:
    def __init__(self, api: TradingApi):
        self.api = api

    def run(self, mticker: str, aticker: str):
        try:
            mbook = self.api.get_order_book(mticker)
            abook = self.api.get_order_book(aticker)

            if not mbook.bids or not mbook.asks or not abook.bids or not abook.asks:
                return

            mbid = mbook.bids[0].price
            mask = mbook.asks[0].price
            abid = abook.bids[0].price
            aask = abook.asks[0].price

            m_bid_room = sum(b.quantity - b.quantity_filled for b in mbook.bids if b.price == mbid)
            m_ask_room = sum(a.quantity - a.quantity_filled for a in mbook.asks if a.price == mask)
            a_bid_room = sum(b.quantity - b.quantity_filled for b in abook.bids if b.price == abid)
            a_ask_room = sum(a.quantity - a.quantity_filled for a in abook.asks if a.price == aask)

            # Market Arbitrage
            if mbid - aask > TAKER_FEE + BUFFER * 2:
                qty = min(m_bid_room, a_ask_room, MAX_QUANTITY)
                if qty > 0:
                    self.api.post_order(mticker, "MARKET", "SELL", qty)
                    self.api.post_order(aticker, "MARKET", "BUY", qty)
                    logger.info(f"Market Arb: Sell {mticker} @ {mbid}, Buy {aticker} @ {aask}, Qty: {qty}")
            elif abid - mask > TAKER_FEE + BUFFER * 2:
                qty = min(a_bid_room, m_ask_room, MAX_QUANTITY)
                if qty > 0:
                    self.api.post_order(aticker, "MARKET", "SELL", qty)
                    self.api.post_order(mticker, "MARKET", "BUY", qty)
                    logger.info(f"Market Arb: Sell {aticker} @ {abid}, Buy {mticker} @ {mask}, Qty: {qty}")

            # Limit Arbitrage
            if mbid - aask > BUFFER:
                qty = min(m_bid_room, a_ask_room, MAX_QUANTITY)
                if qty > 0:
                    self.api.post_order(mticker, "LIMIT", "SELL", qty, mbid)
                    self.api.post_order(aticker, "LIMIT", "BUY", qty, aask)
            elif abid - mask > BUFFER:
                qty = min(a_bid_room, m_ask_room, MAX_QUANTITY)
                if qty > 0:
                    self.api.post_order(aticker, "LIMIT", "SELL", qty, abid)
                    self.api.post_order(mticker, "LIMIT", "BUY", qty, mask)

        except Exception as e:
            logger.error(f"ExchangeArbitrage error: {e}")

class IndexArbitrage:
    def __init__(self, api: TradingApi):
        self.api = api

    def run(self, tickers: List[str]):
        try:
            securities = self.api.get_securities()
            if "ETF" not in securities:
                return

            etf = securities["ETF"]
            best_bids = {}
            best_bids_q = {}
            best_asks = {}
            best_asks_q = {}

            for t in tickers:
                tm = f"{t}-M"
                ta = f"{t}-A"
                if tm not in securities or ta not in securities:
                    continue
                
                sm = securities[tm]
                sa = securities[ta]

                if sm.bid >= sa.bid:
                    best_bids[tm] = sm.bid
                    best_bids_q[tm] = sm.bid_size
                else:
                    best_bids[ta] = sa.bid
                    best_bids_q[ta] = sa.bid_size

                if sm.ask <= sa.ask:
                    best_asks[tm] = sm.ask
                    best_asks_q[tm] = sm.ask_size
                else:
                    best_asks[ta] = sa.ask
                    best_asks_q[ta] = sa.ask_size

            if not best_bids or not best_asks:
                return

            composite_bid = sum(best_bids.values())
            composite_bid_q = min(best_bids_q.values())
            composite_ask = sum(best_asks.values())
            composite_ask_q = min(best_asks_q.values())

            if etf.bid - composite_ask > TAKER4 + BUFFER:
                qty = min(etf.bid_size, composite_ask_q, MAX_QUANTITY)
                if qty > 0:
                    self.api.post_order("ETF", "MARKET", "SELL", qty)
                    for t_sym in best_asks:
                        self.api.post_order(t_sym, "MARKET", "BUY", qty)
                    logger.info(f"Index Arb: Sell ETF @ {etf.bid}, Buy Components @ {composite_ask}, Qty: {qty}")
            elif composite_bid - etf.ask > TAKER4 + BUFFER:
                qty = min(etf.ask_size, composite_bid_q, MAX_QUANTITY)
                if qty > 0:
                    for t_sym in best_bids:
                        self.api.post_order(t_sym, "MARKET", "SELL", qty)
                    self.api.post_order("ETF", "MARKET", "BUY", qty)
                    logger.info(f"Index Arb: Sell Components @ {composite_bid}, Buy ETF @ {etf.ask}, Qty: {qty}")

        except Exception as e:
            logger.error(f"IndexArbitrage error: {e}")

class ShockHandler:
    def __init__(self, api: TradingApi):
        self.api = api
        self.quantity = 50000

    def run(self, current_tick: int):
        try:
            news_list = self.api.get_news()
            for news in news_list:
                elapsed = current_tick - news.tick
                if elapsed > 2:
                    continue

                try:
                    amount_str = news.headline[-6:].replace('$', '')
                    amount = float(amount_str)
                except ValueError:
                    continue

                m_ticker = f"{news.ticker}-M"
                a_ticker = f"{news.ticker}-A"

                if elapsed < 2:
                    if amount > MAIN_TAKER + BUFFER * 2:
                        self.api.post_order(m_ticker, "MARKET", "BUY", self.quantity)
                        self.api.post_order(a_ticker, "MARKET", "BUY", self.quantity)
                    elif -amount > MAIN_TAKER + BUFFER * 2:
                        self.api.post_order(m_ticker, "MARKET", "SELL", self.quantity)
                        self.api.post_order(a_ticker, "MARKET", "SELL", self.quantity)
                elif elapsed == 2:
                    if amount > MAIN_TAKER + BUFFER * 2:
                        self.api.post_order(m_ticker, "MARKET", "SELL", self.quantity)
                        self.api.post_order(a_ticker, "MARKET", "SELL", self.quantity)
                    elif -amount > MAIN_TAKER + BUFFER * 2:
                        self.api.post_order(m_ticker, "MARKET", "BUY", self.quantity)
                        self.api.post_order(a_ticker, "MARKET", "BUY", self.quantity)

        except Exception as e:
            logger.error(f"ShockHandler error: {e}")
