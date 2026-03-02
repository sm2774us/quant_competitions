from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field

class Order(BaseModel):
    type: Literal["add", "cancel", "convert"]
    order_id: int
    symbol: Optional[str] = None
    dir: Optional[Literal["BUY", "SELL"]] = None
    price: Optional[int] = None
    size: Optional[int] = None

class BookLevel(BaseModel):
    price: int
    size: int

class BookMessage(BaseModel):
    type: Literal["book"]
    symbol: str
    buy: List[List[int]]  # [price, size]
    sell: List[List[int]]

class FillMessage(BaseModel):
    type: Literal["fill"]
    order_id: int
    symbol: str
    dir: Literal["BUY", "SELL"]
    price: int
    size: int

class AckMessage(BaseModel):
    type: Literal["ack"]
    order_id: int

class RejectMessage(BaseModel):
    type: Literal["reject"]
    order_id: int
    error: str

class ErrorMessage(BaseModel):
    type: Literal["error"]
    error: str

class HelloMessage(BaseModel):
    type: Literal["hello"]
    symbols: List[dict]

class TradeMessage(BaseModel):
    type: Literal["trade"]
    symbol: str
    price: int
    size: int

ExchangeMessage = Union[
    BookMessage, FillMessage, AckMessage, RejectMessage, ErrorMessage, HelloMessage, TradeMessage
]
