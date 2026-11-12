"""Ch. 1 Country profile: human development, economic structure, basic facts with global and regional ranks.

Writes figures/ch01_hdi.png, figures/ch01_structure.png, data/derived/ch01_profile_table.md, data/derived/ch01.json.
Run: python scripts/ch01_profile.py
"""
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, NAMES, RAW, economies, grouped_bars, line_chart, load, ordinal,
                         rank_table, retrieved, save_numbers)

HDR = RAW / "manual" / "undp_hdr25_composite_time_series.csv"
hdr = pd.read_csv(HDR, encoding="latin-1")
econ, eas = economies()
numbers = {}

# ---- Fig 1.1 HDI over time
cols = [f"hdi_{y}" for y in range(2004, 2024)]
h = hdr.set_index("iso3")
hdi = h.loc[GROUP + ["ZZF.EAP", "ZZK.WORLD"], cols].T
hdi.index = [int(c[-4:]) for c in hdi.index]
rank_sgp = int(h.loc[FOCUS, "hdi_rank_2023"])
n_ranked = int(h.hdi_rank_2023.notna().sum())
hdi_eas = rank_table(h[h.index.isin(eas)]["hdi_2023"], eas).loc[FOCUS]
numbers["hdi"] = {"value_2023": float(h.loc[FOCUS, "hdi_2023"]), "rank": rank_sgp, "n": n_ranked,
                  "eap_rank": int(hdi_eas["rank"]), "eap_n": int(hdi_eas.n),
                  "peers_2023": {k: float(h.loc[k, "hdi_2023"]) for k in GROUP},
                  "eap_avg_2023": float(h.loc["ZZF.EAP", "hdi_2023"]), "world_2023": float(h.loc["ZZK.WORLD", "hdi_2023"]),
                  "sgp_2004": float(h.loc[FOCUS, "hdi_2004"])}
line_chart(
    hdi,
    title=f"Singapore ranks {ordinal(rank_sgp)} of {n_ranked} countries on human development",
    subtitle="Human Development Index (0 to 1), 2004 to 2023. Dashed: East Asia & Pacific (EAP) and world averages",
    ylabel="Human Development Index",
    source="Source: UNDP, Human Development Report 2025, composite indices time series (hdi), downloaded "
           f"{retrieved(path=HDR)}. East Asia and the Pacific is UNDP's developing-country regional average.",
    out="ch01_hdi.png", fmt=lambda v: f"{v:.3f}", ymin=0.5, dashed=("ZZF.EAP", "ZZK.WORLD"),
    labels={"ZZF.EAP": "EAP average", "ZZK.WORLD": "World average"},
)

# ---- Fig 1.2 Economic structure (value added, % of GDP), latest common year
parts = {"Agriculture": "NV.AGR.TOTL.ZS", "Manufacturing": "NV.IND.MANF.ZS", "Services": "NV.SRV.TOTL.ZS"}
rows = {}
years = {}
for label, code in parts.items():
    d = load(code)
    d = d[d.iso3.isin(GROUP) & (d.year <= 2024)]
    last = d.sort_values("year").groupby("iso3").tail(1).set_index("iso3")
    rows[label] = last.value.reindex(GROUP)
    years[label] = last.year.reindex(GROUP).to_dict()
struct = pd.DataFrame(rows).T
numbers["structure"] = {"table": struct.round(1).to_dict(), "years": years}
y_note = sorted({int(y) for v in years.values() for y in v.values() if pd.notna(y)})
grouped_bars(
    struct,
    title=f"Manufacturing is still {struct.loc['Manufacturing', FOCUS]:.0f}% of Singapore's GDP, "
          f"unusual for a rich service hub",
    subtitle=f"Value added by sector, % of GDP, latest year ({' to '.join(map(str, (y_note[0], y_note[-1]))) if len(y_note) > 1 else y_note[0]})",
    xlabel="% of GDP", fmt=lambda v: f"{v:.1f}",
    source="Source: World Bank, World Development Indicators (NV.AGR.TOTL.ZS, NV.IND.MANF.ZS, NV.SRV.TOTL.ZS), "
           f"retrieved {retrieved('NV.IND.MANF.ZS')}. Shares need not sum to 100 (industry other than "
           "manufacturing and taxes on products are not shown).",
    out="ch01_structure.png",
)

# ---- Table 1.1 basic facts with ranks
facts = [  # label, code, higher_is_better(for rank direction), format, unit note
    ("Population", "SP.POP.TOTL", True, lambda v: f"{v / 1e6:.2f} m"),
    ("Land area", "AG.LND.TOTL.K2", True, lambda v: f"{v:,.0f} km²"),
    ("Population density", "EN.POP.DNST", True, lambda v: f"{v:,.0f} per km²"),
    ("Urban population", "SP.URB.TOTL.IN.ZS", True, lambda v: f"{v:.0f}%"),
    ("Life expectancy at birth", "SP.DYN.LE00.IN", True, lambda v: f"{v:.1f} years"),
    ("Tertiary enrolment (gross)", "SE.TER.ENRR", True, lambda v: f"{v:.0f}%"),
    ("Population aged 65+", "SP.POP.65UP.TO.ZS", True, lambda v: f"{v:.1f}%"),
]
lines = ["| Indicator | Singapore | Year | Global rank | East Asia & Pacific rank | Malaysia | Hong Kong SAR | Vietnam |",
         "| --- | --- | --- | --- | --- | --- | --- | --- |"]
table_numbers = {}
for label, code, hib, fmt in facts:
    d = load(code)
    d = d[d.year <= 2024]
    yr = int(d[d.iso3 == FOCUS].year.max())
    s = d[(d.year == yr) & d.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas, hib)
    r = t.loc[FOCUS]
    peer = []
    for iso in ["MYS", "HKG", "VNM"]:
        dp = d[d.iso3 == iso]
        peer.append(fmt(dp[dp.year == yr].value.iloc[0]) if (dp.year == yr).any() else "n/a")
    lines.append(f"| {label} | {fmt(r.value)} | {yr} | {ordinal(r['rank'])} of {int(r.n)} | "
                 f"{ordinal(r.region_rank)} of {int(r.region_n)} | " + " | ".join(peer) + " |")
    table_numbers[code] = {"value": float(r.value), "year": yr, "rank": int(r["rank"]), "n": int(r.n),
                           "region_rank": int(r.region_rank), "region_n": int(r.region_n)}
# HDI and schooling rows from UNDP
for label, col, fmt in [("Human Development Index", "hdi_2023", lambda v: f"{v:.3f}"),
                        ("Mean years of schooling", "mys_2023", lambda v: f"{v:.1f} years"),
                        ("Expected years of schooling", "eys_2023", lambda v: f"{v:.1f} years")]:
    s = h[h.index.isin(econ)][col]
    t = rank_table(s, eas, True)
    r = t.loc[FOCUS]
    lines.append(f"| {label} | {fmt(r.value)} | 2023 | {ordinal(r['rank'])} of {int(r.n)} | "
                 f"{ordinal(r.region_rank)} of {int(r.region_n)} | "
                 + " | ".join(fmt(h.loc[i, col]) for i in ["MYS", "HKG", "VNM"]) + " |")
    table_numbers[col] = {"value": float(r.value), "rank": int(r["rank"]), "n": int(r.n),
                          "region_rank": int(r.region_rank), "region_n": int(r.region_n)}
numbers["facts"] = table_numbers
note = ("\n*Ranks: 1st = highest value among economies with data that year (World Bank aggregates excluded); "
        "East Asia & Pacific = World Bank region. Sources: World Bank WDI (SP.POP.TOTL, AG.LND.TOTL.K2, EN.POP.DNST, "
        "SP.URB.TOTL.IN.ZS, SP.DYN.LE00.IN, SE.TER.ENRR, SP.POP.65UP.TO.ZS), retrieved "
        f"{retrieved('SP.POP.TOTL')}; UNDP Human Development Report 2025 (HDI, schooling).*\n")
DERIVED.mkdir(parents=True, exist_ok=True)
(DERIVED / "ch01_profile_table.md").write_text("\n".join(lines) + "\n" + note)
print("wrote data/derived/ch01_profile_table.md")
save_numbers("ch01", numbers)
print(struct.round(1).to_string())
print({k: (v["value"], v["rank"], v["region_rank"]) for k, v in table_numbers.items()})
