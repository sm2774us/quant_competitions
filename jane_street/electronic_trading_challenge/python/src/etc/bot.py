import logging
from typing import List
from .exchange import ExchangeConnection
from .models import MarketState, Side
from .strategies import Strategy, BondStrategy, AdrStrategy, EtfStrategy

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, connection: ExchangeConnection, team_name: str):
        self.connection = connection
        self.team_name = team_name
        self.state = MarketState()
        self.strategies: List[Strategy] = [
            BondStrategy(),
            AdrStrategy(),
            EtfStrategy()
        ]
        self.order_id_counter = 0

    def get_next_order_id(self) -> int:
        self.order_id_counter += 1
        return self.order_id_counter

    def run(self):
        self.connection.connect()
        self.connection.send_hello(self.team_name)
        
        while True:
            message = self.connection.read()
            if message is None:
                logger.info("Connection closed by exchange.")
                break
            
            self.handle_message(message)
            self.execute_strategies()

    def handle_message(self, message: dict):
        msg_type = message.get("type")
        
        if msg_type == "book":
            self.state.update_book(message["symbol"], message["bids"], message["asks"])
        elif msg_type == "trade":
            self.state.add_trade(message["symbol"], message["price"])
        elif msg_type == "fill":
            self.state.update_position(message["symbol"], 
                                      message["size"] if message["dir"] == "BUY" else -message["size"])
            # Update PnL (simplified)
            sign = 1 if message["dir"] == "SELL" else -1
            self.state.pnl += sign * message["price"] * message["size"]
        elif msg_type == "close":
            logger.info("Market closed.")
            # In a real scenario, we might want to exit the loop
        elif msg_type == "hello":
            logger.info(f"Connected. Symbols: {message.get('symbols')}")
            for entry in message.get("symbols", []):
                self.state.positions[entry["symbol"]] = entry["position"]

    def execute_strategies(self):
        for strategy in self.strategies:
            actions = strategy.execute(self.state)
            for action in actions:
                order_id = self.get_next_order_id()
                if action["type"] == "add":
                    self.connection.place_order(
                        order_id, action["symbol"], action["dir"], action["price"], action["size"]
                    )
                elif action["type"] == "convert":
                    self.connection.convert(
                        order_id, action["symbol"], action["dir"], action["size"]
                    )
