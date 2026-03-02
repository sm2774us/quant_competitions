use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Security {
    pub ticker: String,
    pub position: i32,
    pub vwap: f64,
    pub nlv: f64,
    pub last: f64,
    pub bid: f64,
    pub bid_size: i32,
    pub ask: f64,
    pub ask_size: i32,
    pub unrealized: f64,
    pub realized: f64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OrderBookEntry {
    pub price: f64,
    pub quantity: i32,
    pub quantity_filled: i32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OrderBook {
    pub bids: Vec<OrderBookEntry>,
    pub asks: Vec<OrderBookEntry>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct News {
    pub tick: i32,
    pub ticker: String,
    pub headline: String,
    pub body: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CaseStatus {
    pub tick: i32,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Limit {
    pub ticker: String,
    pub gross_limit: i32,
    pub net_limit: i32,
    pub gross: i32,
    pub net: i32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OrderResponse {
    pub order_id: i32,
    pub status: String,
    pub ticker: String,
    #[serde(rename = "type")]
    pub order_type: String,
    pub action: String,
    pub quantity: i32,
    pub price: Option<f64>,
    pub vwap: Option<f64>,
}
