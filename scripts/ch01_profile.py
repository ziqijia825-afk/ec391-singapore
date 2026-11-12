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

# ---- Fig 1.0 Long-run real GDP with structural breaks (Penn World Table 11.0)
PWT = RAW / "manual" / "pwt110.dta"
pwt = pd.read_stata(PWT, columns=["countrycode", "year", "rgdpna"])
lr = pwt[pwt.countrycode.isin(GROUP)].pivot(index="year", columns="countrycode", values="rgdpna")[GROUP] / 1e3
lr = lr.dropna(how="all").loc[1960:]
lr.index = lr.index.astype(int)
growth = lr[FOCUS].pct_change() * 100
breaks = {int(y): float(v) for y, v in growth.items() if v < 1}
line_chart(
    lr,
    title=f"Singapore's real GDP grew {lr[FOCUS].iloc[-1] / lr[FOCUS].iloc[0]:.0f}-fold since 1960, with six "
          "sharp breaks",
    subtitle=f"Real GDP at constant 2021 national prices, US$ billions, log scale, 1960 to {lr.index.max()}",
    ylabel="Real GDP, 2021 US$ billions (log scale)", fmt=lambda v: f"${v:,.0f}bn", ymin=None, logy=True,
    events=[(1965, "Independence"), (1985, "1985 recession"), (1998, "Asian crisis"), (2001, "Dot-com bust"),
            (2009, "Global financial crisis"), (2020, "COVID-19")],
    source=f"Source: Penn World Table 11.0 (rgdpna), Groningen Growth and Development Centre, downloaded "
           f"{retrieved(path=PWT)}. Breaks = years when Singapore's real GDP grew by less than 1% "
           f"({', '.join(str(y) for y in breaks)}).",
    out="ch01_long_run_gdp.png", height=5.8,
)
numbers["long_run"] = {"breaks": breaks, "ratio": float(lr[FOCUS].iloc[-1] / lr[FOCUS].iloc[0]),
                       "first": int(lr.index.min()), "last": int(lr.index.max())}

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

# ---- Fig 1.3 Human development and education vs regional and world averages (World Bank aggregates)
comp_rows = {}
comp_years = {}
for label, code in [("Life expectancy (years)", "SP.DYN.LE00.IN"), ("Adult literacy (%)", "SE.ADT.LITR.ZS"),
                    ("Secondary enrolment, gross (%)", "SE.SEC.ENRR"), ("Tertiary enrolment, gross (%)", "SE.TER.ENRR")]:
    d = load(code)
    d = d[d.iso3.isin([FOCUS, "EAS", "WLD"]) & (d.year <= 2024) & d.value.notna()]
    yr = int(d[d.iso3 == FOCUS].year.max())  # compare in Singapore's latest year, as the profile table does
    pick = {}
    for iso in [FOCUS, "EAS", "WLD"]:
        di = d[d.iso3 == iso].sort_values("year")
        row = di[di.year == yr] if (di.year == yr).any() else di.tail(1)
        pick[iso] = (float(row.value.iloc[0]), int(row.year.iloc[0]))
    comp_rows[label] = pd.Series({k: v[0] for k, v in pick.items()})
    comp_years[label] = {k: v[1] for k, v in pick.items()}
comp = pd.DataFrame(comp_rows).T
comp.loc["Human Development Index (x100)"] = [h.loc[FOCUS, "hdi_2023"] * 100, h.loc["ZZF.EAP", "hdi_2023"] * 100,
                                            h.loc["ZZK.WORLD", "hdi_2023"] * 100]
grouped_bars(
    comp,
    title=f"Singapore is ahead of the East Asia & Pacific average on every human development measure",
    subtitle="Singapore vs regional and world averages, each in Singapore's latest year with data",
    xlabel="Value (units in each row label)", fmt=lambda v: f"{v:.0f}",
    source=f"Source: World Bank WDI (SP.DYN.LE00.IN, SE.ADT.LITR.ZS, SE.SEC.ENRR, SE.TER.ENRR; East Asia & Pacific "
           f"and World aggregates), retrieved {retrieved('SE.ADT.LITR.ZS')}; UNDP HDR 2025 for HDI (UNDP's East Asia "
           f"and the Pacific average). Singapore's literacy is for {comp_years['Adult literacy (%)'][FOCUS]}, tertiary "
           f"enrolment for {comp_years['Tertiary enrolment, gross (%)'][FOCUS]}; gross enrolment can exceed 100%.",
    out="ch01_vs_region.png",
)
numbers["vs_region"] = {"table": comp.round(1).to_dict(), "years": comp_years}

# ---- Table 1.1 basic facts with ranks
facts = [  # label, code, higher_is_better(for rank direction), format, unit note
    ("Population", "SP.POP.TOTL", True, lambda v: f"{v / 1e6:.2f} m"),
    ("Land area", "AG.LND.TOTL.K2", True, lambda v: f"{v:,.0f} km²"),
    ("Population density", "EN.POP.DNST", True, lambda v: f"{v:,.0f} per km²"),
    ("Urban population", "SP.URB.TOTL.IN.ZS", True, lambda v: f"{v:.0f}%"),
    ("Life expectancy at birth", "SP.DYN.LE00.IN", True, lambda v: f"{v:.1f} years"),
    ("Adult literacy rate", "SE.ADT.LITR.ZS", True, lambda v: f"{v:.1f}%"),
    ("Secondary enrolment (gross)", "SE.SEC.ENRR", True, lambda v: f"{v:.0f}%"),
    ("Tertiary enrolment (gross)", "SE.TER.ENRR", True, lambda v: f"{v:.0f}%"),
    ("Population aged 65+", "SP.POP.65UP.TO.ZS", True, lambda v: f"{v:.1f}%"),
]
lines = ["| Indicator | Singapore | Year | Global rank | East Asia & Pacific rank | East Asia & Pacific average | "
         "Malaysia | Hong Kong SAR | Vietnam |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
table_numbers = {}
for label, code, hib, fmt in facts:
    d = load(code)
    d = d[d.year <= 2024]
    yr = int(d[d.iso3 == FOCUS].year.max())
    s = d[(d.year == yr) & d.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas, hib)
    r = t.loc[FOCUS]
    peer = []
    reg = d[(d.iso3 == "EAS")].sort_values("year")
    reg_txt = fmt(reg[reg.year == yr].value.iloc[0]) if (reg.year == yr).any() else (
        f"{fmt(reg.value.iloc[-1])} ({int(reg.year.iloc[-1])})" if len(reg) and code not in ("AG.LND.TOTL.K2", "SP.POP.TOTL") else "n/a")
    for iso in ["MYS", "HKG", "VNM"]:
        dp = d[d.iso3 == iso].sort_values("year")
        if (dp.year == yr).any():
            peer.append(fmt(dp[dp.year == yr].value.iloc[0]))
        elif len(dp):
            peer.append(f"{fmt(dp.value.iloc[-1])} ({int(dp.year.iloc[-1])})")
        else:
            peer.append("n/a")
    lines.append(f"| {label} | {fmt(r.value)} | {yr} | {ordinal(r['rank'])} of {int(r.n)} | "
                 f"{ordinal(r.region_rank)} of {int(r.region_n)} | {reg_txt} | " + " | ".join(peer) + " |")
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
                 f"{ordinal(r.region_rank)} of {int(r.region_n)} | {fmt(h.loc['ZZF.EAP', col])} (UNDP) | "
                 + " | ".join(fmt(h.loc[i, col]) for i in ["MYS", "HKG", "VNM"]) + " |")
    table_numbers[col] = {"value": float(r.value), "rank": int(r["rank"]), "n": int(r.n),
                          "region_rank": int(r.region_rank), "region_n": int(r.region_n)}
numbers["facts"] = table_numbers
note = ("\n*Ranks: 1st = highest value among economies with data that year (World Bank aggregates excluded); "
        "East Asia & Pacific = World Bank region; its average is the World Bank aggregate (UNDP's regional average for HDI "
        "and schooling, which covers developing economies only). A year in brackets marks an earlier latest year. Sources: World Bank WDI (SP.POP.TOTL, AG.LND.TOTL.K2, EN.POP.DNST, "
        "SP.URB.TOTL.IN.ZS, SP.DYN.LE00.IN, SE.ADT.LITR.ZS, SE.SEC.ENRR, SE.TER.ENRR, SP.POP.65UP.TO.ZS), retrieved "
        f"{retrieved('SP.POP.TOTL')}; UNDP Human Development Report 2025 (HDI, schooling).*\n")
DERIVED.mkdir(parents=True, exist_ok=True)
(DERIVED / "ch01_profile_table.md").write_text("\n".join(lines) + "\n" + note)
print("wrote data/derived/ch01_profile_table.md")
save_numbers("ch01", numbers)
print(struct.round(1).to_string())
print({k: (v["value"], v["rank"], v["region_rank"]) for k, v in table_numbers.items()})
