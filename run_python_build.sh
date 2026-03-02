#!/bin/bash
set -e
PROJ_DIR=$1
echo "Running Python build in $PROJ_DIR"
cd "$PROJ_DIR"
poetry install --no-interaction
poetry run pytest
