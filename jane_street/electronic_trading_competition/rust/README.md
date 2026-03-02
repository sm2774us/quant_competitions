# Rust Trading Bot Implementation

## Directory Structure
```text
rust/
├── Cargo.toml
├── Dockerfile
├── README.md
├── RNN-DJIA/
└── src/
    ├── exchange_client.rs
    ├── main.rs
    ├── models.rs
    └── strategies.rs
```

## Instructions

### Local Build and Run
1. Ensure Rust 1.93.1 is installed.
2. Build: `cargo build --release`
3. Run tests: `cargo test`
4. Run bot: `./target/release/trading-bot --hostname production --port 25000 --team PANIPURISTREET`

### Docker Build and Run
1. Build image: `docker build -t trading-bot-rust .`
2. Run bot: `docker run trading-bot-rust --hostname production --port 25000 --team PANIPURISTREET`

## Solution Explanation

### Architecture
The Rust implementation leverages `tokio` for high-performance asynchronous I/O. It uses a strong type system (Enums for messages) to ensure safety and correctness at compile time. Memory management is handled via ownership, eliminating data races and memory leaks.

```text
+----------------+      +------------------+      +-------------------+
|   Exchange     | <--> |  ExchangeClient  | <--> |      tokio loop   |
+----------------+      +------------------+      +---------+---------+
                                                            |
                                           +----------------+----------------+
                                           |                |                |
                                   +-------v-------+ +------v------+ +-------v-------+
                                   | BondStrategy  | | ADRStrategy | | MACDStrategy  |
                                   +---------------+ +-------------+ +---------------+
```

### Time and Space Complexity
- **Time Complexity:** O(N) per message. Rust's zero-cost abstractions provide the lowest latency among all implementations.
- **Space Complexity:** O(M) where M is the number of active symbols.

## UML Sequence Diagram
```text
Exchange -> ExchangeClient: BookMessage(BOND)
ExchangeClient -> main: next_message()
main -> BondStrategy: update_book(buy, sell)
BondStrategy -> main: Vec<Order>
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
| MACD | Trend Following | O(1) | Extremely High |
