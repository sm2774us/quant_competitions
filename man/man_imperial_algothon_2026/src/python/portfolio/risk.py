"""Portfolio risk metrics and performance analytics.

Implements standard and advanced performance measures used in quantitative finance:
Sharpe ratio, Sortino ratio, Calmar ratio, maximum drawdown, CVaR, and
rolling attribution analysis.

Usage:
    >>> analytics = PerformanceAnalytics(risk_free_rate=0.05)
    >>> metrics = analytics.compute(weights, returns)
    >>> print(metrics.sharpe, metrics.max_drawdown)

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

import numpy as np
import polars as pl

logger = logging.getLogger(__name__)

_TRADING_DAYS: Final[int] = 252


@dataclass(slots=True, frozen=True)
class PerformanceMetrics:
    """Full set of portfolio performance metrics.

    Attributes:
        sharpe: Annualised Sharpe ratio (return / vol * sqrt(252)).
        sortino: Annualised Sortino ratio (return / downside-vol).
        calmar: Annualised return / maximum drawdown.
        max_drawdown: Maximum peak-to-trough drawdown (positive number).
        annualised_return: CAGR of portfolio.
        annualised_vol: Annualised standard deviation of returns.
        cvar_95: Conditional Value-at-Risk at 95% confidence.
        hit_rate: Fraction of positive return days.
        avg_turnover: Mean daily L1 portfolio turnover.
        portfolio_returns: (T,) daily portfolio log-returns.
        cumulative_returns: (T,) cumulative wealth index.
        drawdowns: (T,) drawdown series.
    """

    sharpe: float
    sortino: float
    calmar: float
    max_drawdown: float
    annualised_return: float
    annualised_vol: float
    cvar_95: float
    hit_rate: float
    avg_turnover: float
    portfolio_returns: np.ndarray
    cumulative_returns: np.ndarray
    drawdowns: np.ndarray


class PerformanceAnalytics:
    """Computes comprehensive portfolio performance metrics.

    Args:
        risk_free_rate: Annual risk-free rate (default 0.05 = 5%).
        trading_days: Number of trading days per year (default 252).

    Example:
        >>> pa = PerformanceAnalytics(risk_free_rate=0.05)
        >>> metrics = pa.compute(weights_matrix, returns_matrix)
    """

    def __init__(
        self,
        risk_free_rate: float = 0.05,
        trading_days: int = _TRADING_DAYS,
    ) -> None:
        """Initialise analytics engine.

        Args:
            risk_free_rate: Annual risk-free rate used in Sharpe computation.
            trading_days: Trading calendar days per annum.
        """
        self._rfr_daily = risk_free_rate / trading_days
        self._ann_factor = trading_days
        self._sqrt_ann = np.sqrt(trading_days)

    # ------------------------------------------------------------------
    # Core computations
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_drawdowns(cumret: np.ndarray) -> np.ndarray:
        """Compute drawdown series from cumulative returns.

        Args:
            cumret: (T,) cumulative wealth index (starting from 1.0).

        Returns:
            (T,) drawdown series (negative or zero values).
        """
        rolling_max = np.maximum.accumulate(cumret)
        return (cumret - rolling_max) / rolling_max

    def _sortino(self, daily_excess: np.ndarray) -> float:
        """Compute annualised Sortino ratio.

        Args:
            daily_excess: (T,) daily excess returns over risk-free rate.

        Returns:
            Annualised Sortino ratio.
        """
        downside = daily_excess[daily_excess < 0]
        if len(downside) == 0:
            return np.inf
        downside_vol = np.sqrt(np.mean(downside ** 2)) * self._sqrt_ann
        return float(np.mean(daily_excess) * self._ann_factor / (downside_vol + 1e-10))

    def _cvar(self, returns: np.ndarray, confidence: float = 0.95) -> float:
        """Compute Conditional Value-at-Risk (Expected Shortfall).

        Args:
            returns: (T,) daily portfolio returns.
            confidence: Confidence level (default 0.95).

        Returns:
            CVaR (positive number representing expected loss in tail).
        """
        var_threshold = np.percentile(returns, (1 - confidence) * 100)
        tail = returns[returns <= var_threshold]
        return float(-np.mean(tail)) if len(tail) > 0 else 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(
        self,
        weights: np.ndarray,
        returns: np.ndarray,
    ) -> PerformanceMetrics:
        """Compute all performance metrics for a given weights/returns series.

        Args:
            weights: (T, N) portfolio weight matrix.
            returns: (T, N) log-return matrix (aligned with weights).

        Returns:
            PerformanceMetrics dataclass with all computed statistics.
        """
        # Portfolio daily returns
        port_ret = np.sum(weights * returns, axis=1)
        excess_ret = port_ret - self._rfr_daily

        # Cumulative returns
        cum_ret = np.exp(np.cumsum(port_ret))
        drawdowns = self._compute_drawdowns(cum_ret)
        max_dd = float(-drawdowns.min())

        # Annualised statistics
        ann_ret = float(np.mean(port_ret) * self._ann_factor)
        ann_vol = float(np.std(port_ret) * self._sqrt_ann)
        sharpe = float(np.mean(excess_ret) / (np.std(port_ret) + 1e-10) * self._sqrt_ann)
        sortino = self._sortino(excess_ret)
        calmar = ann_ret / (max_dd + 1e-10)

        # Risk measures
        cvar = self._cvar(port_ret)
        hit_rate = float(np.mean(port_ret > 0))

        # Turnover
        if weights.shape[0] > 1:
            daily_turnover = np.mean(np.sum(np.abs(np.diff(weights, axis=0)), axis=1))
        else:
            daily_turnover = 0.0

        return PerformanceMetrics(
            sharpe=sharpe,
            sortino=sortino,
            calmar=calmar,
            max_drawdown=max_dd,
            annualised_return=ann_ret,
            annualised_vol=ann_vol,
            cvar_95=cvar,
            hit_rate=hit_rate,
            avg_turnover=float(daily_turnover),
            portfolio_returns=port_ret,
            cumulative_returns=cum_ret,
            drawdowns=drawdowns,
        )

    def rolling_sharpe(
        self, weights: np.ndarray, returns: np.ndarray, window: int = 252
    ) -> np.ndarray:
        """Compute rolling Sharpe ratio over a sliding window.

        Args:
            weights: (T, N) weight matrix.
            returns: (T, N) return matrix.
            window: Rolling window in days.

        Returns:
            (T,) rolling Sharpe series (NaN for t < window).
        """
        port_ret = np.sum(weights * returns, axis=1)
        T = len(port_ret)
        rolling = np.full(T, np.nan)
        for t in range(window, T):
            r = port_ret[t - window : t]
            mu = np.mean(r) - self._rfr_daily
            sigma = np.std(r)
            rolling[t] = mu / (sigma + 1e-10) * self._sqrt_ann
        return rolling

    def to_polars(
        self, metrics: PerformanceMetrics, dates: np.ndarray
    ) -> pl.DataFrame:
        """Convert time-series metrics to a Polars DataFrame.

        Args:
            metrics: PerformanceMetrics instance.
            dates: (T,) array of date objects.

        Returns:
            Polars DataFrame with date, portfolio_return, cumulative_return, drawdown.
        """
        return pl.DataFrame({
            "date": dates,
            "portfolio_return": metrics.portfolio_returns,
            "cumulative_return": metrics.cumulative_returns,
            "drawdown": metrics.drawdowns,
        })
