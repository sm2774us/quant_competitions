import click
import pandas as pd
import numpy as np
import torch
import json
from .engine import InferenceEngine
from .models import ModelManager
from .preprocessor import MarketPreprocessor
from .scorer import UtilityScorer

@click.group()
def cli():
    """Jane Street Market Prediction CLI."""
    pass

@cli.command()
@click.option('--input-csv', required=True, help='Path to input CSV file')
@click.option('--output-csv', required=True, help='Path to output results')
@click.option('--threshold', default=0.5, help='Prediction threshold')
def predict(input_csv, output_csv, threshold):
    """Run inference on a CSV dataset."""
    df = pd.read_csv(input_csv)
    
    # Identify feature columns (feature_0 to feature_129)
    feature_cols = [f'feature_{i}' for i in range(130)]
    
    # Initialize Engine
    model_manager = ModelManager()
    preprocessor = MarketPreprocessor()
    engine = InferenceEngine(model_manager, preprocessor, threshold=threshold)
    
    # Run batch prediction
    features = df[feature_cols].values
    actions = engine.batch_predict(features)
    
    df['action'] = actions
    df.to_csv(output_csv, index=False)
    click.echo(f"Predictions saved to {output_csv}")

@cli.command()
@click.option('--input-csv', required=True, help='Path to validation CSV file')
def validate(input_csv):
    """Validate model and calculate utility score."""
    df = pd.read_csv(input_csv)
    
    feature_cols = [f'feature_{i}' for i in range(130)]
    
    # Initialize Engine
    model_manager = ModelManager()
    preprocessor = MarketPreprocessor()
    engine = InferenceEngine(model_manager, preprocessor)
    
    # Run batch prediction
    features = df[feature_cols].values
    actions = engine.batch_predict(features)
    df['action'] = actions
    
    # Calculate utility
    stats = UtilityScorer.summary_table(df)
    
    # Convert numpy types to native python types for JSON serialization
    serializable_stats = {k: float(v) if isinstance(v, (np.floating, np.integer)) else v for k, v in stats.items()}
    
    click.echo(json.dumps(serializable_stats, indent=2))

if __name__ == "__main__":  # pragma: no cover
    cli()
