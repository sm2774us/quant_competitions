#include "bot.hpp"
#include <iostream>
#include <chrono>
#include <thread>

namespace citadel {

TradingBot::TradingBot(std::shared_ptr<TradingApi> api) : api_(api) {
    exchange_arb_ = std::make_unique<ExchangeArbitrage>(api);
    index_arb_ = std::make_unique<IndexArbitrage>(api);
    shock_handler_ = std::make_unique<ShockHandler>(api);
}

bool TradingBot::run_once() {
    try {
        auto case_status = api_->get_case();
        if (case_status.status == "STOPPED") return false;

        if (case_status.tick != last_tick_) {
            last_tick_ = case_status.tick;
            std::cout << "Tick: " << last_tick_ << std::endl;

            shock_handler_->run_with_tick(last_tick_);
            exchange_arb_->run();
            index_arb_->run();
        }
    } catch (const std::exception& e) {
        std::cerr << "Bot error: " << e.what() << std::endl;
    }
    return true;
}

void TradingBot::start(double interval_seconds) {
    std::cout << "Starting C++ trading bot..." << std::endl;
    while (run_once()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(static_cast<int>(interval_seconds * 1000)));
    }
}

} // namespace citadel
