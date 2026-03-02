pub mod data_generator;
pub mod environment;
pub mod model;

use ndarray::{Array1, Array2};

#[derive(Debug, Clone)]
pub struct Observation {
    pub train_features: Array2<f64>,
    pub train_target: Array1<f64>,
    pub test_features: Array2<f64>,
    pub ids: Vec<i32>,
}
