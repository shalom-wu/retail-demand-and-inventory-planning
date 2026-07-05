"""Download the Kaggle Store Item Demand Forecasting data."""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
COMPETITION = "demand-forecasting-kernels-only"
DATASET_MIRROR = "akshaymairal/store-item-demand-forecasting-challenge"


def _extract_zip(zip_path: Path) -> None:
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(RAW_DIR)


def _download_competition() -> None:
    """Try the official competition source first."""

    cmd = [
        sys.executable,
        "-m",
        "kaggle",
        "competitions",
        "download",
        "-c",
        COMPETITION,
        "-p",
        str(RAW_DIR),
    ]
    subprocess.run(cmd, check=True)
    _extract_zip(RAW_DIR / f"{COMPETITION}.zip")


def _download_dataset_mirror() -> None:
    """Download a Kaggle-hosted mirror when competition rules block access."""

    cmd = [
        sys.executable,
        "-m",
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET_MIRROR,
        "-p",
        str(RAW_DIR),
    ]
    subprocess.run(cmd, check=True)
    _extract_zip(RAW_DIR / "store-item-demand-forecasting-challenge.zip")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _download_competition()
    except subprocess.CalledProcessError as exc:
        print(
            "Official competition download failed. "
            "Trying the Kaggle-hosted dataset mirror instead.",
            file=sys.stderr,
        )
        print(f"Competition error: {exc}", file=sys.stderr)
        _download_dataset_mirror()

    expected = ["train.csv", "test.csv", "sample_submission.csv"]
    missing = [name for name in expected if not (RAW_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing Kaggle files after download: {missing}")

    print(f"Downloaded Kaggle files to {RAW_DIR}")


if __name__ == "__main__":
    main()
