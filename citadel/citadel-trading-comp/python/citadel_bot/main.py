import click
import logging
from .api import TradingApi
from .bot import TradingBot
from typing import Final

# Python 3.13 Type Statement (conceptual for monorepo alignment)
type ApiUrl = str
type ApiKey = str

DEFAULT_URL: Final[ApiUrl] = "http://localhost:9998"

@click.command()
@click.option("--url", default=DEFAULT_URL, help="API base URL")
@click.option("--key", required=True, help="API Key")
@click.option("--interval", default=0.1, help="Polling interval in seconds")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(url: ApiUrl, key: ApiKey, interval: float, verbose: bool) -> None:
    """Citadel Trading Bot CLI - Modernized for Python 3.13"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    api = TradingApi(url, key)
    bot = TradingBot(api)
    
    try:
        logging.info(f"Starting bot with URL: {url} and interval: {interval}s")
        bot.start(interval)
    except KeyboardInterrupt:
        click.echo("\nInterrupted by user. Closing...")
    finally:
        api.close()

if __name__ == "__main__":
    main()
