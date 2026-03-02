#include <gtest/gtest.h>
#include "market_prediction/engine.hpp"

using namespace market_prediction;

TEST(EngineTest, PredictAction) {
    auto model_manager = std::make_shared<ModelManager>(130);
    auto preprocessor = std::make_shared<MarketPreprocessor>(130);
    InferenceEngine engine(model_manager, preprocessor, 0.5);
    
    Eigen::VectorXd features = Eigen::VectorXd::Random(130);
    int action = engine.predict_action(features);
    EXPECT_TRUE(action == 0 || action == 1);
}

TEST(EngineTest, BatchPredict) {
    auto model_manager = std::make_shared<ModelManager>(130);
    auto preprocessor = std::make_shared<MarketPreprocessor>(130);
    InferenceEngine engine(model_manager, preprocessor, 0.5);
    
    Eigen::MatrixXd features_batch = Eigen::MatrixXd::Random(5, 130);
    auto actions = engine.batch_predict(features_batch);
    EXPECT_EQ(actions.size(), 5);
}
