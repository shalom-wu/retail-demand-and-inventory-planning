from __future__ import annotations

import pandas as pd

from retail_demand.modeling import mape, metrics_frame, rmse, wmape


def test_metrics_are_reasonable_for_perfect_forecast() -> None:
    actual = pd.Series([10, 20, 30])
    forecast = pd.Series([10, 20, 30])

    assert rmse(actual, forecast) == 0
    assert mape(actual, forecast) == 0
    assert wmape(actual, forecast) == 0


def test_metrics_frame_sorts_by_wmape() -> None:
    actual = pd.Series([10, 20, 30])
    metrics = metrics_frame(
        actual,
        {
            "worse": pd.Series([5, 15, 25]),
            "better": pd.Series([10, 20, 30]),
        },
    )

    assert metrics.iloc[0]["model"] == "better"

