"""Download World Bank data (WDI + WGI) for ALL economies, 2004-2024.

Run by the "Fetch data" GitHub Actions workflow (GitHub's servers can reach the World Bank API).
Output: data/raw/wdi/<indicator>.csv (long format: iso3, country, year, value) + countries.csv metadata.
All economies are kept so we can compute global and regional rankings.
"""
import csv
import sys
import time
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "wdi"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://api.worldbank.org/v2"
YEARS = "2004:2024"

# (indicator code, source id, who uses it)
INDICATORS = [
    # Ch. 2 - Member A
    ("NY.GDP.MKTP.CD", 2, "A ch2 GDP current US$"),
    ("NY.GDP.MKTP.PP.CD", 2, "A ch2 GDP PPP current intl $"),
    ("NY.GDP.PCAP.CD", 2, "A ch2 GDP per capita current US$"),
    ("NY.GDP.PCAP.PP.CD", 2, "A ch2 GDP per capita PPP"),
    ("NY.GDP.MKTP.KD.ZG", 2, "A ch2 real GDP growth %"),
    ("SI.POV.GINI", 2, "A ch2 Gini index"),
    ("SI.POV.DDAY", 2, "A ch2 poverty headcount $2.15/day"),
    ("LP.LPI.OVRL.XQ", 2, "A ch2 Logistics Performance Index overall"),
    # Ch. 2 - Worldwide Governance Indicators (source 3): estimate and percentile rank
    *[(f"{d}.{m}", 3, f"A ch2 WGI {d} {m}")
      for d in ("VA", "PV", "GE", "RQ", "RL", "CC") for m in ("EST", "PER.RNK")],
    # Ch. 1, 3, 4 - Member B
    ("SP.POP.TOTL", 2, "B ch1 population"),
    ("SP.DYN.LE00.IN", 2, "B ch1 life expectancy"),
    ("SE.ADT.LITR.ZS", 2, "B ch1 adult literacy"),
    ("NE.TRD.GNFS.ZS", 2, "B ch3 trade % of GDP"),
    ("NE.EXP.GNFS.CD", 2, "B ch3 exports of goods and services"),
    ("NE.IMP.GNFS.CD", 2, "B ch3 imports of goods and services"),
    ("BX.GSR.MRCH.CD", 2, "B ch3 goods exports (BoP)"),
    ("BM.GSR.MRCH.CD", 2, "B ch3 goods imports (BoP)"),
    ("BX.GSR.NFSV.CD", 2, "B ch3 services exports (BoP)"),
    ("BM.GSR.NFSV.CD", 2, "B ch3 services imports (BoP)"),
    ("NY.GDP.TOTL.RT.ZS", 2, "B ch4 natural resource rents % of GDP"),
    # Ch. 6 - Member C
    ("BX.KLT.DINV.CD.WD", 2, "C ch6 FDI net inflows US$"),
    ("BX.KLT.DINV.WD.GD.ZS", 2, "C ch6 FDI net inflows % of GDP"),
    ("BM.KLT.DINV.CD.WD", 2, "C ch6 FDI net outflows US$"),
    ("BM.KLT.DINV.WD.GD.ZS", 2, "C ch6 FDI net outflows % of GDP"),
    ("NE.GDI.FTOT.CD", 2, "C ch6 gross fixed capital formation US$"),
]


def get(url, params):
    for attempt in range(5):
        try:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            print(f"  retry {attempt + 1}: {e}", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"failed: {url}")


def fetch_paged(url, params):
    rows, page = [], 1
    while True:
        meta, data = get(url, {**params, "page": page, "per_page": 20000, "format": "json"})[:2]
        rows += data or []
        if page >= int(meta.get("pages", 1)):
            return rows
        page += 1


def main():
    countries = fetch_paged(f"{API}/country", {})
    with open(OUT / "countries.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["iso3", "name", "region_id", "region", "income", "is_aggregate"])
        for c in countries:
            w.writerow([c["id"], c["name"], c["region"]["id"], c["region"]["value"],
                        c["incomeLevel"]["value"], c["region"]["value"] == "Aggregates"])
    print(f"countries.csv: {len(countries)} rows")

    failed = []
    for code, source, note in INDICATORS:
        # WGI codes changed names in some API versions, so try the alternative spelling too
        candidates = [code] + ([f"GOV_WGI_{code}"] if source == 3 else [])
        rows = None
        for cand in candidates:
            try:
                rows = fetch_paged(f"{API}/country/all/indicator/{cand}", {"date": YEARS, "source": source})
                if rows:
                    break
            except (RuntimeError, ValueError, KeyError) as e:
                print(f"  {cand} not available: {e}", file=sys.stderr)
        if not rows:
            print(f"FAILED {code}", file=sys.stderr)
            failed.append(code)
            continue
        with open(OUT / f"{code}.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["iso3", "country", "year", "value"])
            for r in rows:
                w.writerow([r["countryiso3code"] or r["country"]["id"], r["country"]["value"],
                            r["date"], "" if r["value"] is None else r["value"]])
        n = sum(r["value"] is not None for r in rows)
        print(f"{code}: {len(rows)} rows, {n} non-empty  ({note})")
        time.sleep(0.5)

    if failed:
        print("Failed indicators:", ", ".join(failed), file=sys.stderr)


if __name__ == "__main__":
    main()
