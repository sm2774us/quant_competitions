cmake_minimum_required(VERSION 3.25)
project(TradingBot LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(src)

# Dependencies (using FetchContent for simplicity)
include(FetchContent)

FetchContent_Declare(
    json
    URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
)
FetchContent_MakeAvailable(json)

FetchContent_Declare(
    argparse
    GIT_REPOSITORY https://github.com/p-ranav/argparse.git
    GIT_TAG v3.0
)
FetchContent_MakeAvailable(argparse)

FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Source files
set(SOURCES
    src/exchange_client.cpp
    src/strategies.cpp
)

# Executable
add_executable(trading_bot src/main.cpp ${SOURCES})
target_link_libraries(trading_bot PRIVATE nlohmann_json::nlohmann_json argparse)

# Tests
enable_testing()
add_executable(test_trading_bot tests/test_strategies.cpp ${SOURCES})
target_link_libraries(test_trading_bot PRIVATE gtest_main nlohmann_json::nlohmann_json)
add_test(NAME StrategyTests COMMAND test_trading_bot)
