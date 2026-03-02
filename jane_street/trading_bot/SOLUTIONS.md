# Jane Street Trading Bot - Solutions Summary

This repository contains three independent, high-performance implementations of the Jane Street Trading Bot challenge.

## Implementations

| Language | Build Tool | CLI Library | Documentation |
| :--- | :--- | :--- | :--- |
| **Python 3.13** | Poetry | `click` | [Read More](./python/README.md) |
| **C++26** | CMake | `CLI11` | [Read More](./cpp/README.md) |
| **Rust 1.93.1** | Cargo | `clap` | [Read More](./rust/README.md) |

## Common Entry Point (Bazel)

A `WORKSPACE` and `BUILD` file are provided at the root to allow building and testing all solutions through a single command.

### Bazel Instructions

#### Build all solutions
```bash
bazel build //...
```

#### Run all tests
```bash
bazel test //...
```

#### Run Coverage Reports
```bash
bazel coverage //...
```

#### Docker Mode (with Bazel)
To build container images using Bazel:
```bash
bazel run //python:image
bazel run //cpp:image
bazel run //rust:image
```

## Strategy Comparison

All implementations utilize a robust "BOND Arbitrage" strategy by default:
1.  **Fixed Fair Value:** BONDS have a guaranteed fair value of 1000.
2.  **Aggressive Taker:** Take any liquidity in the book that is mispriced (buy < 1000, sell > 1000).
3.  **Passive Maker:** Maintain orders at the tightest possible spread around fair value (buy at 999, sell at 1001).
4.  **Position Management:** Strictly adhere to the +/- 100 position limit for BONDS to avoid penalties and manage risk.

## Directory Structure
```text
.
├── README.md           # Challenge Description
├── SOLUTIONS.md        # This file
├── WORKSPACE           # Bazel Workspace
├── BUILD               # Bazel Build Rules
├── python/             # Python 3.13 Implementation
├── cpp/                # C++26 Implementation
├── rust/               # Rust 1.93.1 Implementation
└── old_code/           # Original Challenge Code
```
