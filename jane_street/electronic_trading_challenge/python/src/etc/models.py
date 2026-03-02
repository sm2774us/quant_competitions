from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    order_id: int
    symbol: str
    side: Side
    price: int
    size: int
    filled: int = 0

@dataclass
class BookEntry:
    price: int
    size: int

@dataclass
class OrderBook:
    symbol: str
    bids: List[BookEntry] = field(default_factory=list)
    asks: List[BookEntry] = field(default_factory=list)

    @property
    def mid_price(self) -> Optional[float]:
        if not self.bids or not self.asks:
            return None
        return (self.bids[0].price + self.asks[0].price) / 2.0

    @property
    def best_bid(self) -> Optional[int]:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Optional[int]:
        return self.asks[0].price if self.asks else None

class MarketState:
    def __init__(self):
        self.books: Dict[str, OrderBook] = {}
        self.positions: Dict[str, int] = {}
        self.last_trades: Dict[str, List[int]] = {}  # History of trade prices
        self.orders: Dict[int, Order] = {}
        self.pnl: int = 0

    def update_book(self, symbol: str, bids: List[List[int]], asks: List[List[int]]):
        if symbol not in self.books:
            self.books[symbol] = OrderBook(symbol)
        self.books[symbol].bids = [BookEntry(p, s) for p, s in bids]
        self.books[symbol].asks = [BookEntry(p, s) for p, s in asks]

    def add_trade(self, symbol: str, price: int):
        if symbol not in self.last_trades:
            self.last_trades[symbol] = []
        self.last_trades[symbol].append(price)
        if len(self.last_trades[symbol]) > 100:
            self.last_trades[symbol].pop(0)

    def update_position(self, symbol: str, change: int):
        self.positions[symbol] = self.positions.get(symbol, 0) + change
