"""Download the remaining public datasets into data/raw/manual/ (small files, committed):

- Transparency International CPI scores 2012-2024, via Our World in Data's copy (TI's own file needs a browser).
- UNDP Human Development Report 2025, composite indices time series (HDI, schooling).
- Penn World Table 11.0 (Groningen Growth and Development Centre): capital stock and employment for K/L (Ch. 4).
- UNCTAD World Investment Report 2026 annex tables: FDI inflows, M&A and greenfield by host economy (Ch. 6).
- WTO tariff profiles for Singapore and peers (data/raw/wto/), Ch. 7.
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
    # UNCTAD World Investment Report 2026 annex tables (FDI inflows; inward and outward FDI stock; net cross-border M&A sales value and number;
    # announced greenfield projects value and number, by destination)
    **{f"unctad_wir26_tab{t}.xlsx": f"https://unctad.org/system/files/non-official-document/wir26_tab{t}.xlsx"
       for t in ("01", "03", "04", "05", "07", "14", "17")},
}
# WTO tariff profiles (MFN applied and bound tariffs, duty ranges, maximum duties by product group), Ch. 7
WTO = Path(__file__).resolve().parents[1] / "data" / "raw" / "wto"
WTO.mkdir(parents=True, exist_ok=True)
WTO_FILES = {f"tariff_profile_{c}.pdf": f"https://www.wto.org/english/res_e/statis_e/daily_update_e/tariff_profiles/{c}_e.pdf"
             for c in ("SG", "MY", "HK", "VN")}


def main():
    for name, url in FILES.items():
        r = requests.get(url, headers=HEADERS, timeout=300)
        r.raise_for_status()
        (OUT / name).write_bytes(r.content)
        print(f"{name}: {len(r.content) / 1e6:.1f} MB")
    for name, url in WTO_FILES.items():
        r = requests.get(url, headers=HEADERS, timeout=120)
        r.raise_for_status()
        (WTO / name).write_bytes(r.content)
        print(f"wto/{name}: {len(r.content) / 1e3:.0f} kB")


if __name__ == "__main__":
    main()
