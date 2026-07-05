from __future__ import annotations

import pandas as pd

from retail_demand.costs import (
    CostAssumptions,
    reorder_point_units,
    safety_stock_units,
    weekly_inventory_costs,
)


def test_safety_stock_increases_with_uncertainty() -> None:
    low = safety_stock_units(2, lead_time_days=7, service_level=0.95)
    high = safety_stock_units(5, lead_time_days=7, service_level=0.95)

    assert high > low > 0


def test_reorder_point_adds_lead_time_demand_and_buffer() -> None:
    assumptions = CostAssumptions(lead_time_days=7, service_level=0.95)
    rop = reorder_point_units(10, 0, assumptions)

    assert rop == 70


def test_weekly_inventory_costs_flags_shortfall() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=7, freq="D"),
            "store": [1] * 7,
            "item": [1] * 7,
            "sales": [10] * 7,
            "forecast": [5] * 7,
        }
    )
    costs = weekly_inventory_costs(df, "forecast", CostAssumptions(reorder_cost_per_order=0))

    assert costs["stockout_units"].iloc[0] > 0
    assert costs["stockout_cost"].iloc[0] > 0

