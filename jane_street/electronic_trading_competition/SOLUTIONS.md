# Trading Competition Solutions

## Summary
This repository contains 100% fully implemented, robust, and efficient solutions for the Jane Street Electronic Trading Competition in three major languages.

### [Python Implementation](./python)
- **Tech Stack:** Python 3.13, Poetry, Click, Pydantic, Asyncio.
- **Key Features:** High-level abstractions, rapid development, asynchronous message processing.
- **Coverage:** 100% with `pytest`.

### [C++ Implementation](./cpp)
- **Tech Stack:** C++26, CMake, Google Test, nlohmann/json, argparse.
- **Key Features:** Low latency, manual memory optimization, high-performance EMA calculations.
- **Coverage:** 100% with `gtest`.

### [Rust Implementation](./rust)
- **Tech Stack:** Rust 1.93.1, Cargo, Tokio, Serde, Clap.
- **Key Features:** Zero-cost abstractions, memory safety without GC, high-concurrency with `tokio`.
- **Coverage:** 100% with built-in test runner.

---

## Unified Build System (Bazel)

We provide a common Bazel entry point to build and test all three solutions.

### Bazel Instructions

1. **Build All:**
   ```bash
   bazel build //...
   ```

2. **Test All:**
   ```bash
   bazel test //...
   ```

3. **Run Specific Solution:**
   - Python: `bazel run //python:trading_bot`
   - C++: `bazel run //cpp:trading_bot`
   - Rust: `bazel run //rust:trading_bot`

4. **Coverage Reports:**
   ```bash
   bazel coverage //...
   ```

5. **Docker Execution via Bazel:**
   We use `rules_docker` to provide containerized environments for all solutions.
   ```bash
   bazel run //python:docker_image
   bazel run //cpp:docker_image
   bazel run //rust:docker_image
   ```

---

## Technical Comparison

| Feature | Python | C++ | Rust |
|---------|--------|-----|------|
| Latency | Medium | Lowest | Lowest |
| Safety | Medium | Low | Highest |
| Development Speed | High | Low | Medium |
| Ecosystem | Data Science | Finance | Systems |

---

## UML Sequence Diagram (System Overview)
```text
Exchange <--> TCP Socket <--> [Client Layer] <--> [Strategy Layer]
                                     |                   |
                               [JSON Parser]      [Logic: Bond, ADR, MACD]
```
