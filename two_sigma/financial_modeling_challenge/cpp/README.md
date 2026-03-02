# C++ Solution: Two Sigma Financial Modeling

## 1. Directory Structure
```
.
├── CMakeLists.txt
├── Dockerfile
├── README.md
├── include
│   ├── common.h
│   ├── data_generator.h
│   ├── environment.h
│   └── model.h
├── src
│   ├── data_generator.cpp
│   ├── environment.cpp
│   ├── main.cpp
│   └── model.cpp
└── tests
    └── test_solution.cpp
```

## 2. Instructions

### Build and Run Locally
1. Ensure you have CMake (>= 3.25) and a C++20/23/26 compatible compiler (e.g., GCC 14).
2. Create build directory:
   ```bash
   mkdir build && cd build
   ```
3. Configure and build:
   ```bash
   cmake ..
   make
   ```
4. Generate synthetic data:
   ```bash
   ./two-sigma generate-data --samples 1000 --output data/train.csv
   ```
5. Train the model:
   ```bash
   ./two-sigma train --data data/train.csv --model-path models/model.bin
   ```
6. Evaluate the model:
   ```bash
   ./two-sigma evaluate --data data/train.csv --model-path models/model.bin
   ```
7. Run tests:
   ```bash
   ./two-sigma-tests
   ```

### Build and Run via Docker
1. Build the image:
   ```bash
   docker build -t two-sigma-cpp .
   ```
2. Run a command (e.g., generate data):
   ```bash
   docker run -v $(pwd)/data:/app/data two-sigma-cpp generate-data --output data/train.csv
   ```

## 3. Solution Explanation
The C++ solution provides a high-performance implementation of Ridge Regression using the Eigen library.
- **Data Generator**: Produces CSV datasets with customizable dimensions.
- **Environment API**: Handles data loading and provides a step-wise interface for evaluation, splitting data into training and testing sets by timestamp.
- **Model Architecture**:
  - Implements Ridge Regression via the Normal Equations: $(X^T X + \alpha I) w = X^T y$.
  - Uses `Eigen::LDLT` decomposition for efficient and numerically stable solution.
  - Supports binary serialization for saving and loading model weights.

### Complexity Analysis
- **Time Complexity**:
  - Training: $O(N 	imes F^2 + F^3)$ for matrix multiplication and decomposition.
  - Prediction: $O(F)$ per sample (vector dot product).
- **Space Complexity**:
  - $O(F)$ for model weights.

### Architecture Diagram
```
[ CLI ] <--> [ FinancialModel ] <--> [ Environment ]
                   ^                       |
                   |                       v
            [ Eigen Algebra ] <--> [ Data (CSV) ]
```

## 4. UML Sequence Diagram
```
User -> CLI: run evaluate
CLI -> Model: load(path)
CLI -> Environment: Environment(path)
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
[Start] --> [Generate CSV Data] --> [Train Ridge Model]
                                         |
                                         v
[Finish] <-- [Calculate R-Score] <-- [Evaluate Steps]
```

## 6. Tabulated Summary
| Feature | Implementation |
|---------|----------------|
| Language | C++26 |
| Algebra | Eigen 3.4.0 |
| CLI | CLI11 |
| Build Tool | CMake |
| Testing | Google Test |
| Format | CSV |
