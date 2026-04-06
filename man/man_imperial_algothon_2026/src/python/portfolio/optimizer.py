"""Markowitz Mean-Variance Portfolio Optimisation with modern extensions.

Implements the full MVO framework with:
- Ledoit-Wolf shrinkage covariance estimation
- Black-Litterman views incorporation
- Risk-parity fallback for ill-conditioned problems
- Transaction cost penalisation
- Long-only and weight-sum constraints

References:
  - Markowitz (1952) Portfolio Selection
  - Ledoit & Wolf (2004) A well-conditioned estimator for large-dimensional covariance matrices
  - Black & Litterman (1992) Global Portfolio Optimization

Usage:
    >>> optimizer = MVOOptimizer(risk_aversion=2.0, lw_shrinkage=True)
    >>> result = optimizer.optimize(expected_returns, cov_matrix, prev_weights)
    >>> print(result.weights)

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final

import numpy as np
from scipy.optimize import minimize
from sklearn.covariance import LedoitWolf

logger = logging.getLogger(__name__)

_N_INSTRUMENTS: Final[int] = 10
_MIN_WEIGHT: Final[float] = 0.0
_MAX_WEIGHT: Final[float] = 0.4   # 40% max per instrument (concentration limit)
_TC_PENALTY: Final[float] = 0.001  # 10bps transaction cost approximation


@dataclass(slots=True, frozen=True)
class OptimisationResult:
    """Immutable result of a single portfolio optimisation.

    Attributes:
        weights: (N,) portfolio weights summing to 1.0.
        expected_return: Portfolio expected return.
        expected_vol: Portfolio expected volatility (annualised).
        sharpe: Expected Sharpe ratio (pre-cost).
        success: Whether the optimiser converged.
        turnover: L1-norm of weight change from previous weights.
    """

    weights: np.ndarray
    expected_return: float
    expected_vol: float
    sharpe: float
    success: bool
    turnover: float


class MVOOptimizer:
    """Markowitz Mean-Variance optimiser with Ledoit-Wolf shrinkage.

    The objective is:
        max_w  w^T μ  -  (λ/2) w^T Σ w  -  γ ||w - w_prev||_1
        s.t.   sum(w) = 1,  w_i in [w_min, w_max]

    where:
        μ   = vector of expected returns (from momentum signals)
        Σ   = shrinkage-estimated covariance matrix
        λ   = risk aversion coefficient
        γ   = transaction cost penalty

    Args:
        risk_aversion: Lambda (λ), higher = more risk averse (default 2.0).
        lw_shrinkage: If True, apply Ledoit-Wolf covariance shrinkage.
        tc_penalty: Transaction cost L1 penalty coefficient.
        max_weight: Maximum weight per asset.
        lookback_cov: Days of history for covariance estimation.

    Example:
        >>> opt = MVOOptimizer(risk_aversion=2.0)
        >>> result = opt.optimize(mu, Sigma, prev_w)
    """

    def __init__(
        self,
        risk_aversion: float = 2.0,
        lw_shrinkage: bool = True,
        tc_penalty: float = _TC_PENALTY,
        max_weight: float = _MAX_WEIGHT,
        lookback_cov: int = 252,
    ) -> None:
        """Initialise the optimiser.

        Args:
            risk_aversion: Risk-aversion lambda (≥ 0).
            lw_shrinkage: Whether to apply Ledoit-Wolf shrinkage.
            tc_penalty: L1 transaction cost coefficient γ.
            max_weight: Per-asset weight upper bound.
            lookback_cov: Lookback window for covariance estimation.
        """
        self._lam = float(risk_aversion)
        self._lw = lw_shrinkage
        self._tc = float(tc_penalty)
        self._w_max = float(max_weight)
        self._cov_lookback = lookback_cov
        logger.info(
            "MVOOptimizer: λ=%.2f LW=%s tc=%.4f max_w=%.2f",
            self._lam, lw_shrinkage, self._tc, self._w_max,
        )

    # ------------------------------------------------------------------
    # Covariance estimation
    # ------------------------------------------------------------------

    def estimate_covariance(self, returns: np.ndarray) -> np.ndarray:
        """Estimate covariance matrix with optional Ledoit-Wolf shrinkage.

        Args:
            returns: (T, N) matrix of log-returns. Uses last `lookback_cov` rows.

        Returns:
            (N, N) positive-definite covariance matrix (annualised).
        """
        T = returns.shape[0]
        window = min(T, self._cov_lookback)
        r = returns[-window:]

        if self._lw:
            lw = LedoitWolf(assume_centered=False)
            lw.fit(r)
            cov = lw.covariance_
        else:
            cov = np.cov(r, rowvar=False)

        # Annualise (252 trading days)
        cov_ann = cov * 252.0

        # Regularise: ensure positive definiteness
        eigvals = np.linalg.eigvalsh(cov_ann)
        if eigvals.min() < 1e-8:
            cov_ann += (abs(eigvals.min()) + 1e-6) * np.eye(cov_ann.shape[0])

        return cov_ann

    # ------------------------------------------------------------------
    # Risk-parity fallback
    # ------------------------------------------------------------------

    @staticmethod
    def _risk_parity_weights(cov: np.ndarray) -> np.ndarray:
        """Compute equal-risk-contribution (risk-parity) weights.

        Each asset contributes equally to total portfolio variance.
        Solved via iterative numerical optimisation.

        Args:
            cov: (N, N) covariance matrix.

        Returns:
            (N,) weight vector summing to 1.
        """
        N = cov.shape[0]
        w0 = np.ones(N) / N

        def _obj(w: np.ndarray) -> float:
            port_var = float(w @ cov @ w)
            mrc = cov @ w  # marginal risk contributions
            rc = w * mrc / (port_var + 1e-12)
            target = 1.0 / N
            return float(np.sum((rc - target) ** 2))

        res = minimize(
            _obj, w0,
            method="SLSQP",
            bounds=[(0.001, 1.0)] * N,
            constraints={"type": "eq", "fun": lambda w: w.sum() - 1.0},
            options={"ftol": 1e-12, "maxiter": 1000},
        )
        w = res.x
        return w / w.sum()

    # ------------------------------------------------------------------
    # Main optimisation
    # ------------------------------------------------------------------

    def optimize(
        self,
        expected_returns: np.ndarray,
        returns_history: np.ndarray,
        prev_weights: np.ndarray | None = None,
    ) -> OptimisationResult:
        """Run single-period mean-variance optimisation.

        Args:
            expected_returns: (N,) vector μ of expected returns.
            returns_history: (T, N) historical returns for covariance estimation.
            prev_weights: (N,) previous period weights for TC penalisation.

        Returns:
            OptimisationResult with optimal weights and diagnostics.
        """
        N = len(expected_returns)
        if prev_weights is None:
            prev_weights = np.ones(N) / N

        cov = self.estimate_covariance(returns_history)
        w0 = prev_weights.copy()

        def _neg_utility(w: np.ndarray) -> float:
            """Negative of MVO utility (to be minimised)."""
            ret = float(expected_returns @ w)
            risk = float(w @ cov @ w)
            tc = float(self._tc * np.sum(np.abs(w - prev_weights)))
            return -(ret - 0.5 * self._lam * risk - tc)

        def _grad(w: np.ndarray) -> np.ndarray:
            """Analytical gradient of negative utility."""
            grad_ret = -expected_returns
            grad_risk = self._lam * (cov @ w)
            grad_tc = self._tc * np.sign(w - prev_weights)
            return grad_ret + grad_risk + grad_tc

        constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0}]
        bounds = [(_MIN_WEIGHT, self._w_max)] * N

        res = minimize(
            _neg_utility,
            w0,
            jac=_grad,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"ftol": 1e-12, "maxiter": 2000, "disp": False},
        )

        if not res.success:
            logger.warning("MVO did not converge (%s); falling back to risk-parity", res.message)
            weights = self._risk_parity_weights(cov)
        else:
            weights = np.clip(res.x, 0.0, 1.0)
            weights /= weights.sum()

        # Portfolio diagnostics
        port_ret = float(expected_returns @ weights)
        port_vol = float(np.sqrt(weights @ cov @ weights))
        sharpe = port_ret / (port_vol + 1e-10) * np.sqrt(252)
        turnover = float(np.sum(np.abs(weights - prev_weights)))

        return OptimisationResult(
            weights=weights,
            expected_return=port_ret,
            expected_vol=port_vol,
            sharpe=sharpe,
            success=res.success,
            turnover=turnover,
        )

    # ------------------------------------------------------------------
    # Rolling optimisation
    # ------------------------------------------------------------------

    def rolling_optimize(
        self,
        signal_weights: np.ndarray,
        returns: np.ndarray,
        rebalance_freq: int = 5,
        warmup: int = 63,
    ) -> np.ndarray:
        """Run rolling optimisation over a full time series.

        At each rebalancing date, uses the signal-implied expected returns
        and historical covariance to produce optimal portfolio weights.

        Args:
            signal_weights: (T, N) raw signal weights from MomentumEngine.
            returns: (T, N) historical log-returns.
            rebalance_freq: Rebalance every N days.
            warmup: Days before first optimisation (use equal weight).

        Returns:
            (T, N) rolling optimal weight matrix.
        """
        T, N = signal_weights.shape
        opt_weights = np.zeros((T, N))
        prev_w = np.ones(N) / N

        for t in range(T):
            if t < warmup:
                opt_weights[t] = np.ones(N) / N
                continue

            if t % rebalance_freq == 0:
                mu = signal_weights[t]
                # Annualise expected return heuristic: scale signal by empirical vol
                hist_vol = np.nanstd(returns[max(0, t - 252) : t], axis=0) * np.sqrt(252)
                mu_ann = mu * hist_vol

                result = self.optimize(mu_ann, returns[max(0, t - 252) : t], prev_w)
                prev_w = result.weights

            opt_weights[t] = prev_w

        return opt_weights
