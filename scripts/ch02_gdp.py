"""Ch. 2 figure: GDP in current US$, Singapore vs comparison economies, 2004-2024.

Reads data/raw/wdi/NY.GDP.MKTP.CD.csv (from the Fetch data workflow) and writes figures/ch02_gdp_current_usd.png.
Run: python scripts/ch02_gdp.py
"""
from chart_style import FOCUS, PEERS, line_chart, retrieved, wide

CODE = "NY.GDP.MKTP.CD"
FOLD = {2: "doubled", 3: "tripled", 4: "grew about fourfold", 5: "grew about fivefold", 6: "grew about sixfold"}

gdp = wide(CODE, [FOCUS] + PEERS).loc[2004:2024]
first, last = gdp.index.min(), gdp.index.max()
sgp0, sgp1 = gdp.loc[first, FOCUS] / 1e9, gdp.loc[last, FOCUS] / 1e9
ratio = sgp1 / sgp0
growth = FOLD.get(round(ratio), f"grew {ratio:.1f}x")

print(f"SGP {first}: ${sgp0:,.1f}bn   SGP {last}: ${sgp1:,.1f}bn   ratio {ratio:.2f}")
for iso in PEERS:
    print(f"{iso} {last}: ${gdp.loc[last, iso] / 1e9:,.1f}bn")

line_chart(
    gdp,
    title=f"Singapore's economy {growth} in {last - first} years, to ${sgp1:,.0f}bn in {last}",
    subtitle=f"GDP in current US dollars, Singapore vs comparison economies, {first}–{last}",
    ylabel="GDP, current US$ billions",
    source=f"Source: World Bank, World Development Indicators ({CODE}), retrieved {retrieved(CODE)}. "
           "Current prices, not adjusted for inflation.",
    out="ch02_gdp_current_usd.png",
    fmt=lambda v: f"${v:,.0f}bn",
    scale=1e9,
)
