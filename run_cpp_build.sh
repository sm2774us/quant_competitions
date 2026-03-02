#!/bin/bash
set -e
export CXX=g++-14
PROJ_DIR=$1
ABS_PROJ_DIR=$(realpath "$PROJ_DIR")
echo "Running C++ build in $ABS_PROJ_DIR"

cd "$ABS_PROJ_DIR"
mkdir -p build
cd build
cmake -S .. -B . -DCMAKE_BUILD_TYPE=Release -G Ninja -DCMAKE_CXX_STANDARD=26
cmake --build .

# Check if tests exist before running
if [ -f "./citadel_tests" ]; then ./citadel_tests; fi
if [ -f "./test_strategies" ]; then ./test_strategies; fi
if [ -f "./run_tests" ]; then ./run_tests; fi
if [ -f "./etc_tests" ]; then ./etc_tests; fi
if [ -f "./test_bot" ]; then ./test_bot; fi
