FROM gcc:14 AS build

WORKDIR /app

RUN apt-get update && apt-get install -y cmake git

COPY . .

RUN mkdir build && cd build && 
    cmake .. && 
    make -j$(nproc)

FROM debian:bookworm-slim

WORKDIR /app

COPY --from=build /app/build/two_sigma_news /app/two_sigma_news
COPY --from=build /app/build/test_two_sigma /app/test_two_sigma

ENTRYPOINT ["./two_sigma_news"]
CMD ["--help"]
