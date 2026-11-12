"""Download UNCTAD TRAINS non-tariff measure (NTM) summaries from WITS (World Bank) for Singapore and peers (Ch. 7).

WITS publishes, per country, the NTM coverage and frequency ratios of imports, the ten most imposed measures and the
ratios by sector. This script saves the page and parses those tables.
Output: data/raw/wits_ntm/<ISO3>.html, ntm_summary.csv, ntm_measures.csv, ntm_sectors.csv
Run: python scripts/fetch_wits_ntm.py
"""
import re
import time
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd
import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "wits_ntm"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "ec391-singapore/1.0 (university course project)"}
ECON = ["SGP", "MYS", "HKG", "VNM"]


class Tables(HTMLParser):
    """Collect every <table> as a list of rows of cell texts."""

    def __init__(self):
        super().__init__()
        self.tables, self.row, self.cell, self.in_cell = [], None, [], False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables.append([])
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th"):
            self.in_cell, self.cell = True, []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.in_cell = False
        elif tag == "tr" and self.row is not None and self.tables:
            if self.row:
                self.tables[-1].append(self.row)
            self.row = None

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)


def num(x):
    return float(re.sub(r"[%,]", "", x)) if re.search(r"\d", x or "") else None


def main():
    measures, sectors = [], []
    for iso in ECON:
        r = requests.get(f"https://wits.worldbank.org/tariff/non-tariff-measures/en/country/{iso}", headers=HEADERS,
                         timeout=120)
        r.raise_for_status()
        (OUT / f"{iso}.html").write_text(r.text, encoding="utf-8")
        p = Tables()
        p.feed(r.text)
        for t in p.tables:
            if not t:
                continue
            head = " ".join(t[0]).lower()
            body = [row for row in t[1:] if len(row) >= 4]
            if head.startswith("measure"):
                for row in body:
                    measures.append({"iso3": iso, "measure": row[0], "coverage": num(row[1]), "frequency": num(row[2]),
                                     "products": num(row[3])})
            elif head.startswith("sector"):
                for row in body:
                    sectors.append({"iso3": iso, "sector": row[0], "coverage": num(row[1]), "frequency": num(row[2]),
                                    "products": num(row[3])})
        print(f"{iso}: {len(p.tables)} tables")
        time.sleep(1)
    sec = pd.DataFrame(sectors)
    summ = sec[sec.sector == "All Import Products"].rename(columns={"coverage": "imports_coverage",
                                                                    "frequency": "imports_frequency"})
    summ = summ[["iso3", "imports_coverage", "imports_frequency", "products"]]
    summ = pd.concat([summ, pd.DataFrame({"iso3": [i for i in ECON if i not in set(summ.iso3)]})])
    summ.to_csv(OUT / "ntm_summary.csv", index=False)  # economies without TRAINS data appear with blanks
    pd.DataFrame(measures).to_csv(OUT / "ntm_measures.csv", index=False)
    pd.DataFrame(sectors).to_csv(OUT / "ntm_sectors.csv", index=False)
    print(f"{len(measures)} measure rows, {len(sectors)} sector rows")


if __name__ == "__main__":
    main()
