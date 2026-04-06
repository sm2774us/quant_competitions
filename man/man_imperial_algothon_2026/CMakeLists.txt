cmake_minimum_required(VERSION 3.28)
project(algothon_cpp VERSION 1.0.0 LANGUAGES CXX)

# ============================================================================
# C++26 standard enforcement
# ============================================================================
set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================================
# Build type defaults
# ============================================================================
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# ============================================================================
# Compiler flags: performance + SIMD
# ============================================================================
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(
    -O3
    -march=native          # Enable all CPU-native SIMD (AVX2/AVX512)
    -ffast-math            # Allows vectoriser to reorder FP operations
    -funroll-loops
    -fomit-frame-pointer
    -Wall
    -Wextra
    -Wpedantic
  )
elseif(MSVC)
  add_compile_options(
    /O2
    /arch:AVX2
    /fp:fast
    /W4
  )
endif()

# ============================================================================
# Dependencies via FetchContent
# ============================================================================
include(FetchContent)

# --- Eigen (header-only, SIMD-native linear algebra) ---
FetchContent_Declare(
  eigen
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG        3.4.0
  GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(eigen)

# --- nanobind (Python ↔ C++ zero-copy bridge) ---
FetchContent_Declare(
  nanobind
  GIT_REPOSITORY https://github.com/wjakob/nanobind.git
  GIT_TAG        v2.2.0
  GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(nanobind)

# --- Google Test (unit testing) ---
FetchContent_Declare(
  googletest
  GIT_REPOSITORY https://github.com/google/googletest.git
  GIT_TAG        v1.14.0
  GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(googletest)

# ============================================================================
# Python discovery (for nanobind)
# ============================================================================
find_package(Python 3.13 COMPONENTS Interpreter Development.Module REQUIRED)

# ============================================================================
# nanobind extension module
# ============================================================================
nanobind_add_module(
  algothon_cpp
  STABLE_ABI
  src/cpp/src/bindings.cpp
)

target_include_directories(algothon_cpp PRIVATE
  ${CMAKE_SOURCE_DIR}/src/cpp/include
  ${eigen_SOURCE_DIR}
)

target_link_libraries(algothon_cpp PRIVATE
  Eigen3::Eigen
)

# Install the .so/.pyd into src/python so it is importable
install(
  TARGETS algothon_cpp
  LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/src/python
  RUNTIME DESTINATION ${CMAKE_SOURCE_DIR}/src/python
)

# ============================================================================
# C++ unit tests
# ============================================================================
enable_testing()

add_executable(cpp_tests
  tests/cpp/test_portfolio_engine.cpp
)

target_include_directories(cpp_tests PRIVATE
  ${CMAKE_SOURCE_DIR}/src/cpp/include
  ${eigen_SOURCE_DIR}
)

target_link_libraries(cpp_tests PRIVATE
  GTest::gtest_main
  Eigen3::Eigen
)

include(GoogleTest)
gtest_discover_tests(cpp_tests)

# ============================================================================
# Summary
# ============================================================================
message(STATUS "Build type     : ${CMAKE_BUILD_TYPE}")
message(STATUS "CXX standard   : ${CMAKE_CXX_STANDARD}")
message(STATUS "Install prefix : ${CMAKE_INSTALL_PREFIX}")
