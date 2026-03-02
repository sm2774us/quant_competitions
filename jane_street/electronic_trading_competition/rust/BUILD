load("@rules_rust//rust:defs.bzl", "rust_binary", "rust_test")

rust_binary(
    name = "trading_bot",
    srcs = glob(["src/*.rs"]),
    edition = "2024",
    deps = [
        # External crates would be managed by cargo_build_script or crate_universe
    ],
)

rust_test(
    name = "trading_bot_test",
    srcs = glob(["src/*.rs"]),
    edition = "2024",
)
