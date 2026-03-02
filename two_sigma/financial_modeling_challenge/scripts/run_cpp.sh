#!/bin/bash
cd cpp
mkdir -p build && cd build
cmake ..
make -j$(nproc)
./two-sigma generate-data --samples 100 --output data/train.csv
./two-sigma train --data data/train.csv --model-path models/model.bin
./two-sigma evaluate --data data/train.csv --model-path models/model.bin
