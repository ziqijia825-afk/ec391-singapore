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
dump("kpis", {"kpis": kpis, "facts": {"capital": "Singapore", "area_km2": 735.6, "population_m": 6.21,
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
