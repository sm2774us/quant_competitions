#pragma once
#include <string>
#include <vector>
#include <variant>
#include <nlohmann/json.hpp>

namespace trading_bot {

enum class Direction { BUY, SELL };

struct Order {
    int order_id;
    std::string symbol;
    Direction dir;
    int price;
    int size;
};

struct BookUpdate {
    std::string symbol;
    std::vector<std::pair<int, int>> buy;
    std::vector<std::pair<int, int>> sell;
};

struct FillUpdate {
    int order_id;
    std::string symbol;
    Direction dir;
    int price;
    int size;
};

struct Position {
    std::string symbol;
    int size;
};

} // namespace trading_bot
