import os
import pytest
import pandas as pd
import numpy as np
from click.testing import CliRunner
from two_sigma.data_generator import DataGenerator
from two_sigma.environment import make
from two_sigma.model import FinancialModel
from two_sigma.cli import cli

@pytest.fixture
def temp_data(tmp_path):
    """Fixture to create a temporary HDF5 dataset."""
    data_path = tmp_path / "test_train.h5"
    generator = DataGenerator(n_samples=200, n_features=10, n_instruments=5)
    generator.generate(str(data_path))
    return str(data_path)

def test_data_generator(temp_data):
    """Tests the synthetic data generation."""
    assert os.path.exists(temp_data)
    df = pd.read_hdf(temp_data, 'train')
    assert len(df) == 200
    assert 'y' in df.columns
    assert 'timestamp' in df.columns

def test_environment(temp_data):
    """Tests the Kaggle-like environment API."""
    env = make(temp_data)
    obs = env.reset()
    assert obs is not None
    assert isinstance(obs.train, pd.DataFrame)
    assert len(obs.features) > 0
    
    target = obs.target
    target['y'] = 0.01
    
    next_obs, reward, done, info = env.step(target)
    assert not done
    assert next_obs is not None

def test_model_training_and_prediction(temp_data):
    """Tests the model training and prediction lifecycle."""
    env = make(temp_data)
    model = FinancialModel()
    model.train(env.train)
    
    obs = env.reset()
    preds = model.predict(obs.features)
    assert len(preds) == len(obs.features)

def test_cli_flow(temp_data, tmp_path):
    """Tests the full CLI workflow."""
    runner = CliRunner()
    model_path = tmp_path / "model.joblib"
    
    # Train
    result = runner.invoke(cli, ['train', '--data', temp_data, '--model-path', str(model_path)])
    assert result.exit_code == 0
    assert "Model training complete" in result.output
    
    # Evaluate
    result = runner.invoke(cli, ['evaluate', '--data', temp_data, '--model-path', str(model_path)])
    assert result.exit_code == 0
    assert "Evaluation complete" in result.output

def test_cli_generate(tmp_path):
    """Tests the generate-data CLI command."""
    runner = CliRunner()
    output = tmp_path / "gen.h5"
    result = runner.invoke(cli, ['generate-data', '--samples', '100', '--output', str(output)])
    assert result.exit_code == 0
    assert os.path.exists(output)

def test_cli_missing_data():
    """Tests CLI behavior when data is missing."""
    runner = CliRunner()
    result = runner.invoke(cli, ['train', '--data', 'non_existent.h5'])
    assert "not found" in result.output
