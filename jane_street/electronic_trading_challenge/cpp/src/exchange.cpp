#include "etc/exchange.h"
#include <iostream>
#include <stdexcept>

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#endif

namespace etc {

void ExchangeConnection::send_hello(const std::string& team_name) {
    nlohmann::json msg = {{"type", "hello"}, {"team", team_name}};
    write(msg);
}

void ExchangeConnection::place_order(int order_id, const std::string& symbol, const std::string& side, int price, int size) {
    nlohmann::json msg = {
        {"type", "add"},
        {"order_id", order_id},
        {"symbol", symbol},
        {"dir", side},
        {"price", price},
        {"size", size}
    };
    write(msg);
}

void ExchangeConnection::cancel_order(int order_id) {
    nlohmann::json msg = {{"type", "cancel"}, {"order_id", order_id}};
    write(msg);
}

void ExchangeConnection::convert(int order_id, const std::string& symbol, const std::string& side, int size) {
    nlohmann::json msg = {
        {"type", "convert"},
        {"order_id", order_id},
        {"symbol", symbol},
        {"dir", side},
        {"size", size}
    };
    write(msg);
}

TcpExchangeConnection::~TcpExchangeConnection() {
    close();
}

void TcpExchangeConnection::connect(const std::string& host, int port) {
#ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif

    struct addrinfo hints{}, *res;
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host.c_str(), std::to_string(port).c_str(), &hints, &res) != 0) {
        throw std::runtime_error("getaddrinfo failed");
    }

    sock = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (::connect(sock, res->ai_addr, res->ai_addrlen) < 0) {
        freeaddrinfo(res);
        throw std::runtime_error("connect failed");
    }
    freeaddrinfo(res);
}

void TcpExchangeConnection::close() {
    if (sock != -1) {
#ifdef _WIN32
        closesocket(sock);
        WSACleanup();
#else
        ::close(sock);
#endif
        sock = -1;
    }
}

std::optional<nlohmann::json> TcpExchangeConnection::read() {
    char buf[1024];
    while (buffer.find('\n') == std::string::npos) {
        int n = recv(sock, buf, sizeof(buf), 0);
        if (n <= 0) return std::nullopt;
        buffer.append(buf, n);
    }
    size_t pos = buffer.find('\n');
    std::string line = buffer.substr(0, pos);
    buffer.erase(0, pos + 1);
    return nlohmann::json::parse(line);
}

void TcpExchangeConnection::write(const nlohmann::json& message) {
    std::string s = message.dump() + "\n";
    send(sock, s.c_str(), s.size(), 0);
}

} // namespace etc
