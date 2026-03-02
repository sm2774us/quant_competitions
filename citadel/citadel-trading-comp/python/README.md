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
