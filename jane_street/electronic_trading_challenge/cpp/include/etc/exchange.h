#pragma once
#include <string>
#include <memory>
#include <optional>
#include <nlohmann/json.hpp>

namespace etc {

class ExchangeConnection {
public:
    virtual ~ExchangeConnection() = default;
    virtual void connect(const std::string& host, int port) = 0;
    virtual void close() = 0;
    virtual std::optional<nlohmann::json> read() = 0;
    virtual void write(const nlohmann::json& message) = 0;

    void send_hello(const std::string& team_name);
    void place_order(int order_id, const std::string& symbol, const std::string& side, int price, int size);
    void cancel_order(int order_id);
    void convert(int order_id, const std::string& symbol, const std::string& side, int size);
};

class TcpExchangeConnection : public ExchangeConnection {
public:
    TcpExchangeConnection() = default;
    ~TcpExchangeConnection() override;
    void connect(const std::string& host, int port) override;
    void close() override;
    std::optional<nlohmann::json> read() override;
    void write(const nlohmann::json& message) override;

private:
#ifdef _WIN32
    uintptr_t sock = -1;
#else
    int sock = -1;
#endif
    std::string buffer;
};

} // namespace etc
