#include "etc/strategies.h"
#include <numeric>
#include <algorithm>

namespace etc {

std::vector<Action> BondStrategy::execute(const MarketState& state) {
    std::vector<Action> actions;
    auto it = state.books.find("BOND");
    if (it == state.books.end()) return actions;

    int current_pos = 0;
    auto pos_it = state.positions.find("BOND");
    if (pos_it != state.positions.end()) current_pos = pos_it->second;

    int limit = 100;
    if (current_pos < limit) {
        actions.push_back({"add", "BOND", "BUY", 999, limit - current_pos});
    }
    if (current_pos > -limit) {
        actions.push_back({"add", "BOND", "SELL", 1001, limit + current_pos});
    }
    return actions;
}

std::vector<Action> AdrStrategy::execute(const MarketState& state) {
    std::vector<Action> actions;
    auto valbz_it = state.last_trades.find("VALBZ");
    auto vale_it = state.last_trades.find("VALE");

    if (valbz_it == state.last_trades.end() || vale_it == state.last_trades.end()) return actions;
    if (valbz_it->second.size() < 10 || vale_it->second.size() < 10) return actions;

    double valbz_mean = std::accumulate(valbz_it->second.end() - 10, valbz_it->second.end(), 0.0) / 10.0;
    double vale_mean = std::accumulate(vale_it->second.end() - 10, vale_it->second.end(), 0.0) / 10.0;

    if (valbz_mean - vale_mean >= 2) {
        actions.push_back({"add", "VALE", "BUY", (int)vale_mean + 1, 10});
        actions.push_back({"convert", "VALE", "SELL", 0, 10});
        actions.push_back({"add", "VALBZ", "SELL", (int)valbz_mean - 1, 10});
    }
    return actions;
}

std::vector<Action> EtfStrategy::execute(const MarketState& state) {
    std::vector<Action> actions;
    std::vector<std::string> symbols = {"XLF", "BOND", "GS", "MS", "WFC"};
    std::map<std::string, double> means;

    for (const auto& sym : symbols) {
        auto it = state.last_trades.find(sym);
        if (it == state.last_trades.end() || it->second.size() < 25) return actions;
        means[sym] = std::accumulate(it->second.end() - 25, it->second.end(), 0.0) / 25.0;
    }

    double nav = 3 * means["BOND"] + 2 * means["GS"] + 3 * means["MS"] + 2 * means["WFC"];
    double xlf_price = 10 * means["XLF"];

    if (xlf_price + 150 < nav) {
        actions.push_back({"add", "XLF", "BUY", (int)means["XLF"] + 1, 100});
        actions.push_back({"convert", "XLF", "SELL", 0, 100});
        actions.push_back({"add", "BOND", "SELL", (int)means["BOND"] - 1, 30});
        actions.push_back({"add", "GS", "SELL", (int)means["GS"] - 1, 20});
        actions.push_back({"add", "MS", "SELL", (int)means["MS"] - 1, 30});
        actions.push_back({"add", "WFC", "SELL", (int)means["WFC"] - 1, 20});
    } else if (xlf_price - 150 > nav) {
        actions.push_back({"add", "BOND", "BUY", (int)means["BOND"] + 1, 30});
        actions.push_back({"add", "GS", "BUY", (int)means["GS"] + 1, 20});
        actions.push_back({"add", "MS", "BUY", (int)means["MS"] + 1, 30});
        actions.push_back({"add", "WFC", "BUY", (int)means["WFC"] + 1, 20});
        actions.push_back({"convert", "XLF", "BUY", 0, 100});
        actions.push_back({"add", "XLF", "SELL", (int)means["XLF"] - 1, 100});
    }

    return actions;
}

} // namespace etc
