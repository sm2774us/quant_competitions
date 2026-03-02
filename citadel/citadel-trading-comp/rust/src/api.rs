use crate::models::*;
use reqwest::blocking::Client;
use anyhow::Result;
use mockall::automock;

#[automock]
pub trait TradingApi {
    fn get_case(&self) -> Result<CaseStatus>;
    fn get_securities(&self) -> Result<Vec<Security>>;
    fn get_order_book(&self, ticker: &str) -> Result<OrderBook>;
    fn get_news(&self, limit: i32) -> Result<Vec<News>>;
    fn post_order(&self, ticker: &str, order_type: &str, action: &str, quantity: i32, price: Option<f64>) -> Result<OrderResponse>;
}

pub struct RealTradingApi {
    base_url: String,
    api_key: String,
    client: Client,
}

impl RealTradingApi {
    pub fn new(base_url: String, api_key: String) -> Self {
        Self {
            base_url,
            api_key,
            client: Client::new(),
        }
    }
}

impl TradingApi for RealTradingApi {
    fn get_case(&self) -> Result<CaseStatus> {
        let resp = self.client.get(format!("{}/v1/case", self.base_url))
            .header("X-API-Key", &self.api_key)
            .send()?
            .json::<CaseStatus>()?;
        Ok(resp)
    }

    fn get_securities(&self) -> Result<Vec<Security>> {
        let resp = self.client.get(format!("{}/v1/securities", self.base_url))
            .header("X-API-Key", &self.api_key)
            .send()?
            .json::<Vec<Security>>()?;
        Ok(resp)
    }

    fn get_order_book(&self, ticker: &str) -> Result<OrderBook> {
        let resp = self.client.get(format!("{}/v1/securities/book", self.base_url))
            .header("X-API-Key", &self.api_key)
            .query(&[("ticker", ticker)])
            .send()?
            .json::<OrderBook>()?;
        Ok(resp)
    }

    fn get_news(&self, limit: i32) -> Result<Vec<News>> {
        let resp = self.client.get(format!("{}/v1/news", self.base_url))
            .header("X-API-Key", &self.api_key)
            .query(&[("limit", limit)])
            .send()?
            .json::<Vec<News>>()?;
        Ok(resp)
    }

    fn post_order(&self, ticker: &str, order_type: &str, action: &str, quantity: i32, price: Option<f64>) -> Result<OrderResponse> {
        let mut params = vec![
            ("ticker", ticker.to_string()),
            ("type", order_type.to_string()),
            ("action", action.to_string()),
            ("quantity", quantity.to_string()),
        ];
        if let Some(p) = price {
            params.push(("price", p.to_string()));
        }

        let resp = self.client.post(format!("{}/v1/orders", self.base_url))
            .header("X-API-Key", &self.api_key)
            .query(&params)
            .send()?
            .json::<OrderResponse>()?;
        Ok(resp)
    }
}
