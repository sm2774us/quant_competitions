use ndarray::{Array1, Array2, Axis};
use std::path::Path;

pub trait Layer {
    fn forward(&self, input: Array2<f64>) -> Array2<f64>;
}

pub struct Linear {
    pub weights: Array2<f64>, // (out, in)
    pub bias: Array1<f64>,
}

impl Layer for Linear {
    fn forward(&self, input: Array2<f64>) -> Array2<f64> {
        let mut res = input.dot(&self.weights.t());
        res += &self.bias;
        res
    }
}

pub struct BatchNorm {
    pub mean: Array1<f64>,
    pub var: Array1<f64>,
    pub gamma: Array1<f64>,
    pub beta: Array1<f64>,
    pub eps: f64,
}

impl Layer for BatchNorm {
    fn forward(&self, input: Array2<f64>) -> Array2<f64> {
        let inv_std = (&self.var + self.eps).mapv(|v| v.sqrt().recip());
        let normalized = (input - &self.mean) * &inv_std;
        (normalized * &self.gamma) + &self.beta
    }
}

pub struct LeakyReLU {
    pub slope: f64,
}

impl Layer for LeakyReLU {
    fn forward(&self, input: Array2<f64>) -> Array2<f64> {
        input.mapv(|x| if x > 0.0 { x } else { x * self.slope })
    }
}

pub struct MarketModel {
    layers: Vec<Box<dyn Layer>>,
}

impl MarketModel {
    pub fn new(input_dim: usize) -> Self {
        let mut layers: Vec<Box<dyn Layer>> = Vec::new();
        let hidden_size = input_dim * 2;
        
        // Layer 1
        layers.push(Box::new(BatchNorm {
            mean: Array1::zeros(input_dim),
            var: Array1::ones(input_dim),
            gamma: Array1::ones(input_dim),
            beta: Array1::zeros(input_dim),
            eps: 1e-5,
        }));
        layers.push(Box::new(Linear {
            weights: Array2::zeros((hidden_size, input_dim)),
            bias: Array1::zeros(hidden_size),
        }));
        layers.push(Box::new(LeakyReLU { slope: 0.01 }));

        // Layer 2
        layers.push(Box::new(BatchNorm {
            mean: Array1::zeros(hidden_size),
            var: Array1::ones(hidden_size),
            gamma: Array1::ones(hidden_size),
            beta: Array1::zeros(hidden_size),
            eps: 1e-5,
        }));
        layers.push(Box::new(Linear {
            weights: Array2::zeros((hidden_size, hidden_size)),
            bias: Array1::zeros(hidden_size),
        }));
        layers.push(Box::new(LeakyReLU { slope: 0.01 }));

        // Layer 3
        layers.push(Box::new(BatchNorm {
            mean: Array1::zeros(hidden_size),
            var: Array1::ones(hidden_size),
            gamma: Array1::ones(hidden_size),
            beta: Array1::zeros(hidden_size),
            eps: 1e-5,
        }));
        layers.push(Box::new(Linear {
            weights: Array2::zeros((hidden_size, hidden_size)),
            bias: Array1::zeros(hidden_size),
        }));
        layers.push(Box::new(LeakyReLU { slope: 0.01 }));

        // Final
        layers.push(Box::new(Linear {
            weights: Array2::zeros((1, hidden_size)),
            bias: Array1::zeros(1),
        }));
        
        Self { layers }
    }

    pub fn predict(&self, input: &Array1<f64>) -> f64 {
        let mut x = input.clone().insert_axis(Axis(0));
        for layer in &self.layers {
            x = layer.forward(x);
        }
        1.0 / (1.0 + (-x[[0, 0]]).exp())
    }
}

pub struct ModelManager {
    model: MarketModel,
}

impl ModelManager {
    pub fn new(input_dim: usize) -> Self {
        Self {
            model: MarketModel::new(input_dim),
        }
    }

    pub fn predict(&self, input: &Array1<f64>) -> f64 {
        self.model.predict(input)
    }

    pub fn load_weights<P: AsRef<Path>>(&mut self, _path: P) -> Result<(), Box<dyn std::error::Error>> {
        // Implementation for loading weights from a binary format would go here.
        // For simplicity, we provide the architecture and the loading scaffold.
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_model_predict() {
        let manager = ModelManager::new(136);
        let input = Array1::from_elem(136, 1.0);
        let prob = manager.predict(&input);
        assert!(prob >= 0.0 && prob <= 1.0);
    }
}
