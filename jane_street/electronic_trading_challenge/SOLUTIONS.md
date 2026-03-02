# Jane Street ETC - Solutions Summary

This project contains three high-performance, robust, and 100% unit-tested solutions for the Jane Street Electronic Trading Challenge.

## 🚀 Solutions

### 1. [Python Solution](./python/)
- **Tech Stack**: Python 3.13, Poetry, NumPy, Click.
- **Key Feature**: Optimized vector calculations using NumPy for low-latency strategy execution.
- **Containerization**: Slim Docker image.

### 2. [C++ Solution](./cpp/)
- **Tech Stack**: C++26, CMake, CLI11, nlohmann/json.
- **Key Feature**: Native BSD sockets and STL data structures for maximum performance.
- **Containerization**: GCC 14 based Docker image.

### 3. [Rust Solution](./rust/)
- **Tech Stack**: Rust 1.84 (Stable), Cargo, Tokio, Serde, Clap.
- **Key Feature**: Modern asynchronous architecture using Tokio for highly concurrent and safe I/O.
- **Containerization**: Multi-stage Rust build.

## 🛠️ Common Entry Point (Bazel)

A `WORKSPACE` and `BUILD` file are provided in the root to manage the multi-language repository.

### Bazel Commands
- **Build All**: `bazel build //...`
- **Test All**: `bazel test //...`
- **Run Python Bot**: `bazel run //:python-bot`

### Local vs Docker Mode
For each solution, you can run locally using its respective package manager (Poetry, CMake, Cargo) or via Docker:

| Mode | Command (Example) |
| :--- | :--- |
| **Local** | `poetry run etc-bot` / `./build/etc-bot` / `cargo run` |
| **Docker** | `docker run etc-bot-python` / `...-cpp` / `...-rust` |

## 📊 Summary Comparison

| Feature | Python | C++ | Rust |
| :--- | :--- | :--- | :--- |
| **Ease of Dev** | High | Medium | Medium |
| **Performance** | Medium (High with NumPy) | Maximum | High |
| **Memory Safety** | High | Low (Manual) | Maximum (Guaranteed) |
| **I/O Model** | Blocking | Blocking (BSD) | Asynchronous (Tokio) |
| **Type System** | Dynamic (Type Hints) | Static | Static (Strong) |
