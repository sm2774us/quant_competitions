#!/bin/bash
# discover_and_test.sh <language>
# language: python, cpp, rust

LANG=$1
set -e

# Base directory (monorepo root)
ROOT_DIR=$(pwd)
EXIT_CODE=0

case $LANG in
  python)
    echo "--- Discovering Python projects ---"
    # Set executable bit for the build script
    chmod +x "$ROOT_DIR/run_python_build.sh"
    # Find all directories containing pyproject.toml
    find . -name "pyproject.toml" -not -path "*/.venv/*" | while read -r pyproj; do
      proj_dir=$(dirname "$pyproj")
      echo "::group::Testing Python project in $proj_dir"
      # Change to project dir, run build, return to root
      cd "$ROOT_DIR/$proj_dir"
      bash "$ROOT_DIR/run_python_build.sh" || { echo "FAILURE in $proj_dir"; exit 1; }
      cd "$ROOT_DIR"
      echo "::endgroup::"
    done
    ;;
  cpp)
    echo "--- Discovering C++ projects ---"
    # Set executable bit for the build script
    chmod +x "$ROOT_DIR/run_cpp_build.sh"
    # Find all directories containing CMakeLists.txt
    find . -name "CMakeLists.txt" -not -path "*/build/*" | while read -r cmakelist; do
      proj_dir=$(dirname "$cmakelist")
      echo "::group::Testing C++ project in $proj_dir"
      cd "$ROOT_DIR/$proj_dir"
      bash "$ROOT_DIR/run_cpp_build.sh" || { echo "FAILURE in $proj_dir"; exit 1; }
      cd "$ROOT_DIR"
      echo "::endgroup::"
    done
    ;;
  rust)
    echo "--- Discovering Rust projects ---"
    # Set executable bit for the build script
    chmod +x "$ROOT_DIR/run_rust_build.sh"
    # Find all directories containing Cargo.toml
    find . -name "Cargo.toml" -not -path "*/target/*" | while read -r cargo; do
      proj_dir=$(dirname "$cargo")
      echo "::group::Testing Rust project in $proj_dir"
      cd "$ROOT_DIR/$proj_dir"
      bash "$ROOT_DIR/run_rust_build.sh" || { echo "FAILURE in $proj_dir"; exit 1; }
      cd "$ROOT_DIR"
      echo "::endgroup::"
    done
    ;;
  *)
    echo "Unknown language: $LANG"
    exit 1
    ;;
esac
