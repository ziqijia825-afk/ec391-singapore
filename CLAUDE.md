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
- Chart style (see `figures/ch02_gdp_current_usd.png`): one colour per economy in every chart (Nov 12, after comparing
  with the Argentina site): Singapore red `#e34948`, Malaysia blue `#2a78d6`, Hong Kong SAR gold `#eda100`, Vietnam green
  `#008300`, regional and world averages neutral and dashed; sectors keep fixed colours (goods distinct hues, services one
  warm family), years an ordinal blue ramp (older lighter). Palette checked with the dataviz validator. All set in
  `chart_style.py` (`ECON`, `SECTOR`, `color_for`) and mirrored in `site/app/js/chart.js` (`ECON`, `CATEGORICAL`); takeaway title stating the finding with its number; subtitle with measure + years;
  direct labels at line ends; light horizontal grid only; single y-axis; source line at the bottom with indicator code and
  retrieval date. One PNG per figure, `figures/chNN_topic.png`.
- Text: one Markdown file per section in `text/` (`ch01_profile.md`, `ch02_macro.md`, … `ch09_case.md`, `conclusion.md`),
  each with: key finding (numbers + ranks) → figures (footnote + source) → analysis answering the guideline questions →
  implications for trade and investment + bridge sentence → sources.
- Log every downloaded file in `data/SOURCES.md` (database, version, date, link, who).

## Lessons from the Argentina team's site (same course)

Another EC 391 team's site (https://piranha315.github.io/Argentina-Interactive-Website/, checked Nov 12, 2026). Borrow
structure, data routes and methods only; never their text, charts or numbers (the professor requires our own charts).

- **Tie every section to the course.** Their strongest move: each chapter names the lecture model or reading it tests
  (Ch. 8 learning function and infant industry, Nunn 2007 institutions → specialization, Juhász natural experiment,
  the Ireland / "dark matter" FDI readings) and compares team estimates with the class estimate (gravity distance
  elasticity, class value on 2024 world data −1.46). Do the same in every chapter (likely the "depth of analysis" 35%).
- **Appendix page:** sources grouped by provider and tagged by type (Government / IGO / UN / NGO), data-access date,
  methods with formulas (RCA, gravity, HHI, export groups by HS range), and a "Still to collect" list.
- **Tables to copy in form:** RCA by HS chapter vs peers with shading (dark ≥ 10, mid 1–10, pale < 1); PTA table with
  columns Agreement · In force · Type · Scope · Note (sources: WTO RTA database, etc.).
- **Ch. 3 gravity:** OLS of ln(exports to partner) on ln(partner GDP) and ln(capital-to-capital distance) from Comtrade
  + WDI country coordinates; scatter of size-adjusted exports vs distance. For Singapore, use domestic exports where
  possible, since re-exports follow entrepôt routes, not gravity alone.
- **Ch. 4 RCA:** they use 2023 Comtrade as the latest year with near-complete reporter coverage (world = sum of 167
  reporters). Services matter for Singapore: consider the Harvard Atlas services data (see Emily-coding/comparative-advantage).
- **Ch. 6 FDI:** label stock by *immediate* investor country and footnote that holding-company hubs hide the ultimate
  parent. For Singapore this cuts both ways (it is itself such a hub): say so.
- **Ch. 9 case structure:** course argument → policy facts (legal texts) → data test (RCA, exports vs imports) →
  verdict in the model's terms → what further data would confirm it.
- **Do not copy:** their GDP chart uses bars + line on two y-axes (our rule: single y-axis); their map hero and
  game-style design. TiVA, UNCTAD NTM counts and IIA BIT counts blocked their automated download: plan manual exports.

## Repo

- Approved sources only (guidelines p. 4 list + national statistics office). The Harvard Atlas is NOT on the list and
  was removed on Nov 12: goods trade now comes from CEPII BACI HS92 V202601 (2.4 GB zip in data/raw/baci/, git-ignored;
  `scripts/process_baci.py` aggregates it into data/derived/baci_*.csv), services exports by category from WDI BoP
  (`scripts/trade_data.py`). CPI still comes via Our World in Data until someone downloads TI's CPI2025_Results.xlsx by
  hand (TI blocks scripts); UNCTAD's IIA Navigator is behind Cloudflare, so BIT partners come from METI's page.
- Download: `fetch_worldbank.py` (WDI, WGI, B-READY, Doing Business rank; "Fetch data" workflow too), `fetch_singstat.py`,
  `fetch_tiva.py` (OECD SDMX sti-public), `fetch_comtrade.py` (partners every year + HS chapter titles),
  `fetch_other.py` (CPI via OWID, UNDP HDI, PWT 11.0, UNCTAD WIR 2026 annex, WTO tariff profiles), `fetch_wits_ntm.py`
  (TRAINS NTMs via WITS), `fetch_geo.py` (Natural Earth + geoBoundaries for the maps). Scripts send an honest project
  User-Agent; never spoof a browser or get past bot checks.
- Analysis: one script per chapter (`ch01_profile.py` … `ch09_case.py`) writes `figures/chNN_*.png`, a JSON spec per
  figure in `site/data/figs/` (same numbers, units, source), `data/derived/chNN.json` and `data/derived/*.md` tables.
  `export_site_data.py` writes the interactive datasets (KPIs, Sankey, GVC network, FDI explorer, WGI by year, RCA by
  year). `run_all.py` reruns everything and builds the site.
- Site: `site/build.py` builds `_site/index.html`, an editorial country profile modelled on the Growth Lab and OEC
  profiles (Nov 13, after the picture book was dropped): a cover that is the interactive atlas (title and six ranked
  KPIs on the left, `sgMap` on the right opening on the twelve partners' trade lanes, with the country and places views,
  a caption per view, an exports/imports switch with the twelve partners' total share, a line-width legend, distance
  rings at 1,000/2,000/3,000 km, and a scale bar and north arrow measured on the map), then one screen per question, made by `paginate()`: text column on the left (question, bold answer,
  short paragraphs, expandable details, previous/next section links), a sticky full-height chart on the right,
  full-width screens for interactive components, single-column prose screens, navy chapter openers with contents and
  three number cards. `js/story.js` renders charts lazily, follows the reader (chapter tab, address, progress bar) and
  resolves `#pN`, `#chNN` and `#sec=chNN|Heading` links. Palette and type: navy, gold, Singapore red, Source Serif 4,
  Inter, one accent colour per chapter (`BANNER_COLORS` in build.py); small UI: numbered chapter chips, a Contents
  drawer, a key-number strip with line icons (`js/icons.js`), a dictionary-style fact grid (`ch01_facts.md`), atlas list
  and detail cards with map zoom controls. `js/enhance.js` threads small UI through the text (number highlights, peer colour dots,
  glossary tooltips with the team's own definitions, chart and table counts on "More" toggles, next-chapter cards, a
  callout box for the Ch. 9 verdict and the investment recommendation). Nov 13: fine print cut after a second
  comparison with Argentina (no running heads, prev/next links, source badges, stat strips, chapter meta chips or year
  badges; the year sits in the title; Data/PNG/link buttons show on hover). Ch. 9 has a learning-curve model
  (`learncurve` in components.js, H(t) = A − B/t, sliders, "Fit to our data" from the BACI RCA series). Figures and tables are numbered per chapter; `## Heading {Feyrer 2009}` becomes a course-reading tag; the
  Ch. 1 atlas (`site/data/atlas.json`) has 7 places and 12 partners with sourced cards. ECharts 5.5.0 vendored;
  `_site/article/*.html` is the static version and the Markdown deliverable `report/EC391_Singapore.md`. In `text/*.md`, `<!-- include: data/derived/X.md -->` inserts a
  table and `<!-- interactive: NAME -->` places a component (sgmap, sankey, treemap, gvc, fdi). Build adds `?v=` cache
  busting to JS and data. Local preview `ec391-site` on :8391 (`~/.claude/launch.json`).
- Testing in a hidden browser pane: IntersectionObserver and animations are throttled, so render charts by importing
  `/js/chart.js?v=${window.__V}` and disable animation before screenshots.

## Status (Nov 12, 2026)

- Guidelines audit: `docs/guidelines_audit_and_design.md`. Fixed: approved sources only (BACI + WDI services), literacy
  and regional averages (Ch. 1), PWT long-run GDP with structural breaks, GDP PPP and per-capita USD series, $2.15 to
  $3.00 poverty-line note, Doing Business 2020 rank (Ch. 2), outward FDI by industry and investment income (Ch. 6),
  WTO tariff profiles with peaks, TRAINS NTMs, 45 BITs with partners (Ch. 7).
- Writing rules for text and chart titles: connected paragraphs, no bullet lists, no en/em dashes (ranges as "2004 to
  2024"), no semicolon pivots or "not X but Y" lead-ins; every number must come from `data/derived/*.json`.
- Ch. 3, 4 and 9 rerun on BACI (Nov 12): services 20% to 48% of exports, transport RCA 4.5, chips RCA 4.6, finished pharma
  RCA 0.16 to 1.78 (so the case verdict changed: pharma built an export advantage but its value added and FDI stock fell).
  BACI 2017 chip value for SGP is a one-year outlier ($125bn), footnoted. Treemap RCA uses a goods + services base, the
  HS table a goods-only base; both are labelled.
- UI restyled as an illustrated poster (hero.svg 1965 vs 2024, Chewy / Patrick Hand SC / Nunito, ink outlines, chapter
  banners with icons in site/app/icons/).
- Length (Nov 13): cut from 80 screens / 9,000 words to 43 screens, about 30 screen heights at 1440 x 900 (26,700 px after the atlas moved to the cover)
  and 5,300 words; the Argentina page is about 21. Openers and full-width screens are compact, chart screens cap at
  680 px, the text column is 40% wide and holds up to 1,500 characters before a continuation screen. No separate "Implications"
  sections (the bridge sentence ends each chapter's last section), secondary charts live in "More" toggles, the GVC
  network and FDI explorer components are no longer placed, and the site opens on a one-minute summary
  (`data/derived/summary.md`, written by export_site_data.py; the intro opener is skipped). Keep new text inside this budget.
- Syllabus (Nov 13, `~/Downloads/syllabus_2026 (2).pdf`): 12 modules with readings but no lecture dates. Headings carry
  `{Module N · reading}` tags (filled module chip + reading chip): BoP 2, Ricardo/RCA 3, H-O 4, GVC/MNEs 6 (Fort 2017,
  Boehm et al. 2015), trade policy 7 (Conconi, MFN, US China trade war), gravity 8 (Feyrer), know-how and institutions 9
  (Juhász 2015, Nunn 2007). Final exam Dec 15.
- Still to do by members: check 2–3 numbers per chart; rewrite text in own words; link chapters to specific lectures;
  confirm case topic; download TI's CPI 2025 file; ask the professor the open questions in the appendix.
