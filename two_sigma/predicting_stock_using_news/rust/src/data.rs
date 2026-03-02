use serde::{Deserialize, Serialize};
use std::error::Error;
use std::fs::File;
use std::collections::HashMap;

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct MarketRecord {
    pub time: String,
    pub asset_name: String,
    pub open: f64,
    pub close: f64,
    pub returns_open_next_mktres10: f64,
    pub universe: i32,
    #[serde(skip)]
    pub features: Vec<f64>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct NewsRecord {
    pub time: String,
    pub asset_name: String,
    pub sentiment_negative: f64,
    pub sentiment_neutral: f64,
    pub sentiment_positive: f64,
    pub relevance: f64,
    pub word_count: f64,
}

pub fn load_market_data(path: &str) -> Result<Vec<MarketRecord>, Box<dyn Error>> {
    let file = File::open(path)?;
    let mut rdr = csv::Reader::from_reader(file);
    let mut records = Vec::new();
    for result in rdr.deserialize() {
        let record: MarketRecord = result?;
        records.push(record);
    }
    Ok(records)
}

pub fn load_news_data(path: &str) -> Result<Vec<NewsRecord>, Box<dyn Error>> {
    let file = File::open(path)?;
    let mut rdr = csv::Reader::from_reader(file);
    let mut records = Vec::new();
    for result in rdr.deserialize() {
        let record: NewsRecord = result?;
        records.push(record);
    }
    Ok(records)
}
