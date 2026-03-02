#!/bin/bash
set -e
export HOME=$PWD
cargo build --release
cargo test
