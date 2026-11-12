"""Download World Bank data (WDI + WGI + B-READY) for ALL economies, 2004-2025.

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
YEARS = "2004:2025"  # charts use 2004-2024; 2025 is here for WGI and B-READY, whose latest editions are dated 2025

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
    # Ch. 2 - Worldwide Governance Indicators (source 3): estimate (-2.5..2.5) and governance score (0-100).
    # The API serves them as GOV_WGI_XX.EST / GOV_WGI_XX.SC; percentile ranks (PER.RNK) are no longer served.
    *[(f"{d}.{m}", 3, f"A ch2 WGI {d} {m}")
      for d in ("VA", "PV", "GE", "RQ", "RL", "CC") for m in ("EST", "SC")],
    # Ch. 2 - B-READY: every IC.BRE.* indicator in WDI is added at run time (see discover()).
    # Ch. 2 - legacy Doing Business (source 1, discontinued 2021): overall score (DB17-20 methodology) and rank
    ("IC.BUS.EASE.DFRN.XQ.DB1719", 1, "A ch2 Doing Business score, DB17-20 methodology"),
    ("IC.BUS.EASE.XQ", 1, "A ch2 Doing Business rank (1 = most business-friendly)"),
    # Ch. 1, 3, 4 - Member B
    ("SP.POP.TOTL", 2, "B ch1 population"),
    ("SP.DYN.LE00.IN", 2, "B ch1 life expectancy"),
    ("SE.ADT.LITR.ZS", 2, "B ch1 adult literacy"),
    ("SE.TER.ENRR", 2, "B ch1 tertiary enrolment, gross %"),
    ("SE.SEC.ENRR", 2, "B ch1 secondary enrolment, gross %"),
    ("SE.XPD.TOTL.GD.ZS", 2, "B ch1 government education spending % of GDP"),
    ("AG.LND.TOTL.K2", 2, "B ch1 land area km2"),
    ("AG.LND.ARBL.HA.PC", 2, "B ch4 arable land hectares per person"),
    ("EN.POP.DNST", 2, "B ch1 population density"),
    ("SP.URB.TOTL.IN.ZS", 2, "B ch1 urban population %"),
    ("SP.POP.65UP.TO.ZS", 2, "B ch1 population aged 65+ %"),
    ("NV.AGR.TOTL.ZS", 2, "B ch1 agriculture value added % of GDP"),
    ("NV.IND.MANF.ZS", 2, "B ch1 manufacturing value added % of GDP"),
    ("NV.SRV.TOTL.ZS", 2, "B ch1 services value added % of GDP"),
    ("SL.UEM.TOTL.ZS", 2, "A ch2 unemployment %"),
    ("FP.CPI.TOTL.ZG", 2, "A ch2 inflation, consumer prices %"),
    ("BN.CAB.XOKA.GD.ZS", 2, "A ch2 current account % of GDP"),
    ("NE.EXP.GNFS.ZS", 2, "B ch3 exports % of GDP"),
    ("NE.IMP.GNFS.ZS", 2, "B ch3 imports % of GDP"),
    ("TX.VAL.TECH.MF.ZS", 2, "B ch4 high-technology exports % of manufactured exports"),
    ("TX.VAL.TECH.CD", 2, "B ch4 high-technology exports US$"),
    ("BX.GSR.TRAN.ZS", 2, "B ch3 transport services % of service exports"),
    ("BX.GSR.INSF.ZS", 2, "B ch3 insurance and financial services % of service exports"),
    ("BX.GSR.CMCP.ZS", 2, "B ch3 ICT services % of service exports"),
    ("BX.GSR.TRVL.ZS", 2, "B ch3 travel services % of service exports"),
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
    ("BX.GSR.FCTY.CD", 2, "C ch6 primary income receipts (BoP) US$: earnings on investment abroad"),
    ("BM.GSR.FCTY.CD", 2, "C ch6 primary income payments (BoP) US$: earnings of foreign investors"),
    ("NY.GNP.MKTP.CD", 2, "C ch6 GNI current US$"),
    ("BX.GSR.TOTL.CD", 2, "B ch3 exports of goods, services and primary income"),
    ("BX.GSR.CCIS.CD", 2, "B ch4 ICT service exports US$"),
    # Ch. 7 - Member C: tariffs (applied and MFN, simple and trade-weighted mean, all products)
    ("TM.TAX.MRCH.SM.AR.ZS", 2, "C ch7 tariff rate, applied, simple mean %"),
    ("TM.TAX.MRCH.WM.AR.ZS", 2, "C ch7 tariff rate, applied, weighted mean %"),
    ("TM.TAX.MRCH.SM.FN.ZS", 2, "C ch7 tariff rate, MFN, simple mean %"),
    ("TM.TAX.MRCH.WM.FN.ZS", 2, "C ch7 tariff rate, MFN, weighted mean %"),
    # Tariff peaks: TM.TAX.MRCH.IP.ZS is not served by the API (Nov 2026); get peaks from WITS/TRAINS by hand.
]


def discover(prefix, source):
    """All indicator codes in a World Bank source that start with `prefix` (e.g. the B-READY family IC.BRE.*)."""
    found = [(i["id"], source, f"A ch2 {i['name']}")
             for i in fetch_paged(f"{API}/indicator", {"source": source}) if i["id"].startswith(prefix)]
    print(f"discovered {len(found)} indicators starting with {prefix}")
    return found


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
        w.writerow(["iso3", "name", "region_id", "region", "income", "is_aggregate", "capital", "lat", "lon"])
        for c in countries:
            w.writerow([c["id"], c["name"], c["region"]["id"], c["region"]["value"],
                        c["incomeLevel"]["value"], c["region"]["value"] == "Aggregates",
                        c.get("capitalCity", ""), c.get("latitude", ""), c.get("longitude", "")])
    print(f"countries.csv: {len(countries)} rows")

    # Optional: pass indicator codes to download only those (e.g. python scripts/fetch_worldbank.py SE.TER.ENRR)
    only = set(sys.argv[1:])
    indicators = [i for i in INDICATORS if i[0] in only] if only else INDICATORS + discover("IC.BRE.", 2)
    failed = []
    for code, source, note in indicators:
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
