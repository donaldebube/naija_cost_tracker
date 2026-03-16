"""
CBN & Exchange Rate Scraper
============================
Fetches USD/NGN rates from:
  1. ExchangeRate-API (live official/market rates)
  2. Embedded historical data (CBN official + parallel market)

CBN Official rates source: https://www.cbn.gov.ng/rates/ExchRateByCurrency.asp
Parallel market data: Aggregated from multiple public sources.

Usage:
    python scrapers/cbn_scraper.py
"""

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging

log = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Historical USD/NGN rates — Official CBN + Parallel Market
# Sources: CBN Annual Reports, public market trackers
# ---------------------------------------------------------------------------

EXCHANGE_RATE_DATA = {
    "date": [
        "2020-01-01","2020-04-01","2020-07-01","2020-10-01",
        "2021-01-01","2021-04-01","2021-07-01","2021-10-01",
        "2022-01-01","2022-04-01","2022-07-01","2022-10-01",
        "2023-01-01","2023-04-01","2023-07-01","2023-10-01",
        "2024-01-01","2024-04-01","2024-07-01","2024-10-01",
        "2025-01-01",
    ],
    "cbn_official_rate": [
        360, 386, 381, 379,
        379, 379, 411, 414,
        415, 416, 422, 439,
        461, 463, 770, 788,
        1490, 1300, 1480, 1601,
        1550,
    ],
    "parallel_market_rate": [
        360, 445, 470, 468,
        480, 484, 502, 570,
        573, 587, 618, 730,
        750, 760, 900, 1180,
        1530, 1390, 1560, 1700,
        1640,
    ],
    "fuel_price_per_litre_ngn": [
        145, 145, 151, 162,
        162, 162, 162, 165,
        165, 165, 180, 200,
        200, 230, 617, 700,
        855, 855, 897, 1020,
        1030,
    ],
}


def fetch_live_rate(api_key: str = None) -> dict:
    """
    Fetch live USD/NGN rate from ExchangeRate-API.
    Get a free API key at https://www.exchangerate-api.com (1500 req/month free)
    Falls back to latest historical value if no key provided.
    """
    if not api_key:
        api_key = os.getenv("EXCHANGE_RATE_API_KEY", "")

    if not api_key:
        log.warning("No EXCHANGE_RATE_API_KEY set — using cached rate")
        return {"rate": 1640, "source": "cached", "date": datetime.today().strftime("%Y-%m-%d")}

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        ngn_rate = data["conversion_rates"]["NGN"]
        return {
            "rate": round(ngn_rate, 2),
            "source": "ExchangeRate-API",
            "date": data["time_last_update_utc"],
        }
    except Exception as e:
        log.error(f"Failed to fetch live rate: {e}")
        return {"rate": 1640, "source": "cached", "date": datetime.today().strftime("%Y-%m-%d")}


def build_exchange_rate_df() -> pd.DataFrame:
    df = pd.DataFrame(EXCHANGE_RATE_DATA)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["spread"] = df["parallel_market_rate"] - df["cbn_official_rate"]
    df["spread_pct"] = ((df["spread"] / df["cbn_official_rate"]) * 100).round(1)
    df["devaluation_pct"] = df["cbn_official_rate"].pct_change() * 100
    df["label"] = df["date"].dt.strftime("%b %Y")

    # Purchasing power: how many NGN does $500 buy?
    df["usd_500_in_ngn"] = df["cbn_official_rate"] * 500

    log.info(f"Exchange rate data: {len(df)} rows")
    return df


def save_exchange_data():
    df = build_exchange_rate_df()
    df.to_csv(DATA_DIR / "exchange_rates.csv", index=False)
    log.info("Saved exchange_rates.csv")

    live = fetch_live_rate()
    pd.DataFrame([live]).to_csv(DATA_DIR / "live_rate.csv", index=False)
    log.info(f"Live rate: ₦{live['rate']} per $1 ({live['source']})")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    save_exchange_data()