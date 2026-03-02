mod engine;
mod models;
mod preprocessor;
mod scorer;

use crate::engine::InferenceEngine;
use crate::models::ModelManager;
use crate::preprocessor::MarketPreprocessor;
use crate::scorer::{Trade, UtilityScorer};
use clap::{Parser, Subcommand};
use ndarray::Array1;
use std::fs::File;
use std::io::{BufRead, BufReader, Write};

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run inference on a CSV dataset
    Predict {
        #[arg(long)]
        input_csv: String,
        #[arg(long)]
        output_csv: String,
        #[arg(long, default_value = "preprocessing/params.json")]
        params_json: String,
        #[arg(long)]
        weights_path: Option<String>,
        #[arg(long, default_value_t = 0.5)]
        threshold: f64,
    },
    /// Validate model and calculate utility score
    Validate {
        #[arg(long)]
        input_csv: String,
        #[arg(long, default_value = "preprocessing/params.json")]
        params_json: String,
        #[arg(long)]
        weights_path: Option<String>,
    },
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Predict { input_csv, output_csv, params_json, weights_path, threshold } => {
            let mut model_manager = ModelManager::new(136);
            if let Some(w) = weights_path {
                model_manager.load_weights(w)?;
            }
            
            let mut preprocessor = MarketPreprocessor::new(130, 100);
            preprocessor.load_state(params_json)?;
            
            let mut engine = InferenceEngine::new(model_manager, preprocessor, threshold);
            
            let file = File::open(input_csv)?;
            let reader = BufReader::new(file);
            let mut lines = reader.lines();
            
            let header = lines.next().ok_or("Empty file")??;
            let mut out = File::create(&output_csv)?;
            writeln!(out, "{},action", header)?;

            for line in lines {
                let l = line?;
                let values: Vec<f64> = l.split(',')
                    .map(|v| v.parse().unwrap_or(f64::NAN))
                    .collect();
                
                // Assuming features are first 130 columns or mapped
                if values.len() >= 130 {
                    let features = Array1::from_vec(values[..130].to_vec());
                    let action = engine.predict_action(&features);
                    writeln!(out, "{},{}", l, action)?;
                }
            }
            println!("Predictions saved to {}.", output_csv);
        }
        Commands::Validate { input_csv, params_json, weights_path } => {
            let mut model_manager = ModelManager::new(136);
            if let Some(w) = weights_path {
                model_manager.load_weights(w)?;
            }
            let mut preprocessor = MarketPreprocessor::new(130, 100);
            preprocessor.load_state(params_json)?;
            
            let mut engine = InferenceEngine::new(model_manager, preprocessor, 0.5);
            
            let file = File::open(input_csv)?;
            let reader = BufReader::new(file);
            let mut trades = Vec::new();
            
            for line in reader.lines().skip(1) {
                let l = line?;
                let values: Vec<f64> = l.split(',')
                    .map(|v| v.parse().unwrap_or(f64::NAN))
                    .collect();
                
                if values.len() >= 130 {
                    let features = Array1::from_vec(values[..130].to_vec());
                    let action = engine.predict_action(&features);
                    // Mock extraction of metadata for Trade struct
                    trades.push(Trade { date: 0, weight: 1.0, resp: 0.1, action });
                }
            }
            
            let summary = UtilityScorer::summary_table(&trades);
            println!("{}", serde_json::to_string_pretty(&summary)?);
        }
    }

    Ok(())
}
