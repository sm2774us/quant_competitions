mod models;
mod exchange_client;
mod strategies;

use clap::Parser;
use anyhow::Result;
use models::ExchangeMessage;
use exchange_client::ExchangeClient;
use strategies::{BondStrategy, MACDStrategy, TradingStrategy};
use std::collections::HashMap;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long, default_value = "production")]
    hostname: String,

    #[arg(long, default_value_t = 25000)]
    port: u16,

    #[arg(long, default_value = "PANIPURISTREET")]
    team: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    let args = Args::parse();

    let mut client = ExchangeClient::connect(&args.hostname, args.port, &args.team).await?;
    let mut bond_strat = BondStrategy::new();
    let mut macd_strats: HashMap<String, MACDStrategy> = HashMap::new();
    let mut order_id = 0;

    loop {
        match client.next_message().await? {
            Some(ExchangeMessage::Hello { symbols }) => {
                for sym_info in symbols {
                    if sym_info.symbol != "BOND" && sym_info.symbol != "VALE" && sym_info.symbol != "VALBZ" {
                        macd_strats.insert(sym_info.symbol.clone(), MACDStrategy::new(sym_info.symbol));
                    }
                }
            }
            Some(ExchangeMessage::Book { symbol, buy, sell }) => {
                if symbol == "BOND" {
                    let orders = bond_strat.update_book(&buy, &sell, &mut order_id);
                    for order in orders {
                        client.send_order(&order).await?;
                    }
                }
            }
            Some(ExchangeMessage::Trade { symbol, price, .. }) => {
                if let Some(strat) = macd_strats.get_mut(&symbol) {
                    let orders = strat.update_price(price, &mut order_id);
                    for order in orders {
                        client.send_order(&order).await?;
                    }
                }
            }
            Some(ExchangeMessage::Fill { symbol, dir, size, .. }) => {
                if symbol == "BOND" {
                    bond_strat.update_fill(&dir, size);
                } else if let Some(strat) = macd_strats.get_mut(&symbol) {
                    // Assuming MACDStrategy also implements TradingStrategy or has similar update_fill
                    // For now, let's just update the internal position if needed
                }
            }
            Some(_) => {}
            None => break,
        }
    }

    Ok(())
}
