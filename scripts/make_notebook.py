"""Create a reproducible companion notebook."""

from __future__ import annotations

import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_demand import config


def main() -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(
            "# Retail Demand Forecasting & Inventory Optimization\n\n"
            "## tl;dr\n\n"
            "This notebook is the readable companion to the scripted pipeline. "
            "Run `python scripts/run_all.py` first to regenerate the outputs, then use this notebook to inspect the main data-quality, forecasting, and inventory-policy results."
        ),
        nbf.v4.new_markdown_cell(
            "## Context & Methods\n\n"
            "The raw dataset is Kaggle's Store Item Demand Forecasting Challenge. "
            "The training file has one row per date, store, and item. The analysis compares a seasonal naive baseline with a gradient boosting model and then turns forecast uncertainty into safety stock and reorder points.\n\n"
            "### Key Assumptions\n\n"
            "- Observed sales are treated as demand because stockout flags are unavailable.\n"
            "- Reorder logic assumes a 7-day lead time and 95% cycle service level.\n"
            "- Dollar values use planning assumptions for price, gross margin, holding cost, and reorder cost."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import pandas as pd\n"
            "from IPython.display import Markdown, display\n\n"
            "ROOT = Path.cwd()\n"
            "if not (ROOT / 'outputs').exists() and (ROOT.parent / 'outputs').exists():\n"
            "    ROOT = ROOT.parent\n"
            "OUTPUTS = ROOT / 'outputs'\n"
            "FIGURES = ROOT / 'reports' / 'figures'\n"
            "pd.set_option('display.max_columns', 30)"
        ),
        nbf.v4.new_markdown_cell("## Data"),
        nbf.v4.new_code_cell(
            "profile = pd.read_json(OUTPUTS / 'data_profile.json', typ='series')\n"
            "profile"
        ),
        nbf.v4.new_code_cell(
            "display(Markdown((OUTPUTS / 'data_quality_report.md').read_text(encoding='utf-8')))"
        ),
        nbf.v4.new_markdown_cell("## Results"),
        nbf.v4.new_code_cell(
            "metrics = pd.read_csv(OUTPUTS / 'model_metrics.csv')\n"
            "metrics"
        ),
        nbf.v4.new_code_cell(
            "costs = pd.read_csv(OUTPUTS / 'inventory_cost_summary.csv')\n"
            "costs"
        ),
        nbf.v4.new_code_cell(
            "sku = pd.read_csv(OUTPUTS / 'sku_difficulty.csv')\n"
            "sku.head(10)"
        ),
        nbf.v4.new_markdown_cell(
            "## Takeaways\n\n"
            "- The dataset is clean at the expected grain, but missing commercial context matters.\n"
            "- The seasonal naive model is a fair baseline because demand has strong annual seasonality.\n"
            "- The gradient boosting model improves validation accuracy and reduces simulated operating cost under the stated assumptions.\n"
            "- The main operating recommendation is not one global inventory buffer; it is SKU-level safety stock where volatility and forecast error are highest."
        ),
    ]
    notebook_path = config.ROOT / "notebooks" / "retail_demand_forecasting.ipynb"
    notebook_path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, notebook_path)
    print(f"Notebook written to {notebook_path}")


if __name__ == "__main__":
    main()
