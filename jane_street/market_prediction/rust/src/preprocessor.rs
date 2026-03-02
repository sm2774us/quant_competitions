use std::collections::VecDeque;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use ndarray::{Array1, Array2, Axis, concatenate};
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct PreprocessorState {
    medians: Vec<Vec<f64>>,
    scaler_mean: Vec<f64>,
    scaler_scale: Vec<f64>,
}

pub struct MarketPreprocessor {
    n_features: usize,
    window_size: usize,
    window: VecDeque<Array1<f64>>,
    // Pre-trained stats
    pub medians: Array2<f64>,
    pub scaler_mean: Array1<f64>,
    pub scaler_scale: Array1<f64>,
}

impl MarketPreprocessor {
    pub fn new(n_features: usize, window_size: usize) -> Self {
        Self {
            n_features,
            window_size,
            window: VecDeque::new(),
            medians: Array2::zeros((2, n_features)),
            scaler_mean: Array1::zeros(n_features - 1 + 6),
            scaler_scale: Array1::ones(n_features - 1 + 6),
        }
    }

    pub fn transform(&mut self, x: &Array1<f64>) -> Array1<f64> {
        let mut x_imputed = x.clone();
        
        // 1. Imputation
        let side = x[0];
        let side_id = if side == -1.0 { 0 } else { 1 };
        
        // Use medians for initial imputation
        let current_medians = if self.window.is_empty() {
            self.medians.row(side_id).to_owned()
        } else {
            // Calculate rolling median (simplified: mean of window for performance in Rust)
            let mut sum = Array1::zeros(self.n_features);
            for vec in &self.window {
                sum += vec;
            }
            sum / (self.window.len() as f64)
        };

        for i in 0..x_imputed.len() {
            if x_imputed[i].is_nan() {
                x_imputed[i] = current_medians[i];
            }
        }
        
        // 2. Interactions (6 features)
        let interactions = Array1::from_vec(vec![
            x_imputed[3] * x_imputed[45],
            x_imputed[10] * x_imputed[122],
            x_imputed[14] * x_imputed[58],
            x_imputed[22] * x_imputed[42],
            x_imputed[35] * x_imputed[20],
            x_imputed[45] * x_imputed[47],
        ]);
        
        let extended = concatenate![Axis(0), x_imputed, interactions];
        
        // 3. Normalization (skips f0, indices 1..136)
        let f0 = extended[0];
        let f_rest = extended.slice(ndarray::s![1..]);
        
        let f_norm = (f_rest.to_owned() - &self.scaler_mean) / (&self.scaler_scale + 1e-8);
        
        let mut result = Array1::zeros(self.n_features + 6);
        result[0] = f0;
        result.slice_mut(ndarray::s![1..]).assign(&f_norm);
        
        // 4. Update stats
        self.update_stats(x_imputed);
        
        result
    }

    fn update_stats(&mut self, x: Array1<f64>) {
        self.window.push_back(x);
        if self.window.len() > self.window_size {
            self.window.pop_front();
        }
    }

    pub fn load_state<P: AsRef<Path>>(&mut self, path: P) -> Result<(), Box<dyn std::error::Error>> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let state: PreprocessorState = serde_json::from_reader(reader)?;
        
        // Convert Vecs back to Arrays
        if !state.medians.is_empty() {
            let rows = state.medians.len();
            let cols = state.medians[0].len();
            let mut flat = Vec::with_capacity(rows * cols);
            for row in state.medians {
                flat.extend(row);
            }
            self.medians = Array2::from_shape_vec((rows, cols), flat)?;
        }
        
        self.scaler_mean = Array1::from_vec(state.scaler_mean);
        self.scaler_scale = Array1::from_vec(state.scaler_scale);
        
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_preprocessor_init() {
        let prep = MarketPreprocessor::new(130, 5);
        assert_eq!(prep.n_features, 130);
    }

    #[test]
    fn test_preprocessor_transform() {
        let mut prep = MarketPreprocessor::new(130, 5);
        let x = Array1::zeros(130);
        let res = prep.transform(&x);
        assert_eq!(res.len(), 136);
    }

    #[test]
    fn test_nan_imputation() {
        let mut prep = MarketPreprocessor::new(130, 5);
        let mut x = Array1::zeros(130);
        x[0] = -1.0;
        x[1] = f64::NAN;
        
        // Set a median for side -1, feature 1
        prep.medians[[0, 1]] = 20.0;
        
        let res = prep.transform(&x);
        assert_relative_eq!(res[0], -1.0);
        assert_relative_eq!(res[1], 20.0, epsilon = 1e-5);
    }
}
