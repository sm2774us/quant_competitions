#pragma once
#include <string>
#include <vector>
#include <map>

struct MarketRecord {
    std::string time;
    std::string assetName;
    double open;
    double close;
    double returnsOpenNextMktres10;
    int universe;
    // Additional features
    std::vector<double> features;
};

struct NewsRecord {
    std::string time;
    std::string assetName;
    double sentimentNegative;
    double sentimentNeutral;
    double sentimentPositive;
    double relevance;
    double wordCount;
};

class DataLoader {
public:
    std::vector<MarketRecord> loadMarketData(const std::string& path);
    std::vector<NewsRecord> loadNewsData(const std::string& path);
};

class Preprocessor {
public:
    std::vector<MarketRecord> process(std::vector<MarketRecord>& market, const std::vector<NewsRecord>& news);
};

class Model {
public:
    void train(const std::vector<std::vector<double>>& X, const std::vector<double>& y);
    std::vector<double> predict(const std::vector<std::vector<double>>& X);
private:
    std::vector<double> weights;
    double bias = 0.0;
};

class Evaluator {
public:
    double evaluate(const std::vector<double>& predictions, const std::vector<double>& targets, const std::vector<int>& universe, const std::vector<std::string>& times);
};
