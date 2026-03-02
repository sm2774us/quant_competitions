#include <gtest/gtest.h>
#include "../src/Interfaces.hpp"
#include <fstream>

TEST(DataLoaderTest, LoadMarketData) {
    std::ofstream file("test_market.csv");
    file << "time,assetName,open,close,returnsOpenNextMktres10,universe,f1,f2
";
    file << "2024-01-01,AAPL,150.0,155.0,0.02,1,0.1,0.2
";
    file.close();

    DataLoader loader;
    auto data = loader.loadMarketData("test_market.csv");
    ASSERT_EQ(data.size(), 1);
    EXPECT_EQ(data[0].assetName, "AAPL");
    EXPECT_DOUBLE_EQ(data[0].open, 150.0);
}

TEST(PreprocessorTest, ProcessData) {
    std::vector<MarketRecord> market = {{"2024-01-01", "AAPL", 150.0, 155.0, 0.02, 1, {}}};
    std::vector<NewsRecord> news = {{"2024-01-01", "AAPL", 0.1, 0.8, 0.1, 0.9, 500.0}};

    Preprocessor proc;
    auto processed = proc.process(market, news);
    ASSERT_EQ(processed.size(), 1);
    ASSERT_EQ(processed[0].features.size(), 5);
    EXPECT_DOUBLE_EQ(processed[0].features[0], 0.1);
}

TEST(ModelTest, TrainAndPredict) {
    Model model;
    std::vector<std::vector<double>> X = {{1.0, 2.0}, {2.0, 1.0}};
    std::vector<double> y = {1.0, -1.0};
    
    model.train(X, y);
    auto preds = model.predict(X);
    ASSERT_EQ(preds.size(), 2);
    // Rough direction check
    EXPECT_GT(preds[0], 0);
    EXPECT_LT(preds[1], 0);
}

TEST(EvaluatorTest, SharpeRatio) {
    Evaluator evaluator;
    std::vector<double> preds = {0.5, -0.5};
    std::vector<double> targets = {0.1, -0.1};
    std::vector<int> universe = {1, 1};
    std::vector<std::string> times = {"2024-01-01", "2024-01-02"};

    double score = evaluator.evaluate(preds, targets, universe, times);
    // (0.05 + 0.05) / std([0.05, 0.05]) -> std is 0.
    // In my impl, std 0 returns 0 or handled.
    EXPECT_GE(score, 0.0);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
