# Manual Build Instructions

1. Run `python scripts/run_sql.py`.
2. Open Power BI Desktop.
3. Load the CSV files in `data/powerbi/`.
4. Create the DAX measures in `dax_measures.md`.
5. Build three pages:
   - Executive KPI: cards for best WMAPE, total sales units, total operating cost; charts for model metrics and cost summary.
   - Diagnostic Analysis: demand trend, store and item volatility, SKU difficulty table.
   - Decision Support: reorder-point value ranking, safety stock ranking, and an assumptions caveat.
6. Add footer text: `Source: Kaggle Store Item Demand Forecasting Challenge; cost outputs use documented assumptions.`
7. Save as `power-bi/retail_demand_inventory.pbix`.

The images in `screenshots/` are mockups generated from the included data.
