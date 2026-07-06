# Data Manifest

This repo includes the raw Kaggle challenge files, modeled outputs, SQL checks, and Power BI-ready exports.

| File | Type | Shape / size | Used by | Notes |
|---|---|---:|---|---|
| `raw/train.csv` | Real public challenge data | 913,000 x 4, 16.5 MB | Python, SQL, tests | Daily sales at date-store-item grain, 2013-01-01 to 2017-12-31. |
| `raw/test.csv` | Real public challenge data | 45,000 x 4, 952.5 KB | Optional Kaggle-style scoring context | Future date-store-item rows without sales labels. |
| `raw/sample_submission.csv` | Real public challenge file | 45,000 x 2, 384.7 KB | Optional Kaggle-style scoring context | Included for source completeness. |
| `powerbi/fact_sales_sample.csv` | Real extract | 182,500 x 4, 3.3 MB | Power BI | 2017 slice of included train data for dashboard performance. |
| `powerbi/kpi_daily_sales.csv` | Derived aggregate | 1,826 x 2, 30.3 KB | Power BI | Daily total demand trend. |
| `powerbi/kpi_store_summary.csv` | Derived aggregate | 10 x 5, <1 KB | Power BI | Store-level demand volatility. |
| `powerbi/kpi_item_summary.csv` | Derived aggregate | 50 x 5, 3.3 KB | Power BI | Item-level demand volatility. |
| `powerbi/kpi_model_metrics.csv` | Derived model output | 3 x 5, <1 KB | Power BI | Forecast RMSE/MAPE/WMAPE/bias by model. |
| `powerbi/inventory_policy.csv` | Derived + assumed | 500 x 9, 65.0 KB | Power BI | Safety-stock and reorder-point recommendations. |
| `powerbi/inventory_cost_summary.csv` | Derived + assumed | 3 x 8, <1 KB | Power BI | Operating cost comparison using documented inventory assumptions. |
| `powerbi/sku_difficulty.csv` | Derived | 500 x 8, 51.8 KB | Power BI | Store-item forecast difficulty ranking. |

The official Kaggle competition is the canonical source. The fallback mirror metadata checked on 2026-07-06 returned license `MIT`; if publishing the full raw files publicly, review the active Kaggle competition terms as well.
