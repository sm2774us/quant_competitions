mod data;
mod preprocess;
mod model;
mod evaluate;

use clap::Parser;
use std::error::Error;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(long)]
    market: String,

    #[arg(long)]
    news: String,
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();

    println!("Loading data...");
    let mut market_data = data::load_market_data(&args.market)?;
    let news_data = data::load_news_data(&args.news)?;

    println!("Preprocessing...");
    preprocess::preprocess(&mut market_data, &news_data);

    // Split 80/20
    let split_idx = (market_data.len() as f64 * 0.8) as usize;
    
    let (train, test) = market_data.split_at(split_idx);
    
    let x_train: Vec<Vec<f64>> = train.iter().map(|m| m.features.clone()).collect();
    let y_train: Vec<f64> = train.iter().map(|m| m.returns_open_next_mktres10).collect();

    let x_test: Vec<Vec<f64>> = test.iter().map(|m| m.features.clone()).collect();
    let y_test: Vec<f64> = test.iter().map(|m| m.returns_open_next_mktres10).collect();
    let u_test: Vec<i32> = test.iter().map(|m| m.universe).collect();
    let t_test: Vec<String> = test.iter().map(|m| m.time.clone()).collect();

    println!("Training...");
    let mut model = model::Model::new();
    model.train(&x_train, &y_train);

    println!("Predicting...");
    let predictions = model.predict(&x_test);

    println!("Evaluating...");
    let score = evaluate::evaluate(&predictions, &y_test, &u_test, &t_test);

    println!("Final Score (Sharpe Ratio): {:.4}", score);

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_flow() {
        // Basic integration test or component tests can be added here
        assert!(true);
    }
}
