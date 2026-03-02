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
