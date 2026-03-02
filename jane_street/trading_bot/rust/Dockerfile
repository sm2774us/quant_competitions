FROM rust:1.81-slim AS build

WORKDIR /app

COPY . .

RUN cargo build --release

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=build /app/target/release/trading-bot .

ENTRYPOINT ["./trading-bot"]
CMD ["--host", "localhost", "--port", "25000", "--team", "TEAMNAME"]
