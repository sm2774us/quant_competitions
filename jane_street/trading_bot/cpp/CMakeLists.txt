cmake_minimum_required(VERSION 3.25)
project(trading_bot VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(include)

# Dependencies (using FetchContent for JSON)
include(FetchContent)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(nlohmann_json)

# CLI library (using CLI11)
FetchContent_Declare(
    cli11
    GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
    GIT_TAG v2.3.2
)
FetchContent_MakeAvailable(cli11)

# GTest
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/03597a01ee9d7941a87677d33d937085b30b05b3.zip
)
FetchContent_MakeAvailable(googletest)

# Library
add_library(trading_bot_lib
    src/exchange.cpp
    src/strategy.cpp
    src/bot.cpp
)
target_link_libraries(trading_bot_lib nlohmann_json::nlohmann_json)

# Executable
add_executable(trading_bot src/main.cpp)
target_link_libraries(trading_bot trading_bot_lib CLI11::CLI11)

# Tests
enable_testing()
add_executable(trading_bot_tests tests/test_bot.cpp)
target_link_libraries(trading_bot_tests trading_bot_lib GTest::gtest_main GTest::gmock)
include(GoogleTest)
gtest_discover_tests(trading_bot_tests)
