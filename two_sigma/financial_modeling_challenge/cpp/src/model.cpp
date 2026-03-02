#include "model.h"
#include <iostream>
#include <fstream>
#include <Eigen/Dense>

namespace two_sigma {

FinancialModel::FinancialModel(double alpha) : alpha_(alpha) {}

void FinancialModel::train(const Eigen::MatrixXd& X, const Eigen::VectorXd& y) {
    // Add bias term
    Eigen::MatrixXd X_bias(X.rows(), X.cols() + 1);
    X_bias << Eigen::MatrixXd::Ones(X.rows(), 1), X;
    
    // Ridge regression formula: (X^T * X + alpha * I) \ (X^T * y)
    Eigen::MatrixXd XtX = X_bias.transpose() * X_bias;
    XtX += alpha_ * Eigen::MatrixXd::Identity(XtX.rows(), XtX.cols());
    
    weights_ = XtX.ldlt().solve(X_bias.transpose() * y);
    std::cout << "Model training complete." << std::endl;
}

Eigen::VectorXd FinancialModel::predict(const Eigen::MatrixXd& X) const {
    // Add bias term
    Eigen::MatrixXd X_bias(X.rows(), X.cols() + 1);
    X_bias << Eigen::MatrixXd::Ones(X.rows(), 1), X;
    
    return X_bias * weights_;
}

void FinancialModel::save(const std::string& path) const {
    std::ofstream out(path, std::ios::binary);
    if (out) {
        size_t size = weights_.size();
        out.write(reinterpret_cast<const char*>(&size), sizeof(size));
        out.write(reinterpret_cast<const char*>(weights_.data()), size * sizeof(double));
        std::cout << "Model saved to " << path << std::endl;
    }
}

FinancialModel FinancialModel::load(const std::string& path) {
    FinancialModel model;
    std::ifstream in(path, std::ios::binary);
    if (in) {
        size_t size;
        in.read(reinterpret_cast<char*>(&size), sizeof(size));
        model.weights_.resize(size);
        in.read(reinterpret_cast<char*>(model.weights_.data()), size * sizeof(double));
    }
    return model;
}

} // namespace two_sigma
