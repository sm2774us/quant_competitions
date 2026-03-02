#pragma once
#include <vector>
#include <string>
#include <memory>
#include "api.hpp"

namespace citadel {

class Strategy {
public:
    virtual ~Strategy() = default;
    virtual void run() = 0;
};

class ExchangeArbitrage : public Strategy {
public:
    ExchangeArbitrage(std::shared_ptr<TradingApi> api);
    void run() override;
    void execute(const std::string& mticker, const std::string& aticker);

private:
    std::shared_ptr<TradingApi> api_;
};

class IndexArbitrage : public Strategy {
public:
    IndexArbitrage(std::shared_ptr<TradingApi> api);
    void run() override;

private:
    std::shared_ptr<TradingApi> api_;
    std::vector<std::string> tickers_ = {"WMT", "MMM", "CAT"};
};

class ShockHandler : public Strategy {
public:
    ShockHandler(std::shared_ptr<TradingApi> api);
    void run() override;
    void run_with_tick(int current_tick);

private:
    std::shared_ptr<TradingApi> api_;
};

} // namespace citadel
