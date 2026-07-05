"""Project configuration and business assumptions."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

TRAIN_CSV = DATA_RAW / "train.csv"
TEST_CSV = DATA_RAW / "test.csv"

RANDOM_SEED = 42

# The Kaggle dataset has units sold but no prices, costs, on-hand inventory,
# lead times, or supplier terms. These assumptions translate units into a
# decision-ready inventory model without pretending to know a real retailer's
# private economics.
UNIT_PRICE = 8.00
GROSS_MARGIN_RATE = 0.35
UNIT_COST = UNIT_PRICE * (1 - GROSS_MARGIN_RATE)
ANNUAL_HOLDING_COST_RATE = 0.25
DAILY_HOLDING_COST_PER_UNIT = UNIT_COST * ANNUAL_HOLDING_COST_RATE / 365
REORDER_COST_PER_ORDER = 35.00
LEAD_TIME_DAYS = 7
SERVICE_LEVEL = 0.95
REVIEW_PERIOD_DAYS = 7

ASSUMPTION_NOTES = {
    "unit_price": "Planning placeholder because the Kaggle data has sales units only.",
    "gross_margin_rate": "Planning placeholder for general retail gross margin.",
    "annual_holding_cost_rate": "25% sits inside the commonly cited 20%-30% annual carrying-cost range.",
    "reorder_cost_per_order": "Fixed ordering/admin cost placeholder; supplier and freight data are unavailable.",
    "lead_time_days": "One-week replenishment cycle assumption for a multi-store retailer.",
    "service_level": "95% cycle service level for the base reorder-point scenario.",
}

