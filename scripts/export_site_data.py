"""Export the datasets used by the interactive components of the site (beyond the per-figure specs that
chart_style.py writes): landing KPIs, Sankey of trade partners by year, GVC network, FDI explorer, WGI by year,
RCA by year. Every dataset carries its source line. Run after the chapter scripts: python scripts/export_site_data.py
"""
import json

import numpy as np
import pandas as pd

from chart_style import FOCUS, GROUP, NAMES, RAW, ROOT, economies, load, rank_table, retrieved, sanitize

OUT = ROOT / "site" / "data"
OUT.mkdir(parents=True, exist_ok=True)
DER = ROOT / "data" / "derived"
econ, eas = economies()
C = pd.read_csv(RAW / "wdi" / "countries.csv", keep_default_na=False)
CNAME = dict(zip(C.iso3, C.name))
CNAME.update({"TWN": "Taiwan", "S19": "Taiwan", "HKG": "Hong Kong SAR", "KOR": "Korea, Rep.", "VNM": "Vietnam"})


def dump(name, obj):
    def clean(o):
        if isinstance(o, float) and np.isnan(o):
            return None
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(f"{float(o):.6g}")
        raise TypeError(type(o))
    (OUT / f"{name}.json").write_text(json.dumps(sanitize(obj), default=clean, separators=(",", ":"), allow_nan=False))
    print(f"wrote site/data/{name}.json")


def derived(ch):
    return json.loads((DER / f"{ch}.json").read_text())


# ---- country names for tooltips
names = dict(CNAME)
names.update({"TWN": "Taiwan", "SGP": "Singapore", "MYS": "Malaysia"})
(OUT / "names.json").write_text(json.dumps(names, separators=(",", ":")))

# ---- landing KPIs
d2, d3, d6, d1 = derived("ch02"), derived("ch03"), derived("ch06"), derived("ch01")
kpis = [
    {"label": "GDP, 2024", "value": f"${d2['gdp']['2024_bn']:,.0f}bn", "rank": d2["gdp"]["rank_2024"],
     "source": "World Bank WDI (NY.GDP.MKTP.CD)"},
    {"label": "GDP per person, PPP, 2024", "value": f"${d2['gdp_pc']['ppp_2024']:,.0f}", "rank": d2["gdp_pc"]["ppp_rank"],
     "source": "World Bank WDI (NY.GDP.PCAP.PP.CD)"},
    {"label": "Trade, % of GDP, 2024", "value": f"{d3['openness']['2024']['SGP']:.0f}%", "rank": d3["openness"]["rank"],
     "source": "World Bank WDI (NE.TRD.GNFS.ZS)"},
    {"label": "FDI inflows, % of GDP, 2024", "value": f"{d6['inflows_gdp']['2024']['SGP']:.0f}%",
     "rank": d6["inflows_gdp"]["rank_2024"], "source": "World Bank WDI (BX.KLT.DINV.WD.GD.ZS)"},
    {"label": "Human Development Index, 2023", "value": f"{d1['hdi']['value_2023']:.3f}",
     "rank": {"rank": d1["hdi"]["rank"], "n": d1["hdi"]["n"], "region_rank": d1["hdi"]["eap_rank"],
              "region_n": d1["hdi"]["eap_n"]}, "source": "UNDP HDR 2025"},
    {"label": "Government effectiveness, 2025", "value": f"{d2['wgi']['ranks']['GE']['value']:.1f}/100",
     "rank": d2["wgi"]["ranks"]["GE"], "source": "World Bank WGI"},
]
dump("kpis", {"kpis": kpis, "facts": {"capital": "Singapore", "area_km2": 745.1, "population_m": 6.21,
                                      "residents_m": 4.23, "nonresidents_m": 1.98,  # SingStat, Population Trends 2026
                                      "languages": "Malay (national), English, Mandarin, Tamil",
                                      "system": "Parliamentary republic", "coords": [103.82, 1.35]}})

# ---- Sankey: Singapore's imports by source -> Singapore -> exports by destination, every year
CT = RAW / "comtrade"
ASEAN = {"BRN", "KHM", "IDN", "LAO", "MYS", "MMR", "PHL", "THA", "VNM"}
EU = {"AUT", "BEL", "BGR", "HRV", "CYP", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN", "IRL", "ITA", "LVA",
      "LTU", "LUX", "MLT", "NLD", "POL", "PRT", "ROU", "SVK", "SVN", "ESP", "SWE"}
FTA = {"USA": "US-Singapore FTA (2004)", "CHN": "China-Singapore FTA (2009); ASEAN-China (2005)",
       "JPN": "Japan-Singapore EPA (2002)", "KOR": "Korea-Singapore FTA (2006)", "IND": "India-Singapore CECA (2005)",
       "AUS": "Singapore-Australia FTA (2003)", "NZL": "ANZSCEP (2001)", "HKG": "ASEAN-Hong Kong FTA (2019)",
       "GBR": "UK-Singapore FTA (2021)", "TWN": "ASTEP (2014, outside METI's FTA count)",
       "CHE": "EFTA-Singapore FTA (2003)", "NOR": "EFTA-Singapore FTA (2003)", "ARE": "GCC-Singapore FTA (2013)",
       "SAU": "GCC-Singapore FTA (2013)", "QAT": "GCC-Singapore FTA (2013)", "TUR": "Türkiye-Singapore FTA (2017)",
       "PAN": "Panama-Singapore FTA (2006)", "PER": "Peru-Singapore FTA (2009)", "MEX": "CPTPP (2018)",
       "CAN": "CPTPP (2018)", "CHL": "TPSEP (2006)", "LKA": "Sri Lanka-Singapore FTA (2018)",
       "JOR": "Jordan-Singapore FTA (2005)", "CRI": "Costa Rica-Singapore FTA (2013)"}
lat = C[C.lat != ""].set_index("iso3")[["lat", "lon"]].astype(float)


def km(iso):
    if iso not in lat.index:
        return None
    a, b = np.radians(lat.loc[FOCUS]), np.radians(lat.loc[iso])
    return float(6371 * 2 * np.arcsin(np.sqrt(np.sin((b.lat - a.lat) / 2) ** 2 + np.cos(a.lat) * np.cos(b.lat)
                                              * np.sin((b.lon - a.lon) / 2) ** 2)))


years, partners = {}, {}
for y in range(2004, 2025):
    row = {}
    for flow in ("X", "M"):
        f = pd.read_csv(CT / f"sgp_{flow}_partners_{y}.csv", dtype={"partner_iso3": str})
        world = float(f.loc[f.partner_code == 0, "value_usd"].iloc[0])
        f = f[f.partner_code != 0].copy()
        f["iso"] = f.partner_iso3.replace({"S19": "TWN"})
        f = f.groupby("iso").value_usd.sum().sort_values(ascending=False)
        row[flow] = {"world_bn": world / 1e9, "top": [[k, float(v / 1e9)] for k, v in f.head(10).items()],
                     "other_bn": float((world - f.head(10).sum()) / 1e9)}
        for k, v in f.items():
            partners.setdefault(k, {"X": {}, "M": {}})[flow][y] = float(v / world * 100)
    years[y] = row
keep = {k for r in years.values() for flow in ("X", "M") for k, _ in r[flow]["top"]}
pinfo = {k: {"name": CNAME.get(k, k), "km": km(k), "fta": FTA.get(k) or ("ASEAN (AFTA 1993) and RCEP (2022)" if k in ASEAN
         else "EU-Singapore FTA (2019)" if k in EU else None),
         "share_x": partners[k]["X"], "share_m": partners[k]["M"]} for k in keep}
dump("sankey", {"years": years, "partners": pinfo,
                "source": f"UN Comtrade, Singapore's reported merchandise trade by partner (incl. re-exports), "
                          f"downloaded {retrieved(path=CT / 'sgp_X_partners_2024.csv')}; distances from World Bank "
                          "capital coordinates; FTAs from Enterprise Singapore."})

# ---- GVC network (OECD TiVA origin of value added in gross exports)
TIVA = RAW / "tiva"
tot = pd.read_csv(TIVA / "tiva_total_all.csv", usecols=["MEASURE", "REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
econ_t = econ | {"TWN"}
tot = tot[tot.REF_AREA.isin(econ_t)].pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="MEASURE",
                                                 values="OBS_VALUE")
orig = pd.read_csv(TIVA / "tiva_origin_matrix.csv",
                   usecols=["VALUE_ADDED_SOURCE_AREA", "EXPORTING_AREA", "TIME_PERIOD", "OBS_VALUE"])
orig = orig[orig.EXPORTING_AREA.isin(econ_t) & orig.VALUE_ADDED_SOURCE_AREA.isin(econ_t)]
fwd = (orig[orig.VALUE_ADDED_SOURCE_AREA != orig.EXPORTING_AREA]
       .groupby(["VALUE_ADDED_SOURCE_AREA", "TIME_PERIOD"]).OBS_VALUE.sum())
fwd.index.names = ["REF_AREA", "TIME_PERIOD"]
tot["backward"] = tot.EXGR_FVA / tot.EXGR * 100
tot["forward"] = fwd.reindex(tot.index) / tot.EXGR * 100
tot["position"] = np.log1p(tot.forward / 100) - np.log1p(tot.backward / 100)
net = {}
for y in sorted(orig.TIME_PERIOD.unique()):
    o = orig[orig.TIME_PERIOD == y]
    src = o[(o.EXPORTING_AREA == FOCUS) & (o.VALUE_ADDED_SOURCE_AREA != FOCUS)].set_index("VALUE_ADDED_SOURCE_AREA").OBS_VALUE
    dst = o[(o.VALUE_ADDED_SOURCE_AREA == FOCUS) & (o.EXPORTING_AREA != FOCUS)].set_index("EXPORTING_AREA").OBS_VALUE
    nodes = set(src.nlargest(10).index) | set(dst.nlargest(10).index) | {FOCUS, "MYS", "HKG", "VNM"}
    cur = tot.xs(y, level=1)
    net[int(y)] = {
        "nodes": [{"id": k, "name": CNAME.get(k, k), "exgr_bn": float(cur.loc[k, "EXGR"] / 1e3),
                   "backward": float(cur.loc[k, "backward"]), "forward": float(cur.loc[k, "forward"]),
                   "position": float(cur.loc[k, "position"])} for k in nodes if k in cur.index],
        "in": [[k, float(v / 1e3)] for k, v in src[src.index.isin(nodes)].items()],
        "out": [[k, float(v / 1e3)] for k, v in dst[dst.index.isin(nodes)].items()],
    }
series = {k: {int(y): [float(r.backward), float(r.forward)] for y, r in tot.xs(k, level=0).iterrows()}
          for k in tot.index.get_level_values(0).unique()}
dump("gvc", {"network": net, "series": series, "names": {k: CNAME.get(k, k) for k in series},
             "source": f"OECD TiVA 2025 edition (EXGR, EXGR_FVA; EXGRVA origin of value added), retrieved "
                       f"{retrieved(path=TIVA / 'tiva_total_all.csv')}; team calculation. US$ billions."})

# ---- FDI explorer (SingStat): inward/outward stock by economy and by industry, every year
SS = RAW / "singstat"


def ss(table):
    d = pd.read_csv(SS / f"{table}.csv", dtype={"series_no": str, "period": str})
    d["value"] = pd.to_numeric(d.value, errors="coerce")
    d = d[d.period.str.fullmatch(r"\d{4}")]
    d["year"] = d.period.astype(int)
    return d[d.year >= 2004]


def panel(table, depth, exclude=(), rename=None):
    d = ss(table)
    tot_ = d[d.series_no == "1"].set_index("year").value
    parts = d[(d.series_no.str.count(r"\.") == depth) & ~d.series.isin(exclude)]
    wide_ = parts.pivot_table(index="year", columns="series", values="value") / 1e3
    if rename:
        wide_ = wide_.rename(columns=rename)
    top = wide_.loc[wide_.index.max()].sort_values(ascending=False).head(10).index
    out = wide_[top].copy().fillna(0)  # unpublished (confidential) cells shown as zero in the stacked view
    rest = tot_ / 1e3 - out.sum(axis=1)
    if (rest.abs() > 0.5).any():
        out["All other"] = rest.clip(lower=0)
    return {"years": [int(y) for y in out.index], "total": [float(v / 1e3) for v in tot_.reindex(out.index)],
            "series": [{"name": c, "values": [None if pd.isna(v) else float(v) for v in out[c]]} for c in out.columns]}


pretty = {"United States Of America": "United States", "Republic Of Korea": "Korea"}
fdi = {
    "inward_source": panel("M083801", 2, rename=pretty),
    "inward_industry": panel("M084831", 1),
    "outward_destination": panel("M084431", 2, rename=pretty),
    "outward_industry": panel("M084441", 1),
    "hubs": ["Cayman Islands", "British Virgin Islands", "Bermuda", "Luxembourg", "Netherlands", "Bahamas",
             "Mauritius", "Ireland"],
    "unit": "S$ billions, stock at year-end",
    "source": f"Singapore Department of Statistics, tables M083801, M084831, M084431, M084441, downloaded "
              f"{retrieved(path=SS / 'M083801.csv')}. Recorded by immediate investor / immediate destination; cells "
              "SingStat does not publish (confidential) are shown as zero.",
}
dump("fdi", fdi)

# ---- WGI scores and ranks by year (for the radar's year control)
dims = {"VA": "Voice and accountability", "PV": "Political stability", "GE": "Government effectiveness",
        "RQ": "Regulatory quality", "RL": "Rule of law", "CC": "Control of corruption"}
wgi = {}
for d, label in dims.items():
    df = load(f"{d}.SC")
    for y, g in df[df.iso3.isin(econ)].groupby("year"):
        s = g.set_index("iso3").value
        t = rank_table(s, eas)
        row = wgi.setdefault(int(y), {})
        row[d] = {"values": {k: (float(s[k]) if k in s.index else None) for k in GROUP},
                  "eap": float(s[s.index.isin(eas)].mean()),
                  "rank": {k: [int(t.loc[k, "rank"]), int(t.loc[k, "n"]), int(t.loc[k, "region_rank"]),
                               int(t.loc[k, "region_n"])] for k in GROUP if k in t.index}}
dump("wgi", {"dims": dims, "years": wgi, "names": {k: NAMES[k] for k in GROUP},
             "source": f"World Bank, Worldwide Governance Indicators (GOV_WGI_*.SC, governance score 0 to 100), "
                       f"retrieved {retrieved('GE.SC')}; ranks among economies with data, region = East Asia & Pacific."})

# ---- RCA by year (written by ch04_rca.py when BACI data are available)
rca_path = DER / "rca_years.json"
if rca_path.exists():
    (OUT / "rca.json").write_text(rca_path.read_text())
    print("wrote site/data/rca.json")

# ---------------------------------------------------------------- chapter number cards (book title spreads)
from chart_style import ordinal  # noqa: E402


def rk(r, region=True):
    s = f"{ordinal(r['rank'])} of {r['n']}"
    return s + (f" · {ordinal(r['region_rank'])} in East Asia & Pacific" if region and r.get("region_rank") else "")


c1, c2, c3, c4, c5, c6, c7, c9 = (derived(c) for c in ("ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch09"))
ge = c2["wgi"]["ranks"]["GE"]
tiles = {
    "ch01_profile": [
        {"value": f"{c1['hdi']['value_2023']:.3f}", "label": "Human Development Index, 2023",
         "rank": f"{ordinal(c1['hdi']['rank'])} of {c1['hdi']['n']} · {ordinal(c1['hdi']['eap_rank'])} in the region"},
        {"value": f"{c1['long_run']['ratio']:.0f}×", "label": f"Growth of real GDP, {c1['long_run']['first']} to {c1['long_run']['last']}",
         "rank": "Penn World Table"},
        {"value": f"{c1['structure']['table']['SGP']['Manufacturing']:.0f}%", "label": "Manufacturing share of GDP, 2024",
         "rank": f"Malaysia {c1['structure']['table']['MYS']['Manufacturing']:.0f}%, Hong Kong SAR {c1['structure']['table']['HKG']['Manufacturing']:.0f}%"}],
    "ch02_macro": [
        {"value": f"${c2['gdp_pc']['ppp_2024'] / 1e3:,.0f}k", "label": "GDP per person at PPP, 2024", "rank": rk(c2["gdp_pc"]["ppp_rank"])},
        {"value": f"${c2['gdp']['2024_bn']:,.0f}bn", "label": "GDP, current US$, 2024", "rank": rk(c2["gdp"]["rank_2024"])},
        {"value": f"{ge['value']:.1f}", "label": "Government effectiveness (WGI), 2025", "rank": rk(ge)}],
    "ch03_trade": [
        {"value": f"{c3['openness']['2024']['SGP']:.0f}%", "label": "Trade in goods and services, % of GDP, 2024", "rank": rk(c3["openness"]["rank"])},
        {"value": f"${c3['balances']['services_exports_rank']['value'] / 1e9:,.0f}bn", "label": "Services exports, 2024",
         "rank": rk(c3["balances"]["services_exports_rank"])},
        {"value": f"{c3['reexports']['share']['Re-exports']['2024']:.1f}%", "label": "Re-exports, % of merchandise exports, 2024",
         "rank": f"{c3['reexports']['share']['Re-exports']['2004']:.1f}% in 2004"}],
    "ch04_rca": [
        {"value": f"{c4['rca_sector']['2024']['SGP']['Transport & logistics']:.1f}", "label": "RCA, transport and logistics, 2024",
         "rank": f"{c4['rca_sector']['2004']['SGP']['Transport & logistics']:.1f} in 2004"},
        {"value": f"{c4['rca_sector']['2024']['SGP']['Finance & insurance']:.1f}", "label": "RCA, finance and insurance, 2024",
         "rank": f"{c4['rca_sector']['2004']['SGP']['Finance & insurance']:.1f} in 2004"},
        {"value": f"${c4['endowments']['kl_sgp'] / 1e3:,.0f}k", "label": f"Capital per worker, {c4['endowments']['pwt_year']}",
         "rank": f"{ordinal(c4['endowments']['kl_rank'])} of {c4['endowments']['kl_n']}"}],
    "ch05_gvc": [
        {"value": f"{c5['backward']['sgp']:.1f}%", "label": f"Foreign value added in exports, {c5['year']}", "rank": rk(c5["backward"])},
        {"value": f"{c5['participation']['sgp']:.1f}%", "label": f"GVC participation, {c5['year']}", "rank": rk(c5["participation"])},
        {"value": f"{c5['position']['sgp']:.2f}".replace("-", "−"), "label": "Position index (below 0 = downstream)", "rank": rk(c5["position"], False)}],
    "ch06_fdi": [
        {"value": f"{c6['inflows_gdp']['2024']['SGP']:.1f}%", "label": "FDI net inflows, % of GDP, 2024", "rank": rk(c6["inflows_gdp"]["rank_2024"])},
        {"value": f"${c6['inflows_gdp']['inflows_usd_rank_2024']['value'] / 1e9:,.0f}bn", "label": "FDI net inflows, 2024",
         "rank": rk(c6["inflows_gdp"]["inflows_usd_rank_2024"])},
        {"value": f"{c6['stocks']['pct_gdp']['Inward FDI stock']['2024']:.0f}%", "label": "Inward FDI stock, % of GDP, 2024",
         "rank": f"Outward {c6['stocks']['pct_gdp']['Outward FDI stock']['2024']:.0f}%"}],
    "ch07_policy": [
        {"value": f"{c7['TM.TAX.MRCH.SM.FN.ZS']['value']:.2f}%", "label": "Average MFN tariff, 2022",
         "rank": rk(c7["TM.TAX.MRCH.SM.FN.ZS"])},
        {"value": str(c7["fta"]["n"]), "label": "Free trade agreements in force", "rank": f"{c7['fta']['count_2004']} in 2004"},
        {"value": str(c7["bits"]["n"]), "label": "Bilateral investment treaties", "rank": f"first in {c7['bits']['first'][:4]}"}],
    "ch09_case": [
        {"value": f"{c9['rca_groups']['Chips']['2024']:.1f}", "label": "RCA in chips (HS 8541, 8542), 2024",
         "rank": f"{c9['ic_world_share']['2024']:.1f}% of world IC exports"},
        {"value": f"{c9['rca_groups']['Finished pharma']['2024']:.1f}", "label": "RCA in finished pharma and biologics, 2024",
         "rank": f"{c9['rca_groups']['Finished pharma']['2004']:.2f} in 2004"},
        {"value": f"{c9['va_share']['Semiconductors']['2025']:.0f}%", "label": "Chips' share of manufacturing value added, 2025",
         "rank": f"pharma {c9['va_share']['Pharmaceuticals']['2025']:.0f}%"}],
    "conclusion": [  # one number from each part of the argument
        {"value": f"{c3['openness']['2024']['SGP']:.0f}%", "label": "Trade, % of GDP, 2024 (Chapter 3)", "rank": rk(c3["openness"]["rank"], False)},
        {"value": f"{c6['stocks']['pct_gdp']['Inward FDI stock']['2024']:.0f}%", "label": "Inward FDI stock, % of GDP, 2024 (Chapter 6)",
         "rank": f"outward {c6['stocks']['pct_gdp']['Outward FDI stock']['2024']:.0f}%"},
        {"value": ordinal(ge["rank"]), "label": "Government effectiveness, world rank, 2025 (Chapter 2)", "rank": f"of {ge['n']} economies"}],
}
(ROOT / "data" / "derived" / "tiles.json").write_text(json.dumps(tiles, indent=1, ensure_ascii=False))

# ---------------------------------------------------------------- the one-minute summary after the cover (index)
sr = c6["stock_ranks"]["inward"]
svc = c3["structure"]["services_share"]
cards = [
    ("ch03_trade", "Chapter 3", f"{c3['openness']['2024']['SGP']:.0f}%",
     f"Trade in goods and services is three times GDP, {ordinal(c3['openness']['rank']['rank'])} of {c3['openness']['rank']['n']} economies."),
    ("ch04_rca", "Chapter 4", f"{svc['2024']:.0f}%",
     f"of exports are services, up from {svc['2004']:.0f}% in 2004, led by transport (RCA "
     f"{c4['rca_sector']['2024']['SGP']['Transport & logistics']:.1f}) and finance "
     f"({c4['rca_sector']['2024']['SGP']['Finance & insurance']:.1f})."),
    ("ch02_macro", "Chapter 2", ordinal(ge["rank"]),
     f"of {ge['n']} on government effectiveness. Courts and regulators work as an export advantage."),
    ("ch05_gvc", "Chapter 5", f"{c5['backward']['sgp']:.0f}%",
     "of the value of exports is made abroad. Singapore sits downstream, processing and coordinating Asia's supply chains."),
    ("ch06_fdi", "Chapter 6", ordinal(sr["rank"]),
     f"of {sr['n']} for inward FDI stock relative to GDP, much of it passing through holding companies."),
    ("ch07_policy", "Chapter 7", f"{c7['TM.TAX.MRCH.SM.FN.ZS']['value']:.2f}%",
     f"average MFN tariff, while {c7['fta']['n']} trade agreements open partners' markets."),
    ("ch09_case", "Chapter 9", f"{c9['did']['pct'] / 100 + 1:.1f}×",
     f"rise in the pharmaceutical advantage after the 2000 biomedical push, while chips kept an RCA of "
     f"{c9['rca_groups']['Chips']['2024']:.1f}."),
]
cards.sort(key=lambda c: c[1])  # in chapter order
summary = ('<section class="summary"><p class="sm-eyebrow">Singapore in one minute</p>'
           '<h2 class="sm-h">A location turned into an economy by institutions and foreign capital</h2><div class="sm-grid">'
           + "".join(f'<a class="sm" href="#{ch}"><b>{num}</b><span>{txt}</span><i>{lab} &rarr;</i></a>'
                     for ch, lab, num, txt in cards)
           + '<a class="sm sm-verdict" href="#conclusion"><b>Verdict</b><span>The region\'s best base for headquarters and high '
             'value production, and a costly one for everything else.</span><i>Conclusion &rarr;</i></a></div></section>')
(ROOT / "data" / "derived" / "summary.md").write_text(summary + "\n", encoding="utf-8")
print("wrote data/derived/summary.md")
print("wrote data/derived/tiles.json")

# ---------------------------------------------------------------- Ch. 5 value-chain cards (numbers from ch05/ch09)
sec = {r["sector"]: r for r in c5["sectors"] if r["iso"] == "SGP"}
cards = [
    ("Chips", "Midstream", "Wafers, tools and designs come in, and Singapore fabricates and tests the chips that assemblers across Asia build into devices.",
     f"{sec['Electronics & instruments']['fva_share']:.0f}%", "foreign value in electronics exports"),
    ("Refining", "Downstream processing", "Every barrel of crude is imported, and the refineries on Jurong Island turn it into fuels that leave by sea.",
     f"{sec['Refined petroleum']['fva_share']:.0f}%", "foreign value in refined fuel exports"),
    ("Biologics", "Midstream", "Plants make active ingredients and biologics that are formulated, packed and sold by parent firms abroad.",
     f"{c9['rca_products']['3002 Biologics and vaccines']['2024']:.1f}", "RCA in biologics and vaccines, 2024"),
    ("Logistics and finance", "Hub services", "Ships, warehouses, banks and insurers move and finance goods made elsewhere in the region.",
     f"{sec['Finance & insurance']['fva_share']:.0f}%", "foreign value in finance exports, the most domestic sector"),
]
html = ['<section class="chains">'] + [
    f'<div class="chain"><h4>{t}</h4><span class="pos">{p}</span><p>{d}</p><b>{v}</b><small>{lab}</small></div>'
    for t, p, d, v, lab in cards] + [f'<p class="chains-src">OECD TiVA 2025 edition ({c5["year"]}) and CEPII BACI, team calculations.</p></section>']
(ROOT / "data" / "derived" / "ch05_chains.md").write_text("".join(html) + "\n")
print("wrote data/derived/ch05_chains.md")

# ---------------------------------------------------------------- Ch. 9 scorecard (numbers from ch09.json)
g, va, fs = c9["rca_groups"], c9["va_share"], c9["fdi_stock_sgd_bn"]
first_semi = min(fs["Semiconductors"], key=int)
rows = [
    ("Revealed comparative advantage, 2004 to 2024",
     f"{g['Chips']['2004']:.1f} to {g['Chips']['2024']:.1f}",
     f"finished {g['Finished pharma']['2004']:.2f} to {g['Finished pharma']['2024']:.2f}, ingredients {g['Pharma ingredients']['2004']:.1f} to {g['Pharma ingredients']['2024']:.1f}"),
    ("Share of manufacturing value added, 2004 to 2025",
     f"{va['Semiconductors']['2004']:.0f}% to {va['Semiconductors']['2025']:.0f}%", f"{va['Pharmaceuticals']['2004']:.0f}% to {va['Pharmaceuticals']['2025']:.1f}%"),
    ("Inward FDI stock, S$ billion",
     f"{fs['Semiconductors'][first_semi]:.0f} ({first_semi}) to {fs['Semiconductors']['2024']:.0f} (2024)",
     f"{fs['Pharmaceuticals']['2004']:.0f} (2004) to {fs['Pharmaceuticals']['2024']:.0f} (2024)"),
    ("Reading in the learning curve model", "a strong advantage held while value added and investment grew",
     "export advantage without a deeper domestic industry"),
]
md = ["| Scorecard | Chips (HS 8541, 8542) | Pharmaceuticals (HS 2933 to 2941, 3002, 3004) |", "| --- | --- | --- |"]
md += [f"| {a} | {b} | {c} |" for a, b, c in rows]
md.append("\n*Sources: team calculation from CEPII BACI (RCA, world shares); EDB Census of Manufacturing Activities via SingStat "
          "M355181 (value added, 2025 preliminary); SingStat M084831 (FDI stock).*\n")
(ROOT / "data" / "derived" / "ch09_scorecard.md").write_text("\n".join(md))
print("wrote data/derived/ch09_scorecard.md")

# ---------------------------------------------------------------- Ch. 1 data atlas: places and partners
# Every number below is read from data/derived; the notes are the team's own wording and link each place to a course idea.
c4e = c4["endowments"]
ntm_sg = next(r for r in c7["ntm"]["summary"] if r["iso3"] == "SGP")
reex = c3["reexports"]["share"]
ind = c6["industries_2024"]
sites = [
    {"id": "port", "section": "Does its trade follow gravity?", "name": "Pasir Panjang port", "coord": [103.765, 1.272], "chapter": "ch03_trade", "chapter_label": "Chapter 3",
     "tag": "Feyrer 2009", "rows": [
        [f"{c4['rca_sector']['2024']['SGP']['Transport & logistics']:.1f}", "RCA in transport and logistics, 2024",
         f"{c4['rca_sector']['2004']['SGP']['Transport & logistics']:.1f} in 2004, team calculation"],
        [f"{c3['structure']['exports']['Transport services']['2024']:.1f}%", "of exports are transport services, 2024", "World Bank BoP and BACI"],
        [f"{reex['Re-exports']['2024']:.1f}%", "of merchandise exports are re-exports, 2024", f"{reex['Re-exports']['2004']:.1f}% in 2004, SingStat"],
        [f"{c2['lpi']['value']:.2f}", f"Logistics Performance Index, {c2['lpi']['year']}", f"{ordinal(c2['lpi']['rank'])} of {c2['lpi']['n']}, World Bank"]],
     "note": "Ships between the Indian Ocean and East Asia pass this port, so Singapore earns a living by moving goods made elsewhere. "
             "Feyrer's Suez Canal experiment shows that sea distance is a real trade cost, and the port exists to lower it."},
    {"id": "jurong", "section": "Does it fit Heckscher Ohlin?", "name": "Jurong Island", "coord": [103.69, 1.262], "chapter": "ch04_rca", "chapter_label": "Chapter 4",
     "tag": "Nunn 2007", "rows": [
        [f"{sec['Refined petroleum']['fva_share']:.0f}%", f"foreign value in refined fuel exports, {c5['year']}", "OECD TiVA"],
        [f"{c4['rca_sector']['2024']['SGP']['Refined petroleum']:.2f}", "RCA in refined petroleum, 2024",
         f"{c4['rca_sector']['2004']['SGP']['Refined petroleum']:.2f} in 2004, team calculation"],
        [f"{reex['Oil domestic exports']['2024']:.1f}%", "of merchandise exports are oil made in Singapore, 2024", "SingStat"],
        [f"{c4['rca_sector']['2024']['SGP']['Chemicals & plastics']:.2f}", "RCA in chemicals and plastics, 2024",
         f"{c4['rca_sector']['2004']['SGP']['Chemicals & plastics']:.2f} in 2004"]],
     "note": "Crude comes in and fuels and plastics go out. Refining is among Nunn's least contract intensive industries, and it lost its "
             "advantage as capacity grew in the Middle East and China, while Singapore's skill and contract intensive sectors kept theirs."},
    {"id": "fabs", "section": "The scorecard", "name": "Wafer fab parks", "coord": [103.789, 1.447], "chapter": "ch09_case", "chapter_label": "Chapter 9",
     "tag": "Infant industry", "rows": [
        [f"{c9['rca_groups']['Chips']['2024']:.1f}", "RCA in chips, 2024", f"{c9['rca_groups']['Chips']['1995']:.1f} in 1995, team calculation from BACI"],
        [f"${c9['ic_exports_bn']['2024']:.1f}bn", "integrated circuit exports, 2024", f"{c9['ic_world_share']['2024']:.1f}% of the world, BACI"],
        [f"{c9['va_share']['Semiconductors']['2025']:.0f}%", "of manufacturing value added, 2025", "EDB census via SingStat"],
        [f"S${c9['fdi_stock_sgd_bn']['Semiconductors']['2024']:.0f}bn", "foreign investment stock in chips, 2024", "SingStat"]],
     "note": "Woodlands, Tampines and Pasir Ris host the wafer fabs. Chips are the infant industry that grew up without a tariff, "
             "drawn in by tax holidays in 1968 and moved up into fabrication from 1987."},
    {"id": "tuas", "section": "The scorecard", "name": "Tuas Biomedical Park", "coord": [103.635, 1.322], "chapter": "ch09_case", "chapter_label": "Chapter 9",
     "tag": "Infant industry", "rows": [
        [f"{c9['rca_groups']['Finished pharma']['2024']:.2f}", "RCA in finished medicines and biologics, 2024",
         f"{c9['rca_groups']['Finished pharma']['2004']:.2f} in 2004, team calculation"],
        [f"{c9['rca_products']['3002 Biologics and vaccines']['2024']:.2f}", "RCA in biologics and vaccines, 2024", "HS 3002, BACI"],
        [f"{c9['va_share']['Pharmaceuticals']['2025']:.1f}%", "of manufacturing value added, 2025",
         f"{c9['va_share']['Pharmaceuticals']['2004']:.0f}% in 2004, EDB census"],
        [f"S${c9['fdi_stock_sgd_bn']['Pharmaceuticals']['2024']:.0f}bn", "foreign investment stock in pharma, 2024",
         f"S${c9['fdi_stock_sgd_bn']['Pharmaceuticals']['2004']:.0f}bn in 2004, SingStat"]],
     "note": "The second bet of the industrial policy, launched in 2000. Its plants built a real export advantage in biologics, "
             "while the industry's weight in value added and foreign capital at home shrank."},
    {"id": "onenorth", "section": "Which sectors rely most on foreign inputs?", "name": "one-north and Biopolis", "coord": [103.789, 1.299], "chapter": "ch05_gvc", "chapter_label": "Chapter 5",
     "tag": "Fort 2017", "rows": [
        [f"{c4e['hc_sgp']:.2f}", "human capital index, PWT", f"{ordinal(c4e['hc_rank'])} of {c4e['hc_n']}"],
        [f"{c1['vs_region']['table']['SGP']['Tertiary enrolment, gross (%)']:.0f}%", "tertiary enrolment, gross",
         f"East Asia & Pacific {c1['vs_region']['table']['EAS']['Tertiary enrolment, gross (%)']:.0f}%, World Bank"],
        [f"{c4['rca_sector']['2024']['SGP']['ICT & business services']:.1f}", "RCA in ICT and business services, 2024",
         f"{c4['rca_sector']['2004']['SGP']['ICT & business services']:.1f} in 2004"],
        [f"{c1['hdi']['value_2023']:.3f}", "Human Development Index, 2023", f"{ordinal(c1['hdi']['rank'])} of {c1['hdi']['n']}, UNDP"]],
     "note": "The research district. Fort shows that cheaper communication lets firms split production toward places with high "
             "human capital, so Singapore keeps the design and research stages while assembly moves to its neighbours."},
    {"id": "cbd", "section": "Who invests, and in what?", "name": "Central business district", "coord": [103.851, 1.282], "chapter": "ch06_fdi", "chapter_label": "Chapter 6",
     "tag": "Phantom FDI", "rows": [
        [f"${c6['inflows_gdp']['inflows_usd_rank_2024']['value'] / 1e9:.0f}bn", "FDI net inflows, 2024",
         f"{ordinal(c6['inflows_gdp']['inflows_usd_rank_2024']['rank'])} of {c6['inflows_gdp']['inflows_usd_rank_2024']['n']}, World Bank"],
        [f"{ind['Finance: holding companies']:.1f}%", "of the inward FDI stock is in holding companies, 2024", "SingStat"],
        [f"{c6['stocks']['pct_gdp']['Inward FDI stock']['2024']:.0f}%", "inward FDI stock, % of GDP, 2024", "SingStat"],
        [f"{c4['rca_sector']['2024']['SGP']['Finance & insurance']:.1f}", "RCA in finance and insurance, 2024",
         f"{c4['rca_sector']['2004']['SGP']['Finance & insurance']:.1f} in 2004"]],
     "note": "Banks, regional headquarters and holding companies sit here, so much of the investment recorded in Singapore "
             "is money passing through on its way to the rest of Asia."},
    {"id": "changi", "section": "What are its trade agreements for?", "name": "Changi Airport and Airport Logistics Park", "coord": [103.99, 1.355], "chapter": "ch07_policy",
     "chapter_label": "Chapter 7", "tag": "Rules of origin", "rows": [
        [f"{c7['TM.TAX.MRCH.SM.FN.ZS']['value']:.2f}%", "average MFN tariff, 2022",
         f"{ordinal(c7['TM.TAX.MRCH.SM.FN.ZS']['rank'])} lowest of {c7['TM.TAX.MRCH.SM.FN.ZS']['n']}, WITS"],
        [str(c7["fta"]["n"]), "free trade agreements in force", f"{c7['fta']['count_2004']} in 2004, Enterprise Singapore"],
        [f"{ntm_sg['imports_coverage']:.1f}%", "of imports touched by non-tariff measures", "UNCTAD TRAINS via WITS"],
        [str(c7["bits"]["n"]), "bilateral investment treaties", f"first in {c7['bits']['first'][:4]}, METI"]],
     "note": "An air cargo free trade zone inside a country that already charges almost no tariffs. Because of that, partners "
             "rely on rules of origin to stop goods slipping through, which makes regional content rules matter for Singapore."},
]
FDI_NAME = {"USA": "United States Of America", "JPN": "Japan", "HKG": "Hong Kong", "CHN": "Mainland China", "TWN": "Taiwan",
            "KOR": "Republic Of Korea"}
OUT_NAME = {"CHN": "Mainland China", "IND": "India", "IDN": "Indonesia", "HKG": "Hong Kong", "AUS": "Australia", "MYS": "Malaysia",
            "USA": "United States Of America"}
partner_pos = {  # map position; partners beyond the regional map sit at its edge, marked "off map"
    "MYS": ([101.69, 3.14], False), "IDN": ([106.85, -6.21], False), "THA": ([100.50, 13.75], False), "VNM": ([105.85, 21.03], False),
    "HKG": ([114.17, 22.32], False), "CHN": ([110.0, 25.6], True), "TWN": ([121.0, 24.2], False), "KOR": ([126.8, 25.6], True),
    "JPN": ([127.8, 19.0], True), "USA": ([127.8, 8.0], True), "AUS": ([123.0, -10.3], True), "IND": ([92.7, 19.5], True)}
pnotes = {
    "MYS": "The closest partner, across the Causeway, trades about what gravity predicts. Much of it is two way trade in "
           "electronics inside the same supply chains, and the Johor Singapore Special Economic Zone of 2025 aims to deepen it.",
    "CHN": "The largest export market and, with the United States, the largest source of foreign value in Singapore's exports. "
           "Trade runs well above what size and distance predict, with two agreements and shared supply chains behind it.",
    "HKG": "The other entrepôt buys far more than gravity predicts, most likely because goods bound for mainland China pass "
           "through it. Trade between two hubs shows how re-exports stretch the gravity model.",
    "USA": "Distant yet one of the largest markets and the largest direct investor. Its 2025 tariffs and chip export controls "
           "are the main outside risk for Singapore's two industrial bets (Chapters 7 and 9).",
    "IDN": "A large neighbour that buys about what gravity predicts, and one of the main destinations of Singapore's own "
           "investment abroad.",
    "TWN": "The largest source of imports, largely chips for testing, packaging and re-export. Taiwan is outside the gravity "
           "sample because the World Bank publishes no GDP for it.",
    "JPN": "An early agreement partner (2002), the third largest source of foreign value in Singapore's exports and a large "
           "direct investor.",
    "KOR": "A supplier of inputs to Singapore's exports that also buys far more than gravity predicts, under an agreement in "
           "force since 2006.",
    "IND": "Linked by a 2005 agreement, India supplies services and goods to Singapore's exports and is the second destination "
           "of its investment abroad.",
    "THA": "An ASEAN partner in the same electronics and chemicals chains, buying above the gravity prediction.",
    "VNM": "The newcomer competing for the same factories also buys well above the gravity prediction, a sign of supply "
           "chain links across ASEAN.",
    "AUS": "A distant partner with an agreement since 2003 that buys several times the gravity prediction and hosts Singapore "
           "investment.",
}
sk = json.loads((OUT / "sankey.json").read_text())["partners"]
partners = []
for iso, (pos, edge) in partner_pos.items():
    p = sk.get(iso, {})
    rows = []
    if p:
        rows.append([f"{p['share_x']['2024']:.1f}%", "of Singapore's exports, 2024", "UN Comtrade"])
        rows.append([f"{p['share_m']['2024']:.1f}%", "of Singapore's imports, 2024", "UN Comtrade"])
    ratio = c3["gravity_ratio"].get(iso)
    if ratio:
        rows.append([f"{ratio:.1f}×", "actual exports over the gravity prediction", "team regression, Chapter 3"])
    if iso in c5["fva_origin_top10"]:
        rows.append([f"{c5['fva_origin_top10'][iso]:.1f}%", f"of foreign value in Singapore's exports, {c5['year']}", "OECD TiVA"])
    if iso in FDI_NAME and FDI_NAME[iso] in c6["sources_2024"]:
        rows.append([f"{c6['sources_2024'][FDI_NAME[iso]]:.1f}%", "of inward FDI stock, 2024", "SingStat"])
    if iso in OUT_NAME and OUT_NAME[iso] in c6["outward_2024"]["top"]:
        rows.append([f"{c6['outward_2024']['top'][OUT_NAME[iso]]:.1f}%", "of Singapore's FDI abroad, 2024", "SingStat"])
    partners.append({"id": iso, "name": p.get("name") or NAMES.get(iso, iso), "coord": pos, "edge": edge,
                     "km": p.get("km"), "fta": p.get("fta"), "rows": rows[:5], "note": pnotes[iso],
                     "share_x": p.get("share_x", {}).get("2024"), "share_m": p.get("share_m", {}).get("2024"), "chapter": "ch03_trade", "chapter_label": "Chapter 3",
                     "section": "Does its trade follow gravity?", "tag": "Gravity model"})
# the country itself: capital and politics, land, people and the link to Malaysia (Chapter 1's profile on the map)
kf = json.loads((OUT / "kpis.json").read_text())["facts"]
f1 = c1["facts"]
wr = c2["wgi"]["ranks"]
reg = lambda r: f"{ordinal(r['region_rank'])} of {r['region_n']} in East Asia & Pacific"
mys = sk.get("MYS", {})
country = [
    {"id": "capital", "section": "How good are its institutions?", "name": "Parliament House, Civic District", "coord": [103.8505, 1.2895],
     "chapter": "ch02_macro", "chapter_label": "Chapter 2", "tag": "Political system", "rows": [
        [ordinal(wr["GE"]["rank"]), f"of {wr['GE']['n']} on government effectiveness, {c2['wgi']['year']}", f"{reg(wr['GE'])}, World Bank WGI"],
        [ordinal(wr["RQ"]["rank"]), f"of {wr['RQ']['n']} on regulatory quality", f"{reg(wr['RQ'])}, WGI"],
        [ordinal(wr["VA"]["rank"]), f"of {wr['VA']['n']} on voice and accountability", f"{reg(wr['VA'])}, WGI"],
        ["87 of 97", "seats won by the People's Action Party, May 2025", "about 65.6% of the vote, AP via PBS"]],
     "note": "A city state, so the capital is the country itself. The prime minister and cabinet answer to an elected parliament, "
             "the People's Action Party has governed since 1959 and Lawrence Wong has been prime minister since May 2024. "
             "Investors read this continuity as predictable policy, which Chapter 2 tests with the governance indicators."},
    {"id": "land", "section": "What kind of country is it?", "name": "Tuas and the reclaimed coast", "coord": [103.64, 1.30],
     "chapter": "ch01_profile", "chapter_label": "Chapter 1", "tag": "Geography", "rows": [
        [f"{kf['area_km2']} km²", "of land, June 2026", "SingStat, Population Trends 2026"],
        ["+28%", "since 1965, when it was 581.5 km²", "mostly reclamation, SingStat"],
        [f"{ordinal(f1['AG.LND.TOTL.K2']['rank'])} of {f1['AG.LND.TOTL.K2']['n']}", "by land area",
         f"World Bank, {f1['AG.LND.TOTL.K2']['value']:.0f} km² in {f1['AG.LND.TOTL.K2']['year']}, {reg(f1['AG.LND.TOTL.K2'])}"],
        [f"{f1['SP.URB.TOTL.IN.ZS']['value']:.0f}%", "of people live in urban areas",
         f"{ordinal(f1['SP.URB.TOTL.IN.ZS']['rank'])} of {f1['SP.URB.TOTL.IN.ZS']['n']}, World Bank"]],
     "note": "An island on the Strait of Malacca that adds land by filling in the sea. The new coast at Tuas, Jurong Island and "
             "Marina Bay holds ports, refineries and offices, yet land stays the scarcest input, which is why land intensive "
             "production moves to the neighbours (Chapter 4)."},
    {"id": "people", "section": "What kind of country is it?", "name": "The heartland housing towns", "coord": [103.848, 1.334],
     "chapter": "ch01_profile", "chapter_label": "Chapter 1", "tag": "Population", "rows": [
        [f"{kf['population_m']}m", "people, June 2026",
         f"{kf['residents_m']}m residents and {kf['nonresidents_m']}m foreign workers, students and dependants, SingStat"],
        [f"{f1['EN.POP.DNST']['value']:,.0f}", f"people per km², {f1['EN.POP.DNST']['year']}",
         f"{ordinal(f1['EN.POP.DNST']['rank'])} of {f1['EN.POP.DNST']['n']}, {reg(f1['EN.POP.DNST'])}, World Bank"],
        [f"{f1['SP.DYN.LE00.IN']['value']:.1f}", f"years of life expectancy, {f1['SP.DYN.LE00.IN']['year']}",
         f"{ordinal(f1['SP.DYN.LE00.IN']['rank'])} of {f1['SP.DYN.LE00.IN']['n']}, {reg(f1['SP.DYN.LE00.IN'])}"],
        [f"{f1['SP.POP.65UP.TO.ZS']['value']:.1f}%", f"aged 65 or older, {f1['SP.POP.65UP.TO.ZS']['year']}",
         f"{ordinal(f1['SP.POP.65UP.TO.ZS']['rank'])} of {f1['SP.POP.65UP.TO.ZS']['n']}, World Bank"]],
     "note": "Four official languages, Malay, English, Mandarin and Tamil, with English for business, connect Singapore to "
             "China, India and the Malay world. A third of the people are foreign workers, students and dependants, so the "
             "labour force can grow with demand."},
    {"id": "link", "section": "Does Singapore invest abroad?", "name": "Woodlands Causeway to Johor", "coord": [103.769, 1.452],
     "chapter": "ch06_fdi", "chapter_label": "Chapter 6", "tag": "Neighbours", "rows": [
        [f"{mys['share_x']['2024']:.1f}%", "of Singapore's exports go to Malaysia, 2024", "UN Comtrade"],
        [f"{mys['share_m']['2024']:.1f}%", "of its imports come from Malaysia, 2024", "UN Comtrade"],
        [f"{c3['gravity_ratio']['MYS']:.2f}×", "Malaysia's purchases over the gravity prediction", "team regression, Chapter 3"],
        [f"{mys['km']:,.0f} km", "from Singapore to Kuala Lumpur", "World Bank capital coordinates"]],
     "note": "The road and rail link across the Johor Strait to Malaysia, the federation Singapore left in 1965. Firms "
             "increasingly pair a Singapore headquarters with land and workers in Johor, the division of labour the Johor "
             "Singapore Special Economic Zone of January 2025 is designed to support."},
]
dump("atlas", {"country": country, "sites": sites, "partners": partners,
               "source": "Team calculations from UN Comtrade, CEPII BACI, OECD TiVA, SingStat, World Bank WDI and LPI, PWT, UNDP, "
                         "WITS and METI; numbers as in the chapters."})

# ---------------------------------------------------------------- Ch. 1 fact grid (dictionary-style entries)
facts = json.loads((OUT / "kpis.json").read_text())["facts"]
entries = [("Capital", f"{facts['capital']} (city state)"), ("Official languages", facts["languages"]),
           ("Land area", f"{facts['area_km2']} km² (June 2026), +28% since 1965"), ("Population", f"{facts['population_m']} million (June 2026)"),
           ("Political system", f"{facts['system']}, PAP in government since 1959"), ("Prime minister", "Lawrence Wong, since May 2024"),
           ("Currency", "Singapore dollar (S$)"), ("Memberships", "ASEAN (1967), APEC (1989), WTO (1995), CPTPP, RCEP")]
(ROOT / "data" / "derived" / "ch01_facts.md").write_text(
    '<section class="facts">' + "".join(f"<div><span>{k}</span><b>{v}</b></div>" for k, v in entries)
    + '<p class="facts-src">SingStat Population Trends 2026 and land area series, Constitution of Singapore, Prime Minister\'s Office, WTO.</p></section>\n')
print("wrote data/derived/ch01_facts.md")
