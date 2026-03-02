FROM rust:1.85-slim AS build

WORKDIR /app

COPY . .

RUN cargo build --release

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=build /app/target/release/two_sigma_news /app/two_sigma_news

ENTRYPOINT ["./two_sigma_news"]
CMD ["--help"]
