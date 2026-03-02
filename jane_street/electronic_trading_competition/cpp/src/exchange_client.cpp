#include "exchange_client.hpp"
#include <stdexcept>
#include <sstream>

namespace trading_bot {

ExchangeClient::ExchangeClient(const std::string& hostname, int port, const std::string& team_name)
    : hostname_(hostname), port_(port), team_name_(team_name) {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        throw std::runtime_error("WSAStartup failed");
    }
#endif
}

ExchangeClient::~ExchangeClient() {
#ifdef _WIN32
    if (socket_ != INVALID_SOCKET) closesocket(socket_);
    WSACleanup();
#else
    if (socket_ != -1) close(socket_);
#endif
}

void ExchangeClient::connect() {
    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(hostname_.c_str(), std::to_string(port_).c_str(), &hints, &res) != 0) {
        throw std::runtime_error("getaddrinfo failed");
    }

#ifdef _WIN32
    socket_ = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (socket_ == INVALID_SOCKET) {
#else
    socket_ = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (socket_ == -1) {
#endif
        freeaddrinfo(res);
        throw std::runtime_error("socket creation failed");
    }

    if (::connect(socket_, res->ai_addr, (int)res->ai_addrlen) != 0) {
        freeaddrinfo(res);
        throw std::runtime_error("connection failed");
    }

    freeaddrinfo(res);
    send({{"type", "hello"}, {"team", team_name_}});
}

void ExchangeClient::send(const nlohmann::json& j) {
    std::string data = j.dump() + "\n";
    ::send(socket_, data.c_str(), (int)data.length(), 0);
}

void ExchangeClient::send_order(const Order& order) {
    send(order.to_json());
}

nlohmann::json ExchangeClient::read() {
    std::string line;
    char buffer[1];
    while (true) {
        int n = recv(socket_, buffer, 1, 0);
        if (n <= 0) break;
        if (buffer[0] == '\n') break;
        line += buffer[0];
    }
    if (line.empty()) return json::object();
    return json::parse(line);
}

} // namespace trading_bot
