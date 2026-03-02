#include <iostream>
#include <vector>
#include <string>
#include "CLI11.hpp"
#include "Interfaces.hpp"

int main(int argc, char** argv) {
    CLI::App app{"Two Sigma Stock News Challenge - C++ Solution"};

    std::string marketPath;
    std::string newsPath;
    app.add_option("--market", marketPath, "Path to market data (CSV)")->required();
    app.add_option("--news", newsPath, "Path to news data (CSV)")->required();

    CLI11_PARSE(app, argc, argv);

    std::cout << "Loading data..." << std::endl;
    DataLoader loader;
    auto marketData = loader.loadMarketData(marketPath);
    auto newsData = loader.loadNewsData(newsPath);

    std::cout << "Preprocessing..." << std::endl;
    Preprocessor preprocessor;
    auto processedMarket = preprocessor.process(marketData, newsData);

    // Split 80/20
    size_t split_idx = static_cast<size_t>(processedMarket.size() * 0.8);
    
    std::vector<std::vector<double>> X_train, X_test;
    std::vector<double> y_train, y_test;
    std::vector<int> u_test;
    std::vector<std::string> t_test;

    for (size_t i = 0; i < split_idx; ++i) {
        X_train.push_back(processedMarket[i].features);
        y_train.push_back(processedMarket[i].returnsOpenNextMktres10);
    }
    for (size_t i = split_idx; i < processedMarket.size(); ++i) {
        X_test.push_back(processedMarket[i].features);
        y_test.push_back(processedMarket[i].returnsOpenNextMktres10);
        u_test.push_back(processedMarket[i].universe);
        t_test.push_back(processedMarket[i].time);
    }

    std::cout << "Training..." << std::endl;
    Model model;
    model.train(X_train, y_train);

    std::cout << "Predicting..." << std::endl;
    auto predictions = model.predict(X_test);

    std::cout << "Evaluating..." << std::endl;
    Evaluator evaluator;
    double score = evaluator.evaluate(predictions, y_test, u_test, t_test);

    std::cout << "Final Score (Sharpe Ratio): " << score << std::endl;

    return 0;
}
