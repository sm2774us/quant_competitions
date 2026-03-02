#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include "strategies.hpp"
#include "api.hpp"

using namespace citadel;
using namespace testing;

class MockTradingApi : public TradingApi {
public:
    MockTradingApi() : TradingApi("http://test", "key") {}
    MOCK_METHOD(CaseStatus, get_case, (), (override));
    MOCK_METHOD(std::map<std::string, Security>, get_securities, (), (override));
    MOCK_METHOD(OrderBook, get_order_book, (const std::string&), (override));
    MOCK_METHOD(std::vector<News>, get_news, (int), (override));
    MOCK_METHOD(OrderResponse, post_order, (const std::string&, const std::string&, const std::string&, int, std::optional<double>), (override));
};

TEST(ExchangeArbitrageTest, MarketArb) {
    auto mock_api = std::make_shared<MockTradingApi>();
    ExchangeArbitrage arb(mock_api);

    OrderBook mbook{"WMT-M", {{100.5, 1000, 0}}, {{101.0, 1000, 0}}};
    OrderBook abook{"WMT-A", {{99.5, 1000, 0}}, {{100.0, 1000, 0}}};

    EXPECT_CALL(*mock_api, get_order_book("WMT-M")).WillOnce(Return(mbook));
    EXPECT_CALL(*mock_api, get_order_book("WMT-A")).WillOnce(Return(abook));
    EXPECT_CALL(*mock_api, post_order("WMT-M", "MARKET", "SELL", 1000, _)).WillOnce(Return(OrderResponse{}));
    EXPECT_CALL(*mock_api, post_order("WMT-A", "MARKET", "BUY", 1000, _)).WillOnce(Return(OrderResponse{}));

    arb.execute("WMT-M", "WMT-A");
}

TEST(ShockHandlerTest, BuyOnShock) {
    auto mock_api = std::make_shared<MockTradingApi>();
    ShockHandler handler(mock_api);

    std::vector<News> news = {{10, "WMT", "WMT stock jump $10.00", ""}};
    EXPECT_CALL(*mock_api, get_news(_)).WillOnce(Return(news));
    EXPECT_CALL(*mock_api, post_order("WMT-M", "MARKET", "BUY", 50000, _)).WillOnce(Return(OrderResponse{}));
    EXPECT_CALL(*mock_api, post_order("WMT-A", "MARKET", "BUY", 50000, _)).WillOnce(Return(OrderResponse{}));

    handler.run_with_tick(11); // elapsed = 1
}

TEST(ShockHandlerTest, ReversalOnShock) {
    auto mock_api = std::make_shared<MockTradingApi>();
    ShockHandler handler(mock_api);

    std::vector<News> news = {{10, "WMT", "WMT stock jump $10.00", ""}};
    EXPECT_CALL(*mock_api, get_news(_)).WillOnce(Return(news));
    EXPECT_CALL(*mock_api, post_order("WMT-M", "MARKET", "SELL", 50000, _)).WillOnce(Return(OrderResponse{}));
    EXPECT_CALL(*mock_api, post_order("WMT-A", "MARKET", "SELL", 50000, _)).WillOnce(Return(OrderResponse{}));

    handler.run_with_tick(12); // elapsed = 2
}
