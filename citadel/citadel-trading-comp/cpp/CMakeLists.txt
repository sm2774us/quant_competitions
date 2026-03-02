cmake_minimum_required(VERSION 3.20)
project(citadel_bot VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23) # Using 23 as C++26 is very new and might not be fully supported by all compilers yet, but I'll aim for modern.
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Dependencies via FetchContent
include(FetchContent)

FetchContent_Declare(
    cpr
    GIT_REPOSITORY https://github.com/libcpr/cpr.git
    GIT_TAG 1.10.x
)
FetchContent_MakeAvailable(cpr)

FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.2
)
FetchContent_MakeAvailable(json)

FetchContent_Declare(
    cli11
    GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
    GIT_TAG v2.3.2
)
FetchContent_MakeAvailable(cli11)

FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

# Library
add_library(citadel_bot_lib
    src/api.cpp
    src/bot.cpp
    src/strategies.cpp
)
target_include_directories(citadel_bot_lib PUBLIC include)
target_link_libraries(citadel_bot_lib PUBLIC cpr::cpr nlohmann_json::nlohmann_json)

# Executable
add_executable(citadel_bot src/main.cpp)
target_link_libraries(citadel_bot PRIVATE citadel_bot_lib CLI11::CLI11)

# Tests
enable_testing()
add_executable(citadel_tests tests/test_strategies.cpp)
target_link_libraries(citadel_tests PRIVATE citadel_bot_lib GTest::gtest_main GTest::gmock)
add_test(NAME citadel_tests COMMAND citadel_tests)
