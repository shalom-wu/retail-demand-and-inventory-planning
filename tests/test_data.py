from __future__ import annotations

import pandas as pd

from retail_demand.data import add_lag_features, profile_sales


def test_profile_sales_detects_complete_grid() -> None:
    dates = pd.date_range("2024-01-01", periods=3, freq="D")
    rows = [
        {"date": date, "store": store, "item": item, "sales": 10}
        for date in dates
        for store in [1, 2]
        for item in [1, 2]
    ]
    profile = profile_sales(pd.DataFrame(rows))

    assert profile.rows == 12
    assert profile.complete_daily_grid is True
    assert profile.duplicate_grain_rows == 0
    assert profile.missing_values == 0


def test_lag_features_use_prior_rows_only() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=10, freq="D"),
            "store": [1] * 10,
            "item": [1] * 10,
            "sales": list(range(10)),
        }
    )
    featured = add_lag_features(df)

    assert pd.isna(featured.loc[0, "lag_1"])
    assert featured.loc[1, "lag_1"] == 0
    assert featured.loc[7, "lag_7"] == 0

