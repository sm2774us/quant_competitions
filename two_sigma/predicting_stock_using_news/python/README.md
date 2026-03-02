# Python Solution: Two Sigma Stock News Challenge

This is a robust, time-efficient, and vector-optimized Python solution for the Two Sigma Stock News Challenge.

## Directory Structure (UNIX tree format)
```
.
├── Dockerfile
├── pyproject.toml
├── README.md
├── src
│   └── two_sigma_news
│       ├── __init__.py
│       ├── interfaces.py
│       ├── main.py
│       ├── models.py
│       └── processors.py
└── tests
    └── test_two_sigma.py
```

## How to Build and Run Locally
1.  **Install Poetry** (if not already installed):
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
2.  **Install Dependencies**:
    ```bash
    poetry install
    ```
3.  **Run the CLI**:
    ```bash
    poetry run two-sigma-news run --market path/to/market.csv --news path/to/news.csv
    ```
4.  **Run Tests**:
    ```bash
    poetry run pytest tests/ --cov=src/two_sigma_news
    ```

## How to Build and Run via Docker
1.  **Build the Image**:
    ```bash
    docker build -t two-sigma-python .
    ```
2.  **Run the Container**:
    ```bash
    docker run -v $(pwd)/data:/app/data two-sigma-python run --market /app/data/market.csv --news /app/data/news.csv
    ```

## Solution Explanation, Complexity, and Architecture

### Solution Architecture
The solution follows an Object-Oriented approach with clear separation of concerns:
- **Interfaces**: Define the contract for data loading, preprocessing, modeling, and evaluation.
- **Processors**: Handles data cleaning and vectorized merging of market and news datasets.
- **Models**: Implements a high-performance Ridge model optimized for financial return predictions.
- **Evaluator**: Calculates the Sharpe-like ratio score using vectorized pandas/numpy operations.

### ASCII Diagram
```text
[Market Data] 
               > [TwoSigmaPreprocessor] -> [Merged DataFrame] -> [TwoSigmaModel] -> [Confidence Values]
[News Data]   /                                      ^                                    |
                                                     |                                    v
                                               [Targets/Universe] ----------------> [TwoSigmaEvaluator]
                                                                                          |
                                                                                          v
                                                                                    [Sharpe Score]
```

### Time and Space Complexity
- **Time Complexity**: 
    - Preprocessing: $O(N + M \log M)$ where $N$ is market rows, $M$ is news rows (due to grouping and merging).
    - Training: $O(N_{samples} \cdot K^2)$ where $K$ is the number of features (standard Ridge training).
    - Prediction: $O(N_{test} \cdot K)$.
- **Space Complexity**: $O(N + M)$ to hold the dataframes and model parameters.

## UML Sequence Diagram
```text
User -> CLI: run(market_path, news_path)
CLI -> DataLoader: load_market_data(market_path)
CLI -> DataLoader: load_news_data(news_path)
CLI -> Preprocessor: process(market_df, news_df)
Preprocessor -> Preprocessor: Filter & Merge
Preprocessor --> CLI: merged_df
CLI -> Model: train(X_train, y_train)
CLI -> Model: predict(X_test)
Model --> CLI: predictions
CLI -> Evaluator: evaluate_with_time(test_df)
Evaluator --> CLI: score
CLI -> User: Print Score
```

## Flowchart Diagram
```text
START
  |
[Load Market & News Data]
  |
[Clean & Filter Data]
  |
[Aggregate News & Merge with Market]
  |
[Split Data into Train/Test]
  |
[Train Ridge Model]
  |
[Predict Confidence Values]
  |
[Calculate Sharpe Score]
  |
END
```

## Tabulated Summary
| Component | Implementation | Optimization |
|---|---|---|
| Language | Python 3.13 | Native vector support |
| Data Handling | Pandas 2.2 | Vectorized operations |
| ML Model | Ridge (Scikit-Learn) | $L_2$ Regularized |
| Testing | Pytest | 100% Coverage target |
| CLI | Click | Modern & Robust |
