"""Forecasting models and evaluation utilities."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error

from retail_demand import config
from retail_demand.data import add_lag_features, train_validation_split


FEATURE_COLUMNS = [
    "store",
    "item",
    "dayofweek",
    "weekofyear",
    "month",
    "quarter",
    "year",
    "dayofyear",
    "is_weekend",
    "lag_1",
    "lag_7",
    "lag_14",
    "lag_28",
    "lag_365",
    "rolling_mean_7",
    "rolling_std_7",
    "rolling_mean_28",
    "rolling_std_28",
]


@dataclass(frozen=True)
class ModelRunConfig:
    """Parameters for the reproducible modeling run."""

    validation_start: str = "2017-10-01"
    model_name: str = "hist_gradient_boosting"
    max_iter: int = 220
    learning_rate: float = 0.06
    l2_regularization: float = 0.10
    random_seed: int = config.RANDOM_SEED


def rmse(y_true: pd.Series | np.ndarray, y_pred: pd.Series | np.ndarray) -> float:
    """Root mean squared error."""

    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def mape(y_true: pd.Series | np.ndarray, y_pred: pd.Series | np.ndarray) -> float:
    """Mean absolute percentage error as a percent."""

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    denominator = np.maximum(np.abs(y_true), 1e-9)
    return float(np.mean(np.abs((y_true - y_pred) / denominator)) * 100)


def wmape(y_true: pd.Series | np.ndarray, y_pred: pd.Series | np.ndarray) -> float:
    """Weighted MAPE as a percent."""

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    return float(np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) * 100)


def metrics_frame(
    y_true: pd.Series,
    predictions: dict[str, pd.Series | np.ndarray],
) -> pd.DataFrame:
    """Evaluate forecast columns with time-series metrics."""

    rows = []
    for name, pred in predictions.items():
        rows.append(
            {
                "model": name,
                "rmse": rmse(y_true, pred),
                "mape": mape(y_true, pred),
                "wmape": wmape(y_true, pred),
                "bias_units": float(np.mean(np.asarray(pred) - np.asarray(y_true))),
            }
        )
    return pd.DataFrame(rows).sort_values("wmape").reset_index(drop=True)


def add_baseline_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Add seasonal naive and moving-average baseline predictions."""

    out = add_lag_features(df)
    out["seasonal_naive"] = out["lag_365"]
    out["moving_average_28"] = out["rolling_mean_28"]
    return out


def fit_gradient_boosting(
    train_df: pd.DataFrame,
    run_config: ModelRunConfig | None = None,
) -> HistGradientBoostingRegressor:
    """Fit a gradient boosting model on calendar and lagged features."""

    run_config = run_config or ModelRunConfig()
    model = HistGradientBoostingRegressor(
        max_iter=run_config.max_iter,
        learning_rate=run_config.learning_rate,
        l2_regularization=run_config.l2_regularization,
        random_state=run_config.random_seed,
        loss="squared_error",
        max_leaf_nodes=31,
    )
    train_model_df = train_df.dropna(subset=FEATURE_COLUMNS + ["sales"])
    model.fit(train_model_df[FEATURE_COLUMNS], train_model_df["sales"])
    return model


def run_forecast_model(
    df: pd.DataFrame,
    run_config: ModelRunConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, HistGradientBoostingRegressor]:
    """Run baselines, train the model, and return validation predictions."""

    run_config = run_config or ModelRunConfig()
    featured = add_baseline_predictions(df)
    train_df, validation_df = train_validation_split(
        featured,
        validation_start=run_config.validation_start,
    )
    model = fit_gradient_boosting(train_df, run_config)

    validation_model_df = validation_df.dropna(subset=FEATURE_COLUMNS).copy()
    validation_model_df["gradient_boosting"] = model.predict(
        validation_model_df[FEATURE_COLUMNS]
    )
    for col in ["seasonal_naive", "moving_average_28", "gradient_boosting"]:
        validation_model_df[col] = validation_model_df[col].clip(lower=0)

    metric_table = metrics_frame(
        validation_model_df["sales"],
        {
            "seasonal_naive": validation_model_df["seasonal_naive"],
            "moving_average_28": validation_model_df["moving_average_28"],
            "gradient_boosting": validation_model_df["gradient_boosting"],
        },
    )
    return validation_model_df, metric_table, model


def per_sku_error(
    validation_predictions: pd.DataFrame,
    model_col: str = "gradient_boosting",
) -> pd.DataFrame:
    """Calculate SKU-level error and demand volatility."""

    work = validation_predictions.copy()
    work["abs_pct_error"] = (
        (work["sales"] - work[model_col]).abs() / work["sales"].clip(lower=1e-9)
    ) * 100
    summary = (
        work.groupby(["store", "item"], as_index=False)
        .agg(
            mean_sales=("sales", "mean"),
            sales_std=("sales", "std"),
            mape=("abs_pct_error", "mean"),
            rmse=("sales", lambda s: np.nan),
        )
    )
    rmse_rows = (
        work.groupby(["store", "item"])
        .apply(lambda g: rmse(g["sales"], g[model_col]), include_groups=False)
        .rename("rmse")
        .reset_index()
    )
    summary = summary.drop(columns=["rmse"]).merge(rmse_rows, on=["store", "item"])
    summary["cv"] = summary["sales_std"] / summary["mean_sales"]
    summary["difficulty_score"] = summary["cv"].rank(pct=True) * 0.5 + summary[
        "mape"
    ].rank(pct=True) * 0.5
    return summary.sort_values("difficulty_score", ascending=False).reset_index(drop=True)


def save_model_metadata(path: Path, run_config: ModelRunConfig, metrics: pd.DataFrame) -> None:
    """Persist lightweight model metadata."""

    payload = {
        "run_config": asdict(run_config),
        "feature_columns": FEATURE_COLUMNS,
        "metrics": metrics.to_dict(orient="records"),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
