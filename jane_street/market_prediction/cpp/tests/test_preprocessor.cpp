#include <gtest/gtest.h>
#include "market_prediction/preprocessor.hpp"

using namespace market_prediction;

TEST(PreprocessorTest, Init) {
    MarketPreprocessor prep(130, 5);
}

TEST(PreprocessorTest, Transform) {
    MarketPreprocessor prep(130, 5);
    Eigen::VectorXd x = Eigen::VectorXd::Zero(130);
    x(0) = 1.0;
    
    Eigen::VectorXd res = prep.transform(x);
    EXPECT_EQ(res.size(), 136); // 130 + 6 interactions
}

TEST(PreprocessorTest, NaNs) {
    MarketPreprocessor prep(130, 5);
    Eigen::VectorXd x = Eigen::VectorXd::Zero(130);
    x(0) = -1.0;
    x(1) = std::nan("");
    
    // Default medians are 0
    Eigen::VectorXd res = prep.transform(x);
    EXPECT_EQ(res.size(), 136);
    EXPECT_DOUBLE_EQ(res(0), -1.0);
    // res(1) = (imputed_val - mean) / scale. If all 0, res(1) = (0-0)/1 = 0
    EXPECT_NEAR(res(1), 0.0, 1e-7);
}
