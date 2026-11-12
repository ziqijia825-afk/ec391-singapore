// The report as a picture book: two-page spreads (one page at a time on phones), turned with a 3D page flip.
import { renderFigure } from './chart.js';

const DUR = 420;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const singleMQ = matchMedia('(max-width: 820px)');

export function initBook(specials) {
  const book = document.getElementById('book');
  const spreads = [...book.querySelectorAll('.spread')];
  const firstOf = new Map();
  spreads.forEach((sp, i) => { if (!firstOf.has(sp.dataset.ch)) firstOf.set(sp.dataset.ch, i); });
  const navLinks = [...document.querySelectorAll('#nav a')];
  let single = singleMQ.matches;
  let list = [];
  let idx = 0;
  let busy = false;

  // ---------- positions: spreads on wide screens, single pages on phones ----------
  function buildList() {
    list = [];
    spreads.forEach((sp, s) => {
      if (!single) { list.push({ s, sp, pages: [...sp.querySelectorAll('.page')] }); return; }
      sp.querySelectorAll('.page').forEach((pg) => {
        if (sp.classList.contains('plate') && pg.classList.contains('right')) return; // decorative plate: skip on phones
        list.push({ s, sp, pages: [pg] });
      });
    });
  }
  const indexOfSpread = (s, right = false) => {
    const hits = list.map((e, i) => [e, i]).filter(([e]) => e.s === s);
    if (!hits.length) return 0;
    return (right && hits.length > 1 ? hits[hits.length - 1] : hits[0])[1];
  };

  // ---------- lazy rendering of the charts on the pages being shown ----------
  const run = (el) => {
    if (el.dataset.done) return;
    el.dataset.done = '1';
    const job = el.dataset.fig ? renderFigure(el, el.dataset.fig) : specials[el.dataset.special]?.(el);
    Promise.resolve(job).catch((err) => { console.error(err); el.classList.add('card'); el.insertAdjacentHTML('beforeend', `<p class="hint">Chart could not load (${err.message}).</p>`); });
  };
  const renderIn = (root) => root.querySelectorAll('[data-fig], [data-special]').forEach((el) => {
    const closed = el.closest('details:not([open])');
    if (!closed) run(el);
  });
  document.addEventListener('toggle', (e) => { if (e.target.open) renderIn(e.target); }, true);

  function show(e, z) {
    e.sp.classList.add('vis');
    e.sp.style.zIndex = z;
    if (single) e.pages.forEach((p) => { p.classList.add('pg-vis'); p.style.zIndex = z; });
    e.pages.forEach(renderIn);
  }
  function hide(e) {
    e.pages.forEach((p) => { p.classList.remove('pg-vis'); p.style.zIndex = ''; p.style.transform = ''; p.getAnimations().forEach((a) => a.cancel()); });
    if (!list.some((x, i) => i === idx && x.sp === e.sp)) { e.sp.classList.remove('vis'); e.sp.style.zIndex = ''; }
    e.sp.getAnimations().forEach((a) => a.cancel());
  }
  const anim = (el, frames, opts = {}) => el.animate(frames, { duration: DUR, easing: 'ease-in-out', fill: 'forwards', ...opts }).finished;

  async function flipDouble(A, B, dir) {
    const a = A.sp, b = B.sp;
    if (a.classList.contains('wide') || b.classList.contains('wide')) {  // two-page pictures slide instead of folding
      show(B, 1); a.style.zIndex = 2;
      await anim(a, [{ opacity: 1, transform: 'none' }, { opacity: 0, transform: `translateX(${-dir * 4}%) rotateY(${dir * 10}deg)` }], { duration: 360 });
      return;
    }
    const out = a.querySelector(dir > 0 ? '.page.right' : '.page.left');
    const inn = b.querySelector(dir > 0 ? '.page.left' : '.page.right');
    inn.style.transform = `rotateY(${dir > 0 ? 90 : -90}deg)`;
    show(B, 1); a.style.zIndex = 2;
    await anim(out, [{ transform: 'rotateY(0deg)', filter: 'brightness(1)' }, { transform: `rotateY(${dir > 0 ? -90 : 90}deg)`, filter: 'brightness(.75)' }], { easing: 'ease-in' });
    b.style.zIndex = 3;
    await anim(inn, [{ transform: `rotateY(${dir > 0 ? 90 : -90}deg)`, filter: 'brightness(.75)' }, { transform: 'rotateY(0deg)', filter: 'brightness(1)' }], { easing: 'ease-out' });
    inn.style.transform = '';
    inn.getAnimations().forEach((x) => x.cancel());
  }

  async function flipSingle(A, B, dir) {
    const out = A.pages[0], inn = B.pages[0];
    if (dir > 0) {
      show(B, 1); A.sp.style.zIndex = Math.max(2, Number(A.sp.style.zIndex)); out.style.zIndex = 2;
      if (A.sp === B.sp) { inn.style.zIndex = 1; }
      await anim(out, [{ transform: 'rotateY(0deg)', opacity: 1 }, { transform: 'rotateY(-100deg)', opacity: 0.4 }], { easing: 'ease-in' });
    } else {
      inn.style.transform = 'rotateY(-100deg)';
      show(B, 3); out.style.zIndex = 2;
      await anim(inn, [{ transform: 'rotateY(-100deg)', opacity: 0.4 }, { transform: 'rotateY(0deg)', opacity: 1 }], { easing: 'ease-out' });
      inn.style.transform = '';
      inn.getAnimations().forEach((x) => x.cancel());
    }
  }

  async function go(to, { instant = false } = {}) {
    to = Math.max(0, Math.min(list.length - 1, to));
    if (busy || to === idx) return;
    const A = list[idx], B = list[to], dir = to > idx ? 1 : -1;
    idx = to;
    if (instant || reduceMotion) { hide(A); show(B, 2); return after(); }
    busy = true;
    try { await (single ? flipSingle(A, B, dir) : flipDouble(A, B, dir)); } catch (err) { console.error(err); }
    if (A.sp !== B.sp) hide(A); else A.pages.forEach((p) => { if (!B.pages.includes(p)) { p.classList.remove('pg-vis'); p.getAnimations().forEach((x) => x.cancel()); p.style.zIndex = ''; } });
    B.sp.style.zIndex = 2; B.sp.getAnimations().forEach((x) => x.cancel());
    B.pages.forEach((p) => { p.style.zIndex = 2; });
    busy = false;
    after();
  }

  // ---------- chrome: page number, progress, chapter tabs, address bar ----------
  const pageno = document.getElementById('pageno');
  const bar = document.querySelector('#pager .progress i');
  const prevBtn = document.querySelector('.turn.prev');
  const nextBtn = document.querySelector('.turn.next');
  function after() {
    const e = list[idx];
    const folios = e.pages.map((p) => p.querySelector('.folio')?.textContent).filter(Boolean);
    const last = spreads.length * 2;
    const label = folios.join(' and ');
    pageno.textContent = `${label.includes(' and ') ? 'Pages' : 'Page'} ${label} of ${last}`;
    bar.style.width = `${((idx + 1) / list.length) * 100}%`;
    prevBtn.disabled = idx === 0; nextBtn.disabled = idx === list.length - 1;
    const ch = e.sp.dataset.ch;
    navLinks.forEach((a) => {
      const on = a.getAttribute('href') === `#${ch}`;
      a.classList.toggle('on', on);
      if (on) a.scrollIntoView({ block: 'nearest', inline: 'center' });
    });
    const side = single && e.pages[0].classList.contains('right') ? '-r' : '';
    history.replaceState(null, '', `#${e.sp.id}${side}`);
  }

  function target(hash) {
    const h = decodeURIComponent(hash.replace(/^#/, ''));
    const m = h.match(/^p(\d+)(-r)?$/);
    if (m) { const s = spreads.findIndex((sp) => sp.id === `p${m[1]}`); if (s >= 0) return indexOfSpread(s, !!m[2]); }
    if (firstOf.has(h)) return indexOfSpread(firstOf.get(h));
    return null;
  }
  const goHash = (hash, opts) => { const t = target(hash); if (t != null) go(t, opts); return t != null; };

  // ---------- input: buttons, keys, swipes, links ----------
  prevBtn.addEventListener('click', () => go(idx - 1));
  nextBtn.addEventListener('click', () => go(idx + 1));
  document.addEventListener('keydown', (e) => {
    if (!document.body.classList.contains('reading') || e.target.closest('input, textarea, select')) return;
    if (['ArrowRight', 'PageDown'].includes(e.key)) { e.preventDefault(); go(idx + 1); }
    if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); go(idx - 1); }
    if (e.key === 'Home') go(0);
    if (e.key === 'End') go(list.length - 1);
  });
  let touch = null;
  book.addEventListener('pointerdown', (e) => {
    touch = e.target.closest('.card, [data-special], .tablewrap, canvas') ? null : { x: e.clientX, y: e.clientY };
  });
  book.addEventListener('pointerup', (e) => {
    if (!touch) return;
    const dx = e.clientX - touch.x, dy = e.clientY - touch.y;
    touch = null;
    if (Math.abs(dx) > 60 && Math.abs(dy) < 50) go(idx + (dx < 0 ? 1 : -1));
  });
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    const page = href.match(/^(\w+)\.html$/);
    const hash = page ? `#${page[1] === 'index' ? 'intro' : page[1]}` : href.startsWith('#') ? href : null;
    if (!hash || hash === '#cover') return;
    if (target(hash) != null) { e.preventDefault(); goHash(hash); }
  });
  window.addEventListener('hashchange', () => goHash(location.hash));

  singleMQ.addEventListener('change', () => {
    const s = list[idx].s;
    list.forEach(hide);
    single = singleMQ.matches;
    document.body.classList.toggle('single', single);
    buildList();
    idx = indexOfSpread(s);
    show(list[idx], 2);
    after();
  });

  // ---------- start ----------
  document.body.classList.toggle('single', single);
  buildList();
  const start = target(location.hash);
  idx = start ?? 0;
  return {
    open() { show(list[idx], 2); after(); },
    hasTarget: start != null,
  };
}
