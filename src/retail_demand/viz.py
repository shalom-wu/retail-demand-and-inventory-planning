"""Charting helpers for reports and the strategy deck."""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}

COLORS = {
    "blue": "#5477C4",
    "blue_light": "#A3BEFA",
    "gold": "#B8A037",
    "orange": "#CC6F47",
    "orange_light": "#F0986E",
    "olive": "#71B436",
    "pink": "#BD569B",
    "neutral": "#7A828F",
}


def use_chart_theme() -> None:
    """Set a restrained, presentation-ready Seaborn theme."""

    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "figure.edgecolor": "none",
            "savefig.facecolor": TOKENS["surface"],
            "savefig.edgecolor": "none",
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "axes.grid": True,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "font.family": "sans-serif",
            "font.sans-serif": ["Aptos", "Inter", "Segoe UI", "DejaVu Sans", "Arial"],
        },
    )


def save_figure(fig: plt.Figure, output_path: Path) -> None:
    """Save and close a Matplotlib figure."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def format_date_axis(ax: plt.Axes, max_ticks: int = 6) -> None:
    """Format date axes with readable labels."""

    locator = mdates.AutoDateLocator(minticks=3, maxticks=max_ticks)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))


def add_header(fig: plt.Figure, ax: plt.Axes, title: str, subtitle: str) -> None:
    """Place a simple chart title and subtitle."""

    ax.set_title("")
    left = ax.get_position().x0
    fig.subplots_adjust(top=0.84)
    fig.text(left, 0.98, title, ha="left", va="top", fontsize=13, fontweight="semibold", color=TOKENS["ink"])
    fig.text(left, 0.925, subtitle, ha="left", va="top", fontsize=9, color=TOKENS["muted"])


def plot_weekly_sales(daily_sales: pd.DataFrame, output_path: Path) -> None:
    """Plot total weekly demand over time."""

    use_chart_theme()
    weekly = (
        daily_sales.set_index("date")["sales"].resample("W").sum().reset_index()
    )
    fig, ax = plt.subplots(figsize=(10, 4.8))
    sns.lineplot(data=weekly, x="date", y="sales", ax=ax, color=COLORS["blue"], linewidth=1.5)
    ax.set_xlabel("")
    ax.set_ylabel("Weekly units sold")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    format_date_axis(ax)
    add_header(
        fig,
        ax,
        "Weekly demand rises with a repeatable annual rhythm",
        "All stores and items, weekly unit sales from 2013 through 2017.",
    )
    save_figure(fig, output_path)


def plot_monthly_seasonality(df: pd.DataFrame, output_path: Path) -> None:
    """Plot average daily sales by month."""

    use_chart_theme()
    monthly = df.groupby(df["date"].dt.month)["sales"].mean().reset_index(name="avg_daily_sales")
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    sns.barplot(data=monthly, x="date", y="avg_daily_sales", ax=ax, color=COLORS["orange_light"], edgecolor=COLORS["orange"])
    ax.set_xlabel("Month")
    ax.set_ylabel("Average units per store-item day")
    add_header(
        fig,
        ax,
        "Demand is strongest in late spring and summer",
        "Average daily unit sales by calendar month across all store-item combinations.",
    )
    save_figure(fig, output_path)


def plot_weekday_pattern(df: pd.DataFrame, output_path: Path) -> None:
    """Plot average daily sales by weekday."""

    use_chart_theme()
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly = (
        df.assign(dayofweek=df["date"].dt.dayofweek)
        .groupby("dayofweek")["sales"]
        .mean()
        .reindex(range(7))
        .reset_index(name="avg_daily_sales")
    )
    weekly["weekday"] = [day_names[i] for i in weekly["dayofweek"]]
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    sns.barplot(data=weekly, x="weekday", y="avg_daily_sales", ax=ax, color=COLORS["blue_light"], edgecolor=COLORS["blue"])
    ax.set_xlabel("")
    ax.set_ylabel("Average units per store-item day")
    add_header(
        fig,
        ax,
        "Weekends carry materially higher unit demand",
        "Average daily sales by weekday; useful for store-level replenishment timing.",
    )
    save_figure(fig, output_path)


def plot_store_item_cv_heatmap(variance_table: pd.DataFrame, output_path: Path) -> None:
    """Plot store-item demand volatility as a heatmap."""

    use_chart_theme()
    matrix = variance_table.pivot(index="item", columns="store", values="cv").sort_index(ascending=False)
    fig, ax = plt.subplots(figsize=(8.6, 11))
    cmap = sns.blend_palette(["#FFFFFF", "#EAF1FE", "#A3BEFA", "#5477C4"], as_cmap=True)
    sns.heatmap(matrix, ax=ax, cmap=cmap, linewidths=0.3, linecolor="#FFFFFF", cbar_kws={"label": "Coefficient of variation"})
    ax.set_xlabel("Store")
    ax.set_ylabel("Item")
    add_header(
        fig,
        ax,
        "Volatility clusters by item more than by store",
        "Coefficient of variation for each store-item daily sales series.",
    )
    save_figure(fig, output_path)


def plot_forecast_comparison(validation: pd.DataFrame, output_path: Path) -> None:
    """Plot aggregate validation actuals versus forecasts."""

    use_chart_theme()
    daily = (
        validation.groupby("date", as_index=False)
        .agg(
            actual=("sales", "sum"),
            seasonal_naive=("seasonal_naive", "sum"),
            gradient_boosting=("gradient_boosting", "sum"),
        )
        .melt("date", var_name="series", value_name="units")
    )
    palette = {
        "actual": COLORS["ink"],
        "seasonal_naive": COLORS["neutral"],
        "gradient_boosting": COLORS["blue"],
    }
    fig, ax = plt.subplots(figsize=(10, 4.8))
    sns.lineplot(data=daily, x="date", y="units", hue="series", palette=palette, ax=ax, linewidth=1.3)
    ax.set_xlabel("")
    ax.set_ylabel("Daily units sold")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    format_date_axis(ax)
    ax.legend(title="", loc="upper left", bbox_to_anchor=(0, 1.03), ncol=3, frameon=False)
    add_header(
        fig,
        ax,
        "Gradient boosting tracks the validation quarter more tightly",
        "Aggregate daily demand in the October-December 2017 holdout window.",
    )
    save_figure(fig, output_path)


def plot_sku_error_scatter(sku_metrics: pd.DataFrame, output_path: Path) -> None:
    """Plot relationship between demand volatility and model error."""

    use_chart_theme()
    plot_df = sku_metrics.copy()
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    sns.scatterplot(
        data=plot_df,
        x="cv",
        y="mape",
        size="mean_sales",
        sizes=(24, 220),
        color=COLORS["orange_light"],
        edgecolor=COLORS["orange"],
        alpha=0.62,
        ax=ax,
        legend=False,
    )
    ax.set_xlabel("Demand volatility (coefficient of variation)")
    ax.set_ylabel("Validation MAPE")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(decimals=0))
    add_header(
        fig,
        ax,
        "High-variance SKUs are where forecast error concentrates",
        "Each point is one store-item series; bubble size reflects average daily unit demand.",
    )
    save_figure(fig, output_path)


def plot_cost_comparison(costs: pd.DataFrame, output_path: Path) -> None:
    """Plot stockout and overstock operating costs by forecast policy."""

    use_chart_theme()
    plot_df = costs.melt(
        id_vars="model",
        value_vars=["stockout_cost", "holding_cost"],
        var_name="cost_type",
        value_name="cost",
    )
    label_map = {"stockout_cost": "Stockout cost", "holding_cost": "Holding cost"}
    plot_df["cost_type"] = plot_df["cost_type"].map(label_map)
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    sns.barplot(
        data=plot_df,
        x="model",
        y="cost",
        hue="cost_type",
        palette={"Stockout cost": COLORS["orange_light"], "Holding cost": COLORS["blue_light"]},
        edgecolor=TOKENS["ink"],
        ax=ax,
    )
    ax.set_xlabel("")
    ax.set_ylabel("Validation-period cost")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("${x:,.0f}"))
    ax.legend(title="", loc="upper left", bbox_to_anchor=(0, 1.04), ncol=2, frameon=False)
    add_header(
        fig,
        ax,
        "Better forecasts reduce the expensive side of the tradeoff",
        "Validation-period policy simulation using lost-margin stockout cost and carrying cost.",
    )
    save_figure(fig, output_path)

