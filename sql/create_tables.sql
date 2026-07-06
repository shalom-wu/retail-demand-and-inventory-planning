-- DuckDB views over the included Kaggle sales files and modeled outputs.

CREATE OR REPLACE VIEW train_sales AS
SELECT
    CAST(date AS DATE) AS date,
    store::INTEGER AS store,
    item::INTEGER AS item,
    sales::INTEGER AS sales
FROM read_csv_auto('data/raw/train.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW validation_predictions AS
SELECT *
FROM read_csv_auto('outputs/validation_predictions.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW inventory_policy AS
SELECT *
FROM read_csv_auto('outputs/inventory_policy.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_fact_sales AS
SELECT *
FROM train_sales
WHERE date >= DATE '2017-01-01';
