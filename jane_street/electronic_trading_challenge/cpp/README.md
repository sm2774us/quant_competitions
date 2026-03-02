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
