FROM rust:1.84

WORKDIR /app

COPY . .

RUN cargo build --release

ENTRYPOINT ["./target/release/jane-street-etc"]
