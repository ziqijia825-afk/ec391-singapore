"""Download the remaining public datasets into data/raw/manual/ (small files, committed):

- Transparency International CPI scores 2012-2024, via Our World in Data's copy (TI's own file needs a browser).
- UNDP Human Development Report 2025, composite indices time series (HDI, schooling).
- Penn World Table 11.0 (Groningen Growth and Development Centre): capital stock and employment for K/L (Ch. 4).
- UNCTAD World Investment Report 2026 annex tables: FDI inflows, M&A and greenfield by host economy (Ch. 6).
Run: python scripts/fetch_other.py
"""
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "manual"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "ec391-singapore/1.0 (university course project)"}

FILES = {
    "ti_cpi_2012_2024_owid.csv":
        "https://ourworldindata.org/grapher/ti-corruption-perception-index.csv?v=1&csvType=full&useColumnShortNames=true",
    "undp_hdr25_composite_time_series.csv":
        "https://hdr.undp.org/sites/default/files/2025_HDR/HDR25_Composite_indices_complete_time_series.csv",
    "pwt110.dta": "https://dataverse.nl/api/access/datafile/554030",  # doi:10.34894/FABVLR
    # UNCTAD World Investment Report 2026 annex tables (FDI inflows; net cross-border M&A sales value and number;
    # announced greenfield projects value and number, by destination)
    **{f"unctad_wir26_tab{t}.xlsx": f"https://unctad.org/system/files/non-official-document/wir26_tab{t}.xlsx"
       for t in ("01", "05", "07", "14", "17")},
}


def main():
    for name, url in FILES.items():
        r = requests.get(url, headers=HEADERS, timeout=300)
        r.raise_for_status()
        (OUT / name).write_bytes(r.content)
        print(f"{name}: {len(r.content) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
