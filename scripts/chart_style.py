"""Shared helpers for every chart: load World Bank CSVs and draw in the project's house style.

Style (see CLAUDE.md): Singapore in blue, peers in grays; takeaway title with its number; subtitle with
measure + years; direct labels at line ends; light horizontal grid only; single y-axis; source line at the bottom
with indicator code and retrieval date. One PNG per figure, figures/chNN_topic.png.
"""
import datetime as dt
import subprocess
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
WDI = ROOT / "data" / "raw" / "wdi"
FIGURES = ROOT / "figures"

FOCUS = "SGP"
PEERS = ["MYS", "HKG", "VNM"]
REGION = "EAS"  # World Bank "East Asia & Pacific" aggregate
NAMES = {"SGP": "Singapore", "MYS": "Malaysia", "HKG": "Hong Kong SAR", "VNM": "Vietnam",
         "EAS": "East Asia & Pacific", "WLD": "World"}

BLUE = "#2a78d6"
GRAYS = ["#5f5e5a", "#8a8a85", "#b3b2ab"]
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
})


def load(code):
    """One indicator as a long table (iso3, country, year, value), empty values dropped."""
    df = pd.read_csv(WDI / f"{code}.csv")
    return df.dropna(subset=["value"]).astype({"year": int})


def wide(code, economies):
    """year x economy table for the chosen economies."""
    df = load(code)
    return df[df.iso3.isin(economies)].pivot(index="year", columns="iso3", values="value")[economies]


def countries():
    """Country metadata; is_aggregate rows are regions/income groups, not economies."""
    df = pd.read_csv(WDI / "countries.csv", keep_default_na=False)
    df["is_aggregate"] = df.is_aggregate.astype(str) == "True"
    return df


def retrieved(code):
    """Date the CSV was committed (= downloaded by the Fetch data workflow); today if not committed yet."""
    path = WDI / f"{code}.csv"
    out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    day = dt.date.fromisoformat(out) if out else dt.date.today()
    return f"{day:%b} {day.day}, {day.year}"


def _spread(ys, gap):
    """Nudge label positions apart so no two are closer than `gap`, keeping their order."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    pos = list(ys)
    for a, b in zip(order, order[1:]):
        if pos[b] - pos[a] < gap:
            pos[b] = pos[a] + gap
    return pos


def line_chart(data, *, title, subtitle, ylabel, source, out, fmt, scale=1.0, ymin=0):
    """Line chart, focus economy first in `data.columns`.

    data: year x economy table (raw units); scale divides values for display (e.g. 1e9 for billions);
    fmt: formats a displayed end value for the direct label, e.g. lambda v: f"${v:,.0f}bn".
    """
    d = data / scale
    fig, ax = plt.subplots(figsize=(9, 5.4))
    fig.subplots_adjust(left=0.09, right=0.75, top=0.82, bottom=0.15)

    # Peers get darker grays the higher they end, so label order and shade agree.
    focus_iso, peers = d.columns[0], list(d.columns[1:])
    peers.sort(key=lambda iso: d[iso].dropna().iloc[-1], reverse=True)
    colors = {focus_iso: BLUE, **{iso: GRAYS[min(i, len(GRAYS) - 1)] for i, iso in enumerate(peers)}}
    ends = []
    for iso in [*reversed(peers), focus_iso]:  # focus drawn last, on top
        s = d[iso].dropna()
        focus = iso == focus_iso
        ax.plot(s.index, s.values, color=colors[iso], lw=2.6 if focus else 1.8,
                zorder=3 if focus else 2, solid_capstyle="round")
        ends.append((iso, s.index[-1], s.iloc[-1], focus))

    # y range: start at ymin and end on a tick just above the data, so the top gridline is drawn.
    ticks = ax.yaxis.get_major_locator().tick_values(ymin if ymin is not None else d.min().min(), d.max().max())
    lo = ymin if ymin is not None else ticks[0]
    hi = ticks[ticks >= d.max().max()][0]
    ax.set_ylim(lo, hi)
    ax.set_xlim(d.index.min(), d.index.max())
    label_y = _spread([e[2] for e in ends], gap=(hi - lo) * 0.06)
    for (iso, year, val, focus), y in zip(ends, label_y):
        ax.annotate(f"{NAMES.get(iso, iso)}  {fmt(val)}", xy=(year, y), xytext=(12, 0),
                    textcoords="offset points", va="center", annotation_clip=False,
                    color=INK if focus else MUTED, fontweight="bold" if focus else "normal")

    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=3)
    ax.set_ylabel(ylabel)
    years = d.index
    ax.set_xticks(range(years.min(), years.max() + 1, 4))

    fig.text(0.07, 0.94, title, fontsize=14, fontweight="bold", color=INK)
    fig.text(0.07, 0.885, subtitle, fontsize=11, color=MUTED)
    fig.text(0.07, 0.03, source, fontsize=8.5, color=MUTED)

    FIGURES.mkdir(exist_ok=True)
    fig.savefig(FIGURES / out)
    plt.close(fig)
    print(f"wrote figures/{out}")
