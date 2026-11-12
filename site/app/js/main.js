// Page wiring: the cover chart, the column of screens, and the global year control.
import { state, set, YEARS, getJSON } from './state.js';
import { coverMap, sgMap, wgiRadar, tradeSankey, rcaTreemap, gvcNetwork, fdiExplorer } from './components.js';
import { initStory } from './story.js';
import { enhance } from './enhance.js';
import { ICON } from './icons.js';

const SPECIALS = { sgmap: sgMap, wgi: wgiRadar, sankey: tradeSankey, treemap: rcaTreemap, gvc: gvcNetwork, fdi: fdiExplorer };

function setupTime() {
  const input = document.getElementById('year');
  const out = document.getElementById('yearout');
  const play = document.getElementById('play');
  input.min = YEARS.min; input.max = YEARS.max; input.value = state.year;
  const show = () => { out.textContent = state.year; input.value = state.year; };
  input.addEventListener('input', () => { set({ year: Number(input.value) }); show(); });
  let timer = null;
  play.addEventListener('click', () => {
    if (timer) { clearInterval(timer); timer = null; play.textContent = '▶'; return; }
    if (state.year >= YEARS.max) set({ year: YEARS.min });
    play.textContent = '❚❚';
    timer = setInterval(() => {
      if (state.year >= YEARS.max) { clearInterval(timer); timer = null; play.textContent = '▶'; return; }
      set({ year: state.year + 1 }); show();
    }, 700);
  });
  show();
}

document.addEventListener('DOMContentLoaded', () => {
  const topbar = document.getElementById('topbar');
  const setTb = () => document.documentElement.style.setProperty('--tb', `${topbar.offsetHeight}px`);
  setTb();
  new ResizeObserver(setTb).observe(topbar);
  coverMap(document.getElementById('cover-map'), document.getElementById('cover-kpis')).catch(console.error);
  // key numbers that stay in view under the top bar, each with its own icon
  const icons = [ICON.gdp, ICON.income, ICON.trade, ICON.fdi, ICON.hdi, ICON.gov];
  getJSON('data/kpis.json').then((k) => {
    const short = (l) => l.replace(/, (19|20)\d\d$/, '').replace('GDP per person, PPP', 'per person (PPP)').replace('Human Development Index', 'HDI')
      .replace('Government effectiveness', 'gov. effectiveness').replace('FDI inflows, % of GDP', 'FDI / GDP').replace('Trade, % of GDP', 'trade / GDP');
    document.getElementById('kpistrip').innerHTML = k.kpis.map((x, i) => `<span class="ks" title="${x.label}: ${x.value}${x.rank?.rank ? `, rank ${x.rank.rank} of ${x.rank.n}` : ''}">`
      + `${icons[i] || ''}<b>${x.value.replace('/100', '')}</b><em>${short(x.label)}</em>${x.rank?.rank ? `<small>#${x.rank.rank}</small>` : ''}</span>`).join('');
  }).catch(console.error);
  // contents drawer
  const drawer = document.getElementById('contents');
  const openBtn = document.getElementById('ct-open');
  const toggle = (open) => { drawer.hidden = !open; openBtn.setAttribute('aria-expanded', String(open)); document.body.classList.toggle('ct-on', open); };
  openBtn.addEventListener('click', () => toggle(drawer.hidden));
  document.getElementById('ct-close').addEventListener('click', () => toggle(false));
  drawer.addEventListener('click', (e) => { if (e.target === drawer || e.target.closest('a')) toggle(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !drawer.hidden) toggle(false); });
  enhance();
  initStory(SPECIALS);
  setupTime();
});
