"""Ch. 7 Trade policy: tariffs (WDI/WITS-TRAINS) and the FTA network (hand-compiled list, see data/raw/manual).

Figures: MFN tariff vs peers; cumulative FTAs in force. Tables: FTA list and tariff ranks.
Run: python scripts/ch07_policy.py
"""
import re

import pandas as pd
from pypdf import PdfReader

from chart_style import (DERIVED, FOCUS, GROUP, NAMES, RAW, bar_rank, economies, grouped_bars, line_chart, load,
                         ordinal, rank_table, retrieved, save_numbers, wide)

econ, eas = economies()
N = {}

# ---- 7.1 MFN and applied tariffs
mfn = wide("TM.TAX.MRCH.SM.FN.ZS", GROUP, last=2022)
_all = load("TM.TAX.MRCH.SM.FN.ZS")
mfn["Median"] = _all[_all.iso3.isin(econ)].groupby("year").value.median().reindex(mfn.index)
last = {k: (int(mfn[k].dropna().index.max()), float(mfn[k].dropna().iloc[-1])) for k in mfn.columns}
line_chart(
    mfn.ffill(limit=1),
    title=f"Singapore's average MFN tariff is effectively zero ({last[FOCUS][1]:.2f}%), against Vietnam's "
          f"{last['VNM'][1]:.1f}%",
    subtitle="Tariff rate, most-favoured-nation, simple mean, all products, %, 2004 to 2022. Dashed: median economy",
    ylabel="MFN tariff, simple mean, %",
    source=f"Source: World Bank, World Development Indicators (TM.TAX.MRCH.SM.FN.ZS, from WITS/UNCTAD TRAINS), retrieved "
           f"{retrieved('TM.TAX.MRCH.SM.FN.ZS')}. Singapore's latest year {last[FOCUS][0]}; gaps of one year are "
           "carried forward.",
    out="ch07_tariffs.png", fmt=lambda v: f"{v:.1f}%", dashed=("Median",), labels={"Median": "Median economy"},
)
rows = []
for label, code in [("MFN tariff, simple mean", "TM.TAX.MRCH.SM.FN.ZS"), ("MFN tariff, trade-weighted mean", "TM.TAX.MRCH.WM.FN.ZS"),
                    ("Applied tariff, simple mean", "TM.TAX.MRCH.SM.AR.ZS"), ("Applied tariff, trade-weighted mean", "TM.TAX.MRCH.WM.AR.ZS")]:
    d = load(code)
    yr = int(d[d.iso3 == FOCUS].year.max())
    s = d[(d.year == yr) & d.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas, higher_is_better=False).loc[FOCUS]
    peers = []
    for k in ["MYS", "HKG", "VNM"]:
        dk = d[d.iso3 == k].sort_values("year")
        peers.append(f"{dk.value.iloc[-1]:.2f}% ({int(dk.year.iloc[-1])})" if len(dk) else "n/a")
    rows.append(f"| {label} | {t.value:.2f}% | {yr} | {ordinal(t['rank'])} of {int(t.n)} | "
                f"{ordinal(t.region_rank)} of {int(t.region_n)} | " + " | ".join(peers) + " |")
    N[code] = {"value": float(t.value), "year": yr, "rank": int(t["rank"]), "n": int(t.n),
               "region_rank": int(t.region_rank), "region_n": int(t.region_n)}
table = ["| Tariff measure | Singapore | Year | Global rank (1st = lowest) | East Asia & Pacific rank | Malaysia | "
         "Hong Kong SAR | Vietnam |", "| --- | --- | --- | --- | --- | --- | --- | --- |"] + rows + [
    "\n*Ties share the best rank, so many zero-tariff economies can be '1st'. Source: World Bank WDI (WITS/UNCTAD "
    f"TRAINS), retrieved {retrieved('TM.TAX.MRCH.SM.FN.ZS')}.*\n"]
(DERIVED / "ch07_tariff_table.md").write_text("\n".join(table))
print("wrote data/derived/ch07_tariff_table.md")
N["mfn_last"] = last

# ---- 7.2 FTA network
FTA = RAW / "manual" / "sg_fta_list.csv"
fta = pd.read_csv(FTA, parse_dates=["signed", "in_force_sg"]).sort_values("in_force_sg")
years = range(1993, 2027)
cum = pd.DataFrame({"FTAs in force": [int((fta.in_force_sg.dt.year <= y).sum()) for y in years]}, index=list(years))
line_chart(
    cum.loc[2000:],
    title=f"Singapore has signed its way to {len(fta)} free trade agreements in force",
    subtitle="Number of Singapore's FTAs in force at year-end, 2000 to 2026",
    ylabel="FTAs in force", fmt=lambda v: f"{v:.0f}", step=True, labels={"FTAs in force": "FTAs in force"},
    events=[(2004, "US FTA"), (2009, "China FTA"), (2018.99, "CPTPP"), (2019.9, "EU FTA"), (2022, "RCEP")],
    source=f"Source: team list compiled from Enterprise Singapore 'Find an FTA' pages and the WTO RTA database "
           f"(data/raw/manual/sg_fta_list.csv), Nov 2026. 2026 counts agreements in force by 1 Feb 2026.",
    out="ch07_fta_count.png",
)
lines = ["| Agreement | Partner(s) | Type | In force for Singapore | Scope |", "| --- | --- | --- | --- | --- |"]
for _, r in fta.iterrows():
    lines.append(f"| {r.agreement} | {r.partners} | {r.type} | {r.in_force_sg:%d %b %Y} | {r.scope} |")
lines.append("\n*Sources: Enterprise Singapore 'Find an FTA'; WTO Regional Trade Agreements database; Ministry of Energy, "
             "Trade and Industry. AFTA dated from the start of CEPT tariff cuts (1993). Where sources differ, see "
             "data/raw/manual/sg_fta_list.csv.*\n")
(DERIVED / "ch07_fta_table.md").write_text("\n".join(lines))
print("wrote data/derived/ch07_fta_table.md")
N["fta"] = {"n": len(fta), "by_type": fta.type.value_counts().to_dict(),
            "count_2004": int(cum.loc[2004].iloc[0]), "count_2014": int(cum.loc[2014].iloc[0])}
# ---- 7.3 WTO tariff profiles: averages, duty-free lines, peaks (lines above 15%) and maximum duties
WTO = RAW / "wto"


def profile(code):
    text = PdfReader(WTO / f"tariff_profile_{code}.pdf").pages[0].extract_text()
    nums = lambda line: [float(x) for x in re.findall(r"-?\d+\.?\d*", line.split("2025")[-1] if "2025" in line else line)]
    lines = text.splitlines()
    bound = re.search(r"Simple average final bound\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    applied = re.search(r"Simple average 20\d\d\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    weighted = re.search(r"Trade weighted average 20\d\d\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    dist = [nums(l)[-9:] for l in lines if l.strip().startswith("MFN applied 20")]
    a2 = text.split("Part A.2")[1].split("Part B")[0]
    maxima = []
    for l in a2.splitlines():
        toks = l.replace("> 1000", "1000").split()
        if len(toks) >= 7 and all(re.fullmatch(r"-|\d+\.?\d*", t) for t in toks[:7]):
            maxima.append(float(toks[6]) if toks[6] != "-" else 0.0)
    return {"bound_avg": float(bound[1]), "applied_avg": float(applied[1]), "applied_ag": float(applied[2]),
            "applied_nonag": float(applied[3]), "weighted_avg": float(weighted[1]),
            "dutyfree_ag": dist[0][0], "dutyfree_nonag": dist[1][0],
            "peak_ag": sum(dist[0][4:8]), "peak_nonag": sum(dist[1][4:8]), "max_applied": max(maxima)}


prof = {iso: profile(c) for iso, c in [("SGP", "SG"), ("MYS", "MY"), ("HKG", "HK"), ("VNM", "VN")]}
rows = [("MFN applied tariff, simple average (all products)", "applied_avg", "{:.1f}%"),
        ("of which agricultural products", "applied_ag", "{:.1f}%"),
        ("of which non-agricultural products", "applied_nonag", "{:.1f}%"),
        ("MFN applied tariff, trade-weighted average", "weighted_avg", "{:.1f}%"),
        ("Duty-free tariff lines, agriculture", "dutyfree_ag", "{:.1f}%"),
        ("Duty-free tariff lines, non-agriculture", "dutyfree_nonag", "{:.1f}%"),
        ("Tariff peaks: lines above 15%, agriculture", "peak_ag", "{:.1f}%"),
        ("Tariff peaks: lines above 15%, non-agriculture", "peak_nonag", "{:.1f}%"),
        ("Highest applied duty in any product group", "max_applied", "max"),
        ("Simple average final bound tariff", "bound_avg", "{:.1f}%")]
tl = ["| WTO tariff profile, 2025 | Singapore | Malaysia | Hong Kong SAR | Vietnam |", "| --- | --- | --- | --- | --- |"]
for label, key, fmt in rows:
    cell = lambda v: (">1,000%" if v >= 1000 else f"{v:.0f}%") if fmt == "max" else fmt.format(v)
    tl.append(f"| {label} | " + " | ".join(cell(prof[k][key]) for k in GROUP) + " |")
tl.append("\n*Source: WTO, Tariff Profiles (Part A.1 and A.2), downloaded "
          f"{retrieved(path=WTO / 'tariff_profile_SG.pdf')}. Tariff peaks follow the WTO convention of duties above 15%. "
          "Ad valorem equivalents of specific duties are included where the WTO reports them.*\n")
(DERIVED / "ch07_wto_profile_table.md").write_text("\n".join(tl))
print("wrote data/derived/ch07_wto_profile_table.md")
N["wto_profiles"] = prof

# ---- 7.4 Non-tariff measures (UNCTAD TRAINS via WITS)
NTM = RAW / "wits_ntm"
ms = pd.read_csv(NTM / "ntm_measures.csv")
sm = pd.read_csv(NTM / "ntm_summary.csv").set_index("iso3")
SHORT = {"Prohibitions/restrictions of imports for objectives set out in the TBT agreement, n.e.s.": "TBT import "
         "prohibitions or restrictions n.e.s.", "Requirement to pass through specified port of customs": "Entry only "
         "through specified customs ports"}
ms["measure"] = ms.measure.apply(lambda m: next((m.replace(k, v) for k, v in SHORT.items() if k in m), m))
sg_ms = ms[ms.iso3 == FOCUS].set_index("measure").coverage
bar_rank(
    sg_ms,
    title=f"Most of Singapore's non-tariff measures are technical (TBT) rules; they cover "
          f"{sm.loc[FOCUS, 'imports_coverage']:.0f}% of imports",
    subtitle="Ten most imposed non-tariff measures in Singapore, coverage ratio (% of import value affected)",
    xlabel="Coverage ratio, % of imports", fmt=lambda v: f"{v:.1f}%", highlight=(),
    source=f"Source: UNCTAD TRAINS via World Bank WITS, NTM summary for Singapore, downloaded "
           f"{retrieved(path=NTM / 'ntm_measures.csv')}. Codes follow the UNCTAD classification: B = technical barriers "
           "to trade (TBT), E = licensing and quotas, F = price control measures, C = pre-shipment inspection.",
    out="ch07_ntm_measures.png",
)
sec = pd.read_csv(NTM / "ntm_sectors.csv")
sec = sec[sec.sector != "All Import Products"].pivot(index="sector", columns="iso3", values="coverage")
sec = sec.reindex(columns=[c for c in GROUP if c in sec.columns])
sec = sec.loc[sec[FOCUS].sort_values(ascending=False).index[:8]]
grouped_bars(
    sec,
    title="Food, fuel and chemicals face the most non-tariff measures in Singapore and its neighbours",
    subtitle="NTM coverage ratio by sector, % of each sector's imports, top 8 sectors in Singapore",
    xlabel="Coverage ratio, %", fmt=lambda v: f"{v:.0f}",
    source=f"Source: UNCTAD TRAINS via World Bank WITS, downloaded {retrieved(path=NTM / 'ntm_sectors.csv')}. Hong Kong "
           "SAR has no TRAINS sector data.",
    out="ch07_ntm_sectors.png",
)
N["ntm"] = {"summary": sm.reset_index().to_dict("records"), "sg_measures": sg_ms.round(1).to_dict()}

# ---- 7.5 Bilateral investment treaties (METI list)
BIT = RAW / "manual" / "sg_bit_list.csv"
bit = pd.read_csv(BIT, parse_dates=["in_force"]).sort_values("in_force")
by = pd.DataFrame({"BITs in force": [int((bit.in_force.dt.year <= y).sum()) for y in range(1966, 2027)]},
                  index=list(range(1966, 2027)))
line_chart(
    by,
    title=f"Singapore has {len(bit)} bilateral investment treaties in force, the first with the US in 1966",
    subtitle="Number of Singapore's bilateral investment treaties and investment guarantee agreements in force, "
             "1966 to 2026",
    ylabel="BITs/IGAs in force", fmt=lambda v: f"{v:.0f}", step=True, labels={"BITs in force": "BITs in force"},
    source=f"Source: Ministry of Energy, Trade and Industry, list of BITs/IGAs in force (data/raw/manual/sg_bit_list.csv), "
           "transcribed Nov 2026. Investment chapters of 26 FTAs are not counted here.",
    out="ch07_bits.png",
)
bl = ["| Decade | Partners (year of entry into force) |", "| --- | --- |"]
for dec, g in bit.groupby((bit.in_force.dt.year // 10) * 10):
    bl.append(f"| {dec}s | " + ", ".join(f"{r.partner} ({r.in_force.year})" for r in g.itertuples()) + " |")
bl.append("\n*Source: Ministry of Energy, Trade and Industry (METI), BITs/IGAs in force. Ten treaties with EU members "
          "will lapse when the EU-Singapore Investment Protection Agreement enters into force.*\n")
(DERIVED / "ch07_bit_table.md").write_text("\n".join(bl))
print("wrote data/derived/ch07_bit_table.md")
N["bits"] = {"n": len(bit), "first": str(bit.in_force.min().date()), "latest": str(bit.in_force.max().date()),
             "by_decade": bit.groupby((bit.in_force.dt.year // 10) * 10).size().to_dict(),
             "eu_to_lapse": int(bit.note.fillna("").str.contains("EUSIPA").sum())}
save_numbers("ch07", N)
print("\n".join(tl))
print("\n".join(table))
print(last)
print(N["fta"])
