# DAX Measures

```DAX
Total Sales Units = SUM(fact_sales_sample[sales])

Avg Daily Sales = AVERAGE(fact_sales_sample[sales])

Best WMAPE =
MIN(kpi_model_metrics[wmape])

Total Operating Cost =
SUM(inventory_cost_summary[total_operating_cost])

Total Reorder Point Value =
SUM(inventory_policy[reorder_point_value])

Avg Safety Stock Units =
AVERAGE(inventory_policy[safety_stock_units])
```

Format WMAPE as a percentage-like number if using the existing 0-100 field values. Cost fields are planning estimates, not observed finance actuals.
