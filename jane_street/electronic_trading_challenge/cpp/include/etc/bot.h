#pragma once
#include <vector>
#include <memory>
#include "models.h"
#include "exchange.h"
#include "strategies.h"

namespace etc {

class TradingBot {
public:
    TradingBot(std::unique_ptr<ExchangeConnection> connection, const std::string& team_name);
    void run(const std::string& host, int port);

private:
    void handle_message(const nlohmann::json& message);
    void execute_strategies();
    int get_next_order_id();

    std::unique_ptr<ExchangeConnection> connection;
    std::string team_name;
    MarketState state;
    std::vector<std::unique_ptr<Strategy>> strategies;
    int order_id_counter = 0;
};

} // namespace etc
