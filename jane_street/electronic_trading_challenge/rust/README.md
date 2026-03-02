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
