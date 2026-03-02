#include <iostream>
#include <map>
#include <argparse/argparse.hpp>
#include "exchange_client.hpp"
#include "strategies.hpp"

using namespace trading_bot;

int main(int argc, char* argv[]) {
    argparse::ArgumentParser program("trading_bot");

    program.add_argument("--hostname").default_value(std::string("production"));
    program.add_argument("--port").default_value(25000).scan<'i', int>();
    program.add_argument("--team").default_value(std::string("PANIPURISTREET"));

    try {
        program.parse_args(argc, argv);
    } catch (const std::runtime_error& err) {
        std::cerr << err.what() << std::endl;
        std::cerr << program;
        return 1;
    }

    std::string hostname = program.get<std::string>("--hostname");
    int port = program.get<int>("--port");
    std::string team = program.get<std::string>("--team");

    ExchangeClient client(hostname, port, team);
    BondStrategy bond_strat;
    std::map<std::string, std::unique_ptr<MACDStrategy>> macd_strats;
    int order_id_counter = 0;

    try {
        client.connect();
        while (true) {
            json msg = client.read();
            if (msg.empty()) break;

            std::string type = msg.value("type", "");
            if (type == "hello") {
                for (auto& symbol_info : msg["symbols"]) {
                    std::string sym = symbol_info["symbol"];
                    if (sym != "BOND" && sym != "VALE" && sym != "VALBZ") {
                        macd_strats[sym] = std::make_unique<MACDStrategy>(sym);
                    }
                }
            } else if (type == "book") {
                std::string sym = msg["symbol"];
                std::vector<Order> orders;
                if (sym == "BOND") {
                    orders = bond_strat.update_book(BookMessage::from_json(msg), order_id_counter);
                }
                for (auto& o : orders) client.send_order(o);
            } else if (type == "trade") {
                std::string sym = msg["symbol"];
                if (macd_strats.contains(sym)) {
                    std::vector<Order> orders = macd_strats[sym]->update_price(msg["price"], order_id_counter);
                    for (auto& o : orders) client.send_order(o);
                }
            } else if (type == "fill") {
                std::string sym = msg["symbol"];
                if (sym == "BOND") bond_strat.update_fill(msg["dir"], msg["size"]);
                else if (macd_strats.contains(sym)) macd_strats[sym]->update_fill(msg["dir"], msg["size"]);
            }
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
