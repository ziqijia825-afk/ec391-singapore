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
        bg, fg = "#104281", "#ffffff"
    elif v >= 2:
        bg, fg = "#256abf", "#ffffff"
    elif v >= 1:
        bg, fg = "#86b6ef", "#1f1f1d"
    elif v >= 0.5:
        bg, fg = "#fbd2b8", "#1f1f1d"
    else:
        bg, fg = "#fde9dc", "#5f5e5a"
    return f' style="background:{bg};color:{fg};text-align:center"', f"{v:.2f}"


html = ['<table class="rca">', "<thead><tr><th>Sector</th>" + "".join(f"<th>{NAMES[g]}</th>" for g in GROUP)
        + "</tr></thead>", "<tbody>"]
for sector, row in heat.iterrows():
    html.append(f"<tr><td>{sector}</td>" + "".join(f"<td{shade(v)[0]}>{shade(v)[1]}</td>" for v in row.values) + "</tr>")
html += ["</tbody></table>", "",
         f"*Balassa RCA = (country's exports of sector k / its total exports of goods and services) ÷ (world exports of k / "
         f"world total), {LAST}. Shading: dark blue ≥ 10, blue 2 to 10, light blue 1 to 2 (advantage); light orange 0.5 to 1 and pale orange "
         f"below 0.5 (no comparative advantage); n/a = no services breakdown reported. {src_line} Sector grouping in the appendix.*", ""]
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
# ---- A cross-country test of Heckscher Ohlin: do capital rich economies specialise in capital intensive goods?
# y = ln(RCA in capital and skill intensive chapters / RCA in labour intensive chapters), x = ln capital per worker.
# The grouping of HS chapters by factor intensity is the team's, following the textbook examples.
import numpy as np  # noqa: E402
from chart_style import scatter  # noqa: E402

K_CH = ["28", "29", "30", "84", "85", "87", "88", "90"]  # chemicals, pharma, machinery, electronics, vehicles, aircraft, instruments
L_CH = ["42", "61", "62", "64", "94", "95"]              # leather goods, apparel, footwear, furniture, toys
hb = pd.read_csv(DERIVED / "baci_hs2.csv", dtype={"hs2": str})
hb = hb[hb.year == pyear]
tot_c = hb.groupby("exp").v.sum()
tot_w = hb.v.sum()
grp = lambda ch: hb[hb.hs2.isin(ch)].groupby("exp").v.sum()
rca_k = (grp(K_CH) / tot_c) / (grp(K_CH).sum() / tot_w)
rca_l = (grp(L_CH) / tot_c) / (grp(L_CH).sum() / tot_w)
econ_set, _ = economies()
ho = pd.DataFrame({"y": np.log(rca_k / rca_l), "kl": kl / 1e3, "exports": tot_c}).dropna()
ho = ho[ho.index.isin(econ_set) & np.isfinite(ho.y) & (ho.exports > 1e9)]
ho["x"] = np.log(ho.kl)
Xm = np.column_stack([np.ones(len(ho)), ho.x.values])
bh, *_ = np.linalg.lstsq(Xm, ho.y.values, rcond=None)
eh = ho.y.values - Xm @ bh
XtXi = np.linalg.inv(Xm.T @ Xm)
Vh = XtXi @ (Xm.T * eh ** 2) @ Xm @ XtXi * len(ho) / (len(ho) - 2)
r2 = 1 - (eh ** 2).sum() / ((ho.y - ho.y.mean()) ** 2).sum()
pred_sg = bh[0] + bh[1] * ho.loc[FOCUS, "x"]
ho = ho.reset_index(names="iso3")
scatter(
    ho, x="x", y="y", label_col="iso3", highlight=[FOCUS], annotate=[FOCUS, "MYS", "HKG", "VNM", "CHN", "USA", "JPN"],
    fit=(bh[0], bh[1]),
    title=f"Capital rich economies export capital intensive goods, and Singapore sits {'above' if ho.loc[ho.iso3 == FOCUS, 'y'].iloc[0] > pred_sg else 'below'} the line",
    subtitle=f"ln(RCA in capital and skill intensive goods / RCA in labour intensive goods) against ln capital per worker, "
             f"{len(ho)} economies, {pyear}",
    xlabel="ln capital per worker (thousand 2021 US$)", ylabel="ln(RCA capital intensive / RCA labour intensive)",
    source=f"Source: team calculation from CEPII BACI (HS 1992, V202601) and Penn World Table 11.0 (rnna / emp), "
           f"downloaded {retrieved(path=PWT)}. Capital and skill intensive: HS {', '.join(K_CH)}; labour intensive: "
           f"HS {', '.join(L_CH)}. Economies exporting over $1bn. OLS slope {bh[1]:.2f} (robust s.e. "
           f"{np.sqrt(Vh[1, 1]):.2f}), R² {r2:.2f}.",
    out="ch04_ho_test.png",
)
N["ho_test"] = {"slope": round(float(bh[1]), 2), "se": round(float(np.sqrt(Vh[1, 1])), 2), "r2": round(float(r2), 2),
                "n": int(len(ho)), "year": pyear, "y_sgp": round(float(ho.loc[ho.iso3 == FOCUS, "y"].iloc[0]), 2),
                "pred_sgp": round(float(pred_sg), 2),
                "ratio_sgp": round(float(np.exp(ho.loc[ho.iso3 == FOCUS, "y"].iloc[0])), 1),
                "pct_above": round(float((ho.y < ho.loc[ho.iso3 == FOCUS, "y"].iloc[0]).mean() * 100), 0)}
print("HO", N["ho_test"])
save_numbers("ch04", N)
print(heat.round(2).to_string())
print(sg.round(2).to_string())
for row in hs_out:
    print(row)
print(N["n_chapters_rca_ge1"])
