"""Ch. 9 Case study: semiconductors and pharmaceuticals, the EDB's FDI-led strategy.

Data test of the course argument: did FDI-led industrial policy create a lasting comparative advantage?
- RCA of Singapore in integrated circuits (HS 8542), semiconductor devices (8541) and pharmaceuticals
  (finished 3004, biologics 3002, active ingredients 2933/2934/2937/2941), 1995-latest (CEPII BACI, goods-only RCA)
- Share of semiconductors and pharmaceuticals in manufacturing output and value added (EDB census via SingStat)
- FDI stock in semiconductor devices vs pharmaceutical products (SingStat M084831)
Run: python scripts/ch09_case.py
"""
import pandas as pd

from chart_style import DERIVED, FOCUS, GROUP, RAW, line_chart, retrieved, save_numbers

SS = RAW / "singstat"
N = {}
PRODUCTS = {"8542": "Integrated circuits", "8541": "Semiconductor devices", "3004": "Medicaments (finished)",
            "3002": "Biologics and vaccines", "2933": "APIs: heterocyclic (N)", "2934": "APIs: nucleic acids",
            "2937": "APIs: hormones", "2941": "APIs: antibiotics"}
GROUPS = {"Chips": ["8541", "8542"],
          "Finished pharma": ["3002", "3004"],
          "Pharma ingredients": ["2933", "2934", "2937", "2941"]}

# ---- product exports by exporter (BACI, aggregated by scripts/process_baci.py) and goods totals for RCA
ext = pd.read_csv(DERIVED / "baci_hs4_case.csv", dtype={"hs4": str}).rename(
    columns={"exp": "country_iso3_code", "hs4": "product_hs92_code", "v": "export_value"})
world = ext.groupby(["product_hs92_code", "year"]).export_value.sum().reset_index().assign(country_iso3_code="WLD")
ext = pd.concat([ext, world])
hs2 = pd.read_csv(DERIVED / "baci_hs2.csv", dtype={"hs2": str}).rename(columns={"exp": "country_iso3_code",
                                                                              "v": "export_value"})
tot = hs2.groupby(["country_iso3_code", "year"]).export_value.sum()
wtot = hs2.groupby("year").export_value.sum()
BACI_SRC = (f"team calculation from CEPII BACI (HS 1992, V202601), downloaded "
            f"{retrieved(path=DERIVED / 'baci_hs2.csv')}")


def group_rca(iso, codes):
    x = ext[(ext.country_iso3_code == iso) & ext.product_hs92_code.isin(codes)].groupby("year").export_value.sum()
    w = ext[(ext.country_iso3_code == "WLD") & ext.product_hs92_code.isin(codes)].groupby("year").export_value.sum()
    return (x / tot.loc[iso].reindex(x.index)) / (w / wtot.reindex(w.index))


rca = pd.DataFrame({g: group_rca(FOCUS, c) for g, c in GROUPS.items()}).loc[1995:]
line_chart(
    rca,
    title=f"Chips keep a strong advantage (RCA {rca.iloc[-1, 0]:.1f}) and finished pharma built one, "
          f"from {rca.loc[2004].iloc[1]:.1f} in 2004 to {rca.iloc[-1, 1]:.1f}",
    subtitle=f"Singapore's revealed comparative advantage by product group, 1995 to {rca.index.max()} (above 1 = advantage)",
    ylabel="Balassa RCA (goods only)", fmt=lambda v: f"{v:.1f}", ymin=0,
    labels={c: c for c in rca.columns},
    events=[(2000, "Biomedical initiative"), (2003, "Biopolis opens"), (2009, "GlobalFoundries buys Chartered"),
            (2021, "New fab wave")],
    source=f"Source: {BACI_SRC}. RCA = product share "
           "of Singapore's goods exports ÷ product share of world goods exports. Chips: HS 8541 and 8542; finished pharma: "
           "HS 3002, 3004; ingredients: HS 2933, 2934, 2937, 2941. The 2017 chip value is a one-year BACI outlier (see text).",
    out="ch09_rca.png", height=5.8,
)
peer = pd.DataFrame({k: group_rca(k, GROUPS["Chips"]) for k in GROUP}).loc[1995:]
LASTC = int(rca.index.max())
N["last_year"] = LASTC
N["rca_groups"] = rca.loc[[1995, 2000, 2004, 2010, 2014, 2020, LASTC]].round(2).to_dict()
N["rca_semis_peers"] = peer.loc[[2004, 2014, LASTC]].round(2).to_dict()
single = {}
for code, name in PRODUCTS.items():
    s = group_rca(FOCUS, [code])
    single[f"{code} {name}"] = {y: round(float(s.get(y, float("nan"))), 2) for y in (2004, 2014, LASTC)}
N["rca_products"] = single
sg_ic = ext[(ext.country_iso3_code == FOCUS) & (ext.product_hs92_code == "8542")].set_index("year").export_value
w_ic = ext[(ext.country_iso3_code == "WLD") & (ext.product_hs92_code == "8542")].set_index("year").export_value
N["ic_world_share"] = {y: float(sg_ic[y] / w_ic[y] * 100) for y in (2004, 2014, LASTC)}
N["ic_exports_bn"] = {y: float(sg_ic[y] / 1e9) for y in (2004, 2014, LASTC)}

# ---- manufacturing structure (EDB Census of Manufacturing Activities via SingStat)
def cluster(table):
    d = pd.read_csv(SS / f"{table}.csv", dtype={"series_no": str, "period": str})
    d["value"] = pd.to_numeric(d.value, errors="coerce")
    return d.pivot_table(index="period", columns="series", values="value")


va = cluster("M355181")
print(sorted(va.columns))
tot_col = [c for c in va.columns if c.strip().lower().startswith("total")][0]
semi_col = [c for c in va.columns if "semiconductor" in c.lower()][0]
pharma_col = [c for c in va.columns if c.strip().lower().startswith("pharmaceutical")][0]
bio_col = [c for c in va.columns if c.strip().lower().startswith("biomedical")][0]
share = pd.DataFrame({"Semiconductors": va[semi_col] / va[tot_col] * 100,
                      "Pharmaceuticals": va[pharma_col] / va[tot_col] * 100})
share.index = share.index.astype(int)
share = share.loc[2004:]
line_chart(
    share,
    title=f"Semiconductors now make {share.iloc[-1, 0]:.0f}% of Singapore's manufacturing value added, "
          f"pharma {share.iloc[-1, 1]:.0f}%",
    subtitle=f"Share of manufacturing value added, %, 2004 to {share.index.max()} ({share.index.max()} preliminary)",
    ylabel="% of manufacturing value added", fmt=lambda v: f"{v:.0f}%", ymin=0,
    labels={c: c for c in share.columns},
    source=f"Source: Economic Development Board, Census of Manufacturing Activities, via Singapore Department of "
           f"Statistics table M355181, downloaded {retrieved(path=SS / 'M355181.csv')}.",
    out="ch09_manufacturing.png",
)
N["va_share"] = share.round(1).loc[[2004, 2010, 2014, 2020, share.index.max()]].to_dict()
N["va_columns"] = {"total": tot_col, "semis": semi_col, "pharma": pharma_col, "biomedical": bio_col}
N["biomedical_va_share"] = {int(y): float(v) for y, v in (va[bio_col] / va[tot_col] * 100).items()
                            if int(y) in (2004, 2014, 2024)}

# ---- FDI stock: semiconductor devices vs pharmaceutical products
f = pd.read_csv(SS / "M084831.csv", dtype={"series_no": str, "period": str})
f["value"] = pd.to_numeric(f.value, errors="coerce")
fd = f[f.series_no.isin(["1.1.11.1", "1.1.5"])].pivot(index="period", columns="series_no", values="value") / 1e3
fd.index = fd.index.astype(int)
fd = fd.rename(columns={"1.1.11.1": "Semiconductors", "1.1.5": "Pharmaceuticals"})
fd = fd[["Semiconductors", "Pharmaceuticals"]].loc[2004:]
line_chart(
    fd,
    title=f"Foreign investment in chip plants grew to S${fd.iloc[-1, 0]:,.0f}bn while pharma's shrank to "
          f"S${fd.iloc[-1, 1]:,.0f}bn",
    subtitle=f"Inward FDI stock in Singapore by industry, S$ billions, {fd.dropna(how='all').index.min()} to 2024",
    ylabel="Inward FDI stock, S$ billions", fmt=lambda v: f"S${v:,.0f}bn", ymin=0,
    labels={c: c for c in fd.columns},
    source=f"Source: Singapore Department of Statistics, table M084831 (FDI in Singapore by detailed industry), "
           f"downloaded {retrieved(path=SS / 'M084831.csv')}. Stock by immediate investor; gaps are years not "
           "published.",
    out="ch09_fdi_stock.png",
)
N["fdi_stock_sgd_bn"] = {c: {int(y): round(float(v), 1) for y, v in fd[c].dropna().items()
                             if int(y) in (2004, 2010, 2014, 2020, 2024)} for c in fd.columns}
# ---- The test the case calls for: difference in differences on BACI (HS 2 digit chemicals, 1995 to latest)
# ln RCA_ckt = a_ck + b_kt + g_ct + beta (Singapore x Pharma x Post2000) + e_ckt, with Malaysia and Hong Kong SAR as
# comparison economies and the other chemical chapters (HS 28 to 38 except 30) as the comparison products.
import numpy as np  # noqa: E402

CHEM = [f"{k:02d}" for k in range(28, 39)]
DID_C = ["SGP", "MYS", "HKG"]
h = hs2.rename(columns={"export_value": "v"})
h = h[h.hs2.isin(CHEM)].copy()
wk = h.groupby(["hs2", "year"]).v.sum()
h = h[h.country_iso3_code.isin(DID_C)].copy()
cty_tot = h.apply(lambda r: tot.loc[(r.country_iso3_code, r.year)], axis=1)
h["rca"] = (h.v / cty_tot) / (h.apply(lambda r: wk.loc[(r.hs2, r.year)], axis=1) / h.year.map(wtot))
h = h[h.rca > 0].assign(y=lambda d: np.log(d.rca))
h["treat"] = (h.country_iso3_code == "SGP") & (h.hs2 == "30")


def ols_fe(df, regs):
    """OLS of y on regs plus country-product, product-year and country-year fixed effects; HC1 standard errors."""
    fe = pd.get_dummies(df.country_iso3_code + "_" + df.hs2, drop_first=True, dtype=float)
    fe2 = pd.get_dummies(df.hs2 + "_" + df.year.astype(str), drop_first=True, dtype=float)
    fe3 = pd.get_dummies(df.country_iso3_code + "_" + df.year.astype(str), drop_first=True, dtype=float)
    X = pd.concat([regs, fe, fe2, fe3], axis=1)
    X.insert(0, "const", 1.0)
    Xv, yv = X.values, df.y.values
    beta, *_ = np.linalg.lstsq(Xv, yv, rcond=None)
    e = yv - Xv @ beta
    n, k = Xv.shape[0], np.linalg.matrix_rank(Xv)
    XtXi = np.linalg.pinv(Xv.T @ Xv)
    V = XtXi @ (Xv.T * e ** 2) @ Xv @ XtXi * n / (n - k)
    se = np.sqrt(np.diag(V))
    return {c: (float(beta[i]), float(se[i])) for i, c in enumerate(X.columns) if c in regs.columns}, n


post = pd.DataFrame({"sgp_pharma_post": (h.treat & (h.year >= 2000)).astype(float)}, index=h.index)
did, n_did = ols_fe(h, post)
b, se = did["sgp_pharma_post"]
# event study: one coefficient per year, 1999 = 0 (the year before the Biomedical Sciences Initiative)
ev_years = [int(y) for y in sorted(h.year.unique()) if y != 1999]
ev = pd.DataFrame({f"y{y}": (h.treat & (h.year == y)).astype(float) for y in ev_years}, index=h.index)
es, _ = ols_fe(h, ev)
est = pd.DataFrame({"Estimate": {y: es[f"y{y}"][0] for y in ev_years}, "se": {y: es[f"y{y}"][1] for y in ev_years}})
est.loc[1999] = [0.0, 0.0]
est = est.sort_index()
# keys SGP / EAS / WLD only borrow the house colours: the estimate in Singapore red, the 95% band in neutral dashes
band = pd.DataFrame({"SGP": est.Estimate, "EAS": est.Estimate + 1.96 * est.se, "WLD": est.Estimate - 1.96 * est.se})
BAND_LABELS = {"SGP": "Estimate", "EAS": "Upper 95%", "WLD": "Lower 95%"}
pre = est.loc[:1998, "Estimate"]
N["did"] = {"beta": round(b, 3), "se": round(se, 3), "pct": round(float(np.exp(b) - 1) * 100, 0), "n": n_did,
            "pre_mean": round(float(pre.mean()), 2), "pre_max_abs": round(float(pre.abs().max()), 2),
            "last": int(h.year.max()), "est_last": round(float(est.Estimate.iloc[-1]), 2),
            "est_2010": round(float(est.loc[2010, "Estimate"]), 2), "est_2018": round(float(est.loc[2018, "Estimate"]), 2)}
line_chart(
    band,
    title=f"Against its other chemicals and its peers, Singapore's pharma RCA rose {np.exp(b):.1f} times after 2000",
    subtitle=f"Event study, ln RCA of pharma (HS 30) vs. other chemicals and vs. Malaysia and Hong Kong SAR, 1999 = 0, "
             f"1995 to {int(h.year.max())}",
    ylabel="Difference in ln RCA relative to 1999", fmt=lambda v: f"{v:.2f}", ymin=None, zero_line=True,
    labels=BAND_LABELS,
    events=((2000, "Biomedical Sciences Initiative"),),
    source=f"Source: {BACI_SRC}. OLS with country-product, product-year and country-year fixed effects; "
           f"bands are 95% intervals from heteroskedasticity robust (HC1) errors; {n_did} observations. With three "
           "economies and four pre-years the test is suggestive, not conclusive.",
    out="ch09_did.png",
)
print("DID", N["did"])
print(est.round(2).T.to_string())
save_numbers("ch09", N)
print(rca.round(2).loc[[1995, 2000, 2004, 2010, 2014, 2020, LASTC]])
print(peer.round(2).loc[[2004, 2014, LASTC]])
print(single)
print(N["ic_world_share"], N["ic_exports_bn"])
print(share.round(1))
print(fd.round(1))
