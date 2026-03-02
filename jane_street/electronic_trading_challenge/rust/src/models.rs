use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct BookEntry {
    pub price: i32,
    pub size: i32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OrderBook {
    pub symbol: String,
    pub bids: Vec<BookEntry>,
    pub asks: Vec<BookEntry>,
}

impl OrderBook {
    pub fn mid_price(&self) -> Option<f64> {
        if self.bids.is_empty() || self.asks.is_empty() {
            return None;
        }
        Some((self.bids[0].price + self.asks[0].price) as f64 / 2.0)
    }
}

#[derive(Default)]
pub struct MarketState {
    pub books: HashMap<String, OrderBook>,
    pub positions: HashMap<String, i32>,
    pub last_trades: HashMap<String, Vec<i32>>,
    pub pnl: i32,
}

impl MarketState {
    pub fn update_book(&mut self, symbol: String, bids: Vec<Vec<i32>>, asks: Vec<Vec<i32>>) {
        let book = self.books.entry(symbol.clone()).or_insert(OrderBook {
            symbol,
            bids: vec![],
            asks: vec![],
        });
        book.bids = bids.into_iter().map(|v| BookEntry { price: v[0], size: v[1] }).collect();
        book.asks = asks.into_iter().map(|v| BookEntry { price: v[0], size: v[1] }).collect();
    }

    pub fn add_trade(&mut self, symbol: String, price: i32) {
        let trades = self.last_trades.entry(symbol).or_default();
        trades.push(price);
        if trades.len() > 100 {
            trades.remove(0);
        }
    }

    pub fn update_position(&mut self, symbol: String, change: i32) {
        *self.positions.entry(symbol).or_default() += change;
    }
}

#[derive(Debug)]
pub enum Action {
    Add { symbol: String, dir: String, price: i32, size: i32 },
    Convert { symbol: String, dir: String, size: i32 },
}
