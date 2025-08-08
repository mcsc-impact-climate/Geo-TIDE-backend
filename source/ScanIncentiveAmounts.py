"""
Date: 250807
Author: danikae
Purpose: Scan AFDC pages to identify any that list specific monetary incentive amounts.
"""

from pathlib import Path
import pandas as pd, re, time, requests
from bs4 import BeautifulSoup
from CommonTools import get_top_dir

top_dir  = Path(get_top_dir())

out_file  = "incentive_amount_scan.csv"
pause_sec = 1
timeout   = 15
headers   = {"User-Agent": "Mozilla/5.0"}

amount_re = re.compile(
    r"""(
        \$\s*[\d,]+(?:\.\d+)?\s*[kKmMbB]?     # $2,500  $5k  $1.2M
        |
        \b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*%    # 50%  12.5%
    )""",
    re.VERBOSE,
)

# ── folders & files ──────────────────────────────────────────────────
csv_dir  = top_dir / "data" / "incentives_and_regulations" / "state_level"
csv_paths = sorted(csv_dir.glob("*incentives.csv"))   # ← Path.glob(), not pathlib.glob()

# check we found something
print(f"Scanning {len(csv_paths)} CSVs under {csv_dir}")

# ── gather unique URLs ───────────────────────────────────────────────
source_urls: set[str] = set()
for csv_path in csv_paths:
    df = pd.read_csv(csv_path, usecols=["Source"] + (["Types"] if "Types" in pd.read_csv(csv_path, nrows=0).columns else []))

    # If a Types column is present, keep only rows that mention ‘Electricity’
    if "Types" in df.columns:
        df = df[df["Types"].str.contains("Electricity", case=False, na=False)]

    source_urls.update(df["Source"].dropna().unique())l

print(f"{len(source_urls)} unique incentive URLs discovered "
      f"from {len(csv_paths)} CSV files.\n")

# ─── scan each page ────────────────────────────────────────────────────
rows: list[dict] = []
for i, url in enumerate(sorted(source_urls), start=1):
    print(f"[{i}/{len(source_urls)}]  {url}", end="", flush=True)

    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # plain-text version of the main body
        text = soup.get_text(" ", strip=True)
        m = amount_re.search(text)

        rows.append(
            {
                "source_url": url,
                "monetary_amount_found": "yes" if m else "no",
                "first_match": m.group(0) if m else "",
            }
        )
        print("  →  yes" if m else "  →  no")
    except Exception as e:
        rows.append(
            {
                "source_url": url,
                "monetary_amount_found": f"error ({e.__class__.__name__})",
                "first_match": "",
            }
        )
        print(f"  →  ERROR: {e}")

    time.sleep(pause_sec)

# ─── write results ─────────────────────────────────────────────────────
pd.DataFrame(rows).to_csv(out_file, index=False)
print(f"\nScan complete – results saved to {out_file}")

