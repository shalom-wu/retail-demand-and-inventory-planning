# Retail Demand Forecasting Summary

## Executive Summary

**The model improves forecast accuracy enough to change inventory decisions.**
On the October-December 2017 validation period, gradient boosting cuts WMAPE
from 19.9% for seasonal naive to 11.0%. Under the planning cost assumptions,
that translates to about $7.5k lower operating cost over the validation window.

**Seasonality is real and operationally useful.** July is the strongest month,
weekends run about 23% above weekdays, and store 2 plus item 15 are the largest
volume contributors.

**The inventory answer is targeted safety stock.** High-variance store-item
series, such as store 7 item 5, need more dynamic reorder points. Stable,
high-volume items can be run with lower buffers.

## Evidence

- Raw data: 913,000 rows, 10 stores, 50 items, complete daily coverage.
- Best validation model: gradient boosting at 11.0% WMAPE and 7.77 RMSE.
- Seasonal naive baseline: 19.9% WMAPE and 14.49 RMSE.
- Modeled savings versus baseline: $7,486 validation-period operating cost.

## Recommendation

Start with SKU-level dynamic safety stock for the highest-risk store-item pairs,
then expand to centralized forecasting once promotion, inventory, supplier, and
pricing data are available.

## Caveat

The dollar model is intentionally transparent, not definitive. The Kaggle data
does not include actual inventory positions or item economics, so a real rollout
would replace the assumptions with finance and supply-chain data.

