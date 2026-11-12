# CLAUDE.md: EC 391 Country Team Project (Singapore)

Context for Claude Code. This project was planned in a claude.ai conversation; this file carries that context over.

## The assignment

- Course: EC 391, "Country Team App Project". Country: **Singapore**. Team of 3.
- Deliverables: a **website** (published from this repo via GitHub Pages) + **one Markdown file** (all sections concatenated).
- Deadline: **Fri Dec 11, 2026**, submit before noon. Internal final version: Wed Dec 9.
- Professor's principles: build every chart ourselves from raw data (no screenshots/copied charts; AI is allowed and encouraged
  for building statistics); give **global and regional rankings** for every indicator; use only approved sources (ask the
  professor otherwise); every figure has axis labels, units, footnotes and a source line.
- Grading: depth of trade & FDI analysis (RCA, GVC, …) 35% · data quality 25% · case study + country generalities 20% ·
  group management (confidential self-assessment) 20%.
- Sections (the guidelines have no Section 8):
  1. Country profile: geography, population, languages, political system, capital; development phases; HDI, life
     expectancy, literacy, education vs regional average
  2. Macro, business climate, governance: 20-yr GDP (current + PPP), GDP per capita, real growth; poverty ($2.15/day) and
     Gini; B-READY (and legacy Doing Business); WGI six dimensions (radar or table); CPI rank + trend; LPI. Global + regional
     rank for each and what it implies for trade/investment
  3. Openness & trade patterns: (X+M)/GDP vs peers; goods and services balances separately; export/import structure;
     main partners; concentration (HHI); 20-yr composition shift; does trade follow gravity
  4. Specialization & comparative advantage: own Balassa RCA by sector vs 2–3 peers; shift over the decade; endowments
     (K/L from PWT, resource rents); does it match Heckscher-Ohlin; (optional) exporter characteristics
  5. Global value chains: value-added vs gross exports (foreign content); backward + forward participation;
     upstream/downstream; most integrated sectors (OECD TiVA; 2025 edition covers Singapore)
  6. FDI: inflows % of GDP 15–20 yrs; stock by source country and sector; greenfield vs M&A; what foreign firms seek;
     outward FDI and its size relative to GDP
  7. Trade policy: WTO membership, MFN average and peak tariffs; PTAs (partner, year, scope); regional blocs and stage;
     NTMs (TRAINS); BITs; SEZs; recent controversies
  9. Case study: one policy/shock distinctive to Singapore (ideas: semiconductor/pharma FDI and EDB strategy;
     EU-Singapore FTA 2019 or US-Singapore FTA 2004; global minimum tax and Singapore's response)
  + Conclusion page: overall findings + SWOT + investment recommendation

## Storyline (draft, team to confirm)

Singapore has almost no natural resources and a small domestic market, yet through open institutions, free trade
agreements and foreign investment it became a hub of global value chains and regional headquarters.
Six parts: 1 Starting point (Ch. 1–2) → 2 Openness (Ch. 3) → 3 Advantage (Ch. 4) → 4 Position (Ch. 5) →
5 FDI & policy (Ch. 6–7) → 6 Case + conclusion. Every section ends with one "bridge" sentence into the next.

## Team and workflow ("AI hub")

| | Sections | Case part | Reviews |
| --- | --- | --- | --- |
| A (Estella, repo owner) | Ch. 2, Ch. 5 | Background & policy | B |
| B | Ch. 1, 3, 4 | Data & before/after | C |
| C | Ch. 6, 7, Conclusion | Impact & conclusion | A |

One AI (this repo + Claude Code) does calculations, charts, first drafts and the site, so style and numbers stay
consistent. Each member: downloads data for their sections, spot-checks 2–3 numbers per chart against the original
source, and rewrites their sections' text in their own words. Weekly meeting on the weekend (time TBD, proposed Sun 4pm).

Key dates: Nov 15 data downloaded, peers + case topic decided · Nov 22 all charts done and checked ·
Nov 29 text rewritten (Thanksgiving, no meeting) · Dec 6 case + peer review, read-through · Dec 9 final · Dec 11 submit.

## Conventions

- Comparison economies: **Malaysia (MYS), Hong Kong SAR (HKG), Vietnam (VNM)**. Region: World Bank "East Asia & Pacific"
  (EAS). Years **2004–2024**. Keep all economies in raw data so rankings can be computed.
- A shared table of 8–10 sectors (electronics, chemicals, pharma, machinery, refined petroleum, finance, logistics, …) is
  used by Ch. 4 (HS codes), Ch. 5 (TiVA/ISIC) and Ch. 6 (FDI by industry) so the chapters line up. Not built yet.
- Chart style (see `figures/ch02_gdp_current_usd.png`): Singapore in blue `#2a78d6`, peers in grays
  (`#5f5e5a`, `#8a8a85`, `#b3b2ab`); takeaway title stating the finding with its number; subtitle with measure + years;
  direct labels at line ends; light horizontal grid only; single y-axis; source line at the bottom with indicator code and
  retrieval date. One PNG per figure, `figures/chNN_topic.png`.
- Text: one Markdown file per section in `text/` (`ch01_profile.md`, `ch02_macro.md`, … `ch09_case.md`, `conclusion.md`),
  each with: key finding (numbers + ranks) → figures (footnote + source) → analysis answering the guideline questions →
  implications for trade and investment + bridge sentence → sources.
- Log every downloaded file in `data/SOURCES.md` (database, version, date, link, who).

## Repo

- `scripts/fetch_worldbank.py`: downloads WDI + WGI for all economies into `data/raw/wdi/` (run locally or via the
  "Fetch data" workflow). WGI codes are tried as `XX.EST` and `GOV_WGI_XX.EST`.
- `site/build.py`: builds `_site/` from `text/*.md` + `figures/`; `.github/workflows/pages.yml` publishes it
  (one-time: Settings → Pages → Source: GitHub Actions). `.github/workflows/fetch-data.yml` runs the fetch on GitHub.

## Status (Nov 11, 2026)

- Done: project scaffold; WDI + WGI fetched by the Fetch data workflow (Nov 12, `data/raw/wdi/`); first Ch. 2 chart
  (GDP current US$, SGP vs peers) redrawn from the official CSV by `scripts/ch02_gdp.py` (SGP 2024 = $572.9bn).
- Charts: shared style in `scripts/chart_style.py` (`line_chart`, `wide`, `load`, `countries`, `retrieved`); one script per
  figure, `scripts/chNN_topic.py`. Local setup: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
  The World Bank API is not reachable from Estella's Mac (times out): fetch via the GitHub workflow, then `git pull`.
- WGI: the API serves the estimates only as `GOV_WGI_XX.EST` (saved as `XX.EST.csv`); percentile ranks (`XX.PER.RNK`)
  are not available, so compute global/regional ranks from the estimates.
- Notes found during planning: World Bank WDI likely has no $2.15 poverty or Gini data for Singapore; Singapore's official
  Gini is published by SingStat (household income from work, before/after taxes and transfers): ask the professor
  whether SingStat is acceptable. B-READY 2024 (first edition) covers Singapore. OECD TiVA 2025 edition covers Singapore.
  Much of Singapore's exports are re-exports: use SingStat's domestic exports vs re-exports split in Ch. 3–4.
  A lot of Singapore's FDI passes through regional HQ / holding companies: mention in Ch. 6.
- Next for Member A: Ch. 2 charts (GDP per capita incl. PPP, growth, WGI radar, CPI/LPI/B-READY rank
  tables with global + regional rank); then Ch. 5 from TiVA (download from data-explorer.oecd.org if no API route works).
- Open questions for the professor: SingStat OK as a source? Compute RCA ourselves or OEC values OK? Required
  platform/format for the site? Is a class presentation required? Is AI-drafted text OK?
