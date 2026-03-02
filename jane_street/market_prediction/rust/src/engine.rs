use crate::models::ModelManager;
use crate::preprocessor::MarketPreprocessor;
use ndarray::Array1;

pub struct InferenceEngine {
    model_manager: ModelManager,
    preprocessor: MarketPreprocessor,
    threshold: f64,
}

impl InferenceEngine {
    pub fn new(model_manager: ModelManager, preprocessor: MarketPreprocessor, threshold: f64) -> Self {
        Self {
            model_manager,
            preprocessor,
            threshold,
        }
    }

    pub fn predict_action(&mut self, features: &Array1<f64>) -> i32 {
        let processed = self.preprocessor.transform(features);
        let prob = self.model_manager.predict(&processed);
        if prob >= self.threshold { 1 } else { 0 }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_engine_predict() {
        let model_manager = ModelManager::new(136);
        let preprocessor = MarketPreprocessor::new(130, 5);
        let mut engine = InferenceEngine::new(model_manager, preprocessor, 0.5);
        
        let features = Array1::from_elem(130, 0.5);
        let action = engine.predict_action(&features);
        assert!(action == 0 || action == 1);
    }
}
