"""Ch. 9 Case study: semiconductors and pharmaceuticals, the EDB's FDI-led strategy.

Data test of the course argument: did FDI-led industrial policy create a lasting comparative advantage?
- RCA of Singapore in integrated circuits (HS 8542), semiconductor devices (8541) and pharmaceuticals
  (finished 3004, biologics 3002, active ingredients 2933/2934/2937/2941), 1995-2024 (Atlas HS 1992, goods-only RCA)
- Share of semiconductors and pharmaceuticals in manufacturing output and value added (EDB census via SingStat)
- FDI stock in semiconductor devices vs pharmaceutical products (SingStat M084831)
Run: python scripts/ch09_case.py
"""
import pandas as pd

from chart_style import DERIVED, FOCUS, GROUP, RAW, line_chart, retrieved, save_numbers

ATLAS = RAW / "atlas"
SS = RAW / "singstat"
N = {}
PRODUCTS = {"8542": "Integrated circuits", "8541": "Semiconductor devices", "3004": "Medicaments (finished)",
            "3002": "Biologics and vaccines", "2933": "APIs: heterocyclic (N)", "2934": "APIs: nucleic acids",
            "2937": "APIs: hormones", "2941": "APIs: antibiotics"}
GROUPS = {"Chips": ["8541", "8542"],
          "Finished pharma": ["3002", "3004"],
          "Pharma ingredients": ["2933", "2934", "2937", "2941"]}

# ---- product exports: Singapore, peers and world totals, from the 4-digit Atlas file (read in chunks)
cache = DERIVED / "ch09_hs4_extract.csv"
if not cache.exists():
    parts = []
    for chunk in pd.read_csv(ATLAS / "hs92_country_product_year_4.csv", chunksize=2_000_000,
                             usecols=["country_iso3_code", "product_hs92_code", "year", "export_value"],
                             dtype={"product_hs92_code": str}):
        c = chunk[chunk.product_hs92_code.isin(PRODUCTS)]
        world = c.groupby(["product_hs92_code", "year"]).export_value.sum().reset_index().assign(country_iso3_code="WLD")
        parts += [c[c.country_iso3_code.isin(GROUP)], world]
    ext = pd.concat(parts).groupby(["country_iso3_code", "product_hs92_code", "year"]).export_value.sum().reset_index()
    ext.to_csv(cache, index=False)
ext = pd.read_csv(cache, dtype={"product_hs92_code": str})

# goods totals for RCA denominators
hs2 = pd.read_csv(ATLAS / "hs92_country_product_year_2.csv", usecols=["country_iso3_code", "year", "export_value"])
tot = hs2.groupby(["country_iso3_code", "year"]).export_value.sum()
wtot = hs2.groupby("year").export_value.sum()


def group_rca(iso, codes):
    x = ext[(ext.country_iso3_code == iso) & ext.product_hs92_code.isin(codes)].groupby("year").export_value.sum()
    w = ext[(ext.country_iso3_code == "WLD") & ext.product_hs92_code.isin(codes)].groupby("year").export_value.sum()
    return (x / tot.loc[iso].reindex(x.index)) / (w / wtot.reindex(w.index))


rca = pd.DataFrame({g: group_rca(FOCUS, c) for g, c in GROUPS.items()}).loc[1995:2024]
line_chart(
    rca,
    title=f"Chips keep a strong advantage (RCA {rca.iloc[-1, 0]:.1f}) while finished pharma never got one "
          f"({rca.iloc[-1, 1]:.1f})",
    subtitle="Singapore's revealed comparative advantage by product group, 1995 to 2024 (above 1 = advantage)",
    ylabel="Balassa RCA (goods only)", fmt=lambda v: f"{v:.1f}", ymin=0,
    labels={c: c for c in rca.columns},
    events=[(2000, "Biomedical initiative"), (2003, "Biopolis opens"), (2009, "GlobalFoundries buys Chartered"),
            (2021, "New fab wave")],
    source="Source: team calculation from the Harvard Growth Lab Atlas of Economic Complexity (HS 1992, 4-digit; "
           f"Dataverse v18), downloaded {retrieved(path=ATLAS / 'hs92_country_product_year_2.csv')}. RCA = product share "
           "of Singapore's goods exports ÷ product share of world goods exports. Chips: HS 8541 and 8542; finished pharma: "
           "HS 3002, 3004; ingredients: HS 2933, 2934, 2937, 2941.",
    out="ch09_rca.png", height=5.8,
)
peer = pd.DataFrame({k: group_rca(k, GROUPS["Chips"]) for k in GROUP}).loc[1995:2024]
N["rca_groups"] = rca.loc[[1995, 2000, 2004, 2010, 2014, 2020, 2024]].round(2).to_dict()
N["rca_semis_peers"] = peer.loc[[2004, 2014, 2024]].round(2).to_dict()
single = {}
for code, name in PRODUCTS.items():
    s = group_rca(FOCUS, [code])
    single[f"{code} {name}"] = {y: round(float(s.get(y, float("nan"))), 2) for y in (2004, 2014, 2024)}
N["rca_products"] = single
sg_ic = ext[(ext.country_iso3_code == FOCUS) & (ext.product_hs92_code == "8542")].set_index("year").export_value
w_ic = ext[(ext.country_iso3_code == "WLD") & (ext.product_hs92_code == "8542")].set_index("year").export_value
N["ic_world_share"] = {y: float(sg_ic[y] / w_ic[y] * 100) for y in (2004, 2014, 2024)}
N["ic_exports_bn"] = {y: float(sg_ic[y] / 1e9) for y in (2004, 2014, 2024)}

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
save_numbers("ch09", N)
print(rca.round(2).loc[[1995, 2000, 2004, 2010, 2014, 2020, 2024]])
print(peer.round(2).loc[[2004, 2014, 2024]])
print(single)
print(N["ic_world_share"], N["ic_exports_bn"])
print(share.round(1))
print(fd.round(1))
