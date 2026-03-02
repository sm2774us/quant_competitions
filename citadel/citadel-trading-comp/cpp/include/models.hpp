#pragma once
#include <string>
#include <vector>
#include <optional>
#include <nlohmann/json.hpp>

namespace citadel {

struct Security {
    std::string ticker;
    int position;
    double vwap;
    double nlv;
    double last;
    double bid;
    int bid_size;
    double ask;
    int ask_size;
    double unrealized;
    double realized;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Security, ticker, position, vwap, nlv, last, bid, bid_size, ask, ask_size, unrealized, realized)

struct OrderBookEntry {
    double price;
    int quantity;
    int quantity_filled;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(OrderBookEntry, price, quantity, quantity_filled)

struct OrderBook {
    std::string ticker;
    std::vector<OrderBookEntry> bids;
    std::vector<OrderBookEntry> asks;
};

struct News {
    int tick;
    std::string ticker;
    std::string headline;
    std::string body;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(News, tick, ticker, headline, body)

struct CaseStatus {
    int tick;
    std::string status;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(CaseStatus, tick, status)

struct Limit {
    std::string ticker;
    int gross_limit;
    int net_limit;
    int gross;
    int net;
};

NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(Limit, ticker, gross_limit, net_limit, gross, net)

struct OrderResponse {
    int order_id;
    std::string status;
    std::string ticker;
    std::string type;
    std::string action;
    int quantity;
    std::optional<double> price;
    std::optional<double> vwap;
};

inline void from_json(const nlohmann::json& j, OrderResponse& r) {
    j.at("order_id").get_to(r.order_id);
    j.at("status").get_to(r.status);
    j.at("ticker").get_to(r.ticker);
    j.at("type").get_to(r.type);
    j.at("action").get_to(r.action);
    j.at("quantity").get_to(r.quantity);
    if (j.contains("price") && !j.at("price").is_null()) r.price = j.at("price").get<double>();
    if (j.contains("vwap") && !j.at("vwap").is_null()) r.vwap = j.at("vwap").get<double>();
}

} // namespace citadel
