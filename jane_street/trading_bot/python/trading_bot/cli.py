import click
import logging
from .bot import TradingBot

@click.command()
@click.option('--host', default='localhost', help='Exchange host')
@click.option('--port', default=25000, type=int, help='Exchange port')
@click.option('--team', default='TEAMNAME', help='Team name')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def main(host, port, team, verbose):
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    bot = TradingBot(host, port, team)
    try:
        bot.run()
    except KeyboardInterrupt:
        click.echo("
Bot stopped by user.")
    except Exception as e:
        click.echo(f"Error: {e}")

if __name__ == '__main__':
    main()
