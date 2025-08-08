"""
Date: 250807
Author: danikae
Purpose: Remove expired incentives and regulations from csv files
"""

import time, re, shutil, datetime, pathlib
import pandas as pd
import requests
from bs4 import BeautifulSoup
from CommonTools import get_top_dir

# ─── CSVs to clean ────────────────────────────────────────────────────────────
files = [
    "emissions_incentives.csv",
    "emissions_regulations.csv",
    "fuel_use_incentives.csv",
    "fuel_use_regulations.csv",
    "infrastructure_incentives.csv",
    "infrastructure_regulations.csv",
    "vehicle_purchase_incentives.csv",
    "vehicle_purchase_regulations.csv",
]

top_dir = get_top_dir()

# ─── user-configurable settings ───────────────────────────────────────────────
PAUSE_SEC = 1.5          # courteous crawl delay
TIMEOUT   = 15           # per-request timeout (s)
HEADERS   = {"User-Agent": "Mozilla/5.0"}
PATTERN   = re.compile(r"\b(Expired|Archived):", re.I)
# ──────────────────────────────────────────────────────────────────────────────


def afdc_status(url: str) -> str:
    """Return 'expired', 'archived', 'active', or 'check_manual (…)'. """
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        h2_text = " ".join(
            h.get_text(" ", strip=True)
            for h in BeautifulSoup(r.text, "html.parser").select("h2")
        )
        m = PATTERN.search(h2_text)
        return m.group(1).lower() if m else "active"
    except Exception as e:
        return f"check_manual ({e.__class__.__name__})"


def process_file(csv_path: pathlib.Path) -> int:
    """Scan one CSV; drop expired/archived rows; return number of rows removed."""
    if not csv_path.exists():
        print(f"⚠️  {csv_path} not found – skipping.\n")
        return 0

    df = pd.read_csv(csv_path)
    total = len(df)
    to_drop_info = []  # (original_idx, url, status)

    print(f"\n=== Cleaning {csv_path} ({total} links) ===\n")
    for i, (orig_idx, url) in enumerate(df["Source"].items(), start=1):
        print(f"[{i:>{len(str(total))}}/{total}] {url}", end="", flush=True)
        status = afdc_status(url)
        print(f"  →  {status}")
        if status in {"expired", "archived"}:
            to_drop_info.append((orig_idx, url, status))
        time.sleep(PAUSE_SEC)

    if not to_drop_info:
        print("No expired or archived links found — file left unchanged.\n")
        return 0

    # ── back up & overwrite ───────────────────────────────────────────────────
    backup = csv_path.with_suffix(f".bak_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv")
    shutil.copy2(csv_path, backup)

    drop_indices = [idx for idx, _, _ in to_drop_info]
    df.drop(index=drop_indices, inplace=True)
    df.reset_index(drop=True).to_csv(csv_path, index=False)

    # ── summary ───────────────────────────────────────────────────────────────
    print(f"\nRemoved {len(to_drop_info)} rows; cleaned file saved back to {csv_path}")
    print(f"Backup written to {backup}")
    print("Rows removed (1-based index in *original* file):")
    for idx, url, status in to_drop_info:
        print(f"  • {idx + 1}: {url}   [{status}]")
    print()  # blank line after each file

    return len(to_drop_info)


def main() -> None:
    total_removed = 0
    csv_dir = pathlib.Path(top_dir) / "data" / "incentives_and_regulations" / "state_level"
    for fname in files:
        csv_path = csv_dir / fname
        total_removed += process_file(pathlib.Path(csv_path))

    print("=== All files processed ===")
    print(f"Total rows removed across all CSVs: {total_removed}")


if __name__ == "__main__":
    main()
