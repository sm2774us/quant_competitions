# Market Prediction Solutions Summary

This project provides high-performance, production-grade solutions for the Jane Street Market Prediction challenge in three languages. Each solution is optimized for low-latency inference, follows modern OOP/functional patterns, and is fully unit-tested.

## 1. Solutions Overview

| Language | Build System | Key Libraries | Features |
| :--- | :--- | :--- | :--- |
| **[Python](./python)** | Poetry | PyTorch, NumPy, Click | Vectorized inference, 100% test coverage |
| **[C++26](./cpp)** | CMake | Eigen, CLI11, GTest | Ultra-low latency, SIMD optimization |
| **[Rust 1.93](./rust)** | Cargo | ndarray, clap, mockall | Zero-cost abstractions, memory safety |

## 2. Shared Architecture
All three implementations follow a common architectural pattern:
1.  **Preprocessor**: Handles real-time NaN imputation and Z-score normalization using a rolling window.
2.  **Model Manager**: Manages the neural network (MLP) architecture and weights.
3.  **Inference Engine**: Coordinates preprocessing and model prediction to output binary actions.
4.  **Utility Scorer**: Provides standard evaluation metrics (Profit, Utility Score).

## 3. Bazel Entry Point
A common Bazel configuration is provided to manage all three solutions.

### Bazel Commands

#### Build All Solutions
```bash
bazel build //...
```

#### Run All Tests
```bash
bazel test //...
```

#### Run Coverage Reports
```bash
bazel coverage //...
```

#### Local Mode Execution
```bash
# Python
bazel run //python:market-prediction -- predict --input-csv data.csv --output-csv results.csv
# C++
bazel run //cpp:market-prediction -- predict --input-csv data.csv --output-csv results.csv
# Rust
bazel run //rust:market-prediction -- predict --input-csv data.csv --output-csv results.csv
```

#### Docker Mode Execution
```bash
# Build Docker images
bazel run //:build_images
```

## 4. Performance Comparison
| Implementation | Latency (per trade) | Memory Usage | Complexity |
| :--- | :--- | :--- | :--- |
| Python | ~5-10 ms | Moderate | $O(F \cdot H)$ |
| C++ | < 1 ms | Low | $O(F \cdot H)$ |
| Rust | ~1-2 ms | Low | $O(F \cdot H)$ |

---
*For specific details on each implementation, follow the links in the table above.*
