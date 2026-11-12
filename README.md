# EC 391 Country Team App Project: Singapore

A data-driven economic portrait of Singapore, focused on trade and foreign direct investment (FDI).
Deliverables: the website (published from this repo with GitHub Pages) + one Markdown file.

**Storyline (draft):** Singapore has almost no natural resources and a small domestic market, yet through open
institutions, free trade agreements and foreign investment it became a hub of global value chains and regional
headquarters.

## Team

| | Sections | Case study part | Reviews |
| --- | --- | --- | --- |
| Member A | Ch. 2 Macro & governance; Ch. 5 Global value chains | Background and policy | B |
| Member B | Ch. 1 Country profile; Ch. 3 Trade patterns; Ch. 4 Comparative advantage | Data and before/after | C |
| Member C | Ch. 6 FDI; Ch. 7 Trade policy; Conclusion | Impact and conclusion | A |

Each member, for their own sections: **download data → check numbers → rewrite text in their own words.**
Calculations, charts and the website are produced in one place (the "AI hub") so style and numbers stay consistent.

Comparison economies: Malaysia (MYS), Hong Kong SAR (HKG), Vietnam (VNM). Region: World Bank "East Asia & Pacific" (EAS).
Years: 2004–2024.

## Folders

| Folder | What goes in it |
| --- | --- |
| `data/raw/wdi/` | World Bank data, downloaded automatically by the **Fetch data** workflow |
| `data/raw/manual/` | Files we download by hand (CPI, B-READY, TiVA, SingStat, BACI, …). Name them `source_topic_year.ext` |
| `scripts/` | Download, calculation and chart scripts |
| `figures/` | Charts, one PNG per figure, named `chNN_topic.png` |
| `text/` | One Markdown file per section (`ch01_profile.md`, …), rewritten by each owner |
| `site/` | Website builder; the site is published automatically on every push |

## How to add data you downloaded by hand

1. Open the repo on github.com → `data/raw/manual/` → **Add file → Upload files**
2. Drag your file in, write a one-line note (e.g. "CPI 2025 results, downloaded Nov 12"), click **Commit changes**
3. Add a line to `data/SOURCES.md`: database, version, download date, link

## How to check a chart

Open the chart on the website, pick 2–3 numbers (latest year, peak), look up the same number on the original
source. If it matches, say "Ch. X checked" in the group chat; if not, open an Issue with the original number and link.
