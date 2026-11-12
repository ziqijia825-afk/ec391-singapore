// The report as a column of screens: one question per screen, text on the left and its chart on the right.
// Charts render as they come near the viewport; the chapter tab, address and progress bar follow the reader.
import { renderFigure, sleepWhenHidden } from './chart.js';

export function initStory(specials) {
  const spreads = [...document.querySelectorAll('#story .spread')];
  const navLinks = [...document.querySelectorAll('#nav a')];
  const bar = document.querySelector('#topbar .progress i');
  const firstOf = new Map();
  spreads.forEach((sp) => { if (!firstOf.has(sp.dataset.ch)) firstOf.set(sp.dataset.ch, sp); });

  // ---------- lazy charts ----------
  const idle = window.requestIdleCallback ? (f) => requestIdleCallback(f, { timeout: 300 }) : (f) => setTimeout(f, 30);
  const run = (el) => {
    if (el.dataset.done) return;
    el.dataset.done = '1';
    const job = el.dataset.fig ? renderFigure(el, el.dataset.fig) : specials[el.dataset.special]?.(el);
    Promise.resolve(job).then(() => sleepWhenHidden(el)).catch((err) => { console.error(err); el.insertAdjacentHTML('beforeend', `<p class="hint">Chart could not load (${err.message}).</p>`); });
  };
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting || e.target.closest('details:not([open])')) return;
    io.unobserve(e.target);
    idle(() => run(e.target));  // build charts between scroll frames, not during them
  }), { rootMargin: '600px 0px' });
  document.querySelectorAll('#story [data-fig], #story [data-special]').forEach((el) => io.observe(el));
  document.addEventListener('toggle', (e) => {
    if (e.target.open) e.target.querySelectorAll('[data-fig], [data-special]').forEach(run);
  }, true);

  // ---------- where the reader is ----------
  let current = null;
  const spy = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    current = e.target;
    const ch = current.dataset.ch;
    navLinks.forEach((a) => {
      const on = a.getAttribute('href') === `#${ch}`;
      if (on && !a.classList.contains('on')) {  // centre the chip inside the bar only; never move the page
        const nav = a.parentElement;
        nav.scrollTo({ left: a.offsetLeft - (nav.clientWidth - a.offsetWidth) / 2, behavior: 'smooth' });
      }
      a.classList.toggle('on', on);
    });
    current.classList.add('seen');  // whatever the reader is looking at is always shown
    history.replaceState(null, '', `#${current.id}`);
    const acc = getComputedStyle(current).getPropertyValue('--c').trim() || '#e34948';
    document.getElementById('topbar').style.setProperty('--acc', acc);
  }), { rootMargin: '-45% 0px -50% 0px' });

  // ---------- section numbers within each chapter: 01, 02 ... drawn large above each question ----------
  const count = new Map();
  spreads.forEach((sp) => {
    if (sp.classList.contains('opener')) return;
    sp.querySelectorAll('.page.left .pbody > h2, .page.prose .pbody > h2, .pbody > .callout > h2').forEach((h) => {
      if (h.classList.contains('cont') || h.classList.contains('kf')) return;
      const n = (count.get(sp.dataset.ch) || 0) + 1;
      count.set(sp.dataset.ch, n);
      h.dataset.n = String(n).padStart(2, '0');
    });
  });

  // ---------- arrival: content rises in, big numbers count up ----------
  const countUp = (el) => {
    const m = el.textContent.match(/^([^\d]*)([\d,]*\.?\d+)(.*)$/);
    if (!m || el.dataset.counted) return;
    el.dataset.counted = '1';
    const [, pre, num, post] = m;
    const target = parseFloat(num.replace(/,/g, ''));
    const decimals = (num.split('.')[1] || '').length;
    const comma = num.includes(',');
    const t0 = performance.now();
    const step = (t) => {
      const k = Math.min(1, (t - t0) / 1100);
      const v = target * (1 - Math.pow(1 - k, 3));
      const s = comma ? v.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : v.toFixed(decimals);
      el.textContent = `${pre}${s}${post}`;
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const seen = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (!e.isIntersecting) return;
    seen.unobserve(e.target);
    e.target.classList.add('seen');
    if (!reduce) e.target.querySelectorAll('.tile b').forEach(countUp);
  }), { threshold: 0.12 });
  spreads.forEach((sp) => seen.observe(sp));
  spreads.forEach((sp) => spy.observe(sp));
  let ticking = false, max = 0;
  const measure = () => { max = document.documentElement.scrollHeight - innerHeight; };
  const progress = () => {
    ticking = false;
    bar.style.transform = `scaleX(${max > 0 ? Math.min(1, scrollY / max) : 0})`;
    document.body.classList.toggle('past-cover', scrollY > innerHeight);
  };
  measure();
  new ResizeObserver(measure).observe(document.body);
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(progress); } }, { passive: true });
  progress();

  // ---------- links and keys ----------
  const target = (hash) => {
    const h = decodeURIComponent(hash.replace(/^#/, ''));
    if (!h) return null;
    if (h === 'cover') return document.getElementById('cover');
    const byId = document.getElementById(h.replace(/-r$/, ''));
    if (byId && (byId.classList.contains('spread') || byId.id === 'cover')) return byId;
    if (firstOf.has(h)) return firstOf.get(h);
    const sec = h.match(/^sec=(\w+)\|(.*)$/);
    if (sec) {
      const want = sec[2].trim().toLowerCase();
      return spreads.find((sp) => sp.dataset.ch === sec[1] && [...sp.querySelectorAll('h2')]
        .some((x) => x.textContent.trim().toLowerCase().startsWith(want))) || firstOf.get(sec[1]) || null;
    }
    return null;
  };
  const go = (el, smooth = true) => el?.scrollIntoView({ behavior: smooth ? 'smooth' : 'instant', block: 'start' });
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a) return;
    const href = a.getAttribute('href');
    const page = href.match(/^(\w+)\.html$/);
    const hash = page ? `#${page[1] === 'index' ? 'intro' : page[1]}` : href.startsWith('#') ? href : null;
    const t = hash && target(hash);
    if (t) { e.preventDefault(); go(t); }
  });
  document.addEventListener('keydown', (e) => {
    if (e.target.closest('input, textarea, select') || e.metaKey || e.ctrlKey) return;
    const i = current ? spreads.indexOf(current) : -1;
    if (['ArrowDown', 'PageDown', 'ArrowRight'].includes(e.key) && i < spreads.length - 1) { e.preventDefault(); go(spreads[i + 1]); }
    if (['ArrowUp', 'PageUp', 'ArrowLeft'].includes(e.key)) { e.preventDefault(); go(i > 0 ? spreads[i - 1] : document.getElementById('cover')); }
  });
  const start = target(location.hash);
  if (start && start.id !== 'cover') requestAnimationFrame(() => go(start, false));
  addEventListener('hashchange', () => { const t = target(location.hash); if (t && t !== current) go(t); });
}
