# Citadel Trading Comp (Citadel)

## 📋 Overview

# citadel-trading-comp
Citadel Trading Competition Code. The JSON files are an overnight run of 36 sessions.

# Strategies

- Main/Alternative Exchange Arbitradge
  - When the bid-ask spreads of the same underlying company cross on two exchanges, arbitradge
  - Detail: when cross-over is big, send a market order for ensured execution. when cross-over is small, send limit order to ensure execution price, with the risk of partially stuck in an order
 
- Index Arbitradge
  - Similar to exchange arbitradge, take the sum of highest bids of constituents of an ETF, and compare with ETF ask. Arbitradge if there is an opportunity. Vice versa using lowest asks of constituents with ETF bid
 
- News response
  - When a negative shock is informed, immediately short. 3 ticks later, long same amount. Both are market orders for timely execution. 
  - When a positive shock is informed, the other way round
  - For small shocks, ignore


## 🚀 Solutions

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


## 💻 Implementations

### Python

# Citadel Trading Bot - Python Solution

A robust, OOP-style trading bot for the Citadel Trading Competition, implemented in Python 3.13.

## a) Directory Structure
```text
python/
├── citadel_bot/
│   ├── __init__.py
│   ├── api.py           # API Client using httpx
│   ├── bot.py           # Bot orchestrator
│   ├── models.py        # Pydantic models
│   └── strategies.py    # Trading strategy logic
├── tests/
│   ├── __init__.py
│   └── test_strategies.py
├── Dockerfile
├── pyproject.toml       # Poetry configuration
└── README.md
```

## b) Instructions

### Local Execution
1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Run the bot: `poetry run citadel-bot --key YOUR_API_KEY`
4. Run tests: `poetry run pytest --cov=citadel_bot`

### Docker Execution
1. Build image: `docker build -t citadel-bot-py .`
2. Run container: `docker run citadel-bot-py --key YOUR_API_KEY --url http://host.docker.internal:9998`

## c) Solution Explanation & Architecture

### Strategy Logic
- **Exchange Arbitrage**: Monitors `WMT`, `CAT`, `MMM` across Main (-M) and Alt (-A) exchanges. Executes market orders if the spread exceeds taker fees + buffer, or limit orders for smaller spreads.
- **Index Arbitrage**: Calculates the weighted sum of constituents (choosing the best price across exchanges) and compares it with the `ETF` price.
- **Shock Handling**: Responds to news headlines. Positions are opened on a shock and reversed 2 ticks later.

### Complexity
- **Time Complexity**: $O(N)$ per tick, where $N$ is the number of securities and news items.
- **Space Complexity**: $O(1)$ persistent storage, as it only maintains the last seen tick and minimal state.

### Architecture Diagram
```text
+-------------+      +----------------+      +------------------+
|   Main CLI  | ---> |   TradingBot   | ---> |    TradingApi    |
+-------------+      +----------------+      +---------+--------+
                            |                          |
                            v                          v
                     +--------------+          +----------------+
                     |  Strategies  |          |   REST Server  |
                     +--------------+          +----------------+
                     | - ExchangeArb|
                     | - IndexArb   |
                     | - ShockHandl |
                     +--------------+
```

## d) UML Sequence Diagram
1. User starts Bot via CLI.
2. Bot enters polling loop.
3. Bot requests Case Status from Api.
4. If new Tick:
    a. Bot calls ShockHandler.run().
    b. Bot calls ExchangeArbitrage.run().
    c. Bot calls IndexArbitrage.run().
5. Strategies request OrderBook/Securities/News from Api.
6. Strategies analyze data and post Orders if profitable.
7. Bot sleeps for interval and repeats.

## e) Flowchart
```text
[Start] --> [Initialize API/Bot]
   |
   v
[Get Case Status] <----------------+
   |                               |
[Is Tick New?] --No--> [Sleep] ----+
   |
  Yes
   |
[Shock Handler] --> [Exchange Arb] --> [Index Arb]
   |                     |                |
   +-----------> [Post Orders] <----------+
                         |
                         v
                    [Update State]
                         |
                         v
                    [Wait next tick]
```

## f) Tabulated Summary

| Feature | Implementation |
|---------|----------------|
| Language | Python 3.13 |
| Package Manager | Poetry |
| HTTP Client | httpx |
| Data Validation | Pydantic |
| CLI Framework | click |
| Testing | pytest + pytest-mock |
| Strategy | Arb + Index + News |


### Cpp

# Citadel Trading Bot - C++ Solution

A high-performance, OOP-style trading bot for the Citadel Trading Competition, implemented in C++23.

## a) Directory Structure
```text
cpp/
├── include/
│   ├── api.hpp          # API Client header (CPR)
│   ├── bot.hpp          # Bot orchestrator header
│   ├── models.hpp       # Data models (nlohmann/json)
│   └── strategies.hpp   # Trading strategies header
├── src/
│   ├── api.cpp
│   ├── bot.cpp
│   ├── main.cpp         # CLI entry point (CLI11)
│   └── strategies.cpp
├── tests/
│   └── test_strategies.cpp # Google Test cases
├── CMakeLists.txt
├── Dockerfile
└── README.md
```

## b) Instructions

### Local Execution
1. Install CMake and a C++23 compatible compiler (GCC 13+, Clang 16+).
2. Install libcurl: `sudo apt-get install libcurl4-openssl-dev`
3. Build the project:
   ```bash
   mkdir build && cd build
   cmake .. -DCMAKE_BUILD_TYPE=Release
   make
   ```
4. Run the bot: `./citadel_bot --key YOUR_API_KEY`
5. Run tests: `./citadel_tests`

### Docker Execution
1. Build image: `docker build -t citadel-bot-cpp .`
2. Run container: `docker run citadel-bot-cpp --key YOUR_API_KEY --url http://host.docker.internal:9998`

## c) Solution Explanation & Architecture

### Strategy Logic
- **Exchange Arbitrage**: Identifies price discrepancies between Main and Alt exchanges.
- **Index Arbitrage**: Monitors ETF components and executes arbitrage if the composite price deviates significantly from the ETF price.
- **Shock Handling**: Rapidly responds to news "shocks" by taking directional positions and reversing them after 2 ticks.

### Complexity
- **Time Complexity**: $O(N)$ per tick. C++ implementation offers minimal latency.
- **Space Complexity**: $O(1)$ persistent storage.

### Architecture Diagram
```text
+-------------+      +----------------+      +------------------+
|   Main CLI  | ---> |   TradingBot   | ---> |    TradingApi    |
+-------------+      +----------------+      +---------+--------+
 (CLI11)                    |                      (CPR)
                            v                          v
                     +--------------+          +----------------+
                     |  Strategies  |          |   REST Server  |
                     +--------------+          +----------------+
```

## d) UML Sequence Diagram
1. CLI parses arguments and initializes `TradingApi`.
2. `TradingBot` is created with the API instance.
3. Polling loop starts:
    - Bot calls `api->get_case()`.
    - If new tick:
        - `ShockHandler` checks for recent news.
        - `ExchangeArbitrage` checks price spreads.
        - `IndexArbitrage` checks ETF/Components balance.
    - If profitable conditions met, `api->post_order()` is called.
4. Loop repeats until case is stopped.

## e) Flowchart
```text
[Start] --> [Initialize API]
   |
   v
[Polling Loop] <-------------------+
   |                               |
[Get Tick]                         |
   |                               |
[Tick Changed?] --No--> [Wait] ----+
   |
  Yes
   |
[Process Strategies] 
   | (Arb, Index, Shock)
   v
[Send Orders]
   |
   v
[Repeat]
```

## f) Tabulated Summary

| Feature | Implementation |
|---------|----------------|
| Language | C++23 |
| Build System | CMake |
| HTTP Client | CPR (libcurl) |
| JSON | nlohmann/json |
| CLI Framework | CLI11 |
| Testing | Google Test / Mock |
| Strategy | Arb + Index + News |


### Rust

# Citadel Trading Bot - Rust Solution

A safe, concurrent, and high-performance trading bot for the Citadel Trading Competition, implemented in Rust.

## a) Directory Structure
```text
rust/
├── src/
│   ├── api.rs           # API Client (reqwest)
│   ├── bot.rs           # Bot orchestrator
│   ├── lib.rs           # Library exports
│   ├── main.rs          # CLI entry point (clap)
│   ├── models.rs        # Data models (serde)
│   └── strategies.rs    # Trading strategies
├── tests/
│   └── test_strategies.rs # Mocked tests
├── Cargo.toml
├── Dockerfile
└── README.md
```

## b) Instructions

### Local Execution
1. Install Rust (latest stable recommended).
2. Build the project: `cargo build --release`
3. Run the bot: `cargo run --release -- --key YOUR_API_KEY`
4. Run tests: `cargo test`

### Docker Execution
1. Build image: `docker build -t citadel-bot-rust .`
2. Run container: `docker run citadel-bot-rust --key YOUR_API_KEY --url http://host.docker.internal:9998`

## c) Solution Explanation & Architecture

### Strategy Logic
- **Exchange Arbitrage**: Leverages Rust's performance to detect and act on cross-exchange spreads.
- **Index Arbitrage**: Monitors ETF components and executes multi-leg orders.
- **Shock Handling**: Directional trading on news shocks with 2-tick reversal logic.

### Complexity
- **Time Complexity**: $O(N)$ per tick.
- **Space Complexity**: $O(1)$ persistent storage.

### Architecture Diagram
```text
+-------------+      +----------------+      +------------------+
|   Main CLI  | ---> |   TradingBot   | ---> |    TradingApi    |
+-------------+      +----------------+      +---------+--------+
 (clap)                                          (reqwest)
                            |                          |
                            v                          v
                     +--------------+          +----------------+
                     |  Strategies  |          |   REST Server  |
                     +--------------+          +----------------+
```

## d) UML Sequence Diagram
1. `main` parses `Args`.
2. `RealTradingApi` is instantiated.
3. `TradingBot` loop:
    - `api.get_case()` to check for new tick.
    - If new tick:
        - `ShockHandler` -> `api.get_news()` -> `api.post_order()`.
        - `ExchangeArbitrage` -> `api.get_order_book()` -> `api.post_order()`.
        - `IndexArbitrage` -> `api.get_securities()` -> `api.post_order()`.
4. Loop continues until `STOPPED`.

## e) Flowchart
```text
[Start] --> [Initialize API]
   |
   v
[Polling Loop] <-------------------+
   |                               |
[Get Case Status]                  |
   |                               |
[New Tick?] --No--> [Wait] --------+
   |
  Yes
   |
[Shock] -> [Exch Arb] -> [Idx Arb]
   |          |             |
   +----> [Post Orders] <---+
              |
              v
          [Repeat]
```

## f) Tabulated Summary

| Feature | Implementation |
|---------|----------------|
| Language | Rust |
| HTTP Client | reqwest |
| JSON | serde / serde_json |
| CLI Framework | clap |
| Testing | cargo test / mockall |
| Error Handling | anyhow / thiserror |
| Strategy | Arb + Index + News |


