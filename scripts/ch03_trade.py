"""Ch. 3 Openness and trade patterns.

Figures: openness vs peers; goods and services balances; domestic exports vs re-exports (SingStat); export and import
structure by sector 2004/2014/2024 (Atlas); top partners (Comtrade, as reported); partner concentration (HHI);
gravity scatter. Tables: gravity regressions -> data/derived/ch03_gravity_table.md.
Run: python scripts/ch03_trade.py
"""
import numpy as np
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, RAW, bar_rank, economies, line_chart, load, ordinal, retrieved,
                         save_numbers, scatter, stacked_shares, wdi_rank, wide)
from sectors import hs_to_sector, services_to_sector

econ, eas = economies()
N = {}
ATLAS = RAW / "atlas"
atlas_note = "Harvard Growth Lab, Atlas of Economic Complexity (HS 1992, 2-digit; services), Dataverse v18"

# ---- 3.1 Openness
op = wide("NE.TRD.GNFS.ZS", GROUP + ["EAS", "WLD"])
r_op = wdi_rank("NE.TRD.GNFS.ZS", 2024)
line_chart(
    op,
    title=f"Singapore trades {op.loc[2024, FOCUS]:.0f}% of its GDP, the {ordinal(r_op['rank'])} most open economy",
    subtitle="Trade openness: exports plus imports of goods and services, % of GDP, 2004 to 2024",
    ylabel="(Exports + imports) / GDP, %",
    source=f"Source: World Bank, World Development Indicators (NE.TRD.GNFS.ZS), retrieved {retrieved('NE.TRD.GNFS.ZS')}. "
           f"Rank among {r_op['n']} economies with 2024 data. Ratios above 100% are possible because trade is "
           "measured gross while GDP is value added.",
    out="ch03_openness.png", fmt=lambda v: f"{v:.0f}%", dashed=("EAS", "WLD"),
    labels={"EAS": "East Asia & Pacific", "WLD": "World"},
)
N["openness"] = {"2024": op.loc[2024].round(1).to_dict(), "2004": op.loc[2004].round(1).to_dict(), "rank": r_op,
                 "peak": (int(op[FOCUS].idxmax()), float(op[FOCUS].max()))}

# ---- 3.2 Goods and services balances (BoP), Singapore
bal = pd.DataFrame({
    "Goods balance": wide("BX.GSR.MRCH.CD", [FOCUS])[FOCUS] - wide("BM.GSR.MRCH.CD", [FOCUS])[FOCUS],
    "Services balance": wide("BX.GSR.NFSV.CD", [FOCUS])[FOCUS] - wide("BM.GSR.NFSV.CD", [FOCUS])[FOCUS],
}).dropna()
line_chart(
    bal,
    title=f"Singapore earns a goods surplus of ${bal['Goods balance'].iloc[-1] / 1e9:,.0f}bn and a services "
          f"surplus of ${bal['Services balance'].iloc[-1] / 1e9:,.0f}bn",
    subtitle=f"Trade balances from the balance of payments, current US$ billions, 2004 to {bal.index.max()}",
    ylabel="Balance, US$ billions",
    source="Source: World Bank, World Development Indicators (BX.GSR.MRCH.CD, BM.GSR.MRCH.CD, BX.GSR.NFSV.CD, "
           f"BM.GSR.NFSV.CD), retrieved {retrieved('BX.GSR.MRCH.CD')}. Balance = exports minus imports.",
    out="ch03_balances.png", fmt=lambda v: f"${v:,.0f}bn", scale=1e9, ymin=None, zero_line=True,
    labels={c: c for c in bal.columns},
)
svc_x = wide("BX.GSR.NFSV.CD", [FOCUS])[FOCUS]
gds_x = wide("BX.GSR.MRCH.CD", [FOCUS])[FOCUS]
N["balances"] = {"goods_bn": (bal["Goods balance"] / 1e9).round(1).to_dict(),
                 "services_bn": (bal["Services balance"] / 1e9).round(1).to_dict(),
                 "services_share_of_exports": float(svc_x.loc[2024] / (svc_x.loc[2024] + gds_x.loc[2024]) * 100),
                 "services_share_2004": float(svc_x.loc[2004] / (svc_x.loc[2004] + gds_x.loc[2004]) * 100),
                 "services_exports_rank": wdi_rank("BX.GSR.NFSV.CD", 2024),
                 "goods_exports_rank": wdi_rank("BX.GSR.MRCH.CD", 2024)}

# ---- 3.3 Domestic exports vs re-exports (SingStat, S$; annual sums of monthly data)
ss = pd.read_csv(RAW / "singstat" / "M451001.csv")
ss["year"] = ss.period.str[:4].astype(int)
ss["value"] = pd.to_numeric(ss.value, errors="coerce")
ann = ss[ss.series_no.isin(["3", "4.1", "4.2", "5"])].groupby(["year", "series_no"]).value.sum().unstack()
ann = ann.loc[2004:2024]
ann.columns = [{"3": "total", "4.1": "oil_dx", "4.2": "nonoil_dx", "5": "rx"}[c] for c in ann.columns]
shares = pd.DataFrame({
    "Re-exports": ann.rx / ann.total * 100,
    "Non-oil domestic exports": ann.nonoil_dx / ann.total * 100,
    "Oil domestic exports": ann.oil_dx / ann.total * 100,
})
stacked_shares(
    shares.loc[[2004, 2014, 2024]],
    title=f"Re-exports grew from {shares.loc[2004, 'Re-exports']:.1f}% to {shares.loc[2024, 'Re-exports']:.1f}% "
          "of Singapore's merchandise exports",
    subtitle="Composition of total merchandise exports, % (Singapore dollars, annual sums of monthly data)",
    source="Source: Singapore Department of Statistics / Enterprise Singapore, table M451001 (Merchandise Trade by "
           f"Commodity Section), downloaded {retrieved(path=RAW / 'singstat' / 'M451001.csv')}. Re-exports are goods "
           "imported and exported again without substantial transformation; domestic exports are made in Singapore.",
    out="ch03_reexports.png", colors=["#b3b2ab", "#2a78d6", "#6aa3e5"],
)
N["reexports"] = {"share": shares.round(1).to_dict(), "total_sgd_bn_2024": float(ann.loc[2024, "total"] / 1e6)}

# ---- Partners data (Singapore's own reports, incl. re-exports)
CT = RAW / "comtrade"
cx = pd.read_csv(CT / "sgp_X_partners_2024.csv")
cm = pd.read_csv(CT / "sgp_M_partners_2024.csv")
names = {"China, Hong Kong SAR": "Hong Kong SAR", "Other Asia, nes": "Taiwan (Other Asia, nes)",
         "Rep. of Korea": "Korea, Rep.", "USA": "United States", "China": "China (mainland)"}


# ---- 3.4 Export and import structure by sector (Atlas: goods by HS chapter + services)
hs = pd.read_csv(ATLAS / "hs92_country_product_year_2.csv", dtype={"product_hs92_code": str})
hs = hs[hs.product_hs92_code.str.isdigit()]
hs["chapter"] = hs.product_hs92_code.astype(int)
hs["sector"] = hs.chapter.map(hs_to_sector())
sv = pd.read_csv(ATLAS / "services_unilateral_country_product_year_2.csv")
sv["sector"] = sv.product_services_unilateral_code.map(services_to_sector()).fillna("Other services")
GROUPS = {  # combine sectors into chart groups (kept to 9 so the stacked bars stay readable)
    "Electronics & instruments": "Electronics & instruments", "Machinery incl. computers": "Machinery & computers",
    "Refined petroleum": "Refined petroleum", "Chemicals & plastics": "Chemicals & pharma",
    "Pharmaceuticals": "Chemicals & pharma", "Gold & metals": "Gold & metals", "Food & agriculture": "Other goods",
    "Transport equipment": "Other goods", "Other goods": "Other goods",
    "Transport & logistics": "Transport services", "Finance & insurance": "Financial services",
    "ICT & business services": "Business & ICT services", "Travel & tourism": "Other services",
    "Other services": "Other services"}
ORDER = ["Electronics & instruments", "Machinery & computers", "Refined petroleum", "Chemicals & pharma",
         "Gold & metals", "Other goods", "Transport services", "Business & ICT services", "Financial services",
         "Other services"]


def structure(iso, flow, years=(2004, 2014, 2024), with_services=True):
    g = hs[(hs.country_iso3_code == iso) & hs.year.isin(years)].groupby(["year", "sector"])[flow].sum()
    parts = [g]
    if with_services:
        parts.append(sv[(sv.country_iso3_code == iso) & sv.year.isin(years)].groupby(["year", "sector"])[flow].sum())
    t = pd.concat(parts).groupby(level=[0, 1]).sum().unstack().fillna(0)
    t = t.T.groupby(t.columns.map(GROUPS)).sum().T
    t = t.reindex(columns=[c for c in ORDER if c in t.columns])
    return t.div(t.sum(axis=1), axis=0) * 100, t.sum(axis=1)


exp_sh, exp_tot = structure(FOCUS, "export_value")
SVC = ["Transport services", "Business & ICT services", "Financial services", "Other services"]
palette = ["#2a78d6", "#4f8fdd", "#7aaae6", "#a9c8ee", "#d2e2f6", "#e9e8e3", "#5f5e5a", "#8a8a85", "#b3b2ab",
           "#d9d8d2"]
stacked_shares(
    exp_sh,
    title=f"Services rose from {exp_sh.loc[2004, SVC].sum():.0f}% to {exp_sh.loc[2024, SVC].sum():.0f}% of "
          "Singapore's exports as every goods sector lost share",
    subtitle="Singapore's exports of goods and services by sector, % of total, 2004, 2014 and 2024",
    source=f"Source: {atlas_note}, downloaded {retrieved(path=ATLAS / 'hs92_country_product_year_2.csv')}; team "
           "grouping of HS chapters (see appendix). Atlas goods figures are reconciled from exporter and importer reports and "
           f"are below Singapore's own (2024: ${exp_tot.loc[2024] / 1e9 * (1 - exp_sh.loc[2024, SVC].sum() / 100):,.0f}bn "
           f"vs ${cx.loc[cx.partner_code == 0, 'value_usd'].iloc[0] / 1e9:,.0f}bn reported to UN Comtrade).",
    out="ch03_export_structure.png", colors=palette, min_label=3.5,
)
imp_sh, _ = structure(FOCUS, "import_value", with_services=False)
stacked_shares(
    imp_sh,
    title=f"Electronics are also Singapore's largest import: {imp_sh.loc[2024, 'Electronics & instruments']:.0f}% "
          "of goods imports in 2024",
    subtitle="Singapore's goods imports by sector, % of total, 2004, 2014 and 2024",
    source=f"Source: {atlas_note}, downloaded {retrieved(path=ATLAS / 'hs92_country_product_year_2.csv')}; team "
           "grouping of HS chapters. Large two-way trade in the same sectors reflects processing and re-export.",
    out="ch03_import_structure.png", colors=palette, min_label=3.5,
)
N["structure"] = {"services_share": exp_sh[SVC].sum(axis=1).round(1).to_dict(), "exports": exp_sh.round(1).to_dict(), "imports": imp_sh.round(1).to_dict(),
                  "atlas_total_exports_bn": (exp_tot / 1e9).round(1).to_dict()}

# ---- 3.5 Partners
def partner_shares(df):
    world = df.loc[df.partner_code == 0, "value_usd"].iloc[0]
    p = df[df.partner_code != 0].copy()
    p["share"] = p.value_usd / world * 100
    p["name"] = p.partner.replace(names)
    return p.sort_values("share", ascending=False), world


xs, xworld = partner_shares(cx)
ms, mworld = partner_shares(cm)
top = xs.head(10).set_index("name").share
bar_rank(
    top,
    title=f"Asia takes most of Singapore's exports: China, Hong Kong and Malaysia lead",
    subtitle=f"Top 10 destinations of Singapore's merchandise exports (incl. re-exports), % of total, 2024",
    xlabel="% of Singapore's exports", fmt=lambda v: f"{v:.1f}%", highlight=(), labels={},
    source=f"Source: UN Comtrade, Singapore's reported exports by partner, 2024 (total ${xworld / 1e9:,.0f}bn), "
           f"downloaded {retrieved(path=CT / 'sgp_X_partners_2024.csv')}. \"Other Asia, nes\" is Comtrade's code for "
           "Taiwan.",
    out="ch03_partners.png",
)
hhi_x = float(((xs.share / 100) ** 2).sum())
hhi_m = float(((ms.share / 100) ** 2).sum())
N["partners"] = {"exports_top10": xs.head(10)[["name", "share"]].round(1).values.tolist(),
                 "imports_top10": ms.head(10)[["name", "share"]].round(1).values.tolist(),
                 "hhi_exports": hhi_x, "hhi_imports": hhi_m, "exports_bn": xworld / 1e9, "imports_bn": mworld / 1e9}

# partner concentration over time (Atlas bilateral, all four economies)
bil = pd.read_csv(ATLAS / "hs92_country_country_year.csv",
                  usecols=["country_iso3_code", "partner_iso3_code", "year", "export_value"])
bil = bil[bil.country_iso3_code.isin(GROUP) & bil.year.between(2004, 2024)]
sh = bil.groupby(["country_iso3_code", "year"]).export_value.transform(lambda v: v / v.sum())
bil["sq"] = sh ** 2
hhi = bil.groupby(["year", "country_iso3_code"]).sq.sum().unstack()[GROUP]
line_chart(
    hhi,
    title=f"Singapore's export markets are diversified: partner HHI {hhi.loc[2024, FOCUS]:.2f}",
    subtitle="Herfindahl-Hirschman index of export destinations (0 = spread out, 1 = one partner), 2004 to 2024",
    ylabel="HHI of export partners",
    source=f"Source: {atlas_note}, bilateral goods exports, downloaded "
           f"{retrieved(path=ATLAS / 'hs92_country_country_year.csv')}; HHI computed by the team as the sum of squared "
           "partner shares.",
    out="ch03_partner_hhi.png", fmt=lambda v: f"{v:.2f}", ymin=0,
)
N["hhi_atlas"] = hhi.round(3).to_dict()

# ---- 3.6 Gravity: ln(exports) = a + b1 ln(partner GDP) + b2 ln(distance)
c = pd.read_csv(RAW / "wdi" / "countries.csv", keep_default_na=False)
c = c[(~(c.is_aggregate.astype(str) == "True")) & (c.lat != "")]
coords = c.set_index("iso3")[["lat", "lon"]].astype(float)
lat0, lon0 = coords.loc[FOCUS]
la, lo = np.radians(coords.lat), np.radians(coords.lon)
dist = 6371 * 2 * np.arcsin(np.sqrt(np.sin((la - np.radians(lat0)) / 2) ** 2 + np.cos(np.radians(lat0)) * np.cos(la)
                                    * np.sin((lo - np.radians(lon0)) / 2) ** 2))
gdp24 = load("NY.GDP.MKTP.CD").query("year == 2024").set_index("iso3").value


def ols(y, X):
    X = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ beta
    n, k = X.shape
    xtx_inv = np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(xtx_inv) * (e @ e) / (n - k))
    meat = X.T @ (X * (e ** 2)[:, None])
    se_r = np.sqrt(np.diag(xtx_inv @ meat @ xtx_inv) * n / (n - k))  # HC1 robust
    r2 = 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))
    return beta, se, se_r, r2, n


def gravity(values):
    d = pd.DataFrame({"x": values}).join(gdp24.rename("gdp")).join(dist.rename("dist")).dropna()
    d = d[(d.x > 0) & (d.index != FOCUS)]
    beta, se, se_r, r2, n = ols(np.log(d.x.values), np.column_stack([np.log(d.gdp), np.log(d.dist)]))
    return d, beta, se, se_r, r2, n


reported = cx[cx.partner_code != 0].set_index("partner_iso3").value_usd
atlas_x = bil[(bil.country_iso3_code == FOCUS) & (bil.year == 2024)].set_index("partner_iso3_code").export_value
res = {"Reported exports (incl. re-exports), Comtrade": gravity(reported),
       "Atlas reconciled exports": gravity(atlas_x)}
lines = ["| Sample, 2024 | ln partner GDP | ln distance | R² | Partners (N) |", "| --- | --- | --- | --- | --- |"]
for label, (d, b, se, se_r, r2, n) in res.items():
    lines.append(f"| {label} | {b[1]:.2f} (s.e. {se_r[1]:.2f}) | {b[2]:.2f} (s.e. {se_r[2]:.2f}) | {r2:.2f} | {n} |")
note = ("\n*OLS of ln(Singapore's exports to partner j) on ln(GDP of j, current US$, 2024) and ln(great-circle distance "
        "between capitals, km). Robust (HC1) standard errors in parentheses. Sources: UN Comtrade; Harvard Atlas; World "
        "Bank WDI (GDP, capital coordinates). Taiwan is excluded (no World Bank GDP).*\n")
(DERIVED / "ch03_gravity_table.md").write_text("\n".join(lines) + "\n" + note)
d, b, se, se_r, r2, n = res["Reported exports (incl. re-exports), Comtrade"]
d = d.assign(adj=np.log(d.x) - b[1] * np.log(d.gdp), iso=d.index)
scatter(
    d, x="dist", y="adj", logx=True, fit=(b[0], b[2]), label_col="iso",
    annotate=["MYS", "IDN", "CHN", "HKG", "USA", "JPN", "IND", "AUS", "DEU", "VNM", "THA", "BRA", "GBR", "KOR"],
    highlight=(),
    title=f"Trade falls with distance: 10% farther means about {abs(b[2]) * 10:.0f}% less exported",
    subtitle="Singapore's exports to each partner, adjusted for partner size, against distance, 2024 (N = "
             f"{n})",
    xlabel="Distance between capitals, km (log scale)",
    ylabel=f"ln(exports) − {b[1]:.2f} × ln(partner GDP)",
    source="Source: UN Comtrade (Singapore's reported exports by partner, 2024); World Bank WDI (GDP, capital "
           f"coordinates), retrieved {retrieved('NY.GDP.MKTP.CD')}. Dashed line: OLS fit, distance elasticity "
           f"{b[2]:.2f} (robust s.e. {se_r[2]:.2f}), R² {r2:.2f}.",
    out="ch03_gravity.png",
)
N["gravity"] = {k: {"b_gdp": float(v[1][1]), "b_dist": float(v[1][2]), "se_gdp": float(v[3][1]),
                    "se_dist": float(v[3][2]), "r2": float(v[4]), "n": int(v[5])} for k, v in res.items()}
resid = d.adj - (b[0] + b[2] * np.log(d.dist))
N["gravity_residuals_top"] = resid.sort_values(ascending=False).head(8).round(2).to_dict()
N["gravity_residuals_bottom"] = resid.sort_values().head(5).round(2).to_dict()
save_numbers("ch03", N)
print("\n".join(lines))
print(exp_sh.round(1).to_string())
print(imp_sh.round(1).to_string())
print(shares.loc[[2004, 2014, 2024]].round(1))
print(N["partners"]["exports_top10"], N["partners"]["imports_top10"][:5], hhi_x)
print(hhi.loc[[2004, 2024]].round(3))
print(N["gravity_residuals_top"], N["gravity_residuals_bottom"])
