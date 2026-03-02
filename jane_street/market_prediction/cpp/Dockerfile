# Use a recent GCC image for C++26 support
FROM gcc:latest

# Install CMake
RUN apt-get update && apt-get install -y cmake

# Set working directory
WORKDIR /app

# Copy source code
COPY . .

# Create build directory
RUN mkdir build && cd build && 
    cmake .. -DCMAKE_BUILD_TYPE=Release && 
    make -j$(nproc)

# Entry point
ENTRYPOINT ["/app/build/market-prediction"]
