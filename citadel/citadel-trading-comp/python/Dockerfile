FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock* README.md ./
COPY citadel_bot ./citadel_bot

RUN poetry config virtualenvs.create false 
    && poetry install --no-dev

ENTRYPOINT ["citadel-bot"]
