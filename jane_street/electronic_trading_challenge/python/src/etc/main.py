import click
import logging
from .exchange import ExchangeConnection
from .bot import TradingBot

@click.command()
@click.option("--host", default="production", help="Exchange host")
@click.option("--port", default=25000, type=int, help="Exchange port")
@click.option("--team", default="FOMO", help="Team name")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(host: str, port: int, team: str, verbose: bool):
    """Jane Street Electronic Trading Challenge Bot."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    conn = ExchangeConnection(host, port)
    bot = TradingBot(conn, team)
    try:
        bot.run()
    except KeyboardInterrupt:
        click.echo("Exiting...")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
