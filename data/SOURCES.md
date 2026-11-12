# Source log

One line per file group: files · database · version/edition · download date · link · how.

| Files | Database | Version | Downloaded | Link | How |
| --- | --- | --- | --- | --- | --- |
| data/raw/wdi/*.csv | World Bank WDI, WGI (2025 release), B-READY 2025 (via WDI API) | latest at download | 12 Nov 2026 | https://api.worldbank.org/v2 | `fetch_worldbank.py` (Fetch data workflow + local) |
| data/raw/singstat/*.csv | Singapore Department of Statistics Table Builder (trade, Gini, FDI, GDP, manufacturing census) | per table, see `*.meta.txt` | 12 Nov 2026 | https://tablebuilder.singstat.gov.sg | `fetch_singstat.py` |
| data/raw/tiva/*.csv | OECD Trade in Value Added | 2025 edition (to 2022) | 12 Nov 2026 | https://sdmx.oecd.org/sti-public/rest | `fetch_tiva.py` |
| data/raw/comtrade/*.csv | UN Comtrade, Singapore reported trade by partner | every year 2004 to 2024 | 12 Nov 2026 | https://comtradeapi.un.org | `fetch_comtrade.py` |
| data/raw/baci/*.zip (not in git) → data/derived/baci_*.csv | CEPII BACI, HS 1992 | V202601 | 12 Nov 2026 | https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37 | download + `process_baci.py` |
| data/raw/wto/tariff_profile_*.pdf | WTO Tariff Profiles (SG, MY, HK, VN) | 2025 profiles | 12 Nov 2026 | https://www.wto.org/english/res_e/statis_e/tariff_profiles_list_e.htm | `fetch_other.py` |
| data/raw/wits_ntm/* | UNCTAD TRAINS NTM summaries via World Bank WITS | latest on WITS | 12 Nov 2026 | https://wits.worldbank.org/tariff/non-tariff-measures/en/country/SGP | `fetch_wits_ntm.py` |
| data/raw/manual/sg_bit_list.csv | METI list of BITs/IGAs in force | Nov 2026 | 12 Nov 2026 | see `sg_bit_list.README.md` | transcribed |
| data/raw/comtrade/hs_chapters.csv | UN Comtrade HS reference (chapter titles) | current | 12 Nov 2026 | https://comtradeapi.un.org/files/v1/app/reference/HS.json | `fetch_comtrade.py` |
| site/data/geo_*.json | Natural Earth 1:50m (public domain); geoBoundaries gbOpen SGP ADM0 (CC BY 4.0) | current | 12 Nov 2026 | naturalearthdata.com; geoboundaries.org | `fetch_geo.py` |
| data/raw/manual/ti_cpi_2012_2024_owid.csv | Transparency International CPI via Our World in Data (replace with TI's own CPI2025_Results.xlsx, downloaded by hand in a browser) | 2012–2024 | 12 Nov 2026 | https://www.transparency.org/en/cpi/2025 | `fetch_other.py` |
| data/raw/manual/undp_hdr25_composite_time_series.csv | UNDP Human Development Report | HDR 2025 (data to 2023) | 12 Nov 2026 | https://hdr.undp.org | `fetch_other.py` |
| data/raw/manual/pwt110.dta | Penn World Table | 11.0 | 12 Nov 2026 | https://doi.org/10.34894/FABVLR | `fetch_other.py` |
| data/raw/manual/unctad_wir26_tab*.xlsx | UNCTAD World Investment Report annex tables 1, 5, 7, 14, 17 | WIR 2026 | 12 Nov 2026 | https://unctad.org/topic/investment/world-investment-report | `fetch_other.py` |
| data/raw/manual/sg_fta_list.csv | Team list from Enterprise Singapore + WTO RTA database | Nov 2026 | 12 Nov 2026 | see `sg_fta_list.README.md` | hand-compiled |
| (in `export_site_data.py`, facts) | Land area 745.1 km², June 2026, supplied by Estella; source to cite: SingStat Population Trends 2026 | Jun 2026 | 12 Nov 2026 | https://www.singstat.gov.sg/publication-resources/population-trends-2026 | typed in |
