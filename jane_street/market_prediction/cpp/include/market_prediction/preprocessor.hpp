#pragma once

#include <Eigen/Dense>
#include <vector>
#include <deque>
#include <cmath>

namespace market_prediction {

class MarketPreprocessor {
public:
    explicit MarketPreprocessor(int n_features = 130, int window_size = 100);

    Eigen::VectorXd transform(const Eigen::VectorXd& x);

    void save_state(const std::string& path);
    void load_state(const std::string& path);

private:
    void update_stats(const Eigen::VectorXd& x);

    int n_features_;
    int window_size_;
    Eigen::VectorXd means_;
    Eigen::VectorXd stds_;
    
    // Pre-trained stats
    Eigen::MatrixXd medians_;
    Eigen::VectorXd scaler_mean_;
    Eigen::VectorXd scaler_scale_;
    
    std::deque<Eigen::VectorXd> window_;
};

} // namespace market_prediction
