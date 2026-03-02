# Trading Bot - C++ Solution

## Directory Structure
```text
cpp/
├── CMakeLists.txt
├── Dockerfile
├── README.md
├── include/
│   ├── bot.hpp
│   ├── exchange.hpp
│   ├── models.hpp
│   └── strategy.hpp
├── src/
│   ├── bot.cpp
│   ├── exchange.cpp
│   ├── main.cpp
│   └── strategy.cpp
└── tests/
    └── test_bot.cpp
```

## Instructions

### Local Build and Run
1.  **Prerequisites:** CMake 3.25+, GCC 14+ or Clang 18+, WinSock2 (on Windows).
2.  **Generate Build Files:** `mkdir build && cd build && cmake ..`
3.  **Build:** `cmake --build .`
4.  **Run Tests:** `ctest --output-on-failure`
5.  **Run Bot:** `./trading_bot --host localhost --port 25000 --team MYTEAM`

### Docker Build and Run
1.  **Build Image:** `docker build -t trading-bot-cpp .`
2.  **Run Container:** `docker run trading-bot-cpp --host host.docker.internal --port 25000`

## Solution Explanation
The C++ solution is designed for high-performance and uses modern C++26 features:
-   **Header-Only Models:** Using POD structs for efficient data handling.
-   **Exchange:** Cross-platform TCP implementation using standard sockets.
-   **Strategy:** Efficient position management and decision-making logic.
-   **CLI:** Integrated using CLI11 for a modern command-line experience.

### Time and Space Complexity
-   **Time Complexity:** $O(1)$ per message. Dictionary-like lookups using `std::map` provide logarithmic time, but could be $O(1)$ with `std::unordered_map`. For a small number of symbols, `std::map` is extremely fast.
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
[Start] -> [Socket Create] -> [Handshake]
   ^                              |
   |                              v
   |                        [Recv JSON]
   |                              |
   +--- [Update Pos] <---- (Fill?) <--+--> (Book?) ----> [Logic]
                                      |                    |
                                      v                    v
                                   (Other)            [Send Order]
                                      |                    |
                                      +<-------------------+
```

### Tabulated Summary
| Feature | Implementation |
| :--- | :--- |
| Language | C++26 |
| Build Tool | CMake |
| CLI Library | CLI11 |
| Testing | Google Test |
| JSON Library | nlohmann/json |
| Strategy | BOND Arbitrage |
