# Use Rust 1.93.1 or latest stable
FROM rust:latest

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build for release
RUN cargo build --release

# Entry point
ENTRYPOINT ["/app/target/release/market-prediction"]
