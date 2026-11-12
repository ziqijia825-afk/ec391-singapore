"""Download Singapore Department of Statistics (SingStat) Table Builder tables (official national data).

Used where international databases miss Singapore specifics: domestic exports vs re-exports (Ch. 3-4), Gini (Ch. 2),
FDI stock by source economy and industry, direct investment abroad (Ch. 6).
Output: data/raw/singstat/<table id>.csv (long: series_no, series, unit, period, value) + <id>.meta.txt
Run: python scripts/fetch_singstat.py [TABLE_ID ...]
"""
import csv
import sys
import time
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "singstat"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://tablebuilder.singstat.gov.sg/api/table/tabledata"
HEADERS = {"User-Agent": "ec391-singapore/1.0 (university course project)"}  # the API rejects the default UA
PAGE = 5000  # the API returns at most 5,000 data points per call; `offset` counts data points

TABLES = {
    "M451001": "Merchandise trade by commodity section incl. domestic exports and re-exports, monthly (Ch. 3)",
    "M451501": "Domestic exports by region and market, monthly (Ch. 3)",
    "M451511": "Re-exports by region and market, monthly (Ch. 3)",
    "17892": "Gini coefficient among resident employed households, 2000-2025 (Ch. 2)",
    "M810361": "Key indicators on household employment income, incl. Gini after transfers (Ch. 2)",
    "M083791": "Principal statistics of FDI in Singapore (Ch. 6)",
    "M083801": "FDI in Singapore by source economy, stock (Ch. 6)",
    "M084831": "FDI in Singapore by detailed industry, stock (Ch. 6)",
    "M085801": "FDI in Singapore by component, flows (Ch. 6)",
    "M082221": "Singapore's direct investment abroad, stock (Ch. 6)",
    "M084431": "Direct investment abroad by destination economy, stock (Ch. 6)",
    "M084441": "Direct investment abroad by industry abroad, stock (Ch. 6)",
    "M015731": "GDP at current prices by industry, S$ (Ch. 6 ratios)",
    "M355171": "Manufacturing output by cluster, EDB census (Ch. 9)",
    "M355181": "Manufacturing value added by cluster, EDB census (Ch. 9)",
    "M450981": "Electronic non-oil domestic exports, monthly (Ch. 9)",
}


def fetch(table_id):
    rows, meta, offset = {}, None, 0
    while True:
        for attempt in range(4):
            try:
                r = requests.get(f"{API}/{table_id}", params={"offset": offset, "limit": PAGE},
                                 headers=HEADERS, timeout=120)
                r.raise_for_status()
                data = r.json()["Data"]
                break
            except Exception as e:  # noqa: BLE001
                print(f"  retry {attempt + 1}: {e}", file=sys.stderr)
                time.sleep(3 * (attempt + 1))
        else:
            raise RuntimeError(f"failed: {table_id}")
        meta = meta or data
        got = 0
        for row in data.get("row") or []:
            key = row.get("seriesNo") or row["rowNo"]  # time-series tables use seriesNo, others rowNo
            entry = rows.setdefault(key, {"series": row["rowText"], "unit": row.get("uoM", ""), "values": {}})
            for col in row["columns"]:
                entry["values"][col["key"]] = col["value"]
                got += 1
        if got < PAGE:
            return meta, rows
        offset += PAGE
        time.sleep(0.3)


def main():
    ids = sys.argv[1:] or list(TABLES)
    for tid in ids:
        meta, rows = fetch(tid)
        with open(OUT / f"{tid}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["series_no", "series", "unit", "period", "value"])
            for no, e in rows.items():
                for period, value in e["values"].items():
                    w.writerow([no, e["series"], e["unit"], period, value])
        (OUT / f"{tid}.meta.txt").write_text(
            f"{meta.get('title')}\nSource: {(meta.get("datasource") or meta.get("dataSource"))}\nLast updated: {meta.get('dataLastUpdated')}\n"
            f"Downloaded: {meta.get('dateGenerated')}\nhttps://tablebuilder.singstat.gov.sg/table/TS/{tid}\n\n"
            f"{meta.get('footnote', '')}\n", encoding="utf-8")
        n = sum(len(e["values"]) for e in rows.values())
        print(f"{tid}: {len(rows)} series, {n} points  ({TABLES.get(tid, '')})")


if __name__ == "__main__":
    main()
