#include "data_generator.h"
#include <fstream>
#include <iostream>
#include <random>
#include <filesystem>

namespace two_sigma {

DataGenerator::DataGenerator(int n_samples, int n_features, int n_instruments)
    : n_samples_(n_samples), n_features_(n_features), n_instruments_(n_instruments) {}

void DataGenerator::generate(const std::string& output_path) {
    std::filesystem::create_directories(std::filesystem::path(output_path).parent_path());
    std::ofstream out(output_path);
    if (!out) return;

    // Header
    out << "id,timestamp,y";
    for (int i = 0; i < n_features_; ++i) {
        out << ",technical_" << i;
    }
    out << "\n";

    std::mt19937 gen(42);
    std::normal_distribution<double> dist_y(0.0, 0.02);
    std::normal_distribution<double> dist_feat(0.0, 1.0);

    int n_timestamps = n_samples_ / n_instruments_;
    for (int t = 0; t < n_timestamps; ++t) {
        for (int i = 0; i < n_instruments_; ++i) {
            out << i << "," << t << "," << dist_y(gen);
            for (int f = 0; f < n_features_; ++f) {
                out << "," << dist_feat(gen);
            }
            out << "\n";
        }
    }
    std::cout << "Generated synthetic data at " << output_path << std::endl;
}

} // namespace two_sigma
