#pragma once
#include <vector>
#include <string>
#include <memory>
#include "models.h"

namespace etc {

class Strategy {
public:
    virtual ~Strategy() = default;
    virtual std::vector<Action> execute(const MarketState& state) = 0;
};

class BondStrategy : public Strategy {
public:
    std::vector<Action> execute(const MarketState& state) override;
};

class AdrStrategy : public Strategy {
public:
    std::vector<Action> execute(const MarketState& state) override;
};

class EtfStrategy : public Strategy {
public:
    std::vector<Action> execute(const MarketState& state) override;
};

} // namespace etc
