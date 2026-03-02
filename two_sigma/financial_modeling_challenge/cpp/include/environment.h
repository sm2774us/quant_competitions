#ifndef TWO_SIGMA_ENVIRONMENT_H
#define TWO_SIGMA_ENVIRONMENT_H

#include "common.h"
#include <string>
#include <vector>
#include <memory>

namespace two_sigma {

class Environment {
public:
    Environment(const std::string& data_path);
    
    Observation reset();
    std::pair<Observation, double> step(const Eigen::VectorXd& predictions);
    bool is_done() const;
    double calculate_final_score() const;

private:
    std::string data_path_;
    Eigen::MatrixXd all_features_;
    Eigen::VectorXd all_targets_;
    std::vector<int> timestamps_;
    std::vector<int> unique_timestamps_;
    std::vector<int> ids_;
    
    size_t current_ts_idx_;
    size_t split_ts_idx_;
    std::vector<double> predictions_full_;
    std::vector<double> targets_full_;

    void load_data();
};

} // namespace two_sigma

#endif // TWO_SIGMA_ENVIRONMENT_H
