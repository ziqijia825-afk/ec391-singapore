// Page wiring: the poster cover with its map, the book of chapters, and the global year control.
import { state, set, YEARS } from './state.js';
import { landingMap, sgMap, wgiRadar, tradeSankey, rcaTreemap, gvcNetwork, fdiExplorer } from './components.js';
import { initBook } from './book.js';

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
  const book = initBook(SPECIALS);
  const cover = document.getElementById('landing');
  let opened = false;
  const open = (animate = true) => {
    if (document.body.classList.contains('reading')) return;
    if (animate && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
      cover.animate([{ transform: 'perspective(1800px) rotateY(0deg)', opacity: 1 }, { transform: 'perspective(1800px) rotateY(-75deg)', opacity: 0 }],
        { duration: 650, easing: 'ease-in' }).finished.then(() => { document.body.classList.add('reading'); if (!opened) { book.open(); opened = true; } });
    } else {
      document.body.classList.add('reading');
      if (!opened) { book.open(); opened = true; }
    }
  };
  const close = () => { document.body.classList.remove('reading'); history.replaceState(null, '', '#cover'); };
  landingMap(document.getElementById('landing-map'), () => open()).catch(console.error);
  document.getElementById('enter').addEventListener('click', () => open());
  document.addEventListener('click', (e) => { if (e.target.closest('a[href="#cover"]')) { e.preventDefault(); close(); } });
  setupTime();
  const topbar = document.getElementById('topbar');
  new ResizeObserver(() => document.documentElement.style.setProperty('--tb', `${topbar.offsetHeight}px`)).observe(topbar);
  if (book.hasTarget) open(false);
});
