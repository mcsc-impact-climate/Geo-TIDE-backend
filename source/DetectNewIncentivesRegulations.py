#!/usr/bin/env python3
"""
Date: 250807
Author: danikae
Purpose: List every AFDC law / incentive whose `enacted_date`
is within the past 2 years and save the result to CSV.

Note: Need to obtain a 40-character NREL key from https://developer.nrel.gov/signup, then export as an env variable NREL_API_KEY.
  export NREL_API_KEY="YOUR_40_CHAR_KEY"
"""

import os, sys, json, datetime as dt
import requests, pandas as pd
from dateutil.relativedelta import relativedelta

# ── user settings ────────────────────────────────────────────────────────────
API_KEY   = os.getenv("NREL_API_KEY", "DEMO_KEY")      # replace or export
API_URL   = "https://developer.nrel.gov/api/transportation-incentives-laws/v1.json"
LOOKBACK  = relativedelta(years=2)                     # change if needed
OUT_FILE  = "afdc_new_laws_last_2_years.csv"
KEEP_COLS = ["id", "state", "title", "afdc_url",
             "enacted_date", "significant_update_date", "type"]
# ─────────────────────────────────────────────────────────────────────────────

def fetch_all_laws(limit: int = 5000) -> pd.DataFrame:
    """Return a DataFrame of the entire AFDC catalogue."""
    r = requests.get(API_URL, params={"api_key": API_KEY, "limit": limit}, timeout=30)
    r.raise_for_status()
    data = r.json()

    # Accept any of the common response shapes
    if isinstance(data, list):
        laws = data
    elif isinstance(data, dict) and isinstance(data.get("result"), list):
        laws = data["result"]
    elif isinstance(data, dict) and "laws" in data.get("result", {}):
        laws = data["result"]["laws"]
    else:
        raise ValueError("Unexpected API response:\n" + json.dumps(data)[:400])

    return pd.DataFrame(laws)

def main() -> None:
    print("Downloading AFDC catalogue …", flush=True)
    df = fetch_all_laws()

    # Parse dates
    for col in ("enacted_date", "significant_update_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.tz_localize(None)

    # Build the direct URL column
    df["afdc_url"] = df["id"].apply(lambda i: f"https://afdc.energy.gov/laws/{i}")

    # Filter to last 2 years
    cutoff = dt.datetime.today() - LOOKBACK
    recent = df[df["enacted_date"] >= cutoff].copy()

    if recent.empty:
        print(f"No new laws enacted since {cutoff.date():%Y-%m-%d} 🎉")
        return

    recent.sort_values("enacted_date", ascending=False, inplace=True)
    recent.to_csv(OUT_FILE,
                  columns=[c for c in KEEP_COLS if c in recent.columns],
                  index=False)

    print(f"\n🚀  Found {len(recent)} laws/incentives enacted since {cutoff.date():%Y-%m-%d}")
    print(f"    Saved to {OUT_FILE}\n")
    print(recent[KEEP_COLS].head(10).to_string(index=False))

if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as e:
        sys.exit(f"HTTP {e.response.status_code}: {e.response.text[:200]}…")
    except Exception as exc:
        sys.exit(f"Error: {exc}")
