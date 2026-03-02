# Root BUILD file

# Python target
sh_binary(
    name = "python-bot",
    srcs = ["python/src/etc/main.py"],
    # In a full Bazel setup, we'd use py_binary with a toolchain.
    # For this challenge, we assume poetry is used as described in the READMEs.
)

# C++ target
# Native cc_binary could be used here if we managed deps with Bazel.
# Since we use CMake for the C++ solution, we'll refer to the cpp/ README.

# Rust target
# rules_rust could manage this if we mirrored Cargo.toml here.
