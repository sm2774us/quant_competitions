use ndarray::{Array1, Array2};
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::{BufReader, BufWriter};

#[derive(Serialize, Deserialize, Default)]
pub struct FinancialModel {
    // Manually handle serialization of weights to avoid complex ndarray trait bounds in CI
    pub weights_vec: Option<Vec<f64>>,
    pub alpha: f64,
    #[serde(skip)]
    pub weights: Option<Array1<f64>>,
}

impl FinancialModel {
    pub fn new(alpha: f64) -> Self {
        Self { weights_vec: None, weights: None, alpha }
    }

    pub fn train(&mut self, x: &Array2<f64>, y: &Array1<f64>) {
        let n_samples = x.nrows();
        let n_features = x.ncols();
        let mut x_bias = Array2::zeros((n_samples, n_features + 1));
        x_bias.column_mut(0).fill(1.0);
        x_bias.slice_mut(ndarray::s![.., 1..]).assign(x);

        let xt = x_bias.t();
        let mut xtx = xt.dot(&x_bias);

        for i in 0..xtx.nrows() {
            xtx[[i, i]] += self.alpha;
        }

        let xty = xt.dot(y);
        let w = self.solve_linear_system(xtx, xty);
        self.weights_vec = Some(w.to_vec());
        self.weights = Some(w);
        println!("Model training complete.");
    }

    fn solve_linear_system(&self, mut a: Array2<f64>, mut b: Array1<f64>) -> Array1<f64> {
        let n = b.len();
        for i in 0..n {
            let mut pivot = i;
            for j in i + 1..n {
                if a[[j, i]].abs() > a[[pivot, i]].abs() {
                    pivot = j;
                }
            }
            if pivot != i {
                for k in i..n {
                    let tmp = a[[i, k]];
                    a[[i, k]] = a[[pivot, k]];
                    a[[pivot, k]] = tmp;
                }
                let tmp = b[i];
                b[i] = b[pivot];
                b[pivot] = tmp;
            }

            for j in i + 1..n {
                let factor = a[[j, i]] / a[[i, i]];
                b[j] -= factor * b[i];
                for k in i..n {
                    a[[j, k]] -= factor * a[[i, k]];
                }
            }
        }

        let mut x = Array1::zeros(n);
        for i in (0..n).rev() {
            let mut sum = 0.0;
            for j in i + 1..n {
                sum += a[[i, j]] * x[j];
            }
            x[i] = (b[i] - sum) / a[[i, i]];
        }
        x
    }

    pub fn predict(&self, x: &Array2<f64>) -> Array1<f64> {
        let w = if let Some(ref w) = self.weights {
            w.clone()
        } else if let Some(ref wv) = self.weights_vec {
            Array1::from_vec(wv.clone())
        } else {
            panic!("Model must be trained before prediction");
        };

        let n_samples = x.nrows();
        let n_features = x.ncols();
        let mut x_bias = Array2::zeros((n_samples, n_features + 1));
        x_bias.column_mut(0).fill(1.0);
        x_bias.slice_mut(ndarray::s![.., 1..]).assign(x);
        
        x_bias.dot(&w)
    }

    pub fn save(&self, path: &str) -> std::io::Result<()> {
        let file = File::create(path)?;
        let writer = BufWriter::new(file);
        serde_json::to_writer(writer, self)?;
        println!("Model saved to {}", path);
        Ok(())
    }

    pub fn load(path: &str) -> std::io::Result<Self> {
        let file = File::open(path)?;
        let reader = BufReader::new(file);
        let mut model: FinancialModel = serde_json::from_reader(reader)?;
        if let Some(ref wv) = model.weights_vec {
            model.weights = Some(Array1::from_vec(wv.clone()));
        }
        Ok(model)
    }
}
