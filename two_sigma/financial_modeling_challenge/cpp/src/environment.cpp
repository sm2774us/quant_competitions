#include "environment.h"
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <cmath>

namespace two_sigma {

Environment::Environment(const std::string& data_path) : data_path_(data_path), current_ts_idx_(0) {
    load_data();
}

void Environment::load_data() {
    std::ifstream file(data_path_);
    if (!file) {
        std::cerr << "Could not open " << data_path_ << std::endl;
        return;
    }

    std::string line, word;
    std::getline(file, line); // header

    std::vector<std::vector<double>> rows;
    while (std::getline(file, line)) {
        std::stringstream ss(line);
        std::vector<double> row;
        while (std::getline(ss, word, ',')) {
            row.push_back(std::stod(word));
        }
        rows.push_back(row);
    }

    size_t n_rows = rows.size();
    if (n_rows == 0) return;
    size_t n_cols = rows[0].size();

    all_features_.resize(n_rows, n_cols - 3);
    all_targets_.resize(n_rows);
    ids_.reserve(n_rows);
    timestamps_.reserve(n_rows);

    for (size_t i = 0; i < n_rows; ++i) {
        ids_.push_back(static_cast<int>(rows[i][0]));
        timestamps_.push_back(static_cast<int>(rows[i][1]));
        all_targets_(i) = rows[i][2];
        for (size_t j = 3; j < n_cols; ++j) {
            all_features_(i, j - 3) = rows[i][j];
        }
    }

    std::vector<int> unique_ts = timestamps_;
    std::sort(unique_ts.begin(), unique_ts.end());
    unique_ts.erase(std::unique(unique_ts.begin(), unique_ts.end()), unique_ts.end());
    unique_timestamps_ = unique_ts;

    split_ts_idx_ = unique_timestamps_.size() / 2;
    current_ts_idx_ = split_ts_idx_;
}

Observation Environment::reset() {
    current_ts_idx_ = split_ts_idx_;
    predictions_full_.clear();
    targets_full_.clear();

    Observation obs;
    
    // Training data: everything before split_ts_idx_
    int split_ts = unique_timestamps_[split_ts_idx_];
    std::vector<int> train_indices;
    for (size_t i = 0; i < timestamps_.size(); ++i) {
        if (timestamps_[i] < split_ts) train_indices.push_back(i);
    }

    obs.train_features.resize(train_indices.size(), all_features_.cols());
    obs.train_target.resize(train_indices.size());
    for (size_t i = 0; i < train_indices.size(); ++i) {
        obs.train_features.row(i) = all_features_.row(train_indices[i]);
        obs.train_target(i) = all_targets_(train_indices[i]);
    }

    // Current test data
    std::vector<int> test_indices;
    for (size_t i = 0; i < timestamps_.size(); ++i) {
        if (timestamps_[i] == split_ts) test_indices.push_back(i);
    }
    
    obs.test_features.resize(test_indices.size(), all_features_.cols());
    obs.ids.clear();
    for (size_t i = 0; i < test_indices.size(); ++i) {
        obs.test_features.row(i) = all_features_.row(test_indices[i]);
        obs.ids.push_back(ids_[test_indices[i]]);
        targets_full_.push_back(all_targets_(test_indices[i]));
    }

    return obs;
}

std::pair<Observation, double> Environment::step(const Eigen::VectorXd& predictions) {
    for (int i = 0; i < predictions.size(); ++i) {
        predictions_full_.push_back(predictions(i));
    }

    current_ts_idx_++;
    if (is_done()) return {Observation(), 0.0};

    int ts = unique_timestamps_[current_ts_idx_];
    Observation next_obs;
    std::vector<int> test_indices;
    for (size_t i = 0; i < timestamps_.size(); ++i) {
        if (timestamps_[i] == ts) test_indices.push_back(i);
    }

    next_obs.test_features.resize(test_indices.size(), all_features_.cols());
    for (size_t i = 0; i < test_indices.size(); ++i) {
        next_obs.test_features.row(i) = all_features_.row(test_indices[i]);
        next_obs.ids.push_back(ids_[test_indices[i]]);
        targets_full_.push_back(all_targets_(test_indices[i]));
    }

    return {next_obs, 0.0};
}

bool Environment::is_done() const {
    return current_ts_idx_ >= unique_timestamps_.size();
}

double Environment::calculate_final_score() const {
    if (predictions_full_.empty()) return 0.0;
    
    double mean_y = 0;
    for (double y : targets_full_) mean_y += y;
    mean_y /= targets_full_.size();

    double ss_res = 0, ss_tot = 0;
    for (size_t i = 0; i < predictions_full_.size(); ++i) {
        ss_res += std::pow(targets_full_[i] - predictions_full_[i], 2);
        ss_tot += std::pow(targets_full_[i] - mean_y, 2);
    }
    
    double r2 = 1.0 - (ss_res / ss_tot);
    return (r2 > 0 ? 1.0 : -1.0) * std::sqrt(std::abs(r2));
}

} // namespace two_sigma
