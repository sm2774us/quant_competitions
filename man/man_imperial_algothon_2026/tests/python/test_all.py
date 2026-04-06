"""Python unit tests for the Algothon 2026 data loader, signals, and optimizer.

Tests are designed to be fast, deterministic, and self-contained.
They do not require network access or GPU hardware.

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import polars as pl
import pytest

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src" / "python"))

from data.loader import DataLoader, AlgothonDataset, _INSTRUMENTS
from signals.momentum import MomentumEngine, MomentumSignals
from portfolio.optimizer import MVOOptimizer
from portfolio.risk import PerformanceAnalytics

_DATA_DIR = _ROOT / "data" / "sample"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def dataset() -> AlgothonDataset:
    loader = DataLoader(_DATA_DIR)
    return loader.load_all()


@pytest.fixture(scope="module")
def signals(dataset: AlgothonDataset) -> MomentumSignals:
    engine = MomentumEngine(lookbacks=[4, 8, 16, 32])
    return engine.compute(dataset.returns, dataset.signals)


@pytest.fixture(scope="module")
def small_returns() -> np.ndarray:
    """Small synthetic return matrix for fast optimizer tests."""
    rng = np.random.default_rng(42)
    return rng.normal(0.0005, 0.01, size=(300, 10))


# ============================================================================
# DataLoader tests
# ============================================================================

class TestDataLoader:
    def test_raises_on_missing_dir(self):
        with pytest.raises(FileNotFoundError):
            DataLoader("/nonexistent/path")

    def test_prices_shape(self, dataset: AlgothonDataset):
        assert dataset.prices.height > 0
        assert set(_INSTRUMENTS).issubset(set(dataset.prices.columns))

    def test_prices_no_nulls(self, dataset: AlgothonDataset):
        null_counts = dataset.prices.select(_INSTRUMENTS).null_count().row(0)
        assert all(v == 0 for v in null_counts), "Prices contain nulls"

    def test_returns_finite(self, dataset: AlgothonDataset):
        ret_mat = dataset.returns.select(_INSTRUMENTS).to_numpy()
        assert np.all(np.isfinite(ret_mat)), "Returns contain non-finite values"

    def test_returns_reasonable_magnitude(self, dataset: AlgothonDataset):
        ret_mat = dataset.returns.select(_INSTRUMENTS).to_numpy()
        daily_std = np.nanstd(ret_mat, axis=0)
        assert np.all(daily_std < 0.20), "Daily vol > 20% — data anomaly"
        assert np.all(daily_std > 1e-6), "Zero-variance instrument detected"

    def test_signals_columns(self, dataset: AlgothonDataset):
        for inst in _INSTRUMENTS:
            for lb in [4, 8, 16, 32]:
                col = f"{inst}_trend{lb}"
                assert col in dataset.signals.columns, f"Missing signal column: {col}"

    def test_date_alignment(self, dataset: AlgothonDataset):
        prices_dates = set(dataset.prices["date"].to_list())
        returns_dates = set(dataset.returns["date"].to_list())
        signals_dates = set(dataset.signals["date"].to_list())
        assert returns_dates.issubset(prices_dates)
        assert signals_dates == prices_dates

    def test_get_aligned_slice(self, dataset: AlgothonDataset):
        sliced = dataset.get_aligned_slice("2023-01-01", "2024-01-01")
        assert sliced.prices.height > 0
        min_date = sliced.prices["date"].min()
        max_date = sliced.prices["date"].max()
        import datetime
        assert min_date >= datetime.date(2023, 1, 1)
        assert max_date <= datetime.date(2024, 1, 1)


# ============================================================================
# MomentumEngine tests
# ============================================================================

class TestMomentumEngine:
    def test_signal_shape(self, signals: MomentumSignals, dataset: AlgothonDataset):
        T = dataset.returns.height
        assert signals.combined.shape == (T, 10)
        assert signals.tsmom.shape == (T, 10)
        assert signals.xsmom.shape == (T, 10)

    def test_signal_finite_after_warmup(self, signals: MomentumSignals):
        # After warmup period (32 days), signals should be finite
        warmup = 40
        post = signals.combined[warmup:]
        assert np.all(np.isfinite(post)), "Non-finite signals after warmup"

    def test_signal_to_weights_sum_one(self, signals: MomentumSignals):
        engine = MomentumEngine()
        weights = engine.signal_to_weights(signals, method="vol_parity", long_only=True)
        row_sums = weights.sum(axis=1)
        assert np.allclose(row_sums, 1.0, atol=1e-6), "Weights do not sum to 1"

    def test_signal_to_weights_non_negative(self, signals: MomentumSignals):
        engine = MomentumEngine()
        weights = engine.signal_to_weights(signals, method="vol_parity", long_only=True)
        assert np.all(weights >= -1e-9), "Negative weights in long-only mode"

    def test_signal_to_weights_equal_method(self, signals: MomentumSignals):
        engine = MomentumEngine()
        weights = engine.signal_to_weights(signals, method="equal", long_only=True)
        # Equal-weighted: each nonzero weight should be 1/K
        row = weights[50]  # after warmup
        nonzero = row[row > 1e-9]
        if len(nonzero) > 1:
            assert np.allclose(nonzero, nonzero[0], atol=1e-6)

    def test_blend_alpha_pure_tsmom(self, dataset: AlgothonDataset):
        engine = MomentumEngine(blend_alpha=1.0)
        sigs = engine.compute(dataset.returns)
        assert np.allclose(sigs.combined[100:], sigs.tsmom[100:], atol=1e-9)

    def test_blend_alpha_pure_xsmom(self, dataset: AlgothonDataset):
        engine = MomentumEngine(blend_alpha=0.0)
        sigs = engine.compute(dataset.returns)
        assert np.allclose(sigs.combined[100:], sigs.xsmom[100:], atol=1e-9)


# ============================================================================
# MVOOptimizer tests
# ============================================================================

class TestMVOOptimizer:
    def test_weights_sum_to_one(self, small_returns: np.ndarray):
        opt = MVOOptimizer(risk_aversion=2.0, lw_shrinkage=True)
        mu = np.ones(10) * 0.05
        result = opt.optimize(mu, small_returns)
        assert abs(result.weights.sum() - 1.0) < 1e-5

    def test_weights_non_negative(self, small_returns: np.ndarray):
        opt = MVOOptimizer()
        mu = np.ones(10) * 0.05
        result = opt.optimize(mu, small_returns)
        assert np.all(result.weights >= -1e-6)

    def test_weights_respect_max_weight(self, small_returns: np.ndarray):
        opt = MVOOptimizer(max_weight=0.3)
        mu = np.array([0.2] + [0.01] * 9)  # One dominant asset
        result = opt.optimize(mu, small_returns)
        assert np.all(result.weights <= 0.3 + 1e-5)

    def test_sharpe_positive_with_good_mu(self, small_returns: np.ndarray):
        opt = MVOOptimizer()
        mu = np.ones(10) * 0.10  # Strongly positive expected returns
        result = opt.optimize(mu, small_returns)
        assert result.sharpe > 0.0

    def test_covariance_pd(self, small_returns: np.ndarray):
        opt = MVOOptimizer(lw_shrinkage=True)
        cov = opt.estimate_covariance(small_returns)
        eigvals = np.linalg.eigvalsh(cov)
        assert eigvals.min() > 0.0, "Covariance is not positive definite"

    def test_risk_parity_fallback(self):
        """Risk-parity fallback produces valid weights."""
        opt = MVOOptimizer()
        rng = np.random.default_rng(0)
        cov = rng.random((10, 10))
        cov = cov @ cov.T + np.eye(10) * 0.01  # PD
        w = opt._risk_parity_weights(cov)
        assert abs(w.sum() - 1.0) < 1e-5
        assert np.all(w >= 0)

    def test_rolling_optimize_shape(self, small_returns: np.ndarray):
        opt = MVOOptimizer()
        signals = np.abs(np.random.default_rng(7).normal(0, 1, (300, 10)))
        signals /= signals.sum(axis=1, keepdims=True)
        weights = opt.rolling_optimize(signals, small_returns, rebalance_freq=5, warmup=63)
        assert weights.shape == (300, 10)

    def test_rolling_optimize_row_sums(self, small_returns: np.ndarray):
        opt = MVOOptimizer()
        rng = np.random.default_rng(9)
        signals = np.abs(rng.normal(0, 1, (300, 10)))
        signals /= signals.sum(axis=1, keepdims=True)
        weights = opt.rolling_optimize(signals, small_returns, warmup=63)
        assert np.allclose(weights.sum(axis=1), 1.0, atol=1e-5)


# ============================================================================
# PerformanceAnalytics tests
# ============================================================================

class TestPerformanceAnalytics:
    def test_sharpe_positive_trending(self):
        pa = PerformanceAnalytics(risk_free_rate=0.0)
        rng = np.random.default_rng(42)
        # Strongly positive daily returns
        returns = rng.normal(0.002, 0.01, (252, 10))
        weights = np.ones((252, 10)) / 10
        metrics = pa.compute(weights, returns)
        assert metrics.sharpe > 0.0

    def test_max_drawdown_non_negative(self):
        pa = PerformanceAnalytics()
        rng = np.random.default_rng(1)
        returns = rng.normal(0, 0.01, (500, 10))
        weights = np.ones((500, 10)) / 10
        metrics = pa.compute(weights, returns)
        assert metrics.max_drawdown >= 0.0

    def test_cumulative_returns_starts_near_one(self):
        pa = PerformanceAnalytics()
        rng = np.random.default_rng(2)
        returns = rng.normal(0, 0.01, (100, 10))
        weights = np.ones((100, 10)) / 10
        metrics = pa.compute(weights, returns)
        assert abs(metrics.cumulative_returns[0] - 1.0) < 0.05

    def test_rolling_sharpe_length(self):
        pa = PerformanceAnalytics()
        rng = np.random.default_rng(3)
        returns = rng.normal(0, 0.01, (300, 10))
        weights = np.ones((300, 10)) / 10
        rs = pa.rolling_sharpe(weights, returns, window=100)
        assert len(rs) == 300
        # First 100 values should be NaN
        assert np.all(np.isnan(rs[:100]))

    def test_hit_rate_in_range(self):
        pa = PerformanceAnalytics()
        rng = np.random.default_rng(4)
        returns = rng.normal(0.001, 0.01, (500, 10))
        weights = np.ones((500, 10)) / 10
        metrics = pa.compute(weights, returns)
        assert 0.0 <= metrics.hit_rate <= 1.0
