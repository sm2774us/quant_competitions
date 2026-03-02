#!/bin/bash
set -e
PROJ_DIR=$1
echo "Running Rust build in $PROJ_DIR"
cd "$PROJ_DIR"
# Ensure toolchain is active in this shell
rustup default stable > /dev/null 2>&1 || true
cargo build --release
cargo test
