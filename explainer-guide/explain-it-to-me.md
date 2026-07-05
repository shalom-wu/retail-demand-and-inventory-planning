# Explain It To Me: Retail Demand Forecasting

## 1. Plain-English Walkthrough

### The business question

A retailer has to decide how much inventory to keep in each store. Too little
inventory means a customer wants to buy something and the shelf is empty. Too
much inventory means cash is tied up in stock that is sitting around.

This project asks: **can a better demand forecast help the retailer set smarter
reorder points?**

A **forecast** is an estimate of what will happen next. In this project, the
forecast is daily unit demand for each store and item.

A **reorder point** is the inventory level where the store should order more.
If the reorder point is too low, the store risks a stockout. If it is too high,
the store holds too much inventory.

### The data

The data comes from Kaggle's Store Item Demand Forecasting Challenge. It has
daily unit sales from 2013 through 2017 for 10 stores and 50 items. Each row
says: on this date, in this store, for this item, this many units sold.

The data is clean, but it is not complete business data. It does not include
price, margin, promotions, weather, stock-on-hand, supplier lead time, or whether
the shelf was actually empty.

### What was built

I built three things:

1. A data-quality and exploratory analysis layer.
2. A forecasting model that predicts daily store-item sales.
3. An inventory logic layer that converts forecast error into safety stock and
   reorder points.

**Safety stock** is extra inventory held as a buffer because forecasts are never
perfect. A more uncertain item needs more safety stock than a stable item.

The baseline forecast is simple: use the same date last year. That is called a
**seasonal naive** model. It is a fair baseline because retail demand is very
seasonal.

The stronger model is **gradient boosting**, a machine-learning method that
learns patterns from calendar features, recent sales, and historical lags. In
plain English, it asks: "Given what usually happens on this weekday, in this
month, for this store and item, and given recent sales, what should tomorrow's
sales look like?"

## 2. Explanation Versions

### 30-second version

I used a public Kaggle retail dataset to forecast daily demand for 10 stores and
50 items. A seasonal naive baseline had 19.9% WMAPE on the holdout period. A
gradient boosting model improved that to 11.0%. I then translated the forecast
error into safety stock and reorder points, showing that better forecasts reduce
stockout cost without just adding inventory everywhere.

### 2-minute version

The project starts with the business problem: stores lose money when products
are out of stock, but over-ordering ties up cash. I cleaned and checked the
Kaggle Store Item Demand Forecasting dataset, which has 913,000 daily sales rows
from 2013 to 2017. The data is clean at the date-store-item level, but it is
missing real-world fields like prices, promotions, inventory, and supplier lead
times.

I explored seasonality and found clear patterns: summer is stronger, weekends
are higher than weekdays, and some store-item pairs are much more volatile than
others. Then I compared a same-day-last-year forecast with a stronger model
using calendar and lag features. The stronger model improved WMAPE from 19.9%
to 11.0% on the final-quarter holdout.

The important part is that I did not stop at model accuracy. I converted model
uncertainty into safety stock, reorder points, and a simple cost model. That
makes the work more business-facing: the recommendation is dynamic SKU-level
safety stock for the hard-to-forecast items, not a generic inventory increase.

### 5-minute version

This is a forecasting and inventory project built around a realistic retail
decision. Forecasting by itself is useful, but the actual business decision is
how much inventory to hold and when to reorder.

The dataset is Kaggle's Store Item Demand Forecasting Challenge. It contains
daily sales for 10 stores and 50 items over five years. First, I checked whether
the data was usable. It has no missing values, no duplicate date-store-item
rows, no negative sales, and complete daily coverage. The main issue is not data
quality in the file. The issue is missing context: no inventory, no stockout
flags, no prices, no promotions, and no external drivers.

Then I looked for patterns a retailer could act on. Demand is seasonal, with
summer stronger than winter. Weekends are materially higher than weekdays.
Volume differs by store and item, and volatility differs by store-item pair.
That matters because a high-volume stable item and a low-volume erratic item
should not get the same safety-stock treatment.

For modeling, I used a seasonal naive baseline and a gradient boosting model.
The seasonal naive model predicts each day using the same day last year. The
gradient boosting model uses calendar fields, store and item ids, recent sales,
rolling averages, and prior-year lagged sales. On the holdout period, gradient
boosting was meaningfully better: 11.0% WMAPE versus 19.9% for seasonal naive.

Finally, I translated forecast error into inventory logic. The project assumes a
7-day lead time and a 95% service level. For each store-item pair, the model
estimates expected demand plus a safety-stock buffer based on forecast error.
Then it compares the policy against actual validation demand and estimates
stockout cost, holding cost, and reorder cost. The result is a practical
recommendation: start with dynamic safety stock where forecast error and demand
volatility are highest.

## 3. How The Code Actually Works

### What each file and folder does

- `data-sources.md`: explains the Kaggle source, the mirror fallback, and the
  assumptions behind the cost model.
- `src/retail_demand/config.py`: holds paths and business assumptions.
- `src/retail_demand/data.py`: loads the data, checks the schema, profiles data
  quality, and creates calendar and lag features.
- `src/retail_demand/modeling.py`: builds baseline forecasts, trains gradient
  boosting, and calculates MAPE, WMAPE, RMSE, and SKU-level error.
- `src/retail_demand/costs.py`: turns forecast uncertainty into safety stock,
  reorder points, and dollarized inventory costs.
- `src/retail_demand/viz.py`: creates the charts used in the reports and deck.
- `scripts/run_eda.py`: runs data-quality checks and exploratory analysis.
- `scripts/run_modeling.py`: trains models and creates inventory outputs.
- `scripts/build_deck.py`: builds the markdown strategy deck from outputs.
- `scripts/make_notebook.py`: creates the companion notebook.
- `reports/strategy_deck.md`: the 7-slide strategy deck.
- `outputs/`: generated tables and reports.
- `tests/`: small unit tests for the important logic.

Suggested reading order: `README.md`, `reports/strategy_deck.md`,
`outputs/model_report.md`, then `src/retail_demand/modeling.py` and
`src/retail_demand/costs.py`.

### Key functions in plain terms

- `load_sales()`: reads the Kaggle CSV and makes sure the expected columns are
  present.
- `profile_sales()`: checks row count, date range, stores, items, duplicates,
  missing values, and whether the daily grid is complete.
- `add_lag_features()`: adds recent-sales and prior-year features so the model
  can learn from history without looking into the future.
- `run_forecast_model()`: creates baseline forecasts, trains gradient boosting,
  and returns validation predictions and metrics.
- `safety_stock_units()`: calculates the extra buffer needed when forecast error
  is uncertain.
- `reorder_point_units()`: adds expected lead-time demand plus safety stock.
- `weekly_inventory_costs()`: estimates what stockouts, overstock, and reorder
  admin cost would look like under a forecast policy.

### How the model works conceptually

The model is trained on past rows. Each row contains the actual sales number and
features that would have been known at the time: date parts, store, item, recent
sales, rolling averages, and last year's sales.

Gradient boosting builds many small decision trees. Each tree tries to fix the
mistakes left by the trees before it. The final forecast is the combined answer
from those trees.

The code ties this to inventory in `costs.py`: forecast error becomes safety
stock, and safety stock plus expected demand becomes the reorder point.

### How to run the project

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python scripts/download_data.py
python scripts/run_all.py
pytest
```

### What I would point to first in an interview

I would start with `src/retail_demand/costs.py`, because it shows the bridge
from model metrics to business decisions. Then I would show
`src/retail_demand/modeling.py`, because it shows the baseline comparison and
the validation setup.

## 4. Anticipated Questions

### Why this dataset?

Because it is clean, public, and well-known, which makes it easy for an
interviewer to reproduce. It is not pretending to be secret client data. The
tradeoff is that it lacks real retail context like promotions and stockouts.

### Why this forecasting approach?

I started with seasonal naive because the data clearly has yearly seasonality.
Then I used gradient boosting because it handles nonlinear calendar and lag
patterns well without needing a very heavy deep-learning setup.

### What would you do differently with promotion or external data?

I would add promotion flags, price changes, holiday calendars, local events,
weather, and inventory-on-hand. Promotions and stockouts are especially
important because they can make observed sales different from true demand.

### How confident are you in the numbers?

I am confident in the model comparison on this dataset. I am directionally
confident in the inventory logic. I would not treat the dollar ROI as final
until a real retailer supplied actual item economics and operating constraints.

### Biggest limitation?

The data shows sales, not unmet demand. If a product stocked out, the sales file
does not show how many extra customers would have bought it.

### Walk me through this function.

For `weekly_inventory_costs()`: it groups validation predictions into weekly
store-item demand, adds safety stock based on forecast error, compares that
target to actual weekly sales, and assigns dollars to stockouts, holding cost,
and reorder cost.

## Glossary

- **Demand:** what customers want to buy.
- **Observed sales:** what actually sold. This can be lower than demand if the
  item was out of stock.
- **Forecast:** a prediction of future demand.
- **Seasonality:** a repeating pattern by time, such as weekends or summer peaks.
- **Seasonal naive:** a simple forecast that uses the same season in the past,
  such as the same day last year.
- **MAPE:** mean absolute percentage error; average percent miss of a forecast.
- **WMAPE:** weighted MAPE; total absolute error divided by total actual demand.
- **RMSE:** root mean squared error; penalizes bigger misses more heavily.
- **Safety stock:** extra inventory held as a buffer against uncertainty.
- **Reorder point:** inventory level where the retailer should order more.
- **Lead time:** time between placing an order and receiving it.
- **Service level:** probability target for having enough stock to meet demand.
- **Stockout:** when the store does not have enough inventory to meet demand.
- **Overstock:** inventory above what is needed.
- **Holding cost:** cost of keeping inventory on hand.
- **Gradient boosting:** a machine-learning method that combines many small
  decision trees to make better predictions.

