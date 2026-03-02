# Use a recent Rust version
FROM rust:1.84

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build the project
RUN cargo build --release

# Expose data directory for mounting
VOLUME ["/app/data", "/app/models"]

# Set entrypoint
ENTRYPOINT ["/app/target/release/two_sigma_financial_modeling"]
CMD ["--help"]
