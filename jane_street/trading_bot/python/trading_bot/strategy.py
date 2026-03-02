from typing import List, Dict, Optional
from .models import BookUpdate, Direction, Order, Position, FillUpdate

class Strategy:
    def __init__(self):
        self.positions: Dict[str, int] = {}
        self.order_id_counter = 0
        self.limits = {"BOND": 100, "VALBZ": 10, "VALE": 10, "GS": 100, "MS": 100, "WFC": 100, "XLF": 100}

    def next_order_id(self) -> int:
        self.order_id_counter += 1
        return self.order_id_counter

    def on_hello(self, symbols: List[Dict[str, any]]):
        for s in symbols:
            self.positions[s['symbol']] = s['position']

    def on_fill(self, fill: FillUpdate):
        if fill.symbol not in self.positions:
            self.positions[fill.symbol] = 0
        
        delta = fill.size if fill.dir == Direction.BUY else -fill.size
        self.positions[fill.symbol] += delta

    def decide(self, book: BookUpdate) -> List[Order]:
        orders = []
        symbol = book.symbol
        
        if symbol == "BOND":
            orders.extend(self._bond_strategy(book))
        
        return orders

    def _bond_strategy(self, book: BookUpdate) -> List[Order]:
        orders = []
        symbol = "BOND"
        pos = self.positions.get(symbol, 0)
        limit = self.limits.get(symbol, 100)

        # BOND always has a fair price of 1000.
        # Buy if someone sells for < 1000
        # Sell if someone buys for > 1000
        
        # Check sell orders in book (someone is selling, we can buy)
        for price, size in book.sell:
            if price < 1000:
                buy_size = min(size, limit - pos)
                if buy_size > 0:
                    orders.append(Order(self.next_order_id(), symbol, Direction.BUY, price, buy_size))
                    pos += buy_size

        # Check buy orders in book (someone is buying, we can sell)
        for price, size in book.buy:
            if price > 1000:
                sell_size = min(size, limit + pos)
                if sell_size > 0:
                    orders.append(Order(self.next_order_id(), symbol, Direction.SELL, price, sell_size))
                    pos -= sell_size

        # Passive orders
        if pos < limit:
            orders.append(Order(self.next_order_id(), symbol, Direction.BUY, 999, limit - pos))
        if pos > -limit:
            orders.append(Order(self.next_order_id(), symbol, Direction.SELL, 1001, limit + pos))

        return orders
