"""Ch. 2 Macroeconomy, business climate and governance.

Figures: GDP (current US$), GDP per capita (PPP), real growth, Gini (SingStat), WGI radar, CPI, B-READY topics.
Table: every Ch. 2 indicator with global and East Asia & Pacific ranks -> data/derived/ch02_rank_table.md.
Run: python scripts/ch02_macro.py
"""
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, NAMES, PEERS, RAW, economies, grouped_bars, line_chart, load,
                         ordinal, radar, rank_table, retrieved, save_numbers, wdi_rank, wide)

econ, eas = economies()
N = {}

# ---- 2.1 GDP, current US$
FOLD = {2: "doubled", 3: "tripled", 4: "grew about fourfold", 5: "grew about fivefold", 6: "grew about sixfold"}
gdp = wide("NY.GDP.MKTP.CD", GROUP)
sgp0, sgp1 = gdp.loc[2004, FOCUS] / 1e9, gdp.loc[2024, FOCUS] / 1e9
line_chart(
    gdp,
    title=f"Singapore's economy {FOLD.get(round(sgp1 / sgp0), f'grew {sgp1 / sgp0:.1f}x')} in 20 years, "
          f"to ${sgp1:,.0f}bn in 2024",
    subtitle="GDP in current US dollars, Singapore vs comparison economies, 2004 to 2024",
    ylabel="GDP, current US$ billions",
    source=f"Source: World Bank, World Development Indicators (NY.GDP.MKTP.CD), retrieved "
           f"{retrieved('NY.GDP.MKTP.CD')}. Current prices, not adjusted for inflation.",
    out="ch02_gdp_current_usd.png", fmt=lambda v: f"${v:,.0f}bn", scale=1e9,
)
N["gdp"] = {"2004_bn": sgp0, "2024_bn": sgp1, "ratio": sgp1 / sgp0,
            "rank_2004": wdi_rank("NY.GDP.MKTP.CD", 2004), "rank_2024": wdi_rank("NY.GDP.MKTP.CD", 2024),
            "ppp_rank_2024": wdi_rank("NY.GDP.MKTP.PP.CD", 2024)}

# ---- 2.1b GDP at PPP and GDP per capita in current US$ (the guidelines ask for both measures as time series)
gppp = wide("NY.GDP.MKTP.PP.CD", GROUP)
r_gppp = wdi_rank("NY.GDP.MKTP.PP.CD", 2024)
line_chart(
    gppp,
    title=f"At purchasing power parity Singapore's GDP reached ${gppp.loc[2024, FOCUS] / 1e9:,.0f}bn, "
          f"{ordinal(r_gppp['rank'])} in the world",
    subtitle="GDP, PPP (current international $), billions, 2004 to 2024",
    ylabel="GDP, PPP, billion international $",
    source=f"Source: World Bank, World Development Indicators (NY.GDP.MKTP.PP.CD), retrieved "
           f"{retrieved('NY.GDP.MKTP.PP.CD')}. PPP values adjust for differences in price levels across countries; "
           f"rank among {r_gppp['n']} economies with 2024 data.",
    out="ch02_gdp_ppp.png", fmt=lambda v: f"${v:,.0f}bn", scale=1e9,
)
pcu = wide("NY.GDP.PCAP.CD", GROUP + ["EAS", "WLD"])
r_pcu = wdi_rank("NY.GDP.PCAP.CD", 2024)
line_chart(
    pcu,
    title=f"In current dollars Singapore's GDP per person is ${pcu.loc[2024, FOCUS] / 1e3:,.0f}k, "
          f"{ordinal(r_pcu['rank'])} in the world",
    subtitle="GDP per capita, current US$, thousands, 2004 to 2024. Dashed: regional and world aggregates",
    ylabel="GDP per capita, thousand current US$",
    source=f"Source: World Bank, World Development Indicators (NY.GDP.PCAP.CD), retrieved "
           f"{retrieved('NY.GDP.PCAP.CD')}. Rank among {r_pcu['n']} economies with 2024 data.",
    out="ch02_gdp_per_capita_usd.png", fmt=lambda v: f"${v:,.0f}k", scale=1e3, dashed=("EAS", "WLD"),
    labels={"EAS": "East Asia & Pacific", "WLD": "World"},
)

# ---- 2.2 GDP per capita, PPP
pc = wide("NY.GDP.PCAP.PP.CD", GROUP + ["EAS", "WLD"])
r_pc = wdi_rank("NY.GDP.PCAP.PP.CD", 2024)
line_chart(
    pc,
    title=f"Singapore is the {ordinal(r_pc['rank'])} richest economy per person: "
          f"${pc.loc[2024, FOCUS] / 1e3:,.0f}k at PPP",
    subtitle="GDP per capita, PPP (current international $), 2004 to 2024. Dashed: regional and world aggregates",
    ylabel="GDP per capita, PPP, thousand intl $",
    source=f"Source: World Bank, World Development Indicators (NY.GDP.PCAP.PP.CD), retrieved "
           f"{retrieved('NY.GDP.PCAP.PP.CD')}. PPP adjusts for price levels across countries. Rank among "
           f"{r_pc['n']} economies with 2024 data.",
    out="ch02_gdp_per_capita_ppp.png", fmt=lambda v: f"${v:,.0f}k", scale=1e3, dashed=("EAS", "WLD"),
    labels={"EAS": "East Asia & Pacific", "WLD": "World"},
)
N["gdp_pc"] = {"ppp_2024": float(pc.loc[2024, FOCUS]), "ppp_rank": r_pc,
               "usd_rank": wdi_rank("NY.GDP.PCAP.CD", 2024),
               "usd_2024": float(wide("NY.GDP.PCAP.CD", [FOCUS]).loc[2024, FOCUS]),
               "ppp_2004": float(pc.loc[2004, FOCUS]),
               "peers_ppp_2024": {k: float(pc.loc[2024, k]) for k in GROUP}}

# ---- 2.3 Real GDP growth
g = wide("NY.GDP.MKTP.KD.ZG", GROUP)
avg = g.mean()
line_chart(
    g,
    title=f"Singapore averaged {avg[FOCUS]:.1f}% real growth a year, with slumps in 2009 and 2020",
    subtitle="Real GDP growth, % per year, 2004 to 2024 (constant prices)",
    ylabel="Real GDP growth, %",
    source=f"Source: World Bank, World Development Indicators (NY.GDP.MKTP.KD.ZG), retrieved "
           f"{retrieved('NY.GDP.MKTP.KD.ZG')}. Averages are simple means of annual rates, 2004 to 2024.",
    out="ch02_real_growth.png", fmt=lambda v: f"{v:.1f}%", ymin=None, zero_line=True,
)
econ_growth = load("NY.GDP.MKTP.KD.ZG")
econ_growth = econ_growth[econ_growth.iso3.isin(econ) & econ_growth.year.between(2004, 2024)]
full = econ_growth.groupby("iso3").filter(lambda d: len(d) == 21).groupby("iso3").value.mean()
gr = rank_table(full, eas).loc[FOCUS]
N["growth"] = {"avg": avg.round(2).to_dict(), "min": {k: (int(g[k].idxmin()), float(g[k].min())) for k in GROUP},
               "max": {k: (int(g[k].idxmax()), float(g[k].max())) for k in GROUP},
               "avg_rank": int(gr["rank"]), "avg_n": int(gr.n), "avg_region_rank": int(gr.region_rank),
               "avg_region_n": int(gr.region_n), "2024": g.loc[2024].round(2).to_dict()}

# ---- 2.4 Inequality: SingStat Gini (World Bank has no Singapore Gini or poverty data)
gini_raw = pd.read_csv(RAW / "singstat" / "17892.csv")
gini = gini_raw.pivot(index="period", columns="series_no", values="value").astype(float)
gini.index = gini.index.astype(int)
gini = gini.loc[2004:2025]
gini.columns = ["Before transfers", "After transfers"]
gini = gini[["After transfers", "Before transfers"]]  # focus series first (blue)
line_chart(
    gini,
    title=f"Singapore's Gini fell from {gini.iloc[:, 1].max():.3f} to {gini.loc[2025].iloc[1]:.3f} before "
          f"transfers, {gini.loc[2025].iloc[0]:.3f} after",
    subtitle="Gini of employment income per household member, resident employed households, 2004 to 2025",
    ylabel="Gini coefficient (0 = equal)",
    source="Source: Singapore Department of Statistics, table 17892 (Gini Coefficient Among Resident Employed "
           f"Households, incl. employer CPF contributions), downloaded {retrieved(path=RAW / 'singstat' / '17892.csv')}. "
           "Not comparable with World Bank survey-based Gini (none published for Singapore).",
    out="ch02_gini.png", fmt=lambda v: f"{v:.3f}", ymin=0.3, labels={c: c for c in gini.columns},
)
N["gini"] = {"before_2025": float(gini.loc[2025].iloc[1]), "after_2025": float(gini.loc[2025].iloc[0]),
             "before_peak": (int(gini.iloc[:, 1].idxmax()), float(gini.iloc[:, 1].max())),
             "before_2004": float(gini.loc[2004].iloc[1]), "after_2004": float(gini.loc[2004].iloc[0])}
wb_gini = load("SI.POV.GINI")
N["gini"]["peers_wb"] = {k: (int(d.year.max()), float(d.sort_values("year").value.iloc[-1]))
                         for k, d in wb_gini[wb_gini.iso3.isin(PEERS)].groupby("iso3")}
pov = load("SI.POV.DDAY")
N["poverty_peers"] = {k: (int(d.year.max()), float(d.sort_values("year").value.iloc[-1]))
                      for k, d in pov[pov.iso3.isin(PEERS + ["EAS", "WLD"])].groupby("iso3")}

# ---- 2.5 WGI radar (governance score 0-100, latest year)
dims = {"VA": "Voice and\naccountability", "PV": "Political\nstability", "GE": "Government\neffectiveness",
        "RQ": "Regulatory\nquality", "RL": "Rule of law", "CC": "Control of\ncorruption"}
wgi_year = int(load("GE.SC").year.max())
wgi_rows, wgi_ranks = {}, {}
for d, label in dims.items():
    df = load(f"{d}.SC")
    s = df[(df.year == wgi_year) & df.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas)
    wgi_rows[label] = {**{k: s.get(k) for k in GROUP}, "EAS": s[s.index.isin(eas)].mean()}
    wgi_ranks[d] = {"value": float(s[FOCUS]), "rank": int(t.loc[FOCUS, "rank"]), "n": int(t.loc[FOCUS, "n"]),
                    "region_rank": int(t.loc[FOCUS, "region_rank"]), "region_n": int(t.loc[FOCUS, "region_n"])}
wgi = pd.DataFrame(wgi_rows).T[GROUP + ["EAS"]]
wgi = wgi.rename(columns={"EAS": "East Asia & Pacific"})
firsts = [k for k, v in wgi_ranks.items() if v["rank"] == 1]
radar(
    wgi,
    title=f"Singapore is 1st in the world on {len(firsts)} governance dimensions, mid-table on voice",
    subtitle=f"Worldwide Governance Indicators, governance score (0 to 100), {wgi_year}. Dashed: East Asia & Pacific "
             "average",
    source=f"Source: World Bank, Worldwide Governance Indicators via WDI API (GOV_WGI_VA/PV/GE/RQ/RL/CC.SC), retrieved "
           f"{retrieved('GE.SC')}. Regional average: simple mean of World Bank East Asia & Pacific economies.",
    out="ch02_wgi_radar.png", ranks=[wgi_ranks[d] for d in dims],
)
N["wgi"] = {"year": wgi_year, "ranks": wgi_ranks, "table": wgi.round(1).to_dict()}

# ---- 2.6 Corruption Perceptions Index (scores comparable from 2012)
CPI = RAW / "manual" / "ti_cpi_2012_2024_owid.csv"
cpi_raw = pd.read_csv(CPI)
cpi = cpi_raw[cpi_raw.code.isin(GROUP)].pivot(index="year", columns="code", values="cpi_score")[GROUP]
c24 = cpi_raw[(cpi_raw.year == 2024) & cpi_raw.code.isin(econ)].set_index("code").cpi_score
ct = rank_table(c24, eas).loc[FOCUS]
line_chart(
    cpi,
    title=f"Singapore is the {ordinal(ct['rank'])} least corrupt of {int(ct.n)} economies (CPI {int(ct.value)}/100)",
    subtitle="Corruption Perceptions Index score (0 = highly corrupt, 100 = very clean), 2012 to 2024",
    ylabel="CPI score",
    source=f"Source: Transparency International, Corruption Perceptions Index 2012 to 2024, via Our World in Data, "
           f"downloaded {retrieved(path=CPI)}. Scores are comparable from 2012; earlier editions used another scale.",
    out="ch02_cpi.png", fmt=lambda v: f"{v:.0f}", ymin=0,
)
N["cpi"] = {"2024": int(ct.value), "rank": int(ct["rank"]), "n": int(ct.n), "region_rank": int(ct.region_rank),
            "region_n": int(ct.region_n), "peers_2024": cpi.loc[2024].to_dict(), "sgp_2012": float(cpi.loc[2012, FOCUS])}

# ---- 2.7 B-READY topics
topics = {"BE": "Business entry", "BL": "Business location", "US": "Utility services", "LB": "Labor",
          "FS": "Financial services", "IT": "International trade", "TX": "Taxation", "DR": "Dispute resolution",
          "MC": "Market competition", "BI": "Business insolvency"}
br_rows, br_ranks = {}, {}
for code, label in topics.items():
    df = load(f"IC.BRE.{code}.OS")
    s = df[df.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas)
    br_rows[label] = {k: s.get(k) for k in GROUP}
    br_ranks[label] = {"value": float(s[FOCUS]), "rank": int(t.loc[FOCUS, "rank"]), "n": int(t.loc[FOCUS, "n"]),
                       "region_rank": int(t.loc[FOCUS, "region_rank"]), "region_n": int(t.loc[FOCUS, "region_n"])}
br = pd.DataFrame(br_rows).T[GROUP]
br["_sgp"] = br[FOCUS]
br = br.sort_values("_sgp", ascending=False).drop(columns="_sgp")
pillars = {}
for code, label in {"P1.RF": "Regulatory framework", "P2.PS": "Public services", "P3.OE": "Operational efficiency"}.items():
    df = load(f"IC.BRE.{code}")
    s = df[df.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas)
    pillars[label] = {"value": float(s[FOCUS]), "rank": int(t.loc[FOCUS, "rank"]), "n": int(t.loc[FOCUS, "n"]),
                      "region_rank": int(t.loc[FOCUS, "region_rank"]), "region_n": int(t.loc[FOCUS, "region_n"]),
                      "peers": {k: s.get(k) for k in GROUP}}
n_br = br_ranks["Business entry"]["n"]
top5 = [k for k, v in br_ranks.items() if v["rank"] <= 5]
grouped_bars(
    br,
    title=f"Singapore is top 5 of {n_br} on {len(top5)} of 10 World Bank B-READY topics",
    subtitle="B-READY topic scores (0 to 100), 2025 edition, Singapore vs comparison economies",
    xlabel="Score (0 to 100)", fmt=lambda v: f"{v:.0f}",
    source=f"Source: World Bank, Business Ready (B-READY) via WDI API (IC.BRE.*.OS), retrieved {retrieved('IC.BRE.BL.OS')}. "
           f"Covers {n_br} economies; ranks are among those economies only.",
    out="ch02_bready.png",
)
N["bready"] = {"topics": br_ranks, "pillars": pillars}

# ---- Table 2.1: ranks for every indicator
lpi_year = int(load("LP.LPI.OVRL.XQ").query("iso3 == 'SGP'").year.max())
rows = [
    ("GDP, current US$", N["gdp"]["rank_2024"], lambda v: f"${v / 1e9:,.0f}bn"),
    ("GDP, PPP", N["gdp"]["ppp_rank_2024"], lambda v: f"${v / 1e9:,.0f}bn"),
    ("GDP per capita, current US$", N["gdp_pc"]["usd_rank"], lambda v: f"${v:,.0f}"),
    ("GDP per capita, PPP", N["gdp_pc"]["ppp_rank"], lambda v: f"${v:,.0f}"),
    ("Real GDP growth, 2024", wdi_rank("NY.GDP.MKTP.KD.ZG", 2024), lambda v: f"{v:.1f}%"),
    ("Inflation (CPI), 2024", wdi_rank("FP.CPI.TOTL.ZG", 2024, higher_is_better=False), lambda v: f"{v:.1f}%"),
    ("Current account, % of GDP", wdi_rank("BN.CAB.XOKA.GD.ZS", 2024), lambda v: f"{v:.1f}%"),
    ("Logistics Performance Index (1 to 5)", wdi_rank("LP.LPI.OVRL.XQ", lpi_year), lambda v: f"{v:.2f}"),
    ("Ease of Doing Business rank (legacy, DB2020 report)", wdi_rank("IC.BUS.EASE.XQ", 2019, higher_is_better=False),
     lambda v: f"{v:.0f} of 190"),
]
lines = ["| Indicator | Singapore | Year | Global rank | East Asia & Pacific rank |", "| --- | --- | --- | --- | --- |"]
for label, r, fmt in rows:
    lines.append(f"| {label} | {fmt(r['value'])} | {r['year']} | {ordinal(r['rank'])} of {r['n']} | "
                 f"{ordinal(r['region_rank'])} of {r['region_n']} |")
lines.append(f"| Average real growth 2004 to 2024 | {avg[FOCUS]:.1f}% | 2004 to 2024 | {ordinal(gr['rank'])} of {int(gr.n)} | "
             f"{ordinal(gr.region_rank)} of {int(gr.region_n)} |")
for d, label in dims.items():
    r = wgi_ranks[d]
    lines.append(f"| WGI: {label.replace(chr(10), ' ')} (0 to 100) | {r['value']:.1f} | {wgi_year} | "
                 f"{ordinal(r['rank'])} of {r['n']} | {ordinal(r['region_rank'])} of {r['region_n']} |")
lines.append(f"| Corruption Perceptions Index (0 to 100) | {N['cpi']['2024']} | 2024 | {ordinal(ct['rank'])} of {int(ct.n)} | "
             f"{ordinal(ct.region_rank)} of {int(ct.region_n)} |")
for label, r in pillars.items():
    lines.append(f"| B-READY: {label} (0 to 100) | {r['value']:.1f} | 2025 | {ordinal(r['rank'])} of {r['n']} | "
                 f"{ordinal(r['region_rank'])} of {r['region_n']} |")
lines.append(f"| Gini, after taxes and transfers (SingStat) | {N['gini']['after_2025']:.3f} | 2025 | not ranked¹ | not ranked¹ |")
lines.append("| Poverty headcount, $3.00/day (2021 PPP) | no data² | | | |")
note = ("\n*Ranks: 1st = best (highest, except inflation: lowest) among economies with data; World Bank aggregates "
        "excluded; ties share a rank. Doing Business (discontinued in 2021) ranked 190 economies; its last edition, "
        "DB2020, uses 2019 data (WDI IC.BUS.EASE.XQ). B-READY ranks are among the economies it covers. ¹ Singapore's Gini is a "
        "national series on employment income and is not comparable with survey-based Gini for other countries. "
        "² The World Bank publishes no poverty headcount for Singapore (no household survey in its database). Sources: "
        f"World Bank WDI, WGI and B-READY via the WDI API, retrieved {retrieved('GE.SC')}; Transparency International "
        "CPI; Singapore Department of Statistics.*\n")
(DERIVED / "ch02_rank_table.md").write_text("\n".join(lines) + "\n" + note)
print("wrote data/derived/ch02_rank_table.md")
N["lpi"] = wdi_rank("LP.LPI.OVRL.XQ", lpi_year)
N["doing_business_2019"] = wdi_rank("IC.BUS.EASE.XQ", 2019, higher_is_better=False)
N["inflation_2024"] = wdi_rank("FP.CPI.TOTL.ZG", 2024, higher_is_better=False)
N["current_account_2024"] = wdi_rank("BN.CAB.XOKA.GD.ZS", 2024)
save_numbers("ch02", N)
print("\n".join(lines))
print(br.round(1).to_string())
print(wgi.round(1).to_string())
print(N["growth"]["avg"], N["growth"]["min"])
print(N["poverty_peers"], N["gini"])
