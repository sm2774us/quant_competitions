#pragma once

#include "models.hpp"
#include "preprocessor.hpp"
#include <Eigen/Dense>

namespace market_prediction {

class InferenceEngine {
public:
    InferenceEngine(std::shared_ptr<ModelManager> model_manager, 
                   std::shared_ptr<MarketPreprocessor> preprocessor,
                   double threshold = 0.5);

    int predict_action(const Eigen::VectorXd& features);
    std::vector<int> batch_predict(const Eigen::MatrixXd& features_batch);

private:
    std::shared_ptr<ModelManager> model_manager_;
    std::shared_ptr<MarketPreprocessor> preprocessor_;
    double threshold_;
};

} // namespace market_prediction
