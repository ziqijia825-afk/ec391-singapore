# EC 391 Country Team App Project: Singapore

A data-driven economic portrait of Singapore, focused on trade and foreign direct investment (FDI).
Deliverables: the website (published from this repo with GitHub Pages) + one Markdown file (`report/EC391_Singapore.md`,
generated from the chapter texts).

**Storyline:** Singapore has almost no natural resources and a small domestic market, yet through open institutions,
free trade agreements and foreign investment it became a hub of global value chains and regional headquarters.

## Team

| | Sections | Case study part | Reviews |
| --- | --- | --- | --- |
| Member A | Ch. 2 Macro & governance; Ch. 5 Global value chains | Background and policy | B |
| Member B | Ch. 1 Country profile; Ch. 3 Trade patterns; Ch. 4 Comparative advantage | Data and before/after | C |
| Member C | Ch. 6 FDI; Ch. 7 Trade policy; Conclusion | Impact and conclusion | A |

All chapters have a complete first draft (charts, tables and text). Each member, for their own sections:
**check 2–3 numbers per chart against the original source → rewrite the text in their own words → link it to the
lectures and readings.** Calculations, charts and the website are produced in one place (the "AI hub") so style and
numbers stay consistent.

Comparison economies: Malaysia (MYS), Hong Kong SAR (HKG), Vietnam (VNM). Region: World Bank "East Asia & Pacific" (EAS).
Years: 2004–2024 (some sources end earlier: TiVA 2022, tariffs 2022).

## Folders

| Folder | What goes in it |
| --- | --- |
| `data/raw/wdi/` | World Bank WDI, WGI and B-READY (`scripts/fetch_worldbank.py` or the **Fetch data** workflow) |
| `data/raw/singstat/` | Singapore Department of Statistics tables (`scripts/fetch_singstat.py`) |
| `data/raw/tiva/` | OECD Trade in Value Added 2025 (`scripts/fetch_tiva.py`) |
| `data/raw/comtrade/` | UN Comtrade, Singapore's trade by partner (`scripts/fetch_comtrade.py`) |
| `data/raw/manual/` | CPI, HDI, Penn World Table, UNCTAD WIR annex tables (`scripts/fetch_other.py`) and the hand-compiled FTA list |
| `data/raw/atlas/` | Harvard Atlas trade files, ~500 MB, **not in git**: run `scripts/fetch_atlas.py` before re-running Ch. 3, 4, 9 |
| `data/derived/` | Numbers (`chNN.json`) and tables (`*.md`) produced by the chapter scripts; the text quotes these |
| `scripts/` | Download scripts (`fetch_*.py`), one analysis script per chapter (`chNN_*.py`), shared style (`chart_style.py`) and sector table (`sectors.py`) |
| `figures/` | Charts, one PNG per figure, named `chNN_topic.png` |
| `text/` | One Markdown file per page; `<!-- include: data/derived/X.md -->` pulls in a generated table |
| `site/` | Website builder; the site is published automatically on every push |
| `report/` | The single Markdown deliverable, rebuilt by `site/build.py` |

## How to regenerate everything

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch_atlas.py      # once (large download)
.venv/bin/python scripts/run_all.py          # all charts, tables, site and report
```

## How to add data you downloaded by hand

1. Open the repo on github.com → `data/raw/manual/` → **Add file → Upload files**
2. Drag your file in, write a one-line note (e.g. "CPI 2025 results, downloaded Nov 12"), click **Commit changes**
3. Add a line to `data/SOURCES.md`: database, version, download date, link

## How to check a chart

Open the chart on the website, pick 2–3 numbers (latest year, peak), look up the same number on the original
source. If it matches, say "Ch. X checked" in the group chat; if not, open an Issue with the original number and link.
