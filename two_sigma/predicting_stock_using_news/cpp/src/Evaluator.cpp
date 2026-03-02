#include "Interfaces.hpp"
#include <cmath>
#include <numeric>
#include <map>

double Evaluator::evaluate(const std::vector<double>& predictions, const std::vector<double>& targets, const std::vector<int>& universe, const std::vector<std::string>& times) {
    if (predictions.empty()) return 0.0;
    
    std::map<std::string, double> dailyReturns;
    for (size_t i = 0; i < predictions.size(); ++i) {
        dailyReturns[times[i]] += predictions[i] * targets[i] * universe[i];
    }
    
    std::vector<double> returns;
    for (auto const& [time, val] : dailyReturns) {
        returns.push_back(val);
    }
    
    if (returns.empty()) return 0.0;
    
    double sum = std::accumulate(returns.begin(), returns.end(), 0.0);
    double mu = sum / returns.size();
    
    double sq_sum = std::inner_product(returns.begin(), returns.end(), returns.begin(), 0.0);
    double stdev = std::sqrt(sq_sum / returns.size() - mu * mu);
    
    if (stdev == 0 || std::isnan(stdev)) return 0.0;
    
    return mu / stdev;
}
