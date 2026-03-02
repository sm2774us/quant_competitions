#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "strategy.hpp"
#include "models.hpp"

using namespace trading_bot;

TEST(StrategyTest, InitialPosition) {
    Strategy strategy;
    strategy.on_hello({{"BOND", 10}});
    // We can't directly inspect positions, but we can see the effect on decisions
    // This is a simple test to ensure it doesn't crash
}

TEST(StrategyTest, BondStrategyPassive) {
    Strategy strategy;
    strategy.on_hello({{"BOND", 0}});
    BookUpdate book;
    book.symbol = "BOND";
    
    auto orders = strategy.decide(book);
    
    bool has_buy = false;
    bool has_sell = false;
    for (const auto& o : orders) {
        if (o.price == 999 && o.dir == Direction::BUY) has_buy = true;
        if (o.price == 1001 && o.dir == Direction::SELL) has_sell = true;
    }
    EXPECT_TRUE(has_buy);
    EXPECT_TRUE(has_sell);
}

TEST(StrategyTest, BondStrategyAggressiveBuy) {
    Strategy strategy;
    strategy.on_hello({{"BOND", 0}});
    BookUpdate book;
    book.symbol = "BOND";
    book.sell.push_back({998, 10});
    
    auto orders = strategy.decide(book);
    
    bool found_aggressive = false;
    for (const auto& o : orders) {
        if (o.price == 998 && o.dir == Direction::BUY && o.size == 10) found_aggressive = true;
    }
    EXPECT_TRUE(found_aggressive);
}

TEST(StrategyTest, FillUpdatesPosition) {
    Strategy strategy;
    strategy.on_hello({{"BOND", 0}});
    
    FillUpdate fill{1, "BOND", Direction::BUY, 999, 10};
    strategy.on_fill(fill);
    
    // Check if position was updated by looking at passive order size
    BookUpdate book;
    book.symbol = "BOND";
    auto orders = strategy.decide(book);
    
    for (const auto& o : orders) {
        if (o.price == 999 && o.dir == Direction::BUY) {
            EXPECT_EQ(o.size, 90); // 100 - 10
        }
    }
}
