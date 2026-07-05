"""Build the markdown strategy deck from generated analysis outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_demand import config
from retail_demand.reporting import money, pct, units, write_markdown


def main() -> None:
    profile = json.loads((config.OUTPUTS / "data_profile.json").read_text(encoding="utf-8"))
    metrics = pd.read_csv(config.OUTPUTS / "model_metrics.csv")
    costs = pd.read_csv(config.OUTPUTS / "inventory_cost_summary.csv")
    store_summary = pd.read_csv(config.OUTPUTS / "store_summary.csv")
    item_summary = pd.read_csv(config.OUTPUTS / "item_summary.csv")
    sku = pd.read_csv(config.OUTPUTS / "sku_difficulty.csv")
    policy = pd.read_csv(config.OUTPUTS / "inventory_policy.csv")

    baseline = metrics.loc[metrics["model"] == "seasonal_naive"].iloc[0]
    model = metrics.loc[metrics["model"] == "gradient_boosting"].iloc[0]
    baseline_cost = costs.loc[costs["model"] == "seasonal_naive"].iloc[0]
    model_cost = costs.loc[costs["model"] == "gradient_boosting"].iloc[0]
    savings = baseline_cost["total_operating_cost"] - model_cost["total_operating_cost"]
    savings_rate = savings / baseline_cost["total_operating_cost"] * 100
    top_store = store_summary.iloc[0]
    top_item = item_summary.iloc[0]
    hardest = sku.iloc[0]
    avg_safety_stock = policy["safety_stock_units"].mean()
    avg_rop = policy["reorder_point_units"].mean()

    deck = f"""
# Retail Demand Forecasting & Inventory Optimization

## 1. Problem Framing

**Manual or naive replenishment leaves money on both sides of the shelf.**

This project uses the Kaggle Store Item Demand Forecasting Challenge dataset:
{profile["rows"]:,} daily observations across {profile["stores"]} stores,
{profile["items"]} items, and five years. The business question is practical:
how much better does a store-item forecast need to be before it changes reorder
decisions?

Baseline assumption: the retailer currently uses a same-day-last-year forecast
as a proxy for manual seasonal reordering.

Validation-period baseline cost:

- Stockout cost: {money(baseline_cost["stockout_cost"])}
- Holding cost: {money(baseline_cost["holding_cost"])}
- Reorder admin cost: {money(baseline_cost["reorder_cost"])}
- Total operating cost: {money(baseline_cost["total_operating_cost"])}

![Weekly sales trend](figures/weekly_sales_trend.png)

## 2. Key Drivers

**The data is seasonal, but not flat enough for one blanket safety-stock rule.**

The demand curve shows a repeatable yearly pattern, with clear weekday lift and
meaningful differences by store and item. Store {int(top_store["store"])} has
the highest total demand in the training set, while item {int(top_item["item"])}
is the highest-volume item overall.

![Monthly seasonality](figures/monthly_seasonality.png)

![Weekday pattern](figures/weekday_pattern.png)

## 3. Forecasting Results

**A feature-based model beats the seasonal naive baseline on the holdout quarter.**

The validation window is October 1, 2017 through December 31, 2017. The stronger
model is a gradient boosting regressor using calendar features, store/item ids,
rolling demand, and lagged sales. The baseline is same-day-last-year demand.

- Seasonal naive WMAPE: {pct(baseline["wmape"])}
- Gradient boosting WMAPE: {pct(model["wmape"])}
- WMAPE improvement: {baseline["wmape"] - model["wmape"]:.1f} percentage points
- Gradient boosting RMSE: {model["rmse"]:.2f} units per store-item day

![Forecast comparison](figures/forecast_comparison.png)

## 4. Cost Of Inaction

**Forecast error becomes expensive when it is converted into stockout exposure.**

Using the same reorder logic, the modeled policy reduces validation-period
operating cost by **{money(savings)}**, or **{savings_rate:.1f}%**, versus the
seasonal naive policy. The largest dollars sit in lost gross margin from unmet
demand, not in the short-run carrying cost.

![Cost comparison](figures/cost_comparison.png)

## 5. Intervention Options

**Option A: SKU-level dynamic safety stock**

- Most targeted option; changes reorder points where forecast uncertainty is high.
- Best fit for items with high volatility or high margin exposure.
- Requires store-item level monitoring and periodic recalibration.

**Option B: Store-level forecasting**

- Easier to explain and operate.
- Useful for labor planning or aggregate replenishment.
- Too blunt for item-level stockout prevention.

**Option C: Centralized forecast with store allocation**

- Best long-term operating model if the retailer can pool demand signals.
- Supports allocation logic across stores when supply is constrained.
- Needs richer data than this Kaggle file: inventory, price, promotions,
  supplier lead time, and store constraints.

## 6. Recommendation And ROI

**Start with SKU-level dynamic safety stock for the top-risk store-item pairs.**

The first rollout should focus on the series with both high demand volatility
and high forecast error. The hardest validation series is store
{int(hardest["store"])}, item {int(hardest["item"])}, with CV
{hardest["cv"]:.2f} and MAPE {hardest["mape"]:.1f}%.

Expected base-case impact under the model assumptions:

- Average recommended safety stock: {avg_safety_stock:.1f} units per store-item
- Average reorder point: {avg_rop:.1f} units per store-item
- Validation-period modeled savings: {money(savings)}
- Main ROI lever: fewer lost-margin stockouts without blindly raising inventory everywhere

## 7. Appendix: Methodology And Caveats

**Methodology**

- Cleaned and validated the Kaggle training data at date-store-item grain.
- Profiled store, item, weekday, monthly, and annual seasonality patterns.
- Decomposed total daily demand with `statsmodels` to separate trend,
  seasonality, and residual variation.
- Compared seasonal naive, 28-day moving average, and gradient boosting models.
- Translated forecast uncertainty into safety stock using a 95% service level
  and a 7-day lead-time assumption.

**Caveats**

- The dataset has observed sales, not true demand. Stockouts could hide demand.
- There are no price, margin, promotion, holiday, weather, competitor, or
  inventory-on-hand fields.
- Lag features in the validation run represent a daily reforecast process after
  recent sales are known; a long-horizon frozen forecast would need recursive
  simulation.
- Dollar results are assumption-driven and should be replaced with retailer
  finance data before a real business case.
"""
    write_markdown(config.REPORTS / "strategy_deck.md", deck)
    print("Deck complete.")


if __name__ == "__main__":
    main()
