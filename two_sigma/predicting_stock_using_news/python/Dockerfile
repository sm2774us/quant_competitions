FROM python:3.13-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

RUN poetry config virtualenvs.create false 
    && poetry install --no-interaction --no-ansi

# Add src to python path
ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "src/two_sigma_news/main.py"]
CMD ["--help"]
