# Use a recent GCC version for C++26 support
FROM gcc:14

# Install CMake
RUN apt-get update && apt-get install -y cmake git

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Build the project
RUN mkdir build && cd build && 
    cmake .. && 
    make -j$(nproc)

# Expose data directory for mounting
VOLUME ["/app/data", "/app/models"]

# Set entrypoint
ENTRYPOINT ["/app/build/two-sigma"]
CMD ["--help"]
