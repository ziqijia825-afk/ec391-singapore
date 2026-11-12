"""Aggregate CEPII BACI (HS 1992, V202601) into the small tables the chapters need. BACI is on the course's list of
approved sources ("harmonized bilateral trade at HS6; high quality for RCA"): it reconciles exporter and importer
reports of UN Comtrade.

Input:  data/raw/baci/BACI_HS92_V202601.zip (2.4 GB, git-ignored; download from
        https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37)
Output (data/derived/, committed):
  baci_hs2.csv        exporter x HS 2-digit chapter x year, exports (US$)        -> RCA, export structure
  baci_sgp_imports.csv  Singapore's imports by HS 2-digit chapter x year (US$)    -> import structure
  baci_bilateral.csv  exports by exporter (SGP, MYS, HKG, VNM) x importer x year -> HHI, gravity robustness
  baci_hs4_case.csv   exporter x selected HS 4-digit products x year (US$)       -> Ch. 9 case study
Run: python scripts/process_baci.py
"""
import io
import re
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "data" / "raw" / "baci" / "BACI_HS92_V202601.zip"
OUT = ROOT / "data" / "derived"
GROUP = ["SGP", "MYS", "HKG", "VNM"]
CASE_HS4 = ["8541", "8542", "3002", "3004", "2933", "2934", "2937", "2941"]


def main():
    z = zipfile.ZipFile(ZIP)
    names = z.namelist()
    codes = pd.read_csv(io.BytesIO(z.read(next(n for n in names if n.startswith("country_codes")))))
    iso = dict(zip(codes.country_code, codes.country_iso3))
    years = sorted(int(m[1]) for n in names if (m := re.search(r"_Y(\d{4})_", n)))
    hs2, imp, bil, hs4 = [], [], [], []
    for y in years:
        member = next(n for n in names if f"_Y{y}_" in n)
        df = pd.read_csv(z.open(member), usecols=["i", "j", "k", "v"], dtype={"i": "int32", "j": "int32", "k": "string",
                                                                              "v": "float64"})
        df["k"] = df.k.str.zfill(6)
        df["v"] = df.v * 1000  # BACI values are in thousand US$
        df["exp"] = df.i.map(iso)
        df["imp"] = df.j.map(iso)
        df["hs2"] = df.k.str[:2]
        hs2.append(df.groupby(["exp", "hs2"]).v.sum().reset_index().assign(year=y))
        imp.append(df[df.imp == "SGP"].groupby("hs2").v.sum().reset_index().assign(year=y))
        bil.append(df[df.exp.isin(GROUP)].groupby(["exp", "imp"]).v.sum().reset_index().assign(year=y))
        df["hs4"] = df.k.str[:4]
        hs4.append(df[df.hs4.isin(CASE_HS4)].groupby(["exp", "hs4"]).v.sum().reset_index().assign(year=y))
        print(f"{y}: {len(df):,} flows, world exports ${df.v.sum() / 1e12:.2f}tn", flush=True)
    pd.concat(hs2).to_csv(OUT / "baci_hs2.csv", index=False)
    pd.concat(imp).to_csv(OUT / "baci_sgp_imports.csv", index=False)
    pd.concat(bil).to_csv(OUT / "baci_bilateral.csv", index=False)
    pd.concat(hs4).to_csv(OUT / "baci_hs4_case.csv", index=False)
    print("wrote data/derived/baci_*.csv")


if __name__ == "__main__":
    main()
