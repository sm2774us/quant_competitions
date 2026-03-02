#!/bin/bash
cd rust
cargo build --release
cargo run --release -- generate-data --samples 100 --output data/train.csv
cargo run --release -- train --data data/train.csv --model-path models/model.json
cargo run --release -- evaluate --data data/train.csv --model-path models/model.json
