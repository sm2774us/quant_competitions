load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

cmake(
    name = "trading_bot_cmake",
    lib_source = ":all_srcs",
    out_binaries = ["trading_bot", "test_trading_bot"],
)

filegroup(
    name = "all_srcs",
    srcs = glob(["src/**", "tests/**", "CMakeLists.txt"]),
)
