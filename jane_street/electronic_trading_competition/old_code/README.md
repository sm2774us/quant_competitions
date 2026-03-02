# Jane Street Electronic Trading Competition

## Overview
This project implements a high-performance algorithmic trading bot designed for the Jane Street Electronic Trading Competition. The bot interacts with a simulated exchange via a TCP socket, processing real-time market data and executing trades across multiple strategies including market making, arbitrage, and technical analysis.

## The Challenge
The goal is to maximize profit (PNL) while managing risk and liquidity in a competitive environment. The bot must handle a high-throughput stream of JSON messages from the exchange and respond with low latency.

### Market Protocols
- **Communication:** TCP Socket with newline-delimited JSON messages.
- **Message Types:** `hello`, `open`, `book`, `trade`, `fill`, `ack`, `reject`, `error`, `out`.
- **Order Types:** `add` (Limit Orders), `cancel`, `convert`.

### Assets and Strategies
1. **BOND Trading:** Trading a fixed-value asset (par value 1000) using market-making strategies.
2. **Pennying (Market Making):** Dynamically adjusting bid/ask prices to capture the spread by outbidding the market by the minimum tick size.
3. **ADR Arbitrage:** Exploiting price differences between `VALE` (the stock) and `VALBZ` (the ADR) via direct trades and the `convert` mechanism.
4. **ETF Arbitrage:** Trading `XLF` against its components (`BOND`, `GS`, `MS`, `WFC`). This involves calculating the Net Asset Value (NAV) and executing basket trades or conversions when the premium/discount exceeds costs.
5. **Technical Analysis (MACD):** Using Exponential Moving Averages (EMA) to identify momentum shifts and trend reversals for directional trading.

## Project Structure
This repository contains production-grade implementations in three languages:
- `./python`: Python 3.13 implementation using Poetry.
- `./cpp`: C++26 implementation using CMake.
- `./rust`: Rust implementation using Cargo.

Each implementation is fully containerized, robustly tested, and optimized for performance.

## Getting Started
Refer to the `SOLUTIONS.md` file in this directory for a summary of all implementations and a unified Bazel entry point for building, testing, and running the solutions.
