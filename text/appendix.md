# Appendix: sources and methods

## Data sources

Every chart and table was built by the team from raw files downloaded by the scripts in the repository (`scripts/fetch_*.py`) and logged in `data/SOURCES.md`, accessed in November 2026.

| Source | Type | Used for | Access |
| --- | --- | --- | --- |
| World Bank, World Development Indicators | IGO | GDP, growth, inflation, population, literacy and education, trade, balance of payments including services exports by category and investment income, FDI flows, tariffs (from WITS/UNCTAD TRAINS), LPI, resource rents, legacy Doing Business rank | [API](https://api.worldbank.org/v2), `fetch_worldbank.py` |
| World Bank, Worldwide Governance Indicators (2025 release) | IGO | Six governance scores (0 to 100) | WDI API, `fetch_worldbank.py` |
| World Bank, Business Ready (B-READY) 2025 | IGO | Ten topic scores and three pillars | WDI API, `fetch_worldbank.py` |
| UNDP, Human Development Report 2025 | UN | HDI, schooling | [CSV](https://hdr.undp.org/data-center/documentation-and-downloads), `fetch_other.py` |
| Transparency International, Corruption Perceptions Index 2012 to 2024 | NGO (required by the guidelines) | CPI scores | via [Our World in Data](https://ourworldindata.org/grapher/ti-corruption-perception-index), `fetch_other.py` |
| Singapore Department of Statistics, Table Builder | Government | Re-exports, Gini, FDI stock by source and industry, direct investment abroad, GDP in S$, manufacturing census | [API](https://tablebuilder.singstat.gov.sg), `fetch_singstat.py` |
| CEPII BACI (HS 1992, V202601) | Research centre (harmonised UN Comtrade) | Exports and imports by HS chapter and product, bilateral trade, for RCA, export structure, concentration and the case study | [CEPII](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37), `process_baci.py` |
| UN Comtrade | UN | Singapore's reported exports and imports by partner, every year 2004 to 2024; HS chapter titles | [API](https://comtradeplus.un.org), `fetch_comtrade.py` |
| OECD, Trade in Value Added, 2025 edition | IGO | Foreign and domestic value added in exports, origin of value added | [SDMX API](https://sdmx.oecd.org), `fetch_tiva.py` |
| Penn World Table 11.0 | University (Groningen Growth and Development Centre) | Capital stock, employment, human capital | [Dataverse](https://doi.org/10.34894/FABVLR), `fetch_other.py` |
| UNCTAD, World Investment Report 2026 annex tables | UN | FDI inflows, inward and outward FDI stocks for ranks, greenfield projects, cross-border M&A | [Annex tables](https://unctad.org/topic/investment/world-investment-report), `fetch_other.py` |
| WTO Tariff Profiles | IGO | MFN averages, duty-free lines, tariff peaks and maximum duties for Singapore and peers | [WTO](https://www.wto.org/english/res_e/statis_e/tariff_profiles_list_e.htm), `fetch_other.py` |
| UNCTAD TRAINS via World Bank WITS | UN / IGO | Non-tariff measures by type and sector | [WITS](https://wits.worldbank.org/tariff/non-tariff-measures/en/country/SGP), `fetch_wits_ntm.py` |
| Enterprise Singapore, WTO RTA database, METI | Government / IGO | List of free trade agreements | `data/raw/manual/sg_fta_list.csv` |
| Ministry of Energy, Trade and Industry (METI) | Government | Bilateral investment treaties in force and partners | `data/raw/manual/sg_bit_list.csv` |
| Natural Earth; geoBoundaries (CC BY 4.0) | Public domain / open data | Country boundaries for the maps (not statistics) | `fetch_geo.py` |
| WTO, Singapore Customs, IRAS, EDB, NLB, MOE | Government / IGO | Facts on membership, tariffs, incentives, taxes, history and education | linked in the text |
| SingStat Population Trends 2026; data.gov.sg land area series | Government | Population by residency, land area in 1965 and 2026 | linked in Chapter 1 |
| Associated Press via PBS | News | Result of the general election of May 2025 | linked in Chapter 1 |

**Limitations.** Singapore's role as an entrepôt and financial centre complicates almost every statistic, so we pair reported exports with BACI and value added data and read FDI as recorded by immediate investor. There are no World Bank poverty or Gini data for Singapore, and TiVA and tariff data end in 2022.

Three gaps remain. Transparency International's 2025 results file must be downloaded by hand to replace the Our World in Data copy, Singapore publishes no FDI by ultimate investor, and the Chapter 9 test would be firmer with plant level data on local suppliers.

## Methods

**Every method in one place.** Ranks, RCA, gravity, concentration, value chains, the Heckscher Ohlin check and the difference in differences are defined below.

<details class="more" markdown="1">
<summary>The formulas and estimation details</summary>

**Ranks.** For every indicator we rank all economies with data in the same year, excluding the World Bank's aggregates. Rank 1 is the highest value unless stated (for inflation and tariffs the lowest), and the regional rank is within the World Bank's East Asia and Pacific region.

**Revealed comparative advantage.** RCA = (X<sub>ik</sub> / X<sub>i</sub>) ÷ (X<sub>wk</sub> / X<sub>w</sub>), with goods from CEPII BACI and services from the World Bank's balance of payments. Sector RCAs use goods and services, HS chapter and product RCAs goods only.

**Gravity.** OLS of ln(Singapore's exports to partner *j*, 2024) on ln(GDP of *j*) and ln(distance between capitals), with robust (HC1) standard errors.

**Concentration.** Herfindahl Hirschman index HHI = Σ s<sub>j</sub><sup>2</sup>, where s<sub>j</sub> is partner *j*'s share of exports.

**Value chains.** Backward participation = foreign value added in gross exports ÷ gross exports. Forward participation = value added in other economies' exports ÷ own gross exports. Position = ln(1 + forward) − ln(1 + backward) (Koopman and coauthors, 2010).

**Heckscher Ohlin check.** For 154 economies exporting over $1bn in 2023, OLS of ln(RCA in HS 28 to 30, 84, 85, 87, 88 and 90 ÷ RCA in HS 42, 61, 62, 64, 94 and 95) on ln(capital per worker, PWT), robust errors.

**Difference in differences.** The Chapter 9 equation for Singapore, Malaysia and Hong Kong SAR, chemical chapters HS 28 to 38, 1995 to 2024, with robust errors; the event study uses one dummy per year, 1999 = 0.

**Shared sector table.** Chapters 3 to 6 map trade, value added and FDI data to one approximate set of sectors.

<!-- include: data/derived/sector_table.md -->

</details>

## References

<details class="more" markdown="1">
<summary>Full reference list</summary>

Boehm, C.E., A. Flaaen and N. Pandalai Nayar (2015), "The role of global supply chains in the transmission of shocks: firm-level evidence from the 2011 Tohoku earthquake", VoxEU, CEPR, 9 January, published as "Input linkages and the transmission of shocks", *Review of Economics and Statistics* 101(1), 2019, 60 to 75. Conconi, P., M. García Santana, L. Puccio and R. Venturini (2016), "The perverse effect of preferential rules of origins", VoxEU, CEPR, 16 March. Damgaard, J., T. Elkjaer and N. Johannesen (2019), "The rise of phantom investments", IMF *Finance and Development*, September. Ekholm, K., R. Forslid and J. Markusen (2007), "Export-platform foreign direct investment", *Journal of the European Economic Association* 5(4), 776 to 795. Feyrer, J. (2009), "The 1967 to 1975 Suez Canal closure: lessons for trade and the trade income link", VoxEU, CEPR, 23 December. Fort, T.C. (2017), "Technology and production fragmentation: domestic versus foreign sourcing", *Review of Economic Studies* 84(2), 650 to 687. Head, K. and T. Mayer (2014), "Gravity equations: workhorse, toolkit, and cookbook", *Handbook of International Economics* 4. Juhász, R. (2015), "Temporary protection and technology adoption: evidence from the Napoleonic blockade", VoxEU, CEPR, 15 January, published in the *American Economic Review* 108(11), 2018, 3339 to 3376. Koopman, R., W. Powers, Z. Wang and S.J. Wei (2010), "Give credit where credit is due", NBER Working Paper 16426. Nunn, N. (2007), "Relationship-specificity, incomplete contracts, and the pattern of trade", *Quarterly Journal of Economics* 122(2), 569 to 600. Young, A. (1992), "A tale of two cities: factor accumulation and technical change in Hong Kong and Singapore", *NBER Macroeconomics Annual* 7, 13 to 54. Ramondo, N. (2026), CAS EC 391 International Trade, syllabus and lecture notes, Boston University, Fall 2026.

</details>
