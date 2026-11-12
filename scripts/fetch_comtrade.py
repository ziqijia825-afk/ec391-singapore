"""Download Singapore's reported merchandise trade by partner from UN Comtrade (public preview API, no key).

These are Singapore's own reports, which include re-exports (Ch. 3: partners, gravity with vs without re-exports).
Output: data/raw/comtrade/sgp_<flow>_partners_<year>.csv
Run: python scripts/fetch_comtrade.py
"""
import csv
import time
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "comtrade"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
HEADERS = {"User-Agent": "ec391-singapore/1.0 (university course project)"}
QUERIES = [("X", 2004), ("X", 2014), ("X", 2024), ("M", 2004), ("M", 2024)]


def main():
    for flow, year in QUERIES:
        r = requests.get(API, params={"reporterCode": 702, "period": year, "flowCode": flow, "cmdCode": "TOTAL",
                                      "includeDesc": "true"}, headers=HEADERS, timeout=120)
        r.raise_for_status()
        rows = r.json()["data"]
        path = OUT / f"sgp_{flow}_partners_{year}.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["partner_code", "partner_iso3", "partner", "value_usd"])
            for x in rows:
                if x.get("motCode", 0) not in (0, None) or x.get("partner2Code", 0) not in (0, None):
                    continue
                w.writerow([x["partnerCode"], x.get("partnerISO"), x.get("partnerDesc"), x["primaryValue"]])
        print(f"{path.name}: {len(rows)} records")
        time.sleep(2)


if __name__ == "__main__":
    main()
