// Interactive components that go beyond the static figures: maps, Sankey, treemap, network, FDI explorer,
// WGI radar by year, FDI explorer. All data come from site/data/*.json (built by Python).
import { state, set, on, getJSON, pickYear, YEARS } from './state.js';
import { cardShell, baseOption, tipFooter, shortSource, radarOption, registry, nameOf } from './chart.js';

const INK = '#1d2b33', MUTED = '#4f5b62', LINE = '#e6dcc4', BLUE = '#2a78d6', RED = '#e23d3d';
const GRAYS = ['#5f5e5a', '#8a8a85', '#b3b2ab'];
const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const ord = (n) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? 'th' : { 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] || 'th'}`;
const rankTxt = (r) => (r ? `${ord(r.rank)} of ${r.n} globally · ${ord(r.region_rank)} of ${r.region_n} in East Asia & Pacific` : '');
const badge = (el, text) => { const b = el.querySelector('.badge') || el.insertAdjacentElement('afterbegin', Object.assign(document.createElement('span'), { className: 'badge' })); b.textContent = text; };

// ---------- landing: Southeast Asia map ----------
export async function landingMap(el, onEnter) {
  const [geo, k] = await Promise.all([getJSON('data/geo_sea.json'), getJSON('data/kpis.json')]);
  echarts.registerMap('sea', geo);
  const chart = echarts.init(el);
  const kpiHtml = `<b style="font-size:14px">Singapore</b>${k.kpis.map((x) => `<div style="margin-top:5px">${esc(x.label)}: <b>${esc(x.value)}</b><br><span style="color:${MUTED};font-size:11px">${esc(rankTxt(x.rank))}</span></div>`).join('')}<div style="margin-top:6px;color:${BLUE}">Click to explore</div>`;
  const o = baseOption();
  const HAND = '"Patrick Hand SC", "Patrick Hand", cursive';
  const sg = k.facts.coords;
  const routes = [  // main sea lanes through the Strait of Malacca and the South China Sea (illustrative)
    { name: 'To China, Korea and Japan', to: [116.5, 15.5], via: [109, 9] },
    { name: 'To India, the Gulf and Europe', to: [94.5, 9.5], via: [99, 4.5] },
    { name: 'To Indonesia and Australia', to: [117, -7.6], via: [108, -3.5] },
  ];
  o.tooltip.trigger = 'item';
  o.tooltip.formatter = (p) => (p.name === 'Singapore' || p.seriesType === 'effectScatter' ? kpiHtml
    : p.seriesType === 'lines' ? `<b>${esc(p.name)}</b><br>Illustrative sea lane` : `<b>${esc(p.name)}</b>`);
  o.geo = { map: 'sea', roam: false, boundingCoords: [[93, 21], [127, -9]], layoutCenter: ['50%', '50%'], layoutSize: '104%', silent: false,
    itemStyle: { areaColor: '#eef7e2', borderColor: '#1d2b33', borderWidth: 1.2 },
    emphasis: { itemStyle: { areaColor: '#ffe7a8' }, label: { show: false } },
    regions: [{ name: 'Singapore', itemStyle: { areaColor: RED } }] };
  o.series = [
    { type: 'lines', coordinateSystem: 'geo', zlevel: 1, silent: false,
      lineStyle: { color: '#e8552f', width: 3.5, type: [8, 6], curveness: .25, opacity: .95 },
      effect: { show: true, period: 6, trailLength: 0, symbol: 'circle', symbolSize: 7, color: '#ffc93c' },
      data: routes.map((r) => ({ name: r.name, coords: [sg, r.via, r.to] })), polyline: true },
    { type: 'scatter', coordinateSystem: 'geo', symbolSize: 1, silent: true,
      data: [...routes.map((r) => ({ name: r.name, value: r.to, label: r.to[0] < 100 ? { position: 'right' } : undefined })),
        { name: 'Strait of Malacca', value: [98.6, 5.8] }],
      label: { show: true, formatter: '{b}', position: 'top', fontFamily: HAND, fontSize: el.clientWidth < 500 ? 12 : 15, color: INK,
        backgroundColor: '#fffdf6', borderColor: INK, borderWidth: 1.5, borderRadius: 4, padding: [2, 6] } },
    { type: 'effectScatter', coordinateSystem: 'geo', zlevel: 2, data: [{ name: 'Singapore', value: sg }],
      symbolSize: 16, rippleEffect: { scale: 4.5, brushType: 'stroke' }, itemStyle: { color: RED, borderColor: INK, borderWidth: 2 },
      label: { show: true, formatter: 'Singapore', position: 'right', fontFamily: HAND, fontSize: 20, color: INK,
        backgroundColor: '#ffc93c', borderColor: INK, borderWidth: 2, borderRadius: 6, padding: [2, 8] } },
  ];
  chart.setOption(o);
  chart.on('click', (p) => { if (p.name === 'Singapore') onEnter(); });
  new ResizeObserver(() => chart.resize()).observe(el);
}

// ---------- country profile: Singapore map with key sites ----------
const SITES = [
  ['Central business district', [103.851, 1.282], 'Finance and regional headquarters (Ch. 6)'],
  ['Jurong Island', [103.69, 1.265], 'Refining and petrochemicals cluster on reclaimed land (Ch. 3, 4)'],
  ['Tuas Port and Tuas Biomedical Park', [103.63, 1.305], 'Container port of the future and pharma plants (Ch. 7, 9)'],
  ['Pasir Panjang terminals', [103.765, 1.272], 'Container transshipment hub (Ch. 3)'],
  ['one-north and Biopolis', [103.789, 1.299], 'Biomedical research complex opened in 2003 (Ch. 9)'],
  ['Woodlands wafer fab park', [103.789, 1.447], 'Semiconductor fabs, including GlobalFoundries (Ch. 9)'],
  ['Tampines and Pasir Ris wafer fab parks', [103.95, 1.372], 'Chip fabs of UMC, Siltronic and VSMC (Ch. 9)'],
  ['Changi Airport and Airport Logistics Park', [103.99, 1.355], 'Air cargo free trade zone (Ch. 7)'],
];
export async function sgMap(el) {
  const [geo, k] = await Promise.all([getJSON('data/geo_sgp.json'), getJSON('data/kpis.json')]);
  echarts.registerMap('sgp', geo);
  const f = k.facts;
  const spec = { title: 'Singapore at a glance: one island economy, eight places that matter for trade',
    subtitle: 'Main island and key economic zones (locations approximate). Hover a point for its role in this report.',
    source: 'Source: geoBoundaries (gbOpen, CC BY 4.0) boundary of Singapore; site roles from the chapters of this report; facts from SingStat (Population Trends 2026, land area mid-2024) and the Constitution.' };
  const chart = cardShell(el, spec, {});
  el.querySelector('.plot').outerHTML = `<div class="split"><div class="plot"></div><div class="panel"><h5>Key facts</h5><dl>
    <dt>Capital</dt><dd>${esc(f.capital)} (city state)</dd><dt>Land area</dt><dd>${f.area_km2} km², +28% since 1965</dd>
    <dt>Population</dt><dd>${f.population_m} million (June 2026)</dd><dt>Languages</dt><dd>${esc(f.languages)}</dd>
    <dt>Political system</dt><dd>${esc(f.system)}; PAP in government since 1959</dd></dl></div></div>`;
  const plot = el.querySelector('.plot');
  const c = echarts.init(plot);
  const o = baseOption();
  o.tooltip.trigger = 'item';
  o.tooltip.formatter = (p) => (p.seriesType === 'scatter' ? `<b>${esc(p.name)}</b><br>${esc(p.data.note)}${tipFooter(spec.source)}` : '<b>Singapore</b>');
  o.geo = { map: 'sgp', roam: true, itemStyle: { areaColor: '#f1efe9', borderColor: '#b3b2ab' }, emphasis: { disabled: true } };
  o.series = [{ type: 'scatter', coordinateSystem: 'geo', symbolSize: 13, itemStyle: { color: BLUE, borderColor: '#fff', borderWidth: 2 },
    data: SITES.map(([n, xy, note]) => ({ name: n, value: xy, note })),
    label: { show: true, formatter: '{b}', fontSize: 10.5, color: INK }, emphasis: { scale: 1.6 } }];
  o.series[0].data.forEach((d) => { d.label = { position: d.value[0] > 103.9 ? 'left' : 'right' }; });
  c.setOption(o);
  new ResizeObserver(() => c.resize()).observe(plot);
  chart.dispose();
}

// ---------- governance: WGI radar following the year control ----------
export async function wgiRadar(el) {
  const w = await getJSON('data/wgi.json');
  const dimsKeys = Object.keys(w.dims);
  const spec = { title: 'Governance scores of Singapore and its peers', subtitle: 'Worldwide Governance Indicators, governance score (0 to 100). Dashed: East Asia & Pacific average. Hover for ranks.',
    source: w.source, png: 'figures/ch02_wgi_radar.png' };
  const chart = cardShell(el, spec, { tall: true });
  const years = Object.keys(w.years);
  const draw = () => {
    const y = pickYear(years, Math.max(state.year, 2004));
    badge(el, `Showing ${y}`);
    const row = w.years[y];
    const econs = ['SGP', 'MYS', 'HKG', 'VNM'];
    const series = econs.map((k, j) => ({ name: w.names[k], key: k, color: j === 0 ? BLUE : GRAYS[j - 1], values: dimsKeys.map((d) => row[d].values[k]) }));
    series.push({ name: 'East Asia & Pacific average', color: '#8a8a85', dashed: true, values: dimsKeys.map((d) => row[d].eap) });
    const tip = (p) => {
      const k = series.find((s) => s.name === p.name)?.key;
      return `<b>${esc(p.name)}, ${y}</b>${dimsKeys.map((d, i) => {
        const r = k && row[d].rank[k];
        return `<div>${esc(w.dims[d])}: <b>${p.value[i]?.toFixed(1)}</b>${r ? ` <span style="color:${MUTED}">(${ord(r[0])}/${r[1]} global, ${ord(r[2])}/${r[3]} region)</span>` : ''}</div>`;
      }).join('')}${tipFooter(w.source)}`;
    };
    chart.setOption(radarOption(dimsKeys.map((d) => w.dims[d]), series, 100, tip), true);
  };
  draw();
  on((s, ch) => { if (ch.includes('year')) draw(); });
}

// ---------- openness: Sankey of trade partners, linked to a partner card ----------
export async function tradeSankey(el) {
  const d = await getJSON('data/sankey.json');
  const spec = { title: 'Where Singapore\'s goods come from and go to', subtitle: 'Merchandise imports by source (left) and exports by destination (right), top 10 partners, US$ billions. Click a partner.', source: d.source };
  const chart = cardShell(el, spec, { tall: true });
  el.querySelector('.extra').innerHTML = '<div class="panel" style="margin-top:8px"><h5>Click a partner to see its trend</h5><div class="mini"></div><div class="pinfo hint"></div></div>';
  const mini = echarts.init(el.querySelector('.mini'));
  const years = Object.keys(d.years);
  const draw = () => {
    const y = pickYear(years);
    badge(el, `Showing ${y}`);
    const r = d.years[y];
    const nodes = [{ name: 'Singapore', itemStyle: { color: BLUE } }];
    const links = [];
    const add = (iso, side) => { const n = `${nameOf(iso) || iso}${side}`; nodes.push({ name: n, iso, itemStyle: { color: state.partner === iso ? BLUE : '#b3b2ab' } }); return n; };
    r.M.top.forEach(([iso, v]) => links.push({ source: add(iso, ' '), target: 'Singapore', value: v, iso }));
    links.push({ source: add('Other', ' '), target: 'Singapore', value: r.M.other_bn, iso: 'Other' });
    r.X.top.forEach(([iso, v]) => links.push({ source: 'Singapore', target: add(iso, '  '), value: v, iso }));
    links.push({ source: 'Singapore', target: add('Other', '  '), value: r.X.other_bn, iso: 'Other' });
    links.forEach((l) => { l.lineStyle = { color: state.partner && l.iso === state.partner ? BLUE : '#c9c8c1', opacity: state.partner && l.iso !== state.partner ? .25 : .55 }; });
    const o = baseOption();
    o.tooltip.trigger = 'item';
    o.tooltip.formatter = (p) => (p.dataType === 'edge'
      ? `<b>${esc(p.data.source.trim())} → ${esc(p.data.target.trim())}</b>, ${y}<br><b>$${p.value.toFixed(1)}bn</b>${tipFooter(d.source)}`
      : `<b>${esc(p.name.trim())}</b>${tipFooter(d.source)}`);
    o.series = [{ type: 'sankey', left: 10, right: 110, top: 10, bottom: 10, nodeWidth: 12, nodeGap: 8, draggable: false,
      data: nodes, links, label: { color: INK, fontSize: 11.5, formatter: (p) => p.name.trim() },
      emphasis: { focus: 'adjacency' } }];
    chart.setOption(o, true);
  };
  const card = () => {
    const iso = state.partner; const p = iso && d.partners[iso];
    const info = el.querySelector('.pinfo');
    el.querySelector('.extra h5').textContent = p ? `${p.name}: share of Singapore's trade, 2004 to 2024` : 'Click a partner to see its trend';
    if (!p) { info.textContent = 'Shares of Singapore\'s exports and imports, 2004 to 2024.'; mini.clear(); return; }
    info.innerHTML = `<b>${esc(p.name)}</b>${p.km ? ` · ${Math.round(p.km).toLocaleString()} km from Singapore` : ''}${p.fta ? ` · FTA: ${esc(p.fta)}` : ''}`;
    const ys = Array.from({ length: 21 }, (_, i) => 2004 + i);
    const o = baseOption();
    o.grid = { left: 40, right: 12, top: 26, bottom: 22 };
    o.legend = { top: 0, itemWidth: 10, itemHeight: 8, textStyle: { fontSize: 11 } };
    o.xAxis = { type: 'category', data: ys, axisLabel: { fontSize: 10 } };
    o.yAxis = { type: 'value', axisLabel: { formatter: '{value}%', fontSize: 10 }, splitLine: { lineStyle: { color: LINE } } };
    o.tooltip.trigger = 'axis';
    o.tooltip.valueFormatter = (v) => (v == null ? 'n/a' : `${v.toFixed(1)}%`);
    o.series = [{ name: 'Share of exports', type: 'line', data: ys.map((y) => p.share_x[y] ?? null), symbol: 'none', lineStyle: { color: BLUE, width: 2.4 }, itemStyle: { color: BLUE } },
      { name: 'Share of imports', type: 'line', data: ys.map((y) => p.share_m[y] ?? null), symbol: 'none', lineStyle: { color: '#8a8a85' }, itemStyle: { color: '#8a8a85' } }];
    mini.setOption(o, true);
  };
  chart.on('click', (p) => { const iso = p.data?.iso; if (iso && iso !== 'Other') set({ partner: state.partner === iso ? null : iso }); });
  draw(); card();
  on((s, ch) => { if (ch.includes('year') || ch.includes('partner')) draw(); if (ch.includes('partner')) card(); });
  // the gravity scatter selects partners too
  on((s, ch) => {
    if (!ch.includes('partner')) return;
    const g = registry.get('ch03_gravity');
    if (g) { g.dispatchAction({ type: 'downplay' }); const idx = g.getOption().series[0].data.findIndex((x) => x.key === state.partner); if (idx >= 0) g.dispatchAction({ type: 'highlight', seriesIndex: 0, dataIndex: idx }); }
  });
}

// ---------- comparative advantage: RCA treemap with drill-down and trend panel ----------
export async function rcaTreemap(el) {
  let d;
  try { d = await getJSON('data/rca.json'); } catch { el.innerHTML = ''; return; }
  const spec = { title: 'Singapore\'s exports by sector, coloured by revealed comparative advantage',
    subtitle: 'Box size = export value (US$ billions); colour = Balassa RCA (blue above 1 = advantage). Click a sector to see its RCA over time; click again to drill into HS chapters. RCA here is measured against world exports of goods and services, so HS chapter values are lower than the goods-only RCAs in the HS chapter table later in this chapter.',
    source: d.source };
  const chart = cardShell(el, spec, { tall: true });
  el.querySelector('.extra').innerHTML = '<div class="panel" style="margin-top:8px"><h5 class="pt">Click a sector</h5><div class="mini"></div></div>';
  const mini = echarts.init(el.querySelector('.mini'));
  const years = Object.keys(d.years);
  const color = (r) => (r == null ? '#e9e8e3' : r >= 2 ? '#2a78d6' : r >= 1 ? '#a9c8ee' : r >= .5 ? '#e4e3dd' : '#f4f3ef');
  const draw = () => {
    const y = pickYear(years);
    badge(el, `Showing ${y}`);
    const data = d.years[y].map((s) => ({ name: s.name, value: s.value, rca: s.rca,
      itemStyle: { color: color(s.rca), borderColor: '#fff' },
      children: (s.children || []).map((c) => ({ name: c.name, value: c.value, rca: c.rca, itemStyle: { color: color(c.rca) } })) }));
    const o = baseOption();
    o.tooltip.formatter = (p) => `<b>${esc(p.name)}</b>, ${y}<br>Exports: <b>$${p.value?.toFixed(1)}bn</b><br>RCA: <b>${p.data.rca == null ? 'n/a' : p.data.rca.toFixed(2)}</b>${tipFooter(d.source)}`;
    o.series = [{ type: 'treemap', roam: false, nodeClick: 'zoomToNode', breadcrumb: { show: true, bottom: 4 },
      top: 6, left: 4, right: 4, bottom: 34, data,
      label: { formatter: (p) => `${p.name}\nRCA ${p.data.rca == null ? 'n/a' : p.data.rca.toFixed(1)}`, color: INK, fontSize: 12 },
      upperLabel: { show: true, height: 20, color: INK }, levels: [{ itemStyle: { gapWidth: 3, borderWidth: 0 } }, { itemStyle: { gapWidth: 1 } }] }];
    chart.setOption(o, true);
  };
  const panel = () => {
    const s = state.sector; const t = s && d.trend[s];
    el.querySelector('.pt').textContent = t ? `RCA of ${s}, 2004 to ${years[years.length - 1]}` : 'Click a sector';
    if (!t) { mini.clear(); return; }
    const o = baseOption();
    o.grid = { left: 40, right: 14, top: 26, bottom: 22 };
    o.legend = { top: 0, itemWidth: 10, itemHeight: 8, textStyle: { fontSize: 11 } };
    o.xAxis = { type: 'category', data: t.years };
    o.yAxis = { type: 'value', splitLine: { lineStyle: { color: LINE } } };
    o.tooltip.trigger = 'axis';
    o.tooltip.valueFormatter = (v) => (v == null ? 'n/a' : v.toFixed(2));
    const cols = { SGP: BLUE, MYS: GRAYS[0], HKG: GRAYS[1], VNM: GRAYS[2] };
    o.series = Object.entries(t.values).map(([k, v]) => ({ name: nameOf(k), type: 'line', data: v, symbol: 'none',
      lineStyle: { color: cols[k], width: k === 'SGP' ? 2.6 : 1.5 }, itemStyle: { color: cols[k] } }));
    o.series[0].markLine = { symbol: 'none', silent: true, lineStyle: { color: '#8a8a85', type: 'dashed' }, label: { formatter: 'RCA = 1' }, data: [{ yAxis: 1 }] };
    mini.setOption(o, true);
  };
  chart.on('click', (p) => { if (p.treePathInfo?.length === 2) set({ sector: p.name }); });
  draw(); panel();
  on((s, ch) => { if (ch.includes('year')) draw(); if (ch.includes('sector')) panel(); });
}

// ---------- value chains: network of value-added links, linked to participation charts ----------
export async function gvcNetwork(el) {
  const d = await getJSON('data/gvc.json');
  const spec = { title: 'Singapore in the value-added network', subtitle: 'Arrows into Singapore: foreign value added in its exports. Arrows out: Singapore\'s value added in partners\' exports (US$ billions). Node colour: position, amber = upstream, slate = downstream. Click a node.',
    source: d.source };
  const chart = cardShell(el, spec, { tall: true });
  el.querySelector('.extra').innerHTML = '<div class="panel" style="margin-top:8px"><h5 class="gt">Backward and forward participation over time</h5><div class="mini"></div></div>';
  const mini = echarts.init(el.querySelector('.mini'));
  const years = Object.keys(d.network);
  const col = (p) => (p > .1 ? '#b07d2b' : p > 0 ? '#d4b277' : p > -.1 ? '#9aa3ad' : '#5d6873');
  const draw = () => {
    const y = pickYear(years);
    badge(el, `Showing ${y}`);
    const n = d.network[y];
    const maxX = Math.max(...n.nodes.map((x) => x.exgr_bn));
    const nodes = n.nodes.map((x) => ({ id: x.id, name: x.name, value: x.exgr_bn, x0: x,
      symbolSize: 14 + 46 * Math.sqrt(x.exgr_bn / maxX),
      itemStyle: { color: x.id === 'SGP' ? BLUE : col(x.position), borderColor: state.economy === x.id ? INK : '#fff', borderWidth: state.economy === x.id ? 3 : 1 },
      label: { show: true, color: INK, fontSize: 11 } }));
    const maxL = Math.max(...n.in.map((l) => l[1]), ...n.out.map((l) => l[1]));
    const links = [...n.in.map(([k, v]) => ({ source: k, target: 'SGP', value: v, dir: 'in' })), ...n.out.map(([k, v]) => ({ source: 'SGP', target: k, value: v, dir: 'out' }))]
      .map((l) => ({ ...l, lineStyle: { width: 0.8 + 7 * l.value / maxL, color: l.dir === 'in' ? '#b3b2ab' : BLUE, opacity: .55, curveness: .15 } }));
    const o = baseOption();
    o.tooltip.formatter = (p) => (p.dataType === 'edge'
      ? `<b>${esc(nameOf(p.data.source))} → ${esc(nameOf(p.data.target))}</b>, ${y}<br>Value added: <b>$${p.data.value.toFixed(1)}bn</b>${tipFooter(d.source)}`
      : `<b>${esc(p.name)}</b>, ${y}<br>Gross exports: <b>$${p.data.x0.exgr_bn.toFixed(0)}bn</b><br>Backward: <b>${p.data.x0.backward.toFixed(1)}%</b> · Forward: <b>${p.data.x0.forward.toFixed(1)}%</b><br>Position index: <b>${p.data.x0.position.toFixed(3)}</b> (${p.data.x0.position > 0 ? 'upstream' : 'downstream'})${tipFooter(d.source)}`);
    o.series = [{ type: 'graph', layout: 'force', roam: true, draggable: true, data: nodes, links,
      edgeSymbol: ['none', 'arrow'], edgeSymbolSize: 6, force: { repulsion: 420, edgeLength: [70, 170], gravity: .08 },
      emphasis: { focus: 'adjacency' } }];
    chart.setOption(o, true);
  };
  const panel = () => {
    const k = state.economy || 'SGP';
    el.querySelector('.gt').textContent = `Backward and forward participation, ${nameOf(k) || d.names[k]}${k !== 'SGP' ? ' vs Singapore' : ''}, % of gross exports`;
    const ys = Object.keys(d.series.SGP);
    const o = baseOption();
    o.grid = { left: 40, right: 14, top: 26, bottom: 22 };
    o.legend = { top: 0, itemWidth: 10, itemHeight: 8, textStyle: { fontSize: 11 } };
    o.xAxis = { type: 'category', data: ys };
    o.yAxis = { type: 'value', axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: LINE } } };
    o.tooltip.trigger = 'axis';
    o.tooltip.valueFormatter = (v) => (v == null ? 'n/a' : `${v.toFixed(1)}%`);
    const mk = (iso, i, name, color, dash) => ({ name, type: 'line', symbol: 'none', data: ys.map((y) => d.series[iso]?.[y]?.[i] ?? null),
      lineStyle: { color, width: iso === 'SGP' ? 2.4 : 1.8, type: dash ? 'dashed' : 'solid' }, itemStyle: { color } });
    o.series = [mk('SGP', 0, 'Singapore backward', BLUE), mk('SGP', 1, 'Singapore forward', BLUE, true)];
    if (k !== 'SGP') o.series.push(mk(k, 0, `${d.names[k]} backward`, '#b07d2b'), mk(k, 1, `${d.names[k]} forward`, '#b07d2b', true));
    mini.setOption(o, true);
    const sc = registry.get('ch05_backward_forward');
    if (sc) { sc.dispatchAction({ type: 'downplay' }); const idx = sc.getOption().series[0].data.findIndex((x) => x.key === k); if (idx >= 0) sc.dispatchAction({ type: 'highlight', seriesIndex: 0, dataIndex: idx }); }
  };
  chart.on('click', (p) => { if (p.dataType === 'node') set({ economy: p.data.id }); });
  draw(); panel();
  on((s, ch) => { if (ch.includes('year')) draw(); if (ch.includes('economy')) { draw(); panel(); } });
}

// ---------- FDI explorer: inward/outward × source/industry, linked to the year control ----------
export async function fdiExplorer(el) {
  const d = await getJSON('data/fdi.json');
  const spec = { title: 'Who invests in Singapore, where Singapore invests, and in what', subtitle: 'Direct investment stock at year-end, S$ billions. Switch the view; the bar shows shares in the selected year.', source: d.source };
  const chart = cardShell(el, spec, { tall: true });
  let view = 'inward_source';
  el.querySelector('.controls').innerHTML = `<div class="seg" data-g="dir"><button data-v="inward" class="on">Inward</button><button data-v="outward">Outward</button></div>
    <div class="seg" data-g="by"><button data-v="source" class="on">By economy</button><button data-v="industry">By industry</button></div>`;
  let dir = 'inward', by = 'source';
  el.querySelectorAll('.seg button').forEach((b) => b.addEventListener('click', () => {
    b.parentElement.querySelectorAll('button').forEach((x) => x.classList.toggle('on', x === b));
    if (b.parentElement.dataset.g === 'dir') dir = b.dataset.v; else by = b.dataset.v;
    view = dir === 'inward' ? (by === 'source' ? 'inward_source' : 'inward_industry') : (by === 'source' ? 'outward_destination' : 'outward_industry');
    draw();
  }));
  const hubs = new Set(d.hubs);
  const palette = ['#2a78d6', '#4f8fdd', '#7aaae6', '#a9c8ee', '#5f5e5a', '#8a8a85', '#b3b2ab', '#c9c8c1', '#d9d8d2', '#e4e3dd', '#efeee9'];
  const draw = () => {
    const p = d[view];
    const y = pickYear(p.years);
    const yi = p.years.indexOf(y);
    badge(el, `Bars: ${y}`);
    const o = baseOption();
    o.legend = { top: 0, type: 'scroll', itemWidth: 10, itemHeight: 8, textStyle: { fontSize: 11 } };
    o.grid = [{ left: 50, right: '52%', top: 46, bottom: 30 }, { left: '70%', right: 56, top: 46, bottom: 30 }];
    o.xAxis = [{ type: 'category', data: p.years, gridIndex: 0, boundaryGap: false }, { type: 'value', gridIndex: 1, axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: LINE } } }];
    o.yAxis = [{ type: 'value', gridIndex: 0, name: 'S$ billions', splitLine: { lineStyle: { color: LINE } } },
      { type: 'category', gridIndex: 1, inverse: true, data: p.series.map((s) => s.name), axisLabel: { width: 135, overflow: 'truncate', fontSize: 11, color: INK } }];
    o.tooltip.trigger = 'axis';
    o.tooltip.formatter = (ps) => {
      if (ps[0].axisIndex === 1 || ps[0].seriesType === 'bar') return `<b>${esc(ps[0].name)}</b>, ${y}<br><b>${ps[0].value.toFixed(1)}%</b> of total${hubs.has(ps[0].name) ? '<br><i>Holding-company hub: immediate, not ultimate, investor</i>' : ''}${tipFooter(d.source)}`;
      return `<b>${ps[0].axisValue}</b>${ps.filter((x) => x.value != null).map((x) => `<div>${esc(x.seriesName)}: <b>S$${x.value.toFixed(0)}bn</b></div>`).join('')}${tipFooter(d.source)}`;
    };
    o.series = p.series.map((s, i) => ({ name: s.name, type: 'line', stack: 'a', areaStyle: { opacity: .85 }, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0,
      data: s.values, lineStyle: { width: .5, color: '#fff' }, itemStyle: { color: hubs.has(s.name) ? '#cfe0f5' : palette[i % palette.length] },
      emphasis: { focus: 'series' } }));
    o.series[0].markLine = { symbol: 'none', silent: true, label: { show: false }, lineStyle: { color: INK, type: 'dashed' }, data: [{ xAxis: String(y) }] };
    const total = p.total[yi];
    o.series.push({ type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: p.series.map((s, i) => ({ value: s.values[yi] == null ? null : s.values[yi] / total * 100,
      itemStyle: { color: hubs.has(s.name) ? '#a9c8ee' : i === 0 ? BLUE : '#c9c8c1' } })),
      label: { show: true, position: 'right', fontSize: 10.5, formatter: (q) => (q.value == null ? '' : `${q.value.toFixed(1)}%`) }, tooltip: { trigger: 'item' } });
    chart.setOption(o, true);
  };
  draw();
  on((s, ch) => { if (ch.includes('year')) draw(); });
}

// ---------- case study: sticky chart + text steps; the years mentioned in the active step are highlighted ----------
