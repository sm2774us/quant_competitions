#include <gtest/gtest.h>
#include "strategies.hpp"

using namespace trading_bot;

TEST(BondStrategyTest, BuyAtLowPrice) {
    BondStrategy strat;
    BookMessage book;
    book.symbol = "BOND";
    book.sell = {{998, 10}};
    int counter = 1;
    auto orders = strat.update_book(book, counter);
    bool found_buy = false;
    for (const auto& o : orders) {
        if (o.dir == "BUY" && o.price == 998) found_buy = true;
    }
    EXPECT_TRUE(found_buy);
}

TEST(BondStrategyTest, SellAtHighPrice) {
    BondStrategy strat;
    BookMessage book;
    book.symbol = "BOND";
    book.buy = {{1002, 10}};
    int counter = 1;
    auto orders = strat.update_book(book, counter);
    bool found_sell = false;
    for (const auto& o : orders) {
        if (o.dir == "SELL" && o.price == 1002) found_sell = true;
    }
    EXPECT_TRUE(found_sell);
}

TEST(MACDStrategyTest, BuyOnMomentum) {
    MACDStrategy strat("AAPL");
    int counter = 1;
    std::vector<Order> orders;
    for (int i = 100; i < 125; ++i) {
        orders = strat.update_price(i, counter);
    }
    ASSERT_FALSE(orders.empty());
    EXPECT_EQ(orders[0].dir, "BUY");
}
