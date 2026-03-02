from typing import List, Optional
from pydantic import BaseModel, Field

class Security(BaseModel):
    ticker: str
    position: int
    vwap: float
    nlv: float
    last: float
    bid: float
    bid_size: int
    ask: float
    ask_size: int
    unrealized: float
    realized: float

class OrderBookEntry(BaseModel):
    price: float
    quantity: int
    quantity_filled: int

class OrderBook(BaseModel):
    ticker: str
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]

class News(BaseModel):
    tick: int
    ticker: str
    headline: str
    body: str

class CaseStatus(BaseModel):
    tick: int
    status: str

class Limit(BaseModel):
    ticker: str
    gross_limit: int
    net_limit: int
    gross: int
    net: int

class OrderResponse(BaseModel):
    order_id: int
    status: str
    ticker: str
    type: str
    action: str
    quantity: int
    price: Optional[float] = None
    vwap: Optional[float] = None
