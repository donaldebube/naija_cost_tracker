"""
Data Loader
============
Unified data loading utility for the Naija Cost Tracker.
Tries BigQuery first (if configured), falls back to CSV files.
Also runs data ingestion scripts if CSVs don't exist yet.
"""

import os
import pandas as pd
from pathlib import Path
import logging
import sys

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

USE_BIGQUERY = os.getenv("USE_BIGQUERY", "false").lower() == "true"


def _ensure_data_exists():
    """Run scrapers if CSV files don't exist yet."""
    scrapers_dir = BASE_DIR / "scrapers"
    sys.path.insert(0, str(BASE_DIR))

    if not (DATA_DIR / "inflation.csv").exists():
        log.info("Generating NBS seed data...")
        from scrapers.nbs_scraper import save_all
        save_all()

    if not (DATA_DIR / "exchange_rates.csv").exists():
        log.info("Generating exchange rate data...")
        from scrapers.cbn_scraper import save_exchange_data
        save_exchange_data()

    if not (DATA_DIR / "macro_indicators.csv").exists():
        log.info("Fetching World Bank data...")
        from scrapers.world_bank import save_macro_data
        save_macro_data()


def load_inflation() -> pd.DataFrame:
    _ensure_data_exists()
    df = pd.read_csv(DATA_DIR / "inflation.csv", parse_dates=["date"])
    return df


def load_food_prices() -> pd.DataFrame:
    _ensure_data_exists()
    df = pd.read_csv(DATA_DIR / "food_prices.csv", parse_dates=["date"])
    return df


def load_state_inflation() -> pd.DataFrame:
    _ensure_data_exists()
    df = pd.read_csv(DATA_DIR / "state_inflation.csv")
    return df


def load_exchange_rates() -> pd.DataFrame:
    _ensure_data_exists()
    df = pd.read_csv(DATA_DIR / "exchange_rates.csv", parse_dates=["date"])
    return df


def load_macro_indicators() -> pd.DataFrame:
    _ensure_data_exists()
    try:
        df = pd.read_csv(DATA_DIR / "macro_indicators.csv")
    except FileNotFoundError:
        from scrapers.world_bank import _fallback_macro_df
        df = _fallback_macro_df()
    return df


def load_live_rate() -> dict:
    try:
        df = pd.read_csv(DATA_DIR / "live_rate.csv")
        return df.iloc[0].to_dict()
    except Exception:
        return {"rate": 1640, "source": "cached", "date": "N/A"}


def compute_hardship_index(inflation_df: pd.DataFrame, fx_df: pd.DataFrame) -> pd.DataFrame:
    """
    Naija Hardship Index — composite score (0-100) combining:
      - Food inflation weight: 45%
      - Headline inflation weight: 30%
      - Exchange rate depreciation weight: 25%

    Score interpretation:
      0-30  → Stable
      31-50 → Moderate pressure
      51-70 → High pressure
      71-85 → Severe
      86-100 → Crisis
    """
    # Normalize inflation to 0-100 scale (max ~40% = 100)
    inf = inflation_df[["date", "headline_inflation_pct", "food_inflation_pct"]].copy()
    inf["inf_score"] = (inf["headline_inflation_pct"] / 40 * 100).clip(0, 100)
    inf["food_score"] = (inf["food_inflation_pct"] / 45 * 100).clip(0, 100)

    # Quarterly FX — map to monthly
    fx = fx_df[["date", "cbn_official_rate"]].copy()
    fx = fx.set_index("date").resample("MS").interpolate().reset_index()

    merged = pd.merge_asof(
        inf.sort_values("date"),
        fx.sort_values("date"),
        on="date",
        direction="backward"
    )

    # FX score: 360 NGN/USD = 0, 2000 NGN/USD = 100
    merged["fx_score"] = ((merged["cbn_official_rate"] - 360) / (2000 - 360) * 100).clip(0, 100)

    merged["hardship_index"] = (
        merged["food_score"] * 0.45 +
        merged["inf_score"] * 0.30 +
        merged["fx_score"] * 0.25
    ).round(1)

    def classify(score):
        if score <= 30: return "Stable 🟢"
        elif score <= 50: return "Moderate 🟡"
        elif score <= 70: return "High Pressure 🟠"
        elif score <= 85: return "Severe 🔴"
        else: return "Crisis ⚫"

    merged["hardship_label"] = merged["hardship_index"].apply(classify)
    return merged[["date", "hardship_index", "hardship_label", "inf_score", "food_score", "fx_score"]]