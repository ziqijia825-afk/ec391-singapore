# 5 Global value chains

## Key finding

Almost half of the value of Singapore's exports was created abroad. In 2022, the latest year of the OECD Trade in Value Added database, foreign value added made up 46.1 percent of Singapore's gross exports, the 7th highest share of 80 economies and the 2nd highest in East Asia and the Pacific after Vietnam. Singapore's own value added used in other countries' exports was 17.3 percent of its exports, so its total participation in global value chains, 63.4 percent, is the 5th highest in the world. The balance between the two puts Singapore at the downstream end of most chains. It buys components, crude oil and services from abroad, adds processing, logistics and coordination, and ships the result on.

## Value added versus gross exports

<!-- interactive: gvc -->

![46% of the value of Singapore's exports is foreign](../figures/ch05_backward.png)

Backward participation, the foreign value added in a country's exports, was already 43.3 percent for Singapore in 2004 and has stayed between 46 and 49 percent since 2008. Only Vietnam, where foreign owned electronics assembly expanded fast, now has a higher share among the peers. Malaysia's share is lower (34.2 percent) because it exports resources produced at home, and Hong Kong SAR's is lowest (18.0 percent) because its exports are now mostly services.

<details class="more" markdown="1">
<summary>How we measured participation from the OECD TiVA data</summary>

Value added trade data split the value of a country's exports into the part created at home and the part embodied in imported inputs. Backward participation is the foreign share of a country's exports. Forward participation is the share of a country's exports that other countries use as inputs into their own exports. We downloaded the 2025 edition of the OECD TiVA database, which covers Singapore and 79 other economies up to 2022, and computed both measures ourselves. Forward participation comes from TiVA's table of the origin of value added in gross exports, summing Singapore's value added in every other country's exports.

</details>

## Participation and position: upstream or downstream?

![Singapore buys far more foreign value added than it sells into others' exports](../figures/ch05_backward_forward.png)

Exporters of raw materials such as Norway, Saudi Arabia and Australia have low backward and high forward participation, because their oil, gas and minerals become inputs into other countries' exports. Small open processing economies such as Luxembourg, Vietnam, Ireland and Singapore have the opposite profile. Singapore's position index (Koopman and coauthors, 2010) is −0.22, 73rd of 80, so it is among the most downstream economies in the database.

<!-- include: data/derived/ch05_participation_table.md -->

<details class="more" markdown="1">
<summary>More: re-exported intermediate inputs</summary>

A Singapore specific measure in TiVA is the value of re-exported intermediate imports, inputs that are imported and leave the country again inside exports. It equalled 47.1 percent of Singapore's gross exports in 2022, the 7th highest share in the world. Together with the re-export figures in Chapter 3, this confirms that a large part of Singapore's role in value chains is to receive, process and redistribute inputs for the region. The position index is the logarithm of one plus forward participation minus the logarithm of one plus backward participation.

</details>

## Which sectors are most integrated?

![Refining and transport carry the most foreign content](../figures/ch05_sector_fva.png)

Refined petroleum has the highest foreign share (72 percent) because the crude oil is all imported, followed by transport and logistics (60 percent), where fuel, ships and aircraft are bought abroad. Electronics, chemicals and machinery are close to the national average of 46 percent, while finance and insurance (28 percent) and wholesale trade (34 percent) carry the most domestic value, which supports the conclusion of Chapter 4 that services are where Singapore now adds most value of its own.

<details class="more" markdown="1">
<summary>More: sector table and where Singapore's foreign inputs come from</summary>

Using the team's shared sector table, the industries that account for most of Singapore's gross exports in TiVA are transport and logistics (20.6 percent), ICT and business services (18.7 percent), electronics and instruments (17.8 percent) and wholesale trade (14.8 percent).

<!-- include: data/derived/ch05_sector_table.md -->

![The US and China each supply 14% of the foreign value in Singapore's exports](../figures/ch05_fva_origin.png)

The United States and China each supplied 13.7 percent of the foreign value added in Singapore's exports in 2022, followed by Japan (7.1 percent), India (5.4 percent) and Taiwan (5.1 percent). Semiconductor production draws on American design and equipment, Japanese materials and Taiwanese and Korean chips, while trade and transport services draw on Chinese and Indian goods and services. Denmark's share of 2.9 percent reflects shipping, since Denmark is home to some of the world's largest container lines. Malaysia supplies only 2.6 percent of the foreign value added although it is one of Singapore's largest sources of imports, which suggests that much of what Singapore buys from Malaysia passes through with little processing.

</details>

## Implications for trade and investment

Fort (2017) helps explain why firms choose a high cost location like Singapore for some stages of production. Using plant data for the United States, she finds that communication technology makes firms more likely to split production across locations, most of all in industries whose designs can be codified electronically, with semiconductor machinery at the top, and that the effect appears for sourcing from countries with high human capital and not from low skill ones. Singapore has the 28th highest human capital index of 143 economies (Chapter 4), so cheaper coordination favours it for the design intensive stages of electronics, while labour intensive assembly goes to Malaysia and Vietnam. Her evidence is for American firms, so for Singapore it is suggestive.

Being downstream and highly integrated lets Singapore specialize in the stages where it is most productive, such as advanced wafer fabrication, testing, logistics and finance, without producing raw materials or every component itself. It also exposes the economy to shocks anywhere upstream, from chip shortages to oil prices and export controls, and to the rivalry between its two largest suppliers of foreign value added, the United States and China. Chapter 6 turns to the foreign firms that operate these links.

<details class="more" markdown="1">
<summary>Sources for this chapter</summary>

OECD, Trade in Value Added (TiVA) database, 2025 edition (principal indicators and origin of value added in gross exports), via the OECD SDMX API; Koopman, R., W. Powers, Z. Wang and S.J. Wei (2010), "Give credit where credit is due: tracing value added in global production chains", NBER Working Paper 16426; Fort, T.C. (2017), "Technology and production fragmentation: domestic versus foreign sourcing", *Review of Economic Studies* 84(2). Figures and tables generated by `scripts/ch05_gvc.py`.

</details>
