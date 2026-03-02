from typing import Dict, Any, List
from .exchange import Exchange
from .strategy import Strategy
from .models import BookUpdate, Direction, Order, FillUpdate
import logging

class TradingBot:
    def __init__(self, host: str, port: int, team: str):
        self.exchange = Exchange(host, port)
        self.strategy = Strategy()
        self.team = team
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.exchange.connect()
        self.exchange.send({"type": "hello", "team": self.team})
        
        while True:
            message = self.exchange.receive()
            if message is None:
                break
            
            self.handle_message(message)

    def handle_message(self, message: Dict[str, Any]):
        msg_type = message.get("type")
        
        if msg_type == "hello":
            self.strategy.on_hello(message.get("symbols", []))
        elif msg_type == "book":
            book = BookUpdate(
                symbol=message["symbol"],
                buy=message["buy"],
                sell=message["sell"]
            )
            orders = self.strategy.decide(book)
            for order in orders:
                self.place_order(order)
        elif msg_type == "fill":
            fill = FillUpdate(
                order_id=message["order_id"],
                symbol=message["symbol"],
                dir=Direction(message["dir"]),
                price=message["price"],
                size=message["size"]
            )
            self.strategy.on_fill(fill)
        elif msg_type == "error":
            self.logger.error(f"Exchange error: {message['error']}")

    def place_order(self, order: Order):
        self.exchange.send({
            "type": "add",
            "order_id": order.order_id,
            "symbol": order.symbol,
            "dir": order.dir.value,
            "price": order.price,
            "size": order.size
        })
