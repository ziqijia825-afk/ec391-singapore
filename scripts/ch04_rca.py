"""Ch. 4 Specialization and comparative advantage.

Balassa RCA_ik = (X_ik / X_i) / (X_wk / X_w), computed by the team from Atlas exports of goods (HS 1992) and services,
with the world = all economies in the Atlas. Sector RCA uses goods + services totals; HS-chapter RCA uses goods only.
Endowments: Penn World Table 11.0 (capital per worker, human capital), WDI (arable land, resource rents).
Outputs: figures/ch04_*.png, data/derived/ch04_rca_heat.md, ch04_hs_table.md, ch04_endowments.md, ch04.json
Run: python scripts/ch04_rca.py
"""
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, NAMES, RAW, bar_rank, economies, grouped_bars, load, ordinal,
                         rank_table, retrieved, save_numbers, wdi_rank)
from sectors import GOODS, SERVICES, hs_to_sector, services_to_sector

econ, eas = economies()
ATLAS = RAW / "atlas"
YEARS = [2004, 2014, 2024]
N = {}

hs = pd.read_csv(ATLAS / "hs92_country_product_year_2.csv", dtype={"product_hs92_code": str},
                 usecols=["country_iso3_code", "product_hs92_code", "year", "export_value"])
hs = hs[hs.product_hs92_code.str.isdigit() & hs.year.isin(YEARS)]
hs["chapter"] = hs.product_hs92_code.astype(int)
hs["sector"] = hs.chapter.map(hs_to_sector())
sv = pd.read_csv(ATLAS / "services_unilateral_country_product_year_2.csv",
                 usecols=["country_iso3_code", "product_services_unilateral_code", "year", "export_value"])
sv = sv[sv.year.isin(YEARS) & (sv.export_value > 0)]  # a zero services category means "not reported" (n/a)
sv["sector"] = sv.product_services_unilateral_code.map(services_to_sector()).fillna("Other services")

# ---- sector RCA (goods + services)
x = pd.concat([hs.groupby(["country_iso3_code", "year", "sector"]).export_value.sum(),
               sv.groupby(["country_iso3_code", "year", "sector"]).export_value.sum()])
x = x.groupby(level=[0, 1, 2]).sum()
xi = x.groupby(level=[0, 1]).transform("sum")              # country total
xwk = x.groupby(level=[1, 2]).transform("sum")             # world by sector
xw = x.groupby(level=[1]).transform("sum")                 # world total
rca = (x / xi) / (xwk / xw)
rca = rca.rename("rca").reset_index().rename(columns={"country_iso3_code": "iso3"})
SECTOR_ORDER = [s for s in GOODS if s != "Other goods"] + [s for s in SERVICES] + ["Other goods"]


def rca_table(year):
    t = rca[(rca.year == year) & rca.iso3.isin(GROUP)].pivot(index="sector", columns="iso3", values="rca")
    return t.reindex(index=[s for s in SECTOR_ORDER if s in t.index], columns=GROUP)


heat = rca_table(2024)


def shade(v):
    if pd.isna(v):
        return "", "n/a"
    if v >= 10:
        bg, fg = "#1f5fae", "#ffffff"
    elif v >= 2:
        bg, fg = "#2a78d6", "#ffffff"
    elif v >= 1:
        bg, fg = "#a9c8ee", "#1f1f1d"
    else:
        bg, fg = "#f1f0ec", "#5f5e5a"
    return f' style="background:{bg};color:{fg};text-align:center"', f"{v:.2f}"


html = ['<table class="rca">', "<thead><tr><th>Sector</th>" + "".join(f"<th>{NAMES[g]}</th>" for g in GROUP)
        + "</tr></thead>", "<tbody>"]
for sector, row in heat.iterrows():
    cells = "".join(f"<td{shade(v)[0]}>{shade(v)[1]}</td>" for v in row.values)
    html.append(f"<tr><td>{sector}</td>{cells}</tr>")
html += ["</tbody></table>", "",
         "*Balassa RCA = (country's exports of sector k / its total exports of goods and services) ÷ (world exports of "
         "k / world total), 2024. Shading: dark blue ≥ 10, blue 2 to 10, light blue 1 to 2, gray < 1 (no comparative "
         "advantage); n/a = the Atlas has no data for that services category (Vietnam reports only unspecified services, "
         "Hong Kong SAR no business services in 2024). Computed by the team from the Harvard Growth Lab Atlas of Economic Complexity (Dataverse v18), "
         f"downloaded {retrieved(path=ATLAS / 'hs92_country_product_year_2.csv')}; sector grouping in the appendix.*", ""]
(DERIVED / "ch04_rca_heat.md").write_text("\n".join(html))
print("wrote data/derived/ch04_rca_heat.md")

# ---- Singapore's RCA over time
sg = pd.DataFrame({str(y): rca_table(y)[FOCUS] for y in [2024, 2014, 2004]})
sg = sg.loc[[s for s in SECTOR_ORDER if s in sg.index and s != "Other goods"]]
sg_sorted = sg.sort_values("2024", ascending=False)
n_adv = int((sg["2024"] >= 1).sum())
grouped_bars(
    sg_sorted.rename(columns={"2024": "2024", "2014": "2014", "2004": "2004"}),
    title=f"Singapore's comparative advantage shifted from goods toward transport and financial services",
    subtitle="Balassa RCA by sector, Singapore, 2004, 2014 and 2024. Dashed line: RCA = 1",
    xlabel="RCA (above 1 = comparative advantage)", fmt=lambda v: f"{v:.1f}",
    source="Source: team calculation from the Harvard Growth Lab Atlas of Economic Complexity (goods HS 1992 and "
           f"services, Dataverse v18), downloaded {retrieved(path=ATLAS / 'hs92_country_product_year_2.csv')}. "
           "Sector grouping in the appendix.",
    out="ch04_rca_change.png", ref=1,
)
N["rca_sector"] = {y: rca_table(y).round(2).to_dict() for y in YEARS}
N["rca_sgp_n_above1_2024"] = n_adv

# ---- HS-chapter RCA (goods only) for Singapore: top chapters by export value
g = hs.groupby(["country_iso3_code", "year", "chapter"]).export_value.sum()
gi = g.groupby(level=[0, 1]).transform("sum")
gwk = g.groupby(level=[1, 2]).transform("sum")
gw = g.groupby(level=[1]).transform("sum")
grca = ((g / gi) / (gwk / gw)).rename("rca").reset_index()
names = pd.read_csv(ATLAS / "product_hs92.csv", dtype={"product_hs92_code": str})
names = names[names.product_level == 2].set_index("product_hs92_code").product_name_short
sgx = g.loc[FOCUS].unstack(0)
share24 = sgx[2024] / sgx[2024].sum() * 100
top = share24.sort_values(ascending=False).head(15).index
lines = ["| HS | Product | Share of Singapore's goods exports, 2024 | RCA 2004 | RCA 2014 | RCA 2024 |",
         "| --- | --- | --- | --- | --- | --- |"]
hs_out = []
for ch in top:
    r = {y: grca[(grca.country_iso3_code == FOCUS) & (grca.year == y) & (grca.chapter == ch)].rca for y in YEARS}
    vals = [float(r[y].iloc[0]) if len(r[y]) else float("nan") for y in YEARS]
    nm = names.get(f"{ch:02d}", str(ch))
    lines.append(f"| {ch:02d} | {nm} | {share24[ch]:.1f}% | " + " | ".join(f"{v:.2f}" for v in vals) + " |")
    hs_out.append([f"{ch:02d}", nm, round(float(share24[ch]), 1)] + [round(v, 2) for v in vals])
lines.append("\n*Goods-only Balassa RCA by HS 1992 chapter (world = all Atlas economies). Source: team calculation from "
             "the Harvard Growth Lab Atlas of Economic Complexity. HS 99 is unclassified trade.*\n")
(DERIVED / "ch04_hs_table.md").write_text("\n".join(lines))
print("wrote data/derived/ch04_hs_table.md")
N["rca_hs_top"] = hs_out
# number of HS chapters with RCA >= 1 (diversification), Singapore and peers
N["n_chapters_rca_ge1_2024"] = {k: int((grca[(grca.country_iso3_code == k) & (grca.year == 2024)].rca >= 1).sum())
                                for k in GROUP}

# ---- Endowments (Penn World Table 11.0)
PWT = RAW / "manual" / "pwt110.dta"
pwt = pd.read_stata(PWT, columns=["countrycode", "country", "year", "rnna", "emp", "hc", "pop"])
pyear = int(pwt[pwt.countrycode == FOCUS].dropna(subset=["rnna", "emp"]).year.max())
p = pwt[pwt.year == pyear].dropna(subset=["rnna", "emp"]).set_index("countrycode")
kl = p.rnna / p.emp  # rnna: million 2021 US$; emp: million workers -> 2021 US$ per worker
klr = rank_table(kl[kl.index.isin(econ)], eas).loc[FOCUS]
hcr = rank_table(p.hc.dropna()[p.hc.dropna().index.isin(econ)], eas).loc[FOCUS]
sel = ["SGP", "MYS", "HKG", "VNM", "USA", "JPN", "KOR", "CHN", "DEU", "IDN", "THA", "PHL", "IND", "AUS", "CHE"]
bar_rank(
    (kl.reindex(sel) / 1e3).dropna(),
    title=f"Singapore has the {ordinal(klr['rank'])} highest capital per worker of {int(klr.n)} economies",
    subtitle=f"Capital stock per worker, thousand 2021 US$ at constant national prices, {pyear}",
    xlabel="Capital per worker, thousand 2021 US$", fmt=lambda v: f"{v:,.0f}",
    highlight=(FOCUS,), labels={"USA": "United States", "JPN": "Japan", "KOR": "Korea", "CHN": "China",
                                 "DEU": "Germany", "IDN": "Indonesia", "THA": "Thailand", "PHL": "Philippines",
                                 "IND": "India", "AUS": "Australia", "CHE": "Switzerland"},
    source=f"Source: Penn World Table 11.0 (Feenstra, Inklaar and Timmer; Groningen Growth and Development Centre), "
           f"variables rnna / emp, downloaded {retrieved(path=PWT)}. Rank among {int(klr.n)} economies in PWT {pyear}.",
    out="ch04_capital_per_worker.png",
)
end_rows = [
    ("Capital per worker (PWT rnna/emp)", f"${kl[FOCUS] / 1e3:,.0f}k", pyear, klr),
    ("Human capital index (PWT hc)", f"{p.hc[FOCUS]:.2f}", pyear, hcr),
]
for label, code, hib, fmt in [("Arable land per person", "AG.LND.ARBL.HA.PC", True, lambda v: f"{v:.4f} ha"),
                              ("Natural resource rents, % of GDP", "NY.GDP.TOTL.RT.ZS", True, lambda v: f"{v:.2f}%")]:
    yr = int(load(code).query("iso3 == 'SGP'").year.max())
    r = wdi_rank(code, yr, hib)
    end_rows.append((label, fmt(r["value"]), yr, pd.Series({"rank": r["rank"], "n": r["n"],
                                                            "region_rank": r["region_rank"], "region_n": r["region_n"]})))
lines = ["| Endowment | Singapore | Year | Global rank | East Asia & Pacific rank | Malaysia | Hong Kong SAR | Vietnam |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
peer_vals = {
    "Capital per worker (PWT rnna/emp)": [f"${kl.get(k, float('nan')) / 1e3:,.0f}k" for k in ["MYS", "HKG", "VNM"]],
    "Human capital index (PWT hc)": [f"{p.hc.get(k, float('nan')):.2f}" for k in ["MYS", "HKG", "VNM"]],
}
for label, code in [("Arable land per person", "AG.LND.ARBL.HA.PC"), ("Natural resource rents, % of GDP", "NY.GDP.TOTL.RT.ZS")]:
    d = load(code)
    pv = []
    for k in ["MYS", "HKG", "VNM"]:
        dk = d[d.iso3 == k].sort_values("year")
        pv.append(f"{dk.value.iloc[-1]:.4f} ha" if "ha" in label or "Arable" in label else f"{dk.value.iloc[-1]:.2f}%")
    peer_vals[label] = pv
for label, val, yr, r in end_rows:
    lines.append(f"| {label} | {val} | {yr} | {ordinal(r['rank'])} of {int(r['n'])} | "
                 f"{ordinal(r['region_rank'])} of {int(r['region_n'])} | " + " | ".join(peer_vals[label]) + " |")
lines.append("\n*Rank 1st = most abundant. Sources: Penn World Table 11.0; World Bank WDI (AG.LND.ARBL.HA.PC, "
             f"NY.GDP.TOTL.RT.ZS), retrieved {retrieved('NY.GDP.TOTL.RT.ZS')}.*\n")
(DERIVED / "ch04_endowments.md").write_text("\n".join(lines))
print("wrote data/derived/ch04_endowments.md")
N["endowments"] = {"pwt_year": pyear, "kl_sgp": float(kl[FOCUS]), "kl_rank": int(klr["rank"]), "kl_n": int(klr.n),
                   "kl_peers": {k: float(kl.get(k, float("nan"))) for k in sel},
                   "hc_sgp": float(p.hc[FOCUS]), "hc_rank": int(hcr["rank"]), "hc_n": int(hcr.n),
                   "hc_peers": {k: float(p.hc.get(k, float("nan"))) for k in GROUP}}
save_numbers("ch04", N)
print(heat.round(2).to_string())
print(sg.round(2).to_string())
print("\n".join(lines))
for r in hs_out:
    print(r)
print(N["n_chapters_rca_ge1_2024"])
