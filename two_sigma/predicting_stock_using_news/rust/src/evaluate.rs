use std::collections::HashMap;

pub fn evaluate(predictions: &[f64], targets: &[f64], universe: &[i32], times: &[String]) -> f64 {
    if predictions.is_empty() { return 0.0; }

    let mut daily_returns: HashMap<String, f64> = HashMap::new();
    for i in 0..predictions.len() {
        let val = predictions[i] * targets[i] * (universe[i] as f64);
        *daily_returns.entry(times[i].clone()).or_insert(0.0) += val;
    }

    let returns: Vec<f64> = daily_returns.values().cloned().collect();
    if returns.is_empty() { return 0.0; }

    let n = returns.len() as f64;
    let mu = returns.iter().sum::<f64>() / n;
    
    let sq_sum = returns.iter().map(|r| r * r).sum::<f64>();
    let stdev = (sq_sum / n - mu * mu).sqrt();

    if stdev == 0.0 || stdev.is_nan() { return 0.0; }
    mu / stdev
}
