# Trading Bot (Jane Street)

## 📋 Overview

# Jane Street Trading Bot Challenge

## Overview
This challenge involves building a robust, high-performance trading bot for the Jane Street Electronic Trading Competition (ETC). The bot must connect to an exchange via a TCP socket and communicate using a custom JSON-based protocol. The primary goal is to maximize profit by trading various securities (e.g., BOND, VALBZ, VALE) based on market data and proprietary strategies.

## Core Objectives
- **Connectivity:** Establish and maintain a reliable TCP connection to the exchange.
- **Protocol Management:** Accurately parse and generate JSON messages for communication with the exchange.
- **Strategy Implementation:**
    - **BOND Strategy:** Trade BONDS, which have a fixed fair value of 1000. Buy at 999 and sell at 1001.
    - **Fair Price Strategy:** Calculate the fair price for other securities using a running average of the mid-price (average of the best bid and best ask) or other indicators.
- **Position Management:** Keep track of current positions for each security and ensure they do not exceed pre-defined limits (e.g., +/- 100 for BOND).
- **Performance:** Ensure high-speed execution to capitalize on transient market opportunities.

## Exchange Protocol
The bot communicates with the exchange using JSON objects separated by newlines (`
`).

### Client Messages (Bot to Exchange)
- **Hello:** `{"type": "hello", "team": "TEAMNAME"}` - Initial handshake.
- **Add Order:** `{"type": "add", "order_id": int, "symbol": string, "dir": "BUY"|"SELL", "price": int, "size": int}` - Places a new limit order.
- **Cancel Order:** `{"type": "cancel", "order_id": int}` - Cancels an existing order.
- **Convert:** `{"type": "convert", "order_id": int, "symbol": string, "dir": "BUY"|"SELL", "size": int}` - Converts ETFs to their underlying assets or vice versa.

### Exchange Messages (Exchange to Bot)
- **Hello:** `{"type": "hello", "symbols": [{"symbol": "BOND", "position": 0}, ...]}` - Acknowledges the handshake and provides initial positions.
- **Open/Close:** `{"type": "open"|"close", "symbols": [string, ...]}` - Notification that trading has opened or closed for certain symbols.
- **Book:** `{"type": "book", "symbol": string, "buy": [[price, size], ...], "sell": [[price, size], ...]}` - Updates on the current order book state.
- **Fill:** `{"type": "fill", "order_id": int, "symbol": string, "dir": "BUY"|"SELL", "price": int, "size": int}` - Notification that an order has been partially or fully filled.
- **Out:** `{"type": "out", "order_id": int}` - Notification that an order has been cancelled or has expired.
- **Trade:** `{"type": "trade", "symbol": string, "price": int, "size": int}` - Notification that a trade has occurred in the market (between any two participants).
- **Error:** `{"type": "error", "error": string}` - Notification of an error (e.g., invalid order).

## Implementation Requirements
This repository provides 100% fully implemented, robust, and tested solutions in three languages:
1. **Python 3.13:** Built with Poetry, using `click` for CLI and `pytest` for testing.
2. **C++26:** Built with CMake, using Google Test and a modern CLI library.
3. **Rust 1.93.1:** Built with Cargo, using `clap` for CLI and native testing framework.

Each solution is containerized using Docker and provides comprehensive documentation, including architecture diagrams, sequence diagrams, and flowcharts.

A common **Bazel** entry point is provided to build, test, and run all three solutions.


## 🚀 Solutions

# Jane Street Trading Bot - Solutions Summary

This repository contains three independent, high-performance implementations of the Jane Street Trading Bot challenge.

## Implementations

| Language | Build Tool | CLI Library | Documentation |
| :--- | :--- | :--- | :--- |
| **Python 3.13** | Poetry | `click` | [Read More](./python/README.md) |
| **C++26** | CMake | `CLI11` | [Read More](./cpp/README.md) |
| **Rust 1.93.1** | Cargo | `clap` | [Read More](./rust/README.md) |

## Common Entry Point (Bazel)

A `WORKSPACE` and `BUILD` file are provided at the root to allow building and testing all solutions through a single command.

### Bazel Instructions

#### Build all solutions
```bash
bazel build //...
```

#### Run all tests
```bash
bazel test //...
```

#### Run Coverage Reports
```bash
bazel coverage //...
```

#### Docker Mode (with Bazel)
To build container images using Bazel:
```bash
bazel run //python:image
bazel run //cpp:image
bazel run //rust:image
```

## Strategy Comparison

All implementations utilize a robust "BOND Arbitrage" strategy by default:
1.  **Fixed Fair Value:** BONDS have a guaranteed fair value of 1000.
2.  **Aggressive Taker:** Take any liquidity in the book that is mispriced (buy < 1000, sell > 1000).
3.  **Passive Maker:** Maintain orders at the tightest possible spread around fair value (buy at 999, sell at 1001).
4.  **Position Management:** Strictly adhere to the +/- 100 position limit for BONDS to avoid penalties and manage risk.

## Directory Structure
```text
.
├── README.md           # Challenge Description
├── SOLUTIONS.md        # This file
├── WORKSPACE           # Bazel Workspace
├── BUILD               # Bazel Build Rules
├── python/             # Python 3.13 Implementation
├── cpp/                # C++26 Implementation
├── rust/               # Rust 1.93.1 Implementation
└── old_code/           # Original Challenge Code
```


## 💻 Implementations

### Python

# Trading Bot - Python Solution

## Directory Structure
```text
python/
├── Dockerfile
├── README.md
├── pyproject.toml
├── tests/
│   ├── __init__.py
│   └── test_bot.py
└── trading_bot/
    ├── __init__.py
    ├── bot.py
    ├── cli.py
    ├── exchange.py
    ├── models.py
    └── strategy.py
```

## Instructions

### Local Build and Run
1.  **Install Poetry:** `pip install poetry`
2.  **Install Dependencies:** `poetry install`
3.  **Run Tests:** `poetry run pytest --cov=trading_bot`
4.  **Run Bot:** `poetry run trading-bot --host localhost --port 25000 --team MYTEAM`

### Docker Build and Run
1.  **Build Image:** `docker build -t trading-bot-python .`
2.  **Run Container:** `docker run trading-bot-python --host host.docker.internal --port 25000`

## Solution Explanation
The solution uses an OOP-style architecture to separate concerns:
-   **Exchange:** Handles TCP connectivity and JSON serialization.
-   **Strategy:** Contains the trading logic (BOND arbitrage and fair price estimation).
-   **TradingBot:** Orchestrates the message loop and links the exchange with the strategy.
-   **Models:** Provides type-safe data structures for market data and orders.

### Time and Space Complexity
-   **Time Complexity:** $O(1)$ per message. Each market update (book or fill) is processed in constant time, as it involves simple dictionary lookups and basic arithmetic.
-   **Space Complexity:** $O(S)$, where $S$ is the number of unique symbols traded. We store positions and limits for each symbol.

### Solution Architecture (ASCII)
```text
+----------+      +------------+      +------------+
| Exchange | <--> | TradingBot | <--> |  Strategy  |
+----------+      +------------+      +------------+
      ^                 |                   |
      |                 v                   v
      +----------- [ Models ] <-------------+
```

### UML Sequence Diagram
```text
Bot                 Exchange                Strategy
 |                     |                       |
 |--- connect() ------>|                       |
 |--- send(hello) ---->|                       |
 |                     |                       |
 |<-- receive(hello)---|                       |
 |--- on_hello() ---------------------------->|
 |                     |                       |
 |                     |                       |
 |<-- receive(book) ---|                       |
 |--- decide(book) --------------------------->|
 |                     |                       |
 |<-- [Orders] --------------------------------|
 |--- send(add) ------>|                       |
 |                     |                       |
 |<-- receive(fill) ---|                       |
 |--- on_fill() ------------------------------>|
 |                     |                       |
```

### Flowchart
```text
[Start] -> [Connect to Exchange] -> [Send Handshake]
   ^                                     |
   |                                     v
   |                          [Wait for Message]
   |                                     |
   +--- [Process Fill] <----- (Fill?) <--+--> (Book?) ----> [Run Strategy]
                                         |                      |
                                         v                      v
                                      (Other?)            [Place Orders]
                                         |                      |
                                         +<---------------------+
```

### Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| Language | Python 3.13 |
| Build Tool | Poetry |
| CLI Library | Click |
| Testing | Pytest |
| Concurrency | Synchronous Blocking IO |
| Strategy | BOND Arbitrage |


### Cpp

# Trading Bot - C++ Solution

## Directory Structure
```text
cpp/
├── CMakeLists.txt
├── Dockerfile
├── README.md
├── include/
│   ├── bot.hpp
│   ├── exchange.hpp
│   ├── models.hpp
│   └── strategy.hpp
├── src/
│   ├── bot.cpp
│   ├── exchange.cpp
│   ├── main.cpp
│   └── strategy.cpp
└── tests/
    └── test_bot.cpp
```

## Instructions

### Local Build and Run
1.  **Prerequisites:** CMake 3.25+, GCC 14+ or Clang 18+, WinSock2 (on Windows).
2.  **Generate Build Files:** `mkdir build && cd build && cmake ..`
3.  **Build:** `cmake --build .`
4.  **Run Tests:** `ctest --output-on-failure`
5.  **Run Bot:** `./trading_bot --host localhost --port 25000 --team MYTEAM`

### Docker Build and Run
1.  **Build Image:** `docker build -t trading-bot-cpp .`
2.  **Run Container:** `docker run trading-bot-cpp --host host.docker.internal --port 25000`

## Solution Explanation
The C++ solution is designed for high-performance and uses modern C++26 features:
-   **Header-Only Models:** Using POD structs for efficient data handling.
-   **Exchange:** Cross-platform TCP implementation using standard sockets.
-   **Strategy:** Efficient position management and decision-making logic.
-   **CLI:** Integrated using CLI11 for a modern command-line experience.

### Time and Space Complexity
-   **Time Complexity:** $O(1)$ per message. Dictionary-like lookups using `std::map` provide logarithmic time, but could be $O(1)$ with `std::unordered_map`. For a small number of symbols, `std::map` is extremely fast.
-   **Space Complexity:** $O(S)$, where $S$ is the number of symbols.

### Solution Architecture (ASCII)
```text
+----------+      +------------+      +------------+
| Exchange | <--> |    Bot     | <--> |  Strategy  |
+----------+      +------------+      +------------+
      ^                 |                   |
      |                 v                   v
      +----------- [ Models ] <-------------+
```

### UML Sequence Diagram
```text
Bot                 Exchange                Strategy
 |                     |                       |
 |--- connect() ------>|                       |
 |--- send(hello) ---->|                       |
 |                     |                       |
 |<-- receive(hello)---|                       |
 |--- on_hello() ---------------------------->|
 |                     |                       |
 |                     |                       |
 |<-- receive(book) ---|                       |
 |--- decide(book) --------------------------->|
 |                     |                       |
 |<-- [Orders] --------------------------------|
 |--- send(add) ------>|                       |
 |                     |                       |
 |<-- receive(fill) ---|                       |
 |--- on_fill() ------------------------------>|
 |                     |                       |
```

### Flowchart
```text
[Start] -> [Socket Create] -> [Handshake]
   ^                              |
   |                              v
   |                        [Recv JSON]
   |                              |
   +--- [Update Pos] <---- (Fill?) <--+--> (Book?) ----> [Logic]
                                      |                    |
                                      v                    v
                                   (Other)            [Send Order]
                                      |                    |
                                      +<-------------------+
```

### Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| Language | C++26 |
| Build Tool | CMake |
| CLI Library | CLI11 |
| Testing | Google Test |
| JSON Library | nlohmann/json |
| Strategy | BOND Arbitrage |


### Rust

# Trading Bot - Rust Solution

## Directory Structure
```text
rust/
├── Cargo.toml
├── Dockerfile
├── README.md
└── src/
    ├── bot.rs
    ├── exchange.rs
    ├── main.rs
    ├── models.rs
    └── strategy.rs
```

## Instructions

### Local Build and Run
1.  **Prerequisites:** Rust 1.81+ (using Cargo).
2.  **Build:** `cargo build --release`
3.  **Run Tests:** `cargo test`
4.  **Run Bot:** `cargo run --release -- --host localhost --port 25000 --team MYTEAM`

### Docker Build and Run
1.  **Build Image:** `docker build -t trading-bot-rust .`
2.  **Run Container:** `docker run trading-bot-rust --host host.docker.internal --port 25000`

## Solution Explanation
The Rust solution focuses on safety, concurrency readiness, and performance:
-   **Serde Integration:** Using `serde` for extremely fast and safe JSON parsing.
-   **Strong Typing:** Leveraging Rust's enum system to represent market and client messages.
-   **Error Handling:** Using `anyhow` for robust error reporting.
-   **CLI:** Built with `clap` (derive API) for a modern CLI experience.

### Time and Space Complexity
-   **Time Complexity:** $O(1)$ per message. Hash map lookups in Rust are highly optimized.
-   **Space Complexity:** $O(S)$, where $S$ is the number of symbols.

### Solution Architecture (ASCII)
```text
+----------+      +------------+      +------------+
| Exchange | <--> |    Bot     | <--> |  Strategy  |
+----------+      +------------+      +------------+
      ^                 |                   |
      |                 v                   v
      +----------- [ Models ] <-------------+
```

### UML Sequence Diagram
```text
Bot                 Exchange                Strategy
 |                     |                       |
 |--- connect() ------>|                       |
 |--- send(hello) ---->|                       |
 |                     |                       |
 |<-- receive(hello)---|                       |
 |--- on_hello() ---------------------------->|
 |                     |                       |
 |                     |                       |
 |<-- receive(book) ---|                       |
 |--- decide(book) --------------------------->|
 |                     |                       |
 |<-- [Orders] --------------------------------|
 |--- send(add) ------>|                       |
 |                     |                       |
 |<-- receive(fill) ---|                       |
 |--- on_fill() ------------------------------>|
 |                     |                       |
```

### Flowchart
```text
[Start] -> [TCP Connect] -> [Handshake]
   ^                            |
   |                            v
   |                     [Read JSON Line]
   |                            |
   +--- [Update State] <--- (Fill?) <--+--> (Book?) ----> [Logic]
                                       |                    |
                                       v                    v
                                    (Other)            [Write JSON]
                                       |                    |
                                       +<-------------------+
```

### Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| Language | Rust 1.93.1 |
| Build Tool | Cargo |
| CLI Library | Clap |
| Testing | Native (Cargo Test) |
| JSON Library | Serde / serde_json |
| Strategy | BOND Arbitrage |


