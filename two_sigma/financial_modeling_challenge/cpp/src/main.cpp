#include <CLI/CLI.hpp>
#include "data_generator.h"
#include "environment.h"
#include "model.h"
#include <iostream>

int main(int argc, char** argv) {
    CLI::App app{"Two Sigma Financial Modeling C++ CLI"};

    auto generate = app.add_subcommand("generate-data", "Generates synthetic data");
    int samples = 1000, features = 100, instruments = 50;
    std::string output = "data/train.csv";
    generate->add_option("--samples", samples, "Number of samples");
    generate->add_option("--features", features, "Number of features");
    generate->add_option("--instruments", instruments, "Number of instruments");
    generate->add_option("--output", output, "Output path");

    auto train = app.add_subcommand("train", "Trains the model");
    std::string data_path = "data/train.csv";
    std::string model_path = "models/model.bin";
    train->add_option("--data", data_path, "Data path");
    train->add_option("--model-path", model_path, "Model save path");

    auto evaluate = app.add_subcommand("evaluate", "Evaluates the model");
    evaluate->add_option("--data", data_path, "Data path");
    evaluate->add_option("--model-path", model_path, "Model load path");

    CLI11_PARSE(app, argc, argv);

    if (generate->parsed()) {
        two_sigma::DataGenerator gen(samples, features, instruments);
        gen.generate(output);
    } else if (train->parsed()) {
        two_sigma::Environment env(data_path);
        auto obs = env.reset();
        two_sigma::FinancialModel model;
        model.train(obs.train_features, obs.train_target);
        model.save(model_path);
    } else if (evaluate->parsed()) {
        two_sigma::Environment env(data_path);
        two_sigma::FinancialModel model = two_sigma::FinancialModel::load(model_path);
        auto obs = env.reset();
        while (!env.is_done()) {
            auto predictions = model.predict(obs.test_features);
            auto [next_obs, reward] = env.step(predictions);
            obs = next_obs;
        }
        std::cout << "Evaluation complete. Final Score: " << env.calculate_final_score() << std::endl;
    }

    return 0;
}
