#include "market_prediction/preprocessor.hpp"
#include <nlohmann/json.hpp>
#include <fstream>
#include <numeric>
#include <algorithm>

namespace market_prediction {

MarketPreprocessor::MarketPreprocessor(int n_features, int window_size)
    : n_features_(n_features), window_size_(window_size) {
    means_ = Eigen::VectorXd::Zero(n_features);
    stds_ = Eigen::VectorXd::Ones(n_features);
    
    medians_ = Eigen::MatrixXd::Zero(2, n_features);
    scaler_mean_ = Eigen::VectorXd::Zero(n_features - 1 + 6);
    scaler_scale_ = Eigen::VectorXd::Ones(n_features - 1 + 6);
}

Eigen::VectorXd MarketPreprocessor::transform(const Eigen::VectorXd& x) {
    Eigen::VectorXd x_imputed = x;
    
    // 1. Impute NaNs
    int side_id = (x(0) == -1.0) ? 0 : 1;
    Eigen::VectorXd current_medians;
    
    if (window_.empty()) {
        current_medians = medians_.row(side_id);
    } else {
        // Simple median calculation across window (could be optimized)
        current_medians = Eigen::VectorXd::Zero(n_features_);
        for (int i = 0; i < n_features_; ++i) {
            std::vector<double> vals;
            for (const auto& w_vec : window_) {
                if (!std::isnan(w_vec(i))) vals.push_back(w_vec(i));
            }
            if (vals.empty()) {
                current_medians(i) = medians_(side_id, i);
            } else {
                std::sort(vals.begin(), vals.end());
                current_medians(i) = vals[vals.size() / 2];
            }
        }
    }
    
    for (int i = 0; i < x_imputed.size(); ++i) {
        if (std::isnan(x_imputed(i))) {
            x_imputed(i) = current_medians(i);
        }
    }
    
    // 2. Interactions (6 features)
    Eigen::VectorXd interactions(6);
    interactions(0) = x_imputed(3) * x_imputed(45);
    interactions(1) = x_imputed(10) * x_imputed(122);
    interactions(2) = x_imputed(14) * x_imputed(58);
    interactions(3) = x_imputed(22) * x_imputed(42);
    interactions(4) = x_imputed(35) * x_imputed(20);
    interactions(5) = x_imputed(45) * x_imputed(47);
    
    Eigen::VectorXd extended(n_features_ + 6);
    extended << x_imputed, interactions;
    
    // 3. Normalize (skipping f0, so indices 1 to 135)
    Eigen::VectorXd result(n_features_ + 6);
    result(0) = extended(0);
    
    Eigen::VectorXd f_rest = extended.tail(n_features_ + 5); // 130+6-1 = 135
    result.tail(n_features_ + 5) = (f_rest - scaler_mean_).array() / (scaler_scale_.array() + 1e-8);
    
    // 4. Update stats
    update_stats(x_imputed);
    
    return result;
}

void MarketPreprocessor::update_stats(const Eigen::VectorXd& x) {
    window_.push_back(x);
    if (window_.size() > static_cast<size_t>(window_size_)) {
        window_.pop_front();
    }
}

void MarketPreprocessor::save_state(const std::string& path) {
    nlohmann::json j;
    std::vector<std::vector<double>> med_vec;
    for(int i=0; i<2; ++i) {
        std::vector<double> row;
        for(int j=0; j<n_features_; ++j) row.push_back(medians_(i,j));
        med_vec.push_back(row);
    }
    j["medians"] = med_vec;
    
    std::vector<double> mean_vec(scaler_mean_.data(), scaler_mean_.data() + scaler_mean_.size());
    std::vector<double> scale_vec(scaler_scale_.data(), scaler_scale_.data() + scaler_scale_.size());
    j["scaler_mean"] = mean_vec;
    j["scaler_scale"] = scale_vec;
    
    std::ofstream o(path);
    o << j.dump(4) << std::endl;
}

void MarketPreprocessor::load_state(const std::string& path) {
    std::ifstream i(path);
    if (!i.is_open()) return;
    
    nlohmann::json j;
    i >> j;
    
    if (j.contains("medians")) {
        auto med_vec = j["medians"].get<std::vector<std::vector<double>>>();
        for(int r=0; r<2; ++r) {
            for(int c=0; c<n_features_; ++c) medians_(r,c) = med_vec[r][c];
        }
    }
    
    if (j.contains("scaler_mean")) {
        auto mean_vec = j["scaler_mean"].get<std::vector<double>>();
        for(size_t k=0; k<mean_vec.size(); ++k) scaler_mean_(k) = mean_vec[k];
    }
    
    if (j.contains("scaler_scale")) {
        auto scale_vec = j["scaler_scale"].get<std::vector<double>>();
        for(size_t k=0; k<scale_vec.size(); ++k) scaler_scale_(k) = scale_vec[k];
    }
}

} // namespace market_prediction
