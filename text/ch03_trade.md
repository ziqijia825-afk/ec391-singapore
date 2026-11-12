# 3 Openness and trade patterns

## Key finding

Singapore's exports plus imports of goods and services were 313 percent of its GDP in 2024, the third highest ratio in the world. It runs surpluses in both goods ($172 billion) and services ($34.5 billion), and services have become the faster growing half of its exports. More than half of its merchandise exports are re-exports, goods that pass through Singapore without being made there, and that share has risen from 46.5 percent in 2004 to 57.5 percent in 2024. Its trade partners are spread widely across Asia, the United States and Europe, and its trade follows the gravity model closely, with exports falling by about 16 percent for every 10 percent of extra distance.

## How open is Singapore?

![Singapore trades 313% of its GDP](../figures/ch03_openness.png)

Trade openness, measured as exports plus imports over GDP, was 313 percent in 2024, against 137 percent in Malaysia, 174 percent in Vietnam and 58 percent in East Asia and the Pacific as a whole. Only Hong Kong SAR (359 percent) and one other economy rank higher among 172 with data. The ratio exceeds 100 percent because trade is measured as the gross value of goods crossing the border while GDP counts only value added at home, and Singapore re-exports and processes a great deal of imported value. Openness peaked at 437 percent in 2008 and has drifted down since, as services and domestic activity have grown faster than goods trade and as commodity prices have fallen from their peaks.

## Goods and services balances

![Singapore earns surpluses on goods and services](../figures/ch03_balances.png)

On the balance of payments, Singapore's goods surplus grew from $41 billion in 2004 to $172 billion in 2024. The services account tells a more interesting story. It was in deficit by $10 billion in 2004 and $13 billion in 2014, mainly because Singaporeans travel abroad and firms pay for foreign transport, insurance and intellectual property. By 2024 it had swung to a surplus of $34.5 billion as exports of transport, financial and business services grew faster than imports. Services made up 16 percent of Singapore's exports of goods and services in 2004 and 40 percent in 2024, and Singapore's services exports of $399 billion are the sixth largest in the world and the largest in East Asia and the Pacific. Its goods exports of $601 billion rank eleventh.

## Domestic exports and re-exports

![Re-exports grew to 58% of merchandise exports](../figures/ch03_reexports.png)

Singapore's own statistics divide merchandise exports into domestic exports, which are made or substantially transformed in Singapore, and re-exports, which are imported and shipped out again with little change. Re-exports were 46.5 percent of the total in 2004 and 57.5 percent in 2024. Non-oil domestic exports, the category that includes semiconductors and pharmaceuticals, fell from 42 to 26 percent, and oil domestic exports, mainly refined petroleum from the refineries on Jurong Island, rose from 11 to 17 percent. This split matters for every trade indicator in this report. Total export figures overstate what Singapore itself produces, so measures of comparative advantage based on reported exports must be read with care, and the value added data in Chapter 5 are the better guide to what Singapore actually contributes.

## What Singapore exports and imports

![Services rose from 21% to 52% of Singapore's exports](../figures/ch03_export_structure.png)

The Harvard Growth Lab's Atlas of Economic Complexity combines goods and services exports in one consistent dataset, which lets us follow the composition of Singapore's exports over twenty years. Its goods figures are reconciled from the reports of both exporters and importers and are lower than Singapore's own (in 2024, $366 billion against $505 billion reported to UN Comtrade), which suggests that they count fewer re-exports. On this basis services rose from 21 percent of exports in 2004 to 52 percent in 2024. Transport services alone are now 18 percent, and business and ICT services 12 percent. Electronics and instruments remain the largest goods group but fell from 32 to 20 percent of exports, and machinery and computers fell from 16 to 7 percent as assembly of disk drives and personal computers moved to cheaper locations in the region.

![Electronics are also Singapore's largest import](../figures/ch03_import_structure.png)

Imports mirror exports. Electronics and instruments were 27 percent of goods imports in 2024 and refined petroleum and crude oil 20 percent. Large two way trade in the same sectors is the signature of an economy that imports components and crude oil, processes them, and ships them on, and of an entrepôt that re-exports chips made elsewhere in Asia. Machinery and computers still make up 14 percent of imports, much of it capital equipment for semiconductor plants.

## Trade partners and concentration

![Asia takes most of Singapore's exports](../figures/ch03_partners.png)

China was Singapore's largest export market in 2024 with 14.0 percent of reported exports, followed by Hong Kong SAR (11.0 percent), Malaysia (10.4 percent), the United States (8.7 percent) and Indonesia (7.9 percent). The largest sources of imports were Taiwan (13.8 percent), mainland China (12.4 percent), the United States (12.2 percent) and Malaysia (11.2 percent). The import list is dominated by chip producers and suppliers of equipment and fuel, the export list by Asian markets that buy or re-route Singapore's goods.

![Singapore's export markets are diversified](../figures/ch03_partner_hhi.png)

The Herfindahl Hirschman index of export destinations, the sum of squared partner shares, was 0.071 in 2024 on Atlas data and 0.068 on Singapore's reported figures. Both values are low, meaning that no single partner dominates. Singapore's concentration has barely changed in twenty years, while Vietnam's rose from 0.076 to 0.129 as exports to the United States grew, and Hong Kong's remains the highest of the four because of its dependence on mainland China. For an investor, the low concentration means that Singapore's export base is less exposed to a downturn in any one market than its neighbours'.

## Does Singapore's trade follow gravity?

![Trade falls with distance](../figures/ch03_gravity.png)

The gravity model predicts that trade between two countries rises with their economic size and falls with the distance between them. We tested this for Singapore by regressing the logarithm of its 2024 exports to each partner on the logarithm of the partner's GDP and of the great circle distance between the two capitals.

<!-- include: data/derived/ch03_gravity_table.md -->

Singapore's trade follows gravity closely. A partner with 10 percent higher GDP buys about 8 percent more from Singapore, and a partner 10 percent farther away buys about 16 percent less. Both coefficients are statistically significant, and the two variables explain just over half of the variation across 192 partners. The distance elasticity of about 1.6 is larger in absolute value than the value of about 1 that is typical in the literature (Head and Mayer, 2014), which suggests that Singapore's role as a regional hub concentrates its trade on nearby Asian markets even more than size alone would predict. The result is almost the same with the Atlas's reconciled export figures, which count fewer re-exports, so the entrepôt trade appears to follow the same geography as the rest of Singapore's exports. The partners that buy much more than the model predicts are Marshall Islands, Liberia, Panama and Malta. All four register large merchant fleets, so these exports are likely to include ships and ship supplies that are recorded under the flag state, which is where trade statistics place a ship regardless of the routes it sails. The partners that buy much less include Iran, Sudan and Afghanistan, where sanctions and conflict limit trade.

## Implications for trade and investment

Openness of this scale makes Singapore an excellent base for firms that serve regional markets, but it also transmits every swing in world demand to the domestic economy. The growth of re-exports and of services shows that Singapore is earning more from handling, financing and coordinating trade than from making goods, which raises the question of what it is actually good at producing. The next chapter answers that question with measures of revealed comparative advantage.

## Sources

World Bank, World Development Indicators; Singapore Department of Statistics / Enterprise Singapore, table M451001; Harvard Growth Lab, Atlas of Economic Complexity; UN Comtrade; Head, K. and T. Mayer (2014), "Gravity equations: workhorse, toolkit, and cookbook", *Handbook of International Economics* 4. Figures generated by `scripts/ch03_trade.py`.
