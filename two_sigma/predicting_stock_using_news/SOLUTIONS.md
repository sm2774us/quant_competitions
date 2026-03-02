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
