# ============================================================================
# Algothon 2026 — Multi-stage Docker build
# Base: Ubuntu 24.04 LTS (noble)
# Python: 3.13 (official deadsnakes)
# C++: GCC-14 with C++26 support + Eigen
# ============================================================================

# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    git \
    curl \
    ca-certificates \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    liblzma-dev \
    libncurses5-dev \
    gcc-14 \
    g++-14 \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    python3-pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set GCC-14 as default (C++26 support)
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-14 100 \
    && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-14 100

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3.13 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /build

# Copy dependency files first (layer caching)
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.in-project true \
    && poetry install --no-root --only main

# Copy source
COPY . .

# Build C++ extension
RUN cmake -S . -B build_cpp \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CXX_COMPILER=g++-14 \
    -GNinja \
    && cmake --build build_cpp --parallel \
    && cmake --install build_cpp

# Install Python package
RUN poetry install --only main

# ── Stage 2: Runtime ─────────────────────────────────────────────────────────
FROM ubuntu:24.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.13 \
    libgomp1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment and built extension from builder
COPY --from=builder /build/.venv ./.venv
COPY --from=builder /build/src ./src
COPY --from=builder /build/data ./data

# Copy sample CSVs (runtime data)
COPY data/sample ./data/sample

# Non-root user for security
RUN useradd -m -u 1001 algothon && chown -R algothon:algothon /app
USER algothon

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3.13 -c "from src.python.data.loader import DataLoader; print('OK')"

EXPOSE 8888

ENTRYPOINT ["python3.13", "-m", "src.python.execution.engine"]
CMD ["--help"]
