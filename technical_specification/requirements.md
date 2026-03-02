# 📄 Technical Specification & Requirements

## 1. Overview
The **Quant Competitions Monorepo** is an elite-grade, multi-language framework designed to host production-grade automated trading solutions. It provides a standardized environment for developing, testing, and documenting strategies for high-frequency trading (HFT) and quantitative modeling competitions.

## 2. Architectural Framework

### 2.1 Monorepo Structure
The repository follows a strict `[Company]/[Competition]/[Language]` hierarchy:
- **Root**: Contains orchestration scripts (`generate_build.py`, `generate_docs.py`), Bazel configuration, and global documentation.
- **Company Folders**: (e.g., `citadel`, `jane_street`) Logic containers for specific institutions.
- **Competition Folders**: (e.g., `citadel-trading-comp`) Self-contained project environments.
- **Language Subdirectories**: (`python`, `cpp`, `rust`) Implementation-specific code using modern standards.

### 2.2 Orchestration Engine
- **Unified Build**: Bazel 7.4.1 (LTS) acts as the high-level orchestrator.
- **Dynamic Discovery**: Python scripts automatically scan the directory tree to generate Bazel `BUILD` targets and MkDocs navigation.
- **Local Execution**: Bazel targets use `local = 1` to leverage system-level toolchains while maintaining a unified interface.

## 3. Technical Requirements

### 3.1 Language Standards
- **Python 3.13**: Must use modern type hinting (PEP 695 `type` statements), Pydantic v2 for data validation, and Poetry for dependency management.
- **C++26**: Compiled with `g++-14`. Must leverage `std::println`, structured bindings with placeholders, and zero-overhead abstractions.
- **Rust 1.93.1**: Target **Edition 2024**. Must use `anyhow` for error handling and `serde` for high-performance JSON serialization.

### 3.2 Performance Mandates
- **Latency**: Main trading loops must target sub-millisecond processing times per market tick.
- **Memory**: C++ and Rust implementations must prioritize stack allocation and cache-friendly data structures (e.g., `std::vector` over `std::list`).
- **Vectorization**: Python solutions must utilize NumPy/Pandas for bulk data processing to overcome GIL limitations.

## 4. CI/CD Pipeline

### 4.1 Continuous Integration (ci.yml)
- **Validation**: Every push triggers a full build/test cycle across all 21+ targets.
- **Toolchains**: Uses Ubuntu 24.04 runners with pre-configured GCC 14, Rust 1.93.1, and Python 3.13.
- **Bazel**: Orchestrates parallel test execution with `bazel test //...`.

### 4.2 Automated Documentation (docs.yml)
- **Generation**: `generate_docs.py` builds a "book-like" documentation site.
- **Deployment**: Deployed to GitHub Pages using MkDocs Material with Mermaid and MathJax support.

## 5. Competition-Specific Implementations

### 5.1 Citadel
- **Exchange Arbitrage**: Cross-exchange spread capture.
- **Index Arbitrage**: Component vs. ETF deviation.
- **Shock Handling**: News sentiment response.

### 5.2 Jane Street
- **Market Making**: Liquidity provision and fair value estimation.
- **Electronic Trading**: ADR/ETF arbitrage and bond pricing.

### 5.3 Two Sigma
- **Financial Modeling**: Predictive time-series analysis.
- **News Sentiment**: NLP-driven alpha extraction.

---

## 6. Extensibility
The framework is designed for **zero-touch extension**:
1. Create a new company folder (e.g., `goldman_sachs`).
2. Add a competition subfolder with `python/`, `cpp/`, or `rust/` implementations.
3. The CI and Docs pipelines will automatically detect and integrate the new project on the next push.

---
*Last Updated: 2026-03-02*
