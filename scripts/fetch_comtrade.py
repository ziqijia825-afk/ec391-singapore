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
QUERIES = [(flow, year) for year in range(2004, 2025) for flow in ("X", "M")]  # every year, for the Sankey slider


def hs_chapters():
    """HS 2-digit chapter titles from UN Comtrade's reference file (used to label HS chapters in Ch. 4)."""
    r = requests.get("https://comtradeapi.un.org/files/v1/app/reference/HS.json", headers=HEADERS, timeout=120)
    r.raise_for_status()
    rows = [x for x in r.json()["results"] if len(str(x["id"])) == 2 and str(x["id"]).isdigit()]
    with open(OUT / "hs_chapters.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["chapter", "title"])
        for x in rows:
            w.writerow([x["id"], x["text"].split(" - ", 1)[-1]])
    print(f"hs_chapters.csv: {len(rows)} chapters")


def main():
    hs_chapters()
    for flow, year in QUERIES:
        if (OUT / f"sgp_{flow}_partners_{year}.csv").exists():
            continue
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
        time.sleep(1.5)


if __name__ == "__main__":
    main()
