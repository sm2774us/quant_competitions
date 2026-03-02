pub struct Model {
    weights: Vec<f64>,
    bias: f64,
}

impl Model {
    pub fn new() -> Self {
        Self { weights: Vec::new(), bias: 0.0 }
    }

    pub fn train(&mut self, x: &[Vec<f64>], y: &[f64]) {
        if x.is_empty() { return; }
        let n_features = x[0].len();
        self.weights = vec![0.0; n_features];
        self.bias = 0.0;

        let lr = 0.01;
        let epochs = 50;

        for _ in 0..epochs {
            for (xi, yi) in x.iter().zip(y.iter()) {
                let mut pred = self.bias;
                for (wj, xij) in self.weights.iter().zip(xi.iter()) {
                    pred += wj * xij;
                }

                let error = pred - yi;
                self.bias -= lr * error;
                for (wj, xij) in self.weights.iter_mut().zip(xi.iter()) {
                    *wj -= lr * error * xij;
                }
            }
        }
    }

    pub fn predict(&self, x: &[Vec<f64>]) -> Vec<f64> {
        x.iter().map(|xi| {
            let mut pred = self.bias;
            for (wj, xij) in self.weights.iter().zip(xi.iter()) {
                pred += wj * xij;
            }
            pred.clamp(-1.0, 1.0)
        }).collect()
    }
}
