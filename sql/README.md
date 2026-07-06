# SQL Layer - Demand, Forecast Error and Inventory KPIs

This folder adds a DuckDB layer on top of the included Kaggle sales data and the modeled Python outputs. SQL validates the date-store-item grain, recomputes core demand cuts, and exports Power BI-ready tables.

Run it from the project root:

```bash
python scripts/run_sql.py
```

Files run in order:

| File | Purpose |
|---|---|
| `create_tables.sql` | Creates views over `data/raw/train.csv`, validation predictions, and the inventory policy output. |
| `data_quality_checks.sql` | Checks grain, date coverage, store/item counts, negative sales, and output row counts. |
| `kpi_views.sql` | Defines demand, model, forecast-error, SKU difficulty, and inventory-policy views. |
| `analysis_queries.sql` | Prints the most relevant review cuts for model and inventory decisions. |

Exports written to `data/powerbi/`:

- `fact_sales_sample.csv` (2017 sales extract for dashboard use)
- `kpi_daily_sales.csv`
- `kpi_store_summary.csv`
- `kpi_item_summary.csv`
- `kpi_model_metrics.csv`
- `inventory_policy.csv`
- `inventory_cost_summary.csv`
- `sku_difficulty.csv`
