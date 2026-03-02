FROM gcc:14

RUN apt-get update && apt-get install -y cmake git

WORKDIR /app

COPY . .

RUN mkdir build && cd build && 
    cmake .. -DCMAKE_BUILD_TYPE=Release && 
    cmake --build . --target etc-bot

ENTRYPOINT ["./build/etc-bot"]
