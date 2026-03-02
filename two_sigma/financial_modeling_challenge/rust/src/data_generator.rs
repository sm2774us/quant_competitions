use std::fs::File;
use std::io::Write;
use rand::prelude::*;
use rand_distr::{Normal, Distribution};

pub struct DataGenerator {
    pub n_samples: usize,
    pub n_features: usize,
    pub n_instruments: usize,
}

impl DataGenerator {
    pub fn new(n_samples: usize, n_features: usize, n_instruments: usize) -> Self {
        Self { n_samples, n_features, n_instruments }
    }

    pub fn generate(&self, output_path: &str) -> std::io::Result<()> {
        let mut file = File::create(output_path)?;
        
        // Header
        write!(file, "id,timestamp,y")?;
        for i in 0..self.n_features {
            write!(file, ",technical_{}", i)?;
        }
        writeln!(file)?;

        let mut rng = StdRng::seed_from_u64(42);
        let dist_y = Normal::new(0.0, 0.02).unwrap();
        let dist_feat = Normal::new(0.0, 1.0).unwrap();

        let n_timestamps = self.n_samples / self.n_instruments;
        for t in 0..n_timestamps {
            for i in 0..self.n_instruments {
                write!(file, "{},{},{}", i, t, dist_y.sample(&mut rng))?;
                for _ in 0..self.n_features {
                    write!(file, ",{}", dist_feat.sample(&mut rng))?;
                }
                writeln!(file)?;
            }
        }
        println!("Generated synthetic data at {}", output_path);
        Ok(())
    }
}
