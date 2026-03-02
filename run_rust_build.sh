#!/bin/bash
set -e
PROJ_DIR=$1
ABS_PROJ_DIR=$(realpath "$PROJ_DIR")
echo "Running Rust build in $ABS_PROJ_DIR"

# Source cargo environment if available
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"

cd "$ABS_PROJ_DIR"
# Ensure toolchain is active
rustup default stable > /dev/null 2>&1 || true
cargo build --release
cargo test
