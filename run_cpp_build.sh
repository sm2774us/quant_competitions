#!/bin/bash
set -e
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -G Ninja -DCMAKE_CXX_STANDARD=26
cmake --build .
# Check if tests exist before running
if [ -f "./test_strategies" ]; then ./test_strategies; fi
if [ -f "./citadel_tests" ]; then ./citadel_tests; fi
