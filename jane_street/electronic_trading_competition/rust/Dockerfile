# Use the official Rust image
FROM rust:1.93.1-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build the project
RUN cargo build --release

# Run the bot
ENTRYPOINT ["./target/release/trading-bot"]
