# Retail Demand Forecasting & Inventory Optimization

Author: Shalom Wu (`shalomwu`)  
License: MIT

This project uses Kaggle's [Store Item Demand Forecasting Challenge](https://www.kaggle.com/competitions/demand-forecasting-kernels-only), a well-known public competition dataset with five years of daily unit sales across 10 stores and 50 items. I treat the business as **a multi-store retailer** deciding whether better demand forecasting can reduce stockouts without blindly adding excess inventory. The work starts with a same-day-last-year baseline, builds a stronger forecasting model, and turns forecast uncertainty into SKU-level safety stock and reorder-point recommendations.

## Key Findings

- The raw training file is clean at the expected grain: **913,000 rows**, no missing values, no duplicate date-store-item rows, and complete daily coverage from **2013-01-01 to 2017-12-31**.
- Demand is strongly seasonal. July is the highest-demand month at about **67.0 units per store-item day**, and weekend demand is about **23% higher** than weekday demand.
- The best model is gradient boosting with calendar and lag features. On the October-December 2017 holdout window, it reaches **11.0% WMAPE** and **7.77 RMSE**, versus **19.9% WMAPE** and **14.49 RMSE** for the seasonal naive baseline.
- Translating forecast error into inventory decisions, the modeled policy reduces validation-period operating cost by about **$7.5k** versus seasonal naive under the stated planning assumptions.
- The recommendation is not "hold more inventory everywhere." It is **dynamic safety stock for high-volatility store-item pairs**, while stable SKUs can run leaner.

## Methodology

1. Cleaned and profiled the Kaggle sales file at date-store-item grain.
2. Explored seasonality by year, month, weekday, store, item, and store-item variance.
3. Used `statsmodels` seasonal decomposition to separate aggregate trend, annual seasonality, and residual movement.
4. Compared seasonal naive, 28-day moving average, and gradient boosting models using MAPE, WMAPE, RMSE, and forecast bias.
5. Converted model residual uncertainty into safety stock using a 95% cycle service level and 7-day lead-time assumption.
6. Simulated weekly reorder decisions and dollarized stockout, holding, and reorder costs.

## Inventory Cost Assumptions

The Kaggle data has unit sales only, so the dollar model uses explicit planning assumptions:

- Unit price: `$8.00`
- Gross margin: `35%`
- Stockout cost: lost gross margin, or `$2.80` per unmet unit
- Unit cost: `$5.20`
- Annual inventory holding cost: `25%`, inside the commonly cited 20%-30% carrying-cost range from [Investopedia](https://www.investopedia.com/terms/c/carryingcostofinventory.asp)
- Reorder cost: `$35` per store-item weekly order
- Lead time: `7 days`
- Service level: `95%`

Retail out-of-stocks matter because they can cause lost sales and customer switching; the README uses the [Stockout](https://en.wikipedia.org/wiki/Stockout) summary and its cited Gruen/Corsten retail out-of-stock research as context, not as a replacement for this project's measured forecast errors.

## Repository Structure

```text
.
|-- data-sources.md
|-- notebooks/
|-- src/retail_demand/
|-- scripts/
|-- outputs/
|-- reports/
|   |-- strategy_deck.md
|   `-- figures/
|-- tests/
|-- requirements.txt
|-- README.md
`-- LICENSE
```

## Reproduce

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python scripts/download_data.py
python scripts/run_all.py
pytest
```

`scripts/download_data.py` tries the official Kaggle competition first. If the Kaggle account has not accepted the competition rules, it falls back to a Kaggle-hosted mirror with matching file names and file sizes: [akshaymairal/store-item-demand-forecasting-challenge](https://www.kaggle.com/datasets/akshaymairal/store-item-demand-forecasting-challenge).

The raw files used by the project are already included in `data/raw/`, so a
reviewer can run the analysis without a Kaggle download.

## SQL and Power BI layer

The [sql/](sql) folder adds DuckDB checks and KPI views over the included sales
data and Python model outputs. It validates the date-store-item grain, date
coverage, store/item counts, prediction output rows, and inventory-policy rows.

```powershell
python scripts/run_sql.py
```

The SQL runner exports Power BI-ready files to `data/powerbi/`: a 2017 sales
fact extract, daily sales, store/item summaries, model metrics, SKU difficulty,
inventory policy, and cost summary. The [power-bi/](power-bi) folder contains
dashboard specs, DAX, data model notes, refresh steps, manual build
instructions, and mockups. No `.pbix` is included yet; I did not create a
placeholder dashboard file.

## Main Artifacts

- [Data quality report](outputs/data_quality_report.md)
- [Modeling and inventory report](outputs/model_report.md)
- [Strategy deck](reports/strategy_deck.md)
- [Companion notebook](notebooks/retail_demand_forecasting.ipynb)

## Portfolio Use

**CV bullets**

- Built a retail demand forecasting and inventory policy project on 913K daily
  store-item sales rows, comparing baseline and machine-learning forecasts.
- Converted forecast error into safety stock, reorder-point, and operating-cost
  recommendations using explicit inventory assumptions.
- SQL-focused: Added DuckDB validation and KPI views for date-store-item grain,
  demand aggregation, model metrics, forecast error, and inventory policy.
- Power BI-focused: Prepared dashboard-ready tables and a three-page inventory
  planning dashboard build spec.

**LinkedIn description**

> Retail Demand Forecasting & Inventory Optimization - I built this project to
> connect forecasting accuracy to a business decision: how much safety stock
> should a retailer carry by store and item?

**Interview explanation**

> "Forecast accuracy only matters if it changes a decision. I used Python for
> forecasting and scenario logic, SQL for reproducible checks and KPI exports,
> and Power BI for model performance, SKU difficulty, and reorder priorities."

**Likely interview questions**

1. *Why not optimize only for RMSE?* Inventory decisions care about the cost of
   being wrong, so I translate errors into stockout and holding-cost tradeoffs.
2. *What is missing from the data?* Prices, true demand, on-hand inventory,
   promotions, supplier lead times, and pack sizes.
3. *How would this work in production?* Add promotion and holiday features,
   refresh forecasts on a schedule, and compare policies to actual outcomes.

## Limitations

- This is a public Kaggle competition dataset, not private retailer data.
- Sales are observed sales, not true demand. If a store stocked out, unmet demand is invisible.
- There are no prices, margins, on-hand inventory, promotions, holidays, weather, local events, supplier constraints, pack sizes, or lead-time fields.
- The validation setup represents a daily reforecast process with recent sales available. A frozen long-horizon production forecast would need recursive simulation.
- The ROI estimate is directional because the cost model uses assumptions. Before using this deck externally, I would want the real retailer's item prices, gross margins, supplier lead times, order costs, pack sizes, and target service levels.
