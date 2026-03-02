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
