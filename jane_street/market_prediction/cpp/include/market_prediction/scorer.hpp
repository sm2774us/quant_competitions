#pragma once

#include <vector>
#include <string>
#include <map>

namespace market_prediction {

struct Trade {
    int date;
    double weight;
    double resp;
    int action;
};

class UtilityScorer {
public:
    static double calculate_utility(const std::vector<Trade>& trades);
    static std::map<std::string, double> summary_table(const std::vector<Trade>& trades);
};

} // namespace market_prediction
