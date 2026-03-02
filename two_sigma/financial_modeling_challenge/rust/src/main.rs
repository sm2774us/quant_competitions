use clap::{Parser, Subcommand};
use two_sigma_financial_modeling::data_generator::DataGenerator;
use two_sigma_financial_modeling::environment::Environment;
use two_sigma_financial_modeling::model::FinancialModel;
use std::error::Error;

#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Generates synthetic data
    GenerateData {
        #[arg(long, default_value_t = 1000)]
        samples: usize,
        #[arg(long, default_value_t = 100)]
        features: usize,
        #[arg(long, default_value_t = 50)]
        instruments: usize,
        #[arg(long, default_value = "data/train.csv")]
        output: String,
    },
    /// Trains the model
    Train {
        #[arg(long, default_value = "data/train.csv")]
        data: String,
        #[arg(long, default_value = "models/model.json")]
        model_path: String,
    },
    /// Evaluates the model
    Evaluate {
        #[arg(long, default_value = "data/train.csv")]
        data: String,
        #[arg(long, default_value = "models/model.json")]
        model_path: String,
    },
}

fn main() -> Result<(), Box<dyn Error>> {
    let cli = Cli::parse();

    match &cli.command {
        Commands::GenerateData { samples, features, instruments, output } => {
            let gen = DataGenerator::new(*samples, *features, *instruments);
            gen.generate(output)?;
        }
        Commands::Train { data, model_path } => {
            let mut env = Environment::new(data)?;
            let obs = env.reset();
            let mut model = FinancialModel::new(1.0);
            model.train(&obs.train_features, &obs.train_target);
            model.save(model_path)?;
        }
        Commands::Evaluate { data, model_path } => {
            let mut env = Environment::new(data)?;
            let model = FinancialModel::load(model_path)?;
            let mut obs = Some(env.reset());
            while let Some(o) = obs {
                let predictions = model.predict(&o.test_features);
                let (next_obs, _, _) = env.step(predictions);
                obs = next_obs;
            }
            println!("Evaluation complete. Final Score: {:.6}", env.calculate_final_score());
        }
    }

    Ok(())
}
