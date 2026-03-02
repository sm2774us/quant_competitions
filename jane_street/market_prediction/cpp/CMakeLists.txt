cmake_minimum_required(VERSION 3.28)
project(market_prediction_cpp VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# FetchContent for dependencies
include(FetchContent)

# Eigen
FetchContent_Declare(
    eigen
    GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
    GIT_TAG 3.4.0
)
FetchContent_MakeAvailable(eigen)

# CLI11
FetchContent_Declare(
    cli11
    GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
    GIT_TAG v2.4.2
)
FetchContent_MakeAvailable(cli11)

# nlohmann_json
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(json)

# GoogleTest
FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG v1.15.2
)
FetchContent_MakeAvailable(googletest)

# Library
add_library(market_prediction
    src/preprocessor.cpp
    src/models.cpp
    src/engine.cpp
    src/scorer.cpp
)
target_include_directories(market_prediction PUBLIC 
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(market_prediction PUBLIC Eigen3::Eigen nlohmann_json::nlohmann_json)

# Executable
add_executable(market-prediction src/main.cpp)
target_link_libraries(market-prediction PRIVATE market_prediction CLI11::CLI11)

# Tests
enable_testing()
add_executable(tests 
    tests/test_preprocessor.cpp 
    tests/test_models.cpp 
    tests/test_engine.cpp 
    tests/test_scorer.cpp
)
target_link_libraries(tests PRIVATE market_prediction GTest::gtest_main)
include(GoogleTest)
gtest_discover_tests(tests)
