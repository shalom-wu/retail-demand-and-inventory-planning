# Data Model

Load these files from `data/powerbi/`:

| Table | File | Grain |
|---|---|---|
| `fact_sales_sample` | `fact_sales_sample.csv` | Date-store-item sales rows for 2017. |
| `kpi_daily_sales` | `kpi_daily_sales.csv` | One row per date. |
| `kpi_store_summary` | `kpi_store_summary.csv` | One row per store. |
| `kpi_item_summary` | `kpi_item_summary.csv` | One row per item. |
| `kpi_model_metrics` | `kpi_model_metrics.csv` | One row per model. |
| `inventory_policy` | `inventory_policy.csv` | One row per store-item. |
| `inventory_cost_summary` | `inventory_cost_summary.csv` | One row per model. |
| `sku_difficulty` | `sku_difficulty.csv` | One row per store-item. |

Relationships:

| From | To | Cardinality |
|---|---|---|
| `fact_sales_sample[store]` | `kpi_store_summary[store]` | many-to-one |
| `fact_sales_sample[item]` | `kpi_item_summary[item]` | many-to-one |

For `inventory_policy` and `sku_difficulty`, create a calculated key in Power Query or DAX: `store_item = store & "-" & item`, then relate the two tables on that key if you want cross-filtering.
