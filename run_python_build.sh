#!/bin/bash
set -e
PROJ_DIR=$1
ABS_PROJ_DIR=$(realpath "$PROJ_DIR")
echo "Running Python build in $ABS_PROJ_DIR"

cd "$ABS_PROJ_DIR"
poetry install --no-interaction
poetry run pytest
