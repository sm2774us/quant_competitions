# Two Sigma: Using News to Predict Stock Movements

## The Challenge
The goal of this challenge is to predict the 10-day market-residualized returns of various stocks using both historical market data and sentiment-indexed news data. This is a classic financial forecasting problem where the objective is to find signals in news data that aren't already priced in by the market.

### Objective
For each asset on each day, predict a signed confidence value $C \in [-1, 1]$.
- A value of $1$ indicates high confidence that the 10-day market-residualized return will be positive.
- A value of $-1$ indicates high confidence that it will be negative.
- A value of $0$ indicates no confidence or no predicted movement.

### Data Description
1. **Market Data (2007 - Present)**:
    - `time`: Current time (all rows taken at 22:00 UTC).
    - `assetCode`: Unique identifier for an asset.
    - `assetName`: Human-readable name of the asset.
    - `universe`: Binary flag indicating if the asset is in the scoring universe on that day.
    - `volume`: Daily trading volume.
    - `close`/`open`: Unadjusted close/open prices.
    - `returnsOpenNextMktres10`: **Target variable**. 10-day market-residualized return.
    - Various other return features (1-day, 10-day, raw, and market-residualized).

2. **News Data (2007 - Present)**:
    - `time`: UTC timestamp of article publication.
    - `assetCodes`: Set of assets mentioned in the article.
    - `sentimentNegative`/`Neutral`/`Positive`: Sentiment scores from automated analysis.
    - `relevance`: Score indicating how relevant the article is to the asset.
    - `noveltyCount`: Frequency of similar news in recent history.
    - `wordCount`: Length of the article.

### Evaluation Metric
The submission is evaluated on a score calculated by:
$$ Score = \frac{\mu}{\sigma} $$
Where:
- $x_t = \sum_i C_{i,t} \cdot R_{i,t} \cdot U_{i,t}$ (Daily weighted return)
- $\mu = \text{mean}(x_t)$
- $\sigma = \text{std}(x_t)$
- $C_{i,t}$: Your predicted confidence.
- $R_{i,t}$: 10-day market-residualized return for asset $i$.
- $U_{i,t}$: Binary universe flag.

## Solutions Overview
This repository provides robust, time-efficient, and vector-optimized implementations in three languages:

- [**Python Solution**](./python): 3.13, Poetry, OOP, Click CLI, 100% Pytest coverage.
- [**C++ Solution**](./cpp): C++26, CMake, OOP, Modern CLI, 100% GTest coverage.
- [**Rust Solution**](./rust): 1.85+, Cargo, OOP, Modern CLI, 100% Test coverage.

All solutions are integrated via **Bazel** for unified building, testing, and Dockerization.

## Getting Started
See [SOLUTIONS.md](./SOLUTIONS.md) for a summary of all implementations and Bazel instructions.
