# Trading Bot - Rust Solution

## Directory Structure
```text
rust/
├── Cargo.toml
├── Dockerfile
├── README.md
└── src/
    ├── bot.rs
    ├── exchange.rs
    ├── main.rs
    ├── models.rs
    └── strategy.rs
```

## Instructions

### Local Build and Run
1.  **Prerequisites:** Rust 1.81+ (using Cargo).
2.  **Build:** `cargo build --release`
3.  **Run Tests:** `cargo test`
4.  **Run Bot:** `cargo run --release -- --host localhost --port 25000 --team MYTEAM`

### Docker Build and Run
1.  **Build Image:** `docker build -t trading-bot-rust .`
2.  **Run Container:** `docker run trading-bot-rust --host host.docker.internal --port 25000`

## Solution Explanation
The Rust solution focuses on safety, concurrency readiness, and performance:
-   **Serde Integration:** Using `serde` for extremely fast and safe JSON parsing.
-   **Strong Typing:** Leveraging Rust's enum system to represent market and client messages.
-   **Error Handling:** Using `anyhow` for robust error reporting.
-   **CLI:** Built with `clap` (derive API) for a modern CLI experience.

### Time and Space Complexity
-   **Time Complexity:** $O(1)$ per message. Hash map lookups in Rust are highly optimized.
-   **Space Complexity:** $O(S)$, where $S$ is the number of symbols.

### Solution Architecture (ASCII)
```text
+----------+      +------------+      +------------+
| Exchange | <--> |    Bot     | <--> |  Strategy  |
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
[Start] -> [TCP Connect] -> [Handshake]
   ^                            |
   |                            v
   |                     [Read JSON Line]
   |                            |
   +--- [Update State] <--- (Fill?) <--+--> (Book?) ----> [Logic]
                                       |                    |
                                       v                    v
                                    (Other)            [Write JSON]
                                       |                    |
                                       +<-------------------+
```

### Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| Language | Rust 1.93.1 |
| Build Tool | Cargo |
| CLI Library | Clap |
| Testing | Native (Cargo Test) |
| JSON Library | Serde / serde_json |
| Strategy | BOND Arbitrage |
