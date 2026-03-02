import pytest
import pandas as pd
import numpy as np
import os
from unittest.mock import MagicMock, patch
from two_sigma_news.processors import TwoSigmaDataLoader, TwoSigmaPreprocessor
from two_sigma_news.models import TwoSigmaModel, TwoSigmaEvaluator

@pytest.fixture
def mock_market_data():
    return pd.DataFrame({
        'time': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-02']),
        'assetName': ['Apple Inc', 'Google', 'Apple Inc'],
        'open': [100.0, 200.0, 105.0],
        'close': [102.0, 198.0, 107.0],
        'returnsClosePrevRaw1': [0.01, -0.01, 0.02],
        'returnsOpenPrevRaw1': [0.01, -0.01, 0.02],
        'returnsClosePrevMktres1': [0.01, -0.01, 0.02],
        'returnsOpenPrevMktres1': [0.01, -0.01, 0.02],
        'returnsClosePrevMktres10': [0.05, -0.05, 0.06],
        'returnsOpenPrevMktres10': [0.05, -0.05, 0.06],
        'returnsOpenNextMktres10': [0.02, -0.02, 0.01],
        'universe': [1, 1, 1]
    })

@pytest.fixture
def mock_news_data():
    return pd.DataFrame({
        'time': pd.to_datetime(['2024-01-01', '2024-01-01', '2024-01-02']),
        'assetName': ['Apple Inc', 'Google', 'Apple Inc'],
        'sentimentNegative': [0.1, 0.2, 0.05],
        'sentimentNeutral': [0.8, 0.6, 0.9],
        'sentimentPositive': [0.1, 0.2, 0.05],
        'relevance': [0.9, 0.8, 1.0],
        'wordCount': [500, 400, 600]
    })

def test_data_loader(tmp_path):
    loader = TwoSigmaDataLoader()
    df = pd.DataFrame({'a': [1]})
    csv_path = tmp_path / "test.csv"
    df.to_csv(csv_path, index=False)
    
    loaded_df = loader.load_market_data(str(csv_path))
    assert len(loaded_df) == 1
    assert loaded_df.iloc[0]['a'] == 1

def test_preprocessor(mock_market_data, mock_news_data):
    processor = TwoSigmaPreprocessor(train_cutoff='2024-01-01')
    merged = processor.process(mock_market_data, mock_news_data)
    
    assert len(merged) == 3
    assert 'sentimentPositive' in merged.columns
    assert 'dailychange' in merged.columns
    # Check outlier handling
    assert merged.iloc[0]['dailychange'] == 102.0 / 100.0

def test_model():
    model = TwoSigmaModel(alpha=1.0)
    X = np.random.rand(10, 5)
    y = np.random.rand(10)
    model.train(X, y)
    preds = model.predict(X)
    assert len(preds) == 10
    assert np.all(preds >= -1) and np.all(preds <= 1)

def test_evaluator():
    evaluator = TwoSigmaEvaluator()
    preds = np.array([0.5, -0.5])
    targets = np.array([0.1, -0.1])
    universe = np.array([1, 1])
    
    score = evaluator.evaluate(preds, targets, universe)
    assert score > 0 # (0.05 + 0.05) / 0 -> handles sigma=0

def test_evaluator_with_time():
    evaluator = TwoSigmaEvaluator()
    df = pd.DataFrame({
        'time': [1, 1, 2, 2],
        'conf': [0.5, 0.6, -0.5, -0.4], # Vary conf slightly to avoid zero std
        'target': [0.1, 0.1, -0.1, -0.1],
        'universe': [1, 1, 1, 1]
    })
    score = evaluator.evaluate_with_time(df, 'conf', 'target', 'universe')
    assert score > 0

@patch('two_sigma_news.main.TwoSigmaDataLoader')
@patch('two_sigma_news.main.TwoSigmaPreprocessor')
@patch('two_sigma_news.main.TwoSigmaModel')
@patch('two_sigma_news.main.TwoSigmaEvaluator')
def test_main_run(mock_eval, mock_model, mock_proc, mock_loader, mock_market_data, mock_news_data):
    from click.testing import CliRunner
    from two_sigma_news.main import run
    
    mock_loader.return_value.load_market_data.return_value = mock_market_data
    mock_loader.return_value.load_news_data.return_value = mock_news_data
    
    # Preprocessor mock
    # Merge them to ensure all columns (sentiment, etc) are present for the main logic
    merged = pd.merge(mock_market_data, mock_news_data, on=['time', 'assetName'])
    mock_proc.return_value.process.return_value = merged
    
    # Model mock
    # Return an array matching the input length (X_test length)
    mock_model.return_value.predict.side_effect = lambda x: np.zeros(len(x))
    
    # Evaluator mock
    mock_eval.return_value.evaluate_with_time.return_value = 0.5
    
    runner = CliRunner()
    # Create real dummy files to satisfy click.Path(exists=True)
    with runner.isolated_filesystem():
        with open('m.csv', 'w') as f: f.write('dummy')
        with open('n.csv', 'w') as f: f.write('dummy')
        from two_sigma_news.main import main
        result = runner.invoke(main, ['run', '--market', 'm.csv', '--news', 'n.csv'])
        assert result.exit_code == 0
        assert "Final Score" in result.output
