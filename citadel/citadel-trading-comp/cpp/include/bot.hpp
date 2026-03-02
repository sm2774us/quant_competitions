#pragma once
#include <memory>
#include "api.hpp"
#include "strategies.hpp"

namespace citadel {

class TradingBot {
public:
    TradingBot(std::shared_ptr<TradingApi> api);
    void start(double interval_seconds = 0.1);
    bool run_once();

private:
    std::shared_ptr<TradingApi> api_;
    std::unique_ptr<ExchangeArbitrage> exchange_arb_;
    std::unique_ptr<IndexArbitrage> index_arb_;
    std::unique_ptr<ShockHandler> shock_handler_;
    int last_tick_ = -1;
};

} // namespace citadel
