#!/bin/bash
set -e
PROJ_DIR=$1
ABS_PROJ_DIR=$(realpath "$PROJ_DIR")
echo "Running Python build in $ABS_PROJ_DIR"

cd "$ABS_PROJ_DIR"

# Ensure lock file is consistent without upgrading dependencies
poetry lock --no-update

# Retry mechanism for poetry install to handle BadZipFile or network flakes
MAX_RETRIES=3
RETRY_COUNT=0
SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if poetry install --no-interaction; then
        SUCCESS=true
        break
    else
        echo "Poetry install failed. Clearing cache and retrying ($((RETRY_COUNT+1))/$MAX_RETRIES)..."
        poetry cache clear --all . -n || true
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "Poetry install failed after $MAX_RETRIES attempts."
    exit 1
fi

poetry run pytest
