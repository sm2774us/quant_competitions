use std::collections::{HashMap, HashSet};
use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct Trade {
    pub date: i32,
    pub weight: f64,
    pub resp: f64,
    pub action: i32,
}

#[derive(Debug, Serialize)]
pub struct Summary {
    pub total_profit: f64,
    pub num_trades_executed: f64,
    pub utility_score: f64,
    pub participation_rate: f64,
}

pub struct UtilityScorer;

impl UtilityScorer {
    pub fn calculate_utility(trades: &[Trade]) -> f64 {
        if trades.is_empty() { return 0.0; }

        let mut daily_profits: HashMap<i32, f64> = HashMap::new();
        let mut unique_dates = HashSet::new();

        for trade in trades {
            let profit = trade.weight * trade.resp * (trade.action as f64);
            *daily_profits.entry(trade.date).or_insert(0.0) += profit;
            unique_dates.insert(trade.date);
        }

        let mut sum_p = 0.0;
        let mut sum_p_sq = 0.0;
        for profit in daily_profits.values() {
            sum_p += profit;
            sum_p_sq += profit * profit;
        }

        if sum_p_sq == 0.0 { return 0.0; }

        let t = (sum_p / sum_p_sq.sqrt()) * ((250.0 / (unique_dates.len() as f64)).sqrt());
        let u = t.max(0.0).min(6.0) * sum_p;

        u
    }

    pub fn summary_table(trades: &[Trade]) -> Summary {
        let mut profit = 0.0;
        let mut num_trades = 0;
        for trade in trades {
            profit += trade.weight * trade.resp * (trade.action as f64);
            if trade.action == 1 { num_trades += 1; }
        }

        Summary {
            total_profit: profit,
            num_trades_executed: num_trades as f64,
            utility_score: Self::calculate_utility(trades),
            participation_rate: if trades.is_empty() { 0.0 } else { (num_trades as f64) / (trades.len() as f64) },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_utility_calculation() {
        let trades = vec![
            Trade { date: 0, weight: 1.0, resp: 0.1, action: 1 },
            Trade { date: 0, weight: 1.0, resp: 0.2, action: 1 },
            Trade { date: 1, weight: 1.0, resp: -0.1, action: 1 },
            Trade { date: 1, weight: 1.0, resp: 0.3, action: 1 },
        ];
        
        let u = UtilityScorer::calculate_utility(&trades);
        assert_relative_eq!(u, 3.0, epsilon = 1e-4);
    }
}
