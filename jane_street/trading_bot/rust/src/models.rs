use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone, Copy, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Direction {
    Buy,
    Sell,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Order {
    pub order_id: i32,
    pub symbol: String,
    pub dir: Direction,
    pub price: i32,
    pub size: i32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct BookUpdate {
    pub symbol: String,
    pub buy: Vec<(i32, i32)>,
    pub sell: Vec<(i32, i32)>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct FillUpdate {
    pub order_id: i32,
    pub symbol: String,
    pub dir: Direction,
    pub price: i32,
    pub size: i32,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Position {
    pub symbol: String,
    pub position: i32,
}

#[derive(Debug, Serialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ClientMessage {
    Hello { team: String },
    Add { 
        order_id: i32, 
        symbol: String, 
        dir: Direction, 
        price: i32, 
        size: i32 
    },
}

#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ExchangeMessage {
    Hello { symbols: Vec<Position> },
    Book(BookUpdate),
    Fill(FillUpdate),
    Open { symbols: Vec<String> },
    Close { symbols: Vec<String> },
    Error { error: String },
    #[serde(other)]
    Unknown,
}
