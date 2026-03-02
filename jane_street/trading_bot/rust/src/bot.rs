use crate::exchange::Exchange;
use crate::strategy::Strategy;
use crate::models::{ClientMessage, ExchangeMessage};
use anyhow::Result;

pub struct Bot {
    exchange: Exchange,
    strategy: Strategy,
    team: String,
}

impl Bot {
    pub fn new(host: &str, port: u16, team: &str) -> Result<Self> {
        let exchange = Exchange::connect(host, port)?;
        Ok(Self {
            exchange,
            strategy: Strategy::new(),
            team: team.to_string(),
        })
    }

    pub fn run(&mut self) -> Result<()> {
        self.exchange.send(&ClientMessage::Hello { team: self.team.clone() })?;

        while let Some(message) = self.exchange.receive()? {
            self.handle_message(message)?;
        }
        Ok(())
    }

    fn handle_message(&mut self, message: ExchangeMessage) -> Result<()> {
        match message {
            ExchangeMessage::Hello { symbols } => {
                self.strategy.on_hello(symbols);
            }
            ExchangeMessage::Book(book) => {
                let orders = self.strategy.decide(book);
                for order in orders {
                    self.exchange.send(&order)?;
                }
            }
            ExchangeMessage::Fill(fill) => {
                self.strategy.on_fill(fill);
            }
            ExchangeMessage::Error { error } => {
                log::error!("Exchange error: {}", error);
            }
            _ => {}
        }
        Ok(())
    }
}
