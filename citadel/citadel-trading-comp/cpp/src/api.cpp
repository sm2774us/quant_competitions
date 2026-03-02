#include "api.hpp"
#include <nlohmann/json.hpp>
#include <stdexcept>

using json = nlohmann::json;

namespace citadel {

TradingApi::TradingApi(const std::string& base_url, const std::string& api_key)
    : base_url_(base_url), headers_({{"X-API-Key", api_key}}) {}

CaseStatus TradingApi::get_case() {
    auto resp = cpr::Get(cpr::Url{base_url_ + "/v1/case"}, headers_);
    if (resp.status_code != 200) throw std::runtime_error("Failed to get case");
    return json::parse(resp.text).get<CaseStatus>();
}

std::map<std::string, Security> TradingApi::get_securities() {
    auto resp = cpr::Get(cpr::Url{base_url_ + "/v1/securities"}, headers_);
    if (resp.status_code != 200) throw std::runtime_error("Failed to get securities");
    auto j = json::parse(resp.text);
    std::map<std::string, Security> result;
    for (auto& item : j) {
        Security s = item.get<Security>();
        result[s.ticker] = s;
    }
    return result;
}

OrderBook TradingApi::get_order_book(const std::string& ticker) {
    auto resp = cpr::Get(cpr::Url{base_url_ + "/v1/securities/book"}, headers_, cpr::Parameters{{"ticker", ticker}});
    if (resp.status_code != 200) throw std::runtime_error("Failed to get order book");
    auto j = json::parse(resp.text);
    return {ticker, j["bids"].get<std::vector<OrderBookEntry>>(), j["asks"].get<std::vector<OrderBookEntry>>()};
}

std::vector<News> TradingApi::get_news(int limit) {
    auto resp = cpr::Get(cpr::Url{base_url_ + "/v1/news"}, headers_, cpr::Parameters{{"limit", std::to_string(limit)}});
    if (resp.status_code != 200) throw std::runtime_error("Failed to get news");
    return json::parse(resp.text).get<std::vector<News>>();
}

OrderResponse TradingApi::post_order(const std::string& ticker, const std::string& type, const std::string& action, int quantity, std::optional<double> price) {
    cpr::Parameters params{{"ticker", ticker}, {"type", type}, {"action", action}, {"quantity", std::to_string(quantity)}};
    if (price) params.Add({"price", std::to_string(*price)});
    
    auto resp = cpr::Post(cpr::Url{base_url_ + "/v1/orders"}, headers_, params);
    if (resp.status_code != 200) throw std::runtime_error("Failed to post order: " + resp.text);
    return json::parse(resp.text).get<OrderResponse>();
}

} // namespace citadel
