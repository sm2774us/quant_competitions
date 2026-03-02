#include "strategies.hpp"
#include <iostream>
#include <algorithm>
#include <cmath>

namespace citadel {

const double MAIN_TAKER = 0.0065;
const double ALT_TAKER = 0.005;
const double TAKER_FEE = (MAIN_TAKER + ALT_TAKER) * 2;
const double BUFFER = 0.01;
const double TAKER4 = MAIN_TAKER * 5;
const int MAX_QUANTITY = 50000;

// ExchangeArbitrage
ExchangeArbitrage::ExchangeArbitrage(std::shared_ptr<TradingApi> api) : api_(api) {}
void ExchangeArbitrage::run() {
    execute("WMT-M", "WMT-A");
    execute("CAT-M", "CAT-A");
    execute("MMM-M", "MMM-A");
}

void ExchangeArbitrage::execute(const std::string& mticker, const std::string& aticker) {
    try {
        auto mbook = api_->get_order_book(mticker);
        auto abook = api_->get_order_book(aticker);

        if (mbook.bids.empty() || mbook.asks.empty() || abook.bids.empty() || abook.asks.empty()) return;

        double mbid = mbook.bids[0].price;
        double mask = mbook.asks[0].price;
        double abid = abook.bids[0].price;
        double aask = abook.asks[0].price;

        int m_bid_room = 0; for (auto& b : mbook.bids) if (b.price == mbid) m_bid_room += (b.quantity - b.quantity_filled);
        int a_ask_room = 0; for (auto& a : abook.asks) if (a.price == aask) a_ask_room += (a.quantity - a.quantity_filled);
        int a_bid_room = 0; for (auto& b : abook.bids) if (b.price == abid) a_bid_room += (b.quantity - b.quantity_filled);
        int m_ask_room = 0; for (auto& a : mbook.asks) if (a.price == mask) m_ask_room += (a.quantity - a.quantity_filled);

        if (mbid - aask > TAKER_FEE + BUFFER * 2) {
            int qty = std::min({m_bid_room, a_ask_room, MAX_QUANTITY});
            if (qty > 0) {
                api_->post_order(mticker, "MARKET", "SELL", qty);
                api_->post_order(aticker, "MARKET", "BUY", qty);
            }
        } else if (abid - mask > TAKER_FEE + BUFFER * 2) {
            int qty = std::min({a_bid_room, m_ask_room, MAX_QUANTITY});
            if (qty > 0) {
                api_->post_order(aticker, "MARKET", "SELL", qty);
                api_->post_order(mticker, "MARKET", "BUY", qty);
            }
        }
    } catch (...) {}
}

// IndexArbitrage
IndexArbitrage::IndexArbitrage(std::shared_ptr<TradingApi> api) : api_(api) {}
void IndexArbitrage::run() {
    try {
        auto secs = api_->get_securities();
        if (secs.find("ETF") == secs.end()) return;

        auto& etf = secs["ETF"];
        std::map<std::string, double> best_bids, best_asks;
        std::map<std::string, int> best_bids_q, best_asks_q;

        for (auto& t : tickers_) {
            std::string tm = t + "-M", ta = t + "-A";
            if (secs.find(tm) == secs.end() || secs.find(ta) == secs.end()) continue;
            auto &sm = secs[tm], &sa = secs[ta];

            if (sm.bid >= sa.bid) { best_bids[tm] = sm.bid; best_bids_q[tm] = sm.bid_size; }
            else { best_bids[ta] = sa.bid; best_bids_q[ta] = sa.bid_size; }

            if (sm.ask <= sa.ask) { best_asks[tm] = sm.ask; best_asks_q[tm] = sm.ask_size; }
            else { best_asks[ta] = sa.ask; best_asks_q[ta] = sa.ask_size; }
        }

        if (best_bids.size() < tickers_.size() || best_asks.size() < tickers_.size()) return;

        double composite_bid = 0, composite_ask = 0;
        int composite_bid_q = MAX_QUANTITY, composite_ask_q = MAX_QUANTITY;
        for (auto const& [k, v] : best_bids) { composite_bid += v; composite_bid_q = std::min(composite_bid_q, best_bids_q[k]); }
        for (auto const& [k, v] : best_asks) { composite_ask += v; composite_ask_q = std::min(composite_ask_q, best_asks_q[k]); }

        if (etf.bid - composite_ask > TAKER4 + BUFFER) {
            int qty = std::min({etf.bid_size, composite_ask_q, MAX_QUANTITY});
            if (qty > 0) {
                api_->post_order("ETF", "MARKET", "SELL", qty);
                for (auto const& [k, v] : best_asks) api_->post_order(k, "MARKET", "BUY", qty);
            }
        } else if (composite_bid - etf.ask > TAKER4 + BUFFER) {
            int qty = std::min({etf.ask_size, composite_bid_q, MAX_QUANTITY});
            if (qty > 0) {
                for (auto const& [k, v] : best_bids) api_->post_order(k, "MARKET", "SELL", qty);
                api_->post_order("ETF", "MARKET", "BUY", qty);
            }
        }
    } catch (...) {}
}

// ShockHandler
ShockHandler::ShockHandler(std::shared_ptr<TradingApi> api) : api_(api) {}
void ShockHandler::run() {}
void ShockHandler::run_with_tick(int current_tick) {
    try {
        auto news_list = api_->get_news();
        for (auto& news : news_list) {
            int elapsed = current_tick - news.tick;
            if (elapsed > 2) continue;

            double amount = 0;
            try {
                std::string s = news.headline.substr(news.headline.size() - 6);
                s.erase(std::remove(s.begin(), s.end(), '$'), s.end());
                amount = std::stod(s);
            } catch (...) { continue; }

            std::string m_ticker = news.ticker + "-M", a_ticker = news.ticker + "-A";
            if (elapsed < 2) {
                if (amount > MAIN_TAKER + BUFFER * 2) {
                    api_->post_order(m_ticker, "MARKET", "BUY", MAX_QUANTITY);
                    api_->post_order(a_ticker, "MARKET", "BUY", MAX_QUANTITY);
                } else if (-amount > MAIN_TAKER + BUFFER * 2) {
                    api_->post_order(m_ticker, "MARKET", "SELL", MAX_QUANTITY);
                    api_->post_order(a_ticker, "MARKET", "SELL", MAX_QUANTITY);
                }
            } else if (elapsed == 2) {
                if (amount > MAIN_TAKER + BUFFER * 2) {
                    api_->post_order(m_ticker, "MARKET", "SELL", MAX_QUANTITY);
                    api_->post_order(a_ticker, "MARKET", "SELL", MAX_QUANTITY);
                } else if (-amount > MAIN_TAKER + BUFFER * 2) {
                    api_->post_order(m_ticker, "MARKET", "BUY", MAX_QUANTITY);
                    api_->post_order(a_ticker, "MARKET", "BUY", MAX_QUANTITY);
                }
            }
        }
    } catch (...) {}
}

} // namespace citadel
