#include "bot.hpp"
#include <iostream>

namespace trading_bot {

Bot::Bot(const std::string& host, int port, const std::string& team)
    : exchange_(host, port), team_(team) {}

void Bot::run() {
    exchange_.connect();
    exchange_.send({{"type", "hello"}, {"team", team_}});

    while (true) {
        json message = exchange_.receive();
        if (message.is_null()) break;
        handle_message(message);
    }
}

void Bot::handle_message(const json& message) {
    std::string type = message["type"];
    
    if (type == "hello") {
        std::vector<Position> initial;
        for (const auto& s : message["symbols"]) {
            initial.push_back({s["symbol"], s["position"]});
        }
        strategy_.on_hello(initial);
    } else if (type == "book") {
        BookUpdate book;
        book.symbol = message["symbol"];
        for (const auto& b : message["buy"]) book.buy.push_back({b[0], b[1]});
        for (const auto& s : message["sell"]) book.sell.push_back({s[0], s[1]});
        
        auto orders = strategy_.decide(book);
        for (const auto& order : orders) {
            place_order(order);
        }
    } else if (type == "fill") {
        FillUpdate fill;
        fill.order_id = message["order_id"];
        fill.symbol = message["symbol"];
        fill.dir = (message["dir"] == "BUY") ? Direction::BUY : Direction::SELL;
        fill.price = message["price"];
        fill.size = message["size"];
        strategy_.on_fill(fill);
    }
}

void Bot::place_order(const Order& order) {
    exchange_.send({
        {"type", "add"},
        {"order_id", order.order_id},
        {"symbol", order.symbol},
        {"dir", (order.dir == Direction::BUY) ? "BUY" : "SELL"},
        {"price", order.price},
        {"size", order.size}
    });
}

} // namespace trading_bot
