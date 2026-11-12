# 9 Case study: chips and pills, Singapore's investment-led industrial policy

## Key finding

Singapore twice tried to grow a high technology industry by courting foreign firms instead of raising tariffs. Chips learned, keeping a strong advantage while value added and investment grew, and pharmaceuticals learned only to export, building an advantage abroad while their weight at home shrank.

## The course argument {Module 9 · Infant industry · Juhász 2015}

**Comparative advantage can be learned, if support stops once the learning is done.** Temporary help lets a new industry ride down its learning curve until it can export alone, as Juhász (2015) shows for French cotton spinning shielded by the Napoleonic blockade. With zero tariffs (Chapter 7), Singapore gave the help through the Economic Development Board instead, with tax holidays, estates and training, and pioneer firms paying 5 to 15 percent or nothing against a headline rate of 17 percent ([EDB](https://www.edb.gov.sg/content/dam/edb-en/how-we-help/incentive-and-schemes/factsheets/DEI(Mfg)%20Factsheet.pdf)).

<!-- interactive: learncurve -->

**Two bets, chips from 1968 and pills from 2000.** National Semiconductor opened the first assembly plant in 1968 and Chartered the first wafer fab in 1987 ([EDB](https://www.edb.gov.sg/en/business-insights/insights/made-in-singapore-60-years-of-manufacturing.html)), and the Biomedical Sciences Initiative of 2000 brought plants from Pfizer, GSK and Novartis.

<details class="more" markdown="1">
<summary>More: the new wave of investment and an evaluation of the pharma cluster</summary>

Chips drew a new wave of fabs after 2021, and the research budget for 2026 to 2030 of S$37 billion names semiconductors first ([EDB](https://www.edb.gov.sg/en/news-and-insights/singapore-invests-s37-billion-in-rie2030-research-plan-semiconductors-ageing-among-focus-areas)). An evaluation of the biomedical cluster found that it met its output and jobs targets but produced few spin-off firms ([CIIP 2021](https://www.ciip.group.cam.ac.uk/wp-content/uploads/2021/02/2021-02-19-SBS.pdf)).

</details>

## The scorecard

**Both industries export with an advantage, and only one has deepened at home.** On four digit BACI data, chips have stayed far above 1, at 4.6 in 2024 with 7.1 percent of world integrated circuit exports, and finished medicines rose from 0.16 in 2004 to 1.78. Yet semiconductors' share of manufacturing value added rose from 16 to 35 percent while pharmaceuticals' fell from 19 to 5.5 percent, and foreign capital in pharmaceuticals shrank from S$32 billion to S$10 billion.

<!-- include: data/derived/ch09_scorecard.md -->

<details class="more" markdown="1">
<summary>More: the RCA chart, and value added and foreign investment over time</summary>

![Chips keep a strong advantage and finished pharma built one](../figures/ch09_rca.png)

![Semiconductors now make 35% of manufacturing value added](../figures/ch09_manufacturing.png)

![Foreign investment in chip plants grew while pharma's shrank](../figures/ch09_fdi_stock.png)

The pharmaceutical share swings because a few foreign plants make most of the output and parents decide where patents and profits are booked.

</details>

<details class="more" markdown="1">
<summary>More: the 2017 outlier and the product detail</summary>

BACI's chip exports for 2017 ($125 billion, twice the neighbouring years) lift that year's RCA to 7.6, and we treat it as a reporting anomaly.

</details>

## The difference in differences test

![Against its other chemicals and its peers, Singapore's pharma RCA rose 4.8 times after 2000](../figures/ch09_did.png)

**Pharmaceuticals gained an advantage that Singapore's other chemicals and its neighbours did not.** We compared Singapore's RCA in pharmaceuticals (HS 30) with its other chemical chapters (HS 28 to 38) and with the same chapters in Malaysia and Hong Kong SAR, before and after 2000, estimating ln RCA<sub>ckt</sub> = a<sub>ck</sub> + b<sub>kt</sub> + g<sub>ct</sub> + β (Singapore<sub>c</sub> × Pharma<sub>k</sub> × Post2000<sub>t</sub>) + e<sub>ckt</sub>. The estimate β = 1.57 (robust s.e. 0.27) means the advantage rose 4.8 times relative to the comparison, with no gap before 2000 and a jump from 2005.

**What it does not show.** The policy built export capacity, but local value added and foreign capital fell at the same time. With three economies and four years before the policy the test is a guide, and plant level data on local suppliers would make it firmer.

## The verdict {Young 1992}

**Chips learned, and pills learned only to export.** Chips are a successful infant industry raised without a tariff, whose advantage survived decades of rising wages because Singapore's capital, skills and suppliers now carry it. Pharmaceuticals built an export advantage while value added and foreign capital moved the other way, which fits Young's (1992) finding that Singapore grew mainly by accumulating factors.

**The next test.** The OECD minimum tax weakens tax holidays, which Singapore offsets with a Refundable Investment Credit the global rules allow ([IRAS](https://www.iras.gov.sg/schemes/disbursement-schemes/refundable-investment-credit-(ric))), and US tariffs put both industries at the centre of strategic rivalry (Chapter 7).

## Sources

CEPII, BACI HS92 V202601 (4-digit products); Economic Development Board, Census of Manufacturing Activities via SingStat table M355181; Singapore Department of Statistics, table M084831; EDB; IRAS; Cambridge CIIP (2021); Juhász (2015), VoxEU; Young (1992). Figures generated by `scripts/ch09_case.py`.
