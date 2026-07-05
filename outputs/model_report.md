# Modeling And Inventory Report

## Executive Summary

- **Best validation model:** `gradient_boosting` with WMAPE of **11.0%** and RMSE of **7.77** units at the store-item-day grain.
- **Model lift over seasonal naive:** gradient boosting improves WMAPE by **8.9 percentage points** versus the same-day-last-year baseline.
- **Inventory impact:** using the modeled reorder policy lowers validation-period operating cost by about **$7,486** versus the seasonal naive policy under the stated assumptions.

## Model Performance

| model | rmse | mape | wmape | bias_units |
| --- | --- | --- | --- | --- |
| gradient_boosting | 7.77 | 13.19 | 10.98 | 0.07 |
| moving_average_28 | 12.56 | 21.07 | 17.45 | 2.7 |
| seasonal_naive | 14.49 | 22.82 | 19.91 | -2.1 |

## Cost Translation

The policy simulation compares weekly demand to weekly forecasted units plus
safety stock. Stockouts are valued as lost gross margin; overstock is valued as
carrying cost and separately reported as working capital tied up in inventory.

| model | stockout_units | overstock_units | stockout_cost | holding_cost | avg_excess_inventory_value | reorder_cost | total_operating_cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gradient_boosting | 1603.97 | 234617.29 | 4491.11 | 2924.68 | 174.29 | 245000.0 | 252415.79 |
| moving_average_28 | 1081.04 | 475498.54 | 3026.91 | 5927.45 | 353.23 | 245000.0 | 253954.35 |
| seasonal_naive | 3894.58 | 320622.2 | 10904.81 | 3996.8 | 238.18 | 245000.0 | 259901.61 |

## Hard-To-Forecast Store-Item Series

These are not necessarily bad products. They are the series where volatility and
forecast error make static safety stock risky.

| store | item | mean_sales | cv | mape |
| --- | --- | --- | --- | --- |
| 7 | 5 | 13.3 | 0.35 | 30.6% |
| 7 | 41 | 15.2 | 0.34 | 28.4% |
| 7 | 27 | 15.0 | 0.33 | 28.5% |
| 6 | 5 | 14.8 | 0.33 | 28.6% |
| 7 | 4 | 16.0 | 0.34 | 24.9% |

## Stable Store-Item Series

These are better candidates for lean replenishment and lower safety stock.

| store | item | mean_sales | cv | mape |
| --- | --- | --- | --- | --- |
| 10 | 28 | 103.2 | 0.20 | 8.1% |
| 10 | 22 | 94.0 | 0.19 | 8.5% |
| 2 | 22 | 108.4 | 0.20 | 7.3% |
| 3 | 25 | 95.0 | 0.19 | 7.8% |
| 2 | 15 | 117.0 | 0.19 | 7.1% |

## Inventory Assumptions

- Unit price: **$8**
- Gross margin: **35%**
- Annual holding cost: **25%**
- Lead time: **7 days**
- Cycle service level: **95%**

The economics are directional. A real retailer should replace these planning
assumptions with item price, landed cost, supplier minimums, pack sizes,
inventory-on-hand, and observed stockout rates.
