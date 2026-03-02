#include "market_prediction/models.hpp"
#include <cmath>

namespace market_prediction {

Linear::Linear(int in_features, int out_features) {
    weights = Eigen::MatrixXd::Random(out_features, in_features) * 0.1;
    bias = Eigen::VectorXd::Zero(out_features);
}

Eigen::MatrixXd Linear::forward(const Eigen::MatrixXd& input) const {
    // input: (batch_size, in_features)
    // weights: (out_features, in_features)
    // result: (batch_size, out_features)
    return (input * weights.transpose()).rowwise() + bias.transpose();
}

BatchNorm::BatchNorm(int num_features) {
    mean = Eigen::VectorXd::Zero(num_features);
    var = Eigen::VectorXd::Ones(num_features);
    gamma = Eigen::VectorXd::Ones(num_features);
    beta = Eigen::VectorXd::Zero(num_features);
}

Eigen::MatrixXd BatchNorm::forward(const Eigen::MatrixXd& input) const {
    Eigen::VectorXd inv_std = (var.array() + eps).sqrt().inverse();
    Eigen::MatrixXd normalized = (input.rowwise() - mean.transpose()).array().rowwise() * inv_std.transpose().array();
    return (normalized.array().rowwise() * gamma.transpose().array()).rowwise() + beta.transpose().array();
}

LeakyReLU::LeakyReLU(double negative_slope) : slope(negative_slope) {}

Eigen::MatrixXd LeakyReLU::forward(const Eigen::MatrixXd& input) const {
    return input.unaryExpr([this](double x) { return x > 0 ? x : x * slope; });
}

MarketModel::MarketModel(int input_dim) {
    int hidden_size = input_dim * 2;
    
    // Layer 1
    layers_.push_back(std::make_unique<BatchNorm>(input_dim));
    layers_.push_back(std::make_unique<Linear>(input_dim, hidden_size));
    layers_.push_back(std::make_unique<LeakyReLU>(0.01));
    
    // Layer 2
    layers_.push_back(std::make_unique<BatchNorm>(hidden_size));
    layers_.push_back(std::make_unique<Linear>(hidden_size, hidden_size));
    layers_.push_back(std::make_unique<LeakyReLU>(0.01));
    
    // Layer 3
    layers_.push_back(std::make_unique<BatchNorm>(hidden_size));
    layers_.push_back(std::make_unique<Linear>(hidden_size, hidden_size));
    layers_.push_back(std::make_unique<LeakyReLU>(0.01));
    
    // Final
    layers_.push_back(std::make_unique<Linear>(hidden_size, 1));
}

Eigen::VectorXd MarketModel::predict(const Eigen::VectorXd& input) const {
    Eigen::MatrixXd x = input.transpose();
    for (const auto& layer : layers_) {
        x = layer->forward(x);
    }
    // Sigmoid
    return x.unaryExpr([](double val) { return 1.0 / (1.0 + std::exp(-val)); }).transpose();
}

Eigen::MatrixXd MarketModel::batch_predict(const Eigen::MatrixXd& inputs) const {
    Eigen::MatrixXd x = inputs;
    for (const auto& layer : layers_) {
        x = layer->forward(x);
    }
    // Sigmoid
    return x.unaryExpr([](double val) { return 1.0 / (1.0 + std::exp(-val)); });
}

ModelManager::ModelManager(int input_dim) {
    model_ = std::make_unique<MarketModel>(input_dim);
}

Eigen::VectorXd ModelManager::predict(const Eigen::VectorXd& input) const {
    return model_->predict(input);
}

Eigen::MatrixXd ModelManager::batch_predict(const Eigen::MatrixXd& inputs) const {
    return model_->batch_predict(inputs);
}

void ModelManager::load_weights(const std::string& path) {
    (void)path;
}

} // namespace market_prediction
