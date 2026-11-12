# Singapore: a small country turned global hub

A data-driven economic portrait of Singapore's trade and foreign direct investment, built for the EC 391 (International
Trade) Country Team App project, Boston University, Fall 2026. Every chart and table is drawn by the team from raw data.

- **Live site:** https://ziqijia825-afk.github.io/ec391-singapore/
- **Markdown deliverable:** [`report/EC391_Singapore.md`](report/EC391_Singapore.md) (all sections in one file, generated from `text/`)
- **AI prompt log:** [`docs/prompt_log.md`](docs/prompt_log.md) (the syllabus asks each group to keep its prompts in Markdown)
- **Sources and download log:** [`data/SOURCES.md`](data/SOURCES.md), and the appendix on the site

## Chapters

The chapters follow the course guidelines. Each question names the syllabus module and reading it tests.

| Chapter | Topic | Course link |
| --- | --- | --- |
| 1 | Country profile, with an atlas of the country, its places of trade and its partners | |
| 2 | Macroeconomy, business climate and governance | Module 9, Nunn (2007) |
| 3 | Openness and trade patterns, with a gravity regression | Modules 2 and 8, Feyrer (2009) |
| 4 | Specialization and comparative advantage | Modules 3, 4 and 9 |
| 5 | Position in global value chains | Module 6, Fort (2017), Boehm et al. (2015) |
| 6 | Foreign direct investment | Modules 2 and 6 |
| 7 | Trade policy and major agreements | Module 7, Conconi et al. (2016) |
| 9 | Case study: chips and pills, Singapore's investment-led industrial policy | Module 9, Juhász (2015) |
| | Conclusion, SWOT and investment recommendation; appendix with sources and methods | |

Comparison economies are Malaysia, Hong Kong SAR and Vietnam, the region is the World Bank's East Asia and Pacific,
and the years are 2004 to 2024 unless a source ends earlier. Every indicator carries its global and regional rank.

## Methods and main results

- **Revealed comparative advantage:** RCA = (X<sub>ik</sub> / X<sub>i</sub>) ÷ (X<sub>wk</sub> / X<sub>w</sub>), goods from
  CEPII BACI and services from the World Bank. Transport RCA 4.5 and finance 2.8 in 2024.
- **Gravity:** OLS of ln(Singapore's exports to partner, 2024) on ln(partner GDP) and ln(distance between capitals),
  robust standard errors. Distance −1.59 (class estimate −1.46), BACI robustness −1.69, FTA dummy 1.98, 192 partners.
- **Heckscher Ohlin check:** across 154 economies, ln(RCA capital intensive ÷ RCA labour intensive) on ln capital per
  worker. Slope 0.43 (s.e. 0.16), R² 0.07; Singapore far above the line.
- **Value chains (OECD TiVA 2025):** foreign value added 46.1% of exports, position index −0.22 (73rd of 80).
- **Case study difference in differences:** ln RCA of pharmaceuticals against other chemicals and against Malaysia and
  Hong Kong SAR, before and after the 2000 Biomedical Sciences Initiative. β = 1.57 (s.e. 0.27), with an event study.
- **Concentration:** Herfindahl Hirschman index of export destinations, 0.074 in 2024.

## Data sources

Approved sources only: World Bank (WDI, WGI, B-READY, LPI), CEPII BACI, UN Comtrade, OECD TiVA, UNCTAD World Investment
Report annex tables, WTO tariff profiles, UNCTAD TRAINS via WITS, Penn World Table 11.0, UNDP, the Singapore Department
of Statistics and Singapore government agencies. Transparency International's CPI is required by the guidelines. Every
download, with version and date, is logged in [`data/SOURCES.md`](data/SOURCES.md).

**Still to collect:** Transparency International's 2025 results file (the site blocks scripts, so it is read through
Our World in Data for now), FDI by ultimate investor (not published by Singapore), and plant level data on local
suppliers for the case study.

## Repository layout

| Folder | What it holds |
| --- | --- |
| `text/` | One Markdown file per chapter, the source of the site and the report |
| `scripts/` | Download scripts (`fetch_*.py`), one analysis script per chapter (`chNN_*.py`), shared chart style |
| `data/raw/` | Raw downloads (the 2.4 GB BACI zip is not in git; download it from CEPII) |
| `data/derived/` | Numbers (`chNN.json`) and tables (`*.md`) written by the scripts; the text quotes these |
| `figures/` | One PNG per figure, `chNN_topic.png` |
| `site/` | Site builder (`build.py`) and the interactive app (`site/app/`, vendored ECharts 5.5.0) |
| `report/` | The Markdown deliverable |

## Rebuilding

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/run_all.py          # every chart, table, the site and the report
```

Every push to `main` rebuilds the site on GitHub Pages. To add a file downloaded by hand, put it in `data/raw/manual/`
and log it in `data/SOURCES.md`.

## Checking the numbers

For each chart, take two or three numbers (the latest year, a peak), look them up on the original source and note the
result in the "Team check" column of the prompt log, or open an Issue if they differ.
