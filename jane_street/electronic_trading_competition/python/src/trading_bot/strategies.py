from typing import List, Dict, Optional
from .models import Order, BookMessage
import numpy as np

class TradingStrategy:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.position = 0

    def update_book(self, book: BookMessage, order_id_counter: int) -> List[Order]:
        return []

    def update_fill(self, dir: str, size: int):
        if dir == "BUY":
            self.position += size
        else:
            self.position -= size

class BondStrategy(TradingStrategy):
    def __init__(self, symbol: str = "BOND"):
        super().__init__(symbol)
        self.fair_price = 1000
        self.limit = 100

    def update_book(self, book: BookMessage, order_id_counter: int) -> List[Order]:
        orders = []
        # Simple market making around fair price
        # Buy below 1000, sell above 1000
        for price, size in book.sell:
            if price < self.fair_price:
                buy_size = min(size, self.limit - self.position)
                if buy_size > 0:
                    orders.append(Order(type="add", order_id=order_id_counter, symbol=self.symbol, dir="BUY", price=price, size=buy_size))
                    order_id_counter += 1

        for price, size in book.buy:
            if price > self.fair_price:
                sell_size = min(size, self.position + self.limit)
                if sell_size > 0:
                    orders.append(Order(type="add", order_id=order_id_counter, symbol=self.symbol, dir="SELL", price=price, size=sell_size))
                    order_id_counter += 1
        
        # Pennying logic: if we have room, bid 999 and ask 1001
        if self.position < self.limit:
            orders.append(Order(type="add", order_id=order_id_counter, symbol=self.symbol, dir="BUY", price=999, size=1))
            order_id_counter += 1
        if self.position > -self.limit:
            orders.append(Order(type="add", order_id=order_id_counter, symbol=self.symbol, dir="SELL", price=1001, size=1))
            order_id_counter += 1

        return orders

class ADRStrategy(TradingStrategy):
    def __init__(self, vale_symbol: str = "VALE", valbz_symbol: str = "VALBZ"):
        super().__init__(vale_symbol)
        self.vale_symbol = vale_symbol
        self.valbz_symbol = valbz_symbol
        self.vale_pos = 0
        self.valbz_pos = 0
        self.vale_book: Optional[BookMessage] = None
        self.valbz_book: Optional[BookMessage] = None
        self.conversion_cost = 10
        self.limit = 10

    def update_book_vale(self, book: BookMessage):
        self.vale_book = book

    def update_book_valbz(self, book: BookMessage):
        self.valbz_book = book

    def calculate_orders(self, order_id_counter: int) -> List[Order]:
        if not self.vale_book or not self.valbz_book:
            return []
        
        orders = []
        # ADR Arbitrage: Buy cheap on one, sell expensive on other, convert
        if self.vale_book.sell and self.valbz_book.buy:
            vale_ask = self.vale_book.sell[0][0]
            valbz_bid = self.valbz_book.buy[0][0]
            if valbz_bid - vale_ask > self.conversion_cost:
                size = min(self.vale_book.sell[0][1], self.valbz_book.buy[0][1], self.limit - self.vale_pos, self.valbz_pos + self.limit)
                if size > 0:
                    orders.append(Order(type="add", order_id=order_id_counter, symbol=self.vale_symbol, dir="BUY", price=vale_ask, size=size))
                    order_id_counter += 1
                    orders.append(Order(type="convert", order_id=order_id_counter, symbol=self.vale_symbol, dir="SELL", size=size))
                    order_id_counter += 1
                    orders.append(Order(type="add", order_id=order_id_counter, symbol=self.valbz_symbol, dir="SELL", price=valbz_bid, size=size))
                    order_id_counter += 1

        return orders

class MACDStrategy(TradingStrategy):
    def __init__(self, symbol: str):
        super().__init__(symbol)
        self.prices = []
        self.ema12 = None
        self.ema20 = None
        self.limit = 50

    def update_price(self, price: int, order_id_counter: int) -> List[Order]:
        self.prices.append(price)
        if len(self.prices) < 20:
            return []
        
        if self.ema12 is None:
            self.ema12 = np.mean(self.prices[-12:])
            self.ema20 = np.mean(self.prices[-20:])
        else:
            self.ema12 = (price - self.ema12) * (2/13) + self.ema12
            self.ema20 = (price - self.ema20) * (2/21) + self.ema20
        
        macd = self.ema12 - self.ema20
        orders = []
        if macd > 0.5 and self.position < self.limit:
            orders.append(Order(type="add", order_id=order_id_counter, symbol=self.symbol, dir="BUY", price=price + 1, size=1))
        elif macd < -0.5 and self.position > -self.limit:
            orders.append(Order(type="add", order_id=order_id_counter, symbol=self.symbol, dir="SELL", price=price - 1, size=1))
        
        return orders
