#ifndef TWO_SIGMA_COMMON_H
#define TWO_SIGMA_COMMON_H

#include <vector>
#include <string>
#include <map>
#include <Eigen/Dense>

namespace two_sigma {

struct Observation {
    Eigen::MatrixXd train_features;
    Eigen::VectorXd train_target;
    Eigen::MatrixXd test_features;
    std::vector<int> ids;
};

} // namespace two_sigma

#endif // TWO_SIGMA_COMMON_H
