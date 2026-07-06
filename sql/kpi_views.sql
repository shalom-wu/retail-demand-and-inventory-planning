-- KPI views behind the inventory dashboard handoff.

CREATE OR REPLACE VIEW v_daily_sales AS
SELECT *
FROM read_csv_auto('outputs/daily_sales.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_store_summary AS
SELECT *
FROM read_csv_auto('outputs/store_summary.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_item_summary AS
SELECT *
FROM read_csv_auto('outputs/item_summary.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_model_metrics AS
SELECT *
FROM read_csv_auto('outputs/model_metrics.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_inventory_policy AS
SELECT *
FROM read_csv_auto('outputs/inventory_policy.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_inventory_cost_summary AS
SELECT *
FROM read_csv_auto('outputs/inventory_cost_summary.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_sku_difficulty AS
SELECT *
FROM read_csv_auto('outputs/sku_difficulty.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_forecast_error_by_store AS
SELECT
    store::INTEGER AS store,
    COUNT(*) AS validation_days,
    ROUND(AVG(ABS(gradient_boosting - sales)), 2) AS mae_units,
    ROUND(AVG(ABS(gradient_boosting - sales) / NULLIF(sales, 0)) * 100, 2) AS mape_pct,
    ROUND(SUM(gradient_boosting - sales), 2) AS bias_units
FROM validation_predictions
GROUP BY 1
ORDER BY mape_pct DESC;

CREATE OR REPLACE VIEW v_forecast_error_by_item AS
SELECT
    item::INTEGER AS item,
    COUNT(*) AS validation_days,
    ROUND(AVG(ABS(gradient_boosting - sales)), 2) AS mae_units,
    ROUND(AVG(ABS(gradient_boosting - sales) / NULLIF(sales, 0)) * 100, 2) AS mape_pct,
    ROUND(SUM(gradient_boosting - sales), 2) AS bias_units
FROM validation_predictions
GROUP BY 1
ORDER BY mape_pct DESC;
