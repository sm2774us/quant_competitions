#include "bot.hpp"
#include <CLI/CLI.hpp>
#include <iostream>

int main(int argc, char** argv) {
    CLI::App app{"Jane Street ETC Trading Bot"};

    std::string host = "localhost";
    int port = 25000;
    std::string team = "TEAMNAME";

    app.add_option("--host", host, "Exchange host");
    app.add_option("--port", port, "Exchange port");
    app.add_option("--team", team, "Team name");

    CLI11_PARSE(app, argc, argv);

    try {
        trading_bot::Bot bot(host, port, team);
        bot.run();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
