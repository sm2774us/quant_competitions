cmake_minimum_required(VERSION 3.25)
project(JaneStreetETC VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# JSON library
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(json)

# CLI library
FetchContent_Declare(
    cli11
    GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
    GIT_TAG v2.3.2
)
FetchContent_MakeAvailable(cli11)

# GTest
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG v1.14.0
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_library(etc_lib
    src/models.cpp
    src/exchange.cpp
    src/strategies.cpp
    src/bot.cpp
)
target_include_directories(etc_lib PUBLIC include)
target_link_libraries(etc_lib PUBLIC nlohmann_json::nlohmann_json)

add_executable(etc-bot src/main.cpp)
target_link_libraries(etc-bot PRIVATE etc_lib CLI11::CLI11)

enable_testing()
add_executable(etc_tests tests/test_bot.cpp)
target_link_libraries(etc_tests PRIVATE etc_lib GTest::gtest_main)
add_test(NAME etc_tests COMMAND etc_tests)
