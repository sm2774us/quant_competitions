#include "market_prediction/engine.hpp"

namespace market_prediction {

InferenceEngine::InferenceEngine(std::shared_ptr<ModelManager> model_manager, 
                                 std::shared_ptr<MarketPreprocessor> preprocessor,
                                 double threshold)
    : model_manager_(model_manager), preprocessor_(preprocessor), threshold_(threshold) {}

int InferenceEngine::predict_action(const Eigen::VectorXd& features) {
    Eigen::VectorXd processed = preprocessor_->transform(features);
    Eigen::VectorXd prob = model_manager_->predict(processed);
    return prob(0) >= threshold_ ? 1 : 0;
}

std::vector<int> InferenceEngine::batch_predict(const Eigen::MatrixXd& features_batch) {
    std::vector<int> actions;
    actions.reserve(features_batch.rows());
    
    // Vectorized preprocessor transform for whole batch would be better, 
    // but here we maintain same logic as python version.
    for (int i = 0; i < features_batch.rows(); ++i) {
        actions.push_back(predict_action(features_batch.row(i)));
    }
    
    return actions;
}

} // namespace market_prediction
