import asyncio
import click
import logging
import sys
from .client import ExchangeClient
from .strategies import BondStrategy, ADRStrategy, MACDStrategy
from .models import Order

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, hostname: str, port: int, team_name: str):
        self.client = ExchangeClient(hostname, port, team_name)
        self.bond_strat = BondStrategy()
        self.adr_strat = ADRStrategy()
        self.macd_strats = {}
        self.order_id_counter = 0

    async def run(self):
        await self.client.connect()
        async for msg in self.client.messages():
            await self.handle_message(msg)

    async def handle_message(self, msg: dict):
        msg_type = msg.get("type")
        
        if msg_type == "hello":
            logger.info(f"Connected to exchange. Initial state: {msg}")
            for symbol_info in msg.get("symbols", []):
                symbol = symbol_info["symbol"]
                if symbol not in ["BOND", "VALE", "VALBZ"]:
                    self.macd_strats[symbol] = MACDStrategy(symbol)

        elif msg_type == "book":
            symbol = msg["symbol"]
            orders = []
            if symbol == "BOND":
                orders = self.bond_strat.update_book(msg, self.order_id_counter)
            elif symbol == "VALE":
                self.adr_strat.update_book_vale(msg)
                orders = self.adr_strat.calculate_orders(self.order_id_counter)
            elif symbol == "VALBZ":
                self.adr_strat.update_book_valbz(msg)
                orders = self.adr_strat.calculate_orders(self.order_id_counter)
            
            for order in orders:
                await self.client.send_order(order)
                self.order_id_counter += 1

        elif msg_type == "trade":
            symbol = msg["symbol"]
            if symbol in self.macd_strats:
                orders = self.macd_strats[symbol].update_price(msg["price"], self.order_id_counter)
                for order in orders:
                    await self.client.send_order(order)
                    self.order_id_counter += 1

        elif msg_type == "fill":
            symbol = msg["symbol"]
            if symbol == "BOND":
                self.bond_strat.update_fill(msg["dir"], msg["size"])
            elif symbol in ["VALE", "VALBZ"]:
                # Simple ADR fill tracking
                pass
            elif symbol in self.macd_strats:
                self.macd_strats[symbol].update_fill(msg["dir"], msg["size"])

@click.command()
@click.option('--hostname', default='production', help='Exchange hostname')
@click.option('--port', default=25000, help='Exchange port')
@click.option('--team', default='PANIPURISTREET', help='Team name')
def main(hostname, port, team):
    bot = TradingBot(hostname, port, team)
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
