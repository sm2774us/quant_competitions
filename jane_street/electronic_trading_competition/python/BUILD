load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_library(
    name = "trading_bot_lib",
    srcs = glob(["src/trading_bot/*.py"]),
    imports = ["src"],
    deps = [
        # In a real bazel setup, we would use pip_parse to manage dependencies
    ],
)

py_binary(
    name = "trading_bot",
    srcs = ["src/trading_bot/cli.py"],
    main = "src/trading_bot/cli.py",
    deps = [":trading_bot_lib"],
)

py_test(
    name = "test_strategies",
    srcs = ["tests/test_strategies.py"],
    deps = [":trading_bot_lib"],
)
