"""
World Bank API Client
======================
Fetches Nigeria macro indicators from the World Bank Open Data API.
No API key required — completely free public API.

Indicators fetched:
  - FP.CPI.TOTL.ZG  → Inflation, consumer prices (annual %)
  - NY.GDP.MKTP.KD.ZG → GDP growth (annual %)
  - SL.UEM.TOTL.ZS  → Unemployment rate
  - PA.NUS.FCRF      → Official exchange rate (LCU per USD)

World Bank API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581

Usage:
    python scrapers/world_bank.py
"""

import requests
import pandas as pd
from pathlib import Path
import logging

log = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

WB_BASE = "https://api.worldbank.org/v2"
COUNTRY = "NG"  # Nigeria ISO code

INDICATORS = {
    "FP.CPI.TOTL.ZG": "inflation_annual_pct",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "SL.UEM.TOTL.ZS": "unemployment_pct",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
}


def fetch_indicator(indicator_code: str, col_name: str, start_year: int = 2015) -> pd.DataFrame:
    """Fetch a single World Bank indicator for Nigeria."""
    url = f"{WB_BASE}/country/{COUNTRY}/indicator/{indicator_code}"
    params = {
        "format": "json",
        "per_page": 100,
        "mrv": 10,  # Most recent 10 values
        "date": f"{start_year}:2024",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if len(data) < 2 or not data[1]:
            log.warning(f"No data returned for {indicator_code}")
            return pd.DataFrame()

        records = [
            {"year": int(item["date"]), col_name: item["value"]}
            for item in data[1]
            if item["value"] is not None
        ]
        df = pd.DataFrame(records).sort_values("year")
        log.info(f"Fetched {len(df)} rows for {indicator_code}")
        return df

    except Exception as e:
        log.error(f"Failed to fetch {indicator_code}: {e}")
        return pd.DataFrame()


def fetch_all_indicators() -> pd.DataFrame:
    """Fetch all indicators and merge into one DataFrame."""
    dfs = []
    for code, name in INDICATORS.items():
        df = fetch_indicator(code, name)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        log.warning("No World Bank data fetched — using embedded fallback")
        return _fallback_macro_df()

    from functools import reduce
    merged = reduce(lambda left, right: pd.merge(left, right, on="year", how="outer"), dfs)
    return merged.sort_values("year")


def _fallback_macro_df() -> pd.DataFrame:
    """Fallback macro data if World Bank API is unreachable."""
    return pd.DataFrame({
        "year": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
        "inflation_annual_pct": [9.0, 15.7, 16.5, 12.1, 11.4, 13.2, 16.9, 19.6, 24.7, 33.2],
        "gdp_growth_pct": [2.7, -1.6, 0.8, 1.9, 2.2, -1.8, 3.4, 3.3, 2.9, 3.2],
        "unemployment_pct": [8.0, 13.9, 16.5, 23.1, 23.1, 33.3, 33.3, 22.6, 20.0, 18.5],
        "gdp_per_capita_usd": [2640, 2175, 1970, 2030, 2230, 1970, 2150, 2095, 1470, 1340],
    })


def save_macro_data():
    df = fetch_all_indicators()
    df.to_csv(DATA_DIR / "macro_indicators.csv", index=False)
    log.info(f"Saved macro_indicators.csv — {len(df)} rows")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    save_macro_data()