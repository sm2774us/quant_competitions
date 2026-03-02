#include <gtest/gtest.h>
#include "market_prediction/scorer.hpp"

using namespace market_prediction;

TEST(ScorerTest, CalculateUtility) {
    std::vector<Trade> trades = {
        {0, 1.0, 0.1, 1},
        {0, 1.0, 0.2, 1},
        {1, 1.0, -0.1, 1},
        {1, 1.0, 0.3, 1}
    };
    
    // p_0 = 0.3, p_1 = 0.2
    // sum_p = 0.5, sum_p_sq = 0.13
    // t = (0.5 / sqrt(0.13)) * sqrt(250 / 2) = 15.49
    // u = 6 * 0.5 = 3.0
    
    double u = UtilityScorer::calculate_utility(trades);
    EXPECT_NEAR(u, 3.0, 1e-4);
}

TEST(ScorerTest, ZeroUtility) {
    std::vector<Trade> trades = {
        {0, 1.0, 0.1, 0}
    };
    EXPECT_DOUBLE_EQ(UtilityScorer::calculate_utility(trades), 0.0);
}

TEST(ScorerTest, SummaryTable) {
    std::vector<Trade> trades = {
        {0, 1.0, 0.1, 1}
    };
    auto summary = UtilityScorer::summary_table(trades);
    EXPECT_EQ(summary["total_profit"], 0.1);
    EXPECT_EQ(summary["num_trades_executed"], 1.0);
}
