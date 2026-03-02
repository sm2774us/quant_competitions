#pragma once
#include <string>
#include <vector>
#include <deque>
#include <optional>
#include "models.hpp"

namespace trading_bot {

class TradingStrategy {
public:
    TradingStrategy(const std::string& symbol) : symbol_(symbol) {}
    virtual ~TradingStrategy() = default;

    virtual std::vector<Order> update_book(const BookMessage& book, int& order_id_counter) = 0;
    virtual void update_fill(const std::string& dir, int size) {
        if (dir == "BUY") position_ += size;
        else position_ -= size;
    }

protected:
    std::string symbol_;
    int position_ = 0;
};

class BondStrategy : public TradingStrategy {
public:
    BondStrategy(const std::string& symbol = "BOND") : TradingStrategy(symbol) {}
    std::vector<Order> update_book(const BookMessage& book, int& order_id_counter) override;

private:
    const int fair_price_ = 1000;
    const int limit_ = 100;
};

class MACDStrategy : public TradingStrategy {
public:
    MACDStrategy(const std::string& symbol) : TradingStrategy(symbol) {}
    std::vector<Order> update_price(int price, int& order_id_counter);
    std::vector<Order> update_book(const BookMessage& book, int& order_id_counter) override { return {}; }

private:
    std::deque<int> prices_;
    std::optional<double> ema12_;
    std::optional<double> ema20_;
    const int limit_ = 50;
};

} // namespace trading_bot
