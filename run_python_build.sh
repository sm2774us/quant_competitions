#!/bin/bash
set -e
export HOME=$PWD
poetry install --no-interaction
poetry run pytest
