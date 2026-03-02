#include "strategy.hpp"
#include <algorithm>

namespace trading_bot {

Strategy::Strategy() {
    limits_["BOND"] = 100;
    limits_["VALBZ"] = 10;
    limits_["VALE"] = 10;
    // ... other limits
}

void Strategy::on_hello(const std::vector<Position>& initial_positions) {
    for (const auto& pos : initial_positions) {
        positions_[pos.symbol] = pos.size;
    }
}

void Strategy::on_fill(const FillUpdate& fill) {
    int delta = (fill.dir == Direction::BUY) ? fill.size : -fill.size;
    positions_[fill.symbol] += delta;
}

std::vector<Order> Strategy::decide(const BookUpdate& book) {
    if (book.symbol == "BOND") {
        return bond_strategy(book);
    }
    return {};
}

int Strategy::next_order_id() {
    return ++order_id_counter_;
}

std::vector<Order> Strategy::bond_strategy(const BookUpdate& book) {
    std::vector<Order> orders;
    std::string symbol = "BOND";
    int pos = positions_[symbol];
    int limit = limits_[symbol];

    // Aggressive Buy
    for (const auto& [price, size] : book.sell) {
        if (price < 1000) {
            int buy_size = std::min(size, limit - pos);
            if (buy_size > 0) {
                orders.push_back({next_order_id(), symbol, Direction::BUY, price, buy_size});
                pos += buy_size;
            }
        }
    }

    // Aggressive Sell
    for (const auto& [price, size] : book.buy) {
        if (price > 1000) {
            int sell_size = std::min(size, limit + pos);
            if (sell_size > 0) {
                orders.push_back({next_order_id(), symbol, Direction::SELL, price, sell_size});
                pos -= sell_size;
            }
        }
    }

    // Passive
    if (pos < limit) {
        orders.push_back({next_order_id(), symbol, Direction::BUY, 999, limit - pos});
    }
    if (pos > -limit) {
        orders.push_back({next_order_id(), symbol, Direction::SELL, 1001, limit + pos});
    }

    return orders;
}

} // namespace trading_bot
