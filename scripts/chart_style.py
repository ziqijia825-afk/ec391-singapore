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

BLUE = "#2a78d6"
BLUE_LIGHT = "#a9c8ee"
GRAYS = ["#5f5e5a", "#8a8a85", "#b3b2ab"]
GRAY_BAR = "#c9c8c1"
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
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    day = dt.date.fromisoformat(out) if out else dt.datetime.now(dt.timezone.utc).date()
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
               zero_line=False, height=5.4, events=(), step=False):
    """Line chart, focus economy first in `data.columns`; other series gray, darker the higher they end.

    scale divides values for display (e.g. 1e9 for billions); fmt formats the end value in the direct label;
    dashed: series drawn dashed (e.g. a regional average); labels: display names overriding NAMES.
    """
    d = data / scale
    labels = labels or {}
    fig, ax = _figure(height=height, plot_box=(0.09, 0.75, 1 - 1.0 / height, 0.85 / height))
    focus_iso, others = d.columns[0], list(d.columns[1:])
    others.sort(key=lambda c: d[c].dropna().iloc[-1], reverse=True)
    colors = {focus_iso: BLUE, **{c: GRAYS[min(i, len(GRAYS) - 1)] for i, c in enumerate(others)}}
    ends = []
    for c in [*reversed(others), focus_iso]:  # focus drawn last, on top
        s = d[c].dropna()
        focus = c == focus_iso
        ax.plot(s.index, s.values, color=colors[c], lw=2.6 if focus else 1.8, zorder=3 if focus else 2,
                ls="--" if c in dashed else "-", solid_capstyle="round", drawstyle="steps-post" if step else "default")
        ends.append((c, s.index[-1], s.iloc[-1], focus))
    lo, hi = _nice_limits(ax, np.nanmin(d.values), np.nanmax(d.values), ymin)
    ax.set_ylim(lo, hi)
    ax.set_xlim(d.index.min(), d.index.max())
    if zero_line and lo < 0 < hi:
        ax.axhline(0, color="#8a8a85", lw=0.9, zorder=1)
    for i, (year, text) in enumerate(events):  # policy events: dotted vertical line with a short label
        ax.axvline(year, color="#b3b2ab", lw=1, ls=":", zorder=1)
        ax.text(year + 0.25, hi - (hi - lo) * (0.03 + 0.065 * (i % 3)), text, fontsize=8.5, color=MUTED, va="top")
    label_y = _spread([e[2] for e in ends], gap=(hi - lo) * 0.06)
    for (c, year, val, focus), y in zip(ends, label_y):
        name = labels.get(c, NAMES.get(c, c))
        ax.annotate(f"{name}  {fmt(val)}", xy=(year, y), xytext=(12, 0), textcoords="offset points",
                    va="center", annotation_clip=False, color=INK if focus else MUTED,
                    fontweight="bold" if focus else "normal")
    _style_axis(ax)
    ax.set_ylabel(ylabel)
    years = d.index
    step = 4 if years.max() - years.min() > 12 else 2
    ax.set_xticks(range(years.min(), years.max() + 1, step))
    _finish(fig, title, subtitle, source, out)


def bar_rank(values, *, title, subtitle, xlabel, source, out, fmt, highlight=(FOCUS,), labels=None,
             light=(), width=9.0, ref=None, ref_label=None):
    """Horizontal bars sorted high to low. values: Series label -> value. Highlighted bars blue, others gray;
    `light` bars light blue (e.g. regional averages). ref: optional vertical reference line."""
    v = values.dropna().sort_values()
    labels = labels or {}
    height = 1.45 + 0.34 * len(v)
    labs = [labels.get(k, NAMES.get(k, k)) for k in v.index]
    left = (max(len(str(x)) for x in labs) * 0.095 + 0.35) / width
    fig, ax = _figure(width=width, height=height, plot_box=(left, 0.90, 1 - 1.0 / height, 0.85 / height))
    colors = [BLUE if k in highlight else BLUE_LIGHT if k in light else GRAY_BAR for k in v.index]
    ax.barh(range(len(v)), v.values, color=colors, height=0.68, zorder=2)
    ax.set_yticks(range(len(v)))
    ax.set_yticklabels([labels.get(k, NAMES.get(k, k)) for k in v.index])
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
    _finish(fig, title, subtitle, source, out)


def grouped_bars(table, *, title, subtitle, xlabel, source, out, fmt, width=9.0, ref=None):
    """Horizontal grouped bars: rows = categories, columns = economies (focus first, blue; peers gray)."""
    t = table
    n_cat, n_ser = t.shape
    height = 1.9 + 0.22 * n_cat * n_ser + 0.18 * n_cat
    left = (max(len(str(i)) for i in t.index) * 0.095 + 0.35) / width
    fig, ax = _figure(width=width, height=height, plot_box=(left, 0.92, 1 - 1.3 / height, 1.05 / height))
    bar_h = 0.8 / n_ser
    colors = [BLUE] + GRAYS
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
    _finish(fig, title, subtitle, source, out)


def stacked_shares(table, *, title, subtitle, source, out, colors=None, width=9.0, min_label=4.0):
    """100% stacked horizontal bars. table: rows = bars (e.g. years), columns = parts (% shares summing to ~100)."""
    t = table
    ncol = 3 if len(t.columns) > 4 else len(t.columns)
    legend_rows = -(-len(t.columns) // ncol)
    top_in = 0.9 + 0.27 * legend_rows
    height = top_in + 0.62 * len(t) + 0.95
    fig, ax = _figure(width=width, height=height, plot_box=(0.10, 0.97, 1 - top_in / height, 0.85 / height))
    palette = colors or ["#2a78d6", "#6aa3e5", "#a9c8ee", "#5f5e5a", "#8a8a85", "#b3b2ab", "#d9d8d2", "#e9e8e3"]
    left = np.zeros(len(t))
    y = np.arange(len(t))[::-1]
    for j, col in enumerate(t.columns):
        vals = t[col].fillna(0).values
        color = palette[j % len(palette)]
        ax.barh(y, vals, left=left, color=color, height=0.62, label=col, edgecolor="white", lw=0.8)
        dark = color in ("#2a78d6", "#4f8fdd", "#5f5e5a", "#8a8a85", "#6aa3e5")
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
    _finish(fig, title, subtitle, source, out)


def radar(table, *, title, subtitle, source, out, vmax=100):
    """Radar chart: rows = axes (dimensions), columns = series (focus first; a column named like the region dashed)."""
    t = table
    angles = np.linspace(0, 2 * np.pi, len(t), endpoint=False).tolist()
    angles += angles[:1]
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_axes([0.16, 0.13, 0.56, 0.68], polar=True)
    colors = [BLUE] + GRAYS + ["#8a8a85"]
    for j, col in enumerate(t.columns):
        vals = t[col].tolist() + t[col].tolist()[:1]
        focus = j == 0
        ls = "--" if col in ("EAS", "East Asia & Pacific", "Region") else "-"
        ax.plot(angles, vals, color=colors[j % len(colors)], lw=2.6 if focus else 1.5, ls=ls,
                label=NAMES.get(col, col), zorder=3 if focus else 2)
        if focus:
            ax.fill(angles, vals, color=BLUE, alpha=0.12)
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
    _finish(fig, title, subtitle, source, out)


def scatter(df, *, x, y, title, subtitle, xlabel, ylabel, source, out, label_col=None, highlight=(), logx=False,
            fit=None, annotate=(), size=None):
    """Scatter of all points in gray, `highlight` labels in blue; optional fitted line fit=(intercept, slope)."""
    fig, ax = _figure(height=6.0, plot_box=(0.10, 0.95, 1 - 1.0 / 6.0, 0.95 / 6.0))
    s = 18 if size is None else size
    ax.scatter(df[x], df[y], s=s, color=GRAY_BAR, edgecolor="#8a8a85", lw=0.4, zorder=2)
    if fit is not None:
        xs = np.linspace(df[x].min(), df[x].max(), 50)
        ax.plot(xs, fit[0] + fit[1] * (np.log(xs) if logx else xs), color=MUTED, lw=1.2, ls="--", zorder=1)
    for key in annotate:
        r = df[df[label_col] == key]
        if len(r):
            r = r.iloc[0]
            hi = key in highlight
            ax.scatter([r[x]], [r[y]], s=38 if hi else s, color=BLUE if hi else "#8a8a85", zorder=3)
            ax.annotate(NAMES.get(key, key), (r[x], r[y]), xytext=(5, 4), textcoords="offset points",
                        fontsize=9, color=INK if hi else MUTED, fontweight="bold" if hi else "normal")
    if logx:
        ax.set_xscale("log")
    _style_axis(ax, grid="both")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    _finish(fig, title, subtitle, source, out)
