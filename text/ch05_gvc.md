# 5 Global value chains

## Key finding

Almost half of the value of Singapore's exports was created abroad. In 2022, the latest year of the OECD Trade in Value Added database, foreign value added made up 46.1 percent of Singapore's gross exports, the 7th highest share of 80 economies and the 2nd highest in East Asia and the Pacific after Vietnam. Singapore's own value added used in other countries' exports was 17.3 percent of its exports, so its total participation in global value chains, 63.4 percent, is the 5th highest in the world. The balance between the two puts Singapore at the downstream end of most chains. It buys components, crude oil and services from abroad, adds processing, logistics and coordination, and ships the result on.

## Backward and forward participation

Value added trade data split the value of a country's exports into the part created at home and the part embodied in imported inputs. Backward participation is the foreign share of a country's exports. Forward participation is the share of a country's exports that other countries use as inputs into their own exports. We downloaded the 2025 edition of the OECD TiVA database, which covers Singapore and 79 other economies up to 2022, and computed both measures ourselves. Forward participation comes from TiVA's table of the origin of value added in gross exports, summing Singapore's value added in every other country's exports.

![46% of the value of Singapore's exports is foreign](../figures/ch05_backward.png)

Singapore's backward participation was already high in 2004 (43.3 percent) and has stayed between 46 and 49 percent since 2008. Vietnam overtook it in 2021 as foreign owned electronics assembly expanded there, and its share reached 48.5 percent in 2022. Malaysia's share is lower (34.2 percent) because its exports include palm oil, gas and other resources produced at home, and Hong Kong SAR's is lowest (18.0 percent) because its exports are now dominated by services that use few imported inputs.

![Singapore buys far more foreign value added than it sells into others' exports](../figures/ch05_backward_forward.png)

Plotting backward against forward participation for all 80 economies shows two groups. Exporters of raw materials such as Norway, Saudi Arabia, Russia and Australia have low backward and high forward participation because their oil, gas and minerals become inputs into other countries' exports. Small open economies with large processing and re-export activity, such as Luxembourg, Vietnam, Ireland and Singapore, have the opposite profile. Singapore sits with the second group. Its position index, the logarithm of one plus forward participation minus the logarithm of one plus backward participation (Koopman and coauthors, 2010), is −0.22, the 73rd of 80, so it is among the most downstream economies in the database.

<!-- include: data/derived/ch05_participation_table.md -->

A Singapore specific measure in TiVA is the value of re-exported intermediate imports, inputs that are imported and leave the country again inside exports. It equalled 47.1 percent of Singapore's gross exports in 2022, the 7th highest share in the world. Together with the re-export figures in Chapter 3, this confirms that a large part of Singapore's role in value chains is to receive, process and redistribute inputs for the region.

## Which sectors are most integrated?

![Refining and transport carry the most foreign content](../figures/ch05_sector_fva.png)

Using the team's shared sector table, the industries that account for most of Singapore's gross exports in TiVA are transport and logistics (20.6 percent), ICT and business services (18.7 percent), electronics and instruments (17.8 percent) and wholesale trade (14.8 percent). The foreign content of each sector's exports shows where Singapore is most deeply embedded in value chains. Refined petroleum has the highest foreign share (72 percent) because the crude oil is all imported, followed by transport and logistics (60 percent), where fuel, ships and aircraft are bought abroad. Electronics, chemicals and machinery are close to the national average of 46 percent. Finance and insurance (28 percent) and wholesale trade (34 percent) have the most domestic value, which supports the conclusion of Chapter 4 that services are where Singapore now adds the most value of its own.

<!-- include: data/derived/ch05_sector_table.md -->

## Where Singapore's inputs come from

![The US and China each supply 14% of the foreign value in Singapore's exports](../figures/ch05_fva_origin.png)

The United States and China each supplied 13.7 percent of the foreign value added in Singapore's exports in 2022, followed by Japan (7.1 percent), India (5.4 percent) and Taiwan (5.1 percent). The list reflects Singapore's two main chains. Semiconductor production draws on American design and equipment, Japanese materials and Taiwanese and Korean chips, while trade and transport services draw on Chinese and Indian goods and services. Denmark's share of 2.9 percent is a reminder that shipping is a global industry, since Denmark is home to some of the world's largest container lines. Malaysia, Singapore's closest neighbour and one of its largest sources of imports (Chapter 3), supplies only 2.6 percent of the foreign value added, which suggests that much of what Singapore buys from Malaysia passes through with little processing.

## Implications for trade and investment

Being downstream and highly integrated has two sides. It lets Singapore specialize in the stages where it is most productive, such as advanced wafer fabrication, testing, logistics and finance, without producing raw materials or every component itself. It also exposes the economy to shocks anywhere upstream, from chip shortages to oil price spikes and export controls, and to the strategic rivalry between its two largest suppliers of foreign value added, the United States and China. For an investor, the high foreign content means that Singapore's attractiveness rests on its links to suppliers and markets as much as on domestic costs. Chapter 6 turns to the foreign firms that operate these links.

## Sources

OECD, Trade in Value Added (TiVA) database, 2025 edition (principal indicators and origin of value added in gross exports), via the OECD SDMX API; Koopman, R., W. Powers, Z. Wang and S.J. Wei (2010), "Give credit where credit is due: tracing value added in global production chains", NBER Working Paper 16426. Figures and tables generated by `scripts/ch05_gvc.py`.
