# 4 Specialization and comparative advantage

## Key finding

Measured by Balassa's revealed comparative advantage, Singapore specializes in transport and logistics services (RCA 4.5), finance and insurance (2.8), electronics and instruments (1.4), ICT and business services (1.3) and pharmaceuticals (1.2). Over twenty years its advantage moved from manufactured goods to services. Transport rose from an RCA of 2.3 in 2004 to 4.5 in 2024 and finance from 1.2 to 2.8, while electronics fell from 2.0 to 1.4 and machinery, chemicals and refined petroleum lost their advantage. The pattern fits Singapore's endowments. It has the 14th highest capital per worker of 173 economies, a skilled workforce and almost no land or natural resources, so in the spirit of Heckscher and Ohlin it exports capital and skill intensive goods and services and imports land and resource intensive ones.

## How we measure comparative advantage

The Balassa index divides a sector's share in a country's exports by the sector's share in world exports, and a value above 1 is a revealed comparative advantage. We computed it ourselves for goods from CEPII's BACI database (HS 1992 chapters, about 200 exporters) and for services from the World Bank's balance of payments categories, using the team's shared sector table so that this chapter lines up with Chapters 5 and 6 (see the [appendix](appendix.html)).

<!-- interactive: treemap -->

<details class="more" markdown="1">
<summary>More: why reconciled data matter for Singapore</summary>

BACI reconciles exporter and importer reports, and importers record the country where goods were made, so much of Singapore's re-export trade is attributed to its origin (Chapter 3). Singapore's goods RCAs on BACI are therefore closer to what it produces than RCAs on its own reported exports, although some entrepôt trade remains. The World Bank does not publish services exports by category for Vietnam, so its services RCAs are missing.

</details>

## Singapore against its peers

<!-- include: data/derived/ch04_rca_heat.md -->

Singapore and Hong Kong SAR are the only two of the four economies with advantages in both transport and finance, the statistical fingerprint of regional hubs, and Singapore differs from Hong Kong SAR in still making much of the electronics and medicines it exports. Malaysia's advantages are in electronics (2.7), refined petroleum (1.9), machinery and food and agriculture, the profile of a manufacturing economy with natural resources. Vietnam's are in electronics (3.1), machinery (1.7) and other goods such as garments and footwear (2.9), the profile of a labour abundant assembly economy.

<details class="more" markdown="1">
<summary>More: Hong Kong SAR's profile</summary>

Hong Kong SAR's largest advantages are finance (3.8), transport (3.0), gold and metals (2.8) and travel (1.6). Manufacturing is less than 1 percent of its GDP (Chapter 1), so its electronics RCA of 1.45 reflects trade it organizes for mainland China.

</details>

## How the pattern changed

![Singapore's comparative advantage shifted toward services](../figures/ch04_rca_change.png)

Between 2004 and 2024 the RCA in transport and logistics almost doubled (2.3 to 4.5) and the RCA in finance more than doubled (1.2 to 2.8), and ICT and business services crossed 1 (0.8 to 1.3). Electronics remains an advantage but fell from 1.95 to 1.41. Machinery (1.7 to 0.8) lost its advantage when disk drive and computer assembly left Singapore in the 2000s, and chemicals (1.4 to 0.8) and refined petroleum (1.3 to 0.9) lost theirs as refining and petrochemical capacity in the Middle East and China grew. Pharmaceuticals moved the other way, from 0.2 to 1.2, which Chapter 9 examines.

<details class="more" markdown="1">
<summary>More: RCA by HS chapter</summary>

Measured within goods trade alone, which is why these values are higher than in the treemap above, the largest goods exports by HS chapter in 2024 were electrical machinery (29.9 percent of goods exports, RCA 2.1), mineral fuels (17.1 percent, RCA 1.3), industrial machinery (14.2 percent, RCA 1.2), pharmaceuticals (6.9 percent, RCA 1.7) and precision instruments (5.9 percent, RCA 2.0). Singapore has an RCA above 1 in 17 of 97 chapters, the same number as Hong Kong SAR, against 11 for Malaysia and 27 for Vietnam, so its goods exports are concentrated in a few high value lines.

<!-- include: data/derived/ch04_hs_table.md -->

</details>

## Endowments and the Heckscher Ohlin test

![Singapore has the 14th highest capital per worker](../figures/ch04_capital_per_worker.png)

The Heckscher Ohlin model predicts that a country exports goods that use its abundant factors intensively. Singapore's capital stock per worker was $657,000 in 2023 at constant 2021 prices, 14th of 173 economies in the Penn World Table and above Japan, Germany and the United States. Its human capital index of 3.40 ranks 28th of 143, and its arable land per person is the smallest of 205 economies. The sectors with an RCA above 1 (logistics, finance, chips, instruments and medicines) all use capital and skilled labour intensively, while food and agriculture (RCA 0.3) are imported, so the export pattern matches the endowments.

<!-- include: data/derived/ch04_endowments.md -->

<details class="more" markdown="1">
<summary>More: caveats to the Heckscher Ohlin reading</summary>

Large exports of refined petroleum are consistent with the model too, because they rest on imported crude processed in very large, capital intensive refineries. Two caveats apply. Factor intensities are not observed directly in these data, so the test is a qualitative comparison. And much of the capital and technology was brought in by foreign multinationals, the point Young (1992) made when he found that Singapore's growth came mainly from factor accumulation. With mobile capital, Singapore's abundance of capital is itself partly the result of the FDI analysed in Chapter 6.

</details>

## Implications for trade and investment

Activities that need capital, skills, reliable institutions and connectivity, such as advanced semiconductor production, biologics, logistics, trading and finance, play to Singapore's strengths. Activities that need land, cheap labour or local raw materials do not, and those have moved to Malaysia and Vietnam. Gross export data cannot show how much of the value of Singapore's exports is created in Singapore, so the next chapter uses value added data to place Singapore in global value chains.

<details class="more" markdown="1">
<summary>Sources for this chapter</summary>

CEPII, BACI HS92 V202601 (Gaulier and Zignago, 2010); World Bank, World Development Indicators (services exports by category); UN Comtrade (HS chapter titles); Penn World Table 11.0 (Feenstra, Inklaar and Timmer, Groningen Growth and Development Centre); Nunn, N. (2007) and Young, A. (1992), see appendix. Figures and tables generated by `scripts/ch04_rca.py`.

</details>
