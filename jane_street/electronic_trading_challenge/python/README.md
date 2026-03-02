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
