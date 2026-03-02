#!/bin/bash
set -e
export CXX=g++-14
PROJ_DIR=$1
echo "Running C++ build in $PROJ_DIR"
cd "$PROJ_DIR"
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -G Ninja -DCMAKE_CXX_STANDARD=26
cmake --build .
# Check if tests exist before running
if [ -f "./citadel_tests" ]; then ./citadel_tests; fi
if [ -f "./test_strategies" ]; then ./test_strategies; fi
if [ -f "./run_tests" ]; then ./run_tests; fi
