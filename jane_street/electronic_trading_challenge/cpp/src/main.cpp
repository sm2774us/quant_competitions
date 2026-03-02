#include <iostream>
#include <CLI/CLI.hpp>
#include "etc/bot.h"
#include "etc/exchange.h"

int main(int argc, char** argv) {
    CLI::App app{"Jane Street Electronic Trading Challenge Bot"};

    std::string host = "production";
    int port = 25000;
    std::string team = "FOMO";

    app.add_option("--host", host, "Exchange host")->default_val("production");
    app.add_option("--port", port, "Exchange port")->default_val(25000);
    app.add_option("--team", team, "Team name")->default_val("FOMO");

    CLI11_PARSE(app, argc, argv);

    try {
        auto conn = std::make_unique<etc::TcpExchangeConnection>();
        etc::TradingBot bot(std::move(conn), team);
        bot.run(host, port);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
