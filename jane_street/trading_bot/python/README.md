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
