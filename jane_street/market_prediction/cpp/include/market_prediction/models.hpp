#pragma once

#include <Eigen/Dense>
#include <vector>
#include <memory>
#include <string>

namespace market_prediction {

class Layer {
public:
    virtual ~Layer() = default;
    virtual Eigen::MatrixXd forward(const Eigen::MatrixXd& input) const = 0;
};

class Linear : public Layer {
public:
    Linear(int in_features, int out_features);
    Eigen::MatrixXd forward(const Eigen::MatrixXd& input) const override;
    
    Eigen::MatrixXd weights;
    Eigen::VectorXd bias;
};

class BatchNorm : public Layer {
public:
    explicit BatchNorm(int num_features);
    Eigen::MatrixXd forward(const Eigen::MatrixXd& input) const override;
    
    Eigen::VectorXd mean;
    Eigen::VectorXd var;
    Eigen::VectorXd gamma;
    Eigen::VectorXd beta;
    double eps = 1e-5;
};

class LeakyReLU : public Layer {
public:
    explicit LeakyReLU(double negative_slope = 0.01);
    Eigen::MatrixXd forward(const Eigen::MatrixXd& input) const override;
    
    double slope;
};

class MarketModel {
public:
    explicit MarketModel(int input_dim);
    Eigen::VectorXd predict(const Eigen::VectorXd& input) const;
    Eigen::MatrixXd batch_predict(const Eigen::MatrixXd& inputs) const;

private:
    std::vector<std::unique_ptr<Layer>> layers_;
};

class ModelManager {
public:
    explicit ModelManager(int input_dim = 136);
    Eigen::VectorXd predict(const Eigen::VectorXd& input) const;
    Eigen::MatrixXd batch_predict(const Eigen::MatrixXd& inputs) const;
    void load_weights(const std::string& path);

private:
    std::unique_ptr<MarketModel> model_;
};

} // namespace market_prediction
