"""Data loading, validation, and feature preparation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from retail_demand import config


REQUIRED_COLUMNS = ["date", "store", "item", "sales"]


@dataclass(frozen=True)
class DataQualityResult:
    """Compact data-quality summary for reporting and tests."""

    rows: int
    columns: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    store_count: int
    item_count: int
    duplicate_grain_rows: int
    missing_values: int
    negative_sales_rows: int
    complete_daily_grid: bool


def load_sales(path: Path | None = None) -> pd.DataFrame:
    """Load Kaggle sales data and enforce the expected schema."""

    csv_path = path or config.TRAIN_CSV
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Could not find {csv_path}. Run `python scripts/download_data.py` first."
        )

    df = pd.read_csv(csv_path, parse_dates=["date"])
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df = df[REQUIRED_COLUMNS].copy()
    df["store"] = df["store"].astype("int16")
    df["item"] = df["item"].astype("int16")
    df["sales"] = df["sales"].astype("int32")
    return df.sort_values(["store", "item", "date"]).reset_index(drop=True)


def profile_sales(df: pd.DataFrame) -> DataQualityResult:
    """Profile the dataset at the expected date-store-item grain."""

    duplicate_grain_rows = int(df.duplicated(["date", "store", "item"]).sum())
    date_range = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    expected_rows = len(date_range) * df["store"].nunique() * df["item"].nunique()

    return DataQualityResult(
        rows=len(df),
        columns=df.shape[1],
        start_date=df["date"].min(),
        end_date=df["date"].max(),
        store_count=int(df["store"].nunique()),
        item_count=int(df["item"].nunique()),
        duplicate_grain_rows=duplicate_grain_rows,
        missing_values=int(df.isna().sum().sum()),
        negative_sales_rows=int((df["sales"] < 0).sum()),
        complete_daily_grid=len(df) == expected_rows and duplicate_grain_rows == 0,
    )


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add deterministic calendar features used by EDA and forecasting."""

    out = df.copy()
    out["dayofweek"] = out["date"].dt.dayofweek
    out["weekofyear"] = out["date"].dt.isocalendar().week.astype("int16")
    out["month"] = out["date"].dt.month.astype("int8")
    out["quarter"] = out["date"].dt.quarter.astype("int8")
    out["year"] = out["date"].dt.year.astype("int16")
    out["dayofyear"] = out["date"].dt.dayofyear.astype("int16")
    out["is_weekend"] = out["dayofweek"].isin([5, 6]).astype("int8")
    return out


def add_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create lagged features without leaking future sales."""

    out = add_time_features(df)
    group_cols = ["store", "item"]
    grouped = out.groupby(group_cols, sort=False)["sales"]
    for lag in [1, 7, 14, 28, 365]:
        out[f"lag_{lag}"] = grouped.shift(lag)
    for window in [7, 28]:
        shifted = grouped.shift(1)
        out[f"rolling_mean_{window}"] = shifted.groupby(
            [out["store"], out["item"]], sort=False
        ).transform(lambda s: s.rolling(window, min_periods=window).mean())
        out[f"rolling_std_{window}"] = shifted.groupby(
            [out["store"], out["item"]], sort=False
        ).transform(lambda s: s.rolling(window, min_periods=window).std())
    out["store_item"] = out["store"].astype(str) + "_" + out["item"].astype(str)
    return out


def train_validation_split(
    df: pd.DataFrame,
    validation_start: str = "2017-10-01",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Use the last complete quarter as a holdout validation window."""

    cutoff = pd.Timestamp(validation_start)
    train = df.loc[df["date"] < cutoff].copy()
    validation = df.loc[df["date"] >= cutoff].copy()
    return train, validation


def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales to total daily demand."""

    return (
        df.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )


def coefficient_of_variation(values: pd.Series) -> float:
    """Return coefficient of variation, guarding against zero means."""

    mean = float(values.mean())
    if np.isclose(mean, 0):
        return float("nan")
    return float(values.std(ddof=0) / mean)

