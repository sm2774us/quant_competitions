# Financial Modeling Challenge (Two Sigma)

## 📋 Overview

# Two Sigma Financial Modeling Challenge

## Overview
This challenge, originally hosted on Kaggle by Two Sigma, focuses on uncovering predictive value in an uncertain financial world. The goal is to forecast economic outcomes by predicting the value of a financial instrument's time-varying variable 'y' based on several anonymized features.

## Challenge Description
Financial markets are complex and driven by numerous factors. In this competition, participants are provided with a dataset containing:
- **`id`**: Unique identifier for each financial instrument.
- **`timestamp`**: Time representation of the observation.
- **`y`**: The target variable to be predicted.
- **Features**: Anonymized numerical features representing various market indicators.

The challenge is to build a predictive model that accurately forecasts 'y' for future timestamps using the provided features. The evaluation metric is typically based on the R-score (a variant of R-squared) between the predicted and actual values.

## Key Constraints
- **Anonymized Data**: Features have no explicit labels or explanations, requiring robust statistical and machine learning techniques for feature engineering and modeling.
- **Temporal Order**: Predictions must be made chronologically, simulating real-world trading where past data is used to predict future movements.
- **Time/Space Efficiency**: In a real-time trading environment, models must be efficient enough to process incoming data quickly.

## Solutions
This repository provides robust, high-performance implementations of the challenge in multiple languages:
- [Python Solution](./python)
- [C++ Solution](./cpp)
- [Rust Solution](./rust)

For a detailed comparison and Bazel-based unified entry point, see [SOLUTIONS.md](./SOLUTIONS.md).


## 🚀 Solutions

# Solutions Summary: Two Sigma Financial Modeling Challenge

This repository contains three robust, high-performance implementations of the Two Sigma Financial Modeling Challenge. All solutions are designed for 100% test coverage, efficiency, and ease of deployment.

## Unified Bazel Entry Point
A common Bazel configuration is provided to orchestrate the build and testing of all three solutions.

### Bazel Commands
- **Build and Run All Solutions**:
  ```bash
  bazel run //:python_solution
  bazel run //:cpp_solution
  bazel run //:rust_solution
  ```
- **Run All Tests**:
  ```bash
  bazel test //:python_tests //:cpp_tests //:rust_tests
  ```

## Solution Overviews

| Language | Framework | Key Features | Detailed Link |
|----------|-----------|--------------|---------------|
| **Python 3.13** | Scikit-Learn | Scikit-Learn Pipeline, Ridge Regression, Poetry, HDF5 | [Python Solution](./python) |
| **C++26** | Eigen 3.4.0 | High-performance Normal Equations, LDLT Solver, Binary Serialization | [C++ Solution](./cpp) |
| **Rust 1.84** | ndarray | Memory-safe implementation, Custom Linear Solver, Serde JSON | [Rust Solution](./rust) |

## Comparison of Implementations

### Python Implementation
- **Pros**: Rapid prototyping, rich ecosystem of machine learning tools (Scikit-Learn).
- **Cons**: Slower execution compared to compiled languages, higher memory overhead for large datasets.

### C++ Implementation
- **Pros**: Maximum performance, fine-grained memory management, low-latency prediction.
- **Cons**: Complex build configuration, manual memory/resource management.

### Rust Implementation
- **Pros**: Guaranteed memory safety, performance comparable to C++, modern tooling (Cargo).
- **Cons**: Steeper learning curve for complex linear algebra operations compared to Python/C++.

## Common Architecture
All three solutions follow a consistent architectural pattern:
1. **Data Generator**: Creates synthetic datasets (HDF5 or CSV) to ensure the code works out-of-the-box.
2. **Environment API**: Mimics the Kaggle environment for realistic evaluation.
3. **Financial Model**: Implements a robust Ridge Regression model with efficient solvers.
4. **CLI**: Provides a modern, easy-to-use interface for data generation, training, and evaluation.
5. **Dockerization**: Each solution is fully containerized for consistent deployment.


## 💻 Implementations

### Python

# Python Solution: Two Sigma Financial Modeling

## 1. Directory Structure
```
.
├── Dockerfile
├── pyproject.toml
├── README.md
├── src
│   └── two_sigma
│       ├── cli.py
│       ├── data_generator.py
│       ├── environment.py
│       ├── __init__.py
│       └── model.py
└── tests
    ├── __init__.py
    └── test_solution.py
```

## 2. Instructions

### Build and Run Locally
1. Install [Poetry](https://python-poetry.org/docs/#installation).
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Generate synthetic data:
   ```bash
   poetry run two-sigma generate-data --samples 1000 --output data/train.h5
   ```
4. Train the model:
   ```bash
   poetry run two-sigma train --data data/train.h5 --model-path models/model.joblib
   ```
5. Evaluate the model:
   ```bash
   poetry run two-sigma evaluate --data data/train.h5 --model-path models/model.joblib
   ```
6. Run tests:
   ```bash
   poetry run pytest --cov=src tests/
   ```

### Build and Run via Docker
1. Build the image:
   ```bash
   docker build -t two-sigma-python .
   ```
2. Run a command (e.g., generate data):
   ```bash
   docker run -v $(pwd)/data:/app/data two-sigma-python generate-data --output data/train.h5
   ```

## 3. Solution Explanation
The Python solution implements a robust machine learning pipeline for financial time-series prediction.
- **Data Generator**: Creates synthetic HDF5 data to ensure the solution works even without the original Kaggle dataset.
- **Environment API**: Mimics the Kaggle `kagglegym` API, allowing for iterative predictions on a per-timestamp basis.
- **Model Architecture**: Uses a Scikit-Learn `Pipeline` consisting of:
  - Custom `FeatureEngineering` (null counts, median imputation).
  - `SimpleImputer` for handling any remaining NaNs.
  - `Ridge` regression for efficient, regularized linear modeling.

### Complexity Analysis
- **Time Complexity**:
  - Training: $O(N 	imes F^2 + F^3)$ where $N$ is number of samples and $F$ is number of features.
  - Prediction: $O(F)$ per sample.
- **Space Complexity**:
  - $O(F)$ to store model weights.

### Architecture Diagram
```
[ CLI ] <--> [ Model ] <--> [ Environment ]
                ^                |
                |                v
        [ Pipeline ] <--> [ Data (HDF5) ]
```

## 4. UML Sequence Diagram
```
User -> CLI: run evaluate
CLI -> Model: load()
CLI -> Environment: make()
Environment -> CLI: obs
loop until done
    CLI -> Model: predict(obs.features)
    Model -> CLI: preds
    CLI -> Environment: step(preds)
    Environment -> CLI: next_obs, reward, done
end
CLI -> User: show score
```

## 5. Flowchart
```
[Start] --> [Generate Data] --> [Train Model]
                                     |
                                     v
[Finish] <-- [Display Score] <-- [Evaluate]
```

## 6. Tabulated Summary
| Feature | Implementation |
|---------|----------------|
| Language | Python 3.13 |
| Framework | Scikit-Learn |
| CLI | Click |
| Build Tool | Poetry |
| Testing | Pytest |
| Metric | R-score |


### Cpp

# C++ Solution: Two Sigma Financial Modeling

## 1. Directory Structure
```
.
├── CMakeLists.txt
├── Dockerfile
├── README.md
├── include
│   ├── common.h
│   ├── data_generator.h
│   ├── environment.h
│   └── model.h
├── src
│   ├── data_generator.cpp
│   ├── environment.cpp
│   ├── main.cpp
│   └── model.cpp
└── tests
    └── test_solution.cpp
```

## 2. Instructions

### Build and Run Locally
1. Ensure you have CMake (>= 3.25) and a C++20/23/26 compatible compiler (e.g., GCC 14).
2. Create build directory:
   ```bash
   mkdir build && cd build
   ```
3. Configure and build:
   ```bash
   cmake ..
   make
   ```
4. Generate synthetic data:
   ```bash
   ./two-sigma generate-data --samples 1000 --output data/train.csv
   ```
5. Train the model:
   ```bash
   ./two-sigma train --data data/train.csv --model-path models/model.bin
   ```
6. Evaluate the model:
   ```bash
   ./two-sigma evaluate --data data/train.csv --model-path models/model.bin
   ```
7. Run tests:
   ```bash
   ./two-sigma-tests
   ```

### Build and Run via Docker
1. Build the image:
   ```bash
   docker build -t two-sigma-cpp .
   ```
2. Run a command (e.g., generate data):
   ```bash
   docker run -v $(pwd)/data:/app/data two-sigma-cpp generate-data --output data/train.csv
   ```

## 3. Solution Explanation
The C++ solution provides a high-performance implementation of Ridge Regression using the Eigen library.
- **Data Generator**: Produces CSV datasets with customizable dimensions.
- **Environment API**: Handles data loading and provides a step-wise interface for evaluation, splitting data into training and testing sets by timestamp.
- **Model Architecture**:
  - Implements Ridge Regression via the Normal Equations: $(X^T X + \alpha I) w = X^T y$.
  - Uses `Eigen::LDLT` decomposition for efficient and numerically stable solution.
  - Supports binary serialization for saving and loading model weights.

### Complexity Analysis
- **Time Complexity**:
  - Training: $O(N 	imes F^2 + F^3)$ for matrix multiplication and decomposition.
  - Prediction: $O(F)$ per sample (vector dot product).
- **Space Complexity**:
  - $O(F)$ for model weights.

### Architecture Diagram
```
[ CLI ] <--> [ FinancialModel ] <--> [ Environment ]
                   ^                       |
                   |                       v
            [ Eigen Algebra ] <--> [ Data (CSV) ]
```

## 4. UML Sequence Diagram
```
User -> CLI: run evaluate
CLI -> Model: load(path)
CLI -> Environment: Environment(path)
Environment -> CLI: reset() -> obs
loop until done
    CLI -> Model: predict(obs.test_features)
    Model -> CLI: predictions
    CLI -> Environment: step(predictions) -> next_obs
end
CLI -> Environment: calculate_final_score()
CLI -> User: show score
```

## 5. Flowchart
```
[Start] --> [Generate CSV Data] --> [Train Ridge Model]
                                         |
                                         v
[Finish] <-- [Calculate R-Score] <-- [Evaluate Steps]
```

## 6. Tabulated Summary
| Feature | Implementation |
|---------|----------------|
| Language | C++26 |
| Algebra | Eigen 3.4.0 |
| CLI | CLI11 |
| Build Tool | CMake |
| Testing | Google Test |
| Format | CSV |


### Rust

# Rust Solution: Two Sigma Financial Modeling

## 1. Directory Structure
```
.
├── Cargo.toml
├── Dockerfile
├── README.md
├── src
│   ├── data_generator.rs
│   ├── environment.rs
│   ├── lib.rs
│   ├── main.rs
│   └── model.rs
└── tests
    └── test_solution.rs
```

## 2. Instructions

### Build and Run Locally
1. Ensure you have Rust and Cargo installed (version >= 1.84).
2. Build the project:
   ```bash
   cargo build --release
   ```
3. Generate synthetic data:
   ```bash
   cargo run --release -- generate-data --samples 1000 --output data/train.csv
   ```
4. Train the model:
   ```bash
   cargo run --release -- train --data data/train.csv --model-path models/model.json
   ```
5. Evaluate the model:
   ```bash
   cargo run --release -- evaluate --data data/train.csv --model-path models/model.json
   ```
6. Run tests:
   ```bash
   cargo test
   ```

### Build and Run via Docker
1. Build the image:
   ```bash
   docker build -t two-sigma-rust .
   ```
2. Run a command (e.g., generate data):
   ```bash
   docker run -v $(pwd)/data:/app/data two-sigma-rust generate-data --output data/train.csv
   ```

## 3. Solution Explanation
The Rust solution provides a type-safe and memory-efficient implementation using the `ndarray` crate.
- **Data Generator**: Utilizes the `rand` crate to produce synthetic financial data in CSV format.
- **Environment API**: Mimics the Kaggle environment, providing a streaming interface for predictions.
- **Model Architecture**:
  - Implements Ridge Regression using the Normal Equations.
  - Features a custom linear system solver using Gaussian elimination with partial pivoting for robustness without external BLAS dependencies.
  - Uses `serde` for JSON serialization of model weights.

### Complexity Analysis
- **Time Complexity**:
  - Training: $O(N 	imes F^2 + F^3)$ for matrix operations and solving the linear system.
  - Prediction: $O(F)$ per sample.
- **Space Complexity**:
  - $O(F)$ for model weights.

### Architecture Diagram
```
[ CLI (Clap) ] <--> [ FinancialModel ] <--> [ Environment ]
                         ^                       |
                         |                       v
                  [ Ndarray Math ] <--> [ Data (CSV) ]
```

## 4. UML Sequence Diagram
```
User -> CLI: run evaluate
CLI -> Model: load(path)
CLI -> Environment: new(path)
Environment -> CLI: reset() -> obs
loop until done
    CLI -> Model: predict(obs.test_features)
    Model -> CLI: predictions
    CLI -> Environment: step(predictions) -> next_obs
end
CLI -> Environment: calculate_final_score()
CLI -> User: show score
```

## 5. Flowchart
```
[Start] --> [Generate CSV] --> [Train Ridge (Rust)]
                                      |
                                      v
[Finish] <-- [Score] <-- [Evaluate Environment]
```

## 6. Tabulated Summary
| Feature | Implementation |
|---------|----------------|
| Language | Rust 1.84 |
| Algebra | ndarray |
| CLI | clap |
| Build Tool | Cargo |
| Testing | Cargo Test |
| Serialization | Serde (JSON) |


