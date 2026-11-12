"""Shared helpers for every chart: load data, compute ranks, and draw in the project's house style.

Style (see CLAUDE.md): Singapore in blue, peers in grays; takeaway title with its number; subtitle with
measure + years; direct labels at line ends; light horizontal grid only; single y-axis; source line at the bottom
with indicator code and retrieval date. One PNG per figure, figures/chNN_topic.png.
"""
import datetime as dt
import json
import subprocess
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
WDI = RAW / "wdi"
DERIVED = ROOT / "data" / "derived"
FIGURES = ROOT / "figures"

FOCUS = "SGP"
PEERS = ["MYS", "HKG", "VNM"]
GROUP = [FOCUS] + PEERS
REGION = "EAS"  # World Bank "East Asia & Pacific" aggregate
NAMES = {"SGP": "Singapore", "MYS": "Malaysia", "HKG": "Hong Kong SAR", "VNM": "Vietnam",
         "EAS": "East Asia & Pacific", "WLD": "World"}
FIRST, LAST = 2004, 2024
SHORT = {"CHN": "China", "IDN": "Indonesia", "THA": "Thailand", "KOR": "Korea", "JPN": "Japan", "IND": "India",
         "AUS": "Australia", "USA": "United States", "DEU": "Germany", "GBR": "UK", "BRA": "Brazil", "PHL": "Philippines",
         "TWN": "Taiwan", "MHL": "Marshall Is.", "LBR": "Liberia", "PAN": "Panama", "NLD": "Netherlands", "FRA": "France"}

# ---- colour: one fixed colour per economy across every chart, a fixed categorical order for everything else.
# Checked with the dataviz palette validator on the cream page surface (#fffdf6): all four economies pass the
# lightness, chroma and normal-vision checks pairwise; red/green sits in the CVD 6 to 8 band, so every chart
# also carries direct labels or a legend plus a data table.
ECON = {"SGP": "#e34948", "MYS": "#2a78d6", "HKG": "#eda100", "VNM": "#008300",
        "EAS": "#7d7468", "WLD": "#a89f90"}  # Singapore flag red; aggregates neutral and dashed
for _iso, _name in list(NAMES.items()):
    ECON[_name] = ECON[_iso]
ECON.update({"East Asia & Pacific average": ECON["EAS"], "East Asia and Pacific": ECON["EAS"], "Region": ECON["EAS"]})
CATEGORICAL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]  # never cycled past 7
SECTOR = {  # goods in distinct hues, services as one warm family (composite encoding: hue family = goods or services)
    "Electronics & instruments": "#2a78d6", "Machinery & computers": "#6250d6", "Machinery incl. computers": "#6250d6",
    "Refined petroleum": "#eda100", "Chemicals & pharma": "#e87ba4", "Chemicals & plastics": "#e87ba4",
    "Pharmaceuticals": "#c2408a", "Gold & metals": "#1baf7a", "Food & agriculture": "#008300",
    "Transport equipment": "#5aa0e8", "Other goods": "#cfc6b4", "Other": "#cfc6b4", "All other": "#cfc6b4",
    "Transport services": "#d95926", "Transport & logistics": "#d95926", "Business & ICT services": "#f08a55",
    "ICT & business services": "#f08a55", "Financial services": "#a8401a", "Finance & insurance": "#a8401a",
    "Travel services": "#f7bf9a", "Travel & tourism": "#f7bf9a",
}
ORDINAL_BLUE = ["#a9c8ee", "#5598e7", "#256abf", "#104281"]  # light to dark, for years
OTHER = "#cfc6b4"
BLUE = ECON["MYS"]
BLUE_LIGHT = "#a9c8ee"
GRAYS = ["#5f5e5a", "#8a8a85", "#b3b2ab"]
GRAY_BAR = "#d9d0bd"


def color_for(key, i=0, n=1, keys=None):
    """Colour of a series: the economy's own colour, a sector colour, a year on the ordinal ramp, or the j-th slot."""
    k = str(key)
    if k in ECON:
        return ECON[k]
    if k in SECTOR:
        return SECTOR[k]
    if k.isdigit() and len(k) == 4 and keys:  # years: older lighter, newer darker, whatever the column order
        years = sorted(str(x) for x in keys)
        ramp = ORDINAL_BLUE[-len(years):] if len(years) <= len(ORDINAL_BLUE) else ORDINAL_BLUE
        return ramp[min(years.index(k), len(ramp) - 1)]
    if k.lower().startswith(("other", "all other", "rest of")):
        return OTHER
    return CATEGORICAL[i % len(CATEGORICAL)]


def _is_dark(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.45


def is_aggregate(key):
    return str(key) in ("EAS", "WLD", "East Asia & Pacific", "World", "East Asia & Pacific average", "Region")
INK = "#1f1f1d"
MUTED = "#5f5e5a"
GRID = "#e4e3dd"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.edgecolor": "#c9c8c1",
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "savefig.dpi": 200,
    "text.parse_math": False,  # "$" in titles is a currency sign, not maths
})


# ---------------------------------------------------------------- data

def load(code):
    """One World Bank indicator as a long table (iso3, country, year, value), empty values dropped."""
    df = pd.read_csv(WDI / f"{code}.csv")
    return df.dropna(subset=["value"]).astype({"year": int})


def wide(code, economies, first=FIRST, last=LAST):
    """year x economy table for the chosen economies (columns in the given order)."""
    df = load(code)
    df = df[df.iso3.isin(economies) & df.year.between(first, last)]
    return df.pivot(index="year", columns="iso3", values="value").reindex(columns=economies)


def countries():
    """Country metadata; is_aggregate rows are regions/income groups, not economies."""
    df = pd.read_csv(WDI / "countries.csv", keep_default_na=False)
    df["is_aggregate"] = df.is_aggregate.astype(str) == "True"
    return df


def economies():
    """Set of ISO3 codes that are economies (not aggregates), and the subset in East Asia & Pacific."""
    c = countries()
    econ = c[~c.is_aggregate]
    return set(econ.iso3), set(econ[econ.region_id == REGION].iso3)


def rank_table(values, region=None, higher_is_better=True):
    """values: Series iso3 -> value (economies only). Returns DataFrame with value, global rank, regional rank.

    Ties share the best rank (method="min"). Region ranks are among economies of `region` (a set of iso3).
    """
    v = values.dropna()
    out = pd.DataFrame({"value": v})
    out["rank"] = v.rank(ascending=not higher_is_better, method="min").astype(int)
    out["n"] = len(v)
    if region is not None:
        r = v[v.index.isin(region)]
        out["region_rank"] = r.rank(ascending=not higher_is_better, method="min").reindex(out.index)
        out["region_n"] = len(r)
    return out


def wdi_rank(code, year, higher_is_better=True, iso=FOCUS):
    """Global and East Asia & Pacific rank of `iso` for a WDI indicator in `year` (economies with data)."""
    econ, eas = economies()
    df = load(code)
    s = df[(df.year == year) & df.iso3.isin(econ)].set_index("iso3").value
    t = rank_table(s, eas, higher_is_better)
    if iso not in t.index:
        return None
    r = t.loc[iso]
    return {"value": float(r.value), "rank": int(r["rank"]), "n": int(r.n),
            "region_rank": int(r.region_rank), "region_n": int(r.region_n), "year": year}


def latest_year(code, iso=FOCUS, last=LAST):
    df = load(code)
    years = df[(df.iso3 == iso) & (df.year <= last)].year
    return int(years.max()) if len(years) else None


def retrieved(code=None, path=None):
    """Date a raw file was committed (= downloaded); today if not committed yet."""
    path = path or (WDI / f"{code}.csv")
    out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", str(path)],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    stamp = dt.datetime.fromisoformat(out) if out else dt.datetime.now(dt.timezone.utc)
    day = stamp.astimezone(dt.timezone.utc).date()  # UTC, so local and GitHub-workflow commits agree
    return f"{day:%b} {day.day}, {day.year}"


def save_numbers(name, numbers):
    """Key numbers used in the text, so the Markdown can be checked against the data."""
    DERIVED.mkdir(parents=True, exist_ok=True)
    path = DERIVED / f"{name}.json"
    path.write_text(json.dumps(numbers, indent=2, default=float) + "\n")
    print(f"wrote data/derived/{name}.json")


def ordinal(n):
    n = int(n)
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# ---------------------------------------------------------------- layout

def _figure(width=9.0, height=5.4, plot_box=(0.09, 0.75, 0.80, 0.16)):
    """Figure with room for title/subtitle on top and the source line at the bottom (fractions of the figure)."""
    fig, ax = plt.subplots(figsize=(width, height))
    left, right, top, bottom = plot_box
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)
    return fig, ax


def _style_axis(ax, grid="y"):
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=3)


def _fit_text(fig, x, y, text, size, min_size, **kw):
    """Place text, shrinking the font until it fits inside the figure width."""
    renderer = fig.canvas.get_renderer()
    t = fig.text(x, y, text, fontsize=size, **kw)
    width = fig.get_size_inches()[0] * fig.dpi
    while t.get_window_extent(renderer).x1 > width * 0.985 and size > min_size:
        size -= 0.5
        t.set_fontsize(size)
    return t


def _finish(fig, title, subtitle, source, out):
    w, h = fig.get_size_inches()
    x = 0.55 / w
    _fit_text(fig, x, 1 - 0.36 / h, title, 14, 11, fontweight="bold", color=INK, va="baseline")
    _fit_text(fig, x, 1 - 0.66 / h, subtitle, 11, 9, color=MUTED, va="baseline")
    lines = textwrap.wrap(source, width=int(w * 13.6))
    if len(lines) > 2:  # make room for a longer source note
        for ax in fig.axes:
            if ax.name != "polar":
                pos = ax.get_position()
                extra = (len(lines) - 2) * 0.17 / h
                ax.set_position([pos.x0, pos.y0 + extra, pos.width, pos.height - extra])
    fig.text(x, 0.12 / h, "\n".join(lines), fontsize=8.5, color=MUTED, va="bottom", linespacing=1.35)
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / out)
    plt.close(fig)
    print(f"wrote figures/{out}")


SPECS = ROOT / "site" / "data" / "figs"


def _clean(v):
    """JSON-safe number: None for NaN, rounded to keep files small."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (int, np.integer)):
        return int(v)
    return float(f"{float(v):.6g}")


def sanitize(o):
    """Recursively make an object strict-JSON safe: NaN/inf -> None, numpy scalars -> Python numbers."""
    if isinstance(o, dict):
        return {str(k): sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if not np.isfinite(o) else float(f"{float(o):.6g}")
    return o


def _spec(out, kind, title, subtitle, source, **data):
    """Write the data behind a figure as JSON so the interactive site draws exactly the same numbers."""
    SPECS.mkdir(parents=True, exist_ok=True)
    spec = {"id": Path(out).stem, "kind": kind, "title": title, "subtitle": subtitle, "source": source,
            "png": f"figures/{out}", **data}
    (SPECS / f"{Path(out).stem}.json").write_text(json.dumps(sanitize(spec), separators=(",", ":"), allow_nan=False))


def _fmt_all(fmt, values):
    return [None if v is None or (isinstance(v, float) and np.isnan(v)) else fmt(v) for v in values]


def _spread(ys, gap):
    """Nudge label positions apart so no two are closer than `gap`, keeping their order."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    pos = list(ys)
    for a, b in zip(order, order[1:]):
        if pos[b] - pos[a] < gap:
            pos[b] = pos[a] + gap
    return pos


def _nice_limits(ax, lo_data, hi_data, ymin):
    ticks = ax.yaxis.get_major_locator().tick_values(lo_data if ymin is None else ymin, hi_data)
    lo = ymin if ymin is not None else ticks[ticks <= lo_data][-1] if (ticks <= lo_data).any() else ticks[0]
    hi = ticks[ticks >= hi_data][0] if (ticks >= hi_data).any() else ticks[-1]
    return lo, hi


# ---------------------------------------------------------------- charts

def line_chart(data, *, title, subtitle, ylabel, source, out, fmt, scale=1.0, ymin=0, dashed=(), labels=None,
               zero_line=False, height=5.4, events=(), step=False, logy=False):
    """Line chart, focus economy first in `data.columns`; other series gray, darker the higher they end.

    scale divides values for display (e.g. 1e9 for billions); fmt formats the end value in the direct label;
    dashed: series drawn dashed (e.g. a regional average); labels: display names overriding NAMES.
    """
    d = data / scale
    labels = labels or {}
    fig, ax = _figure(height=height, plot_box=(0.09, 0.75, 1 - 1.0 / height, 0.85 / height))
    focus_iso, others = d.columns[0], list(d.columns[1:])
    others.sort(key=lambda c: d[c].dropna().iloc[-1], reverse=True)
    cols = [focus_iso, *others]
    colors = {c: color_for(c, j, len(cols), cols) for j, c in enumerate(cols)}
    dashed = set(dashed) | {c for c in cols if is_aggregate(c)}
    ends = []
    for c in [*reversed(others), focus_iso]:  # focus drawn last, on top
        s = d[c].dropna()
        focus = c == focus_iso
        ax.plot(s.index, s.values, color=colors[c], lw=2.6 if focus else 1.8, zorder=3 if focus else 2,
                ls="--" if c in dashed else "-", solid_capstyle="round", drawstyle="steps-post" if step else "default")
        ends.append((c, s.index[-1], s.iloc[-1], focus))
    if logy:
        ax.set_yscale("log")
        lo, hi = np.nanmin(d.values) * 0.8, np.nanmax(d.values) * 1.25
    else:
        lo, hi = _nice_limits(ax, np.nanmin(d.values), np.nanmax(d.values), ymin)
    ax.set_ylim(lo, hi)
    ax.set_xlim(d.index.min(), d.index.max())
    if zero_line and lo < 0 < hi:
        ax.axhline(0, color="#8a8a85", lw=0.9, zorder=1)
    for i, (year, text) in enumerate(events):  # policy events: dotted vertical line with a short label
        ax.axvline(year, color="#b3b2ab", lw=1, ls=":", zorder=1)
        ty = hi / (1.12 ** (i % 3 + 0.3)) if logy else hi - (hi - lo) * (0.03 + 0.065 * (i % 3))
        ax.text(year + 0.25, ty, text, fontsize=8.5, color=MUTED, va="top")
    label_y = [e[2] for e in ends] if logy else _spread([e[2] for e in ends], gap=(hi - lo) * 0.06)
    for (c, year, val, focus), y in zip(ends, label_y):
        name = labels.get(c, NAMES.get(c, c))
        ax.annotate(f"{name}  {fmt(val)}", xy=(year, y), xytext=(12, 0), textcoords="offset points",
                    va="center", annotation_clip=False, color=INK if focus else MUTED,
                    fontweight="bold" if focus else "normal")
    _style_axis(ax)
    ax.set_ylabel(ylabel)
    years = d.index
    span = years.max() - years.min()
    xstep = 10 if span > 40 else 4 if span > 12 else 2
    ax.set_xticks(range(years.min(), years.max() + 1, xstep))
    _spec(out, "line", title, subtitle, source, ylabel=ylabel, years=[int(y) for y in d.index], logy=logy,
          step=step, zero_line=zero_line, ymin=ymin, events=[[float(y), t] for y, t in events],
          series=[{"key": str(c), "name": labels.get(c, NAMES.get(c, c)), "color": colors[c],
                   "focus": c == focus_iso, "dashed": c in dashed,
                   "values": [_clean(v) for v in d[c].values], "labels": _fmt_all(fmt, d[c].values)}
                  for c in [focus_iso, *others]])
    _finish(fig, title, subtitle, source, out)


def bar_rank(values, *, title, subtitle, xlabel, source, out, fmt, highlight=(FOCUS,), labels=None,
             light=(), width=9.0, ref=None, ref_label=None):
    """Horizontal bars sorted high to low. values: Series label -> value. Highlighted bars blue, others gray;
    `light` bars light blue (e.g. regional averages). ref: optional vertical reference line."""
    v = values.dropna().sort_values()
    labels = labels or {}
    height = 1.45 + 0.34 * len(v)
    labs = ["\n".join(textwrap.wrap(str(labels.get(k, NAMES.get(k, k))), 34)) for k in v.index]
    left = min((max(len(line) for x in labs for line in x.split("\n")) * 0.095 + 0.35) / width, 0.45)
    height += 0.18 * sum(x.count("\n") for x in labs)
    fig, ax = _figure(width=width, height=height, plot_box=(left, 0.90, 1 - 1.0 / height, 0.85 / height))
    econ_bars = any(str(k) in ECON for k in v.index) or bool(highlight and set(highlight) & set(v.index))

    def bar_color(k):
        if econ_bars:  # ranking of economies: each comparison economy in its own colour, the rest neutral
            return ECON.get(str(k), "#f3a5a4" if k in highlight else ECON["EAS"] if k in light else GRAY_BAR)
        return SECTOR.get(str(k), "#eb6834" if k in highlight else BLUE_LIGHT if k in light else BLUE)  # one series: one colour
    colors = [bar_color(k) for k in v.index]
    ax.barh(range(len(v)), v.values, color=colors, height=0.68, zorder=2)
    ax.set_yticks(range(len(v)))
    ax.set_yticklabels(labs)
    for lab in ax.get_yticklabels():
        if lab.get_text() in [labels.get(k, NAMES.get(k, k)) for k in highlight]:
            lab.set_color(INK)
            lab.set_fontweight("bold")
    span = max(v.max(), 0) - min(v.min(), 0)
    for i, val in enumerate(v.values):
        ax.text(val + span * 0.01 if val >= 0 else val - span * 0.01, i, fmt(val), va="center",
                ha="left" if val >= 0 else "right", fontsize=10, color=MUTED)
    ax.set_xlim(min(v.min(), 0) * 1.15, max(v.max(), 0) * 1.15)
    if ref is not None:
        ax.axvline(ref, color="#8a8a85", lw=1, ls="--", zorder=3)
        if ref_label:
            ax.text(ref, len(v) - 0.4, f" {ref_label}", color=MUTED, fontsize=9, va="bottom")
    if min(v.min(), 0) < 0:
        ax.axvline(0, color="#8a8a85", lw=0.9)
    _style_axis(ax, grid="x")
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(xlabel)
    order = list(v.index)[::-1]  # high to low for the interactive version
    _spec(out, "bar", title, subtitle, source, xlabel=xlabel, ref=ref, ref_label=ref_label,
          cats=[str(labels.get(k, NAMES.get(k, k))) for k in order], keys=[str(k) for k in order],
          values=[_clean(v[k]) for k in order], labels=[fmt(v[k]) for k in order],
          colors=[bar_color(k) for k in order])
    _finish(fig, title, subtitle, source, out)


def grouped_bars(table, *, title, subtitle, xlabel, source, out, fmt, width=9.0, ref=None):
    """Horizontal grouped bars: rows = categories, columns = economies (focus first, blue; peers gray)."""
    t = table
    n_cat, n_ser = t.shape
    height = 1.9 + 0.22 * n_cat * n_ser + 0.18 * n_cat
    left = (max(len(str(i)) for i in t.index) * 0.095 + 0.35) / width
    fig, ax = _figure(width=width, height=height, plot_box=(left, 0.92, 1 - 1.3 / height, 1.05 / height))
    bar_h = 0.8 / n_ser
    colors = [color_for(c, j, n_ser, list(t.columns)) for j, c in enumerate(t.columns)]
    for j, col in enumerate(t.columns):
        y = np.arange(n_cat)[::-1] + (n_ser / 2 - j - 0.5) * bar_h
        ax.barh(y, t[col].values, height=bar_h * 0.92, color=colors[j % len(colors)], label=NAMES.get(col, col),
                zorder=2)
        for yy, val in zip(y, t[col].values):
            if pd.notna(val):
                ax.text(val, yy, " " + fmt(val), va="center", fontsize=8.5, color=MUTED)
    ax.set_yticks(np.arange(n_cat)[::-1])
    ax.set_yticklabels(t.index)
    if ref is not None:
        ax.axvline(ref, color="#8a8a85", lw=1, ls="--", zorder=3)
    ax.set_xlim(min(0, np.nanmin(t.values)) * 1.15, np.nanmax(t.values) * 1.18)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), frameon=False, fontsize=9.5, ncol=len(t.columns),
              handlelength=1.2, columnspacing=1.4)
    _style_axis(ax, grid="x")
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(xlabel)
    _spec(out, "grouped", title, subtitle, source, xlabel=xlabel, ref=ref, cats=[str(i) for i in t.index],
          series=[{"key": str(c), "name": NAMES.get(c, c), "color": colors[j % len(colors)],
                   "values": [_clean(x) for x in t[c].values], "labels": _fmt_all(fmt, t[c].values)}
                  for j, c in enumerate(t.columns)])
    _finish(fig, title, subtitle, source, out)


def stacked_shares(table, *, title, subtitle, source, out, colors=None, width=9.0, min_label=4.0):
    """100% stacked horizontal bars. table: rows = bars (e.g. years), columns = parts (% shares summing to ~100)."""
    t = table
    ncol = 3 if len(t.columns) > 4 else len(t.columns)
    legend_rows = -(-len(t.columns) // ncol)
    top_in = 0.9 + 0.27 * legend_rows
    height = top_in + 0.62 * len(t) + 0.95
    fig, ax = _figure(width=width, height=height, plot_box=(0.10, 0.97, 1 - top_in / height, 0.85 / height))
    palette = colors or [color_for(c, j, len(t.columns), list(t.columns)) for j, c in enumerate(t.columns)]
    left = np.zeros(len(t))
    y = np.arange(len(t))[::-1]
    for j, col in enumerate(t.columns):
        vals = t[col].fillna(0).values
        color = palette[j % len(palette)]
        ax.barh(y, vals, left=left, color=color, height=0.62, label=col, edgecolor="#fffdf6", lw=1.5)
        dark = _is_dark(color)
        for yy, l0, v in zip(y, left, vals):
            if v >= min_label:
                ax.text(l0 + v / 2, yy, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color="white" if dark else INK)
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels([str(i) for i in t.index])
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_ylim(-0.5, len(t) - 0.5)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.01), ncol=ncol, frameon=False, fontsize=9,
              handlelength=1.1, columnspacing=1.2)
    _style_axis(ax, grid=None)
    ax.tick_params(axis="y", length=0)
    _spec(out, "stacked", title, subtitle, source, rows=[str(i) for i in t.index],
          parts=[{"name": str(c), "color": palette[j % len(palette)], "values": [_clean(x) for x in t[c].values]}
                 for j, c in enumerate(t.columns)])
    _finish(fig, title, subtitle, source, out)


def radar(table, *, title, subtitle, source, out, vmax=100, ranks=None):
    """Radar chart: rows = axes (dimensions), columns = series (focus first; a column named like the region dashed)."""
    t = table
    angles = np.linspace(0, 2 * np.pi, len(t), endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.16, 0.13, 0.56, 0.68], polar=True)
    colors = [color_for(c, j, len(t.columns)) for j, c in enumerate(t.columns)]
    for j, col in enumerate(t.columns):
        vals = t[col].tolist() + t[col].tolist()[:1]
        focus = j == 0
        ls = "--" if col in ("EAS", "East Asia & Pacific", "Region") else "-"
        ax.plot(angles, vals, color=colors[j % len(colors)], lw=2.6 if focus else 1.5, ls=ls,
                label=NAMES.get(col, col), zorder=3 if focus else 2)
        if focus:
            ax.fill(angles, vals, color=colors[0], alpha=0.12)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(t.index, fontsize=10, color=INK)
    ax.set_ylim(0, vmax)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25", "50", "75", "100"], fontsize=8, color=MUTED)
    ax.set_rlabel_position(102)
    ax.grid(color=GRID)
    ax.spines["polar"].set_color(GRID)
    ax.tick_params(axis="x", pad=10)
    ax.legend(loc="upper left", bbox_to_anchor=(1.12, 0.95), frameon=False, fontsize=10)
    _spec(out, "radar", title, subtitle, source, vmax=vmax, dims=[str(i).replace("\n", " ") for i in t.index],
          ranks=ranks, series=[{"key": str(c), "name": NAMES.get(c, c), "color": colors[j % len(colors)],
                                "dashed": c in ("EAS", "East Asia & Pacific", "Region"),
                                "values": [_clean(x) for x in t[c].values]} for j, c in enumerate(t.columns)])
    _finish(fig, title, subtitle, source, out)


def scatter(df, *, x, y, title, subtitle, xlabel, ylabel, source, out, label_col=None, highlight=(), logx=False,
            fit=None, annotate=(), size=None):
    """Scatter of all points in gray, `highlight` labels in blue; optional fitted line fit=(intercept, slope)."""
    fig, ax = _figure(height=6.0, plot_box=(0.10, 0.95, 1 - 1.0 / 6.0, 0.95 / 6.0))
    s = 18 if size is None else size
    ax.scatter(df[x], df[y], s=s, color="#a9c8ee", edgecolor="#5598e7", lw=0.5, zorder=2)
    if fit is not None:
        xs = np.linspace(df[x].min(), df[x].max(), 50)
        ax.plot(xs, fit[0] + fit[1] * (np.log(xs) if logx else xs), color=MUTED, lw=1.2, ls="--", zorder=1)
    pts = []
    for key in annotate:
        r = df[df[label_col] == key]
        if len(r):
            r = r.iloc[0]
            hi = key in highlight
            ax.scatter([r[x]], [r[y]], s=46 if hi else 30, color=ECON.get(str(key), "#eb6834"), edgecolor="#fffdf6",
                       lw=1, zorder=3)
            pts.append((key, r[x], r[y], hi))
    if logx:
        ax.set_xscale("log")
    fig.canvas.draw()
    placed = []  # label boxes already drawn, in display pixels: try four offsets and take the first free one
    for key, px, py, hi in sorted(pts, key=lambda t: t[1]):
        name = NAMES.get(key, SHORT.get(key, key))
        w, h = len(name) * 6.2 * fig.dpi / 100, 12 * fig.dpi / 100
        X, Y = ax.transData.transform((px, py))
        for dx, dy, ha in ((5, 4, "left"), (5, -13, "left"), (-5, 4, "right"), (-5, -13, "right"), (5, 15, "left")):
            x0 = X + dx * fig.dpi / 72 - (w if ha == "right" else 0)
            y0 = Y + dy * fig.dpi / 72
            box = (x0, y0, x0 + w, y0 + h)
            if not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] for b in placed):
                break
        placed.append(box)
        ax.annotate(name, (px, py), xytext=(dx, dy), textcoords="offset points", ha=ha,
                    fontsize=9, color=INK if hi else MUTED, fontweight="bold" if hi else "normal")
    if logx:  # plain numbers on the log axis (mathtext is off, so matplotlib's 10^x labels would print raw)
        ax.set_xscale("log")
        lo, hi = df[x][df[x] > 0].min(), df[x].max()
        ticks = [t for t in (100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000) if lo * 0.8 <= t <= hi * 1.25]
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:,}" for t in ticks])
        ax.xaxis.set_minor_formatter(plt.NullFormatter())
    _style_axis(ax, grid="both")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    _spec(out, "scatter", title, subtitle, source, xlabel=xlabel, ylabel=ylabel, logx=logx,
          fit=[_clean(f) for f in fit] if fit is not None else None, highlight=list(highlight),
          annotate=list(annotate),
          points=[{"key": str(r[label_col]) if label_col else None,
                   "name": NAMES.get(r[label_col], r[label_col]) if label_col else None,
                   "x": _clean(r[x]), "y": _clean(r[y])} for _, r in df.iterrows()])
    _finish(fig, title, subtitle, source, out)
