# Data Sources

## Primary Dataset

This project uses Kaggle's **Store Item Demand Forecasting Challenge** dataset:

- Kaggle competition: https://www.kaggle.com/competitions/demand-forecasting-kernels-only
- Dataset slug: `demand-forecasting-kernels-only`
- Files used: `train.csv`, `test.csv`, `sample_submission.csv`
- Grain: one row per `date` x `store` x `item`
- Training coverage: daily sales from 2013-01-01 through 2017-12-31
- Scale: 913,000 training rows across 10 stores and 50 items

This is a well-known Kaggle competition dataset. It is useful for a portfolio
project because the structure is clean enough to focus on forecasting and
inventory decisions, but it should not be presented as proprietary client data
or as a live retailer's operating system.

## Access

The raw files needed to review and run the project are included under
`data/raw/`:

- `train.csv`
- `test.csv`
- `sample_submission.csv`

To refresh them from Kaggle, run:

```powershell
python scripts/download_data.py
```

The script uses the official Kaggle API, so a local Kaggle token must be
available at `%USERPROFILE%\.kaggle\kaggle.json`.

The downloader tries the official competition first. If Kaggle blocks the
competition download because the local account has not accepted the competition
rules, it falls back to a Kaggle-hosted mirror with matching file names and file
sizes:

- Mirror used as fallback: https://www.kaggle.com/datasets/akshaymairal/store-item-demand-forecasting-challenge

The metadata check for the mirror dataset on 2026-07-06 returned license
`MIT`. The official competition remains the canonical source; the mirror is a
practical fallback for reproducibility.

## External Benchmarks Used For Assumptions

The inventory cost model uses benchmark ranges, not company-specific finance
data. The assumptions are documented in `src/retail_demand/config.py` and the
generated `outputs/cost_assumptions.csv`.

- Inventory carrying cost: modeled at 25% of inventory value per year, within
  the commonly cited 20%-30% range for holding/carrying inventory.
- Stockout impact: modeled as lost gross margin on unmet demand. A retail
  out-of-stock benchmark is used only as context for why this matters, not as
  an input replacing the dataset's measured demand volatility.
- Reorder cost: modeled as a fixed order-processing cost per store-item order.
  This is a planning assumption because the Kaggle dataset has no supplier,
  freight, pack-size, or labor-cost fields.
