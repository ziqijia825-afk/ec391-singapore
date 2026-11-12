# EC 391 Singapore: FDI (Ch. 6) and EDB case study, research notes

Compiled 2026-11-12. Every number was pulled from the source named next to it. SingStat figures were downloaded live from the Table Builder API on 2026-11-12. "S$" means Singapore dollars and "US$" means US dollars. Anything I could not verify is marked **unconfirmed**.

---

## A. FDI

### A1. SingStat Table Builder: working table IDs (all tested, all return JSON)

API pattern: `https://tablebuilder.singstat.gov.sg/api/table/tabledata/<ID>?limit=5000` returns JSON (`Data.row[].columns[] = {key: year, value}`).
Search endpoint: `https://tablebuilder.singstat.gov.sg/api/table/resourceid?keyword=direct%20investment&searchOption=all`
Human page: `https://tablebuilder.singstat.gov.sg/table/TS/<ID>` (has a CSV download button).
**API caveat:** some tables come back with rows truncated when `limit` is set (M451041 returned only 5 rows). Use `?search=<row text>` to get a single row, e.g. `M451041?search=Medicinal`.

| ID | Title | Years | Tested |
|---|---|---|---|
| M083791 | Principal Statistics of FDI in Singapore (stock, equity, inter-co lending, income, return %) | 1998–2024 | JSON OK |
| M083801 | FDI in Singapore by Source Economy (stock, year-end) | 1998–2024 | JSON OK |
| M083811 | FDI in Singapore by Source Economy and Industry (stock) | — | listed (not downloaded) |
| M084831 | FDI in Singapore by Detailed Industry (stock) | 1998–2024 | JSON OK |
| M085871 | FDI in Singapore by Component and Industry (stock) | — | JSON OK |
| M083011 / M084811 | Foreign Direct *Equity* Investment by Source Economy / Detailed Industry | — | JSON OK |
| M085801 | FDI in Singapore by Component (flows) | 2015–2025 | JSON OK |
| M085761 | FDI in Singapore by Source Economy (flows) | 2015–2025 | JSON OK |
| M085771 | FDI in Singapore by Industry (flows) | 2015–2025 | JSON OK |
| M085811 / M085821 | FDI flows by Source × Industry / Source × Component | — | listed |
| M083901 / M084001 / M084871 / M084911 | Income and Return on FDI by source / industry | — | listed |
| M082221 | Singapore's Direct Investment Abroad (DIA), stock | 1994–2024 | JSON OK |
| M084431 | DIA by Destination Economy (stock) | 1994–2024 | JSON OK |
| M084441 | DIA by Industry Abroad (stock) | 1994–2024 | JSON OK |
| M081971 / M082051 / M082121 / M085881 | DIA by destination × industry, etc. | — | M081971 JSON OK |
| M060231 / M060241 | International Investment Position, annual / quarterly | — | listed |
| M015731 | GDP at current prices by industry (for ratios) | to 2025 | JSON OK |

Source: SingStat Table Builder API, https://tablebuilder.singstat.gov.sg/api/table/resourceid?keyword=direct%20investment&searchOption=all. FDI stock tables were last updated 23/03/2026, flows 28/04/2026 and DIA 03–05/03/2026.

#### Inward FDI stock (S$ million; M083791 / M083801)

| Year | Total FDI stock | Equity | Net inter-company lending | Return on FDI % |
|---|---|---|---|---|
| 2004 | 276,819.2 | 253,618.4 | 23,200.8 | 16.8 |
| 2014 | 1,112,348.1 | 1,005,273.7 | 107,074.4 | 8.7 |
| 2023 | 2,858,847.9 | 2,613,088.9 | 245,759.0 | 12.3 |
| 2024 | 3,130,445.8 | 2,824,743.7 | 305,702.1 | 12.7 |
| 2025 (advance est.) | ≈3,506,000 (+9.9% y/y; equity 91.2%, lending 8.8%) | | | |

Sources: https://tablebuilder.singstat.gov.sg/api/table/tabledata/M083791. 2025: SingStat "Advance Estimates of FDI in Singapore (Stock as at end 2025)", published 30 Oct 2026, https://www.singstat.gov.sg/news/advance-estimates-of-foreign-direct-investment-in-singapore-stock-as-at-end-2025 (PDF https://www.singstat.gov.sg/files/0e288a68-ce6d-4d4e-b2b3-e455872f9881.pdf). That release gives only the top-10 share (74.0%) and names the USA, UK, Japan, Hong Kong and Mainland China among the top sources. The full 2025 source-economy breakdown is not yet in the Table Builder.

#### Top source economies, end-2024 (S$ million; share of S$3,130,445.8m) (M083801, immediate investor)

| Rank | Economy | Stock | Share |
|---|---|---|---|
| 1 | United States | 778,574.6 | 24.9% |
| 2 | Cayman Islands | 345,544.2 | 11.0% |
| 3 | British Virgin Islands | 202,735.1 | 6.5% |
| 4 | Japan | 196,064.0 | 6.3% |
| 5 | United Kingdom | 174,338.4 | 5.6% |
| 6 | Luxembourg | 143,636.1 | 4.6% |
| 7 | Bermuda | 122,410.6 | 3.9% |
| 8 | Hong Kong | 111,418.2 | 3.6% |
| 9 | Canada | 96,307.3 | 3.1% |
| 10 | Netherlands | 90,253.8 | 2.9% |
| 11 | Mainland China | 88,052.0 | 2.8% |
| 12 | Taiwan | 61,194.9 | 2.0% |
| (comparators) | Malaysia 49,401.2 (1.6%); Viet Nam 9.1 (≈0%) | | |

Regional totals for 2024: North America 874,881.4; Europe 791,074.9; South & Central America and Caribbean 716,479.5; Asia 678,355.6; EU-27 433,144.8; ASEAN 96,108.2. The four Caribbean financial centres (Cayman, BVI, Bermuda, Bahamas) together hold S$699.7bn, or 22.4%.
Source: https://tablebuilder.singstat.gov.sg/api/table/tabledata/M083801

#### Inward FDI stock by industry, end-2024 (S$ million; M084831)

| Industry | 2004 | 2014 | 2024 | Share 2024 |
|---|---|---|---|---|
| Finance & Insurance | 101,909.2 | 521,786.8 | 2,049,179.8 | 65.5% |
| of which Holding Companies | 79,886.6 | 447,717.9 | 1,733,909.0 | **55.4%** |
| Wholesale & Retail Trade | 43,285.4 | 237,988.9 | 418,217.9 | 13.4% |
| Manufacturing | 95,234.9 | 156,682.6 | 249,584.8 | 8.0% |
| of which Computer, Electronic & Optical | 31,732.0 | 58,167.0 | 88,463.1 | 2.8% |
| of which Semiconductor Devices | n.a. | 24,056.5 | 69,322.6 | 2.2% |
| of which Pharmaceutical & Biological Products | 31,864.9 | 14,800.9 | 9,779.2 | 0.3% |
| Professional, Admin & Support | 9,339.7 | 80,523.8 | 152,038.5 | 4.9% |
| Transportation & Storage | 13,090.0 | 37,845.7 | 115,331.3 | 3.7% |
| Information & Communications | 3,445.8 | 17,417.8 | 64,139.2 | 2.0% |
| Real Estate | 6,713.2 | 36,708.0 | 46,528.9 | 1.5% |

Source: https://tablebuilder.singstat.gov.sg/api/table/tabledata/M084831

#### FDI inflows (flows), S$ million (M085801 / M085771 / M085761)

| | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|
| Total inflows | 133,256.7 | 169,545.9 | 188,138.9 | 169,959.6 | 181,993.7 | 197,291.2 |
| Equity capital | 129,415.0 | 85,587.4 | 104,441.7 | 138,490.8 | 82,363.8 | 136,441.4 |
| Reinvested earnings | 11,592.0 | 74,528.9 | 76,448.1 | 2,492.8 | 81,795.9 | 65,851.8 |
| Net inter-co lending | -7,750.3 | 9,429.6 | 7,249.1 | 28,976.0 | 17,834.0 | -5,002.0 |
| Finance & Insurance | 56,286.7 | 67,144.3 | 65,501.7 | 188,437.3 | 134,569.7 | 126,111.6 |
| Manufacturing | 22,166.2 | 25,402.8 | 26,347.5 | -16,498.0 | -11,851.0 | 7,960.8 |
| From USA | 62,719.6 | 36,075.7 | 12,694.1 | 110,061.0 | 39,657.3 | 35,176.1 |

The 2025 release says inflows were S$197bn (+8.4%). The top five sources (USA, Netherlands, Ireland, Mainland China, UK) supplied 46.8%, and Finance & Insurance took 63.9% of inflows. (SingStat "FDI in Singapore (Flows) 2025", 28 Apr 2026, https://www.singstat.gov.sg/files/7ade01f6-3c35-498e-a2e4-423ba4c72d0f.pdf; data https://tablebuilder.singstat.gov.sg/api/table/tabledata/M085801)

#### FDI relative to GDP (my calculation: SingStat FDI ÷ SingStat nominal GDP, M015731)

| Year | Nominal GDP S$m | Inflow/GDP | Stock/GDP |
|---|---|---|---|
| 2004 | 194,433 | – | 142% |
| 2014 | 398,948 | – | 279% |
| 2019 | 514,052 | 25.9% | – |
| 2022 | 708,983 | 26.5% | – |
| 2023 | 686,398 | 24.8% | 417% |
| 2024 | 765,498 | 23.8% | 409% |
| 2025 | 789,529 | 25.0% | ≈444% (advance) |

Source GDP: https://tablebuilder.singstat.gov.sg/api/table/tabledata/M015731 (updated 10/02/2026)

#### Outward: Singapore's Direct Investment Abroad (DIA), stock S$ million

Total stock: 2004 179,633.9; 2014 651,222.0; 2023 1,535,752.5; 2024 1,652,795.5. Equity in 2024 was 1,516,280.1 and net inter-co lending 136,515.4. (https://tablebuilder.singstat.gov.sg/api/table/tabledata/M082221)

Top destinations at end-2024 (M084431): Mainland China 228,303.5 (13.8%); India 122,640.0 (7.4%); UK 109,827.4 (6.6%); Indonesia 104,285.4 (6.3%); Netherlands 103,285.6 (6.2%); Luxembourg 96,831.2 (5.9%); Hong Kong 91,335.8 (5.5%); Cayman 87,406.1 (5.3%); Australia 81,626.4 (4.9%); Malaysia 75,635.5 (4.6%); USA 65,984.6 (4.0%); Viet Nam 48,145.6 (2.9%). ASEAN took 300,857.3 (18.2%) and Asia 865,555.8 (52.4%). (https://tablebuilder.singstat.gov.sg/api/table/tabledata/M084431)

By industry abroad, 2024 (M084441): Finance & Insurance 834,213.1 (50.5%); Manufacturing 281,677.3 (17.0%); Wholesale & Retail 110,976.5 (6.7%); Real Estate 108,873.6 (6.6%); Info & Comms 83,870.7 (5.1%). (https://tablebuilder.singstat.gov.sg/api/table/tabledata/M084441)

### A2. Ultimate vs immediate investor

- SingStat records FDI by the **immediate** source economy, following BPM6. Its technical notes give the example that "if Country A invests in Singapore through Country B, it would be recorded as an investment from Country B (immediate) and not Country A (ultimate)." (SingStat Technical Notes, FDI in Singapore, https://www.singstat.gov.sg/files/4603e8e3-2291-424f-9c8d-b96962ef6a02.pdf). DIA is recorded by immediate destination in the same way (https://www.singstat.gov.sg/files/7d3d9820-3600-45fa-aab8-8cba749c05ee.pdf).
- **Unconfirmed:** I could not find any current SingStat table or publication of FDI by *ultimate* investing economy. Neither the Table Builder search for "ultimate" nor the "Our data explained" page (https://www.singstat.gov.sg/find-data/explore-data-themes/trade-investment/foreign-direct-investment/our-data-explained) has one. A 2013 Statistics Singapore Newsletter article might have covered it, but the link now returns an HTML page instead of the PDF (https://www.singstat.gov.sg/-/media/files/publications/trade_and_investment/ssnsep13-pg1-9.pdf).

### A3. UNCTAD World Investment Report: WIR 2026 is out (released 7 July 2026)

Annex tables (Excel), all downloaded and parsed:
- Tab 1 inflows: https://unctad.org/system/files/non-official-document/wir26_tab01.xlsx
- Tab 2 outflows: …/wir26_tab02.xlsx · Tab 3 inward stock: …/wir26_tab03.xlsx · Tab 4 outward stock: …/wir26_tab04.xlsx
- Tab 5 value of net cross-border M&A sales: …/wir26_tab05.xlsx · Tab 7 number of net M&A sales: …/wir26_tab07.xlsx
- Tab 14 value of announced greenfield projects by destination: …/wir26_tab14.xlsx · Tab 17 number of greenfield projects by destination: …/wir26_tab17.xlsx
- WIR 2025 set: same names with `wir25_tabNN.xlsx`.
(Index page: https://unctad.org/topic/investment/world-investment-report). UNCTAD notes that its data exclude Caribbean financial centres and SPEs **in reporting countries**.

**FDI inflows, US$ million (WIR 2026 Annex Table 1)**

| | 2004 | 2014 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Singapore | 22,325 | 73,287 | 97,684 | 126,199 | 136,464 | 126,574 | 136,199 | 150,898 |
| Hong Kong | 29,154 | 113,038 | 73,714 | 140,186 | 109,685 | 122,947 | 137,923 | 116,475 |
| Malaysia | 4,624 | 10,877 | 7,813 | 12,173 | 17,136 | 8,468 | 10,202 | 15,390 |
| Viet Nam | 1,610 | 9,200 | 16,120 | 15,660 | 17,900 | 18,500 | 20,170 | 20,350 |
| World | 699,193 | 1,468,245 | 1,652,463 | 1,777,123 | 1,437,432 | 1,320,858 | 1,531,691 | 1,624,259 |

- **Rank:** In 2025 Singapore was the **2nd** largest recipient, after the US (277,300) and ahead of Hong Kong (116,475) and China (104,659). On the revised WIR 2026 data, Singapore was **3rd** in 2024, behind the US (283,968) and Hong Kong (137,923). WIR **2025** had first reported Singapore's 2024 inflow as 143,352, which ranked **2nd** at the time (https://unctad.org/system/files/non-official-document/wir25_tab01.xlsx).
- WIR 2026 text: "Other major recipients included Singapore, Hong Kong (China) and China, in that order". It also cautions that rank changes "are often driven by a limited number of transactions, particularly in financial centres and investment hubs, rather than broad-based changes in productive capacity." (WIR 2026 Ch. I, https://unctad.org/system/files/official-document/wir2026_ch01_en.pdf). The Asia regional fact sheet says Singapore's ranking reflects "its role as a headquarters location and financial hub". It also reports 2025 growth of +51% for Malaysia and +1% for Viet Nam, and lists Singapore among Asia's top-10 home economies (https://unctad.org/system/files/non-official-document/wir2026-regional_trends_developing_asia_en.pdf).

**Outflows, stocks, M&A and greenfield (US$ million; WIR 2026 annex)**

| Indicator | Singapore 2024 | Singapore 2025 | HK 2025 | Malaysia 2025 | Viet Nam 2025 |
|---|---|---|---|---|---|
| FDI outflows (T2) | 55,257 | 94,202 | 95,326 | 2,901 | 680 |
| Inward stock (T3) | 2,230,874 | 3,169,240* | 2,587,370 | 268,146 | 269,491 |
| Outward stock (T4) | 1,174,122 | 2,068,481* | 2,438,239 | 145,263 | 14,295 |
| Net cross-border M&A sales, value (T5) | 6,111 | 3,990 | 2,585 | 2,301 | 854 |
| Net M&A sales, number (T7) | 87 | 100 | 45 | 48 | 33 |
| Announced greenfield, value (T14) | 23,012 | 17,512 | 4,953 | 22,156 | 24,304 |
| Announced greenfield, number (T17) | 451 | 354 | 147 | 236 | 249 |

Same indicators for 2024 for the comparators: greenfield value HK 4,214 / MY 29,168 / VN 22,480; greenfield number HK 162 / MY 236 / VN 335; M&A value HK 3,485 / MY 1,079 / VN 129. Singapore's M&A sales spiked at 46,138 in 2021. Viet Nam shows 24,955 in 2023 (an outlier in the data).
\*Singapore's stock jumps between 2024 and 2025 (+42% inward, +76% outward). That jump is far larger than SingStat's +9.9% (end-2025 S$3,506bn is roughly US$2.7tn at about 1.29 S$/US$, my rough conversion). It looks like a source or method break in UNCTAD's series. **Unconfirmed why.** Use SingStat for stock levels.

### A4. EDB Year-in-Review (investment commitments)

| Indicator (S$) | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| FAI commitments (S$m) | 9,389 | 9,449 | 10,873 | 15,184 | 17,171 | 11,796 | 22,490 | 12,660 | 13,451 | 14,159 |
| TBE commitments (S$m) | 8,270 | 6,533 | 6,170 | 9,020 | 6,815 | 5,151 | 6,209 | 8,909 | 8,369 | 8,891 |
| Value-added expected (S$m) | 12,826 | 17,243 | 13,630 | 29,434 | 31,196 | 16,800 | 20,561 | 26,690 | 23,523 | 17,980 |
| Jobs expected | 20,075 | 22,481 | 17,417 | 32,814 | 19,352 | 17,376 | 17,113 | 20,045 | 18,737 | 15,704 |

- 2025 FAI by industry: Electronics 33.0% (S$4,677m), Biomedical Manufacturing 30.8% (S$4,363m), Chemicals 9.1%, R&D 6.8%, Precision Eng. 6.3%. Manufacturing sub-total was S$12,136m (about S$12.1bn of S$14.2bn).
- 2024 FAI by industry: Electronics **57.0%**, Biomedical 16.5%, HQ & Professional Services 8.4%, R&D 7.8%.
- FAI by source in 2025: Europe 24.9%, **China 20.6%**, US 17.3%, Japan 11.4%, Others 23.2%, Singapore 2.5%. In 2024: US **55.5%**, Europe 24.8%, Singapore 11.6%, Japan 3.5%, China 2.5%.
- 2025 jobs by sector: Services 40%, Manufacturing 37%, R&D & Innovation 23%. About two-thirds pay more than S$5,000 gross per month. Most TBE (S$5,553m) came from HQ & Professional Services.
- Definitions: FAI is incremental capital investment in facilities, equipment and machinery. TBE is incremental annual operating expenditure excluding depreciation. These are **commitments realised over about 5 years, not FDI** (see SingStat infographic https://www.singstat.gov.sg/-/media/files/visualising_data/infographics/trade_and_investment/fdi-fai-commitments.ashx).
Sources: EDB YIR 2025 media release, 9 Feb 2026, https://www.edb.gov.sg/content/dam/edb-en/about-edb/media-releases/news/edb-year-2025-in-review/EDB%20YIR%202025%20Media%20Release.pdf. 2024 release: https://www.edb.gov.sg/content/dam/edb-en/about-edb/media-releases/news/edb-year-2024-in-review/EDB%20YIR%202024%20Media%20Release.pdf

### A5. Regional headquarters

- EDB: Singapore "is home to about 4,200 regional headquarters", citing an EY report from 2019 (EDB article dated 18 Apr 2022, https://www.edb.gov.sg/en/news-and-insights/futuristic-workspace-spore-a-hub-for-corporate-headquarters). The reasons it gives are ease of doing business, political stability, access to talent, world-class infrastructure and rule of law. **No newer official count found (unconfirmed for 2024–26).**
- EDB HQ page: calls Singapore the "most popular regional headquarter destination in Asia". It cites company setup in as little as one day, links to over 170 cities via 100 airlines, rule of law, and ecosystem access (https://www.edb.gov.sg/en/industries/headquarters).
- EDB YIR 2025: Companies from China, the US and Europe "continued to anchor HQs with global mandates". Tech firms were the largest contributor to HQ investments (YIR 2025 PDF above). PC/DEI awards can come with "International Headquarters Award" status (see B8).

### A6. Pass-through / phantom FDI (interpreting inflows of about 25% of GDP)

- IMF F&D (Damgaard, Elkjaer, Johannesen, 1 Sept 2019): "phantom FDI" passes through empty shells (SPEs) that do holding, intrafirm financing or intangible management. It rose from about 30% to almost 40% of global FDI. Ten economies host more than 85% of it: Luxembourg, the Netherlands, Hong Kong SAR, BVI, Bermuda, **Singapore**, Cayman, Switzerland, Ireland and Mauritius. https://www.imf.org/en/Publications/fandd/issues/2019/09/the-rise-of-phantom-FDI-in-tax-havens-damgaard (underlying paper: IMF WP/19/274 "What Is Real and What Is Not in the Global FDI Network?").
- SingStat's own data are consistent with this. **Holding companies hold 55.4% of the inward FDI stock** (S$1.73tn of S$3.13tn, 2024), and Caribbean financial centres plus Luxembourg/Netherlands appear among the top-10 sources (tables above). The 2025 inflow mix was Finance & Insurance 63.9% and manufacturing about 4%.
- UNCTAD WIR 2026: rank swings in financial centres and investment hubs reflect "a limited number of transactions" (Ch. I, link above).
- IMF Singapore Selected Issues 2025 (Country Report 25/193, June 2025): "Hong Kong SAR and Singapore play a much more important role in this [FDI] network than in the trade network, likely due to their nature as financial centers". It also says "about half of all FDI coming to Singapore is from either Europe or the United States", while outbound FDI goes mostly to Asia. https://www.imf.org/en/Publications/CR/Issues/2025/07/16/Singapore-Selected-Issues-568648
- **Unconfirmed:** Whether Singapore separately identifies SPEs in its BOP/FDI. I found no SingStat SPE series. An OECD-specific note on Singapore was not found.

---

## B. Case study: semiconductors and pharmaceuticals

### B7. Timeline

| Year | Event | Source |
|---|---|---|
| 1961 | UN (Winsemius) mission recommends creating "over 200,000 jobs in a decade". Jurong industrial estate begins. EDB set up 1961 (founding date 1 Aug 1961 **unconfirmed on an official page**). | EDB "Made in Singapore: 60 years of manufacturing", 11 Aug 2025, https://www.edb.gov.sg/en/business-insights/insights/made-in-singapore-60-years-of-manufacturing.html |
| 1968 | EDB "breakthrough" with National Semiconductor, "running within two weeks". Fairchild, Texas Instruments, HP and GE follow. | same EDB page; A*STAR feature 16 Jun 2025, https://www.a-star.edu.sg/news/features/singapore-semiconductor-rise-ai-chip-wars |
| 1968–70 | Exact TI arrival year: sources conflict (1968 vs 1969/1970). **Treat as "late 1960s".** | NTU microelectronics blog https://blogs.ntu.edu.sg/microelectronics/?p=125 |
| 1987 | Chartered Semiconductor incorporated 16 Nov 1987. It was a JV of Singapore Technologies, Sierra Semiconductor and National Semiconductor, formed with EDB support, and gave Singapore its first wafer fab. GlobalFoundries acquired it in 2009 for US$1.8bn plus US$2.2bn of debt. | SGX https://links.sgx.com/1.0.0/corporate-information/1525; A*STAR feature (above) |
| 1991 | TECH Semiconductor (TI/EDB/Canon/HP JV DRAM fab): **unconfirmed** (no source found) | — |
| 1995 | Jurong Island reclamation begins (completed 2009, 3,000 ha) | EDB 60-years page |
| 1997 | Tuas Biomedical Park opens (370 ha prepared land) | Cambridge CIIP report (below) |
| June 2000 | Biomedical Sciences (BMS) Initiative launched. Phase 1 2000–05 (basic research infrastructure), Phase 2 2006–10 (translational). Initially US$1bn allocated for Biopolis, institutes and R&D co-funding. Bio*One Capital ran a S$1bn Biomedical Sciences Investment Fund. **Exact official phase budgets unconfirmed.** | Killen, Palladino & Gonzalez, Cambridge CIIP, 19 Feb 2021, https://www.ciip.group.cam.ac.uk/wp-content/uploads/2021/02/2021-02-19-SBS.pdf |
| Late 2003 | Biopolis (one-north) officially launched (Zaha Hadid master plan) | CIIP report |
| 2003 | Pfizer starts API manufacturing at Tuas (Pfizer in SG since 1964) | Pharmaboardroom / FiercePharma via search; **secondary** |
| 2004 | Novartis Institute for Tropical Diseases set up at Biopolis | CIIP report |
| 2006–08 | Genentech, GSK, Lonza and Novartis announce 5 biologics plants worth about US$1.5bn (2008 EDB release) | quoted in ISPE/EDB results; **secondary** |
| 2009 | GlobalFoundries acquires Chartered | A*STAR feature |
| Dec 2020 / 2024 | RIE2025: S$25bn announced 2020, topped up by S$3bn in Budget 2024 to S$28bn (Apr 2021–Mar 2026) | MOF Budget 2024; EDB https://www.edb.gov.sg/en/news-and-insights/singapore-invests-s37-billion-in-rie2030-research-plan-semiconductors-ageing-among-focus-areas |
| Apr 2021 | Sanofi announces about S$638m Evolutive Vaccine Facility (Tuas). Later cost and opening reported as about US$590–595m; **opening date unconfirmed** | https://www.fiercepharma.com/pharma/sanofi-opens-590m-modular-vaccine-biologics-plant-singapore |
| Jun 2021 → 12 Sep 2023 | GlobalFoundries US$4bn fab expansion at Woodlands: groundbreaking 2021, opened 12 Sep 2023. Adds 450,000 300mm wafers a year (campus about 1.5m a year) and about 1,000 jobs. | EDB https://www.edb.gov.sg/en/news-and-insights/press-release/globalfoundries-opens-us4-billion-expansion-facility-in-singapore |
| Oct 2021 → 12 Jun 2024 | Siltronic new 300mm fab (Tampines): groundbreaking Oct 2021, first wafers 7 Nov 2023, opened 12 Jun 2024. About 600 jobs. Cost about US$2.2bn per a secondary source (**€2bn unconfirmed**). A*STAR feature says "S$3 billion". | EDB https://www.edb.gov.sg/en/news-and-insights/siltronic-breaks-ground-for-a-new-fab-in-singapore |
| Feb 2022 → Apr 2025 | UMC 22/28nm fab expansion (Fab12i P3) at Pasir Ris: US$5bn, 30,000 wafers/month first phase, about 700 jobs. First tool-in 21 May 2024, opening ceremony 1 Apr 2025, volume production 2026. | EDB https://www.edb.gov.sg/en/news-and-insights/umc-announces-new-22nm-wafer-fab-in-singapore; MTI speech https://www.mti.gov.sg/newsroom/speech-by-dpm-and-minister-for-trade-and-industry-gan-kim-yong-at-the-united-microelectronics-corporation--umc--fab-expansion-opening-ceremony/ |
| May 2024 → 7 Nov 2024 | AstraZeneca US$1.5bn ADC plant (Tuas South): announced 20 May 2024 (**not March 2025**), groundbreaking 7 Nov 2024, ready by 2029, more than 800 jobs | https://www.astrazeneca.com/country-sites/singapore/press-releases/astrazeneca-to-manufacture-adcs-in-singapore.html |
| 5 Jun 2024 → Dec 2024 | VSMC (VIS 60% / NXP 40%) 300mm fab, Tampines: initial build US$7.8bn, production 2027, 55,000 wafers/month by 2029, TSMC-licensed process. A*STAR puts it at about S$10.5bn; groundbreaking Dec 2024 | NXP https://www.nxp.com/company/about-nxp/newsroom/NW-VSMC |
| 2024 | AbbVie US$223m biologics expansion (more than US$740m at the site over a decade); GSK US$343m (2023) Hep B antigen expansion | EDB https://www.edb.gov.sg/en/news-and-insights/abbvie-expands-biologics-manufacturing-capacity-with-a-223mil-investment-in-singapore |
| 8 Jan 2025 | Micron breaks ground on HBM advanced-packaging plant: about US$7bn, 1,400 jobs rising to about 3,000, operations "scheduled to begin in 2026". **Actual start unconfirmed.** | EDB https://www.edb.gov.sg/en/news-and-insights/micron-breaks-ground-on-7billion-hbm-facility-in-singapore |
| 5 Dec 2025 | RIE2030: S$37bn (+32% over RIE2025's S$28bn, about 1% of GDP). New S$3bn for RIE Flagships and Grand Challenges. First flagship: semiconductors (S$800m, 2026–30). | EDB RIE2030 article (above); EDB SG Semiconductor release 25 Sep 2026 https://www.edb.gov.sg/en/news-and-insights/singapore-announces-sg-semiconductor-to-strengthen-its-role-in-the-global-semiconductor-ecosystem |
| Jun 2026 | Applied Materials opens S$600m (about US$500m) Tampines campus (announced 2023), about 1,000 jobs, "Singapore 2030" plan | EDB https://www.edb.gov.sg/en/news-and-insights/applied-materials-expands-singapore-manufacturing-for-ai; TrendForce 11 Jun 2026 |
| — | Soitec, Amgen, Lonza: **not verified this round** | — |

**Global share (official):** "one in ten global chip output and one-fifth of global semiconductor manufacturing equipment production" (EDB, 25 Sep 2026, link above). Minister of State Alvin Tan, 16 Apr 2026: semiconductors are "33% of our manufacturing output" and "6% of our GDP" (https://www.meti.gov.sg/newsroom/speech-by-minister-of-state-alvin-tan-at-the-ssia-semiconductor-business-connect-2026/; note mti.gov.sg now redirects to meti.gov.sg, which names the ministry "Ministry of Energy, Trade and Industry"). A*STAR feature: in 2023 the industry was nearly 6% of GDP and employed more than 35,000 people.

### B8. Incentives and tax

- **Headline corporate income tax rate: 17%** since YA2010, for local and foreign companies (IRAS, https://www.iras.gov.sg/taxes/corporate-income-tax/basics-of-corporate-income-tax/basic-guide-to-corporate-income-tax-for-companies).
- **Pioneer Certificate (PC) / Development & Expansion Incentive (DEI):** Under the Economic Expansion Incentives (Relief from Income Tax) Act, PC gives tax exemption and DEI a concessionary 5% or 10% rate on qualifying income. The incentive period is **5 years** and extensions are possible. PC requires technology "substantially more advanced than the average prevailing in Singapore" and new, pioneering activities. Manufacturing projects must commit FAI. HQ activities qualify, with International HQ Award status available. (EDB PC & DEI brochure, https://www.edb.gov.sg/content/dam/edb-zh/downloads/brochures/PC%20and%20DEI%20Brochure.pdf)
- **DEI (Manufacturing) v3.0:** 5%, 10% or **15%** rate on income above a 36-month base, per 5-year period. Conditions: 5% needs at least S$13m extra FAI and 30 skilled jobs; 10% needs S$7m and 20 jobs; 15% needs S$5m and 13 jobs. The 15% tier is the post-Pillar-Two tier. (EDB factsheet, https://www.edb.gov.sg/content/dam/edb-en/how-we-help/incentive-and-schemes/factsheets/DEI(Mfg)%20Factsheet.pdf)
- **Refundable Investment Credit (RIC):** Introduced in Budget 2024, with legal basis in s.93B of the Income Tax Act 1947 and the Income Tax (Refundable Investment Credits) Regulations 2025. It covers up to 50% of each qualifying expenditure category, with a qualifying period of up to 10 years. Unused credits are **paid in cash within 4 years** of meeting conditions. EDB and EnterpriseSG administer it. It can offset CIT and also DTT and MTT. Qualifying activities include new productive capacity, HQ, R&D, commodity trading and decarbonisation. (IRAS RIC page, https://www.iras.gov.sg/schemes/disbursement-schemes/refundable-investment-credit-(ric)). By design it is a "qualified refundable tax credit" under GloBE (EY 2025, https://www.ey.com/en_sg/technical/you-and-the-taxman/singapore-refundable-investment-credit-shaping-the-future-of-foreign-direct-investment).
- **Pillar Two:** The Multinational Enterprise (Minimum Tax) Act 2024 has been in operation since 1 Jan 2025 (gazetted 30 Dec 2024). It introduces the **Multinational Enterprise Top-up Tax (MTT)**, an IIR on low-taxed overseas entities, and the **Domestic Top-up Tax (DTT)** on low-taxed Singapore entities. Both apply to financial years starting on or after 1 Jan 2025 for groups with revenue of at least €750m in 2 of the 4 preceding years, at a 15% minimum ETR. (IRAS GloBE/DTT page, https://www.iras.gov.sg/taxes/pillar-2-top-up-taxes/global-anti-base-erosion-(globe)-rules-and-domestic-top-up-tax-(dtt); Allen & Gledhill https://www.allenandgledhill.com/sg/publication/articles/29841/multinational-enterprise-minimum-tax-act-2024-in-operation-on-1-january-2025). IRAS e-Tax Guide on MTT/DTT: 1st ed. 31 Dec 2024, 2nd ed. 7 Jan 2026 (https://www.iras.gov.sg/docs/default-source/e-tax/e-tax-guide-mtt-and-dtt.pdf). Note that the brief's term "Multinational Enterprise Minimum Tax" is the name of the **Act**; the tax itself is called "MTT".

### B9. Manufacturing statistics (EDB Census of Manufacturing Activities via SingStat; 2025 = preliminary)

Shares of total manufacturing (my calculation from S$m values):

| Cluster | Output 2004 | Output 2014 | Output 2024 | Output 2025p | VA 2004 | VA 2014 | VA 2024 | VA 2025p |
|---|---|---|---|---|---|---|---|---|
| Electronics | 38.7% | 27.1% | 42.2% | **45.6%** | 31.7% | 28.2% | 40.1% | **43.2%** |
| of which Semiconductors | 15.2% | 16.0% | 31.8% | **33.4%** | 15.7% | 17.8% | 32.8% | **34.6%** |
| Biomedical | 9.1% | 9.2% | 7.6% | 7.7% | 21.2% | 19.4% | 11.1% | 12.3% |
| of which Pharmaceuticals | 8.0% | 5.5% | 2.8% | 3.2% | 19.3% | 15.0% | 3.7% | 5.5% |
| Chemicals | 27.9% | 33.4% | 22.2% | 18.4% | 16.1% | 9.2% | 15.0% | 11.5% |
| Precision Eng. | 10.4% | 10.6% | 12.1% | 11.8% | 13.1% | 14.1% | 15.2% | 15.5% |

Levels for 2025p: total manufacturing output S$479.1bn, VA S$132.8bn, employment 350,764. Semiconductors had output S$160.2bn, VA S$46.0bn and 34,451 workers. Biomedical had output S$36.9bn, VA S$16.4bn and 26,259 workers. Manufacturing was 17.4% of 2025 GDP (S$137.6bn of S$789.5bn, M015731).
Tables: Output M355171, VA M355181, Employment M355151 (datasource "Economic Development Board", updated 16/06/2026): https://tablebuilder.singstat.gov.sg/api/table/tabledata/M355171 (also M355181, M355151).
Caveat: the CIIP report puts biomedical at 20% of manufacturing VA in 2019 (S$19.57bn). The current SingStat series gives S$12.4bn for 2019, so the series has been revised or reclassified (SSIC 2025). **Use SingStat.**

**NODX** (Enterprise Singapore data via SingStat; annual = sum of months; S$bn)

| | 2004 | 2014 | 2024 | 2025 |
|---|---|---|---|---|
| Total NODX (M451301) | 142.90 | 162.79 | 173.60 | 182.02 |
| Electronic NODX (M450981) | 77.02 (53.9%) | 48.27 (29.7%) | 39.19 (22.6%) | 44.19 (**24.3%**) |
| Integrated circuits | 21.98 (15.4%) | 21.15 (13.0%) | 19.39 (11.2%) | 22.55 (**12.4%**) |
| Medicinal & pharmaceutical products, SITC 54 domestic exports (M451041) | 1.19 | 8.97 | 7.82 (4.5%) | 7.81 (**4.3%**) |

Check: from these series, electronic NODX grew +12.7% and total NODX +4.8% in 2025, which matches the Enterprise Singapore 2025 review (10 Feb 2026). That review reports NODX +4.8% (2024 +0.2%), electronics +12.7%, ICs +16.3%, PCs +65.1%, pharmaceuticals +10.6% (4Q25 +142.4%) (https://www.enterprisesg.gov.sg/-/media/esg/files/media-centre/media-releases/2026/february/mr00626_review-of-2025-trade-performance.pdf).
Caveat: Enterprise Singapore's "pharmaceuticals" NODX category (+10.6%) is **not** the same as SITC 54 (flat). Much pharma output (APIs) is classified under organic chemicals (SITC 51), so the SITC-54 share understates pharma. **ESG's pharma level and share of NODX are unconfirmed.** Series links: https://tablebuilder.singstat.gov.sg/api/table/tabledata/M450981, https://tablebuilder.singstat.gov.sg/api/table/tabledata/M451301, https://tablebuilder.singstat.gov.sg/api/table/tabledata/M451041?search=Medicinal

### B10. Evaluations and critiques

- **Young (1992),** "A Tale of Two Cities: Factor Accumulation and Technical Change in Hong Kong and Singapore", *NBER Macroeconomics Annual* 7: 13–54. TFP growth contributed substantially in Hong Kong, but in Singapore "next to nil"; growth there came from factor accumulation and government-targeted structural change. Krugman's discussion is in the same volume. https://www.nber.org/chapters/c10990
- **Cambridge CIIP / Gatsby (Killen, Palladino, Gonzalez, 19 Feb 2021),** "Singapore's biomedical cluster":
  - Output and jobs targets were met. The early S$12bn output target for 2005 was hit a year early, and output reached S$18bn in 2005 and S$23bn in 2006 (10,000 jobs). The 2015 target was S$25bn and 15,000 jobs; actual was S$28bn and about 19,000 jobs. In 2019 there were about 24,000 jobs and S$36bn of output.
  - There were no biologics plants in 2000 and about 18 by 2019. Biomedical manufacturing VA grew at a 9% CAGR over 2000–19, against 5% for all manufacturing.
  - **Critiques:** The GERD target of 3% of GDP by 2010 was missed (it peaked at 2.6% in 2008 and fell to 1.9% by 2010). The biomedical public-to-private R&D ratio averaged only 1:0.52. By 2016 there were "only a few" spin-offs and a couple of novel diagnostics, so the cluster was strong in manufacturing but weaker in innovation.
  - https://www.ciip.group.cam.ac.uk/wp-content/uploads/2021/02/2021-02-19-SBS.pdf
- **Finegold, Wong & Cheah (2004),** "Adapting a FDI strategy to the knowledge economy: the case of Singapore's emerging biotechnology cluster", *European Planning Studies* 12: 921–942, doi 10.1080/0965431042000267830. I did not read the full text, so its **findings are unconfirmed**.
- **Lim & Gregory (2004),** "Singapore's biomedical science sector development strategy: is it sustainable?", *Journal of Commercial Biotechnology* (cited in the CIIP report; not read).
- **IMF Selected Issues 2025:** Singapore's FDI network centrality is driven by its financial-centre role (see A6).
- **EDB's own caveat (YIR 2025):** "job creation will become more challenging". Jobs committed fell to 15,704, a 10-year low in the series. Expected VA fell from S$23.5bn in 2024 to S$18.0bn in 2025, even though FAI rose.
- **Not found / unconfirmed:** a World Bank evaluation specific to Singapore's FDI strategy; a quantitative study of MNC–local-firm linkages. EDB itself reports 19 MNC–local enterprise partnership projects in 2025, which is a policy response to the linkage concern.

### B11. Course framing

- **Export-platform FDI:** Ekholm, Forslid & Markusen (2007), "Export-Platform Foreign Direct Investment", *JEEA* 5(4): 776–795 (NBER WP 9517). https://www.nber.org/papers/w9517. This fits Singapore well. Manufacturing FDI there serves world markets, not Singapore's small home market: semiconductors are about 33% of manufacturing output, and Singapore supplies about 10% of world chips (EDB).
- **Vertical FDI:** the assembly-and-test plants of 1968–1970s (NatSemi, TI, Fairchild) were offshore stages of US chip value chains (EDB 60-years page; A*STAR feature).
- **Agglomeration and clusters:** Government-built parks are a deliberate cluster policy: Jurong Island (chemicals, more than 100 firms by 2014), Tuas Biomedical Park, Biopolis, and the Woodlands, Tampines and Pasir Ris wafer fab parks. The IMF finds that FDI follows prior trade links in a gravity model (IMF SI 2025).
- **Horizontal / market-seeking:** the HQ and wholesale-trade FDI stock (13.4%) and the 2025 China surge in FAI share (20.6%) fit the YIR's "launchpad for regional expansion" framing better than a home-market motive.
- I found no official Singapore source that uses the vertical/horizontal terminology. These labels are the student's own framing on top of the sources.
