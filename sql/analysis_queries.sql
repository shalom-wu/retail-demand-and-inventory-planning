-- Business-facing review queries for demand and inventory decisions.

SELECT *
FROM v_model_metrics;

SELECT *
FROM v_inventory_cost_summary;

SELECT *
FROM v_forecast_error_by_store
LIMIT 10;

SELECT *
FROM v_forecast_error_by_item
LIMIT 10;

SELECT *
FROM v_inventory_policy
ORDER BY reorder_point_value DESC
LIMIT 20;
