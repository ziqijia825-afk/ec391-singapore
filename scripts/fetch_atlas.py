"""Download Harvard Growth Lab "Atlas of Economic Complexity" trade files (bulk data behind atlas.hks.harvard.edu).

Why: UN Comtrade-based, cleaned with mirror data so every economy has full goods + services exports, 1995-2024.
Used for Ch. 3 (export structure, partners, gravity), Ch. 4 (RCA) and Ch. 9 (case).
Large raw files go to data/raw/atlas/ (git-ignored); scripts write small derived tables to data/derived/.
Run: python scripts/fetch_atlas.py
"""
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw" / "atlas"
RAW.mkdir(parents=True, exist_ok=True)
API = "https://dataverse.harvard.edu/api"
HEADERS = {"User-Agent": "ec391-singapore/1.0 (university course project)"}  # Dataverse rejects the default UA

FILES = [  # (dataset DOI, file name)
    ("doi:10.7910/DVN/T4CHWJ", "hs92_country_product_year_2.csv"),   # goods exports by country x HS 2-digit x year
    ("doi:10.7910/DVN/T4CHWJ", "hs92_country_product_year_4.csv"),   # goods by HS 4-digit (case study products)
    ("doi:10.7910/DVN/T4CHWJ", "hs92_country_country_year.csv"),     # bilateral totals (partners, gravity)
    ("doi:10.7910/DVN/T4CHWJ", "hs92_data_dictionary.csv"),
    ("doi:10.7910/DVN/NDDMSN", "services_unilateral_country_product_year_2.csv"),  # services exports by category
    ("doi:10.7910/DVN/3BAL1O", "product_hs92.csv"),
    ("doi:10.7910/DVN/3BAL1O", "product_services_unilateral.csv"),
    ("doi:10.7910/DVN/3BAL1O", "location_country.csv"),
]


def file_ids(doi):
    r = requests.get(f"{API}/datasets/:persistentId/", params={"persistentId": doi}, headers=HEADERS, timeout=60)
    r.raise_for_status()
    v = r.json()["data"]["latestVersion"]
    return v["versionNumber"], {f["dataFile"]["filename"]: f["dataFile"]["id"] for f in v["files"]}


def main():
    cache = {}
    for doi, name in FILES:
        if doi not in cache:
            cache[doi] = file_ids(doi)
        version, ids = cache[doi]
        out = RAW / name
        if out.exists() and out.stat().st_size > 0:
            print(f"have {name}")
            continue
        with requests.get(f"{API}/access/datafile/{ids[name]}", headers=HEADERS, stream=True, timeout=600) as r:
            r.raise_for_status()
            tmp = out.with_suffix(".part")
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            tmp.rename(out)
        print(f"downloaded {name} ({out.stat().st_size / 1e6:.1f} MB, {doi} v{version})")


if __name__ == "__main__":
    main()
