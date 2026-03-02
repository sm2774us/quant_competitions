#include <gtest/gtest.h>
#include "market_prediction/models.hpp"

using namespace market_prediction;

TEST(ModelTest, LayerForward) {
    Linear layer(10, 5);
    // input is (batch_size, in_features)
    Eigen::MatrixXd input = Eigen::MatrixXd::Random(8, 10);
    Eigen::MatrixXd output = layer.forward(input);
    // result is (batch_size, out_features)
    EXPECT_EQ(output.rows(), 8);
    EXPECT_EQ(output.cols(), 5);
}

TEST(ModelTest, ModelPredict) {
    MarketModel model(136);
    Eigen::VectorXd input = Eigen::VectorXd::Random(136);
    Eigen::VectorXd output = model.predict(input);
    EXPECT_EQ(output.size(), 1);
    EXPECT_GE(output(0), 0.0);
    EXPECT_LE(output(0), 1.0);
}

TEST(ModelTest, BatchPredict) {
    MarketModel model(136);
    Eigen::MatrixXd inputs = Eigen::MatrixXd::Random(4, 136);
    Eigen::MatrixXd outputs = model.batch_predict(inputs);
    EXPECT_EQ(outputs.rows(), 4);
    EXPECT_EQ(outputs.cols(), 1);
}
