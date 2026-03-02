FROM python:3.13-slim

# Install poetry
RUN pip install poetry

WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use virtualenvs inside container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev

# Copy source
COPY src/ ./src/

# Install the package
RUN poetry install --only-root

# Run the bot
ENTRYPOINT ["etc-bot"]
