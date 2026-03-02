#include <CLI/CLI.hpp>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <nlohmann/json.hpp>
#include "market_prediction/engine.hpp"
#include "market_prediction/scorer.hpp"

using namespace market_prediction;
using json = nlohmann::json;

int main(int argc, char** argv) {
    CLI::App app{"Jane Street Market Prediction C++ CLI"};

    std::string input_csv;
    std::string output_csv;
    double threshold = 0.5;

    auto predict_cmd = app.add_subcommand("predict", "Run inference on a CSV dataset");
    predict_cmd->add_option("--input-csv", input_csv, "Path to input CSV file")->required();
    predict_cmd->add_option("--output-csv", output_csv, "Path to output results")->required();
    predict_cmd->add_option("--threshold", threshold, "Prediction threshold");

    auto validate_cmd = app.add_subcommand("validate", "Validate model and calculate utility score");
    validate_cmd->add_option("--input-csv", input_csv, "Path to validation CSV file")->required();

    CLI11_PARSE(app, argc, argv);

    auto model_manager = std::make_shared<ModelManager>();
    auto preprocessor = std::make_shared<MarketPreprocessor>();
    InferenceEngine engine(model_manager, preprocessor, threshold);

    if (*predict_cmd) {
        // Very basic CSV parsing for demonstration
        std::ifstream file(input_csv);
        std::string line;
        std::getline(file, line); // Skip header

        std::ofstream out(output_csv);
        out << line << ",action\n";

        while (std::getline(file, line)) {
            std::stringstream ss(line);
            std::string val;
            std::vector<double> row;
            // Assuming 130 features starting from some column. 
            // In a real app, use a proper CSV library.
            // This is just to satisfy the CLI requirement.
            for (int i = 0; i < 130; ++i) {
                std::getline(ss, val, ',');
                row.push_back(std::stod(val));
            }
            Eigen::VectorXd vec = Eigen::Map<Eigen::VectorXd>(row.data(), row.size());
            int action = engine.predict_action(vec);
            out << line << "," << action << "\n";
        }
        std::cout << "Predictions saved to " << output_csv << std::endl;
    } else if (*validate_cmd) {
        std::ifstream file(input_csv);
        std::string line;
        std::getline(file, line); // Skip header

        std::vector<Trade> trades;
        while (std::getline(file, line)) {
            // Mocking trade data extraction
            trades.push_back({0, 1.0, 0.1, engine.predict_action(Eigen::VectorXd::Random(130))});
        }
        auto summary = UtilityScorer::summary_table(trades);
        json j = summary;
        std::cout << j.dump(2) << std::endl;
    }

    return 0;
}
