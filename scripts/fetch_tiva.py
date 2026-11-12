"""Download OECD Trade in Value Added (TiVA), 2025 edition, from the OECD SDMX API (Ch. 5).

Three extracts (USD millions, years up to 2022, the edition's last year):
  data/raw/tiva/tiva_total_all.csv   all reporters, total economy, partner = World  -> participation + ranks
  data/raw/tiva/tiva_sectors_peers.csv   SGP + peers, every industry, partner = World -> most integrated sectors
  data/raw/tiva/tiva_origin_matrix.csv  origin of value added in gross exports: every source economy x every exporter,
                                       total economy (DF_EXGRVA) -> forward participation (a country's value added in
                                       other countries' exports) and where Singapore's foreign content comes from
Measures: EXGR gross exports; EXGR_DVA / EXGR_FVA domestic / foreign value added in gross exports (backward = FVA/EXGR);
FEXGR_DVA domestic value added in partners' exports (forward = FEXGR_DVA/EXGR); EXGR_INT intermediate exports;
REII re-exported intermediate imports.
Run: python scripts/fetch_tiva.py
"""
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "tiva"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://sdmx.oecd.org/sti-public/rest/data/OECD.STI.PIE,DSD_TIVA_MAINLV@DF_MAINLV,1.1"
MEASURES = "EXGR+EXGR_DVA+EXGR_FVA+FEXGR_DVA+EXGR_INT+REII"
PEERS = "SGP+MYS+HKG+VNM"

# key order: MEASURE.REF_AREA.ACTIVITY.COUNTERPART_AREA.UNIT_MEASURE.FREQ
QUERIES = {
    "tiva_total_all.csv": f"{MEASURES}.._T.W..A",
    "tiva_sectors_peers.csv": f"{MEASURES}.{PEERS}..W..A",
}
ORIGIN = ("https://sdmx.oecd.org/sti-public/rest/data/OECD.STI.PIE,DSD_TIVA_EXGRVA@DF_EXGRVA,1.1/"
          "EXGRVA.._T.._T.USD.A")  # MEASURE.VA_SOURCE_AREA.VA_SOURCE_ACTIVITY.EXPORTING_AREA.EXPORTING_ACTIVITY.UNIT.FREQ


def main():
    for name, key in QUERIES.items():
        r = requests.get(f"{BASE}/{key}", params={"format": "csvfilewithlabels", "startPeriod": 2004},
                         timeout=900)
        r.raise_for_status()
        (OUT / name).write_bytes(r.content)
        print(f"{name}: {r.content.count(b'\n') - 1} rows")
    r = requests.get(ORIGIN, params={"format": "csvfile", "startPeriod": 2004}, timeout=1800)
    r.raise_for_status()
    (OUT / "tiva_origin_matrix.csv").write_bytes(r.content)
    print(f"tiva_origin_matrix.csv: {r.content.count(b'\n') - 1} rows")


if __name__ == "__main__":
    main()
