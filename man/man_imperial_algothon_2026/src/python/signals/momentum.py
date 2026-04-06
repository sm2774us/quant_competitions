"""Multi-scale momentum signal generation for trend-following strategies.

Implements time-series momentum (TSMOM) and cross-sectional momentum (XSMOM)
as described in Moskowitz, Ooi & Pedersen (2012) and Lempérière et al. (2014),
with vol-normalised signal combination across lookback horizons.

Usage:
    >>> engine = MomentumEngine(lookbacks=[4, 8, 16, 32])
    >>> signals = engine.compute(returns_df, prices_df)
    >>> weights = engine.signal_to_weights(signals, method="vol_parity")

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

import numpy as np
import polars as pl
from scipy.stats import rankdata

logger = logging.getLogger(__name__)

_INSTRUMENTS: list[str] = [f"INSTRUMENT_{i}" for i in range(1, 11)]
_EWM_SPAN_SHORT: int = 20   # ~1 month vol estimation
_EWM_SPAN_LONG: int = 60    # ~3 month vol estimation


@dataclass(slots=True)
class MomentumSignals:
    """Container for computed momentum signals.

    Attributes:
        tsmom: Time-series momentum matrix (T x N), vol-normalised.
        xsmom: Cross-sectional momentum z-scores (T x N).
        combined: Blended signal (T x N).
        dates: Array of datetime.date values.
        instruments: List of instrument names.
        ewm_vols: Exponentially-weighted volatility estimates (T x N).
    """

    tsmom: np.ndarray       # (T, N) float64
    xsmom: np.ndarray       # (T, N) float64
    combined: np.ndarray    # (T, N) float64
    dates: np.ndarray       # (T,) object (date)
    instruments: list[str]
    ewm_vols: np.ndarray    # (T, N) float64


class MomentumEngine:
    """Computes multi-scale, vol-normalised momentum signals.

    The engine combines signals across multiple lookback horizons using
    inverse-variance weighting, following the AHL style described in
    the hackathon materials. Both TSMOM and XSMOM are computed and
    blended via a configurable alpha parameter.

    Args:
        lookbacks: List of lookback horizons in trading days.
        vol_span_short: EWM span for short-term volatility.
        vol_span_long: EWM span for long-term volatility.
        blend_alpha: Weight on TSMOM vs XSMOM (1.0 = pure TSMOM).

    Example:
        >>> engine = MomentumEngine(lookbacks=[4, 8, 16, 32], blend_alpha=0.7)
        >>> sigs = engine.compute(dataset.returns, dataset.prices)
        >>> weights = engine.signal_to_weights(sigs)
    """

    def __init__(
        self,
        lookbacks: list[int] | None = None,
        vol_span_short: int = _EWM_SPAN_SHORT,
        vol_span_long: int = _EWM_SPAN_LONG,
        blend_alpha: float = 0.7,
    ) -> None:
        """Initialise momentum engine with hyperparameters.

        Args:
            lookbacks: Lookback periods in trading days (default [4,8,16,32]).
            vol_span_short: Short EWM span for volatility (default 20).
            vol_span_long: Long EWM span for volatility (default 60).
            blend_alpha: Blend weight on TSMOM; (1-alpha) on XSMOM.
        """
        self._lookbacks = lookbacks or [4, 8, 16, 32]
        self._vol_span_short = vol_span_short
        self._vol_span_long = vol_span_long
        self._blend_alpha = np.clip(blend_alpha, 0.0, 1.0)
        logger.info(
            "MomentumEngine: lookbacks=%s alpha=%.2f", self._lookbacks, self._blend_alpha
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ewm_vol(returns: np.ndarray, span: int) -> np.ndarray:
        """Compute exponentially-weighted rolling volatility.

        Args:
            returns: (T, N) return matrix.
            span: EWM span parameter.

        Returns:
            (T, N) volatility matrix; first `span` rows may be NaN.
        """
        alpha = 2.0 / (span + 1)
        T, N = returns.shape
        var = np.full_like(returns, np.nan)
        # Initialise with first non-NaN return squared
        var[0] = returns[0] ** 2
        for t in range(1, T):
            var[t] = alpha * returns[t] ** 2 + (1 - alpha) * var[t - 1]
        return np.sqrt(np.maximum(var, 1e-12))

    def _tsmom_signal(
        self, returns: np.ndarray, vols: np.ndarray, k: int
    ) -> np.ndarray:
        """Compute vol-normalised time-series momentum signal.

        r_{i,t}^k = (P_{i,t} - P_{i,t-k}) / P_{i,t-k}  [approx sum of log-rets]
        s_{i,t}   = r_{i,t}^k / sigma_{i,t}

        Args:
            returns: (T, N) log-return matrix.
            vols: (T, N) realised-vol matrix.
            k: Lookback horizon in days.

        Returns:
            (T, N) vol-normalised TSMOM signal.
        """
        T, N = returns.shape
        mom_ret = np.full((T, N), np.nan)
        for t in range(k, T):
            mom_ret[t] = np.sum(returns[t - k : t], axis=0)  # sum of log-rets ≈ k-period return
        # Vol-normalise
        signal = np.where(vols > 1e-10, mom_ret / vols, 0.0)
        return signal

    @staticmethod
    def _xsmom_signal(tsmom: np.ndarray) -> np.ndarray:
        """Cross-sectional momentum: z-score of TSMOM across instruments.

        Args:
            tsmom: (T, N) TSMOM signal matrix.

        Returns:
            (T, N) cross-sectionally normalised signal.
        """
        T, N = tsmom.shape
        xsmom = np.zeros_like(tsmom)
        for t in range(T):
            row = tsmom[t]
            valid = ~np.isnan(row)
            if valid.sum() < 2:
                continue
            mu = np.nanmean(row)
            sigma = np.nanstd(row)
            if sigma > 1e-10:
                xsmom[t] = (row - mu) / sigma
        return xsmom

    @staticmethod
    def _ivw_combine(signals: list[np.ndarray]) -> np.ndarray:
        """Inverse-variance-weighted combination of signals.

        Args:
            signals: List of (T, N) signal arrays.

        Returns:
            (T, N) combined signal.
        """
        stacked = np.stack(signals, axis=0)  # (K, T, N)
        variances = np.nanvar(stacked, axis=1, keepdims=True)  # (K, 1, N)
        inv_var = np.where(variances > 1e-12, 1.0 / variances, 0.0)
        weights = inv_var / (inv_var.sum(axis=0, keepdims=True) + 1e-12)
        combined = (stacked * weights).sum(axis=0)  # (T, N)
        return combined

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(
        self,
        returns_df: pl.DataFrame,
        precomputed_signals: pl.DataFrame | None = None,
    ) -> MomentumSignals:
        """Compute multi-scale TSMOM + XSMOM signals.

        Args:
            returns_df: Polars DataFrame with 'date' + instrument log-return columns.
            precomputed_signals: Optional DataFrame of pre-computed signals from
                                 the hackathon data to blend with computed signals.

        Returns:
            MomentumSignals dataclass with all signal matrices.
        """
        dates = returns_df["date"].to_numpy()
        ret_mat = returns_df.select(_INSTRUMENTS).to_numpy().astype(np.float64)
        T, N = ret_mat.shape

        # Blend short and long vol estimates
        vols_short = self._ewm_vol(ret_mat, self._vol_span_short)
        vols_long = self._ewm_vol(ret_mat, self._vol_span_long)
        vols = 0.5 * vols_short + 0.5 * vols_long

        # Compute per-lookback TSMOM signals
        tsmom_signals: list[np.ndarray] = []
        for k in self._lookbacks:
            sig = self._tsmom_signal(ret_mat, vols, k)
            tsmom_signals.append(sig)

        # If pre-computed signals available, incorporate them
        if precomputed_signals is not None:
            for k in self._lookbacks:
                cols = [f"{inst}_trend{k}" for inst in _INSTRUMENTS]
                if all(c in precomputed_signals.columns for c in cols):
                    # Align dates
                    ps = precomputed_signals.join(
                        returns_df.select("date"), on="date", how="right"
                    )
                    pre_mat = ps.select(cols).to_numpy().astype(np.float64)
                    pre_mat = np.nan_to_num(pre_mat, nan=0.0)
                    # Blend: average our computed signal with the provided one
                    idx = self._lookbacks.index(k)
                    tsmom_signals[idx] = 0.5 * tsmom_signals[idx] + 0.5 * pre_mat

        # IVW-combine across lookbacks
        tsmom_combined = self._ivw_combine(tsmom_signals)
        xsmom_combined = self._xsmom_signal(tsmom_combined)

        # Final blend of TSMOM and XSMOM
        combined = (
            self._blend_alpha * tsmom_combined
            + (1.0 - self._blend_alpha) * xsmom_combined
        )

        return MomentumSignals(
            tsmom=tsmom_combined,
            xsmom=xsmom_combined,
            combined=combined,
            dates=dates,
            instruments=_INSTRUMENTS,
            ewm_vols=vols,
        )

    def signal_to_weights(
        self,
        signals: MomentumSignals,
        method: Literal["vol_parity", "equal", "rank"] = "vol_parity",
        long_only: bool = True,
    ) -> np.ndarray:
        """Convert signal matrix to portfolio weights.

        Supports multiple sizing methods:
        - vol_parity: w_i ∝ sign(s_i) * |s_i| / σ_i  (risk-parity flavour)
        - equal: equal-weight across instruments with positive signal
        - rank: weight proportional to cross-sectional rank

        Args:
            signals: MomentumSignals from compute().
            method: Position sizing method.
            long_only: If True, clip negative signals to 0 (long-only constraint).

        Returns:
            (T, N) weight matrix, rows sum to 1.0, all >= 0 if long_only.
        """
        T, N = signals.combined.shape
        raw = signals.combined.copy()

        if long_only:
            raw = np.maximum(raw, 0.0)

        if method == "vol_parity":
            # Risk-parity: divide by vol estimate
            sized = raw / (signals.ewm_vols + 1e-10)
        elif method == "rank":
            sized = np.zeros_like(raw)
            for t in range(T):
                r = rankdata(raw[t]) if raw[t].sum() > 0 else raw[t]
                sized[t] = r
        else:  # equal
            sized = (raw > 0).astype(float)

        # Normalise to sum = 1
        row_sums = sized.sum(axis=1, keepdims=True)
        weights = np.where(row_sums > 1e-10, sized / row_sums, 1.0 / N)
        return weights
