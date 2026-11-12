"""Exports of goods and services by sector for every economy, from approved sources only:

- goods: CEPII BACI (HS 1992), aggregated by scripts/process_baci.py into data/derived/baci_hs2.csv
- services: World Bank WDI balance of payments, commercial services exports (BX.GSR.NFSV.CD) split with the
  category shares transport (BX.GSR.TRAN.ZS), travel (BX.GSR.TRVL.ZS), insurance and financial (BX.GSR.INSF.ZS)
  and computer, communications and other services (BX.GSR.CMCP.ZS)

Balassa RCA_ik = (X_ik / X_i) / (X_wk / X_w), world = all economies in the data for that year.
"""
import pandas as pd

from chart_style import DERIVED, economies, load
from sectors import hs_to_sector

SERVICE_SHARES = {"Transport & logistics": "BX.GSR.TRAN.ZS", "Travel & tourism": "BX.GSR.TRVL.ZS",
                  "Finance & insurance": "BX.GSR.INSF.ZS", "ICT & business services": "BX.GSR.CMCP.ZS"}


def goods_hs2():
    """exporter (iso3) x HS chapter (int) x year -> US$ (BACI)."""
    g = pd.read_csv(DERIVED / "baci_hs2.csv", dtype={"hs2": str})
    g = g[g.hs2.str.isdigit()]
    g["chapter"] = g.hs2.astype(int)
    return g.rename(columns={"exp": "iso3", "v": "value"})[["iso3", "chapter", "year", "value"]]


def services_by_sector():
    """iso3 x sector x year -> US$ (WDI), economies only."""
    econ, _ = economies()
    total = load("BX.GSR.NFSV.CD")
    total = total[total.iso3.isin(econ)].set_index(["iso3", "year"]).value
    parts = []
    for sector, code in SERVICE_SHARES.items():
        sh = load(code)
        sh = sh[sh.iso3.isin(econ)].set_index(["iso3", "year"]).value
        v = (sh / 100 * total).dropna()
        parts.append(v.rename("value").reset_index().assign(sector=sector))
    return pd.concat(parts)


def exports_by_sector(years=None):
    """iso3 x sector x year -> US$, goods (BACI, by the team's sector table) + services (WDI)."""
    econ, _ = economies()
    g = goods_hs2()
    g = g[g.iso3.isin(econ | {"TWN"})]
    g["sector"] = g.chapter.map(hs_to_sector())
    g = g.groupby(["iso3", "sector", "year"]).value.sum().reset_index()
    s = services_by_sector()
    x = pd.concat([g, s])
    x = x[x.year.isin(set(g.year))]  # keep years covered by BACI
    if years is not None:
        x = x[x.year.isin(years)]
    return x


def rca(x, by=("iso3", "sector", "year")):
    """Balassa RCA from a long table with columns iso3, <item>, year, value."""
    iso, item, year = by
    t = x.groupby([iso, item, year]).value.sum()
    xi = t.groupby(level=[0, 2]).transform("sum")
    xwk = t.groupby(level=[1, 2]).transform("sum")
    xw = t.groupby(level=[2]).transform("sum")
    return ((t / xi) / (xwk / xw)).rename("rca").reset_index()


SOURCE = ("CEPII BACI (HS 1992, V202601) for goods and World Bank WDI balance-of-payments services exports "
          "(BX.GSR.NFSV.CD with category shares BX.GSR.TRAN/TRVL/INSF/CMCP.ZS) for services; RCA computed by the team")
