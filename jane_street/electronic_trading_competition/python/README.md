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
