import click
import pandas as pd
import numpy as np
import os
from .processors import TwoSigmaDataLoader, TwoSigmaPreprocessor
from .models import TwoSigmaModel, TwoSigmaEvaluator

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Two Sigma Stock News Challenge - Python Solution"""
    if ctx.invoked_subcommand is None:
        pass

@main.command()
@click.option('--market', type=click.Path(exists=True), help='Path to market data (CSV/PKL)')
@click.option('--news', type=click.Path(exists=True), help='Path to news data (CSV/PKL)')
@click.option('--train-cutoff', default='2010-01-01', help='Date to start training from')
def run(market, news, train_cutoff):
    """Run the training, prediction and evaluation pipeline"""
    if not market or not news:
        click.echo("Error: Market and News data paths are required.")
        return

    click.echo(f"Loading data from {market} and {news}...")
    loader = TwoSigmaDataLoader()
    market_df = loader.load_market_data(market)
    news_df = loader.load_news_data(news)

    click.echo(f"Preprocessing data with cutoff {train_cutoff}...")
    processor = TwoSigmaPreprocessor(train_cutoff=train_cutoff)
    merged_df = processor.process(market_df, news_df)

    # Simple train-test split (80/20)
    split_idx = int(len(merged_df) * 0.8)
    train_df = merged_df[:split_idx]
    test_df = merged_df[split_idx:]

    # Define features
    features = ['returnsClosePrevRaw1', 'returnsOpenPrevRaw1', 'returnsClosePrevMktres1',
                'returnsOpenPrevMktres1', 'returnsClosePrevMktres10', 'returnsOpenPrevMktres10',
                'sentimentNegative', 'sentimentNeutral', 'sentimentPositive', 'relevance', 'wordCount']
    target = 'returnsOpenNextMktres10'
    universe = 'universe'

    click.echo("Training model...")
    model = TwoSigmaModel()
    X_train = train_df[features].values
    y_train = train_df[target].values
    model.train(X_train, y_train)

    click.echo("Predicting and Evaluating...")
    X_test = test_df[features].values
    y_test = test_df[target].values
    u_test = test_df[universe].values
    
    predictions = model.predict(X_test)
    test_df = test_df.copy()
    test_df['confidenceValue'] = predictions

    evaluator = TwoSigmaEvaluator()
    score = evaluator.evaluate_with_time(test_df, 'confidenceValue', target, universe)
    
    click.echo(f"Final Score (Sharpe Ratio): {score:.4f}")

if __name__ == '__main__':
    main()
