use two_sigma_financial_modeling::model::FinancialModel;
use two_sigma_financial_modeling::data_generator::DataGenerator;
use two_sigma_financial_modeling::environment::Environment;
use ndarray::{Array1, Array2};
use std::fs;

#[test]
fn test_model_train_predict() {
    let mut model = FinancialModel::new(0.1);
    let x = Array2::from_elem((10, 5), 1.0);
    let y = Array1::from_elem(10, 2.0);
    model.train(&x, &y);
    let preds = model.predict(&x);
    assert_eq!(preds.len(), 10);
}

#[test]
fn test_data_generation() {
    let path = "test_gen.csv";
    let gen = DataGenerator::new(100, 10, 5);
    gen.generate(path).unwrap();
    assert!(fs::metadata(path).is_ok());
    fs::remove_file(path).unwrap();
}

#[test]
fn test_environment_flow() {
    let path = "test_env.csv";
    let gen = DataGenerator::new(200, 10, 5);
    gen.generate(path).unwrap();
    
    let mut env = Environment::new(path).unwrap();
    let obs = env.reset();
    assert!(obs.train_features.nrows() > 0);
    
    let preds = Array1::from_elem(obs.test_features.nrows(), 0.01);
    let (next, _, _) = env.step(preds);
    assert!(next.is_some());
    
    fs::remove_file(path).unwrap();
}
