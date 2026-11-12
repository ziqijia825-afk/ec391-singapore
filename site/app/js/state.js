// Shared state for linked views: the global year control and cross-chart selections.
export const YEARS = { min: 2004, max: 2024 };
export const state = { year: YEARS.max, partner: null, sector: null, economy: null };
const subscribers = new Set();

export function set(patch) {
  const changed = Object.keys(patch).filter((k) => state[k] !== patch[k]);
  if (!changed.length) return;
  Object.assign(state, patch);
  subscribers.forEach((fn) => fn(state, changed));
}

export function on(fn) {
  subscribers.add(fn);
  return () => subscribers.delete(fn);
}

const cache = new Map();
export function getJSON(path) {
  const url = window.__V ? `${path}?v=${window.__V}` : path;
  if (!cache.has(path)) cache.set(path, fetch(url).then((r) => {
    if (!r.ok) throw new Error(`${path}: ${r.status}`);
    return r.json();
  }));
  return cache.get(path);
}

// Nearest available year not after the selected one (or the first year if all are later).
// At the right end of the slider, show the latest year each source has (e.g. WGI 2025, TiVA 2022).
export function pickYear(available, year = state.year) {
  const ys = available.map(Number).sort((a, b) => a - b);
  if (year >= YEARS.max) return ys[ys.length - 1];
  const le = ys.filter((y) => y <= year);
  return le.length ? le[le.length - 1] : ys[0];
}
