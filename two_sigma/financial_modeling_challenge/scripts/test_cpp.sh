#!/bin/bash
cd cpp
mkdir -p build && cd build
cmake ..
make -j$(nproc)
./two-sigma-tests
