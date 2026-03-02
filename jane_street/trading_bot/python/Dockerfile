FROM python:3.13-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml README.md ./
COPY trading_bot/ ./trading_bot/

# Install dependencies
RUN poetry config virtualenvs.create false 
    && poetry install --no-interaction --no-ansi

# Entry point
ENTRYPOINT ["trading-bot"]
CMD ["--host", "localhost", "--port", "25000", "--team", "TEAMNAME"]
