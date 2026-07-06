-- Checks that matter for a store-item-day forecasting dataset.

SELECT '01 train row count' AS check_name, COUNT(*)::VARCHAR AS result
FROM train_sales;

SELECT '02 unique date-store-item grain' AS check_name,
       CASE WHEN COUNT(*) = COUNT(DISTINCT (date, store, item)) THEN 'pass' ELSE 'fail' END AS result
FROM train_sales;

SELECT '03 date range' AS check_name,
       MIN(date)::VARCHAR || ' to ' || MAX(date)::VARCHAR AS result
FROM train_sales;

SELECT '04 store count' AS check_name, COUNT(DISTINCT store)::VARCHAR AS result
FROM train_sales;

SELECT '05 item count' AS check_name, COUNT(DISTINCT item)::VARCHAR AS result
FROM train_sales;

SELECT '06 missing or negative sales' AS check_name,
       COUNT(*)::VARCHAR AS result
FROM train_sales
WHERE sales IS NULL OR sales < 0;

SELECT '07 validation prediction rows' AS check_name, COUNT(*)::VARCHAR AS result
FROM validation_predictions;

SELECT '08 inventory policy rows' AS check_name, COUNT(*)::VARCHAR AS result
FROM inventory_policy;
