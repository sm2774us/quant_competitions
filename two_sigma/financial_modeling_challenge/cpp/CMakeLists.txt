cmake_minimum_required(VERSION 3.25)
project(TwoSigmaFinance CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# Fetch CLI11 for command-line parsing
FetchContent_Declare(
  cli11
  GIT_REPOSITORY https://github.com/CLIUtils/CLI11.git
  GIT_TAG        v2.4.2
)
FetchContent_MakeAvailable(cli11)

# Fetch GTest for unit testing
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        v1.14.0
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

# Fetch Eigen for linear algebra
FetchContent_Declare(
  eigen
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG        3.4.0
)
FetchContent_MakeAvailable(eigen)

include_directories(include ${EIGEN3_INCLUDE_DIR})

# Main executable
add_executable(two-sigma
    src/main.cpp
    src/model.cpp
    src/environment.cpp
    src/data_generator.cpp
)
target_link_libraries(two-sigma CLI11::CLI11)

# Tests
add_executable(two-sigma-tests
    tests/test_solution.cpp
    src/model.cpp
    src/environment.cpp
    src/data_generator.cpp
)
target_link_libraries(two-sigma-tests GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(two-sigma-tests)
