// Generic interactive renderers for the figure specs written by scripts/chart_style.py.
// Each spec carries the same numbers, labels, units and source line as the static PNG.
import { state, on, getJSON, YEARS } from './state.js';

const INK = '#1d2b33', MUTED = '#4f5b62', LINE = '#e6dcc4', BLUE = '#2a78d6';
// one colour per economy in every chart (same as scripts/chart_style.py), a fixed categorical order for the rest
export const ECON = { SGP: '#e34948', MYS: '#2a78d6', HKG: '#eda100', VNM: '#008300', EAS: '#7d7468', WLD: '#a89f90' };
export const CATEGORICAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6'];
export const rgba = (hex, a) => `rgba(${[1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16)).join(',')},${a})`;
export const registry = new Map(); // figure id -> echarts instance (for cross-chart highlighting)
let NAMES = {};
getJSON('data/names.json').then((n) => { NAMES = n; }).catch(() => {});
export const nameOf = (k) => NAMES[k] || k;

export function shortSource(src) {
  const s = src.replace(/^Source:\s*/, '');
  const cut = s.search(/, (retrieved|downloaded)/);
  return cut > 0 ? s.slice(0, cut) : s.split('. ')[0];
}

const esc = (t) => String(t ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
export const tipFooter = (src) => `<div style="margin-top:6px;color:${MUTED};font-size:11px;max-width:280px;white-space:normal">Source: ${esc(shortSource(src))}</div>`;

export const baseOption = () => ({
  animationDuration: 500,
  textStyle: { fontFamily: 'Nunito, system-ui, -apple-system, Segoe UI, sans-serif', color: MUTED },
  tooltip: { backgroundColor: '#fffdf6', borderColor: INK, borderWidth: 2, textStyle: { color: INK, fontSize: 12.5, fontFamily: 'Nunito, sans-serif' },
    confine: true, extraCssText: 'box-shadow:3px 3px 0 #1d2b33;border-radius:10px;' },
});

// ---------- card shell: title, subtitle, plot, source line, data table, PNG link ----------
export function cardShell(el, spec, { tall = false, badge = '' } = {}) {
  el.classList.add('card');
  el.innerHTML = `
    ${badge ? `<span class="badge">${esc(badge)}</span>` : ''}
    <h4>${el.dataset.num ? `<span class="fignum">${esc(el.dataset.num)}</span> ` : ''}${esc(spec.title)}</h4><div class="sub">${esc(spec.subtitle)}</div>
    <div class="controls"></div>
    <div class="plot${tall ? ' tall' : ''}" role="img" aria-label="${esc(spec.title)}"></div>
    <div class="extra"></div>
    <div class="foot"><div class="src">${esc(spec.source)}</div>
      <div class="actions"><button type="button" class="tbl">Data</button>
      ${spec.png ? `<a class="btn" href="${spec.png}" download>PNG</a>` : ''}</div></div>
    <div class="data"></div>`;
  const dataBox = el.querySelector('.data');
  el.querySelector('.tbl').addEventListener('click', () => {
    if (!dataBox.innerHTML) dataBox.innerHTML = dataTable(spec);
    dataBox.classList.toggle('open');
  });
  const chart = echarts.init(el.querySelector('.plot'), null, { renderer: 'canvas' });
  new ResizeObserver(() => chart.resize()).observe(el.querySelector('.plot'));
  return chart;
}

function dataTable(spec) {
  const td = (v) => `<td>${esc(v ?? '')}</td>`;
  if (spec.kind === 'line') {
    const head = `<tr><th>Year</th>${spec.series.map((s) => `<th>${esc(s.name)}</th>`).join('')}</tr>`;
    const rows = spec.years.map((y, i) => `<tr><td>${y}</td>${spec.series.map((s) => td(s.labels[i])).join('')}</tr>`);
    return `<table>${head}${rows.join('')}</table>`;
  }
  if (spec.kind === 'bar') return `<table>${spec.cats.map((c, i) => `<tr><td>${esc(c)}</td>${td(spec.labels[i])}</tr>`).join('')}</table>`;
  if (spec.kind === 'grouped') {
    const head = `<tr><th></th>${spec.series.map((s) => `<th>${esc(s.name)}</th>`).join('')}</tr>`;
    return `<table>${head}${spec.cats.map((c, i) => `<tr><td>${esc(c)}</td>${spec.series.map((s) => td(s.labels[i])).join('')}</tr>`).join('')}</table>`;
  }
  if (spec.kind === 'stacked') {
    const head = `<tr><th></th>${spec.parts.map((p) => `<th>${esc(p.name)}</th>`).join('')}</tr>`;
    return `<table>${head}${spec.rows.map((r, i) => `<tr><td>${esc(r)}</td>${spec.parts.map((p) => td(p.values[i] == null ? '' : p.values[i].toFixed(1) + '%')).join('')}</tr>`).join('')}</table>`;
  }
  if (spec.kind === 'radar') {
    const head = `<tr><th></th>${spec.series.map((s) => `<th>${esc(s.name)}</th>`).join('')}</tr>`;
    return `<table>${head}${spec.dims.map((d, i) => `<tr><td>${esc(d)}</td>${spec.series.map((s) => td(s.values[i]?.toFixed(1))).join('')}</tr>`).join('')}</table>`;
  }
  if (spec.kind === 'scatter') return `<table><tr><th>Economy</th><th>${esc(spec.xlabel)}</th><th>${esc(spec.ylabel)}</th></tr>${spec.points.map((p) => `<tr><td>${esc(nameOf(p.key))}</td>${td(p.x?.toFixed(2))}${td(p.y?.toFixed(2))}</tr>`).join('')}</table>`;
  return '';
}

// ---------- line ----------
function lineOption(spec, narrow = false) {
  const o = baseOption();
  const longRun = spec.years[0] < YEARS.min - 2;
  o.grid = narrow ? { left: 50, right: 14, top: 44, bottom: 30 } : { left: 64, right: 150, top: 18, bottom: 34 };
  if (narrow) o.legend = { top: 0, left: 0, itemWidth: 12, itemHeight: 8, textStyle: { fontSize: 10.5 }, data: spec.series.map((s) => s.name) };
  o.xAxis = { type: 'value', min: spec.years[0], max: spec.years[spec.years.length - 1], minInterval: 1,
    axisLabel: { formatter: (v) => String(v) }, splitLine: { show: false }, axisLine: { lineStyle: { color: '#c9c8c1' } } };
  o.yAxis = { type: spec.logy ? 'log' : 'value', name: narrow ? '' : spec.ylabel, nameLocation: 'middle', nameGap: 48,
    nameTextStyle: { color: MUTED }, scale: spec.ymin === null, min: spec.ymin === null || spec.logy ? undefined : spec.ymin,
    splitLine: { lineStyle: { color: LINE } } };
  o.tooltip.trigger = 'axis';
  o.tooltip.formatter = (ps) => {
    const i = spec.years.indexOf(ps[0].value[0]);
    const rows = spec.series.filter((s) => s.labels[i] != null)
      .map((s) => `<div><span style="color:${s.color}">●</span> ${esc(s.name)}: <b>${esc(s.labels[i])}</b></div>`);
    return `<b>${ps[0].value[0]}</b>${rows.join('')}${tipFooter(spec.source)}`;
  };
  o.series = spec.series.map((s) => ({
    id: s.key, name: s.name, type: 'line', symbol: 'none', step: spec.step ? 'end' : false,
    data: spec.years.map((y, i) => [y, s.values[i]]).filter((d) => d[1] != null),
    lineStyle: { color: s.color, width: s.focus ? 3 : 1.8, type: s.dashed ? 'dashed' : 'solid' },
    itemStyle: { color: s.color }, z: s.focus ? 5 : 2,
    emphasis: { focus: 'series' },
    endLabel: { show: !narrow, formatter: () => `${s.name}  ${s.labels[s.labels.length - 1 - [...s.labels].reverse().findIndex((l) => l != null)] ?? ''}`,
      color: s.focus ? INK : MUTED, fontWeight: s.focus ? 700 : 400, fontSize: 12 },
  }));
  const marks = (spec.events || []).map(([x, t]) => ({ xAxis: x, label: { formatter: t, position: 'insideEndTop', color: MUTED, fontSize: 11 } }));
  o.series.push({ id: '__year', type: 'line', data: [], silent: true,
    markLine: { symbol: 'none', silent: true, lineStyle: { color: '#b3b2ab', type: 'dotted' }, data: marks } });
  if (spec.zero_line) o.series.push({ id: '__zero', type: 'line', data: [], silent: true,
    markLine: { symbol: 'none', silent: true, lineStyle: { color: '#8a8a85', type: 'solid', width: 1 }, label: { show: false }, data: [{ yAxis: 0 }] } });
  o.__longRun = longRun;
  return o;
}

// Line charts follow the global year control: the visible window ends at the selected year (the series "grow"
// as the slider moves), except for long-run charts, which only get a marker.
function lineFollow(chart, spec, o) {
  const apply = () => {
    const last = spec.years[spec.years.length - 1];
    const marks = (spec.events || []).map(([x, t]) => ({ xAxis: x, label: { formatter: t, position: 'insideEndTop', color: MUTED, fontSize: 11 } }));
    const y = Math.min(state.year, last);
    const yearMark = { xAxis: y, lineStyle: { color: INK, type: 'dashed', opacity: .3 }, label: { show: false } };
    const opt = { series: [{ id: '__year', markLine: { data: [...marks, yearMark] } }] };
    if (!o.__longRun && spec.years[0] >= YEARS.min - 2) {
      const end = Math.max(Math.min(state.year, last), spec.years[0] + 2);
      opt.xAxis = { max: end };
      // series end at the selected year, and their end labels show that year's value
      spec.series.forEach((s) => {
        const idx = spec.years.reduce((k, yy, i) => (yy <= end && s.values[i] != null ? i : k), -1);
        opt.series.push({ id: s.key, data: spec.years.map((yy, i) => [yy, s.values[i]]).filter((d) => d[1] != null && d[0] <= end),
          endLabel: { formatter: () => `${s.name}  ${idx >= 0 ? s.labels[idx] : ''}` } });
      });
    }
    chart.setOption(opt);
  };
  apply();
  on((s, changed) => { if (changed.includes('year')) apply(); });
}

// ---------- bars ----------
function barOption(spec) {
  const o = baseOption();
  o.grid = { left: 10, right: 70, top: 10, bottom: 30, containLabel: true };
  o.xAxis = { type: 'value', name: spec.xlabel, nameLocation: 'middle', nameGap: 26, splitLine: { lineStyle: { color: LINE } } };
  o.yAxis = { type: 'category', inverse: true, data: spec.cats, axisTick: { show: false },
    axisLabel: { color: INK, width: 220, overflow: 'break' } };
  o.tooltip.trigger = 'item';
  o.tooltip.formatter = (p) => `<b>${esc(p.name)}</b><br>${esc(spec.labels[p.dataIndex])}${tipFooter(spec.source)}`;
  o.series = [{ type: 'bar', barWidth: '62%', data: spec.values.map((v, i) => ({ value: v, itemStyle: { color: spec.colors[i], borderRadius: [0, 3, 3, 0] } })),
    label: { show: true, position: 'right', color: MUTED, formatter: (p) => spec.labels[p.dataIndex] },
    emphasis: { itemStyle: { borderColor: INK, borderWidth: 1.5 } },
    markLine: spec.ref == null ? undefined : { symbol: 'none', lineStyle: { color: '#8a8a85', type: 'dashed' },
      label: { formatter: spec.ref_label || '', color: MUTED }, data: [{ xAxis: spec.ref }] } }];
  return o;
}

function groupedOption(spec) {
  const o = baseOption();
  o.grid = { left: 10, right: 50, top: 34, bottom: 30, containLabel: true };
  o.legend = { top: 0, left: 0, itemWidth: 12, itemHeight: 10, textStyle: { color: INK } };
  o.xAxis = { type: 'value', name: spec.xlabel, nameLocation: 'middle', nameGap: 26, splitLine: { lineStyle: { color: LINE } } };
  o.yAxis = { type: 'category', inverse: true, data: spec.cats, axisTick: { show: false }, axisLabel: { color: INK, width: 210, overflow: 'break' } };
  o.tooltip.trigger = 'axis';
  o.tooltip.axisPointer = { type: 'shadow' };
  o.tooltip.formatter = (ps) => `<b>${esc(ps[0].name)}</b>${ps.map((p) => `<div><span style="color:${p.color}">●</span> ${esc(p.seriesName)}: <b>${esc(spec.series[p.seriesIndex].labels[p.dataIndex] ?? 'n/a')}</b></div>`).join('')}${tipFooter(spec.source)}`;
  o.series = spec.series.map((s) => ({ name: s.name, type: 'bar', data: s.values, itemStyle: { color: s.color, borderRadius: [0, 2, 2, 0] },
    barGap: '8%', label: { show: spec.cats.length * spec.series.length <= 28, position: 'right', fontSize: 10.5, color: MUTED,
      formatter: (p) => s.labels[p.dataIndex] ?? '' } }));
  if (spec.ref != null) o.series[0].markLine = { symbol: 'none', lineStyle: { color: '#8a8a85', type: 'dashed' }, label: { show: false }, data: [{ xAxis: spec.ref }] };
  return o;
}

function stackedOption(spec) {
  const o = baseOption();
  o.grid = { left: 10, right: 20, top: 70, bottom: 30, containLabel: true };
  o.legend = { top: 0, left: 0, itemWidth: 12, itemHeight: 10, textStyle: { color: INK, fontSize: 11.5 } };
  o.xAxis = { type: 'value', max: 100, axisLabel: { formatter: '{value}%' }, splitLine: { lineStyle: { color: LINE } } };
  o.yAxis = { type: 'category', inverse: true, data: spec.rows, axisTick: { show: false }, axisLabel: { color: INK } };
  o.tooltip.trigger = 'item';
  o.tooltip.formatter = (p) => `<b>${esc(p.seriesName)}</b>, ${esc(p.name)}<br><b>${p.value?.toFixed(1)}%</b> of total${tipFooter(spec.source)}`;
  const dark = new Set(['#2a78d6', '#4f8fdd', '#5f5e5a', '#8a8a85', '#6aa3e5']);
  o.series = spec.parts.map((p) => ({ name: p.name, type: 'bar', stack: 'all', barWidth: '58%', data: p.values,
    itemStyle: { color: p.color, borderColor: '#fff', borderWidth: 1 }, emphasis: { focus: 'series' },
    label: { show: true, formatter: (d) => (d.value >= 4 ? `${Math.round(d.value)}%` : ''), color: dark.has(p.color) ? '#fff' : INK, fontSize: 11 } }));
  return o;
}

export function radarOption(dims, series, vmax, tipRows) {
  const o = baseOption();
  o.legend = { bottom: 0, itemWidth: 12, itemHeight: 10, textStyle: { color: INK } };
  o.radar = { radius: '64%', center: ['50%', '48%'], indicator: dims.map((d) => ({ name: d, max: vmax })),
    axisName: { color: INK, fontSize: 12 }, splitLine: { lineStyle: { color: LINE } }, splitArea: { show: false },
    axisLine: { lineStyle: { color: LINE } } };
  o.tooltip.trigger = 'item';
  o.tooltip.formatter = tipRows;
  o.series = [{ type: 'radar', symbolSize: 5, data: series.map((s, j) => ({ name: s.name, value: s.values,
    lineStyle: { color: s.color, width: j === 0 ? 3 : 1.6, type: s.dashed ? 'dashed' : 'solid' }, itemStyle: { color: s.color },
    areaStyle: j === 0 ? { color: rgba(s.color, 0.14) } : undefined })) }];
  return o;
}

function scatterOption(spec) {
  const o = baseOption();
  o.grid = { left: 64, right: 30, top: 16, bottom: 50 };
  o.xAxis = { type: spec.logx ? 'log' : 'value', name: spec.xlabel, nameLocation: 'middle', nameGap: 30, splitLine: { lineStyle: { color: LINE } }, scale: true };
  o.yAxis = { type: 'value', name: spec.ylabel, nameLocation: 'middle', nameGap: 44, splitLine: { lineStyle: { color: LINE } }, scale: true };
  o.tooltip.trigger = 'item';
  o.tooltip.formatter = (p) => p.seriesType === 'scatter'
    ? `<b>${esc(nameOf(p.data.key))}</b><br>${esc(spec.xlabel)}: <b>${p.value[0].toLocaleString(undefined, { maximumFractionDigits: 1 })}</b><br>${esc(spec.ylabel)}: <b>${p.value[1].toFixed(2)}</b>${tipFooter(spec.source)}`
    : '';
  const ann = new Set(spec.annotate), hi = new Set(spec.highlight);
  o.series = [{ type: 'scatter', symbolSize: (v, p) => (hi.has(p.data.key) ? 12 : 8),
    data: spec.points.map((p) => ({ value: [p.x, p.y], key: p.key, name: p.key,
      itemStyle: ann.has(p.key) || hi.has(p.key) ? { color: ECON[p.key] || '#eb6834', borderColor: '#fffdf6', borderWidth: 1.2 }
        : { color: '#a9c8ee', borderColor: '#5598e7', borderWidth: .6 },
      label: { show: ann.has(p.key), formatter: () => nameOf(p.key), position: 'right', fontSize: 11, color: hi.has(p.key) ? INK : MUTED } })),
    emphasis: { scale: 1.8, itemStyle: { color: '#eb6834', borderColor: INK } } }];
  if (spec.fit) {
    const xs = spec.points.map((p) => p.x).filter((x) => x > 0);
    const lo = Math.min(...xs), hiX = Math.max(...xs);
    const line = Array.from({ length: 40 }, (_, i) => { const x = spec.logx ? lo * (hiX / lo) ** (i / 39) : lo + (hiX - lo) * i / 39;
      return [x, spec.fit[0] + spec.fit[1] * (spec.logx ? Math.log(x) : x)]; });
    o.series.push({ type: 'line', data: line, symbol: 'none', silent: true, lineStyle: { color: MUTED, type: 'dashed', width: 1.2 } });
  }
  return o;
}

export async function renderFigure(el, id) {
  const spec = await getJSON(`data/figs/${id}.json`);
  const tall = (spec.kind === 'bar' && spec.cats.length > 10) || (spec.kind === 'grouped' && spec.cats.length * spec.series.length > 24) || spec.kind === 'radar';
  const chart = cardShell(el, spec, { tall });
  if (spec.kind === 'grouped' && spec.cats.length * spec.series.length > 36) el.querySelector('.plot').style.height = `${Math.min(900, 80 + spec.cats.length * spec.series.length * 15)}px`;
  if (spec.kind === 'bar' && spec.cats.length > 12) el.querySelector('.plot').style.height = `${80 + spec.cats.length * 30}px`;
  let o;
  const narrow = el.clientWidth < 560;
  if (spec.kind === 'line') o = lineOption(spec, narrow);
  else if (spec.kind === 'bar') o = barOption(spec);
  else if (spec.kind === 'grouped') o = groupedOption(spec);
  else if (spec.kind === 'stacked') o = stackedOption(spec);
  else if (spec.kind === 'scatter') o = scatterOption(spec);
  else if (spec.kind === 'radar') o = radarOption(spec.dims, spec.series, spec.vmax, () => '');
  chart.setOption(o);
  chart.resize();
  if (spec.kind === 'line') lineFollow(chart, spec, o);
  registry.set(id, chart);
  return { chart, spec };
}
