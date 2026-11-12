# Appendix: sources and methods

## Data sources

Every chart and table on this site was built by the team from raw files downloaded by the scripts in the project repository (`scripts/fetch_*.py`). Downloaded files are stored in `data/raw/`, and derived numbers used in the text are saved in `data/derived/`. All data were accessed between 11 and 12 November 2026.

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
| UNCTAD, World Investment Report 2026 annex tables | UN | FDI inflows, greenfield projects, cross-border M&A | [Annex tables](https://unctad.org/topic/investment/world-investment-report), `fetch_other.py` |
| WTO Tariff Profiles | IGO | MFN averages, duty-free lines, tariff peaks and maximum duties for Singapore and peers | [WTO](https://www.wto.org/english/res_e/statis_e/tariff_profiles_list_e.htm), `fetch_other.py` |
| UNCTAD TRAINS via World Bank WITS | UN / IGO | Non-tariff measures by type and sector | [WITS](https://wits.worldbank.org/tariff/non-tariff-measures/en/country/SGP), `fetch_wits_ntm.py` |
| Enterprise Singapore, WTO RTA database, METI | Government / IGO | List of free trade agreements | `data/raw/manual/sg_fta_list.csv` |
| Ministry of Energy, Trade and Industry (METI) | Government | Bilateral investment treaties in force and partners | `data/raw/manual/sg_bit_list.csv` |
| Natural Earth; geoBoundaries (CC BY 4.0) | Public domain / open data | Country boundaries for the maps (not statistics) | `fetch_geo.py` |
| WTO, Singapore Customs, IRAS, EDB, NLB, MOE | Government / IGO | Facts on membership, tariffs, incentives, taxes, history and education | linked in the text |

## Methods

**Global and regional ranks.** For every indicator we rank all economies with data in the same year, excluding the World Bank's regional and income aggregates. Rank 1 is the highest value unless stated otherwise (for inflation and tariffs, 1 is the lowest). Ties share the best rank. The regional rank is among economies in the World Bank's East Asia and Pacific region. B-READY ranks are among the 100 economies it covers, and TiVA ranks among its 80 economies.

**Revealed comparative advantage.** Balassa's index for country *i* and sector *k* is RCA = (X<sub>ik</sub> / X<sub>i</sub>) ÷ (X<sub>wk</sub> / X<sub>w</sub>), where X is exports and *w* is the world, here the sum of all economies in the data. Goods exports come from CEPII BACI and services exports from the World Bank's balance of payments data (transport, travel, insurance and financial, and computer, communications and other services). Sector RCAs in Chapter 4 use exports of goods and services; HS chapter and product RCAs in Chapters 4 and 9 use goods only.

**Gravity.** Ordinary least squares of ln(Singapore's exports to partner *j*, 2024) on ln(GDP of *j*, 2024, current US$) and ln(great circle distance between capitals), with heteroskedasticity robust (HC1) standard errors. Capital coordinates come from the World Bank's country metadata.

**Concentration.** Herfindahl Hirschman index HHI = Σ s<sub>j</sub><sup>2</sup>, where s<sub>j</sub> is partner *j*'s share of exports.

**Value chains.** Backward participation = foreign value added in gross exports ÷ gross exports. Forward participation = the economy's value added contained in other economies' gross exports ÷ its own gross exports. Position index = ln(1 + forward) − ln(1 + backward), following Koopman and coauthors (2010).

**Shared sector table.** Chapters 3 to 6 use one table of sectors so that trade, value added and FDI data refer to the same industries. The mapping between classifications is approximate.

<!-- include: data/derived/sector_table.md -->

## Limitations

Singapore's role as an entrepôt and financial centre complicates almost every statistic in this report. Reported exports include re-exports, so we use domestic export data, BACI reconciled data and value added data alongside them. FDI is recorded by immediate investor and includes large pass through investment by holding companies. The World Bank publishes no poverty or survey based Gini data for Singapore, so we use the national Gini series, which is not comparable across countries. TiVA ends in 2022, and the World Bank's latest tariff data for these economies are for 2022.

## Questions for the professor

Is the Singapore Department of Statistics acceptable as a source for inequality and FDI? Is AI-assisted drafting acceptable if every number is generated from raw data and each owner rewrites the text? Is a class presentation required?

## Course readings

Each analytical chapter tests its findings against a course reading. Chapter 3 compares our gravity estimate with Feyrer's natural experiment from the closure of the Suez Canal. Chapters 2 and 4 use Nunn's evidence that contract enforcement is a source of comparative advantage. Chapter 5 uses Fort's evidence on technology, coordination costs and fragmentation toward high human capital locations. Chapter 7 uses Conconi and coauthors on rules of origin as protection in free trade agreements.

## References

Conconi, P., M. García Santana, L. Puccio and R. Venturini (2016), "The perverse effect of preferential rules of origins", VoxEU, CEPR, 16 March. Damgaard, J., T. Elkjaer and N. Johannesen (2019), "The rise of phantom investments", IMF *Finance and Development*, September. Ekholm, K., R. Forslid and J. Markusen (2007), "Export-platform foreign direct investment", *Journal of the European Economic Association* 5(4), 776 to 795. Feyrer, J. (2009), "The 1967 to 1975 Suez Canal closure: lessons for trade and the trade income link", VoxEU, CEPR, 23 December. Fort, T.C. (2017), "Technology and production fragmentation: domestic versus foreign sourcing", *Review of Economic Studies* 84(2), 650 to 687. Head, K. and T. Mayer (2014), "Gravity equations: workhorse, toolkit, and cookbook", *Handbook of International Economics* 4. Koopman, R., W. Powers, Z. Wang and S.J. Wei (2010), "Give credit where credit is due", NBER Working Paper 16426. Nunn, N. (2007), "Relationship-specificity, incomplete contracts, and the pattern of trade", *Quarterly Journal of Economics* 122(2), 569 to 600. Young, A. (1992), "A tale of two cities: factor accumulation and technical change in Hong Kong and Singapore", *NBER Macroeconomics Annual* 7, 13 to 54.
