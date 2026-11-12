"""Ch. 7 Trade policy: tariffs (WDI/WITS-TRAINS) and the FTA network (hand-compiled list, see data/raw/manual).

Figures: MFN tariff vs peers; cumulative FTAs in force. Tables: FTA list and tariff ranks.
Run: python scripts/ch07_policy.py
"""
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, RAW, economies, line_chart, load, ordinal, rank_table, retrieved,
                         save_numbers, wide)

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
save_numbers("ch07", N)
print("\n".join(table))
print(last)
print(N["fta"])
