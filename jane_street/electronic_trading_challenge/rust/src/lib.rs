pub mod models;
pub mod exchange;
pub mod strategies;
pub mod bot;

#[cfg(test)]
mod tests {
    use crate::models::{MarketState, OrderBook, BookEntry};
    use crate::strategies::{BondStrategy, Strategy};

    #[test]
    fn test_mid_price() {
        let book = OrderBook {
            symbol: "BOND".to_string(),
            bids: vec![BookEntry { price: 999, size: 10 }],
            asks: vec![BookEntry { price: 1001, size: 10 }],
        };
        assert_eq!(book.mid_price(), Some(1000.0));
    }

    #[test]
    fn test_bond_strategy() {
        let mut state = MarketState::default();
        state.update_book("BOND".to_string(), vec![vec![998, 10]], vec![vec![1002, 10]]);
        
        let strategy = BondStrategy;
        let actions = strategy.execute(&state);
        
        assert_eq!(actions.len(), 2);
    }
}
