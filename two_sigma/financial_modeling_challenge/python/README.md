# Python Solution: Two Sigma Financial Modeling

## 1. Directory Structure
```
.
├── Dockerfile
├── pyproject.toml
├── README.md
├── src
│   └── two_sigma
│       ├── cli.py
│       ├── data_generator.py
│       ├── environment.py
│       ├── __init__.py
│       └── model.py
└── tests
    ├── __init__.py
    └── test_solution.py
```

## 2. Instructions

### Build and Run Locally
1. Install [Poetry](https://python-poetry.org/docs/#installation).
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Generate synthetic data:
   ```bash
   poetry run two-sigma generate-data --samples 1000 --output data/train.h5
   ```
4. Train the model:
   ```bash
   poetry run two-sigma train --data data/train.h5 --model-path models/model.joblib
   ```
5. Evaluate the model:
   ```bash
   poetry run two-sigma evaluate --data data/train.h5 --model-path models/model.joblib
   ```
6. Run tests:
   ```bash
   poetry run pytest --cov=src tests/
   ```

### Build and Run via Docker
1. Build the image:
   ```bash
   docker build -t two-sigma-python .
   ```
2. Run a command (e.g., generate data):
   ```bash
   docker run -v $(pwd)/data:/app/data two-sigma-python generate-data --output data/train.h5
   ```

## 3. Solution Explanation
The Python solution implements a robust machine learning pipeline for financial time-series prediction.
- **Data Generator**: Creates synthetic HDF5 data to ensure the solution works even without the original Kaggle dataset.
- **Environment API**: Mimics the Kaggle `kagglegym` API, allowing for iterative predictions on a per-timestamp basis.
- **Model Architecture**: Uses a Scikit-Learn `Pipeline` consisting of:
  - Custom `FeatureEngineering` (null counts, median imputation).
  - `SimpleImputer` for handling any remaining NaNs.
  - `Ridge` regression for efficient, regularized linear modeling.

### Complexity Analysis
- **Time Complexity**:
  - Training: $O(N 	imes F^2 + F^3)$ where $N$ is number of samples and $F$ is number of features.
  - Prediction: $O(F)$ per sample.
- **Space Complexity**:
  - $O(F)$ to store model weights.

### Architecture Diagram
```
[ CLI ] <--> [ Model ] <--> [ Environment ]
                ^                |
                |                v
        [ Pipeline ] <--> [ Data (HDF5) ]
```

## 4. UML Sequence Diagram
```
User -> CLI: run evaluate
CLI -> Model: load()
CLI -> Environment: make()
Environment -> CLI: obs
loop until done
    CLI -> Model: predict(obs.features)
    Model -> CLI: preds
    CLI -> Environment: step(preds)
    Environment -> CLI: next_obs, reward, done
end
CLI -> User: show score
```

## 5. Flowchart
```
[Start] --> [Generate Data] --> [Train Model]
                                     |
                                     v
[Finish] <-- [Display Score] <-- [Evaluate]
```

## 6. Tabulated Summary
| Feature | Implementation |
|---------|----------------|
| Language | Python 3.13 |
| Framework | Scikit-Learn |
| CLI | Click |
| Build Tool | Poetry |
| Testing | Pytest |
| Metric | R-score |
