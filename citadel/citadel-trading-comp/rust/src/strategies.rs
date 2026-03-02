use crate::api::TradingApi;
use crate::models::*;
use std::cmp::min;

const MAIN_TAKER: f64 = 0.0065;
const ALT_TAKER: f64 = 0.005;
const TAKER_FEE: f64 = (MAIN_TAKER + ALT_TAKER) * 2.0;
const BUFFER: f64 = 0.01;
const TAKER4: f64 = MAIN_TAKER * 5.0;
const MAX_QUANTITY: i32 = 50000;

pub struct ExchangeArbitrage<'a> {
    api: &'a dyn TradingApi,
}

impl<'a> ExchangeArbitrage<'a> {
    pub fn new(api: &'a dyn TradingApi) -> Self {
        Self { api }
    }

    pub fn run(&self) {
        let _ = self.execute("WMT-M", "WMT-A");
        let _ = self.execute("CAT-M", "CAT-A");
        let _ = self.execute("MMM-M", "MMM-A");
    }

    fn execute(&self, mticker: &str, aticker: &str) -> anyhow::Result<()> {
        let mbook = self.api.get_order_book(mticker)?;
        let abook = self.api.get_order_book(aticker)?;

        if mbook.bids.is_empty() || mbook.asks.is_empty() || abook.bids.is_empty() || abook.asks.is_empty() {
            return Ok(());
        }

        let mbid = mbook.bids[0].price;
        let mask = mbook.asks[0].price;
        let abid = abook.bids[0].price;
        let aask = abook.asks[0].price;

        let m_bid_room: i32 = mbook.bids.iter().filter(|b| b.price == mbid).map(|b| b.quantity - b.quantity_filled).sum();
        let a_ask_room: i32 = abook.asks.iter().filter(|a| a.price == aask).map(|a| a.quantity - a.quantity_filled).sum();
        let a_bid_room: i32 = abook.bids.iter().filter(|b| b.price == abid).map(|b| b.quantity - b.quantity_filled).sum();
        let m_ask_room: i32 = mbook.asks.iter().filter(|a| a.price == mask).map(|a| a.quantity - a.quantity_filled).sum();

        if mbid - aask > TAKER_FEE + BUFFER * 2.0 {
            let qty = min(min(m_bid_room, a_ask_room), MAX_QUANTITY);
            if qty > 0 {
                self.api.post_order(mticker, "MARKET", "SELL", qty, None)?;
                self.api.post_order(aticker, "MARKET", "BUY", qty, None)?;
            }
        } else if abid - mask > TAKER_FEE + BUFFER * 2.0 {
            let qty = min(min(a_bid_room, m_ask_room), MAX_QUANTITY);
            if qty > 0 {
                self.api.post_order(aticker, "MARKET", "SELL", qty, None)?;
                self.api.post_order(mticker, "MARKET", "BUY", qty, None)?;
            }
        }
        Ok(())
    }
}

pub struct IndexArbitrage<'a> {
    api: &'a dyn TradingApi,
    tickers: Vec<String>,
}

impl<'a> IndexArbitrage<'a> {
    pub fn new(api: &'a dyn TradingApi) -> Self {
        Self {
            api,
            tickers: vec!["WMT".to_string(), "MMM".to_string(), "CAT".to_string()],
        }
    }

    pub fn run(&self) -> anyhow::Result<()> {
        let secs = self.api.get_securities()?;
        let etf = secs.iter().find(|s| s.ticker == "ETF");
        if etf.is_none() { return Ok(()); }
        let etf = etf.unwrap();

        let mut best_bids = std::collections::HashMap::new();
        let mut best_asks = std::collections::HashMap::new();
        let mut best_bids_q = std::collections::HashMap::new();
        let mut best_asks_q = std::collections::HashMap::new();

        for t in &self.tickers {
            let tm = format!("{}-M", t);
            let ta = format!("{}-A", t);
            let sm = secs.iter().find(|s| s.ticker == tm);
            let sa = secs.iter().find(|s| s.ticker == ta);

            if let (Some(sm), Some(sa)) = (sm, sa) {
                if sm.bid >= sa.bid {
                    best_bids.insert(tm.clone(), sm.bid);
                    best_bids_q.insert(tm.clone(), sm.bid_size);
                } else {
                    best_bids.insert(ta.clone(), sa.bid);
                    best_bids_q.insert(ta.clone(), sa.bid_size);
                }

                if sm.ask <= sa.ask {
                    best_asks.insert(tm.clone(), sm.ask);
                    best_asks_q.insert(tm.clone(), sm.ask_size);
                } else {
                    best_asks.insert(ta.clone(), sa.ask);
                    best_asks_q.insert(ta.clone(), sa.ask_size);
                }
            }
        }

        if best_bids.len() < self.tickers.len() || best_asks.len() < self.tickers.len() {
            return Ok(());
        }

        let composite_bid: f64 = best_bids.values().sum();
        let composite_ask: f64 = best_asks.values().sum();
        let composite_bid_q = *best_bids_q.values().min().unwrap_or(&0);
        let composite_ask_q = *best_asks_q.values().min().unwrap_or(&0);

        if etf.bid - composite_ask > TAKER4 + BUFFER {
            let qty = min(min(etf.bid_size, composite_ask_q), MAX_QUANTITY);
            if qty > 0 {
                self.api.post_order("ETF", "MARKET", "SELL", qty, None)?;
                for t_sym in best_asks.keys() {
                    self.api.post_order(t_sym, "MARKET", "BUY", qty, None)?;
                }
            }
        } else if composite_bid - etf.ask > TAKER4 + BUFFER {
            let qty = min(min(etf.ask_size, composite_bid_q), MAX_QUANTITY);
            if qty > 0 {
                for t_sym in best_bids.keys() {
                    self.api.post_order(t_sym, "MARKET", "SELL", qty, None)?;
                }
                self.api.post_order("ETF", "MARKET", "BUY", qty, None)?;
            }
        }

        Ok(())
    }
}

pub struct ShockHandler<'a> {
    api: &'a dyn TradingApi,
}

impl<'a> ShockHandler<'a> {
    pub fn new(api: &'a dyn TradingApi) -> Self {
        Self { api }
    }

    pub fn run(&self, current_tick: i32) -> anyhow::Result<()> {
        let news_list = self.api.get_news(10)?;
        for news in news_list {
            let elapsed = current_tick - news.tick;
            if elapsed > 2 { continue; }

            let amount = if news.headline.len() >= 6 {
                news.headline[news.headline.len()-6..].replace('$', "").parse::<f64>().unwrap_or(0.0)
            } else { 0.0 };

            let m_ticker = format!("{}-M", news.ticker);
            let a_ticker = format!("{}-A", news.ticker);

            if elapsed < 2 {
                if amount > MAIN_TAKER + BUFFER * 2.0 {
                    self.api.post_order(&m_ticker, "MARKET", "BUY", MAX_QUANTITY, None)?;
                    self.api.post_order(&a_ticker, "MARKET", "BUY", MAX_QUANTITY, None)?;
                } else if -amount > MAIN_TAKER + BUFFER * 2.0 {
                    self.api.post_order(&m_ticker, "MARKET", "SELL", MAX_QUANTITY, None)?;
                    self.api.post_order(&a_ticker, "MARKET", "SELL", MAX_QUANTITY, None)?;
                }
            } else if elapsed == 2 {
                if amount > MAIN_TAKER + BUFFER * 2.0 {
                    self.api.post_order(&m_ticker, "MARKET", "SELL", MAX_QUANTITY, None)?;
                    self.api.post_order(&a_ticker, "MARKET", "SELL", MAX_QUANTITY, None)?;
                } else if -amount > MAIN_TAKER + BUFFER * 2.0 {
                    self.api.post_order(&m_ticker, "MARKET", "BUY", MAX_QUANTITY, None)?;
                    self.api.post_order(&a_ticker, "MARKET", "BUY", MAX_QUANTITY, None)?;
                }
            }
        }
        Ok(())
    }
}
