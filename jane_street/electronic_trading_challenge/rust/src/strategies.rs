use crate::models::{MarketState, Action};

pub trait Strategy {
    fn execute(&self, state: &MarketState) -> Vec<Action>;
}

pub struct BondStrategy;
impl Strategy for BondStrategy {
    fn execute(&self, state: &MarketState) -> Vec<Action> {
        let mut actions = vec![];
        if !state.books.contains_key("BOND") { return actions; }
        
        let current_pos = *state.positions.get("BOND").unwrap_or(&0);
        let limit = 100;
        
        if current_pos < limit {
            actions.push(Action::Add { symbol: "BOND".to_string(), dir: "BUY".to_string(), price: 999, size: limit - current_pos });
        }
        if current_pos > -limit {
            actions.push(Action::Add { symbol: "BOND".to_string(), dir: "SELL".to_string(), price: 1001, size: limit + current_pos });
        }
        actions
    }
}

pub struct AdrStrategy;
impl Strategy for AdrStrategy {
    fn execute(&self, state: &MarketState) -> Vec<Action> {
        let mut actions = vec![];
        let valbz_trades = state.last_trades.get("VALBZ");
        let vale_trades = state.last_trades.get("VALE");

        if let (Some(valbz), Some(vale)) = (valbz_trades, vale_trades) {
            if valbz.len() >= 10 && vale.len() >= 10 {
                let valbz_mean: f64 = valbz.iter().rev().take(10).sum::<i32>() as f64 / 10.0;
                let vale_mean: f64 = vale.iter().rev().take(10).sum::<i32>() as f64 / 10.0;

                if valbz_mean - vale_mean >= 2.0 {
                    actions.push(Action::Add { symbol: "VALE".to_string(), dir: "BUY".to_string(), price: vale_mean as i32 + 1, size: 10 });
                    actions.push(Action::Convert { symbol: "VALE".to_string(), dir: "SELL".to_string(), size: 10 });
                    actions.push(Action::Add { symbol: "VALBZ".to_string(), dir: "SELL".to_string(), price: valbz_mean as i32 - 1, size: 10 });
                }
            }
        }
        actions
    }
}

pub struct EtfStrategy;
impl Strategy for EtfStrategy {
    fn execute(&self, state: &MarketState) -> Vec<Action> {
        let mut actions = vec![];
        let symbols = ["XLF", "BOND", "GS", "MS", "WFC"];
        let mut means = std::collections::HashMap::new();

        for &sym in &symbols {
            let trades = match state.last_trades.get(sym) {
                Some(t) if t.len() >= 25 => t,
                _ => return actions,
            };
            let mean: f64 = trades.iter().rev().take(25).sum::<i32>() as f64 / 25.0;
            means.insert(sym, mean);
        }

        let nav = 3.0 * means["BOND"] + 2.0 * means["GS"] + 3.0 * means["MS"] + 2.0 * means["WFC"];
        let xlf_price = 10.0 * means["XLF"];

        if xlf_price + 150.0 < nav {
            actions.push(Action::Add { symbol: "XLF".to_string(), dir: "BUY".to_string(), price: means["XLF"] as i32 + 1, size: 100 });
            actions.push(Action::Convert { symbol: "XLF".to_string(), dir: "SELL".to_string(), size: 100 });
            actions.push(Action::Add { symbol: "BOND".to_string(), dir: "SELL".to_string(), price: means["BOND"] as i32 - 1, size: 30 });
            actions.push(Action::Add { symbol: "GS".to_string(), dir: "SELL".to_string(), price: means["GS"] as i32 - 1, size: 20 });
            actions.push(Action::Add { symbol: "MS".to_string(), dir: "SELL".to_string(), price: means["MS"] as i32 - 1, size: 30 });
            actions.push(Action::Add { symbol: "WFC".to_string(), dir: "SELL".to_string(), price: means["WFC"] as i32 - 1, size: 20 });
        } else if xlf_price - 150.0 > nav {
            actions.push(Action::Add { symbol: "BOND".to_string(), dir: "BUY".to_string(), price: means["BOND"] as i32 + 1, size: 30 });
            actions.push(Action::Add { symbol: "GS".to_string(), dir: "BUY".to_string(), price: means["GS"] as i32 + 1, size: 20 });
            actions.push(Action::Add { symbol: "MS".to_string(), dir: "BUY".to_string(), price: means["MS"] as i32 + 1, size: 30 });
            actions.push(Action::Add { symbol: "WFC".to_string(), dir: "BUY".to_string(), price: means["WFC"] as i32 + 1, size: 20 });
            actions.push(Action::Convert { symbol: "XLF".to_string(), dir: "BUY".to_string(), size: 100 });
            actions.push(Action::Add { symbol: "XLF".to_string(), dir: "SELL".to_string(), price: means["XLF"] as i32 - 1, size: 100 });
        }

        actions
    }
}
