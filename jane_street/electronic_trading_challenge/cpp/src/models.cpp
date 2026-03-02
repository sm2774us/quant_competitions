#include "etc/models.h"
#include <numeric>

namespace etc {

std::optional<double> OrderBook::mid_price() const {
    if (bids.empty() || asks.empty()) return std::nullopt;
    return (bids[0].price + asks[0].price) / 2.0;
}

std::optional<int> OrderBook::best_bid() const {
    if (bids.empty()) return std::nullopt;
    return bids[0].price;
}

std::optional<int> OrderBook::best_ask() const {
    if (asks.empty()) return std::nullopt;
    return asks[0].price;
}

void MarketState::update_book(const std::string& symbol, const nlohmann::json& bids_json, const nlohmann::json& asks_json) {
    auto& book = books[symbol];
    book.symbol = symbol;
    book.bids.clear();
    for (const auto& entry : bids_json) {
        book.bids.push_back({entry[0], entry[1]});
    }
    book.asks.clear();
    for (const auto& entry : asks_json) {
        book.asks.push_back({entry[0], entry[1]});
    }
}

void MarketState::add_trade(const std::string& symbol, int price) {
    auto& trades = last_trades[symbol];
    trades.push_back(price);
    if (trades.size() > 100) {
        trades.erase(trades.begin());
    }
}

void MarketState::update_position(const std::string& symbol, int change) {
    positions[symbol] += change;
}

} // namespace etc
