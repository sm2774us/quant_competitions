# Electronic Trading Challenge (Jane Street)

## 📋 Overview

# Jane Street Electronic Trading Challenge (ETC)

## Challenge Overview
The Jane Street Electronic Trading Challenge is a high-frequency trading simulation where participants build automated trading bots to compete in a simulated market. The goal is to maximize Profit and Loss (PnL) by executing various trading strategies while managing risk and adhering to exchange-imposed limits.

## Exchange Protocol
The bot communicates with the exchange over a TCP socket using a line-delimited JSON protocol.

### Message Types
- **Client to Exchange:**
  - `hello`: Initial handshake to register the team.
  - `add`: Place a new limit order.
  - `cancel`: Cancel an existing order.
  - `convert`: Request conversion between ETFs/ADRs and their underlying components.
- **Exchange to Client:**
  - `hello`: Confirmation of successful handshake and initial market state.
  - `book`: Update on the current order book for a symbol (bids and asks).
  - `trade`: Notification of a trade occurring in the market.
  - `fill`: Notification that the bot's order has been filled (partially or fully).
  - `out`: Notification that an order has been cancelled or closed.
  - `reject` / `error`: Feedback on invalid requests.

## Market Symbols & Dynamics
1. **BOND**: A stable asset typically priced at 1000.
2. **VALE & VALBZ**: VALBZ is the common stock, and VALE is its ADR (American Depositary Receipt). They are highly correlated and can be converted.
3. **XLF**: An ETF representing a basket of stocks.
   - **XLF Composition**: 10 units of XLF can be converted into/from:
     - 3 units of **BOND**
     - 2 units of **GS** (Goldman Sachs)
     - 3 units of **MS** (Morgan Stanley)
     - 2 units of **WFC** (Wells Fargo)

## Core Strategies

### 1. BOND Market Making
Since `BOND` is consistently priced at 1000, a simple market-making strategy involves placing buy orders at 999 and sell orders at 1001.

### 2. ADR Arbitrage (VALE/VALBZ)
Exploiting price discrepancies between the ADR (`VALE`) and the underlying stock (`VALBZ`).
- **Fair Value Estimation**: Use the price of the more liquid `VALBZ` to estimate the fair value of `VALE`.
- **Execution**: When `VALE` is undervalued relative to `VALBZ` (beyond the conversion fee), buy `VALE`, convert it to `VALBZ`, and sell `VALBZ`.

### 3. ETF Arbitrage (XLF)
Exploiting discrepancies between the ETF price and the Net Asset Value (NAV) of its components.
- **NAV Calculation**: $NAV = 3 \times Price(BOND) + 2 \times Price(GS) + 3 \times Price(MS) + 2 \times Price(WFC)$
- **Long ETF Arbitrage**: If $10 \times Price(XLF) < NAV - ConversionFee$, buy XLF, convert to components, and sell components.
- **Short ETF Arbitrage**: If $10 \times Price(XLF) > NAV + ConversionFee$, buy components, convert to XLF, and sell XLF.

## Technical Requirements
- Robust TCP connection management and reconnection logic.
- Efficient JSON parsing and state management.
- Low-latency order execution and position tracking.
- Risk management to avoid hitting position limits or executing loss-making trades.


## 🚀 Solutions

# Jane Street ETC - Solutions Summary

This project contains three high-performance, robust, and 100% unit-tested solutions for the Jane Street Electronic Trading Challenge.

## 🚀 Solutions

### 1. [Python Solution](./python/)
- **Tech Stack**: Python 3.13, Poetry, NumPy, Click.
- **Key Feature**: Optimized vector calculations using NumPy for low-latency strategy execution.
- **Containerization**: Slim Docker image.

### 2. [C++ Solution](./cpp/)
- **Tech Stack**: C++26, CMake, CLI11, nlohmann/json.
- **Key Feature**: Native BSD sockets and STL data structures for maximum performance.
- **Containerization**: GCC 14 based Docker image.

### 3. [Rust Solution](./rust/)
- **Tech Stack**: Rust 1.84 (Stable), Cargo, Tokio, Serde, Clap.
- **Key Feature**: Modern asynchronous architecture using Tokio for highly concurrent and safe I/O.
- **Containerization**: Multi-stage Rust build.

## 🛠️ Common Entry Point (Bazel)

A `WORKSPACE` and `BUILD` file are provided in the root to manage the multi-language repository.

### Bazel Commands
- **Build All**: `bazel build //...`
- **Test All**: `bazel test //...`
- **Run Python Bot**: `bazel run //:python-bot`

### Local vs Docker Mode
For each solution, you can run locally using its respective package manager (Poetry, CMake, Cargo) or via Docker:

| Mode | Command (Example) |
| :--- | :--- |
| **Local** | `poetry run etc-bot` / `./build/etc-bot` / `cargo run` |
| **Docker** | `docker run etc-bot-python` / `...-cpp` / `...-rust` |

## 📊 Summary Comparison

| Feature | Python | C++ | Rust |
| :--- | :--- | :--- | :--- |
| **Ease of Dev** | High | Medium | Medium |
| **Performance** | Medium (High with NumPy) | Maximum | High |
| **Memory Safety** | High | Low (Manual) | Maximum (Guaranteed) |
| **I/O Model** | Blocking | Blocking (BSD) | Asynchronous (Tokio) |
| **Type System** | Dynamic (Type Hints) | Static | Static (Strong) |


## 💻 Implementations

### Python

# Jane Street ETC - Python Solution

## a) Directory Structure
```text
python/
├── src/
│   └── etc/
│       ├── __init__.py
│       ├── bot.py          # Bot orchestration
│       ├── exchange.py     # TCP/JSON handling
│       ├── main.py         # CLI entry point
│       ├── models.py       # Data structures
│       └── strategies.py   # Strategy implementations
├── tests/
│   └── test_bot.py         # Unit tests
├── Dockerfile              # Containerization
└── pyproject.toml          # Poetry configuration
```

## b) Instructions

### Local Build and Run
1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Run tests: `poetry run pytest --cov=src`
4. Run the bot: `poetry run etc-bot --host <host> --port <port> --team <team>`

### Docker Build and Run
1. Build image: `docker build -t etc-bot-python .`
2. Run container: `docker run etc-bot-python --host <host> --port <port> --team <team>`

## c) Solution Explanation
The solution uses an OOP-based architecture to separate concerns:
- **`ExchangeConnection`**: Handles low-level TCP communication and JSON serialization/deserialization.
- **`MarketState`**: Maintains the current view of the market, including order books, positions, and trade history.
- **`Strategy`**: Abstract base class for different trading strategies.
- **`TradingBot`**: The main controller that reads messages from the exchange, updates the market state, and executes strategies.

### Complexity
- **Time Complexity**: $O(1)$ for processing most messages. Strategy execution depends on the number of active strategies and history size (clamped at 100).
- **Space Complexity**: $O(S 	imes H)$ where $S$ is the number of symbols and $H$ is the history size.

### Architecture
```text
+----------------+      +------------------+      +----------------+
|    Exchange    | <--> | ExchangeConnection | <--> |   TradingBot   |
+----------------+      +------------------+      +-------+--------+
                                                          |
                                              +-----------v-----------+
                                              |      MarketState      |
                                              +-----------+-----------+
                                                          |
                                              +-----------v-----------+
                                              |       Strategies      |
                                              | (Bond, Adr, Etf)      |
                                              +-----------------------+
```

## d) UML Sequence Diagram
| Participant | Action | Description |
| :--- | :--- | :--- |
| **Bot** | Connect | Establish TCP connection to Exchange |
| **Bot** -> **Exchange** | `hello` | Send team handshake |
| **Exchange** -> **Bot** | `hello` | Receive initial positions |
| **Exchange** -> **Bot** | `book` / `trade` | Receive market updates |
| **Bot** | `update_state` | Update `MarketState` with new data |
| **Bot** | `execute` | Run strategies based on current state |
| **Bot** -> **Exchange** | `add` / `convert` | Place orders or conversions |
| **Exchange** -> **Bot** | `fill` | Update positions on successful trade |

## e) Flowchart
```text
[Start] -> [Connect to Exchange]
   |
   v
[Send Handshake] -> [Receive Handshake]
   |                      ^
   v                      |
[Read Message] <----------+
   |
   +--> [Is Book/Trade?] -> [Update MarketState] --+
   |                                               |
   +--> [Is Fill?] -> [Update Positions/PnL] ------+
   |                                               |
   +--> [Is Close?] -> [Exit]                      |
   |                                               |
   v                                               v
[Run Strategies] <---------------------------------+
   |
   +--> [Generate Actions]
   |
   v
[Send Actions to Exchange]
   |
   +-----------------------+
                           |
                           v
                     (Loop back to Read)
```

## f) Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| **Language** | Python 3.13 |
| **Build System** | Poetry |
| **CLI Library** | Click |
| **Performance** | Vector efficient using NumPy |
| **Test Framework** | Pytest with Coverage |
| **Containerization** | Docker (slim image) |
| **Strategies** | Bond MM, ADR Arb, ETF Arb |


### Cpp

# Jane Street ETC - C++ Solution

## a) Directory Structure
```text
cpp/
├── include/
│   └── etc/
│       ├── bot.h           # Bot orchestration
│       ├── exchange.h      # TCP/JSON handling
│       ├── models.h        # Data structures
│       └── strategies.h    # Strategy interfaces
├── src/
│   ├── bot.cpp
│   ├── exchange.cpp
│   ├── main.cpp            # CLI entry point
│   ├── models.cpp
│   └── strategies.cpp
├── tests/
│   └── test_bot.cpp        # Unit tests
├── CMakeLists.txt          # Build configuration
└── Dockerfile              # Containerization
```

## b) Instructions

### Local Build and Run
1. Ensure CMake and a C++26 compiler are installed.
2. Build:
   ```bash
   mkdir build && cd build
   cmake ..
   cmake --build .
   ```
3. Run tests: `./etc_tests`
4. Run the bot: `./etc-bot --host <host> --port <port> --team <team>`

### Docker Build and Run
1. Build image: `docker build -t etc-bot-cpp .`
2. Run container: `docker run etc-bot-cpp --host <host> --port <port> --team <team>`

## c) Solution Explanation
The C++ solution is designed for maximum performance using a low-latency architecture:
- **`TcpExchangeConnection`**: Uses native BSD sockets for minimal overhead.
- **`MarketState`**: Uses efficient STL maps and vectors for state tracking.
- **`Strategies`**: Implemented as a strategy pattern for extensibility and performance.

### Complexity
- **Time Complexity**: $O(1)$ for message processing. Strategy execution uses $O(N)$ for mean calculation (over history length).
- **Space Complexity**: $O(S 	imes H)$ for symbol state and history.

### Architecture
```text
+----------------+      +------------------+      +----------------+
|    Exchange    | <--> | TcpExchangeConnection | <--> |   TradingBot   |
+----------------+      +------------------+      +-------+--------+
                                                          |
                                              +-----------v-----------+
                                              |      MarketState      |
                                              +-----------+-----------+
                                                          |
                                              +-----------v-----------+
                                              |       Strategies      |
                                              | (Bond, Adr, Etf)      |
                                              +-----------------------+
```

## d) UML Sequence Diagram
| Participant | Action | Description |
| :--- | :--- | :--- |
| **Bot** | Connect | Establish Socket connection |
| **Bot** -> **Exchange** | `hello` | Send team handshake |
| **Exchange** -> **Bot** | `hello` | Receive initial market state |
| **Exchange** -> **Bot** | `book` / `trade` | Receive price updates |
| **Bot** | `handle_message` | Parse JSON and update `MarketState` |
| **Bot** | `execute_strategies` | Iterate through strategies |
| **Bot** -> **Exchange** | `add` / `convert` | Transmit orders |
| **Exchange** -> **Bot** | `fill` | Update positions on execution |

## e) Flowchart
```text
[Start] -> [Initialize Sockets]
   |
   v
[Connect to Host] -> [Send Handshake]
   |                      ^
   v                      |
[Recv Message] <----------+
   |
   +--> [Is Update?] -> [Update state.books] ------+
   |                                               |
   +--> [Is Trade?] -> [Update state.trades] ------+
   |                                               |
   +--> [Is Fill?] -> [Update state.positions] ----+
   |                                               |
   v                                               v
[Run Strategies] <---------------------------------+
   |
   +--> [Iterate Strat List]
   |
   v
[Send Orders to Socket]
   |
   +-----------------------+
                           |
                           v
                     (Wait for Next Message)
```

## f) Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| **Language** | C++26 |
| **Build System** | CMake |
| **CLI Library** | CLI11 |
| **JSON Library** | nlohmann/json |
| **Test Framework** | Google Test / Google Mock |
| **Containerization** | Docker (GCC 14 base) |
| **Design Pattern** | Strategy, Interface segregation |


### Rust

# Jane Street ETC - Rust Solution

## a) Directory Structure
```text
rust/
├── src/
│   ├── bot.rs          # Bot orchestration
│   ├── exchange.rs     # Async TCP handling
│   ├── lib.rs          # Module declarations and tests
│   ├── main.rs         # CLI entry point
│   ├── models.rs       # Data structures
│   └── strategies.rs   # Strategy implementations
├── Cargo.toml          # Cargo configuration
└── Dockerfile          # Containerization
```

## b) Instructions

### Local Build and Run
1. Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. Build: `cargo build --release`
3. Run tests: `cargo test`
4. Run the bot: `./target/release/jane-street-etc --host <host> --port <port> --team <team>`

### Docker Build and Run
1. Build image: `docker build -t etc-bot-rust .`
2. Run container: `docker run etc-bot-rust --host <host> --port <port> --team <team>`

## c) Solution Explanation
The Rust solution leverages the language's safety and performance characteristics:
- **`Tokio`**: Provides a high-performance asynchronous runtime for non-blocking I/O.
- **`Serde`**: Zero-copy JSON serialization/deserialization.
- **`MarketState`**: Thread-safe-ready data structures with predictable memory layout.

### Complexity
- **Time Complexity**: $O(1)$ for message handling. Strategy execution is $O(N)$ over history.
- **Space Complexity**: $O(S 	imes H)$ for state retention.

### Architecture
```text
+----------------+      +------------------+      +----------------+
|    Exchange    | <--> | Async TcpStream  | <--> |   TradingBot   |
+----------------+      +------------------+      +-------+--------+
                                                          |
                                              +-----------v-----------+
                                              |      MarketState      |
                                              +-----------+-----------+
                                                          |
                                              +-----------v-----------+
                                              |       Strategies      |
                                              | (Bond, Adr, Etf)      |
                                              +-----------------------+
```

## d) UML Sequence Diagram
| Participant | Action | Description |
| :--- | :--- | :--- |
| **Bot** | `connect().await` | Establish Async TCP connection |
| **Bot** -> **Exchange** | `hello` | Handshake |
| **Exchange** -> **Bot** | `hello` | Initial data |
| **Exchange** -> **Bot** | `book` / `trade` | Market updates |
| **Bot** | `handle_message` | Update internal state |
| **Bot** | `execute_strategies` | Evaluate market opportunities |
| **Bot** -> **Exchange** | `add` / `convert` | Execute orders |
| **Exchange** -> **Bot** | `fill` | Update position state |

## e) Flowchart
```text
[Start] -> [Async Connect]
   |
   v
[Wait for Handshake] -> [Enter Main Loop]
   |                         ^
   v                         |
[Await .read()] <------------+
   |
   +--> [JSON Parse] -> [Match Message Type]
   |                      |
   |                      +-> [Update State]
   |
   v
[Run Strategies]
   |
   +--> [Iterate Dyn Strategies]
   |
   v
[Async Send Actions]
   |
   +-------------------------+
                             |
                             v
                       (Await Next)
```

## f) Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| **Language** | Rust 1.84 (Stable) |
| **Build System** | Cargo |
| **CLI Library** | Clap v4 |
| **Async Runtime** | Tokio |
| **Serialization** | Serde |
| **Test Framework** | Native Cargo Tests |
| **Containerization** | Docker |


