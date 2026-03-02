import click
import os
from two_sigma.data_generator import DataGenerator
from two_sigma.environment import make
from two_sigma.model import FinancialModel

@click.group()
def cli():
    """Two Sigma Financial Modeling CLI."""
    pass

@cli.command()
@click.option('--samples', default=1000, help='Number of total samples.')
@click.option('--features', default=100, help='Number of technical features.')
@click.option('--instruments', default=50, help='Number of unique instrument IDs.')
@click.option('--output', default='data/train.h5', help='Output HDF5 path.')
def generate_data(samples, features, instruments, output):
    """Generates synthetic data for development and testing."""
    generator = DataGenerator(samples, features, instruments)
    generator.generate(output)

@cli.command()
@click.option('--data', default='data/train.h5', help='Path to training HDF5 file.')
@click.option('--model-path', default='models/model.joblib', help='Path to save trained model.')
def train(data, model_path):
    """Trains the financial model on the provided dataset."""
    if not os.path.exists(data):
        click.echo(f"Data file {data} not found. Generate it first using generate-data.")
        return
        
    env = make(data)
    model = FinancialModel()
    model.train(env.train)
    
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    click.echo(f"Successfully trained and saved model to {model_path}")

@cli.command()
@click.option('--data', default='data/train.h5', help='Path to HDF5 file.')
@click.option('--model-path', default='models/model.joblib', help='Path to trained model.')
def evaluate(data, model_path):
    """Evaluates the trained model using the environment API."""
    if not os.path.exists(data) or not os.path.exists(model_path):
        click.echo("Data or model not found. Ensure both are available.")
        return
        
    env = make(data)
    model = FinancialModel.load(model_path)
    
    observation = env.reset()
    while True:
        test_df = observation.features
        target_df = observation.target
        
        predictions = model.predict(test_df)
        target_df['y'] = predictions
        
        observation, reward, done, info = env.step(target_df)
        if done:
            click.echo(f"Evaluation complete. Public Score: {info['public_score']:.6f}")
            break

if __name__ == "__main__":
    cli()
