# Jane Street Trading Bot Challenge

## Overview
This challenge involves building a robust, high-performance trading bot for the Jane Street Electronic Trading Competition (ETC). The bot must connect to an exchange via a TCP socket and communicate using a custom JSON-based protocol. The primary goal is to maximize profit by trading various securities (e.g., BOND, VALBZ, VALE) based on market data and proprietary strategies.

## Core Objectives
- **Connectivity:** Establish and maintain a reliable TCP connection to the exchange.
- **Protocol Management:** Accurately parse and generate JSON messages for communication with the exchange.
- **Strategy Implementation:**
    - **BOND Strategy:** Trade BONDS, which have a fixed fair value of 1000. Buy at 999 and sell at 1001.
    - **Fair Price Strategy:** Calculate the fair price for other securities using a running average of the mid-price (average of the best bid and best ask) or other indicators.
- **Position Management:** Keep track of current positions for each security and ensure they do not exceed pre-defined limits (e.g., +/- 100 for BOND).
- **Performance:** Ensure high-speed execution to capitalize on transient market opportunities.

## Exchange Protocol
The bot communicates with the exchange using JSON objects separated by newlines (`
`).

### Client Messages (Bot to Exchange)
- **Hello:** `{"type": "hello", "team": "TEAMNAME"}` - Initial handshake.
- **Add Order:** `{"type": "add", "order_id": int, "symbol": string, "dir": "BUY"|"SELL", "price": int, "size": int}` - Places a new limit order.
- **Cancel Order:** `{"type": "cancel", "order_id": int}` - Cancels an existing order.
- **Convert:** `{"type": "convert", "order_id": int, "symbol": string, "dir": "BUY"|"SELL", "size": int}` - Converts ETFs to their underlying assets or vice versa.

### Exchange Messages (Exchange to Bot)
- **Hello:** `{"type": "hello", "symbols": [{"symbol": "BOND", "position": 0}, ...]}` - Acknowledges the handshake and provides initial positions.
- **Open/Close:** `{"type": "open"|"close", "symbols": [string, ...]}` - Notification that trading has opened or closed for certain symbols.
- **Book:** `{"type": "book", "symbol": string, "buy": [[price, size], ...], "sell": [[price, size], ...]}` - Updates on the current order book state.
- **Fill:** `{"type": "fill", "order_id": int, "symbol": string, "dir": "BUY"|"SELL", "price": int, "size": int}` - Notification that an order has been partially or fully filled.
- **Out:** `{"type": "out", "order_id": int}` - Notification that an order has been cancelled or has expired.
- **Trade:** `{"type": "trade", "symbol": string, "price": int, "size": int}` - Notification that a trade has occurred in the market (between any two participants).
- **Error:** `{"type": "error", "error": string}` - Notification of an error (e.g., invalid order).

## Implementation Requirements
This repository provides 100% fully implemented, robust, and tested solutions in three languages:
1. **Python 3.13:** Built with Poetry, using `click` for CLI and `pytest` for testing.
2. **C++26:** Built with CMake, using Google Test and a modern CLI library.
3. **Rust 1.93.1:** Built with Cargo, using `clap` for CLI and native testing framework.

Each solution is containerized using Docker and provides comprehensive documentation, including architecture diagrams, sequence diagrams, and flowcharts.

A common **Bazel** entry point is provided to build, test, and run all three solutions.
