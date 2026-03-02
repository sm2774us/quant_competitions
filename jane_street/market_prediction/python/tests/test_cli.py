import os
import pandas as pd
import pytest
from click.testing import CliRunner
from market_prediction.cli import cli

def test_cli_predict(mock_market_data, tmp_path):
    # Save mock data to CSV
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    mock_market_data.to_csv(input_path, index=False)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['predict', '--input-csv', str(input_path), '--output-csv', str(output_path)])
    
    assert result.exit_code == 0
    assert os.path.exists(output_path)
    
    # Check if 'action' column exists in output
    out_df = pd.read_csv(output_path)
    assert 'action' in out_df.columns

def test_cli_validate(mock_market_data, tmp_path):
    # Save mock data to CSV
    input_path = tmp_path / "validate.csv"
    mock_market_data.to_csv(input_path, index=False)
    
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', '--input-csv', str(input_path)])
    
    assert result.exit_code == 0
    # Output should be JSON
    import json
    data = json.loads(result.output)
    assert "utility_score" in data
