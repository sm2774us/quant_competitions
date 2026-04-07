"""Main execution engine for the Algothon 2026 portfolio strategy.

Orchestrates data loading, signal computation, portfolio optimisation,
and submission file generation. Designed for both backtesting and
live/round-by-round hackathon submission.

Usage:
    # CLI: python -m src.python.execution.engine --team myteam --round 1
    # Python:
    >>> engine = AlgothonEngine("data/sample", team_name="quant_hawks")
    >>> engine.run_backtest()
    >>> engine.generate_submission(round_number=1)

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl

# Internal imports — resolvable because:
#   • Bazel:  `imports = ["src/python"]` in py_binary/py_library propagates PYTHONPATH.
#   • Poetry: `packages = [{include = "data", from = "src/python"}, ...]` installs them
#             as top-level packages after `poetry install`.
# No sys.path manipulation required.
# # Internal imports
# _ROOT = Path(__file__).resolve().parents[3]
# sys.path.insert(0, str(_ROOT / "src" / "python"))

from data.loader import DataLoader, _INSTRUMENTS
from signals.momentum import MomentumEngine, MomentumSignals
from portfolio.optimizer import MVOOptimizer
from portfolio.risk import PerformanceAnalytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

_SUBMISSION_DIR: Final[Path] = Path("submissions")
_INSTRUMENTS_LIST: Final[list[str]] = _INSTRUMENTS


class AlgothonEngine:
    """End-to-end portfolio strategy engine for the Man Group Hackathon 2026.

    Integrates:
    1. Data ingestion (Polars-based DataLoader)
    2. Multi-scale momentum signal generation (TSMOM + XSMOM)
    3. Markowitz MVO with Ledoit-Wolf shrinkage
    4. Backtesting and performance evaluation
    5. Submission CSV generation

    Args:
        data_dir: Path to directory with CSV data files.
        team_name: Team name for submission file naming.
        risk_aversion: MVO risk-aversion lambda.
        blend_alpha: TSMOM/XSMOM blend (1.0 = pure TSMOM).

    Example:
        >>> engine = AlgothonEngine("data/sample", team_name="quant_hawks")
        >>> metrics = engine.run_backtest()
        >>> print(f"Sharpe: {metrics.sharpe:.3f}")
        >>> engine.generate_submission(round_number=1)
    """

    def __init__(
        self,
        data_dir: str | Path = "data/sample",
        team_name: str = "algothon_team",
        risk_aversion: float = 2.0,
        blend_alpha: float = 0.7,
        rebalance_freq: int = 5,
    ) -> None:
        """Initialise the execution engine.

        Args:
            data_dir: Data directory path.
            team_name: Submission team identifier.
            risk_aversion: Risk-aversion coefficient λ.
            blend_alpha: Signal blend parameter (0–1).
            rebalance_freq: Rebalancing frequency in trading days.
        """
        self._data_dir = Path(data_dir)
        self._team_name = team_name
        self._rebalance_freq = rebalance_freq

        # Component initialisation
        self._loader = DataLoader(self._data_dir)
        self._signal_engine = MomentumEngine(
            lookbacks=[4, 8, 16, 32],
            blend_alpha=blend_alpha,
        )
        self._optimizer = MVOOptimizer(
            risk_aversion=risk_aversion,
            lw_shrinkage=True,
            max_weight=0.40,
        )
        self._analytics = PerformanceAnalytics(risk_free_rate=0.05)

        # State
        self._dataset = None
        self._signals: MomentumSignals | None = None
        self._weights: np.ndarray | None = None
        self._latest_weights: np.ndarray | None = None

    # ------------------------------------------------------------------
    # Data & signal pipeline
    # ------------------------------------------------------------------

    def load_data(self) -> None:
        """Load and preprocess all data."""
        logger.info("Loading dataset from %s", self._data_dir)
        self._dataset = self._loader.load_all()
        logger.info(
            "Loaded %d rows, instruments: %s",
            self._dataset.prices.height,
            _INSTRUMENTS_LIST,
        )

    def compute_signals(self) -> None:
        """Compute momentum signals from loaded dataset."""
        if self._dataset is None:
            self.load_data()

        logger.info("Computing momentum signals...")
        self._signals = self._signal_engine.compute(
            returns_df=self._dataset.returns,
            precomputed_signals=self._dataset.signals,
        )
        logger.info("Signals computed. Shape: %s", self._signals.combined.shape)

    # ------------------------------------------------------------------
    # Backtesting
    # ------------------------------------------------------------------

    def run_backtest(
        self,
        train_end: str = "2024-12-31",
        test_start: str = "2025-01-01",
    ):
        """Run in-sample calibration + out-of-sample backtest.

        Args:
            train_end: End date for training period.
            test_start: Start date for out-of-sample evaluation.

        Returns:
            PerformanceMetrics for the out-of-sample period.
        """
        if self._signals is None:
            self.compute_signals()

        ret_mat = (
            self._dataset.returns.select(_INSTRUMENTS_LIST)
            .to_numpy()
            .astype(np.float64)
        )

        # Raw signal-implied weights
        raw_weights = self._signal_engine.signal_to_weights(
            self._signals, method="vol_parity", long_only=True
        )

        # MVO rolling optimisation
        logger.info("Running rolling MVO optimisation...")
        self._weights = self._optimizer.rolling_optimize(
            signal_weights=raw_weights,
            returns=ret_mat,
            rebalance_freq=self._rebalance_freq,
        )

        # Store latest weights
        self._latest_weights = self._weights[-1]

        # OOS performance
        dates = self._dataset.returns["date"].to_numpy()
        oos_mask = dates >= np.datetime64(test_start)
        oos_w = self._weights[oos_mask]
        oos_r = ret_mat[oos_mask]

        if len(oos_w) == 0:
            logger.warning("No OOS data found after %s", test_start)
            # Use full-sample metrics
            metrics = self._analytics.compute(self._weights, ret_mat)
        else:
            metrics = self._analytics.compute(oos_w, oos_r)

        logger.info(
            "OOS Results: Sharpe=%.3f | Ann.Ret=%.1f%% | Ann.Vol=%.1f%% | MaxDD=%.1f%%",
            metrics.sharpe,
            metrics.annualised_return * 100,
            metrics.annualised_vol * 100,
            metrics.max_drawdown * 100,
        )
        return metrics

    # ------------------------------------------------------------------
    # Submission generation
    # ------------------------------------------------------------------

    def compute_latest_weights(self) -> np.ndarray:
        """Compute weights for the most recent date in the dataset.

        Uses the last available signal and covariance to produce submission weights.

        Returns:
            (N,) normalised weight vector summing to 1.0, all >= 0.
        """
        if self._signals is None:
            self.compute_signals()

        ret_mat = (
            self._dataset.returns.select(_INSTRUMENTS_LIST)
            .to_numpy()
            .astype(np.float64)
        )

        # Latest signal
        latest_signal = self._signals.combined[-1]
        latest_vol = self._signals.ewm_vols[-1]

        # Vol-scaled expected return
        hist_vol = np.nanstd(ret_mat[-252:], axis=0) * np.sqrt(252)
        mu = np.maximum(latest_signal, 0.0) * hist_vol

        # Single-period MVO
        prev_w = self._latest_weights if self._latest_weights is not None else np.ones(10) / 10
        result = self._optimizer.optimize(mu, ret_mat[-252:], prev_w)
        self._latest_weights = result.weights

        logger.info("Latest weights: %s", dict(zip(_INSTRUMENTS_LIST, result.weights.round(4))))
        logger.info("Expected Sharpe: %.3f | Turnover: %.3f", result.sharpe, result.turnover)
        return result.weights

    def generate_submission(
        self,
        round_number: int = 1,
        output_dir: str | Path | None = None,
    ) -> Path:
        """Generate hackathon-compliant submission CSV.

        Creates a file named `{team_name}_round_{N}.csv` with columns
        `asset` and `weight`, weights summing to exactly 1.0.

        Args:
            round_number: Current hackathon round number.
            output_dir: Output directory (default: ./submissions).

        Returns:
            Path to the generated CSV file.

        Raises:
            ValueError: If weights do not satisfy constraints.
        """
        weights = self.compute_latest_weights()

        # Validate constraints
        if abs(weights.sum() - 1.0) > 1e-6:
            logger.warning("Weights sum to %.6f; renormalising", weights.sum())
            weights /= weights.sum()
        if np.any(weights < -1e-8):
            raise ValueError(f"Negative weights detected: {weights}")

        # Round to 4 decimal places but maintain sum = 1, no negatives
        weights = weights.round(4)
        weights = np.maximum(weights, 0.0)
        weights[-1] += 1.0 - weights.sum()  # fix rounding residual on last asset
        weights = np.maximum(weights, 0.0)
        weights /= weights.sum()

        out_dir = Path(output_dir) if output_dir else _SUBMISSION_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = out_dir / f"{self._team_name}_round_{round_number}.csv"
        submission_df = pl.DataFrame({
            "asset": _INSTRUMENTS_LIST,
            "weight": weights.tolist(),
        })
        submission_df.write_csv(filename)

        logger.info("Submission written to %s", filename)
        logger.info("\n%s", submission_df)
        return filename


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Algothon 2026 Strategy Engine")
    p.add_argument("--data-dir", default="data/sample", help="Path to CSV data directory")
    p.add_argument("--team", default="algothon_team", help="Team name")
    p.add_argument("--round", type=int, default=1, help="Hackathon round number")
    p.add_argument("--risk-aversion", type=float, default=2.0, help="MVO risk aversion λ")
    p.add_argument("--blend-alpha", type=float, default=0.7, help="TSMOM/XSMOM blend")
    p.add_argument("--backtest", action="store_true", help="Run full backtest")
    p.add_argument("--output-dir", default="submissions", help="Submission output directory")
    return p.parse_args()


def main() -> int:
    """CLI entry point for the strategy engine.

    Returns:
        Exit code (0 = success).
    """
    args = _parse_args()

    engine = AlgothonEngine(
        data_dir=args.data_dir,
        team_name=args.team,
        risk_aversion=args.risk_aversion,
        blend_alpha=args.blend_alpha,
    )

    if args.backtest:
        metrics = engine.run_backtest()
        print(f"\n{'=' * 50}")
        print(f"OUT-OF-SAMPLE PERFORMANCE SUMMARY")
        print(f"{'=' * 50}")
        print(f"  Sharpe Ratio     : {metrics.sharpe:.4f}")
        print(f"  Annualised Return: {metrics.annualised_return * 100:.2f}%")
        print(f"  Annualised Vol   : {metrics.annualised_vol * 100:.2f}%")
        print(f"  Max Drawdown     : {metrics.max_drawdown * 100:.2f}%")
        print(f"  Sortino Ratio    : {metrics.sortino:.4f}")
        print(f"  Hit Rate         : {metrics.hit_rate * 100:.1f}%")
        print(f"  CVaR(95%)        : {metrics.cvar_95 * 100:.2f}%")
        print(f"{'=' * 50}")

    path = engine.generate_submission(
        round_number=args.round,
        output_dir=args.output_dir,
    )
    print(f"\nSubmission: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
