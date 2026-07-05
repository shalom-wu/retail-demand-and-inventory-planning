"""Run forecasting models and inventory decision analysis."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_demand import config
from retail_demand.costs import (
    CostAssumptions,
    assumptions_table,
    cost_summary,
    summarize_inventory_policy,
    weekly_inventory_costs,
)
from retail_demand.data import load_sales
from retail_demand.modeling import (
    ModelRunConfig,
    per_sku_error,
    run_forecast_model,
    save_model_metadata,
)
from retail_demand.reporting import markdown_table, money, pct, units, write_markdown
from retail_demand.viz import (
    plot_cost_comparison,
    plot_forecast_comparison,
    plot_sku_error_scatter,
)


def _model_report(
    metrics: pd.DataFrame,
    costs: pd.DataFrame,
    sku_metrics: pd.DataFrame,
    assumptions: CostAssumptions,
) -> str:
    best_model = metrics.iloc[0]
    baseline = metrics.loc[metrics["model"] == "seasonal_naive"].iloc[0]
    gbm = metrics.loc[metrics["model"] == "gradient_boosting"].iloc[0]
    cost_baseline = costs.loc[costs["model"] == "seasonal_naive"].iloc[0]
    cost_model = costs.loc[costs["model"] == "gradient_boosting"].iloc[0]
    cost_delta = cost_baseline["total_operating_cost"] - cost_model["total_operating_cost"]
    wmape_delta = baseline["wmape"] - gbm["wmape"]
    hard = sku_metrics.head(5)[["store", "item", "mean_sales", "cv", "mape"]].copy()
    stable = sku_metrics.tail(5)[["store", "item", "mean_sales", "cv", "mape"]].copy()
    for frame in [hard, stable]:
        frame["mean_sales"] = frame["mean_sales"].map(lambda x: f"{x:.1f}")
        frame["cv"] = frame["cv"].map(lambda x: f"{x:.2f}")
        frame["mape"] = frame["mape"].map(lambda x: f"{x:.1f}%")

    return f"""
# Modeling And Inventory Report

## Executive Summary

- **Best validation model:** `{best_model["model"]}` with WMAPE of **{pct(best_model["wmape"])}** and RMSE of **{best_model["rmse"]:.2f}** units at the store-item-day grain.
- **Model lift over seasonal naive:** gradient boosting improves WMAPE by **{wmape_delta:.1f} percentage points** versus the same-day-last-year baseline.
- **Inventory impact:** using the modeled reorder policy lowers validation-period operating cost by about **{money(cost_delta)}** versus the seasonal naive policy under the stated assumptions.

## Model Performance

{markdown_table(metrics.round({"rmse": 2, "mape": 2, "wmape": 2, "bias_units": 2}))}

## Cost Translation

The policy simulation compares weekly demand to weekly forecasted units plus
safety stock. Stockouts are valued as lost gross margin; overstock is valued as
carrying cost and separately reported as working capital tied up in inventory.

{markdown_table(costs.round(2))}

## Hard-To-Forecast Store-Item Series

These are not necessarily bad products. They are the series where volatility and
forecast error make static safety stock risky.

{markdown_table(hard)}

## Stable Store-Item Series

These are better candidates for lean replenishment and lower safety stock.

{markdown_table(stable)}

## Inventory Assumptions

- Unit price: **{money(assumptions.unit_price)}**
- Gross margin: **{assumptions.gross_margin_rate:.0%}**
- Annual holding cost: **{assumptions.annual_holding_cost_rate:.0%}**
- Lead time: **{assumptions.lead_time_days} days**
- Cycle service level: **{assumptions.service_level:.0%}**

The economics are directional. A real retailer should replace these planning
assumptions with item price, landed cost, supplier minimums, pack sizes,
inventory-on-hand, and observed stockout rates.
"""


def main() -> None:
    config.OUTPUTS.mkdir(parents=True, exist_ok=True)
    config.FIGURES.mkdir(parents=True, exist_ok=True)

    assumptions = CostAssumptions()
    run_config = ModelRunConfig()
    sales = load_sales()

    validation, metrics, _ = run_forecast_model(sales, run_config)
    validation.to_csv(config.OUTPUTS / "validation_predictions.csv", index=False)
    metrics.to_csv(config.OUTPUTS / "model_metrics.csv", index=False)
    save_model_metadata(config.OUTPUTS / "model_run_metadata.json", run_config, metrics)

    sku_metrics = per_sku_error(validation, "gradient_boosting")
    sku_metrics.to_csv(config.OUTPUTS / "sku_difficulty.csv", index=False)

    validation_for_policy = validation.copy()
    validation_for_policy["abs_pct_error"] = (
        (validation_for_policy["sales"] - validation_for_policy["gradient_boosting"]).abs()
        / validation_for_policy["sales"].clip(lower=1e-9)
        * 100
    )
    policy = summarize_inventory_policy(validation_for_policy, "gradient_boosting", assumptions)
    policy.to_csv(config.OUTPUTS / "inventory_policy.csv", index=False)

    model_cols = ["seasonal_naive", "moving_average_28", "gradient_boosting"]
    costs = cost_summary(validation, model_cols, assumptions)
    costs.to_csv(config.OUTPUTS / "inventory_cost_summary.csv", index=False)
    weekly_costs = pd.concat(
        [weekly_inventory_costs(validation, col, assumptions) for col in model_cols],
        ignore_index=True,
    )
    weekly_costs.to_csv(config.OUTPUTS / "weekly_inventory_costs.csv", index=False)
    assumptions_table(assumptions).to_csv(config.OUTPUTS / "cost_assumptions.csv", index=False)

    write_markdown(
        config.OUTPUTS / "model_report.md",
        _model_report(metrics, costs, sku_metrics, assumptions),
    )

    plot_forecast_comparison(validation, config.FIGURES / "forecast_comparison.png")
    plot_sku_error_scatter(sku_metrics, config.FIGURES / "sku_variance_vs_error.png")
    plot_cost_comparison(costs, config.FIGURES / "cost_comparison.png")

    print("Modeling complete.")


if __name__ == "__main__":
    main()
