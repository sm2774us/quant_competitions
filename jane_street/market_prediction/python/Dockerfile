# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
    PYTHONUNBUFFERED=1 
    POETRY_VERSION=2.1.1 
    POETRY_HOME="/opt/poetry" 
    POETRY_NO_INTERACTION=1 
    POETRY_VIRTUALENVS_CREATE=false

# Add poetry to path
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends 
    curl 
    build-essential 
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install project dependencies
RUN poetry install --no-root --only main

# Copy source code
COPY . .

# Install the project itself
RUN poetry install --only main

# Entry point
ENTRYPOINT ["poetry", "run", "market-prediction"]
