"""Inventory cost and reorder-point calculations."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from statistics import NormalDist

from retail_demand import config


@dataclass(frozen=True)
class CostAssumptions:
    """Business assumptions for translating forecast error into dollars."""

    unit_price: float = config.UNIT_PRICE
    gross_margin_rate: float = config.GROSS_MARGIN_RATE
    annual_holding_cost_rate: float = config.ANNUAL_HOLDING_COST_RATE
    reorder_cost_per_order: float = config.REORDER_COST_PER_ORDER
    lead_time_days: int = config.LEAD_TIME_DAYS
    review_period_days: int = config.REVIEW_PERIOD_DAYS
    service_level: float = config.SERVICE_LEVEL

    @property
    def unit_cost(self) -> float:
        return self.unit_price * (1 - self.gross_margin_rate)

    @property
    def gross_margin_per_unit(self) -> float:
        return self.unit_price * self.gross_margin_rate

    @property
    def daily_holding_cost_per_unit(self) -> float:
        return self.unit_cost * self.annual_holding_cost_rate / 365

    @property
    def z_score(self) -> float:
        return NormalDist().inv_cdf(self.service_level)


def safety_stock_units(
    daily_error_std: float,
    lead_time_days: int = config.LEAD_TIME_DAYS,
    service_level: float = config.SERVICE_LEVEL,
) -> float:
    """Calculate safety stock from daily forecast uncertainty."""

    if pd.isna(daily_error_std) or daily_error_std < 0:
        daily_error_std = 0.0
    z_score = NormalDist().inv_cdf(service_level)
    return float(z_score * daily_error_std * math.sqrt(lead_time_days))


def reorder_point_units(
    expected_daily_demand: float,
    daily_error_std: float,
    assumptions: CostAssumptions | None = None,
) -> float:
    """Expected lead-time demand plus safety stock."""

    assumptions = assumptions or CostAssumptions()
    return float(
        expected_daily_demand * assumptions.lead_time_days
        + safety_stock_units(
            daily_error_std,
            assumptions.lead_time_days,
            assumptions.service_level,
        )
    )


def summarize_inventory_policy(
    predictions: pd.DataFrame,
    model_col: str,
    assumptions: CostAssumptions | None = None,
) -> pd.DataFrame:
    """Create SKU-level reorder point and safety stock recommendations."""

    assumptions = assumptions or CostAssumptions()
    residual_col = f"{model_col}_residual"
    work = predictions.copy()
    work[residual_col] = work["sales"] - work[model_col]

    summary = (
        work.groupby(["store", "item"])
        .agg(
            avg_daily_demand=("sales", "mean"),
            forecast_daily_demand=(model_col, "mean"),
            daily_error_std=(residual_col, "std"),
            validation_mape=("abs_pct_error", "mean")
            if "abs_pct_error" in work.columns
            else ("sales", "mean"),
        )
        .reset_index()
    )
    summary["safety_stock_units"] = summary["daily_error_std"].apply(
        lambda value: safety_stock_units(
            value, assumptions.lead_time_days, assumptions.service_level
        )
    )
    summary["reorder_point_units"] = (
        summary["forecast_daily_demand"] * assumptions.lead_time_days
        + summary["safety_stock_units"]
    )
    summary["reorder_point_value"] = summary["reorder_point_units"] * assumptions.unit_cost
    return summary.sort_values("reorder_point_value", ascending=False).reset_index(drop=True)


def weekly_inventory_costs(
    predictions: pd.DataFrame,
    model_col: str,
    assumptions: CostAssumptions | None = None,
) -> pd.DataFrame:
    """Estimate weekly stockout, overstock, and reorder costs for a forecast."""

    assumptions = assumptions or CostAssumptions()
    residuals = predictions.assign(residual=predictions["sales"] - predictions[model_col])
    residual_std = (
        residuals.groupby(["store", "item"])["residual"]
        .std()
        .rename("daily_error_std")
        .reset_index()
    )

    weekly = predictions.copy()
    weekly["week_start"] = (
        weekly["date"] - pd.to_timedelta(weekly["date"].dt.dayofweek, unit="D")
    )
    weekly = (
        weekly.groupby(["store", "item", "week_start"], as_index=False)
        .agg(actual_units=("sales", "sum"), forecast_units=(model_col, "sum"))
        .merge(residual_std, on=["store", "item"], how="left")
    )
    weekly["safety_stock_units"] = weekly["daily_error_std"].apply(
        lambda value: safety_stock_units(
            value, assumptions.lead_time_days, assumptions.service_level
        )
    )
    weekly["target_units"] = weekly["forecast_units"] + weekly["safety_stock_units"]
    weekly["stockout_units"] = np.maximum(weekly["actual_units"] - weekly["target_units"], 0)
    weekly["overstock_units"] = np.maximum(weekly["target_units"] - weekly["actual_units"], 0)
    weekly["stockout_cost"] = weekly["stockout_units"] * assumptions.gross_margin_per_unit
    weekly["holding_cost"] = (
        weekly["overstock_units"]
        * assumptions.daily_holding_cost_per_unit
        * assumptions.lead_time_days
        * 0.5
    )
    weekly["excess_inventory_value"] = weekly["overstock_units"] * assumptions.unit_cost
    weekly["reorder_cost"] = np.where(
        weekly["target_units"] > 0,
        assumptions.reorder_cost_per_order,
        0.0,
    )
    weekly["total_operating_cost"] = (
        weekly["stockout_cost"] + weekly["holding_cost"] + weekly["reorder_cost"]
    )
    weekly["model"] = model_col
    return weekly


def cost_summary(
    predictions: pd.DataFrame,
    model_columns: list[str],
    assumptions: CostAssumptions | None = None,
) -> pd.DataFrame:
    """Compare inventory costs across forecast policies."""

    frames = [weekly_inventory_costs(predictions, col, assumptions) for col in model_columns]
    weekly = pd.concat(frames, ignore_index=True)
    summary = (
        weekly.groupby("model", as_index=False)
        .agg(
            stockout_units=("stockout_units", "sum"),
            overstock_units=("overstock_units", "sum"),
            stockout_cost=("stockout_cost", "sum"),
            holding_cost=("holding_cost", "sum"),
            excess_inventory_value=("excess_inventory_value", "mean"),
            reorder_cost=("reorder_cost", "sum"),
            total_operating_cost=("total_operating_cost", "sum"),
        )
        .sort_values("total_operating_cost")
        .reset_index(drop=True)
    )
    return summary


def assumptions_table(assumptions: CostAssumptions | None = None) -> pd.DataFrame:
    """Return assumptions in a report-ready table."""

    assumptions = assumptions or CostAssumptions()
    rows = [
        ("Unit selling price", assumptions.unit_price, "USD/unit", config.ASSUMPTION_NOTES["unit_price"]),
        ("Gross margin rate", assumptions.gross_margin_rate, "share", config.ASSUMPTION_NOTES["gross_margin_rate"]),
        ("Unit cost", assumptions.unit_cost, "USD/unit", "Derived from unit price and gross margin."),
        ("Annual holding cost rate", assumptions.annual_holding_cost_rate, "share", config.ASSUMPTION_NOTES["annual_holding_cost_rate"]),
        ("Daily holding cost", assumptions.daily_holding_cost_per_unit, "USD/unit/day", "Derived carrying cost per unit-day."),
        ("Stockout cost", assumptions.gross_margin_per_unit, "USD/lost unit", "Lost gross margin on unmet demand."),
        ("Reorder cost", assumptions.reorder_cost_per_order, "USD/order", config.ASSUMPTION_NOTES["reorder_cost_per_order"]),
        ("Lead time", assumptions.lead_time_days, "days", config.ASSUMPTION_NOTES["lead_time_days"]),
        ("Cycle service level", assumptions.service_level, "share", config.ASSUMPTION_NOTES["service_level"]),
    ]
    return pd.DataFrame(rows, columns=["assumption", "value", "unit", "note"])

