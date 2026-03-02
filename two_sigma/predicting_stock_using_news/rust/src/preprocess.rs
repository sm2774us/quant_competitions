use crate::data::{MarketRecord, NewsRecord};
use std::collections::HashMap;

pub fn preprocess(market: &mut Vec<MarketRecord>, news: &[NewsRecord]) {
    let mut news_map: HashMap<(String, String), Vec<&NewsRecord>> = HashMap::new();
    for n in news {
        news_map.entry((n.time.clone(), n.asset_name.clone()))
                .or_default()
                .push(n);
    }

    for m in market {
        let key = (m.time.clone(), m.asset_name.clone());
        if let Some(news_items) = news_map.get(&key) {
            let count = news_items.len() as f64;
            let neg: f64 = news_items.iter().map(|n| n.sentiment_negative).sum::<f64>() / count;
            let neut: f64 = news_items.iter().map(|n| n.sentiment_neutral).sum::<f64>() / count;
            let pos: f64 = news_items.iter().map(|n| n.sentiment_positive).sum::<f64>() / count;
            let rel: f64 = news_items.iter().map(|n| n.relevance).sum::<f64>() / count;
            let wc: f64 = news_items.iter().map(|n| n.word_count).sum::<f64>() / count;
            
            m.features = vec![neg, neut, pos, rel, wc];
        } else {
            m.features = vec![0.0, 0.0, 0.0, 0.0, 0.0];
        }

        // Outlier handling
        let ratio = m.close / m.open;
        if ratio < 0.33 { m.open = m.close; }
        if ratio > 2.0 { m.close = m.open; }
    }
}
