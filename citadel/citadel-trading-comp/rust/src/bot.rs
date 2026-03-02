use crate::api::TradingApi;
use crate::strategies::{ExchangeArbitrage, IndexArbitrage, ShockHandler};
use std::thread;
use std::time::Duration;

pub struct TradingBot<'a> {
    api: &'a dyn TradingApi,
    last_tick: i32,
}

impl<'a> TradingBot<'a> {
    pub fn new(api: &'a dyn TradingApi) -> Self {
        Self { api, last_tick: -1 }
    }

    pub fn start(&mut self, interval_seconds: f64) {
        println!("Starting Rust trading bot...");
        while self.run_once() {
            thread::sleep(Duration::from_millis((interval_seconds * 1000.0) as u64));
        }
    }

    pub fn run_once(&mut self) -> bool {
        match self.api.get_case() {
            Ok(case) => {
                if case.status == "STOPPED" { return false; }

                if case.tick != self.last_tick {
                    self.last_tick = case.tick;
                    println!("Tick: {}", self.last_tick);

                    let shock_handler = ShockHandler::new(self.api);
                    let exchange_arb = ExchangeArbitrage::new(self.api);
                    let index_arb = IndexArbitrage::new(self.api);

                    let _ = shock_handler.run(case.tick);
                    exchange_arb.run();
                    let _ = index_arb.run();
                }
                true
            }
            Err(e) => {
                eprintln!("Bot error: {}", e);
                true
            }
        }
    }
}
