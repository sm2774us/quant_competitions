# Rust Solution: Two Sigma Financial Modeling

## 1. Directory Structure
```
.
├── Cargo.toml
├── Dockerfile
├── README.md
├── src
│   ├── data_generator.rs
│   ├── environment.rs
│   ├── lib.rs
│   ├── main.rs
│   └── model.rs
└── tests
    └── test_solution.rs
```

## 2. Instructions

### Build and Run Locally
1. Ensure you have Rust and Cargo installed (version >= 1.84).
2. Build the project:
   ```bash
   cargo build --release
   ```
3. Generate synthetic data:
   ```bash
   cargo run --release -- generate-data --samples 1000 --output data/train.csv
   ```
4. Train the model:
   ```bash
   cargo run --release -- train --data data/train.csv --model-path models/model.json
   ```
5. Evaluate the model:
   ```bash
   cargo run --release -- evaluate --data data/train.csv --model-path models/model.json
   ```
6. Run tests:
   ```bash
   cargo test
   ```

### Build and Run via Docker
1. Build the image:
   ```bash
   docker build -t two-sigma-rust .
   ```
2. Run a command (e.g., generate data):
   ```bash
   docker run -v $(pwd)/data:/app/data two-sigma-rust generate-data --output data/train.csv
   ```

## 3. Solution Explanation
The Rust solution provides a type-safe and memory-efficient implementation using the `ndarray` crate.
- **Data Generator**: Utilizes the `rand` crate to produce synthetic financial data in CSV format.
- **Environment API**: Mimics the Kaggle environment, providing a streaming interface for predictions.
- **Model Architecture**:
  - Implements Ridge Regression using the Normal Equations.
  - Features a custom linear system solver using Gaussian elimination with partial pivoting for robustness without external BLAS dependencies.
  - Uses `serde` for JSON serialization of model weights.

### Complexity Analysis
- **Time Complexity**:
  - Training: $O(N 	imes F^2 + F^3)$ for matrix operations and solving the linear system.
  - Prediction: $O(F)$ per sample.
- **Space Complexity**:
  - $O(F)$ for model weights.

### Architecture Diagram
```
[ CLI (Clap) ] <--> [ FinancialModel ] <--> [ Environment ]
                         ^                       |
                         |                       v
                  [ Ndarray Math ] <--> [ Data (CSV) ]
```

## 4. UML Sequence Diagram
```
User -> CLI: run evaluate
CLI -> Model: load(path)
CLI -> Environment: new(path)
Environment -> CLI: reset() -> obs
loop until done
    CLI -> Model: predict(obs.test_features)
    Model -> CLI: predictions
    CLI -> Environment: step(predictions) -> next_obs
end
CLI -> Environment: calculate_final_score()
CLI -> User: show score
```

## 5. Flowchart
```
[Start] --> [Generate CSV] --> [Train Ridge (Rust)]
                                      |
                                      v
[Finish] <-- [Score] <-- [Evaluate Environment]
```

## 6. Tabulated Summary
| Feature | Implementation |
|---------|----------------|
| Language | Rust 1.84 |
| Algebra | ndarray |
| CLI | clap |
| Build Tool | Cargo |
| Testing | Cargo Test |
| Serialization | Serde (JSON) |
