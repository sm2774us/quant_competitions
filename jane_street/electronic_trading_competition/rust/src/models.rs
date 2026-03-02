use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum Order {
    Add {
        order_id: i32,
        symbol: String,
        dir: String,
        price: i32,
        size: i32,
    },
    Cancel {
        order_id: i32,
    },
    Convert {
        order_id: i32,
        symbol: String,
        dir: String,
        size: i32,
    },
}

#[derive(Deserialize, Debug)]
#[serde(tag = "type", rename_all = "lowercase")]
pub enum ExchangeMessage {
    Hello {
        symbols: Vec<SymbolInfo>,
    },
    Book {
        symbol: String,
        buy: Vec<Vec<i32>>,
        sell: Vec<Vec<i32>>,
    },
    Fill {
        order_id: i32,
        symbol: String,
        dir: String,
        price: i32,
        size: i32,
    },
    Trade {
        symbol: String,
        price: i32,
        size: i32,
    },
    Ack {
        order_id: i32,
    },
    Reject {
        order_id: i32,
        error: String,
    },
    Error {
        error: String,
    },
}

#[derive(Deserialize, Debug)]
pub struct SymbolInfo {
    pub symbol: String,
    pub position: i32,
}
