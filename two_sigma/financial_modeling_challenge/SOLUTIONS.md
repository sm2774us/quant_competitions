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
