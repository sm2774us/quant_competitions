#include "Interfaces.hpp"
#include <algorithm>
#include <numeric>

std::vector<MarketRecord> Preprocessor::process(std::vector<MarketRecord>& market, const std::vector<NewsRecord>& news) {
    // Aggregating news by time and assetName
    std::map<std::pair<std::string, std::string>, std::vector<const NewsRecord*>> newsGroups;
    for (const auto& n : news) {
        newsGroups[{n.time, n.assetName}].push_back(&n);
    }

    for (auto& m : market) {
        auto it = newsGroups.find({m.time, m.assetName});
        if (it != newsGroups.end()) {
            double neg = 0, neut = 0, pos = 0, rel = 0, wc = 0;
            for (const auto* n : it->second) {
                neg += n->sentimentNegative;
                neut += n->sentimentNeutral;
                pos += n->sentimentPositive;
                rel += n->relevance;
                wc += n->wordCount;
            }
            size_t count = it->second.size();
            m.features.push_back(neg / count);
            m.features.push_back(neut / count);
            m.features.push_back(pos / count);
            m.features.push_back(rel / count);
            m.features.push_back(wc / count);
        } else {
            // Fill with zeros if no news
            for (int i = 0; i < 5; ++i) m.features.push_back(0.0);
        }
        
        // Outlier handling
        double ratio = m.close / m.open;
        if (ratio < 0.33) m.open = m.close;
        if (ratio > 2.0) m.close = m.open;
    }
    return market;
}
