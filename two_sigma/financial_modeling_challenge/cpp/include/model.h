#ifndef TWO_SIGMA_MODEL_H
#define TWO_SIGMA_MODEL_H

#include <Eigen/Dense>
#include <string>

namespace two_sigma {

class FinancialModel {
public:
    FinancialModel(double alpha = 1.0);
    
    void train(const Eigen::MatrixXd& X, const Eigen::VectorXd& y);
    Eigen::VectorXd predict(const Eigen::MatrixXd& X) const;
    
    void save(const std::string& path) const;
    static FinancialModel load(const std::string& path);

private:
    Eigen::VectorXd weights_;
    double alpha_;
};

} // namespace two_sigma

#endif // TWO_SIGMA_MODEL_H
