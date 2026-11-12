"""Concentration of export destinations (Herfindahl Hirschman index) for every exporter in BACI's latest year.

Reads the latest yearly file from the BACI zip (data/raw/baci) and writes data/derived/baci_hhi_latest.csv
(exporter, year, hhi), so Chapter 3 can rank Singapore's HHI among all economies.
"""
import io
import re
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "raw" / "baci" / "BACI_HS92_V202601.zip"
OUT = ROOT / "data" / "derived" / "baci_hhi_latest.csv"


def main():
    z = zipfile.ZipFile(ZIP)
    names = z.namelist()
    codes = pd.read_csv(io.BytesIO(z.read(next(n for n in names if n.startswith("country_codes")))))
    iso = dict(zip(codes.country_code, codes.country_iso3))
    year = max(int(m[1]) for n in names if (m := re.search(r"_Y(\d{4})_", n)))
    df = pd.read_csv(z.open(next(n for n in names if f"_Y{year}_" in n)), usecols=["i", "j", "v"])
    bil = df.groupby(["i", "j"]).v.sum().reset_index()
    bil["share"] = bil.v / bil.groupby("i").v.transform("sum")
    hhi = (bil.share ** 2).groupby(bil.i).sum().rename("hhi").reset_index()
    hhi["exporter"] = hhi.i.map(iso)
    hhi["year"] = year
    hhi[["exporter", "year", "hhi"]].dropna().to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(hhi)} exporters, {year}")


if __name__ == "__main__":
    main()
