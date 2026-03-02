#include <gtest/gtest.h>
#include "model.h"
#include "environment.h"
#include "data_generator.h"
#include <filesystem>

using namespace two_sigma;

TEST(FinancialModelTest, TrainAndPredict) {
    FinancialModel model(0.1);
    Eigen::MatrixXd X(10, 5);
    X.setRandom();
    Eigen::VectorXd y(10);
    y.setRandom();
    
    model.train(X, y);
    Eigen::VectorXd predictions = model.predict(X);
    EXPECT_EQ(predictions.size(), 10);
}

TEST(DataGeneratorTest, GenerateFile) {
    std::string path = "test_data.csv";
    DataGenerator gen(100, 10, 5);
    gen.generate(path);
    EXPECT_TRUE(std::filesystem::exists(path));
    std::filesystem::remove(path);
}

TEST(EnvironmentTest, Lifecycle) {
    std::string path = "env_test.csv";
    DataGenerator gen(200, 10, 5);
    gen.generate(path);
    
    Environment env(path);
    auto obs = env.reset();
    EXPECT_GT(obs.train_features.rows(), 0);
    EXPECT_GT(obs.test_features.rows(), 0);
    
    Eigen::VectorXd preds(obs.test_features.rows());
    preds.setConstant(0.01);
    
    auto [next_obs, reward] = env.step(preds);
    EXPECT_FALSE(env.is_done());
    
    std::filesystem::remove(path);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
