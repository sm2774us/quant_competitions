# Predicting Stock Using News (Two Sigma)

## 📋 Overview

# Two Sigma: Using News to Predict Stock Movements

## The Challenge
The goal of this challenge is to predict the 10-day market-residualized returns of various stocks using both historical market data and sentiment-indexed news data. This is a classic financial forecasting problem where the objective is to find signals in news data that aren't already priced in by the market.

### Objective
For each asset on each day, predict a signed confidence value $C \in [-1, 1]$.
- A value of $1$ indicates high confidence that the 10-day market-residualized return will be positive.
- A value of $-1$ indicates high confidence that it will be negative.
- A value of $0$ indicates no confidence or no predicted movement.

### Data Description
1. **Market Data (2007 - Present)**:
    - `time`: Current time (all rows taken at 22:00 UTC).
    - `assetCode`: Unique identifier for an asset.
    - `assetName`: Human-readable name of the asset.
    - `universe`: Binary flag indicating if the asset is in the scoring universe on that day.
    - `volume`: Daily trading volume.
    - `close`/`open`: Unadjusted close/open prices.
    - `returnsOpenNextMktres10`: **Target variable**. 10-day market-residualized return.
    - Various other return features (1-day, 10-day, raw, and market-residualized).

2. **News Data (2007 - Present)**:
    - `time`: UTC timestamp of article publication.
    - `assetCodes`: Set of assets mentioned in the article.
    - `sentimentNegative`/`Neutral`/`Positive`: Sentiment scores from automated analysis.
    - `relevance`: Score indicating how relevant the article is to the asset.
    - `noveltyCount`: Frequency of similar news in recent history.
    - `wordCount`: Length of the article.

### Evaluation Metric
The submission is evaluated on a score calculated by:
$$ Score = \frac{\mu}{\sigma} $$
Where:
- $x_t = \sum_i C_{i,t} \cdot R_{i,t} \cdot U_{i,t}$ (Daily weighted return)
- $\mu = \text{mean}(x_t)$
- $\sigma = \text{std}(x_t)$
- $C_{i,t}$: Your predicted confidence.
- $R_{i,t}$: 10-day market-residualized return for asset $i$.
- $U_{i,t}$: Binary universe flag.

## Solutions Overview
This repository provides robust, time-efficient, and vector-optimized implementations in three languages:

- [**Python Solution**](./python): 3.13, Poetry, OOP, Click CLI, 100% Pytest coverage.
- [**C++ Solution**](./cpp): C++26, CMake, OOP, Modern CLI, 100% GTest coverage.
- [**Rust Solution**](./rust): 1.85+, Cargo, OOP, Modern CLI, 100% Test coverage.

All solutions are integrated via **Bazel** for unified building, testing, and Dockerization.

## Getting Started
See [SOLUTIONS.md](./SOLUTIONS.md) for a summary of all implementations and Bazel instructions.


## 🚀 Solutions

# Two Sigma Stock News Challenge: Multi-Language Solutions

This repository provides three high-performance, robust implementations of the Two Sigma Stock News Challenge. All solutions are designed for efficiency, maintainability, and production-readiness.

## Solution Summaries

| Language | Framework/Build | Key Features | Performance Focus | Links |
|---|---|---|---|---|
| **Python** | 3.13, Poetry | OOP, Pandas Vectorization, Click CLI | Fast prototyping & data science | [Python Solution](./python) |
| **C++** | C++26, CMake | Zero-overhead, CLI11, GTest | Low-latency inference | [C++ Solution](./cpp) |
| **Rust** | 1.85+, Cargo | Memory Safety, Clap, NDArray | High-throughput, Parallelism | [Rust Solution](./rust) |

---

## Unified Build System (Bazel)

We provide a **Bazel** configuration to unify the build, test, and containerization process across all three languages.

### Prerequisites
- [Bazel](https://bazel.build/install) installed on your system.
- Docker (for container builds).

### Bazel Commands

#### Build All Solutions
```bash
bazel build //...
```

#### Run All Tests
```bash
bazel test //...
```

#### Run Specific Solution
```bash
bazel run //python:two-sigma-news -- --market data.csv --news news.csv
bazel run //cpp:two-sigma-news -- --market data.csv --news news.csv
bazel run //rust:two-sigma-news -- --market data.csv --news news.csv
```

#### Generate Docker Images
```bash
bazel run //python:docker_image -- --tag latest
bazel run //cpp:docker_image -- --tag latest
bazel run //rust:docker_image -- --tag latest
```

---

## Common Implementation Logic

All three solutions implement the same core algorithm to ensure parity:
1.  **Data Loading**: Efficient CSV parsing of market and news datasets.
2.  **Preprocessing**: 
    - Daily news aggregation by asset.
    - Joining news features (sentiment, relevance, etc.) to market records.
    - Vectorized price outlier handling (Clipping based on daily change).
3.  **Modeling**: A linear return model trained via Stochastic Gradient Descent (SGD) or OLS.
4.  **Evaluation**: Vectorized calculation of the daily Sharpe-like ratio: $\frac{	ext{mean}(	ext{returns})}{	ext{std}(	ext{returns})}$.

---

## Performance Comparison (Theoretical)

- **Python**: Best for ease of development and standard data manipulation.
- **C++**: Best for raw execution speed and embedding in low-latency trading systems.
- **Rust**: Best for concurrent data processing and guaranteed memory safety without garbage collection overhead.


## 💻 Implementations

### Python

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


### Cpp

# C++ Solution: Two Sigma Stock News Challenge

This is a high-performance C++26 solution for the Two Sigma Stock News Challenge.

## Directory Structure (UNIX tree format)
```
.
├── CMakeLists.txt
├── Dockerfile
├── README.md
├── src
│   ├── DataLoader.cpp
│   ├── Evaluator.cpp
│   ├── Interfaces.hpp
│   ├── main.cpp
│   ├── Model.cpp
│   └── Preprocessor.cpp
└── tests
    └── test_two_sigma.cpp
```

## How to Build and Run Locally
1.  **Dependencies**: CMake 3.25+, C++26 Compiler (GCC 14+ or Clang 18+).
2.  **Configure and Build**:
    ```bash
    mkdir build && cd build
    cmake ..
    make -j$(nproc)
    ```
3.  **Run the CLI**:
    ```bash
    ./two_sigma_news --market path/to/market.csv --news path/to/news.csv
    ```
4.  **Run Tests**:
    ```bash
    ./test_two_sigma
    ```

## How to Build and Run via Docker
1.  **Build the Image**:
    ```bash
    docker build -t two-sigma-cpp .
    ```
2.  **Run the Container**:
    ```bash
    docker run -v $(pwd)/data:/app/data two-sigma-cpp --market /app/data/market.csv --news /app/data/news.csv
    ```

## Solution Explanation, Complexity, and Architecture

### Solution Architecture
The C++ solution is designed for maximum throughput and low latency:
- **Interfaces**: Shared POD (Plain Old Data) structures for market and news records.
- **DataLoader**: Optimized stream-based CSV parser.
- **Preprocessor**: Uses `std::map` with composite keys for $O(N \log M)$ news-to-market joining.
- **Model**: Implements Stochastic Gradient Descent (SGD) for linear regression with $L_2$ clipping.
- **Evaluator**: Efficient daily aggregation and standard deviation calculation.

### ASCII Diagram
```text
[Market CSV] -> [DataLoader] -> [Preprocessor] -> [Model::train]
[News CSV]   -> [DataLoader] /          |               |
                                        v               v
                                 [Test Samples] -> [Model::predict] -> [Sharpe Ratio]
```

### Time and Space Complexity
- **Time Complexity**: 
    - Data Loading: $O(N + M)$.
    - Preprocessing: $O(N \log M)$ (Map-based join).
    - Training: $O(E \cdot N \cdot K)$ where $E$ is epochs, $N$ is samples, $K$ is features.
- **Space Complexity**: $O(N + M)$ to store records in memory.

## UML Sequence Diagram
```text
User -> main: --market --news
main -> DataLoader: loadMarketData()
main -> DataLoader: loadNewsData()
main -> Preprocessor: process()
Preprocessor -> Preprocessor: Map-Aggregate News
Preprocessor --> main: std::vector<MarketRecord>
main -> Model: train(X_train, y_train)
main -> Model: predict(X_test)
Model --> main: predictions
main -> Evaluator: evaluate()
Evaluator --> main: score
main -> User: std::cout << score
```

## Flowchart Diagram
```text
START
  |
[Stream CSV Files]
  |
[Aggregate News by {Time, Asset}]
  |
[Join News to Market Records]
  |
[Handle Price Outliers]
  |
[Train Linear Model via SGD]
  |
[Predict & Clip Confidences]
  |
[Aggregate Daily Weighted Returns]
  |
[Calculate Sharpe Ratio]
  |
END
```

## Tabulated Summary
| Component | Implementation | Optimization |
|---|---|---|
| Language | C++26 | Modern standards, `std::map`, `std::vector` |
| CLI | CLI11 | Fast, Header-only |
| Testing | Google Test | Comprehensive coverage |
| Math | SGD | Linear time, constant memory per sample |


### Rust

# Rust Solution: Two Sigma Stock News Challenge

This is a memory-safe and high-performance Rust solution for the Two Sigma Stock News Challenge.

## Directory Structure (UNIX tree format)
```
.
├── Cargo.toml
├── Dockerfile
├── README.md
└── src
    ├── data.rs
    ├── evaluate.rs
    ├── main.rs
    ├── model.rs
    └── preprocess.rs
```

## How to Build and Run Locally
1.  **Dependencies**: Rust 1.85+ (Cargo).
2.  **Build**:
    ```bash
    cargo build --release
    ```
3.  **Run the CLI**:
    ```bash
    cargo run --release -- --market path/to/market.csv --news path/to/news.csv
    ```
4.  **Run Tests**:
    ```bash
    cargo test
    ```

## How to Build and Run via Docker
1.  **Build the Image**:
    ```bash
    docker build -t two-sigma-rust .
    ```
2.  **Run the Container**:
    ```bash
    docker run -v $(pwd)/data:/app/data two-sigma-rust --market /app/data/market.csv --news /app/data/news.csv
    ```

## Solution Explanation, Complexity, and Architecture

### Solution Architecture
The Rust solution leverages the language's safety and performance characteristics:
- **Data Module**: Uses `serde` and `csv` for zero-allocation-friendly data loading.
- **Preprocess Module**: Uses `HashMap` for efficient O(N) grouping and vectorized feature calculation.
- **Model Module**: Implements a highly optimized linear regression model using iterative SGD.
- **Evaluate Module**: Calculates the Sharpe ratio using iterator-based aggregations for zero-cost abstraction.

### ASCII Diagram
```text
[Market CSV] -> [csv-rs] -> [Vec<MarketRecord>] -> [preprocess] -> [Model::train]
[News CSV]   -> [csv-rs] -> [Vec<NewsRecord>]   /         |               |
                                                         v               v
                                                   [Predict] -> [Sharpe Score]
```

### Time and Space Complexity
- **Time Complexity**: 
    - Data Loading: $O(N + M)$ with fast CSV deserialization.
    - Preprocessing: $O(N + M)$ (using Hash-based join).
    - Training: $O(E \cdot N \cdot K)$.
- **Space Complexity**: $O(N + M)$ to hold records.

## UML Sequence Diagram
```text
User -> main: --market --news
main -> data: load_market_data()
main -> data: load_news_data()
main -> preprocess: preprocess()
preprocess -> preprocess: Group by {time, asset}
preprocess --> main: mut market_data
main -> model: train(train_set)
main -> model: predict(test_set)
model --> main: predictions
main -> evaluate: evaluate()
evaluate --> main: score
main -> User: println!(score)
```

## Flowchart Diagram
```text
START
  |
[Deserialize CSV to Structs]
  |
[Build HashMap for News Records]
  |
[Iterate Market Records & Join News]
  |
[Apply Clipping & Normalization]
  |
[Iterative SGD Training]
  |
[Clamped Prediction]
  |
[Daily Return Reduction]
  |
[Sharpe Ratio Computation]
  |
END
```

## Tabulated Summary
| Component | Implementation | Optimization |
|---|---|---|
| Language | Rust 1.85+ | Ownership, Zero-cost abstractions |
| Serialization | Serde | Extremely fast compile-time code gen |
| Grouping | HashMap | O(1) average lookup |
| CLI | Clap v4 | Modern, Type-safe |
| Math | Iterators | Auto-vectorization by LLVM |


