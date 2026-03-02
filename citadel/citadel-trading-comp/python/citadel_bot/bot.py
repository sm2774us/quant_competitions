import time
import logging
from .api import TradingApi
from .strategies import ExchangeArbitrage, IndexArbitrage, ShockHandler

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, api: TradingApi):
        self.api = api
        self.exchange_arb = ExchangeArbitrage(api)
        self.index_arb = IndexArbitrage(api)
        self.shock_handler = ShockHandler(api)
        self.last_tick = -1

    def run_once(self):
        try:
            case = self.api.get_case()
            if case.status == "STOPPED":
                return False

            if case.tick != self.last_tick:
                self.last_tick = case.tick
                logger.info(f"Tick: {case.tick}")

                # Run strategies
                self.shock_handler.run(case.tick)
                self.exchange_arb.run("WMT-M", "WMT-A")
                self.exchange_arb.run("CAT-M", "CAT-A")
                self.exchange_arb.run("MMM-M", "MMM-A")
                self.index_arb.run(['WMT', 'MMM', 'CAT'])

            return True
        except Exception as e:
            logger.error(f"Error in bot loop: {e}")
            return True

    def start(self, interval: float = 0.1):
        logger.info("Starting trading bot...")
        while self.run_once():
            time.sleep(interval)
        logger.info("Bot stopped.")
