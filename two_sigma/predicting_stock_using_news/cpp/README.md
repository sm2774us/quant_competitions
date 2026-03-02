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
