"""Markdown report and summary helpers."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def money(value: float) -> str:
    """Format a dollar value for reader-facing reports."""

    return f"${value:,.0f}"


def pct(value: float) -> str:
    """Format a percentage value."""

    return f"{value:.1f}%"


def units(value: float) -> str:
    """Format unit counts."""

    return f"{value:,.0f}"


def write_markdown(path: Path, text: str) -> None:
    """Write markdown with stable UTF-8 encoding."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    """Return a compact markdown table."""

    if max_rows is not None:
        df = df.head(max_rows)
    display = df.copy()
    display = display.astype(str).replace({"nan": ""})

    def clean(value: object) -> str:
        return str(value).replace("|", "\\|")

    headers = [clean(col) for col in display.columns]
    rows = [
        [clean(value) for value in row]
        for row in display.itertuples(index=False, name=None)
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)
