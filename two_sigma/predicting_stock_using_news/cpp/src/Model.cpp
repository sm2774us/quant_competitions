#include "Interfaces.hpp"
#include <cmath>
#include <iostream>

void Model::train(const std::vector<std::vector<double>>& X, const std::vector<double>& y) {
    if (X.empty()) return;
    size_t n_samples = X.size();
    size_t n_features = X[0].size();
    
    weights.assign(n_features, 0.0);
    bias = 0.0;
    
    double lr = 0.01;
    int epochs = 100;
    
    for (int epoch = 0; epoch < epochs; ++epoch) {
        for (size_t i = 0; i < n_samples; ++i) {
            double prediction = bias;
            for (size_t j = 0; j < n_features; ++j) {
                prediction += weights[j] * X[i][j];
            }
            
            double error = prediction - y[i];
            bias -= lr * error;
            for (size_t j = 0; j < n_features; ++j) {
                weights[j] -= lr * error * X[i][j];
            }
        }
    }
}

std::vector<double> Model::predict(const std::vector<std::vector<double>>& X) {
    std::vector<double> predictions;
    for (const auto& row : X) {
        double val = bias;
        for (size_t j = 0; j < weights.size(); ++j) {
            val += weights[j] * row[j];
        }
        // Clip to [-1, 1]
        predictions.push_back(std::max(-1.0, std::min(1.0, val)));
    }
    return predictions;
}
