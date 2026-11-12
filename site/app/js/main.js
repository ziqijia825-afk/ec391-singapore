// Page wiring: landing map, scroll-spy navigation, the global year control and lazy chart rendering.
import { state, set, YEARS } from './state.js';
import { renderFigure } from './chart.js';
import { landingMap, sgMap, wgiRadar, tradeSankey, rcaTreemap, gvcNetwork, fdiExplorer, scrolly } from './components.js';

const SPECIALS = { sgmap: sgMap, wgi: wgiRadar, sankey: tradeSankey, treemap: rcaTreemap, gvc: gvcNetwork, fdi: fdiExplorer };

function enter() {
  document.getElementById('content').scrollIntoView({ behavior: 'smooth' });
}

// lazy rendering: draw a chart when its card comes near the viewport
const io = new IntersectionObserver((entries) => entries.forEach((e) => {
  if (!e.isIntersecting) return;
  io.unobserve(e.target);
  const el = e.target;
  const job = el.dataset.fig ? renderFigure(el, el.dataset.fig) : SPECIALS[el.dataset.special]?.(el);
  Promise.resolve(job).catch((err) => { console.error(err); el.classList.add('card'); el.insertAdjacentHTML('beforeend', `<p class="hint">Chart could not load (${err.message}).</p>`); });
}), { rootMargin: '600px 0px' });

function setupNav() {
  const links = [...document.querySelectorAll('#nav a')];
  const byId = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
  const spy = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    links.forEach((a) => a.classList.remove('on'));
    const a = byId.get(e.target.id);
    if (a) { a.classList.add('on'); a.scrollIntoView({ block: 'nearest', inline: 'center', behavior: 'smooth' }); }
  }), { rootMargin: '-45% 0px -50% 0px' });
  document.querySelectorAll('section.chapter').forEach((s) => spy.observe(s));
}

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
  landingMap(document.getElementById('landing-map'), enter).catch(console.error);
  document.getElementById('enter').addEventListener('click', enter);
  setupNav();
  setupTime();
  document.querySelectorAll('[data-fig], [data-special]').forEach((el) => io.observe(el));
  document.querySelectorAll('.scrolly').forEach(scrolly);
});
