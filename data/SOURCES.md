# Source log

One line per file group: files · database · version/edition · download date · link · how.

| Files | Database | Version | Downloaded | Link | How |
| --- | --- | --- | --- | --- | --- |
| data/raw/wdi/*.csv | World Bank WDI, WGI (2025 release), B-READY 2025 (via WDI API) | latest at download | 12 Nov 2026 | https://api.worldbank.org/v2 | `fetch_worldbank.py` (Fetch data workflow + local) |
| data/raw/singstat/*.csv | Singapore Department of Statistics Table Builder (trade, Gini, FDI, GDP, manufacturing census) | per table, see `*.meta.txt` | 12 Nov 2026 | https://tablebuilder.singstat.gov.sg | `fetch_singstat.py` |
| data/raw/tiva/*.csv | OECD Trade in Value Added | 2025 edition (to 2022) | 12 Nov 2026 | https://sdmx.oecd.org/sti-public/rest | `fetch_tiva.py` |
| data/raw/comtrade/*.csv | UN Comtrade, Singapore reported trade by partner | 2004, 2014, 2024 | 12 Nov 2026 | https://comtradeapi.un.org | `fetch_comtrade.py` |
| data/raw/atlas/* (not in git) | Harvard Growth Lab, Atlas of Economic Complexity (HS92, services) | Dataverse v18 / v4 / v12 | 12 Nov 2026 | https://dataverse.harvard.edu/dataverse/atlas | `fetch_atlas.py` |
| data/raw/manual/ti_cpi_2012_2024_owid.csv | Transparency International CPI via Our World in Data | 2012–2024 | 12 Nov 2026 | https://ourworldindata.org/grapher/ti-corruption-perception-index | `fetch_other.py` |
| data/raw/manual/undp_hdr25_composite_time_series.csv | UNDP Human Development Report | HDR 2025 (data to 2023) | 12 Nov 2026 | https://hdr.undp.org | `fetch_other.py` |
| data/raw/manual/pwt110.dta | Penn World Table | 11.0 | 12 Nov 2026 | https://doi.org/10.34894/FABVLR | `fetch_other.py` |
| data/raw/manual/unctad_wir26_tab*.xlsx | UNCTAD World Investment Report annex tables 1, 5, 7, 14, 17 | WIR 2026 | 12 Nov 2026 | https://unctad.org/topic/investment/world-investment-report | `fetch_other.py` |
| data/raw/manual/sg_fta_list.csv | Team list from Enterprise Singapore + WTO RTA database | Nov 2026 | 12 Nov 2026 | see `sg_fta_list.README.md` | hand-compiled |
