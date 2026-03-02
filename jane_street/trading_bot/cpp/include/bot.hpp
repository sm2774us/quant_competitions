#pragma once
#include "exchange.hpp"
#include "strategy.hpp"
#include <string>

namespace trading_bot {

class Bot {
public:
    Bot(const std::string& host, int port, const std::string& team);
    
    void run();

private:
    void handle_message(const json& message);
    void place_order(const Order& order);

    Exchange exchange_;
    Strategy strategy_;
    std::string team_;
};

} // namespace trading_bot
