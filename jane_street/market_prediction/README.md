# Jane Street Market Prediction Challenge

## 1. Challenge Overview
The Jane Street Market Prediction challenge requires developing a quantitative trading strategy that can decide, in real-time, whether to execute or pass on a given trade opportunity. The primary objective is to maximize a "Utility Score" that balances total profit with the stability of returns over time.

### 1.1 The Dataset
- **Features**: 130 anonymized continuous features (feature_0 to feature_129).
- **Metadata**: `date` (day of the trade), `weight` (relative importance), and `ts_id` (time-ordered ID).
- **Targets**: `resp` (return of the trade) and subsidiary returns `resp_1` through `resp_4` representing different time horizons.
- **Constraints**: Features are anonymized, and their relationships with the target are non-stationary and highly noisy.

### 1.2 Evaluation Metric: Utility Score
For each date $i$, the daily profit $p_i$ is defined as:
$$p_i = \sum_j (weight_{ij} \times resp_{ij} \times action_{ij})$$
where $j$ represents the $j$-th trade opportunity of the day.

The overall score is calculated as:
$$t = \frac{\sum p_i}{\sqrt{\sum p_i^2}} \times \sqrt{\frac{250}{|i|}}$$
$$Utility = \min(\max(t, 0), 6) \times \sum p_i$$
where $|i|$ is the number of unique dates. This metric penalizes volatile returns and encourages consistent daily performance.

### 1.3 Key Technical Challenges
- **Real-time Latency**: Inference must be extremely fast (approx. 16ms per trade).
- **Regime Shifts**: Market conditions change, requiring robust generalization or adaptive models.
- **Missing Data**: Features may have missing values that require efficient imputation.
- **Signal-to-Noise**: Financial data is notoriously noisy; avoiding overfitting is critical.

## 2. Solution Requirements
This repository provides highly optimized, production-grade implementations in three languages:
- **Python 3.13**: Using Poetry, focusing on vectorization and modern OOP patterns.
- **C++26**: Using CMake, focusing on low-latency execution and memory safety.
- **Rust 1.93.1**: Using Cargo, focusing on zero-cost abstractions and safety.

All solutions include:
- 100% Unit Test Coverage.
- Dockerized environments.
- Performance-optimized inference engines.
- Comprehensive documentation and architectural diagrams.

---
*For detailed implementation details, please refer to the [SOLUTIONS.md](./SOLUTIONS.md) and individual language directories.*
