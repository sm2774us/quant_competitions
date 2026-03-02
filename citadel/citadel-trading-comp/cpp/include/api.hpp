#pragma once
#include <string>
#include <vector>
#include <map>
#include "models.hpp"
#include <cpr/cpr.h>

namespace citadel {

class TradingApi {
public:
    TradingApi(const std::string& base_url, const std::string& api_key);
    virtual ~TradingApi() = default;

    virtual CaseStatus get_case();
    virtual std::map<std::string, Security> get_securities();
    virtual OrderBook get_order_book(const std::string& ticker);
    virtual std::vector<News> get_news(int limit = 10);
    virtual OrderResponse post_order(const std::string& ticker, const std::string& type, const std::string& action, int quantity, std::optional<double> price = std::nullopt);

private:
    std::string base_url_;
    cpr::Header headers_;
};

} // namespace citadel
