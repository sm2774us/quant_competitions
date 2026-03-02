# Use Python 3.13
FROM python:3.13-slim

# Install poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY src/ ./src/
COPY README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false 
    && poetry install --no-interaction --no-ansi

# Expose data directory for mounting
VOLUME ["/app/data", "/app/models"]

# Set entrypoint to use the CLI
ENTRYPOINT ["two-sigma"]
CMD ["--help"]
