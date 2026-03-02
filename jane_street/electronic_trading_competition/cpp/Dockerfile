# Use a modern C++ compiler
FROM gcc:latest

# Install CMake and other dependencies
RUN apt-get update && apt-get install -y cmake git tar xz-utils

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Build the project
RUN mkdir build && cd build && 
    cmake .. -DCMAKE_BUILD_TYPE=Release && 
    cmake --build .

# Run the bot
ENTRYPOINT ["./build/trading_bot"]
