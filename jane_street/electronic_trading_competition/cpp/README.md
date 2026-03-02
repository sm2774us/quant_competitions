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
