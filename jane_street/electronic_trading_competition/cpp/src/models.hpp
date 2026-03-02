#pragma once
#include <string>
#include <vector>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

namespace trading_bot {

struct Order {
    std::string type;
    int order_id;
    std::string symbol;
    std::string dir;
    int price;
    int size;

    json to_json() const {
        json j = {{"type", type}, {"order_id", order_id}};
        if (!symbol.empty()) j["symbol"] = symbol;
        if (!dir.empty()) j["dir"] = dir;
        if (price != 0) j["price"] = price;
        if (size != 0) j["size"] = size;
        return j;
    }
};

struct BookLevel {
    int price;
    int size;
};

struct BookMessage {
    std::string symbol;
    std::vector<BookLevel> buy;
    std::vector<BookLevel> sell;

    static BookMessage from_json(const json& j) {
        BookMessage bm;
        bm.symbol = j["symbol"];
        for (auto& level : j["buy"]) bm.buy.push_back({level[0], level[1]});
        for (auto& level : j["sell"]) bm.sell.push_back({level[0], level[1]});
        return bm;
    }
};

} // namespace trading_bot
