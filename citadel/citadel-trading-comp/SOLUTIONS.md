# Citadel Trading Competition Solutions

This repository contains robust, OOP-style trading bot implementations in three languages: Python, C++, and Rust. Each solution is fully optimized, 100% unit-tested, and supports both local and Docker-based execution.

## 🚀 Solutions Overview

| Language | Path | Build System | CLI Library | Testing Framework |
|----------|------|--------------|-------------|-------------------|
| **Python** | [./python/](./python/) | Poetry | Click | Pytest |
| **C++** | [./cpp/](./cpp/) | CMake | CLI11 | Google Test |
| **Rust** | [./rust/](./rust/) | Cargo | Clap | Cargo Test |

## 📦 Bazel Entry Point

A common Bazel configuration is provided to manage all three implementations. Use the following commands to build and test:

### Build All
```bash
# Build Python
bazel build //python:build
# Build C++
bazel build //cpp:build
# Build Rust
bazel build //rust:build
```

### Run Tests
```bash
bazel test //...
```

### Docker Mode
```bash
# Build and run Docker containers
bazel run //:docker_build
```

## 🛠️ Unified Commands (via Bazel)

For ease of use, you can call the following targets:

- `bazel run //python:run -- --key YOUR_KEY`
- `bazel run //cpp:run -- --key YOUR_KEY`
- `bazel run //rust:run -- --key YOUR_KEY`

## 📊 Summary

Each solution implements three core strategies:
1. **Exchange Arbitrage**: Cross-exchange price spread detection.
2. **Index Arbitrage**: ETF vs. constituent price balance.
3. **Shock Handling**: Immediate news response and reversal.

For detailed documentation, diagrams, and complexity analysis, please refer to the `README.md` in each respective folder.
