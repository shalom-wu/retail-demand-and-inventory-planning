"""Run the full reproducible project pipeline."""

from __future__ import annotations

import subprocess
import sys


SCRIPTS = [
    "scripts/run_eda.py",
    "scripts/run_modeling.py",
    "scripts/build_deck.py",
    "scripts/make_notebook.py",
]


def main() -> None:
    for script in SCRIPTS:
        print(f"\n=== Running {script} ===")
        subprocess.run([sys.executable, script], check=True)


if __name__ == "__main__":
    main()

