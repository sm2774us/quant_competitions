use crate::models::{MarketState, Action};
use crate::exchange::ExchangeConnection;
use crate::strategies::{Strategy, BondStrategy, AdrStrategy, EtfStrategy};
use anyhow::Result;
use log::info;

pub struct TradingBot {
    connection: ExchangeConnection,
    team_name: String,
    state: MarketState,
    strategies: Vec<Box<dyn Strategy>>,
    order_id_counter: i32,
}

impl TradingBot {
    pub fn new(connection: ExchangeConnection, team_name: String) -> Self {
        Self {
            connection,
            team_name,
            state: MarketState::default(),
            strategies: vec![
                Box::new(BondStrategy),
                Box::new(AdrStrategy),
                Box::new(EtfStrategy),
            ],
            order_id_counter: 0,
        }
    }

    pub async fn run(&mut self) -> Result<()> {
        self.connection.send_hello(&self.team_name).await?;

        loop {
            let msg = match self.connection.read().await? {
                Some(m) => m,
                None => break,
            };

            self.handle_message(msg);
            self.execute_strategies().await?;
        }
        Ok(())
    }

    fn handle_message(&mut self, msg: serde_json::Value) {
        let msg_type = msg["type"].as_str().unwrap_or("");
        match msg_type {
            "book" => {
                let sym = msg["symbol"].as_str().unwrap().to_string();
                let bids = msg["bids"].as_array().unwrap().iter().map(|v| v.as_array().unwrap().iter().map(|x| x.as_i64().unwrap() as i32).collect()).collect();
                let asks = msg["asks"].as_array().unwrap().iter().map(|v| v.as_array().unwrap().iter().map(|x| x.as_i64().unwrap() as i32).collect()).collect();
                self.state.update_book(sym, bids, asks);
            }
            "trade" => {
                let sym = msg["symbol"].as_str().unwrap().to_string();
                let price = msg["price"].as_i64().unwrap() as i32;
                self.state.add_trade(sym, price);
            }
            "fill" => {
                let sym = msg["symbol"].as_str().unwrap().to_string();
                let size = msg["size"].as_i64().unwrap() as i32;
                let dir = msg["dir"].as_str().unwrap();
                let sign = if dir == "BUY" { 1 } else { -1 };
                self.state.update_position(sym, sign * size);
                self.state.pnl += sign * -1 * msg["price"].as_i64().unwrap() as i32 * size;
            }
            "hello" => {
                if let Some(symbols) = msg["symbols"].as_array() {
                    for entry in symbols {
                        let sym = entry["symbol"].as_str().unwrap().to_string();
                        let pos = entry["position"].as_i64().unwrap() as i32;
                        self.state.positions.insert(sym, pos);
                    }
                }
            }
            _ => {}
        }
    }

    async fn execute_strategies(&mut self) -> Result<()> {
        let mut all_actions = vec![];
        for strategy in &self.strategies {
            all_actions.extend(strategy.execute(&self.state));
        }

        for action in all_actions {
            self.order_id_counter += 1;
            match action {
                Action::Add { symbol, dir, price, size } => {
                    self.connection.place_order(self.order_id_counter, &symbol, &dir, price, size).await?;
                }
                Action::Convert { symbol, dir, size } => {
                    self.connection.convert(self.order_id_counter, &symbol, &dir, size).await?;
                }
            }
        }
        Ok(())
    }
}
