"""
Data Loader — Naija Cost Tracker
==================================
Unified data loading. Tries to refresh live exchange rate on every run.
All other data (inflation, food prices) updates when scrapers are re-run.
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
sys.path.insert(0, str(BASE_DIR))


def _ensure_data_exists():
    if not (DATA_DIR / "inflation.csv").exists():
        from scrapers.nbs_scraper import save_all
        save_all()
    if not (DATA_DIR / "exchange_rates.csv").exists():
        from scrapers.cbn_scraper import save_exchange_data
        save_exchange_data()


def load_inflation() -> pd.DataFrame:
    _ensure_data_exists()
    return pd.read_csv(DATA_DIR / "inflation.csv", parse_dates=["date"])


def load_food_prices() -> pd.DataFrame:
    _ensure_data_exists()
    return pd.read_csv(DATA_DIR / "food_prices.csv", parse_dates=["date"])


def load_state_inflation() -> pd.DataFrame:
    _ensure_data_exists()
    return pd.read_csv(DATA_DIR / "state_inflation.csv")


def load_exchange_rates() -> pd.DataFrame:
    _ensure_data_exists()
    df = pd.read_csv(DATA_DIR / "exchange_rates.csv", parse_dates=["date"])
    return df


def load_macro_indicators() -> pd.DataFrame:
    try:
        return pd.read_csv(DATA_DIR / "macro_indicators.csv")
    except FileNotFoundError:
        return pd.DataFrame({
            "year": [2020, 2021, 2022, 2023, 2024, 2025],
            "inflation_annual_pct": [13.2, 16.9, 19.6, 24.7, 33.2, 24.5],
            "gdp_growth_pct":       [-1.8,  3.4,  3.3,  2.9,  3.4,  3.7],
            "unemployment_pct":     [33.3, 33.3, 22.6, 20.0, 18.5, 17.2],
            "gdp_per_capita_usd":   [1970, 2150, 2095, 1470, 1340, 1210],
        })


def fetch_live_rate_now() -> dict:
    """Always attempt a live fetch — called at app startup."""
    try:
        from scrapers.cbn_scraper import fetch_live_rate
        live = fetch_live_rate()
        pd.DataFrame([live]).to_csv(DATA_DIR / "live_rate.csv", index=False)
        return live
    except Exception as e:
        log.error(f"Live rate fetch failed: {e}")
        return {"rate": 1400.0, "source": "CBN NFEM (March 2026)", "date": "2026-03-16", "is_live": False}


def load_live_rate() -> dict:
    try:
        df = pd.read_csv(DATA_DIR / "live_rate.csv")
        return df.iloc[0].to_dict()
    except Exception:
        return {"rate": 1400.0, "source": "CBN NFEM (March 2026)", "date": "2026-03-16", "is_live": False}


def compute_hardship_index(inflation_df: pd.DataFrame, fx_df: pd.DataFrame) -> pd.DataFrame:
    """
    Nigeria Hardship Index — composite economic stress score (0–100)

    Weights:
      Food inflation      45% — largest household expenditure
      Headline inflation  30% — overall price pressure
      FX depreciation     25% — import cost / purchasing power

    Normalization ceilings (calibrated to Nigeria's worst observed periods):
      Food inflation: 45% = 100
      Headline:       40% = 100
      FX rate:        ₦360 → ₦2000 range mapped to 0–100
    """
    inf = inflation_df[["date", "headline_inflation_pct", "food_inflation_pct"]].copy()
    inf["inf_score"]  = (inf["headline_inflation_pct"] / 40 * 100).clip(0, 100)
    inf["food_score"] = (inf["food_inflation_pct"]     / 45 * 100).clip(0, 100)

    fx = fx_df[["date", "cbn_official_rate"]].copy()
    fx = fx.set_index("date").resample("MS").interpolate(method="linear").reset_index()

    merged = pd.merge_asof(
        inf.sort_values("date"),
        fx.sort_values("date"),
        on="date", direction="backward"
    )

    merged["fx_score"] = (
        (merged["cbn_official_rate"] - 360) / (2000 - 360) * 100
    ).clip(0, 100)

    merged["hardship_index"] = (
        merged["food_score"] * 0.45 +
        merged["inf_score"]  * 0.30 +
        merged["fx_score"]   * 0.25
    ).round(1)

    def label(s):
        if s <= 30:  return "Stable 🟢"
        if s <= 50:  return "Moderate 🟡"
        if s <= 70:  return "High Pressure 🟠"
        if s <= 85:  return "Severe 🔴"
        return "Crisis ⚫"

    merged["hardship_label"] = merged["hardship_index"].apply(label)
    return merged[["date","hardship_index","hardship_label","inf_score","food_score","fx_score"]]