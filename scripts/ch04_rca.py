"""Ch. 4 Specialization and comparative advantage.

Balassa RCA_ik = (X_ik / X_i) / (X_wk / X_w), computed by the team from approved sources only: CEPII BACI (goods,
HS 1992) and World Bank WDI balance-of-payments services exports (see trade_data.py). Sector RCA uses goods +
services; HS-chapter RCA in the table uses goods only.
Endowments: Penn World Table 11.0 (capital per worker, human capital), WDI (arable land, resource rents).
Outputs: figures/ch04_*.png, data/derived/ch04_rca_heat.md, ch04_hs_table.md, ch04_endowments.md, ch04.json,
         data/derived/rca_years.json (treemap and trend panel on the site)
Run: python scripts/ch04_rca.py
"""
import json

import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, NAMES, RAW, bar_rank, economies, grouped_bars, load, ordinal,
                         rank_table, retrieved, sanitize, save_numbers, wdi_rank)
from sectors import GOODS, SERVICES, hs_to_sector
from trade_data import SOURCE, exports_by_sector, goods_hs2, rca

econ, eas = economies()
N = {}
BACI_NOTE = DERIVED / "baci_hs2.csv"
x = exports_by_sector()
LAST = int(x.year.max())
YEARS = [2004, 2014, LAST]
r = rca(x)
SECTOR_ORDER = [s for s in GOODS if s != "Other goods"] + SERVICES + ["Other goods"]
src_line = f"Source: team calculation from {SOURCE}. BACI downloaded {retrieved(path=BACI_NOTE)}."


def rca_table(year):
    t = r[(r.year == year) & r.iso3.isin(GROUP)].pivot(index="sector", columns="iso3", values="rca")
    return t.reindex(index=[s for s in SECTOR_ORDER if s in t.index], columns=GROUP)


# ---- heat table, latest year
heat = rca_table(LAST)


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
    html.append(f"<tr><td>{sector}</td>" + "".join(f"<td{shade(v)[0]}>{shade(v)[1]}</td>" for v in row.values) + "</tr>")
html += ["</tbody></table>", "",
         f"*Balassa RCA = (country's exports of sector k / its total exports of goods and services) ÷ (world exports of k / "
         f"world total), {LAST}. Shading: dark blue ≥ 10, blue 2 to 10, light blue 1 to 2, gray < 1 (no comparative "
         f"advantage); n/a = no services breakdown reported. {src_line} Sector grouping in the appendix.*", ""]
(DERIVED / "ch04_rca_heat.md").write_text("\n".join(html))
print("wrote data/derived/ch04_rca_heat.md")

# ---- Singapore's RCA over time
sg = pd.DataFrame({str(y): rca_table(y)[FOCUS] for y in sorted(YEARS, reverse=True)})
sg = sg.loc[[s for s in SECTOR_ORDER if s in sg.index and s != "Other goods"]].sort_values(str(LAST), ascending=False)
grouped_bars(
    sg,
    title="How Singapore's revealed comparative advantage changed by sector",
    subtitle=f"Balassa RCA by sector, Singapore, 2004, 2014 and {LAST}. Dashed line: RCA = 1",
    xlabel="RCA (above 1 = comparative advantage)", fmt=lambda v: f"{v:.1f}",
    source=src_line + " Sector grouping in the appendix.", out="ch04_rca_change.png", ref=1,
)
N["last_year"] = LAST
N["rca_sector"] = {y: rca_table(y).round(2).to_dict() for y in YEARS}
N["rca_sgp_n_above1"] = int((sg[str(LAST)] >= 1).sum())

# ---- HS-chapter RCA (goods only) for Singapore
g = goods_hs2()
g = g[g.iso3.isin(econ | {"TWN"})]
gr = rca(g, by=("iso3", "chapter", "year"))
titles = pd.read_csv(RAW / "comtrade" / "hs_chapters.csv", dtype={"chapter": str}).set_index("chapter").title
sgx = g[g.iso3 == FOCUS].pivot(index="chapter", columns="year", values="value")
share = sgx[LAST] / sgx[LAST].sum() * 100
top = share.sort_values(ascending=False).head(15).index
lines = ["| HS | Product | Share of Singapore's goods exports, " + str(LAST) + " | RCA 2004 | RCA 2014 | RCA " + str(LAST) + " |",
         "| --- | --- | --- | --- | --- | --- |"]
hs_out = []
for ch in top:
    vals = []
    for y in YEARS:
        v = gr[(gr.iso3 == FOCUS) & (gr.year == y) & (gr.chapter == ch)].rca
        vals.append(float(v.iloc[0]) if len(v) else float("nan"))
    nm = titles.get(f"{ch:02d}", str(ch))
    nm = nm if len(nm) <= 70 else nm[:67].rsplit(" ", 1)[0] + "…"
    lines.append(f"| {ch:02d} | {nm} | {share[ch]:.1f}% | " + " | ".join(f"{v:.2f}" for v in vals) + " |")
    hs_out.append([f"{ch:02d}", nm, round(float(share[ch]), 1)] + [round(v, 2) for v in vals])
lines.append("\n*Goods-only Balassa RCA by HS 1992 chapter (world = all BACI exporters). Source: team calculation from "
             "CEPII BACI; chapter titles from UN Comtrade's HS reference.*\n")
(DERIVED / "ch04_hs_table.md").write_text("\n".join(lines))
print("wrote data/derived/ch04_hs_table.md")
N["rca_hs_top"] = hs_out
N["n_chapters_rca_ge1"] = {k: int((gr[(gr.iso3 == k) & (gr.year == LAST)].rca >= 1).sum()) for k in GROUP}

# ---- data for the interactive treemap: sectors (goods + services) with HS-chapter children, every year
items = pd.concat([g.assign(item=g.chapter.map(lambda c: f"HS {c:02d}"))[["iso3", "item", "year", "value"]],
                   x[x.sector.isin(SERVICES)].rename(columns={"sector": "item"})[["iso3", "item", "year", "value"]]])
ir = rca(items, by=("iso3", "item", "year")).set_index(["iso3", "item", "year"]).rca
sector_of = {f"HS {c:02d}": s for c, s in hs_to_sector().items()}
tm_years = {}
for y in sorted(set(x.year)):
    if y < 2004:
        continue
    xs = x[(x.iso3 == FOCUS) & (x.year == y)].groupby("sector").value.sum()
    rs = r[(r.iso3 == FOCUS) & (r.year == y)].set_index("sector").rca
    gy = g[(g.iso3 == FOCUS) & (g.year == y)].set_index("chapter").value
    sectors = []
    for sname in SECTOR_ORDER:
        if sname not in xs.index:
            continue
        node = {"name": sname, "value": float(xs[sname] / 1e9), "rca": float(rs.get(sname, float("nan")))}
        if sname in GOODS:
            kids = [{"name": f"HS {c:02d} {titles.get(f'{c:02d}', '')[:38]}", "value": float(v / 1e9),
                     "rca": float(ir.get((FOCUS, f"HS {c:02d}", y), float("nan")))}
                    for c, v in gy.items() if sector_of.get(f"HS {c:02d}") == sname and v > 5e7]
            node["children"] = sorted(kids, key=lambda k: -k["value"])
        sectors.append(node)
    tm_years[int(y)] = sectors
trend = {}
for sname in SECTOR_ORDER:
    t = r[(r.sector == sname) & r.iso3.isin(GROUP) & (r.year >= 2004)].pivot(index="year", columns="iso3", values="rca")
    if len(t):
        trend[sname] = {"years": [int(v) for v in t.index],
                        "values": {k: [None if pd.isna(v) else float(v) for v in t[k]] if k in t.columns else []
                                   for k in GROUP}}
(DERIVED / "rca_years.json").write_text(json.dumps(sanitize({"years": tm_years, "trend": trend,
                                                             "source": src_line.replace("Source: ", "")}),
                                                   separators=(",", ":"), allow_nan=False))
print("wrote data/derived/rca_years.json")

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
end_rows = [("Capital per worker (PWT rnna/emp)", f"${kl[FOCUS] / 1e3:,.0f}k", pyear, klr),
            ("Human capital index (PWT hc)", f"{p.hc[FOCUS]:.2f}", pyear, hcr)]
for label, code, fmt in [("Arable land per person", "AG.LND.ARBL.HA.PC", lambda v: f"{v:.4f} ha"),
                         ("Natural resource rents, % of GDP", "NY.GDP.TOTL.RT.ZS", lambda v: f"{v:.2f}%")]:
    yr = int(load(code).query("iso3 == 'SGP'").year.max())
    rr = wdi_rank(code, yr, True)
    end_rows.append((label, fmt(rr["value"]), yr, pd.Series({"rank": rr["rank"], "n": rr["n"],
                                                             "region_rank": rr["region_rank"], "region_n": rr["region_n"]})))
peer_vals = {"Capital per worker (PWT rnna/emp)": [f"${kl.get(k, float('nan')) / 1e3:,.0f}k" for k in ["MYS", "HKG", "VNM"]],
             "Human capital index (PWT hc)": [f"{p.hc.get(k, float('nan')):.2f}" for k in ["MYS", "HKG", "VNM"]]}
for label, code in [("Arable land per person", "AG.LND.ARBL.HA.PC"), ("Natural resource rents, % of GDP", "NY.GDP.TOTL.RT.ZS")]:
    d = load(code)
    peer_vals[label] = [(f"{d[d.iso3 == k].sort_values('year').value.iloc[-1]:.4f} ha" if "Arable" in label
                         else f"{d[d.iso3 == k].sort_values('year').value.iloc[-1]:.2f}%") for k in ["MYS", "HKG", "VNM"]]
lines = ["| Endowment | Singapore | Year | Global rank | East Asia & Pacific rank | Malaysia | Hong Kong SAR | Vietnam |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
for label, val, yr, rr in end_rows:
    lines.append(f"| {label} | {val} | {yr} | {ordinal(rr['rank'])} of {int(rr['n'])} | "
                 f"{ordinal(rr['region_rank'])} of {int(rr['region_n'])} | " + " | ".join(peer_vals[label]) + " |")
lines.append("\n*Rank 1st = most abundant. Sources: Penn World Table 11.0; World Bank WDI (AG.LND.ARBL.HA.PC, "
             f"NY.GDP.TOTL.RT.ZS), retrieved {retrieved('NY.GDP.TOTL.RT.ZS')}.*\n")
(DERIVED / "ch04_endowments.md").write_text("\n".join(lines))
print("wrote data/derived/ch04_endowments.md")
N["endowments"] = {"pwt_year": pyear, "kl_sgp": float(kl[FOCUS]), "kl_rank": int(klr["rank"]), "kl_n": int(klr.n),
                   "kl_peers": {k: float(kl.get(k, float("nan"))) for k in sel},
                   "hc_sgp": float(p.hc[FOCUS]), "hc_rank": int(hcr["rank"]), "hc_n": int(hcr.n)}
save_numbers("ch04", N)
print(heat.round(2).to_string())
print(sg.round(2).to_string())
for row in hs_out:
    print(row)
print(N["n_chapters_rca_ge1"])
