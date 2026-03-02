cmake_minimum_required(VERSION 3.25)
project(TwoSigmaNews LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# Fetch CLI11 for modern CLI
FetchContent_Declare(
  cli11
  GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
  GIT_TAG v2.3.2
)
FetchContent_MakeAvailable(cli11)

# Fetch GTest for testing
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG v1.14.0
)
FetchContent_MakeAvailable(googletest)

# Source files
set(SOURCE_FILES
    src/DataLoader.cpp
    src/Preprocessor.cpp
    src/Model.cpp
    src/Evaluator.cpp
)

add_executable(two_sigma_news src/main.cpp ${SOURCE_FILES})
target_link_libraries(two_sigma_news PRIVATE CLI11::CLI11)

# Tests
add_executable(test_two_sigma tests/test_two_sigma.cpp ${SOURCE_FILES})
target_link_libraries(test_two_sigma PRIVATE GTest::gtest_main GTest::gmock)

enable_testing()
add_test(NAME AllTests COMMAND test_two_sigma)
