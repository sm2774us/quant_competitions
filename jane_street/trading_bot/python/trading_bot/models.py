from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple, Dict

class Direction(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    order_id: int
    symbol: str
    dir: Direction
    price: int
    size: int

@dataclass
class BookUpdate:
    symbol: str
    buy: List[Tuple[int, int]] = field(default_factory=list)
    sell: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class FillUpdate:
    order_id: int
    symbol: str
    dir: Direction
    price: int
    size: int

@dataclass
class Position:
    symbol: str
    position: int
