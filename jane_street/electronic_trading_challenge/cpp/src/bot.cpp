#include "etc/bot.h"
#include <iostream>

namespace etc {

TradingBot::TradingBot(std::unique_ptr<ExchangeConnection> conn, const std::string& team)
    : connection(std::move(conn)), team_name(team) {
    strategies.push_back(std::make_unique<BondStrategy>());
    strategies.push_back(std::make_unique<AdrStrategy>());
    strategies.push_back(std::make_unique<EtfStrategy>());
}

void TradingBot::run(const std::string& host, int port) {
    connection->connect(host, port);
    connection->send_hello(team_name);

    while (true) {
        auto msg = connection->read();
        if (!msg) {
            std::cout << "Connection closed by exchange." << std::endl;
            break;
        }

        handle_message(*msg);
        execute_strategies();
    }
}

void TradingBot::handle_message(const nlohmann::json& message) {
    std::string type = message.value("type", "");

    if (type == "book") {
        state.update_book(message["symbol"], message["bids"], message["asks"]);
    } else if (type == "trade") {
        state.add_trade(message["symbol"], message["price"]);
    } else if (type == "fill") {
        int size = message["size"];
        int sign = (message["dir"] == "BUY") ? 1 : -1;
        state.update_position(message["symbol"], sign * size);
        state.pnl += sign * -1 * (int)message["price"] * size;
    } else if (type == "hello") {
        for (const auto& entry : message["symbols"]) {
            state.positions[entry["symbol"]] = entry["position"];
        }
    }
}

void TradingBot::execute_strategies() {
    for (const auto& strategy : strategies) {
        auto actions = strategy->execute(state);
        for (const auto& action : actions) {
            int order_id = get_next_order_id();
            if (action.type == "add") {
                connection->place_order(order_id, action.symbol, action.dir, action.price, action.size);
            } else if (action.type == "convert") {
                connection->convert(order_id, action.symbol, action.dir, action.size);
            }
        }
    }
}

int TradingBot::get_next_order_id() {
    return ++order_id_counter;
}

} // namespace etc
