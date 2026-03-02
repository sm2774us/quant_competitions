use citadel_bot::api::MockTradingApi;
use citadel_bot::strategies::{ExchangeArbitrage, ShockHandler};
use citadel_bot::models::*;
use mockall::predicate::*;

#[test]
fn test_exchange_arbitrage_market() {
    let mut mock_api = MockTradingApi::new();
    
    let mbook = OrderBook { bids: vec![OrderBookEntry { price: 100.5, quantity: 1000, quantity_filled: 0 }], asks: vec![OrderBookEntry { price: 101.0, quantity: 1000, quantity_filled: 0 }] };
    let abook = OrderBook { bids: vec![OrderBookEntry { price: 99.5, quantity: 1000, quantity_filled: 0 }], asks: vec![OrderBookEntry { price: 100.0, quantity: 1000, quantity_filled: 0 }] };

    mock_api.expect_get_order_book().with(eq("WMT-M")).returning(move |_| Ok(mbook.clone()));
    mock_api.expect_get_order_book().with(eq("WMT-A")).returning(move |_| Ok(abook.clone()));
    
    // Add defaults for other tickers to avoid mock failure
    mock_api.expect_get_order_book().returning(|_| Ok(OrderBook { bids: vec![], asks: vec![] }));
    
    mock_api.expect_post_order().with(eq("WMT-M"), eq("MARKET"), eq("SELL"), eq(1000), eq(None)).returning(|_, _, _, _, _| Ok(OrderResponse { order_id: 1, status: "OPEN".into(), ticker: "WMT-M".into(), order_type: "MARKET".into(), action: "SELL".into(), quantity: 1000, price: None, vwap: None }));
    mock_api.expect_post_order().with(eq("WMT-A"), eq("MARKET"), eq("BUY"), eq(1000), eq(None)).returning(|_, _, _, _, _| Ok(OrderResponse { order_id: 2, status: "OPEN".into(), ticker: "WMT-A".into(), order_type: "MARKET".into(), action: "BUY".into(), quantity: 1000, price: None, vwap: None }));

    let arb = ExchangeArbitrage::new(&mock_api);
    arb.run();
}

#[test]
fn test_shock_handler_buy() {
    let mut mock_api = MockTradingApi::new();
    
    let news = vec![News { tick: 10, ticker: "WMT".into(), headline: "WMT stock jump $10.00".into(), body: "".into() }];
    mock_api.expect_get_news().returning(move |_| Ok(news.clone()));
    
    mock_api.expect_post_order().with(eq("WMT-M"), eq("MARKET"), eq("BUY"), eq(50000), eq(None)).returning(|_, _, _, _, _| Ok(OrderResponse { order_id: 1, status: "OPEN".into(), ticker: "WMT-M".into(), order_type: "MARKET".into(), action: "BUY".into(), quantity: 50000, price: None, vwap: None }));
    mock_api.expect_post_order().with(eq("WMT-A"), eq("MARKET"), eq("BUY"), eq(50000), eq(None)).returning(|_, _, _, _, _| Ok(OrderResponse { order_id: 2, status: "OPEN".into(), ticker: "WMT-A".into(), order_type: "MARKET".into(), action: "BUY".into(), quantity: 50000, price: None, vwap: None }));

    let handler = ShockHandler::new(&mock_api);
    handler.run(11).unwrap();
}
