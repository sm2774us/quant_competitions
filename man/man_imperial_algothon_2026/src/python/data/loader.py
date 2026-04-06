"""Data loading and preprocessing utilities for the Algothon 2026 portfolio system.

This module provides high-performance data ingestion using Polars for financial
time-series data including prices, signals, volumes, and cash rates.

Usage:
    >>> loader = DataLoader("data/sample")
    >>> dataset = loader.load_all()
    >>> returns = dataset.compute_returns()
    >>> print(returns.prices.shape)

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

import numpy as np
import polars as pl

logger = logging.getLogger(__name__)

_INSTRUMENTS: Final[list[str]] = [f"INSTRUMENT_{i}" for i in range(1, 11)]
_LOOKBACKS: Final[list[int]] = [4, 8, 16, 32]
_SIGNAL_COLS: Final[list[str]] = [
    f"{inst}_trend{lb}" for inst in _INSTRUMENTS for lb in _LOOKBACKS
]
_YIELD_TENORS: Final[list[str]] = [
    "1mo", "1.5month", "2mo", "3mo", "4mo", "6mo",
    "1yr", "2yr", "3yr", "5yr", "7yr", "10yr", "20yr", "30yr",
]


@dataclass(frozen=True, slots=True)
class AlgothonDataset:
    """Immutable container for all loaded financial data.

    Attributes:
        prices: Daily OHLC-equivalent close prices for 10 instruments.
        signals: Pre-computed trend signals at lookbacks 4/8/16/32.
        volumes: Daily traded volumes per instrument.
        cash_rates: US Treasury yield curve (1990-present).
        returns: Log-returns computed from prices (set after construction).
    """

    prices: pl.DataFrame
    signals: pl.DataFrame
    volumes: pl.DataFrame
    cash_rates: pl.DataFrame
    returns: pl.DataFrame = field(default=None)  # type: ignore[assignment]

    def compute_returns(self) -> "AlgothonDataset":
        """Compute log-returns from price data; returns a new dataset with returns set."""
        price_mat = (
            self.prices.select(_INSTRUMENTS)
            .to_numpy()
            .astype(np.float64)
        )
        log_ret = np.log(price_mat[1:] / price_mat[:-1])
        dates = self.prices["date"][1:]
        ret_df = pl.DataFrame(
            {"date": dates, **{inst: log_ret[:, i] for i, inst in enumerate(_INSTRUMENTS)}}
        )
        return AlgothonDataset(
            prices=self.prices,
            signals=self.signals,
            volumes=self.volumes,
            cash_rates=self.cash_rates,
            returns=ret_df,
        )

    def get_aligned_slice(self, start: str, end: str) -> "AlgothonDataset":
        """Return a date-aligned slice of the dataset.

        Args:
            start: ISO date string, e.g. "2020-01-01".
            end: ISO date string, e.g. "2026-02-28".

        Returns:
            A new AlgothonDataset filtered to [start, end].
        """
        def _filter(df: pl.DataFrame) -> pl.DataFrame:
            return df.filter(
                (pl.col("date") >= pl.lit(start).str.to_date())
                & (pl.col("date") <= pl.lit(end).str.to_date())
            )

        return AlgothonDataset(
            prices=_filter(self.prices),
            signals=_filter(self.signals),
            volumes=_filter(self.volumes),
            cash_rates=_filter(self.cash_rates),
            returns=_filter(self.returns) if self.returns is not None else None,
        )


class DataLoader:
    """High-performance financial data loader backed by Polars lazy evaluation.

    Loads prices, signals, volumes, and cash rates from CSV files in a given
    directory, applies type coercions, and exposes a unified dataset object.

    Args:
        data_dir: Path to directory containing the four CSV files.

    Example:
        >>> loader = DataLoader("data/sample")
        >>> ds = loader.load_all()
        >>> ds = ds.compute_returns()
    """

    def __init__(self, data_dir: str | Path) -> None:
        """Initialise loader with the path to the data directory.

        Args:
            data_dir: Root directory containing prices.csv, signals.csv,
                      volumes.csv, cash_rate.csv.

        Raises:
            FileNotFoundError: If any required CSV is missing.
        """
        self._dir = Path(data_dir)
        required = ["prices.csv", "signals.csv", "volumes.csv", "cash_rate.csv"]
        for f in required:
            if not (self._dir / f).exists():
                raise FileNotFoundError(f"Required file not found: {self._dir / f}")
        logger.info("DataLoader initialised at %s", self._dir)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_prices(self) -> pl.DataFrame:
        """Load and clean price data.

        Returns:
            Polars DataFrame with 'date' column + 10 instrument price columns.
        """
        df = (
            pl.scan_csv(self._dir / "prices.csv", try_parse_dates=True)
            .with_columns(pl.col("date").cast(pl.Date))
            .sort("date")
            .collect()
        )
        logger.debug("Prices shape: %s", df.shape)
        return df

    def _load_signals(self) -> pl.DataFrame:
        """Load pre-computed trend-following signals.

        Returns:
            Polars DataFrame with 40 signal columns (10 instruments × 4 lookbacks).
        """
        df = (
            pl.scan_csv(self._dir / "signals.csv", try_parse_dates=True)
            .with_columns(pl.col("date").cast(pl.Date))
            .sort("date")
            .collect()
        )
        # Forward-fill NaN signals conservatively (signals become valid after warmup)
        signal_exprs = [
            pl.col(c).forward_fill().fill_null(0.0) for c in _SIGNAL_COLS
        ]
        df = df.with_columns(signal_exprs)
        logger.debug("Signals shape: %s", df.shape)
        return df

    def _load_volumes(self) -> pl.DataFrame:
        """Load trading volume data.

        Returns:
            Polars DataFrame with volume columns per instrument.
        """
        vol_cols = [f"{inst}_vol" for inst in _INSTRUMENTS]
        df = (
            pl.scan_csv(self._dir / "volumes.csv", try_parse_dates=True)
            .with_columns(pl.col("date").cast(pl.Date))
            .sort("date")
            .collect()
        )
        # Replace zero volumes with NaN for proper handling downstream
        df = df.with_columns([
            pl.when(pl.col(c) == 0).then(None).otherwise(pl.col(c)).alias(c)
            for c in vol_cols
        ])
        return df

    def _load_cash_rates(self) -> pl.DataFrame:
        """Load US Treasury yield curve data.

        Returns:
            Polars DataFrame with yield columns indexed by date.
        """
        df = (
            pl.scan_csv(self._dir / "cash_rate.csv", try_parse_dates=True)
            .with_columns(pl.col("date").cast(pl.Date))
            .sort("date")
            .collect()
        )
        # Forward-fill missing yields (weekends/holidays)
        df = df.with_columns([pl.col(t).forward_fill() for t in _YIELD_TENORS if t in df.columns])
        return df

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_all(self) -> AlgothonDataset:
        """Load all CSV files and return a unified dataset.

        Returns:
            AlgothonDataset with prices, signals, volumes, cash_rates populated.
        """
        logger.info("Loading all data from %s", self._dir)
        prices = self._load_prices()
        signals = self._load_signals()
        volumes = self._load_volumes()
        cash_rates = self._load_cash_rates()
        ds = AlgothonDataset(
            prices=prices,
            signals=signals,
            volumes=volumes,
            cash_rates=cash_rates,
        )
        return ds.compute_returns()
