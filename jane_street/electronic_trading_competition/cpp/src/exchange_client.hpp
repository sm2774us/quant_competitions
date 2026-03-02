#pragma once
#include <string>
#include <iostream>
#include <memory>
#include <nlohmann/json.hpp>
#include "models.hpp"

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#endif

namespace trading_bot {

class ExchangeClient {
public:
    ExchangeClient(const std::string& hostname, int port, const std::string& team_name);
    ~ExchangeClient();

    void connect();
    void send(const nlohmann::json& j);
    void send_order(const Order& order);
    nlohmann::json read();

private:
    std::string hostname_;
    int port_;
    std::string team_name_;
#ifdef _WIN32
    SOCKET socket_ = INVALID_SOCKET;
#else
    int socket_ = -1;
#endif
};

} // namespace trading_bot
