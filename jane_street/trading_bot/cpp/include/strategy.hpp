#pragma once
#include "models.hpp"
#include <map>
#include <vector>

namespace trading_bot {

class Strategy {
public:
    Strategy();
    
    void on_hello(const std::vector<Position>& initial_positions);
    void on_fill(const FillUpdate& fill);
    std::vector<Order> decide(const BookUpdate& book);

private:
    int next_order_id();
    std::vector<Order> bond_strategy(const BookUpdate& book);

    std::map<std::string, int> positions_;
    int order_id_counter_ = 0;
    std::map<std::string, int> limits_;
};

} // namespace trading_bot
