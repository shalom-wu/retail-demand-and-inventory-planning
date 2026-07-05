"""Run data cleaning, quality checks, EDA tables, and EDA visuals."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_demand import config
from retail_demand.data import (
    aggregate_daily,
    coefficient_of_variation,
    load_sales,
    profile_sales,
)
from retail_demand.reporting import markdown_table, write_markdown
from retail_demand.viz import (
    plot_monthly_seasonality,
    plot_store_item_cv_heatmap,
    plot_weekday_pattern,
    plot_weekly_sales,
)


def _quality_markdown(profile) -> str:
    checks = pd.DataFrame(
        [
            ("Expected grain", "date x store x item", "Pass" if profile.complete_daily_grid else "Review"),
            ("Duplicate grain rows", profile.duplicate_grain_rows, "Pass" if profile.duplicate_grain_rows == 0 else "Fail"),
            ("Missing values", profile.missing_values, "Pass" if profile.missing_values == 0 else "Review"),
            ("Negative sales rows", profile.negative_sales_rows, "Pass" if profile.negative_sales_rows == 0 else "Fail"),
            ("Date coverage", f"{profile.start_date.date()} to {profile.end_date.date()}", "Pass"),
            ("Store/item coverage", f"{profile.store_count} stores x {profile.item_count} items", "Pass"),
        ],
        columns=["check", "evidence", "status"],
    )
    return f"""
# Data Quality Report

## Dataset And Grain

The raw training file has **{profile.rows:,} rows** and **{profile.columns} columns**.
The intended grain is one row per calendar date, store, and item.

## Checks Performed

{markdown_table(checks)}

## Findings

- The file is clean for the core forecasting task: no missing values, no duplicate
  date-store-item rows, no negative sales, and a complete daily grid.
- The biggest data-quality limitation is not a broken field. It is missing
  business context: the dataset has unit sales only, with no price, margin,
  on-hand inventory, stockout flags, promotions, supplier lead times, weather,
  holidays, or local events.
- Because sales are observed sales rather than true demand, a real stockout
  would censor demand. The Kaggle file does not tell us when that happened, so
  the model assumes historical sales are a good proxy for demand.

## Recommended Automated Tests

- Enforce uniqueness on `date`, `store`, and `item`.
- Reject negative sales and missing required fields.
- Check that each store-item series has continuous daily dates.
- Monitor row count by date if this became a recurring pipeline.
"""


def main() -> None:
    config.OUTPUTS.mkdir(parents=True, exist_ok=True)
    config.FIGURES.mkdir(parents=True, exist_ok=True)

    sales = load_sales()
    profile = profile_sales(sales)

    (config.OUTPUTS / "data_profile.json").write_text(
        json.dumps(
            {
                "rows": profile.rows,
                "columns": profile.columns,
                "start_date": str(profile.start_date.date()),
                "end_date": str(profile.end_date.date()),
                "stores": profile.store_count,
                "items": profile.item_count,
                "duplicate_grain_rows": profile.duplicate_grain_rows,
                "missing_values": profile.missing_values,
                "negative_sales_rows": profile.negative_sales_rows,
                "complete_daily_grid": profile.complete_daily_grid,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(config.OUTPUTS / "data_quality_report.md", _quality_markdown(profile))

    daily = aggregate_daily(sales)
    daily.to_csv(config.OUTPUTS / "daily_sales.csv", index=False)

    store_summary = (
        sales.groupby("store", as_index=False)
        .agg(total_sales=("sales", "sum"), avg_daily_sales=("sales", "mean"), sales_std=("sales", "std"))
        .assign(cv=lambda d: d["sales_std"] / d["avg_daily_sales"])
        .sort_values("total_sales", ascending=False)
    )
    store_summary.to_csv(config.OUTPUTS / "store_summary.csv", index=False)

    item_summary = (
        sales.groupby("item", as_index=False)
        .agg(total_sales=("sales", "sum"), avg_daily_sales=("sales", "mean"), sales_std=("sales", "std"))
        .assign(cv=lambda d: d["sales_std"] / d["avg_daily_sales"])
        .sort_values("total_sales", ascending=False)
    )
    item_summary.to_csv(config.OUTPUTS / "item_summary.csv", index=False)

    store_item_variance = sales.groupby(["store", "item"]).agg(
        mean_sales=("sales", "mean"),
        sales_std=("sales", "std"),
        total_sales=("sales", "sum"),
        cv=("sales", coefficient_of_variation),
    ).reset_index()
    store_item_variance = store_item_variance.sort_values("cv", ascending=False)
    store_item_variance.to_csv(config.OUTPUTS / "store_item_variance.csv", index=False)

    monthly = (
        sales.assign(month=sales["date"].dt.month)
        .groupby("month", as_index=False)["sales"]
        .mean()
        .rename(columns={"sales": "avg_daily_sales"})
    )
    monthly.to_csv(config.OUTPUTS / "monthly_seasonality.csv", index=False)

    weekday = (
        sales.assign(dayofweek=sales["date"].dt.dayofweek)
        .groupby("dayofweek", as_index=False)["sales"]
        .mean()
        .rename(columns={"sales": "avg_daily_sales"})
    )
    weekday.to_csv(config.OUTPUTS / "weekday_pattern.csv", index=False)

    decomposition = seasonal_decompose(
        daily.set_index("date")["sales"],
        model="additive",
        period=365,
        extrapolate_trend="freq",
    )
    decomposition_df = pd.DataFrame(
        {
            "date": daily["date"],
            "observed": decomposition.observed.values,
            "trend": decomposition.trend.values,
            "seasonal": decomposition.seasonal.values,
            "residual": decomposition.resid.values,
        }
    )
    decomposition_df.to_csv(config.OUTPUTS / "trend_decomposition.csv", index=False)

    plot_weekly_sales(daily, config.FIGURES / "weekly_sales_trend.png")
    plot_monthly_seasonality(sales, config.FIGURES / "monthly_seasonality.png")
    plot_weekday_pattern(sales, config.FIGURES / "weekday_pattern.png")
    plot_store_item_cv_heatmap(store_item_variance, config.FIGURES / "store_item_cv_heatmap.png")

    print("EDA complete.")


if __name__ == "__main__":
    main()
