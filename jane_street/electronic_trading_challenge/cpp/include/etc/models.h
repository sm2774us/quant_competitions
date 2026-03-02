#pragma once
#include <string>
#include <vector>
#include <map>
#include <optional>
#include <nlohmann/json.hpp>

namespace etc {

enum class Side { BUY, SELL };

struct BookEntry {
    int price;
    int size;
};

struct OrderBook {
    std::string symbol;
    std::vector<BookEntry> bids;
    std::vector<BookEntry> asks;

    std::optional<double> mid_price() const;
    std::optional<int> best_bid() const;
    std::optional<int> best_ask() const;
};

class MarketState {
public:
    std::map<std::string, OrderBook> books;
    std::map<std::string, int> positions;
    std::map<std::string, std::vector<int>> last_trades;
    int pnl = 0;

    void update_book(const std::string& symbol, const nlohmann::json& bids_json, const nlohmann::json& asks_json);
    void add_trade(const std::string& symbol, int price);
    void update_position(const std::string& symbol, int change);
};

struct Action {
    std::string type; // "add", "convert", "cancel"
    std::string symbol;
    std::string dir; // "BUY", "SELL"
    int price = 0;
    int size = 0;
};

} // namespace etc
