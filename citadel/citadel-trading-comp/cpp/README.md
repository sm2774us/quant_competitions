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
