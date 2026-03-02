# Use Python 3.13
FROM python:3.13-slim

# Install poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy source code
COPY src ./src
COPY README.md ./

# Install the project
RUN poetry install --only-root

# Run the bot
ENTRYPOINT ["trading-bot"]
