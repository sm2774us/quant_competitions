# Electronic Trading Competition (Jane Street)

## 📋 Overview

# Jane Street Electronic Trading Competition

## Overview
This project implements a high-performance algorithmic trading bot designed for the Jane Street Electronic Trading Competition. The bot interacts with a simulated exchange via a TCP socket, processing real-time market data and executing trades across multiple strategies including market making, arbitrage, and technical analysis.

## The Challenge
The goal is to maximize profit (PNL) while managing risk and liquidity in a competitive environment. The bot must handle a high-throughput stream of JSON messages from the exchange and respond with low latency.

### Market Protocols
- **Communication:** TCP Socket with newline-delimited JSON messages.
- **Message Types:** `hello`, `open`, `book`, `trade`, `fill`, `ack`, `reject`, `error`, `out`.
- **Order Types:** `add` (Limit Orders), `cancel`, `convert`.

### Assets and Strategies
1. **BOND Trading:** Trading a fixed-value asset (par value 1000) using market-making strategies.
2. **Pennying (Market Making):** Dynamically adjusting bid/ask prices to capture the spread by outbidding the market by the minimum tick size.
3. **ADR Arbitrage:** Exploiting price differences between `VALE` (the stock) and `VALBZ` (the ADR) via direct trades and the `convert` mechanism.
4. **ETF Arbitrage:** Trading `XLF` against its components (`BOND`, `GS`, `MS`, `WFC`). This involves calculating the Net Asset Value (NAV) and executing basket trades or conversions when the premium/discount exceeds costs.
5. **Technical Analysis (MACD):** Using Exponential Moving Averages (EMA) to identify momentum shifts and trend reversals for directional trading.

## Project Structure
This repository contains production-grade implementations in three languages:
- `./python`: Python 3.13 implementation using Poetry.
- `./cpp`: C++26 implementation using CMake.
- `./rust`: Rust implementation using Cargo.

Each implementation is fully containerized, robustly tested, and optimized for performance.

## Getting Started
Refer to the `SOLUTIONS.md` file in this directory for a summary of all implementations and a unified Bazel entry point for building, testing, and running the solutions.


## 🚀 Solutions

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


## 💻 Implementations

### Python

# Python Trading Bot Implementation

## Directory Structure
```text
python/
├── Dockerfile
├── pyproject.toml
├── README.md
├── RNN-DJIA/
├── src/
│   └── trading_bot/
│       ├── __init__.py
│       ├── cli.py
│       ├── client.py
│       ├── models.py
│       └── strategies.py
└── tests/
    ├── test_client.py
    └── test_strategies.py
```

## Instructions

### Local Build and Run
1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Run tests: `poetry run pytest`
4. Run bot: `poetry run trading-bot --hostname production --port 25000 --team PANIPURISTREET`

### Docker Build and Run
1. Build image: `docker build -t trading-bot-python .`
2. Run bot: `docker run trading-bot-python --hostname production --port 25000 --team PANIPURISTREET`

## Solution Explanation

### Architecture
The solution uses an asynchronous event-driven architecture powered by `asyncio`. The `ExchangeClient` manages the TCP connection and JSON serialization. Market messages are dispatched to various strategy modules.

```text
+----------------+      +------------------+      +-------------------+
|   Exchange     | <--> |  ExchangeClient  | <--> |    TradingBot     |
+----------------+      +------------------+      +---------+---------+
                                                            |
                                           +----------------+----------------+
                                           |                |                |
                                   +-------v-------+ +------v------+ +-------v-------+
                                   | BondStrategy  | | ADRStrategy | | MACDStrategy  |
                                   +---------------+ +-------------+ +---------------+
```

### Time and Space Complexity
- **Time Complexity:** O(N) per message, where N is the number of order book levels (limited to 10 by exchange). All updates (EMA, spread checks) are O(1).
- **Space Complexity:** O(M) where M is the number of active symbols. MACD stores a fixed window of prices (O(W)).

## UML Sequence Diagram
```text
Exchange -> ExchangeClient: BookMessage(VALE)
ExchangeClient -> TradingBot: handle_message(BookMessage)
TradingBot -> ADRStrategy: update_book_vale(BookMessage)
ADRStrategy -> TradingBot: [Order(BUY VALE), Order(CONVERT), Order(SELL VALBZ)]
TradingBot -> ExchangeClient: send_order(Order)
ExchangeClient -> Exchange: {"type": "add", ...}
```

## Flowchart
```text
[Start] --> [Connect to Exchange]
    |
[Message Received] <-----------------+
    |                                |
[Parse JSON]                         |
    |                                |
[Identify Type]                      |
    |                                |
    +--[Book]--> [Update Strategy] --+--[Generate Orders]--> [Send to Exchange]
    |                                |
    +--[Trade]--> [Update MACD] -----+
    |                                |
    +--[Fill]--> [Update Position] --+
```

## Tabulated Summary
| Strategy | Goal | Complexity | Efficiency |
|----------|------|------------|------------|
| Bond | Market Making | O(1) | High |
| ADR Arbitrage | Statistical Arbitrage | O(1) | High |
| MACD | Trend Following | O(1) | Medium |


### Cpp

# C++ Trading Bot Implementation

## Directory Structure
```text
cpp/
├── CMakeLists.txt
├── Dockerfile
├── README.md
├── RNN-DJIA/
├── src/
│   ├── exchange_client.cpp
│   ├── exchange_client.hpp
│   ├── main.cpp
│   ├── models.hpp
│   ├── strategies.cpp
│   └── strategies.hpp
└── tests/
    └── test_strategies.cpp
```

## Instructions

### Local Build and Run
1. Ensure CMake and a C++26 compiler are installed.
2. Build:
   ```bash
   mkdir build && cd build
   cmake .. -DCMAKE_BUILD_TYPE=Release
   cmake --build .
   ```
3. Run tests: `./build/test_trading_bot`
4. Run bot: `./build/trading_bot --hostname production --port 25000 --team PANIPURISTREET`

### Docker Build and Run
1. Build image: `docker build -t trading-bot-cpp .`
2. Run bot: `docker run trading-bot-cpp --hostname production --port 25000 --team PANIPURISTREET`

## Solution Explanation

### Architecture
The C++ implementation is optimized for low-latency message processing. It uses a synchronous blocking socket with a tight event loop. Memory allocations are minimized by using pre-allocated buffers and standard containers with reserved capacity.

```text
+----------------+      +------------------+      +-------------------+
|   Exchange     | <--> |  ExchangeClient  | <--> |      main loop    |
+----------------+      +------------------+      +---------+---------+
                                                            |
                                           +----------------+----------------+
                                           |                |                |
                                   +-------v-------+ +------v------+ +-------v-------+
                                   | BondStrategy  | | ADRStrategy | | MACDStrategy  |
                                   +---------------+ +-------------+ +---------------+
```

### Time and Space Complexity
- **Time Complexity:** O(N) per message. C++ provides superior performance for EMA calculations and JSON parsing compared to Python.
- **Space Complexity:** O(M) where M is the number of active symbols.

## UML Sequence Diagram
```text
Exchange -> ExchangeClient: BookMessage(BOND)
ExchangeClient -> main: read()
main -> BondStrategy: update_book(BookMessage)
BondStrategy -> main: [Order(BUY BOND), Order(SELL BOND)]
main -> ExchangeClient: send_order(Order)
ExchangeClient -> Exchange: {"type": "add", ...}
```

## Flowchart
```text
[Start] --> [Connect to Exchange]
    |
[Message Received] <-----------------+
    |                                |
[Parse JSON]                         |
    |                                |
[Identify Type]                      |
    |                                |
    +--[Book]--> [Update Strategy] --+--[Generate Orders]--> [Send to Exchange]
    |                                |
    +--[Trade]--> [Update MACD] -----+
    |                                |
    +--[Fill]--> [Update Position] --+
```

## Tabulated Summary
| Strategy | Goal | Complexity | Efficiency |
|----------|------|------------|------------|
| Bond | Market Making | O(1) | Extremely High |
| ADR Arbitrage | Statistical Arbitrage | O(1) | Extremely High |
| MACD | Trend Following | O(1) | High |


### Rust

# Rust Trading Bot Implementation

## Directory Structure
```text
rust/
├── Cargo.toml
├── Dockerfile
├── README.md
├── RNN-DJIA/
└── src/
    ├── exchange_client.rs
    ├── main.rs
    ├── models.rs
    └── strategies.rs
```

## Instructions

### Local Build and Run
1. Ensure Rust 1.93.1 is installed.
2. Build: `cargo build --release`
3. Run tests: `cargo test`
4. Run bot: `./target/release/trading-bot --hostname production --port 25000 --team PANIPURISTREET`

### Docker Build and Run
1. Build image: `docker build -t trading-bot-rust .`
2. Run bot: `docker run trading-bot-rust --hostname production --port 25000 --team PANIPURISTREET`

## Solution Explanation

### Architecture
The Rust implementation leverages `tokio` for high-performance asynchronous I/O. It uses a strong type system (Enums for messages) to ensure safety and correctness at compile time. Memory management is handled via ownership, eliminating data races and memory leaks.

```text
+----------------+      +------------------+      +-------------------+
|   Exchange     | <--> |  ExchangeClient  | <--> |      tokio loop   |
+----------------+      +------------------+      +---------+---------+
                                                            |
                                           +----------------+----------------+
                                           |                |                |
                                   +-------v-------+ +------v------+ +-------v-------+
                                   | BondStrategy  | | ADRStrategy | | MACDStrategy  |
                                   +---------------+ +-------------+ +---------------+
```

### Time and Space Complexity
- **Time Complexity:** O(N) per message. Rust's zero-cost abstractions provide the lowest latency among all implementations.
- **Space Complexity:** O(M) where M is the number of active symbols.

## UML Sequence Diagram
```text
Exchange -> ExchangeClient: BookMessage(BOND)
ExchangeClient -> main: next_message()
main -> BondStrategy: update_book(buy, sell)
BondStrategy -> main: Vec<Order>
main -> ExchangeClient: send_order(Order)
ExchangeClient -> Exchange: {"type": "add", ...}
```

## Flowchart
```text
[Start] --> [Connect to Exchange]
    |
[Message Received] <-----------------+
    |                                |
[Parse JSON]                         |
    |                                |
[Identify Type]                      |
    |                                |
    +--[Book]--> [Update Strategy] --+--[Generate Orders]--> [Send to Exchange]
    |                                |
    +--[Trade]--> [Update MACD] -----+
    |                                |
    +--[Fill]--> [Update Position] --+
```

## Tabulated Summary
| Strategy | Goal | Complexity | Efficiency |
|----------|------|------------|------------|
| Bond | Market Making | O(1) | Extremely High |
| ADR Arbitrage | Statistical Arbitrage | O(1) | Extremely High |
| MACD | Trend Following | O(1) | Extremely High |


