#include "strategies.hpp"
#include <numeric>

namespace trading_bot {

std::vector<Order> BondStrategy::update_book(const BookMessage& book, int& order_id_counter) {
    std::vector<Order> orders;

    for (const auto& level : book.sell) {
        if (level.price < fair_price_) {
            int buy_size = std::min(level.size, limit_ - position_);
            if (buy_size > 0) {
                orders.push_back({"add", order_id_counter++, symbol_, "BUY", level.price, buy_size});
            }
        }
    }

    for (const auto& level : book.buy) {
        if (level.price > fair_price_) {
            int sell_size = std::min(level.size, position_ + limit_);
            if (sell_size > 0) {
                orders.push_back({"add", order_id_counter++, symbol_, "SELL", level.price, sell_size});
            }
        }
    }

    if (position_ < limit_) orders.push_back({"add", order_id_counter++, symbol_, "BUY", 999, 1});
    if (position_ > -limit_) orders.push_back({"add", order_id_counter++, symbol_, "SELL", 1001, 1});

    return orders;
}

std::vector<Order> MACDStrategy::update_price(int price, int& order_id_counter) {
    prices_.push_back(price);
    if (prices_.size() > 20) prices_.pop_front();
    if (prices_.size() < 20) return {};

    if (!ema12_.has_value()) {
        ema12_ = std::accumulate(prices_.end() - 12, prices_.end(), 0.0) / 12.0;
        ema20_ = std::accumulate(prices_.begin(), prices_.end(), 0.0) / 20.0;
    } else {
        ema12_ = (price - *ema12_) * (2.0 / 13.0) + *ema12_;
        ema20_ = (price - *ema20_) * (2.0 / 21.0) + *ema20_;
    }

    double macd = *ema12_ - *ema20_;
    std::vector<Order> orders;
    if (macd > 0.5 && position_ < limit_) {
        orders.push_back({"add", order_id_counter++, symbol_, "BUY", price + 1, 1});
    } else if (macd < -0.5 && position_ > -limit_) {
        orders.push_back({"add", order_id_counter++, symbol_, "SELL", price - 1, 1});
    }

    return orders;
}

} // namespace trading_bot
