cmake_minimum_required(VERSION 3.28)
project(algothon_cpp VERSION 1.0.0 LANGUAGES CXX)

# ============================================================================
# C++23 standard
# (Upgrade to C++26 when GCC 15 / Clang 20 stabilise in 2026)
# ============================================================================
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ============================================================================
# Build type
# ============================================================================
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# ============================================================================
# Compiler flags: Release → SIMD + fast-math
# ============================================================================
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(
    -O3
    -march=native
    -ffast-math
    -fvisibility=hidden   # required by nanobind ABI
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
# (When invoked via Bazel's cmake() rule, these run inside the hermetic
#  sandbox.  When invoked standalone, they download from GitHub.)
# ============================================================================
include(FetchContent)

# --- Eigen ---
FetchContent_Declare(
  eigen
  GIT_REPOSITORY https://gitlab.com/libeigen/eigen.git
  GIT_TAG        3.4.0
  GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(eigen)

# --- nanobind ---
FetchContent_Declare(
  nanobind
  GIT_REPOSITORY https://github.com/wjakob/nanobind.git
  GIT_TAG        v2.2.0
  GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(nanobind)

# --- Google Test (only when BUILD_TESTING is ON — disabled via Bazel cmake()) ---
if(BUILD_TESTING)
  FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
    GIT_SHALLOW    TRUE
  )
  FetchContent_MakeAvailable(googletest)
endif()

# ============================================================================
# Python discovery
# ============================================================================
find_package(Python 3.13 COMPONENTS Interpreter Development.Module REQUIRED)

# ============================================================================
# nanobind extension module: algothon_cpp
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

# ============================================================================
# Install — DELTA from original:
#
#   BEFORE (broke rules_foreign_cc):
#     LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/src/python
#
#   AFTER (rules_foreign_cc compatible):
#     LIBRARY DESTINATION lib
#     RUNTIME DESTINATION lib
#
# rules_foreign_cc's cmake() rule sets CMAKE_INSTALL_PREFIX to a
# Bazel-managed staging directory.  It then looks for declared
# out_shared_libs inside ${INSTALLDIR}/lib/.
#
# For standalone cmake builds, the install step now places the .so in
# <build_dir>/install/lib/ instead.  run.sh copies it to src/python/.
# ============================================================================
include(GNUInstallDirs)

install(
  TARGETS algothon_cpp
  LIBRARY DESTINATION lib      # → ${CMAKE_INSTALL_PREFIX}/lib/algothon_cpp.so
  RUNTIME DESTINATION lib      # Windows: .pyd also goes to lib/
)

# ============================================================================
# C++ unit tests (only when invoked standalone — Bazel uses cc_test instead)
# ============================================================================
if(BUILD_TESTING)
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
endif()

# ============================================================================
# Summary
# ============================================================================
message(STATUS "Build type     : ${CMAKE_BUILD_TYPE}")
message(STATUS "CXX standard   : ${CMAKE_CXX_STANDARD}")
message(STATUS "Install prefix : ${CMAKE_INSTALL_PREFIX}")
message(STATUS "BUILD_TESTING  : ${BUILD_TESTING}")
