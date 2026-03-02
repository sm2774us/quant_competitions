# 🏰 Citadel Trading Competition

## 📋 Problem Description
The Citadel Trading Competition challenges participants to build a robust, high-performance automated trading bot capable of extracting value from simulated market inefficiencies. 

The environment includes:
- **Multiple Exchanges**: Identical securities (e.g., `WMT-M`, `WMT-A`) trading on different venues.
- **ETFs**: Index funds (e.g., `ETF`) whose price should reflect the sum of its underlying components (`WMT`, `CAT`, `MMM`).
- **News Feed**: Real-time shocks that impact prices predictably over a short window.

### Key Objectives
1. **Minimize Latency**: Fast response to price crosses and news.
2. **Maximize NLV**: Net Liquidating Value through arbitrage and directional news plays.
3. **Risk Management**: Staying within gross and net position limits.

---

## 🚀 Solutions Overview

| Solution | Language | Key Technologies |
|----------|----------|------------------|
| [Python 3.13](./citadel_python.md) | Python | Poetry, Pydantic v2, HTTPX |
| [C++26](./citadel_cpp.md) | C++ | CMake, CLI11, CPR, nlohmann/json |
| [Rust 1.93.1](./citadel_rust.md) | Rust | Cargo, Reqwest, Serde, Clap |

---

## 🐍 Python 3.13 Solution Detail
Implemented using modern Python 3.13 features like **type statement** for type aliases and **improved generics**.

### Architecture
The bot follows a clean **Strategy Pattern**. The `TradingBot` orchestrator polls for new ticks and delegates execution to `ExchangeArbitrage`, `IndexArbitrage`, and `ShockHandler`.

### Performance Optimization
- **Vectorized Logic**: Uses efficient list comprehensions and generator expressions for data processing.
- **Async Polling**: Leverages high-performance HTTPX client.

---

## ⚙️ C++26 Solution Detail
A high-performance implementation utilizing **C++26** features for maximum efficiency.

### Modern C++26 Features Used:
- **`std::println`**: For zero-overhead, type-safe logging.
- **Pack Indexing**: Simplified template metaprogramming for strategy parameter handling.
- **`constexpr` Improvements**: More logic moved to compile-time to reduce runtime latency.
- **Placeholder variables**: Using `_` for unused structured binding results.

### Performance
- **Zero-Allocation Loop**: The main trading loop is designed to avoid heap allocations.
- **Cache-Friendly**: Data structures are optimized for CPU cache locality.

---

## 🦀 Rust 1.93.1 Solution Detail
Focuses on **Memory Safety** and **Zero-Cost Abstractions**.

### Architecture
Uses **Trait-based** strategy definitions to ensure compile-time polymorphism without virtual dispatch overhead.

### Key Features
- **Strict Typing**: Prevents common financial logic errors (e.g., mixing currencies or side types).
- **Concurrency**: Safe multi-threaded polling and execution.
- **Error Handling**: Comprehensive error propagation using `anyhow`.

---

## 📊 Strategy Comparison

| Strategy | Logic | Complexity |
|----------|-------|------------|
| **Exchange Arb** | $P_{Bid, A} - P_{Ask, B} > 	ext{Fees}$ | $O(1)$ |
| **Index Arb** | $|P_{ETF} - \sum P_{Comp}| > 	ext{Threshold}$ | $O(N)$ |
| **Shock Handler** | Immediate position on news + Reversal | $O(1)$ |
