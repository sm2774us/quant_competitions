#!/bin/bash
cd python
poetry install
poetry run pytest --cov=src tests/
