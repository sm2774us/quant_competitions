FROM gcc:14 AS builder

RUN apt-get update && apt-get install -y cmake git libcurl4-openssl-dev

WORKDIR /app
COPY . .

RUN mkdir build && cd build && 
    cmake .. -DCMAKE_BUILD_TYPE=Release && 
    cmake --build . --target citadel_bot

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y libcurl4 ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/build/citadel_bot .

ENTRYPOINT ["./citadel_bot"]
