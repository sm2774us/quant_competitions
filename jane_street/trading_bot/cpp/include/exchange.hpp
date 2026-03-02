#pragma once
#include <string>
#include <memory>
#include <nlohmann/json.hpp>
#ifdef _WIN32
#include <winsock2.h>
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#endif

namespace trading_bot {

using json = nlohmann::json;

class Exchange {
public:
    Exchange(const std::string& host, int port);
    ~Exchange();

    void connect();
    void send(const json& message);
    json receive();
    void close();

private:
    std::string host_;
    int port_;
#ifdef _WIN32
    SOCKET socket_ = INVALID_SOCKET;
#else
    int socket_ = -1;
#endif
    std::string buffer_;
};

} // namespace trading_bot
