# Retail Demand And Inventory Planning

This repository uses Kaggle's Store Item Demand Forecasting Challenge dataset to model daily demand across stores and items, then converts forecast error into safety-stock and reorder-point recommendations.

## Project Summary

| Area | Details |
|---|---|
| Business question | Can better demand forecasts reduce stockout cost without adding unnecessary inventory? |
| Data | Five years of daily sales for 10 stores and 50 items from Kaggle's Store Item Demand Forecasting Challenge. |
| Methods | Data quality checks, seasonality analysis, baseline forecasting, gradient boosting, residual-based safety stock, reorder simulation. |
| Main outputs | Forecast report, inventory cost model, strategy deck, figures, Power BI-ready exports. |
| Tools | Python, pytest, DuckDB SQL, Power BI build documentation. |

## Key Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | The raw file is clean at the expected grain. | 913,000 rows, no missing values, no duplicate date-store-item rows, and complete daily coverage from 2013-01-01 to 2017-12-31. |
| 2 | Demand is strongly seasonal. | July is the highest-demand month, and weekend demand is about 23% higher than weekday demand. |
| 3 | Gradient boosting materially beats the seasonal naive baseline. | Holdout WMAPE improves to 11.0% versus 19.9% for seasonal naive. |
| 4 | The model improves the inventory policy under stated assumptions. | Validation-period operating cost falls by about $7.5K versus the seasonal naive policy. |
| 5 | The recommendation is selective inventory control. | High-volatility store-item pairs need dynamic safety stock; stable SKUs can run leaner. |

![Forecast comparison](https://raw.githubusercontent.com/shalom-wu/retail-demand-and-inventory-planning/main/reports/figures/forecast_comparison.png)

## Data

The project uses Kaggle's [Store Item Demand Forecasting Challenge](https://www.kaggle.com/competitions/demand-forecasting-kernels-only), a public competition dataset with daily unit sales across 10 stores and 50 items.

The raw files are included in `data/raw/`. Source notes, fallback download instructions, and caveats are documented in [data-sources.md](data-sources.md).

## Methodology

1. Validate the date-store-item grain and profile missingness, duplicates, and coverage.
2. Analyze demand seasonality by year, month, weekday, store, item, and store-item variance.
3. Compare seasonal naive, 28-day moving average, and gradient boosting models.
4. Evaluate forecasts with MAPE, WMAPE, RMSE, and forecast bias.
5. Convert residual uncertainty into safety stock using a 95% service level and 7-day lead time.
6. Simulate reorder decisions and dollarize stockout, holding, and reorder costs.

## Repository Contents

| Path | Purpose |
|---|---|
| [notebooks/](notebooks) | Companion analysis notebook. |
| [src/retail_demand/](src/retail_demand) | Data prep, modeling, inventory, and visualization logic. |
| [scripts/](scripts) | Download, pipeline, SQL export, and report scripts. |
| [outputs/](outputs) | Data quality, model, and inventory reports. |
| [reports/](reports) | Strategy deck and generated figures. |
| [sql/](sql) | DuckDB validation and KPI exports. |
| [power-bi/](power-bi) | Dashboard brief, model notes, DAX, refresh steps, and mockups. |
| [tests/](tests) | Unit tests for data, forecasting, and inventory behavior. |

## Reproduce

Requires Python 3.11+.

```bash
git clone https://github.com/shalom-wu/retail-demand-and-inventory-planning.git
cd retail-demand-and-inventory-planning
python -m venv .venv
pip install -r requirements.txt

python scripts/download_data.py
python scripts/run_all.py
python scripts/run_sql.py
pytest
```

The raw files used by the project are already included in `data/raw/`, so a reviewer can run the analysis without a Kaggle download.

## Reporting Layer

SQL validates the date-store-item grain, date coverage, store and item counts, prediction rows, and inventory-policy outputs. The SQL runner exports Power BI-ready files to `data/powerbi/`.

The [power-bi/](power-bi) folder contains dashboard specs, DAX, data model notes, refresh steps, manual build instructions, and mockups. No placeholder `.pbix` file is included.

## Limitations

- Sales are observed sales, not true demand; unmet demand is invisible when stockouts occurred.
- The dataset has no prices, margins, on-hand inventory, promotions, holidays, weather, supplier constraints, pack sizes, or lead-time fields.
- The ROI estimate is directional because the cost model uses planning assumptions.
- A production forecast would need recursive simulation and real replenishment constraints.

## License And Credit

MIT License. Copyright (c) 2026 Shalom Wu.

Data credit: Kaggle Store Item Demand Forecasting Challenge. See [data-sources.md](data-sources.md) for source notes, fallback download details, and usage caveats.
