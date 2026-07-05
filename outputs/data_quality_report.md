# Data Quality Report

## Dataset And Grain

The raw training file has **913,000 rows** and **4 columns**.
The intended grain is one row per calendar date, store, and item.

## Checks Performed

| check | evidence | status |
| --- | --- | --- |
| Expected grain | date x store x item | Pass |
| Duplicate grain rows | 0 | Pass |
| Missing values | 0 | Pass |
| Negative sales rows | 0 | Pass |
| Date coverage | 2013-01-01 to 2017-12-31 | Pass |
| Store/item coverage | 10 stores x 50 items | Pass |

## Findings

- The file is clean for the core forecasting task: no missing values, no duplicate
  date-store-item rows, no negative sales, and a complete daily grid.
- The biggest data-quality limitation is not a broken field. It is missing
  business context: the dataset has unit sales only, with no price, margin,
  on-hand inventory, stockout flags, promotions, supplier lead times, weather,
  holidays, or local events.
- Because sales are observed sales rather than true demand, a real stockout
  would censor demand. The Kaggle file does not tell us when that happened, so
  the model assumes historical sales are a good proxy for demand.

## Recommended Automated Tests

- Enforce uniqueness on `date`, `store`, and `item`.
- Reject negative sales and missing required fields.
- Check that each store-item series has continuous daily dates.
- Monitor row count by date if this became a recurring pipeline.
