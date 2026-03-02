#include <print>
#include <CLI/CLI.hpp>
#include "api.hpp"
#include "bot.hpp"

int main(int argc, char** argv) {
    CLI::App app{"Citadel Trading Bot - C++ Solution (Modernized C++26)"};

    auto url = std::string{"http://localhost:9998"};
    auto key = std::string{};
    auto interval = 0.1;

    app.add_option("--url", url, "API base URL")->default_val(url);
    app.add_option("--key", key, "API Key")->required();
    app.add_option("--interval", interval, "Polling interval in seconds")->default_val(interval);

    CLI11_PARSE(app, argc, argv);

    auto api = std::make_shared<citadel::TradingApi>(url, key);
    auto bot = citadel::TradingBot(api);

    try {
        std::println("Starting bot on URL: {} with interval: {}s", url, interval);
        bot.start(interval);
    } catch (const std::exception& e) {
        std::println(stderr, "Fatal error: {}", e.what());
        return 1;
    }

    return 0;
}
