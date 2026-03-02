use crate::models::{BookUpdate, Direction, FillUpdate, Position, ClientMessage};
use std::collections::HashMap;

pub struct Strategy {
    positions: HashMap<String, i32>,
    order_id_counter: i32,
    limits: HashMap<String, i32>,
}

impl Strategy {
    pub fn new() -> Self {
        let mut limits = HashMap::new();
        limits.insert("BOND".to_string(), 100);
        
        Self {
            positions: HashMap::new(),
            order_id_counter: 0,
            limits,
        }
    }

    pub fn next_order_id(&mut self) -> i32 {
        self.order_id_counter += 1;
        self.order_id_counter
    }

    pub fn on_hello(&mut self, symbols: Vec<Position>) {
        for s in symbols {
            self.positions.insert(s.symbol, s.position);
        }
    }

    pub fn on_fill(&mut self, fill: FillUpdate) {
        let pos = self.positions.entry(fill.symbol).or_insert(0);
        let delta = if fill.dir == Direction::Buy { fill.size } else { -fill.size };
        *pos += delta;
    }

    pub fn decide(&mut self, book: BookUpdate) -> Vec<ClientMessage> {
        if book.symbol == "BOND" {
            return self.bond_strategy(book);
        }
        vec![]
    }

    fn bond_strategy(&mut self, book: BookUpdate) -> Vec<ClientMessage> {
        let mut messages = Vec::new();
        let symbol = "BOND".to_string();
        let mut pos = *self.positions.get(&symbol).unwrap_or(&0);
        let limit = *self.limits.get(&symbol).unwrap_or(&100);

        // Aggressive Buy
        for (price, size) in book.sell {
            if price < 1000 {
                let buy_size = std::cmp::min(size, limit - pos);
                if buy_size > 0 {
                    messages.push(ClientMessage::Add {
                        order_id: self.next_order_id(),
                        symbol: symbol.clone(),
                        dir: Direction::Buy,
                        price,
                        size: buy_size,
                    });
                    pos += buy_size;
                }
            }
        }

        // Aggressive Sell
        for (price, size) in book.buy {
            if price > 1000 {
                let sell_size = std::cmp::min(size, limit + pos);
                if sell_size > 0 {
                    messages.push(ClientMessage::Add {
                        order_id: self.next_order_id(),
                        symbol: symbol.clone(),
                        dir: Direction::Sell,
                        price,
                        size: sell_size,
                    });
                    pos -= sell_size;
                }
            }
        }

        // Passive Buy
        if pos < limit {
            messages.push(ClientMessage::Add {
                order_id: self.next_order_id(),
                symbol: symbol.clone(),
                dir: Direction::Buy,
                price: 999,
                size: limit - pos,
            });
        }

        // Passive Sell
        if pos > -limit {
            messages.push(ClientMessage::Add {
                order_id: self.next_order_id(),
                symbol: symbol.clone(),
                dir: Direction::Sell,
                price: 1001,
                size: limit + pos,
            });
        }

        messages
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::Direction;

    #[test]
    fn test_bond_strategy_passive() {
        let mut strategy = Strategy::new();
        strategy.positions.insert("BOND".to_string(), 0);
        let book = BookUpdate {
            symbol: "BOND".to_string(),
            buy: vec![],
            sell: vec![],
        };
        let messages = strategy.decide(book);
        assert!(messages.iter().any(|m| matches!(m, ClientMessage::Add { price: 999, dir: Direction::Buy, .. })));
        assert!(messages.iter().any(|m| matches!(m, ClientMessage::Add { price: 1001, dir: Direction::Sell, .. })));
    }
}
