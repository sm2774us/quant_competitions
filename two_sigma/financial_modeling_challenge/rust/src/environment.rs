use crate::Observation;
use csv::Reader;
use ndarray::{Array1, Array2};
use std::collections::HashSet;
use std::error::Error;

pub struct Environment {
    data_path: String,
    all_features: Array2<f64>,
    all_targets: Array1<f64>,
    timestamps: Vec<i32>,
    ids: Vec<i32>,
    unique_timestamps: Vec<i32>,
    current_ts_idx: usize,
    split_ts_idx: usize,
    predictions_full: Vec<f64>,
    targets_full: Vec<f64>,
}

impl Environment {
    pub fn new(data_path: &str) -> Result<Self, Box<dyn Error>> {
        let mut reader = Reader::from_path(data_path)?;
        let mut ids = Vec::new();
        let mut timestamps = Vec::new();
        let mut targets = Vec::new();
        let mut features_vec = Vec::new();
        let mut n_features = 0;

        for result in reader.records() {
            let record = result?;
            ids.push(record[0].parse()?);
            timestamps.push(record[1].parse()?);
            targets.push(record[2].parse()?);
            
            let row_features: Vec<f64> = record.iter().skip(3).map(|s| s.parse().unwrap()).collect();
            n_features = row_features.len();
            features_vec.extend(row_features);
        }

        let n_rows = ids.len();
        let all_features = Array2::from_shape_vec((n_rows, n_features), features_vec)?;
        let all_targets = Array1::from_vec(targets);

        let mut unique_ts_set: HashSet<i32> = timestamps.iter().cloned().collect();
        let mut unique_timestamps: Vec<i32> = unique_ts_set.into_iter().collect();
        unique_timestamps.sort();

        let split_ts_idx = unique_timestamps.len() / 2;

        Ok(Self {
            data_path: data_path.to_string(),
            all_features,
            all_targets,
            timestamps,
            ids,
            unique_timestamps,
            current_ts_idx: split_ts_idx,
            split_ts_idx,
            predictions_full: Vec::new(),
            targets_full: Vec::new(),
        })
    }

    pub fn reset(&mut self) -> Observation {
        self.current_ts_idx = self.split_ts_idx;
        self.predictions_full.clear();
        self.targets_full.clear();
        self.get_observation()
    }

    pub fn step(&mut self, predictions: Array1<f64>) -> (Option<Observation>, f64, bool) {
        for &p in predictions.iter() {
            self.predictions_full.push(p);
        }

        self.current_ts_idx += 1;
        if self.is_done() {
            return (None, 0.0, true);
        }

        let obs = self.get_observation();
        (Some(obs), 0.0, false)
    }

    pub fn is_done(&self) -> bool {
        self.current_ts_idx >= self.unique_timestamps.len()
    }

    fn get_observation(&mut self) -> Observation {
        let ts = self.unique_timestamps[self.current_ts_idx];
        
        // Find indices for training (all before split)
        let split_ts = self.unique_timestamps[self.split_ts_idx];
        let mut train_indices = Vec::new();
        for (idx, &t) in self.timestamps.iter().enumerate() {
            if t < split_ts {
                train_indices.push(idx);
            }
        }

        let mut train_feat_vec = Vec::new();
        let mut train_target_vec = Vec::new();
        for &idx in &train_indices {
            for col in 0..self.all_features.ncols() {
                train_feat_vec.push(self.all_features[[idx, col]]);
            }
            train_target_vec.push(self.all_targets[idx]);
        }
        let train_features = Array2::from_shape_vec((train_indices.len(), self.all_features.ncols()), train_feat_vec).unwrap();
        let train_target = Array1::from_vec(train_target_vec);

        // Current test data
        let mut test_indices = Vec::new();
        for (idx, &t) in self.timestamps.iter().enumerate() {
            if t == ts {
                test_indices.push(idx);
            }
        }

        let mut test_feat_vec = Vec::new();
        let mut test_ids = Vec::new();
        for &idx in &test_indices {
            for col in 0..self.all_features.ncols() {
                test_feat_vec.push(self.all_features[[idx, col]]);
            }
            test_ids.push(self.ids[idx]);
            self.targets_full.push(self.all_targets[idx]);
        }
        let test_features = Array2::from_shape_vec((test_indices.len(), self.all_features.ncols()), test_feat_vec).unwrap();

        Observation {
            train_features,
            train_target,
            test_features,
            ids: test_ids,
        }
    }

    pub fn calculate_final_score(&self) -> f64 {
        if self.predictions_full.is_empty() { return 0.0; }
        
        let n = self.targets_full.len();
        let mean_y = self.targets_full.iter().sum::<f64>() / n as f64;
        
        let mut ss_res = 0.0;
        let mut ss_tot = 0.0;
        for i in 0..self.predictions_full.len() {
            ss_res += (self.targets_full[i] - self.predictions_full[i]).powi(2);
            ss_tot += (self.targets_full[i] - mean_y).powi(2);
        }
        
        let r2 = 1.0 - (ss_res / ss_tot);
        r2.signum() * r2.abs().sqrt()
    }
}
