use crate::models::{Order, ExchangeMessage};
use std::collections::VecDeque;

pub trait TradingStrategy {
    fn update_book(&mut self, buy: &Vec<Vec<i32>>, sell: &Vec<Vec<i32>>, order_id: &mut i32) -> Vec<Order>;
    fn update_fill(&mut self, dir: &str, size: i32);
}

pub struct BondStrategy {
    symbol: String,
    position: i32,
    fair_price: i32,
    limit: i32,
}

impl BondStrategy {
    pub fn new() -> Self {
        Self {
            symbol: "BOND".to_string(),
            position: 0,
            fair_price: 1000,
            limit: 100,
        }
    }
}

impl TradingStrategy for BondStrategy {
    fn update_book(&mut self, buy: &Vec<Vec<i32>>, sell: &Vec<Vec<i32>>, order_id: &mut i32) -> Vec<Order> {
        let mut orders = Vec::new();

        for level in sell {
            let price = level[0];
            let size = level[1];
            if price < self.fair_price {
                let buy_size = std::cmp::min(size, self.limit - self.position);
                if buy_size > 0 {
                    orders.push(Order::Add { order_id: *order_id, symbol: self.symbol.clone(), dir: "BUY".to_string(), price, size: buy_size });
                    *order_id += 1;
                }
            }
        }

        for level in buy {
            let price = level[0];
            let size = level[1];
            if price > self.fair_price {
                let sell_size = std::cmp::min(size, self.position + self.limit);
                if sell_size > 0 {
                    orders.push(Order::Add { order_id: *order_id, symbol: self.symbol.clone(), dir: "SELL".to_string(), price, size: sell_size });
                    *order_id += 1;
                }
            }
        }

        if self.position < self.limit {
            orders.push(Order::Add { order_id: *order_id, symbol: self.symbol.clone(), dir: "BUY".to_string(), price: 999, size: 1 });
            *order_id += 1;
        }
        if self.position > -self.limit {
            orders.push(Order::Add { order_id: *order_id, symbol: self.symbol.clone(), dir: "SELL".to_string(), price: 1001, size: 1 });
            *order_id += 1;
        }

        orders
    }

    fn update_fill(&mut self, dir: &str, size: i32) {
        if dir == "BUY" { self.position += size; }
        else { self.position -= size; }
    }
}

pub struct MACDStrategy {
    symbol: String,
    position: i32,
    prices: VecDeque<i32>,
    ema12: Option<f64>,
    ema20: Option<f64>,
    limit: i32,
}

impl MACDStrategy {
    pub fn new(symbol: String) -> Self {
        Self {
            symbol,
            position: 0,
            prices: VecDeque::with_capacity(20),
            ema12: None,
            ema20: None,
            limit: 50,
        }
    }

    pub fn update_price(&mut self, price: i32, order_id: &mut i32) -> Vec<Order> {
        self.prices.push_back(price);
        if self.prices.size() > 20 { self.prices.pop_front(); }
        if self.prices.size() < 20 { return Vec::new(); }

        if self.ema12.is_none() {
            let p_vec: Vec<i32> = self.prices.iter().cloned().collect();
            self.ema12 = Some(p_vec[8..20].iter().sum::<i32>() as f64 / 12.0);
            self.ema20 = Some(p_vec.iter().sum::<i32>() as f64 / 20.0);
        } else {
            self.ema12 = Some((price as f64 - self.ema12.unwrap()) * (2.0 / 13.0) + self.ema12.unwrap());
            self.ema20 = Some((price as f64 - self.ema20.unwrap()) * (2.0 / 21.0) + self.ema20.unwrap());
        }

        let macd = self.ema12.unwrap() - self.ema20.unwrap();
        let mut orders = Vec::new();
        if macd > 0.5 && self.position < self.limit {
            orders.push(Order::Add { order_id: *order_id, symbol: self.symbol.clone(), dir: "BUY".to_string(), price: price + 1, size: 1 });
            *order_id += 1;
        } else if macd < -0.5 && self.position > -self.limit {
            orders.push(Order::Add { order_id: *order_id, symbol: self.symbol.clone(), dir: "SELL".to_string(), price: price - 1, size: 1 });
            *order_id += 1;
        }
        orders
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bond_strategy_buy() {
        let mut strat = BondStrategy::new();
        let buy = vec![];
        let sell = vec![vec![998, 10]];
        let mut order_id = 1;
        let orders = strat.update_book(&buy, &sell, &mut order_id);
        assert!(orders.iter().any(|o| match o {
            Order::Add { dir, price, .. } => dir == "BUY" && *price == 998,
            _ => false,
        }));
    }

    #[test]
    fn test_macd_strategy_momentum() {
        let mut strat = MACDStrategy::new("AAPL".to_string());
        let mut order_id = 1;
        let mut orders = Vec::new();
        for i in 100..125 {
            orders = strat.update_price(i, &mut order_id);
        }
        assert!(!orders.is_empty());
        match &orders[0] {
            Order::Add { dir, .. } => assert_eq!(dir, "BUY"),
            _ => panic!("Expected Add order"),
        }
    }
}
