// Interactive components that go beyond the static figures: maps, Sankey, treemap, network, FDI explorer,
// WGI radar by year, FDI explorer. All data come from site/data/*.json (built by Python).
import { state, set, on, getJSON, pickYear, YEARS } from './state.js';
import { ICON } from './icons.js';
import { cardShell, baseOption, tipFooter, shortSource, radarOption, registry, nameOf, ECON, CATEGORICAL, rgba } from './chart.js';

const INK = '#14212e', MUTED = '#6b7a89', LINE = '#e9ecef', BLUE = '#2a78d6', RED = '#e23d3d';
const GRAYS = ['#5f5e5a', '#8a8a85', '#b3b2ab'];
const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const ord = (n) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? 'th' : { 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] || 'th'}`;
const rankTxt = (r) => (r ? `${ord(r.rank)} of ${r.n} globally · ${ord(r.region_rank)} of ${r.region_n} in East Asia & Pacific` : '');
// the year a snapshot shows is written into its title ("…, 2024") instead of a separate badge
const badge = (el, text) => {
  const h = el.querySelector('h4');
  if (!h) return;
  const y = (text.match(/\d{4}/) || [''])[0];
  const yr = h.querySelector('.yr') || h.appendChild(Object.assign(document.createElement('span'), { className: 'yr' }));
  yr.textContent = y ? `, ${y}` : '';
};

// ---------- landing: Southeast Asia map ----------
export async function coverMap(el, kpiEl) {
  const [geo, k, a] = await Promise.all([getJSON('data/geo_sea.json'), getJSON('data/kpis.json'), getJSON('data/atlas.json')]);
  if (!echarts.getMap('sea')) echarts.registerMap('sea', geo);
  const ord = (n) => `${n}${[11, 12, 13].includes(n % 100) ? 'th' : ({ 1: 'st', 2: 'nd', 3: 'rd' }[n % 10] || 'th')}`;
  if (kpiEl) {
    kpiEl.innerHTML = k.kpis.map((x) => `<div class="kpi"><b>${esc(x.value)}</b><span>${esc(x.label)}</span>`
      + `<small>${x.rank?.rank ? `${ord(x.rank.rank)} of ${x.rank.n}` : ''}</small></div>`).join('');
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
      kpiEl.querySelectorAll('.kpi b').forEach((b, i) => {  // count each headline number up from zero
        const m = b.textContent.match(/^([^\d]*)([\d,]*\.?\d+)(.*)$/);
        if (!m) return;
        const [, pre, num, post] = m;
        const target = parseFloat(num.replace(/,/g, '')), dec = (num.split('.')[1] || '').length, comma = num.includes(',');
        const t0 = performance.now() + i * 90;
        const step = (t) => {
          const kk = Math.max(0, Math.min(1, (t - t0) / 1300));
          const v = target * (1 - Math.pow(1 - kk, 3));
          b.textContent = `${pre}${comma ? v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }) : v.toFixed(dec)}${post}`;
          if (kk < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      });
    }
  }
  const SG = [103.82, 1.35];
  const narrow = () => el.clientWidth < 760;
  const SERIF = '"Source Serif 4", Georgia, serif';
  const SHIP = 'path://M5 0 L10 7 L10 24 L0 24 L0 7 Z';  // a hull seen from above, bow first
  const graticule = [];
  for (let lon = 90; lon <= 130; lon += 5) graticule.push({ coords: [[lon, -15], [lon, 30]] });
  for (let lat = -10; lat <= 25; lat += 5) graticule.push({ coords: [[84, lat], [136, lat]] });
  const chart = echarts.init(el);
  const draw = () => {
    const o = baseOption();
    o.animationDuration = 1400;
    o.tooltip.trigger = 'item';
    o.tooltip.formatter = (p) => {
      const x = a.partners.find((q) => q.id === p.data?.id);
      if (!x) return '';
      const rows = x.rows.slice(0, 3).map((r) => `<div><b>${esc(r[0])}</b> <span style="color:${MUTED}">${esc(r[1])}</span></div>`).join('');
      return `<b style="font-size:14px">${esc(x.name)}</b><div style="color:${MUTED};margin:2px 0 6px">${esc(x.fta || '')}</div>${rows}`;
    };
    o.geo = { map: 'sea', roam: false, silent: true, boundingCoords: [[86, 28], [134, -14]],
      layoutCenter: narrow() ? ['50%', '50%'] : ['67%', '52%'], layoutSize: narrow() ? '100%' : '112%',
      itemStyle: { areaColor: '#e8dcc0', borderColor: '#a88d5f', borderWidth: 0.8, shadowColor: 'rgba(0,0,0,.35)', shadowBlur: 10 },
      emphasis: { disabled: true }, regions: [{ name: 'Singapore', itemStyle: { areaColor: ECON.SGP, borderColor: ECON.SGP } }] };
    o.series = [
      { type: 'lines', coordinateSystem: 'geo', silent: true, z: 0, polyline: true, data: graticule,
        lineStyle: { color: 'rgba(255,255,255,.08)', width: 1, type: [2, 6] } },
      { type: 'scatter', coordinateSystem: 'geo', silent: true, symbolSize: 0, z: 1,
        data: [{ name: 'South China Sea', value: [113.5, 12.5] }, { name: 'Indian Ocean', value: [92, -4] },
          { name: 'Strait of Malacca', value: [97.4, 6.4] }, { name: 'Java Sea', value: [110.8, -5.4] }],
        label: { show: true, formatter: '{b}', color: 'rgba(243,234,215,.55)', fontFamily: SERIF, fontStyle: 'italic', fontSize: 14 } },
      { type: 'lines', coordinateSystem: 'geo', silent: true, z: 2,
        lineStyle: { color: 'rgba(255,207,122,.55)', curveness: 0.24, type: [6, 5] },
        data: a.partners.filter((p) => p.share_x).map((p) => ({ coords: [SG, p.coord], lineStyle: { width: 0.7 + p.share_x / 4.5 } })) },
      { type: 'lines', coordinateSystem: 'geo', silent: true, z: 3,
        effect: { show: true, period: 9, trailLength: 0, symbol: SHIP, symbolSize: [5, 12], color: '#ffffff' },
        lineStyle: { opacity: 0, curveness: 0.24 },
        data: a.partners.filter((p) => p.share_x).map((p) => ({ coords: [SG, p.coord] })) },
      { type: 'scatter', coordinateSystem: 'geo', z: 4, symbol: 'circle', symbolSize: 8,
        itemStyle: { color: '#ffcf7a', borderColor: '#0a2f3e', borderWidth: 2 },
        data: a.partners.map((p) => ({ name: p.edge ? `${p.name} ↗` : p.name, value: p.coord, id: p.id,
          label: { position: p.coord[0] > 125 ? 'left' : 'right' } })),
        label: { show: !narrow(), formatter: '{b}', color: '#f3ead7', fontFamily: SERIF, fontSize: 13, fontWeight: 600, distance: 7,
          textBorderColor: 'rgba(10,47,62,.85)', textBorderWidth: 3 },
        emphasis: { scale: 1.8, label: { color: '#ffffff' } } },
      { type: 'effectScatter', coordinateSystem: 'geo', z: 5, silent: true, data: [{ name: 'Singapore', value: SG }], symbolSize: 12,
        rippleEffect: { scale: 4.5, brushType: 'stroke', color: ECON.SGP }, itemStyle: { color: ECON.SGP, borderColor: '#fff', borderWidth: 1.5 },
        label: { show: true, formatter: 'Singapore', position: 'right', color: '#ffffff', fontFamily: SERIF, fontSize: 17, fontWeight: 700,
          distance: 9, textBorderColor: 'rgba(10,47,62,.9)', textBorderWidth: 3 } },
    ];
    chart.setOption(o, true);
  };
  draw();
  new ResizeObserver(() => { chart.resize(); draw(); }).observe(el);
}

// ---------- country profile: a data atlas of places and partners, each linked to a course idea and a chapter ----------
const LABEL_POS = { onenorth: 'top', port: 'bottom', jurong: 'left', cbd: 'right', tuas: 'top', changi: 'top', fabs: 'right',
  capital: 'right', land: 'right', people: 'top', link: 'right' };
const SHORT_LABEL = { port: 'Port', jurong: 'Jurong Island', fabs: 'Wafer fabs', tuas: 'Biomedical Park', onenorth: 'one-north',
  cbd: 'CBD', changi: 'Changi Airport', capital: 'Parliament', land: 'Reclaimed coast', people: 'Heartland', link: 'Causeway to Johor' };
const SITE_COLORS = ['#5aa9ef', '#eb6834', '#8f7ff0', '#f08cb3', '#2fc48f', '#f2b84b', '#7fd36a'];
const COUNTRY_COLORS = ['#f2b84b', '#2fc48f', '#f08cb3', '#5aa9ef'];
export async function sgMap(el) {
  const [geoS, geoR, k, a] = await Promise.all([getJSON('data/geo_sgp.json'), getJSON('data/geo_sea.json'),
    getJSON('data/kpis.json'), getJSON('data/atlas.json')]);
  if (!echarts.getMap('sgp')) echarts.registerMap('sgp', geoS);
  if (!echarts.getMap('sea')) echarts.registerMap('sea', geoR);
  const f = k.facts;
  const spec = { title: 'An atlas of Singapore: the country, its places of trade and its partners',
    subtitle: 'Click a point for its numbers and ranks, the idea it illustrates and the chapter that tests it.',
    source: `${a.source} Boundaries from geoBoundaries (CC BY 4.0) and Natural Earth, locations approximate. Facts from SingStat (Population Trends 2026), the World Bank WDI and WGI, and AP via PBS for the 2025 election.` };
  const chart = cardShell(el, spec, {});
  el.classList.add('atlas');
  el.querySelector('.controls').innerHTML = '<div class="seg"><button type="button" data-v="country" class="on">The country</button>'
    + `<button type="button" data-v="sites">${a.sites.length} places of trade</button><button type="button" data-v="partners">${a.partners.length} trading partners</button></div>`;
  const panel = el.querySelector('.extra');
  let mode = 'country', sel = null;
  const SETS = { country: a.country || [], sites: a.sites, partners: a.partners };
  const island = () => mode !== 'partners';
  const items = () => SETS[mode];
  const colorOf = (x) => {
    if (mode === 'partners') return partnerColor(x.id);
    const pal = mode === 'country' ? COUNTRY_COLORS : SITE_COLORS;
    return pal[items().indexOf(x) % pal.length];
  };
  const badge = (x) => (island() ? `<i class="ab" style="--k:${colorOf(x)}">${ICON[x.id] || ICON.globe}</i>`
    : `<i class="ab iso" style="--k:${colorOf(x)}">${esc(x.id)}</i>`);
  const sub = (x) => {
    if (mode === 'country') return `${x.rows[0][0]} ${x.rows[0][1]}`;
    if (mode === 'sites') return `${x.tag} · ${x.chapter_label}`;
    const share = x.share_x != null ? `${x.share_x.toFixed(1)}% of exports` : 'largest import source';
    return [share, x.km ? `${Math.round(x.km).toLocaleString()} km` : '', x.edge ? 'off map' : ''].filter(Boolean).join(' · ');
  };
  const HEAD = { country: 'The country at a glance', sites: 'Places that matter for trade', partners: 'Twelve largest partners' };
  const HINT = { country: 'Capital and politics, land, people and the link to Malaysia. Pick one here or on the map.',
    sites: 'Pick a place here or on the map.', partners: 'Line width is the share of Singapore’s exports. Each card compares actual exports with the gravity prediction of Chapter 3.' };
  const list = () => `<div class="panel atlas-card atlas-list"><p class="al-h">${HEAD[mode]}</p>
    <ul>${items().map((x) => `<li><button type="button" data-id="${x.id}">${badge(x)}<span><b>${esc(x.name)}</b><small>${esc(sub(x))}</small></span></button></li>`).join('')}</ul>
    <p class="hint">${HINT[mode]}</p></div>`;
  const card = (x) => {
    const [hero, ...rest] = x.rows;
    return `<div class="panel atlas-card" style="--k:${colorOf(x)}">
    <div class="ac-top">${badge(x)}<div><h5>${esc(x.name)}</h5><p class="ac-sub">${mode !== 'partners' ? `${esc(x.tag)} · ${esc(x.chapter_label)}` : x.km ? `${Math.round(x.km).toLocaleString()} km from Singapore · ${esc(x.fta || 'no trade agreement')}` : esc(x.fta || sub(x))}</p></div>
      <button type="button" class="ac-x" aria-label="Back to the list">${ICON.close}</button></div>
    ${hero ? `<div class="ac-hero"><b>${esc(hero[0])}</b><span>${esc(hero[1])} <small>${esc(hero[2])}</small></span></div>` : ''}
    <dl class="ac-rows">${rest.map((r) => `<div><dt>${esc(r[1])}<small>${esc(r[2])}</small></dt><dd>${esc(r[0])}</dd></div>`).join('')}</dl>
    <blockquote><span class="tag">${esc(x.tag)}</span> ${esc(x.note)}</blockquote>
    <a class="go" href="#sec=${x.chapter}|${encodeURIComponent(x.section || '')}">Read ${esc(x.chapter_label)}${x.section ? `, ${esc(x.section)}` : ''} &rarr;</a></div>`;
  };
  const show = () => {
    const x = items().find((i) => i.id === sel);
    panel.innerHTML = x ? card(x) : list();
    panel.querySelectorAll('[data-id]').forEach((b) => b.addEventListener('click', () => { sel = b.dataset.id; draw(); show(); }));
    panel.querySelector('.ac-x')?.addEventListener('click', () => { sel = null; draw(); show(); });
  };
  // map controls: zoom in and out around the selected place, and reset
  let zoom = 1;
  const plotEl = el.querySelector('.plot');
  plotEl.insertAdjacentHTML('beforeend', `<div class="mapctl"><button type="button" data-z="in" aria-label="Zoom in">${ICON.plus}</button>`
    + `<button type="button" data-z="out" aria-label="Zoom out">${ICON.minus}</button><button type="button" data-z="reset" aria-label="Reset view">${ICON.reset}</button></div>`);
  el.querySelectorAll('.mapctl button').forEach((b) => b.addEventListener('click', () => {
    zoom = b.dataset.z === 'in' ? Math.min(zoom * 1.6, 6) : b.dataset.z === 'out' ? Math.max(zoom / 1.6, 1) : 1;
    if (b.dataset.z === 'reset') sel = null;
    draw(); show();
  }));
  const SG = [103.82, 1.35];
  const narrow = () => el.querySelector('.plot').clientWidth < 420;  // phones: only the selected place is labelled
  // the island in context: Singapore from geoBoundaries, the Johor and Riau coasts from Natural Earth
  if (!echarts.getMap('sgp_region')) {
    echarts.registerMap('sgp_region', { type: 'FeatureCollection', features: [
      ...geoR.features.filter((ft) => ['Malaysia', 'Indonesia'].includes(ft.properties.name)), ...geoS.features] });
  }
  const lab = (extra = {}) => ({ show: true, formatter: '{b}', fontFamily: 'Inter, sans-serif', fontSize: 12, fontWeight: 600,
    color: '#e8eef4', textBorderColor: '#0b2239', textBorderWidth: 3, distance: 7, ...extra });
  const water = (data) => ({ type: 'scatter', coordinateSystem: 'geo', symbolSize: 0, silent: true, z: 1, data,
    label: { show: true, formatter: '{b}', fontFamily: 'Inter, sans-serif', fontSize: 10.5, fontWeight: 600, letterSpacing: 2.5,
      color: 'rgba(159,182,204,.6)' } });
  const LAND = { areaColor: '#163a5c', borderColor: '#3f6b93', borderWidth: 0.8 };
  const draw = () => {
    const o = baseOption();
    o.tooltip.trigger = 'item';
    o.tooltip.formatter = (p) => (p.seriesType === 'scatter' && p.data?.id ? `<b>${esc(p.data.full || p.data.name)}</b><br><span style="color:${MUTED}">Click for its card</span>` : '');
    o.series = [];
    if (island()) {
      o.geo = { map: 'sgp_region', roam: false, boundingCoords: [[103.56, 1.515], [104.11, 1.165]], left: 6, right: 6, top: 6, bottom: 6,
        zoom, center: zoom > 1 ? (items().find((i) => i.id === sel)?.coord || [103.83, 1.35]) : undefined,
        itemStyle: LAND, emphasis: { disabled: true }, silent: true,
        regions: [{ name: 'Singapore', itemStyle: { areaColor: '#24507a', borderColor: '#9cc0e0', borderWidth: 1.3 } }] };
      o.series.push(water([{ name: 'SINGAPORE STRAIT', value: [103.86, 1.205] }, { name: 'JOHOR, MALAYSIA', value: [103.78, 1.497] },
        { name: 'BATAM, INDONESIA', value: [104.0, 1.178] }]));
      const cur = items().find((x) => x.id === sel);
      if (cur) o.series.push({ type: 'effectScatter', coordinateSystem: 'geo', z: 3, silent: true, symbolSize: 18,
        data: [{ value: cur.coord }], rippleEffect: { scale: 3.2, brushType: 'stroke' }, itemStyle: { color: colorOf(cur) } });
      o.series.push({ type: 'scatter', coordinateSystem: 'geo', z: 4, labelLayout: { moveOverlap: 'shiftY' },
        data: items().map((x) => ({ name: SHORT_LABEL[x.id] || x.name, full: x.name, value: x.coord, id: x.id,
          symbolSize: sel === x.id ? 20 : 13, itemStyle: { color: colorOf(x), borderColor: '#ffffff', borderWidth: 2 },
          label: { show: !narrow() || sel === x.id, position: LABEL_POS[x.id] || (x.coord[0] > 103.9 ? 'left' : 'right'),
            ...(sel === x.id ? { color: '#f2b84b', fontSize: 13.5 } : {}) } })),
        label: lab(), emphasis: { scale: 1.25 } });
    } else {
      o.geo = { map: 'sea', roam: false, boundingCoords: [[92, 26.5], [128.5, -11.5]], left: 6, right: 6, top: 10, bottom: 6,
        zoom, center: zoom > 1 ? (items().find((i) => i.id === sel)?.coord || [108, 6]) : undefined,
        itemStyle: LAND, emphasis: { disabled: true }, silent: true,
        regions: [{ name: 'Singapore', itemStyle: { areaColor: ECON.SGP, borderColor: ECON.SGP } }] };
      o.series.push(water([{ name: 'SOUTH CHINA SEA', value: [114, 13] }, { name: 'INDIAN OCEAN', value: [95.5, -3] },
        { name: 'STRAIT OF MALACCA', value: [97.8, 6] }]));
      o.series.push({ type: 'lines', coordinateSystem: 'geo', silent: true, z: 2,
        effect: { show: true, period: 6, trailLength: 0.3, symbol: 'circle', symbolSize: 3, color: '#ffe2a3' },
        data: a.partners.filter((p) => p.share_x).map((p) => ({ coords: [SG, p.coord],
          lineStyle: { width: 0.8 + p.share_x / 2.4, color: sel === p.id ? '#ffffff' : 'rgba(242,184,75,.75)',
            opacity: sel && sel !== p.id ? 0.18 : 1, curveness: 0.22 } })) });
      o.series.push({ type: 'effectScatter', coordinateSystem: 'geo', z: 3, data: [{ name: 'Singapore', value: SG }], symbolSize: 11,
        rippleEffect: { scale: 3.5, brushType: 'stroke' }, itemStyle: { color: ECON.SGP }, silent: true,
        label: { ...lab({ fontSize: 13.5, fontWeight: 700 }), formatter: 'Singapore', position: 'bottom' } });
      o.series.push({ type: 'scatter', coordinateSystem: 'geo', z: 4, labelLayout: { moveOverlap: 'shiftY' },
        data: a.partners.map((x) => ({ name: x.edge ? `${x.name} ↗` : x.name, value: x.coord, id: x.id,
          symbolSize: sel === x.id ? 14 : 9, itemStyle: { color: sel === x.id ? '#ffffff' : '#f2b84b', borderColor: '#0b2239', borderWidth: 1.5 },
          label: { show: !narrow() || sel === x.id, position: LABEL_POS[x.id] || (x.coord[0] > 124 ? 'left' : 'right'),
            ...(sel === x.id ? { color: '#f2b84b' } : {}) } })),
        label: lab({ fontSize: 11.5 }), emphasis: { scale: 1.4 } });
    }
    chart.setOption(o, true);
  };
  chart.on('click', (p) => { if (p.seriesType === 'scatter' && p.data?.id && p.data.id !== sel) { sel = p.data.id; draw(); show(); } });
  el.querySelectorAll('.seg button').forEach((b) => b.addEventListener('click', () => {
    el.querySelectorAll('.seg button').forEach((x) => x.classList.toggle('on', x === b));
    mode = b.dataset.v; sel = null; zoom = 1; draw(); show();
  }));
  draw(); show();
  new ResizeObserver(() => draw()).observe(el.querySelector('.plot'));  // re-fit the map when its box settles
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
    const series = econs.map((k) => ({ name: w.names[k], key: k, color: ECON[k], values: dimsKeys.map((d) => row[d].values[k]) }));
    series.push({ name: 'East Asia & Pacific average', color: ECON.EAS, dashed: true, values: dimsKeys.map((d) => row[d].eap) });
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
// partners keep one colour wherever they appear: comparison economies their own, others a fixed slot from their code
const PARTNER = ['#eb6834', '#1baf7a', '#e87ba4', '#6250d6', '#5aa0e8', '#c2408a', '#2a9d8f', '#d95926'];
const partnerColor = (iso) => {
  if (!iso || /^(other|oth|rest)/i.test(iso)) return '#cfc6b4';
  if (ECON[iso]) return ECON[iso];
  let h = 0;
  for (const c of iso) h = (h * 31 + c.charCodeAt(0)) % 997;
  return PARTNER[h % PARTNER.length];
};

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
    const nodes = [{ name: 'Singapore', itemStyle: { color: ECON.SGP, borderColor: INK } }];
    const links = [];
    const add = (iso, side) => { const n = `${nameOf(iso) || iso}${side}`; nodes.push({ name: n, iso, itemStyle: { color: partnerColor(iso), borderColor: state.partner === iso ? INK : partnerColor(iso), borderWidth: state.partner === iso ? 2 : 0 } }); return n; };
    r.M.top.forEach(([iso, v]) => links.push({ source: add(iso, ' '), target: 'Singapore', value: v, iso }));
    links.push({ source: add('Other', ' '), target: 'Singapore', value: r.M.other_bn, iso: 'Other' });
    r.X.top.forEach(([iso, v]) => links.push({ source: 'Singapore', target: add(iso, '  '), value: v, iso }));
    links.push({ source: 'Singapore', target: add('Other', '  '), value: r.X.other_bn, iso: 'Other' });
    links.forEach((l) => { l.lineStyle = { color: partnerColor(l.iso), opacity: state.partner ? (l.iso === state.partner ? .75 : .12) : .4 }; });
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
    // with nothing selected the panel shows the largest export market, so it is never empty
    const top = d.years[years[years.length - 1]].X.top[0][0];
    const iso = state.partner || top; const p = d.partners[iso];
    const info = el.querySelector('.pinfo');
    el.querySelector('.extra h5').textContent = p ? `${p.name}: share of Singapore's trade, 2004 to 2024` : 'Click a partner to see its trend';
    if (!p) { info.textContent = ''; mini.clear(); return; }
    info.innerHTML = `${state.partner ? '' : 'Largest export market. Click another partner to compare. '}${p.km ? `${Math.round(p.km).toLocaleString()} km from Singapore` : ''}${p.fta ? ` · FTA: ${esc(p.fta)}` : ''}`;
    const ys = Array.from({ length: 21 }, (_, i) => 2004 + i);
    const o = baseOption();
    o.grid = { left: 40, right: 12, top: 26, bottom: 22 };
    o.legend = { top: 0, itemWidth: 10, itemHeight: 8, textStyle: { fontSize: 11 } };
    o.xAxis = { type: 'category', data: ys, axisLabel: { fontSize: 10 } };
    o.yAxis = { type: 'value', axisLabel: { formatter: '{value}%', fontSize: 10 }, splitLine: { lineStyle: { color: LINE } } };
    o.tooltip.trigger = 'axis';
    o.tooltip.valueFormatter = (v) => (v == null ? 'n/a' : `${v.toFixed(1)}%`);
    o.series = [{ name: 'Share of exports', type: 'line', data: ys.map((y) => p.share_x[y] ?? null), symbol: 'none', lineStyle: { color: '#eb6834', width: 2.4 }, itemStyle: { color: '#eb6834' } },
      { name: 'Share of imports', type: 'line', data: ys.map((y) => p.share_m[y] ?? null), symbol: 'none', lineStyle: { color: '#2a78d6', width: 2 }, itemStyle: { color: '#2a78d6' } }];
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
    subtitle: 'Box size = export value (US$ billions); colour = Balassa RCA (blue above 1 = advantage, orange below 1). Click a sector to see its RCA over time; click again to drill into HS chapters. RCA here is measured against world exports of goods and services, so HS chapter values are lower than the goods-only RCAs in the HS chapter table later in this chapter.',
    source: d.source };
  const chart = cardShell(el, spec, { tall: true });
  el.querySelector('.extra').innerHTML = '<div class="panel" style="margin-top:8px"><h5 class="pt">Click a sector</h5><div class="mini"></div></div>';
  const mini = echarts.init(el.querySelector('.mini'));
  const years = Object.keys(d.years);
  // diverging around RCA = 1: blues for an advantage, oranges for a disadvantage
  const color = (r) => (r == null ? '#e9e8e3' : r >= 2 ? '#256abf' : r >= 1 ? '#86b6ef' : r >= .5 ? '#fbd2b8' : '#f5a77f');
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
    const cols = ECON;
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
  // diverging position index: oranges upstream (sells inputs), blues downstream (buys inputs)
  const col = (p) => (p > .1 ? '#eb6834' : p > 0 ? '#f5a77f' : p > -.1 ? '#86b6ef' : '#2a78d6');
  const draw = () => {
    const y = pickYear(years);
    badge(el, `Showing ${y}`);
    const n = d.network[y];
    const maxX = Math.max(...n.nodes.map((x) => x.exgr_bn));
    const nodes = n.nodes.map((x) => ({ id: x.id, name: x.name, value: x.exgr_bn, x0: x,
      symbolSize: 14 + 46 * Math.sqrt(x.exgr_bn / maxX),
      itemStyle: { color: x.id === 'SGP' ? ECON.SGP : col(x.position), borderColor: state.economy === x.id ? INK : '#fff', borderWidth: state.economy === x.id ? 3 : 1 },
      label: { show: true, color: INK, fontSize: 11 } }));
    const maxL = Math.max(...n.in.map((l) => l[1]), ...n.out.map((l) => l[1]));
    const links = [...n.in.map(([k, v]) => ({ source: k, target: 'SGP', value: v, dir: 'in' })), ...n.out.map(([k, v]) => ({ source: 'SGP', target: k, value: v, dir: 'out' }))]
      .map((l) => ({ ...l, lineStyle: { width: 0.8 + 7 * l.value / maxL, color: l.dir === 'in' ? '#1baf7a' : '#e34948', opacity: .5, curveness: .15 } }));
    const o = baseOption();
    o.tooltip.formatter = (p) => (p.dataType === 'edge'
      ? `<b>${esc(nameOf(p.data.source))} → ${esc(nameOf(p.data.target))}</b>, ${y}<br>Value added: <b>$${p.data.value.toFixed(1)}bn</b>${tipFooter(d.source)}`
      : `<b>${esc(p.name)}</b>, ${y}<br>Gross exports: <b>$${p.data.x0.exgr_bn.toFixed(0)}bn</b><br>Backward: <b>${p.data.x0.backward.toFixed(1)}%</b> · Forward: <b>${p.data.x0.forward.toFixed(1)}%</b><br>Position index: <b>${p.data.x0.position.toFixed(3)}</b> (${p.data.x0.position > 0 ? 'upstream' : 'downstream'})${tipFooter(d.source)}`);
    o.series = [{ type: 'graph', layout: 'force', roam: false, draggable: true, data: nodes, links,
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
    o.series = [mk('SGP', 0, 'Singapore backward', ECON.SGP), mk('SGP', 1, 'Singapore forward', ECON.SGP, true)];
    if (k !== 'SGP') o.series.push(mk(k, 0, `${d.names[k]} backward`, ECON[k] || '#6250d6'), mk(k, 1, `${d.names[k]} forward`, ECON[k] || '#6250d6', true));
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
  // ten largest sources or industries: the seven categorical slots, then lighter tints; 'All other' neutral;
  // pass-through hubs carry diagonal stripes so the holding-company caveat is visible in the chart itself
  const palette = [...CATEGORICAL, '#86b6ef', '#f5a77f', '#8fd8bc', '#c9b2f0'];
  const colorOf = (s, i) => (/^all other/i.test(s.name) ? '#cfc6b4' : palette[i % palette.length]);
  const stripes = { symbol: 'rect', dashArrayX: [1, 0], dashArrayY: [3, 4], rotation: Math.PI / 4, color: 'rgba(255,253,246,.7)' };
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
    o.tooltip.formatter = (raw) => {
      const ps = Array.isArray(raw) ? raw : [raw];
      if (ps[0].axisIndex === 1 || ps[0].seriesType === 'bar') return `<b>${esc(ps[0].name)}</b>, ${y}<br><b>${ps[0].value.toFixed(1)}%</b> of total${hubs.has(ps[0].name) ? '<br><i>Holding-company hub: immediate, not ultimate, investor</i>' : ''}${tipFooter(d.source)}`;
      return `<b>${ps[0].axisValue}</b>${ps.filter((x) => x.value != null).map((x) => `<div>${esc(x.seriesName)}: <b>S$${x.value.toFixed(0)}bn</b></div>`).join('')}${tipFooter(d.source)}`;
    };
    o.series = p.series.map((s, i) => ({ name: s.name, type: 'line', stack: 'a', areaStyle: { opacity: .85 }, symbol: 'none', xAxisIndex: 0, yAxisIndex: 0,
      data: s.values, lineStyle: { width: .5, color: '#fffdf6' }, itemStyle: { color: colorOf(s, i), decal: hubs.has(s.name) ? stripes : undefined },
      emphasis: { focus: 'series' } }));
    o.series[0].markLine = { symbol: 'none', silent: true, label: { show: false }, lineStyle: { color: INK, type: 'dashed' }, data: [{ xAxis: String(y) }] };
    const total = p.total[yi];
    o.series.push({ type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: p.series.map((s, i) => ({ value: s.values[yi] == null ? null : s.values[yi] / total * 100,
      itemStyle: { color: colorOf(s, i), decal: hubs.has(s.name) ? stripes : undefined, borderRadius: [0, 3, 3, 0] } })),
      label: { show: true, position: 'right', fontSize: 10.5, formatter: (q) => (q.value == null ? '' : `${q.value.toFixed(1)}%`) }, tooltip: { trigger: 'item' } });
    chart.setOption(o, true);
  };
  draw();
  on((s, ch) => { if (ch.includes('year')) draw(); });
}

// ---------- case study: sticky chart + text steps; the years mentioned in the active step are highlighted ----------

// ---------- infant industry learning curve: the course model with sliders, fitted to our own RCA evidence ----------
// Home productivity H(t) = A − B/t, t = years since support began; the foreign level is 1. Home overtakes foreign at
// t* = B / (A − 1), when support should end. "Fit to our data" sets t* to the year the BACI RCA in Figure 9.1 says
// the advantage arrived, keeping the chosen ceiling A.
export async function learnCurve(el) {
  const fig = await getJSON('data/figs/ch09_rca.json');
  const series = (name) => fig.series.find((s) => s.name === name);
  const yrs = fig.years;
  // finished pharma: first year after which the RCA stays above 1 to the end of the data
  const ph = series('Finished pharma').values;
  let phFrom = null;
  for (let i = yrs.length - 1; i >= 0 && ph[i] != null && ph[i] > 1; i--) phFrom = yrs[i];
  const chip0 = series('Chips').values.find((v) => v != null);
  const CASES = {
    chips: { label: 'Chips, support from 1968', start: 1968, color: ECON.SGP,
      tData: yrs[0] - 1968, note: `BACI starts in ${yrs[0]}, when the chip RCA was already ${chip0.toFixed(2)}, so the crossover came within ${yrs[0] - 1968} years. The fit uses that upper bound.` },
    pills: { label: 'Medicines, support from 2000', start: 2000, color: '#7c3aed',
      tData: phFrom - 2000, note: `The RCA in finished medicines has stayed above 1 every year since ${phFrom}, ${phFrom - 2000} years after the Biomedical Sciences Initiative.` },
  };
  const rcaNum = document.querySelector('[data-fig="ch09_rca"]')?.dataset.num || 'the RCA chart';
  const spec = { title: 'Try it: when should support have stopped?',
    subtitle: 'Home productivity H(t) = A − B/t, t in years since support began, against a foreign level of 1. Parameters are illustrative.',
    source: `Model: the infant industry learning function from the EC 391 lectures. Calibration: CEPII BACI HS92 V202601, revealed comparative advantage by product group (${rcaNum}), team calculation.` };
  const chart = cardShell(el, spec, {});
  el.querySelector('.tbl')?.remove();
  const p = { case: 'pills', A: 1.6, B: 12 };
  el.querySelector('.controls').innerHTML = `<div class="seg">${Object.entries(CASES).map(([k, c]) => `<button type="button" data-k="${k}"${k === p.case ? ' class="on"' : ''}>${c.label}</button>`).join('')}</div>`
    + `<div class="lc"><label>Learning ceiling A <output data-o="A"></output><input type="range" data-p="A" min="1.05" max="3" step="0.05"></label>`
    + `<label>Learning time B (higher is slower) <output data-o="B"></output><input type="range" data-p="B" min="1" max="60" step="1"></label>`
    + `<button type="button" class="fit">Fit to our data</button></div>`;
  el.querySelector('.extra').innerHTML = '<div class="lc-out"></div>';
  const out = el.querySelector('.lc-out');
  const sync = () => {
    el.querySelectorAll('[data-p]').forEach((i) => { i.value = p[i.dataset.p]; });
    el.querySelectorAll('[data-o]').forEach((o) => { o.textContent = p[o.dataset.o].toFixed(o.dataset.o === 'A' ? 2 : 0); });
    el.querySelectorAll('.seg button').forEach((b) => b.classList.toggle('on', b.dataset.k === p.case));
  };
  const draw = () => {
    const c = CASES[p.case];
    const tStar = p.B / (p.A - 1);
    const cross = c.start + tStar;
    const end = Math.max(2040, Math.ceil(cross) + 4);
    const xs = []; for (let y = c.start + 1; y <= end; y++) xs.push(y);
    const o = baseOption();
    o.grid = { left: 44, right: 74, top: 30, bottom: 30 };
    o.tooltip.trigger = 'axis';
    o.tooltip.valueFormatter = (v) => (v == null ? '' : v.toFixed(2));
    o.xAxis = { type: 'value', min: c.start, max: end, axisLabel: { formatter: (v) => String(v) }, splitLine: { show: false } };
    o.yAxis = { type: 'value', min: 0, max: Math.max(2, Math.ceil(p.A * 2) / 2),
      splitLine: { lineStyle: { color: LINE, type: 'dashed' } } };
    o.series = [
      { name: 'Home H(t)', type: 'line', showSymbol: false, data: xs.map((y) => [y, Math.max(0, p.A - p.B / (y - c.start))]), lineStyle: { color: c.color, width: 3 }, itemStyle: { color: c.color },
        endLabel: { show: true, formatter: 'Home', color: c.color, fontWeight: 600 },
        markLine: { silent: true, symbol: 'none', label: { formatter: (m) => m.name, color: INK, fontWeight: 600 }, lineStyle: { color: INK, type: 'dotted' },
          data: [{ name: `Crossover ${Math.round(cross)}`, xAxis: Math.min(cross, end) }] },
        markArea: { silent: true, itemStyle: { color: 'rgba(20,33,46,.05)' }, label: { show: true, position: 'insideTop', color: MUTED, formatter: 'today' },
          data: [[{ xAxis: 2025.5 }, { xAxis: 2026.5 }]] } },
      { name: 'Foreign', type: 'line', showSymbol: false, data: xs.map((y) => [y, 1]), lineStyle: { color: MUTED, width: 1.5, type: 'dashed' }, itemStyle: { color: MUTED },
        endLabel: { show: true, formatter: 'Foreign', color: MUTED } },
    ];
    chart.setOption(o, true);
    const ok = Math.abs(tStar - c.tData) < 0.5;
    out.innerHTML = `<p><b>Home overtakes foreign in ${Math.round(cross)}</b>, ${tStar.toFixed(1)} years after support began. `
      + `In the model support should end then, and the industry should export without it.</p>`
      + `<p class="lc-data">${ok ? '<b>Fitted to our data.</b> ' : ''}${c.note}</p>`;
  };
  el.querySelectorAll('[data-p]').forEach((i) => i.addEventListener('input', () => { p[i.dataset.p] = Number(i.value); sync(); draw(); }));
  el.querySelector('.seg').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) { p.case = b.dataset.k; sync(); draw(); } });
  el.querySelector('.fit').addEventListener('click', () => { p.B = Math.min(60, Math.max(1, Math.round(CASES[p.case].tData * (p.A - 1)))); sync(); draw(); });
  sync(); draw();
}
