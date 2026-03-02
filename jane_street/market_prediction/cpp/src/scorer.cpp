#include "market_prediction/scorer.hpp"
#include <cmath>
#include <numeric>
#include <set>

namespace market_prediction {

double UtilityScorer::calculate_utility(const std::vector<Trade>& trades) {
    if (trades.empty()) return 0.0;

    std::map<int, double> daily_profits;
    std::set<int> unique_dates;

    for (const auto& trade : trades) {
        daily_profits[trade.date] += trade.weight * trade.resp * trade.action;
        unique_dates.insert(trade.date);
    }

    double sum_p = 0.0;
    double sum_p_sq = 0.0;
    for (const auto& [date, profit] : daily_profits) {
        sum_p += profit;
        sum_p_sq += profit * profit;
    }

    if (sum_p_sq == 0) return 0.0;

    double t = (sum_p / std::sqrt(sum_p_sq)) * std::sqrt(250.0 / unique_dates.size());
    double u = std::min(std::max(t, 0.0), 6.0) * sum_p;

    return u;
}

std::map<std::string, double> UtilityScorer::summary_table(const std::vector<Trade>& trades) {
    double profit = 0.0;
    int num_trades = 0;
    for (const auto& trade : trades) {
        profit += trade.weight * trade.resp * trade.action;
        if (trade.action == 1) num_trades++;
    }

    std::map<std::string, double> summary;
    summary["total_profit"] = profit;
    summary["num_trades_executed"] = static_cast<double>(num_trades);
    summary["utility_score"] = calculate_utility(trades);
    summary["participation_rate"] = trades.empty() ? 0.0 : static_cast<double>(num_trades) / trades.size();

    return summary;
}

} // namespace market_prediction
