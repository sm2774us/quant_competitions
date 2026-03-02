#include "exchange.hpp"
#include <stdexcept>
#include <iostream>
#include <cstring>

#ifdef _WIN32
#pragma comment(lib, "ws2_32.lib")
#endif

namespace trading_bot {

Exchange::Exchange(const std::string& host, int port) : host_(host), port_(port) {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        throw std::runtime_error("WSAStartup failed");
    }
#endif
}

Exchange::~Exchange() {
    close();
#ifdef _WIN32
    WSACleanup();
#endif
}

void Exchange::connect() {
#ifdef _WIN32
    socket_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (socket_ == INVALID_SOCKET) {
        throw std::runtime_error("Socket creation failed");
    }
#else
    socket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_ < 0) {
        throw std::runtime_error("Socket creation failed");
    }
#endif

    struct sockaddr_in serv_addr;
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port_);
    
    // Simplification: assume host is IP or localhost for now
    if (host_ == "localhost") {
#ifdef _WIN32
        serv_addr.sin_addr.s_addr = inet_addr("127.0.0.1");
#else
        inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr);
#endif
    } else {
#ifdef _WIN32
        serv_addr.sin_addr.s_addr = inet_addr(host_.c_str());
#else
        inet_pton(AF_INET, host_.c_str(), &serv_addr.sin_addr);
#endif
    }

#ifdef _WIN32
    if (::connect(socket_, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) == SOCKET_ERROR) {
        throw std::runtime_error("Connect failed: " + std::to_string(WSAGetLastError()));
    }
#else
    if (::connect(socket_, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        throw std::runtime_error("Connect failed");
    }
#endif
}

void Exchange::send(const json& message) {
    std::string data = message.dump() + "
";
#ifdef _WIN32
    if (::send(socket_, data.c_str(), (int)data.length(), 0) == SOCKET_ERROR) {
        throw std::runtime_error("Send failed");
    }
#else
    if (::send(socket_, data.c_str(), data.length(), 0) < 0) {
        throw std::runtime_error("Send failed");
    }
#endif
}

json Exchange::receive() {
    while (true) {
        size_t newline_pos = buffer_.find('
');
        if (newline_pos != std::string::npos) {
            std::string line = buffer_.substr(0, newline_pos);
            buffer_.erase(0, newline_pos + 1);
            if (line.empty()) continue;
            return json::parse(line);
        }

        char temp_buffer[4096];
#ifdef _WIN32
        int bytes_received = recv(socket_, temp_buffer, sizeof(temp_buffer), 0);
#else
        int bytes_received = recv(socket_, temp_buffer, sizeof(temp_buffer), 0);
#endif
        if (bytes_received <= 0) {
            return json();
        }
        buffer_.append(temp_buffer, bytes_received);
    }
}

void Exchange::close() {
#ifdef _WIN32
    if (socket_ != INVALID_SOCKET) {
        closesocket(socket_);
        socket_ = INVALID_SOCKET;
    }
#else
    if (socket_ >= 0) {
        ::close(socket_);
        socket_ = -1;
    }
#endif
}

} // namespace trading_bot
