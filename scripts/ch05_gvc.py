"""Ch. 5 Global value chains (OECD TiVA, 2025 edition; latest year 2022).

Backward participation = foreign value added in gross exports / gross exports (EXGR_FVA / EXGR).
Forward participation  = the economy's value added in other economies' gross exports / its gross exports
                         (sum over exporters j != i of EXGRVA[source i, exporter j] / EXGR_i).
GVC position (Koopman et al. 2010) = ln(1 + forward) - ln(1 + backward): above 0 = upstream, below 0 = downstream.
Outputs: figures/ch05_*.png, data/derived/ch05_participation_table.md, ch05_sector_table.md, ch05.json
Run: python scripts/ch05_gvc.py
"""
import numpy as np
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, NAMES, RAW, bar_rank, economies, line_chart, ordinal, rank_table,
                         retrieved, save_numbers, scatter)
from sectors import SECTORS

TIVA = RAW / "tiva"
econ, eas = economies()
econ = econ | {"TWN"}  # TiVA covers Taiwan; the World Bank lists it nowhere, so add it as an economy
eas = eas | {"TWN"}
N = {}
src = f"OECD Trade in Value Added (TiVA) database, 2025 edition, retrieved {retrieved(path=TIVA / 'tiva_total_all.csv')}"

tot = pd.read_csv(TIVA / "tiva_total_all.csv", usecols=["MEASURE", "REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
tot = tot[tot.REF_AREA.isin(econ)].pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="MEASURE",
                                               values="OBS_VALUE")
orig = pd.read_csv(TIVA / "tiva_origin_matrix.csv",
                   usecols=["VALUE_ADDED_SOURCE_AREA", "EXPORTING_AREA", "TIME_PERIOD", "OBS_VALUE"])
orig = orig[orig.EXPORTING_AREA.isin(econ)]
fwd_abs = (orig[(orig.VALUE_ADDED_SOURCE_AREA != orig.EXPORTING_AREA) & orig.VALUE_ADDED_SOURCE_AREA.isin(econ)]
           .groupby(["VALUE_ADDED_SOURCE_AREA", "TIME_PERIOD"]).OBS_VALUE.sum())
fwd_abs.index.names = ["REF_AREA", "TIME_PERIOD"]
tot["backward"] = tot.EXGR_FVA / tot.EXGR * 100
tot["forward"] = fwd_abs.reindex(tot.index) / tot.EXGR * 100
tot["participation"] = tot.backward + tot.forward
tot["position"] = np.log1p(tot.forward / 100) - np.log1p(tot.backward / 100)
tot["reii"] = tot.REII / tot.EXGR * 100
last = int(tot.index.get_level_values(1).max())
cur = tot.xs(last, level=1)
N["year"] = last
N["n_economies"] = int(len(cur))

# ---- 5.1 Backward participation over time
bw = tot.backward.unstack(0)[GROUP]
r_b = rank_table(cur.backward, eas).loc[FOCUS]
line_chart(
    bw,
    title=f"{bw.loc[last, FOCUS]:.0f}% of the value of Singapore's exports is foreign, "
          f"{ordinal(r_b['rank'])} highest of {int(r_b.n)} economies",
    subtitle=f"Backward GVC participation: foreign value added, % of gross exports, 2004 to {last}",
    ylabel="Foreign value added, % of gross exports",
    source=f"Source: {src}; EXGR_FVA / EXGR, total economy. Rank among the {int(r_b.n)} economies TiVA covers.",
    out="ch05_backward.png", fmt=lambda v: f"{v:.0f}%", ymin=0,
)

# ---- 5.2 Backward vs forward, all TiVA economies
sc = cur.reset_index()[["REF_AREA", "backward", "forward"]].dropna()
scatter(
    sc, x="backward", y="forward", label_col="REF_AREA",
    annotate=["SGP", "MYS", "HKG", "VNM", "CHN", "USA", "DEU", "JPN", "KOR", "TWN", "SAU", "RUS", "LUX", "IRL",
              "MEX", "NOR", "AUS", "IND"],
    highlight=("SGP",),
    title="Singapore buys far more foreign value added than it sells into others' exports",
    subtitle=f"Backward vs forward GVC participation, % of gross exports, {last}, {len(sc)} economies",
    xlabel="Backward: foreign value added in own exports, %",
    ylabel="Forward: own value added in other countries' exports, %",
    source=f"Source: {src}; backward = EXGR_FVA / EXGR; forward from the origin-of-value-added table (EXGRVA), "
           "team calculation.",
    out="ch05_backward_forward.png",
)

# ---- participation table with ranks
rows = []
for label, col, hib, fmt in [("Backward participation (FVA, % of exports)", "backward", True, "{:.1f}%"),
                             ("Forward participation (% of exports)", "forward", True, "{:.1f}%"),
                             ("Total GVC participation", "participation", True, "{:.1f}%"),
                             ("GVC position index (+ upstream, − downstream)", "position", True, "{:+.3f}"),
                             ("Re-exported intermediate imports, % of exports", "reii", True, "{:.1f}%")]:
    t = rank_table(cur[col].dropna(), eas, hib)
    r = t.loc[FOCUS]
    peers = " | ".join(fmt.format(cur.loc[k, col]) for k in ["MYS", "HKG", "VNM"])
    rows.append(f"| {label} | {fmt.format(r.value)} | {ordinal(r['rank'])} of {int(r.n)} | "
                f"{ordinal(r.region_rank)} of {int(r.region_n)} | {peers} |")
    N[col] = {"sgp": float(r.value), "rank": int(r["rank"]), "n": int(r.n), "region_rank": int(r.region_rank),
              "region_n": int(r.region_n), "peers": {k: float(cur.loc[k, col]) for k in GROUP},
              "sgp_2004": float(tot.loc[(FOCUS, 2004), col])}
table = (["| Indicator, " + str(last) + " | Singapore | Global rank | East Asia & Pacific rank | Malaysia | "
          "Hong Kong SAR | Vietnam |", "| --- | --- | --- | --- | --- | --- | --- |"] + rows +
         [f"\n*Ranks among the {len(cur)} economies in TiVA 2025 (1st = highest). Position index: Koopman et al. "
          "(2010), ln(1 + forward) − ln(1 + backward). Source: OECD TiVA 2025 edition; team calculation.*\n"])
(DERIVED / "ch05_participation_table.md").write_text("\n".join(table))
print("wrote data/derived/ch05_participation_table.md")

# ---- 5.3 Sector integration (shared sector table -> TiVA activities)
sec = pd.read_csv(TIVA / "tiva_sectors_peers.csv", usecols=["MEASURE", "REF_AREA", "ACTIVITY", "TIME_PERIOD",
                                                            "OBS_VALUE"])
sec = sec[(sec.TIME_PERIOD == last)].pivot_table(index=["REF_AREA", "ACTIVITY"], columns="MEASURE",
                                                 values="OBS_VALUE")
srows = []
for name, _, _, acts, _ in SECTORS:
    if not acts:
        continue
    for iso in GROUP:
        d = sec.loc[[(iso, a) for a in acts if (iso, a) in sec.index]]
        if len(d):
            srows.append({"sector": name, "iso": iso, "EXGR": d.EXGR.sum(), "FVA": d.EXGR_FVA.sum()})
sd = pd.DataFrame(srows)
sd["fva_share"] = sd.FVA / sd.EXGR * 100
sd["export_share"] = sd.EXGR / sd.iso.map(cur.EXGR) * 100
sg = sd[sd.iso == FOCUS].set_index("sector")
bar_rank(
    sg.fva_share,
    title=f"Refining ({sg.fva_share['Refined petroleum']:.0f}%) and transport ({sg.fva_share['Transport & logistics']:.0f}%) "
          "carry the most foreign content in Singapore's exports",
    subtitle=f"Foreign value added as % of each sector's gross exports, Singapore, {last}",
    xlabel="Foreign value added, % of sector's gross exports", fmt=lambda v: f"{v:.0f}%",
    highlight=(), ref=float(cur.loc[FOCUS, "backward"]), ref_label=f"all sectors {cur.loc[FOCUS, 'backward']:.0f}%",
    source=f"Source: {src}; EXGR_FVA / EXGR by industry (ISIC rev.4), mapped to the team's sector table "
           "(appendix).",
    out="ch05_sector_fva.png",
)
lines = ["| Sector | Share of Singapore's gross exports | Foreign value added, % | Malaysia FVA % | Hong Kong SAR FVA % | "
         "Vietnam FVA % |", "| --- | --- | --- | --- | --- | --- |"]
for s_, r in sg.sort_values("export_share", ascending=False).iterrows():
    pv = []
    for k in ["MYS", "HKG", "VNM"]:
        m = sd[(sd.iso == k) & (sd.sector == s_)]
        pv.append(f"{m.fva_share.iloc[0]:.0f}%" if len(m) else "n/a")
    lines.append(f"| {s_} | {r.export_share:.1f}% | {r.fva_share:.0f}% | " + " | ".join(pv) + " |")
lines.append(f"\n*Gross exports and foreign value added by industry, {last}. Source: OECD TiVA 2025 edition; "
             "industries mapped to the team's sector table.*\n")
(DERIVED / "ch05_sector_table.md").write_text("\n".join(lines))
print("wrote data/derived/ch05_sector_table.md")
N["sectors"] = sd.round(2).to_dict("records")

# ---- 5.4 Where Singapore's foreign value added comes from
o = pd.read_csv(TIVA / "tiva_origin_matrix.csv",
                usecols=["VALUE_ADDED_SOURCE_AREA", "EXPORTING_AREA", "TIME_PERIOD", "OBS_VALUE"])
o = o[(o.EXPORTING_AREA == FOCUS) & (o.TIME_PERIOD == last) & (o.VALUE_ADDED_SOURCE_AREA != FOCUS)]
o_e = o[o.VALUE_ADDED_SOURCE_AREA.isin(econ)].set_index("VALUE_ADDED_SOURCE_AREA").OBS_VALUE
fva_total = float(cur.loc[FOCUS, "EXGR_FVA"])
top = (o_e / fva_total * 100).sort_values(ascending=False).head(10)
labels = {"USA": "United States", "CHN": "China", "JPN": "Japan", "KOR": "Korea", "TWN": "Taiwan", "DEU": "Germany",
          "SAU": "Saudi Arabia", "ARE": "UAE", "GBR": "United Kingdom", "IND": "India", "AUS": "Australia",
          "IDN": "Indonesia", "FRA": "France", "IRL": "Ireland", "CHE": "Switzerland", "THA": "Thailand",
          "NLD": "Netherlands", "RUS": "Russia", "DNK": "Denmark", "QAT": "Qatar", "KWT": "Kuwait"}
bar_rank(
    top,
    title=f"The US and China each supply {top.iloc[0]:.0f}% of the foreign value in Singapore's exports",
    subtitle=f"Origin of the foreign value added in Singapore's gross exports, top 10 sources, % of total, {last}",
    xlabel="% of foreign value added in Singapore's exports", fmt=lambda v: f"{v:.1f}%", highlight=(),
    labels=labels,
    source=f"Source: {src}; origin of value added in gross exports (EXGRVA), team calculation. The rest of the world "
           "(W_O) is not shown.",
    out="ch05_fva_origin.png",
)
N["fva_origin_top10"] = top.round(1).to_dict()
save_numbers("ch05", N)
print("\n".join(table))
print("\n".join(lines))
print(top.round(1))
print(bw.round(1).loc[[2004, 2008, 2015, 2020, last]])
