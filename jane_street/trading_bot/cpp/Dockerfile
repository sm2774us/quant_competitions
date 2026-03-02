FROM gcc:14 AS build

RUN apt-get update && apt-get install -y cmake git

WORKDIR /app

COPY . .

RUN mkdir build && cd build && 
    cmake .. -DCMAKE_BUILD_TYPE=Release && 
    cmake --build . --parallel $(nproc)

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=build /app/build/trading_bot .

ENTRYPOINT ["./trading_bot"]
CMD ["--host", "localhost", "--port", "25000", "--team", "TEAMNAME"]
