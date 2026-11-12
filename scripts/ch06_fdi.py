"""Ch. 6 Foreign direct investment.

Figures: FDI inflows % of GDP vs peers (WDI); inward and outward FDI stock % of GDP (SingStat); greenfield vs M&A
(UNCTAD WIR 2026); inward stock by immediate source economy and by industry; outward stock by destination (SingStat).
Tables: greenfield/M&A comparison -> data/derived/ch06_entry_mode_table.md
Run: python scripts/ch06_fdi.py
"""
import pandas as pd

from chart_style import (DERIVED, FOCUS, GROUP, RAW, bar_rank, line_chart, ordinal, retrieved, save_numbers,
                         wdi_rank, wide)

SS = RAW / "singstat"
MAN = RAW / "manual"
N = {}


def singstat(table):
    d = pd.read_csv(SS / f"{table}.csv", dtype={"series_no": str, "period": str})
    d["value"] = pd.to_numeric(d.value, errors="coerce")
    return d


def ss_note(table):
    return f"Singapore Department of Statistics, table {table}, downloaded {retrieved(path=SS / f'{table}.csv')}"


# ---- 6.1 FDI net inflows, % of GDP (World Bank, BoP basis)
fi = wide("BX.KLT.DINV.WD.GD.ZS", GROUP + ["WLD"])
avg = fi.loc[2004:2024].mean()
r_fi = wdi_rank("BX.KLT.DINV.WD.GD.ZS", 2024)
line_chart(
    fi,
    title=f"FDI inflows averaged {avg[FOCUS]:.0f}% of Singapore's GDP a year, versus "
          f"{avg[['MYS', 'VNM']].mean():.0f}% for Malaysia and Vietnam",
    subtitle="Foreign direct investment, net inflows, % of GDP, 2004 to 2024. Dashed: world",
    ylabel="Net FDI inflows, % of GDP",
    source=f"Source: World Bank, World Development Indicators (BX.KLT.DINV.WD.GD.ZS), retrieved "
           f"{retrieved('BX.KLT.DINV.WD.GD.ZS')}. Hong Kong SAR and Singapore are financial hubs: part of their FDI "
           "passes through holding companies to other countries.",
    out="ch06_inflows_gdp.png", fmt=lambda v: f"{v:.0f}%", ymin=None, zero_line=True, dashed=("WLD",),
    labels={"WLD": "World"},
)
N["inflows_gdp"] = {"avg": avg.round(1).to_dict(), "2024": fi.loc[2024].round(1).to_dict(), "rank_2024": r_fi,
                    "outflows_2024": wdi_rank("BM.KLT.DINV.WD.GD.ZS", 2024),
                    "inflows_usd_rank_2024": wdi_rank("BX.KLT.DINV.CD.WD", 2024)}

# ---- 6.2 Inward and outward stock, % of GDP (SingStat, S$)
gdp = singstat("M015731").query("series_no == '1'")
gdp = gdp.assign(year=gdp.period.astype(int)).set_index("year").value
inw = singstat("M083791").query("series_no == '2'")
inw = inw.assign(year=inw.period.astype(int)).set_index("year").value
out = singstat("M082221").query("series_no == '1'")
out = out.assign(year=out.period.astype(int)).set_index("year").value
stock = pd.DataFrame({"Inward FDI stock": inw / gdp * 100, "Outward FDI stock": out / gdp * 100}).loc[2004:2024]
line_chart(
    stock,
    title=f"Foreign firms own assets worth {stock.loc[2024, 'Inward FDI stock'] / 100:.1f} times Singapore's GDP",
    subtitle="Direct investment stock at year-end, % of GDP (both in Singapore dollars), 2004 to 2024",
    ylabel="Stock, % of GDP",
    source=f"Source: {ss_note('M083791')} (inward), M082221 (outward), M015731 (GDP at current prices). "
           "Positions by immediate investor, BPM6 basis.",
    out="ch06_stocks_gdp.png", fmt=lambda v: f"{v:.0f}%", labels={c: c for c in stock.columns},
)
N["stocks"] = {"inward_sgd_bn": {y: float(inw[y] / 1e3) for y in (2004, 2014, 2024)},
               "outward_sgd_bn": {y: float(out[y] / 1e3) for y in (2004, 2014, 2024)},
               "pct_gdp": stock.loc[[2004, 2014, 2024]].round(0).to_dict()}


# ---- 6.3 Greenfield vs M&A (UNCTAD WIR 2026 annex)
def unctad(tab):
    x = pd.read_excel(MAN / f"unctad_wir26_tab{tab}.xlsx", header=None)
    hdr = x.index[x[0].astype(str).str.strip() == "Region/economy"][0]
    years = [int(float(v)) for v in x.loc[hdr, 1:].dropna()]
    body = x.loc[hdr + 1:, :len(years)]
    body.columns = ["economy"] + years
    body["economy"] = body.economy.astype(str).str.strip()
    return body.set_index("economy").apply(pd.to_numeric, errors="coerce")


UNAMES = {"SGP": "Singapore", "MYS": "Malaysia", "HKG": "Hong Kong, China", "VNM": "Viet Nam"}
gf_v, ma_v, gf_n, ma_n, inflow = unctad("14"), unctad("05"), unctad("17"), unctad("07"), unctad("01")
mode = pd.DataFrame({
    "Greenfield": gf_v.loc["Singapore", 2004:2025],
    "Net M&A": ma_v.loc["Singapore", 2004:2025],
}).astype(float)
line_chart(
    mode,
    title=f"Greenfield projects bring more new FDI to Singapore than acquisitions do",
    subtitle="Value of announced greenfield FDI projects and net cross-border M&A sales, Singapore, US$ billions, "
             "2004 to 2025",
    ylabel="US$ billions",
    source=f"Source: UNCTAD, World Investment Report 2026, annex tables 5 and 14, downloaded "
           f"{retrieved(path=MAN / 'unctad_wir26_tab14.xlsx')}. Greenfield values are announced capital expenditure; "
           "net M&A sales = acquisitions of local firms by foreigners minus divestments.",
    out="ch06_greenfield_ma.png", fmt=lambda v: f"${v:,.1f}bn", scale=1e3, ymin=None, zero_line=True,
    labels={c: c for c in mode.columns},
)
lines = ["| Economy | FDI inflows, 2025 (US$ bn) | Greenfield projects, 2025 (number) | Greenfield value, 2025 (US$ bn) | "
         "Net M&A sales, 2025 (number) | Net M&A value, 2025 (US$ bn) | Greenfield value 2016 to 2025 / M&A value 2016 to 2025 |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
entry = {}
for iso in GROUP:
    nm = UNAMES[iso]
    ratio = gf_v.loc[nm, 2016:2025].sum() / ma_v.loc[nm, 2016:2025].sum()
    entry[iso] = {"inflow": float(inflow.loc[nm, 2025]), "gf_n": float(gf_n.loc[nm, 2025]),
                  "gf_v": float(gf_v.loc[nm, 2025]), "ma_n": float(ma_n.loc[nm, 2025]),
                  "ma_v": float(ma_v.loc[nm, 2025]), "ratio_10y": float(ratio)}
    e = entry[iso]
    lines.append(f"| {nm.replace('Hong Kong, China', 'Hong Kong SAR').replace('Viet Nam', 'Vietnam')} | "
                 f"{e['inflow'] / 1e3:,.1f} | {e['gf_n']:,.0f} | {e['gf_v'] / 1e3:,.1f} | {e['ma_n']:,.0f} | "
                 f"{e['ma_v'] / 1e3:,.1f} | {ratio:,.1f}× |")
world_rank = inflow[2025].drop(["World", "Developed economies", "Developing economies"], errors="ignore")
lines.append("\n*Source: UNCTAD, World Investment Report 2026, annex tables 1, 5, 7, 14 and 17. Greenfield = announced "
             "new projects (capital expenditure); M&A = net sales of domestic firms to foreign buyers. The two are not "
             "additive and do not sum to FDI flows.*\n")
(DERIVED / "ch06_entry_mode_table.md").write_text("\n".join(lines))
print("wrote data/derived/ch06_entry_mode_table.md")
N["entry_mode"] = entry
N["unctad_inflows"] = {y: float(inflow.loc["Singapore", y]) for y in (2004, 2014, 2024, 2025)}

# ---- 6.4 Inward stock by immediate source economy, 2024
src = singstat("M083801").query("period == '2024'")
total = float(src.query("series_no == '1'").value.iloc[0])
countries = src[src.series_no.str.count(r"\.") == 2].set_index("series").value
share = (countries / total * 100).sort_values(ascending=False)
pretty = {"United States Of America": "United States", "Republic Of Korea": "Korea"}
top = share.head(12).rename(index=lambda s: pretty.get(s, s))
offshore = {"Cayman Islands", "British Virgin Islands", "Bermuda", "Luxembourg", "Netherlands", "Bahamas",
            "Mauritius", "Ireland"}
caribbean = share[share.index.isin(["Cayman Islands", "British Virgin Islands", "Bermuda", "Bahamas"])].sum()
bar_rank(
    top,
    title=f"The US is the largest investor, but {caribbean:.0f}% of the stock comes via Caribbean financial centres",
    subtitle="Inward FDI stock by immediate source economy, % of total, end-2024 (light blue: holding-company hubs)",
    xlabel="% of inward FDI stock", fmt=lambda v: f"{v:.1f}%", highlight=(), light=tuple(offshore),
    source=f"Source: {ss_note('M083801')}; total S${total / 1e6:,.2f} trillion. Recorded by immediate investor: "
           "a US firm investing through a Cayman holding company is recorded as Cayman.",
    out="ch06_sources.png",
)
N["sources_2024"] = share.head(15).round(1).to_dict()
N["caribbean_share"] = float(caribbean)
N["inward_total_sgd_bn_2024"] = total / 1e3

# ---- 6.5 Inward stock by industry, 2024 (holding companies shown separately)
ind = singstat("M084831").query("period == '2024'").set_index("series_no")
tot_i = float(ind.loc["1", "value"])
parts = {
    "Finance: holding companies": ind.loc["1.7.1.2", "value"],
    "Finance: banks, insurance, other": ind.loc["1.7", "value"] - ind.loc["1.7.1.2", "value"],
    "Wholesale & retail trade": ind.loc["1.3", "value"],
    "Manufacturing": ind.loc["1.1", "value"],
    "Professional & admin services": ind.loc["1.9", "value"],
    "Transportation & storage": ind.loc["1.5", "value"],
    "Information & communications": ind.loc["1.6", "value"],
    "Real estate": ind.loc["1.8", "value"],
}
ind_sh = pd.Series({k: v / tot_i * 100 for k, v in parts.items()})
bar_rank(
    ind_sh,
    title=f"Holding companies hold {ind_sh['Finance: holding companies']:.0f}% of foreign investment in Singapore, "
          f"manufacturing only {ind_sh['Manufacturing']:.0f}%",
    subtitle="Inward FDI stock by industry in Singapore, % of total, end-2024",
    xlabel="% of inward FDI stock", fmt=lambda v: f"{v:.1f}%", highlight=(), light=("Manufacturing",),
    source=f"Source: {ss_note('M084831')}. Holding companies own shares in other firms, often in other countries, so "
           "this part of FDI is largely pass-through.",
    out="ch06_industries.png",
)
man = {k: float(ind.loc[k, "value"] / tot_i * 100) for k in ["1.1.11", "1.1.11.1", "1.1.5", "1.1.4", "1.1.3"]}
N["industries_2024"] = ind_sh.round(1).to_dict()
N["manufacturing_detail_2024"] = {"electronics": man["1.1.11"], "semiconductors": man["1.1.11.1"],
                                  "pharma": man["1.1.5"], "chemicals": man["1.1.4"], "refining": man["1.1.3"]}

# ---- 6.6 Outward stock by destination, 2024
dst = singstat("M084431").query("period == '2024'")
total_o = float(dst.query("series_no == '1'").value.iloc[0])
dcount = dst[dst.series_no.str.count(r"\.") == 2].set_index("series").value
dshare = (dcount / total_o * 100).sort_values(ascending=False)
asean = dst[dst.series.str.strip() == "ASEAN"].value
asia = dst[dst.series.str.strip() == "Asia"].value
bar_rank(
    dshare.head(12).rename(index=lambda s: pretty.get(s, s)),
    title=f"Singapore invests mostly in Asia ({float(asia.iloc[0]) / total_o * 100:.0f}% of its outward stock), "
          "led by China",
    subtitle="Singapore's direct investment abroad by destination, % of total, end-2024 (light blue: holding hubs)",
    xlabel="% of outward FDI stock", fmt=lambda v: f"{v:.1f}%", highlight=(), light=tuple(offshore),
    source=f"Source: {ss_note('M084431')}; total S${total_o / 1e6:,.2f} trillion "
           f"({total_o / float(gdp[2024]) * 100:.0f}% of GDP). Recorded by immediate destination.",
    out="ch06_outward_destinations.png",
)
# ---- 6.8 Is investment abroad a significant source of income? Primary income flows, % of GDP
inc = pd.DataFrame({
    "Income received from abroad": wide("BX.GSR.FCTY.CD", [FOCUS])[FOCUS] / wide("NY.GDP.MKTP.CD", [FOCUS])[FOCUS] * 100,
    "Income paid to foreign investors": wide("BM.GSR.FCTY.CD", [FOCUS])[FOCUS] / wide("NY.GDP.MKTP.CD", [FOCUS])[FOCUS] * 100,
}).dropna()
gni_gdp = (wide("NY.GNP.MKTP.CD", [FOCUS])[FOCUS] / wide("NY.GDP.MKTP.CD", [FOCUS])[FOCUS] * 100).dropna()
line_chart(
    inc,
    title=f"Income from investment abroad reached {inc.iloc[-1, 0]:.0f}% of GDP, but foreign investors take out more",
    subtitle=f"Primary income receipts and payments (mostly investment income), % of GDP, 2004 to {inc.index.max()}",
    ylabel="% of GDP", fmt=lambda v: f"{v:.0f}%", labels={c: c for c in inc.columns},
    source=f"Source: World Bank WDI (BX.GSR.FCTY.CD, BM.GSR.FCTY.CD, NY.GDP.MKTP.CD), balance of payments basis, "
           f"retrieved {retrieved('BX.GSR.FCTY.CD')}. Primary income also includes a small amount of compensation of "
           "employees.",
    out="ch06_income.png",
)
N["income"] = {"receipts_pct_gdp": inc.iloc[:, 0].round(1).loc[[2004, 2014, inc.index.max()]].to_dict(),
               "payments_pct_gdp": inc.iloc[:, 1].round(1).loc[[2004, 2014, inc.index.max()]].to_dict(),
               "gni_gdp": gni_gdp.round(1).loc[[2004, 2014, gni_gdp.index.max()]].to_dict()}

# ---- 6.7 Outward stock by industry abroad, 2024
oi = singstat("M084441").query("period == '2024'")
oi_tot = float(oi.query("series_no == '1'").value.iloc[0])
oi_sh = (oi[oi.series_no != "1"].set_index("series").value / oi_tot * 100).sort_values(ascending=False)
oi_sh = oi_sh[oi_sh > 0.5]
bar_rank(
    oi_sh,
    title=f"Half of Singapore's investment abroad is in finance; manufacturing takes "
          f"{oi_sh.filter(like='Manufacturing').iloc[0]:.0f}%".replace(";", ","),
    subtitle="Singapore's direct investment abroad by industry of the foreign affiliate, % of total, end-2024",
    xlabel="% of outward FDI stock", fmt=lambda v: f"{v:.1f}%", highlight=(), light=("Manufacturing",),
    source=f"Source: {ss_note('M084441')}; total S${oi_tot / 1e6:,.2f} trillion.",
    out="ch06_outward_industries.png",
)
N["outward_industries_2024"] = oi_sh.round(1).to_dict()
N["outward_2024"] = {"total_sgd_bn": total_o / 1e3, "asia_share": float(asia.iloc[0]) / total_o * 100,
                     "asean_share": float(asean.iloc[0]) / total_o * 100 if len(asean) else None,
                     "top": dshare.head(12).round(1).to_dict()}
save_numbers("ch06", N)
print("\n".join(lines))
print(N["inflows_gdp"]["avg"], N["inflows_gdp"]["rank_2024"])
print(stock.loc[[2004, 2014, 2024]].round(0))
print(share.head(12).round(1))
print(ind_sh.round(1))
print(N["outward_2024"])
