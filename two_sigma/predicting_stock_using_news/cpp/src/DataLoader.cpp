#include "Interfaces.hpp"
#include <fstream>
#include <sstream>

std::vector<MarketRecord> DataLoader::loadMarketData(const std::string& path) {
    std::vector<MarketRecord> data;
    std::ifstream file(path);
    if (!file.is_open()) return data;

    std::string line;
    std::getline(file, line); // header

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        MarketRecord record;
        
        std::getline(ss, record.time, ',');
        std::getline(ss, record.assetName, ',');
        
        std::getline(ss, cell, ','); record.open = std::stod(cell);
        std::getline(ss, cell, ','); record.close = std::stod(cell);
        std::getline(ss, cell, ','); record.returnsOpenNextMktres10 = std::stod(cell);
        std::getline(ss, cell, ','); record.universe = std::stoi(cell);
        
        // Let's assume some columns for features
        while (std::getline(ss, cell, ',')) {
            if (!cell.empty()) record.features.push_back(std::stod(cell));
        }
        
        data.push_back(record);
    }
    return data;
}

std::vector<NewsRecord> DataLoader::loadNewsData(const std::string& path) {
    std::vector<NewsRecord> data;
    std::ifstream file(path);
    if (!file.is_open()) return data;

    std::string line;
    std::getline(file, line); // header

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::string cell;
        NewsRecord record;
        
        std::getline(ss, record.time, ',');
        std::getline(ss, record.assetName, ',');
        
        std::getline(ss, cell, ','); record.sentimentNegative = std::stod(cell);
        std::getline(ss, cell, ','); record.sentimentNeutral = std::stod(cell);
        std::getline(ss, cell, ','); record.sentimentPositive = std::stod(cell);
        std::getline(ss, cell, ','); record.relevance = std::stod(cell);
        std::getline(ss, cell, ','); record.wordCount = std::stod(cell);
        
        data.push_back(record);
    }
    return data;
}
