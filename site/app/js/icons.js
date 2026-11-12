// Small line icons drawn for this site (24 x 24, stroke = currentColor).
const svg = (d) => `<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;

export const ICON = {
  gdp: svg('<path d="M4 20h16"/><path d="M7 16v-4M12 16V8M17 16V5"/>'),
  income: svg('<circle cx="12" cy="12" r="8"/><path d="M14.5 9.2c-.5-.8-1.4-1.2-2.5-1.2-1.6 0-2.6.8-2.6 1.9 0 2.6 5.3 1.4 5.3 4.1 0 1.1-1.1 2-2.7 2-1.2 0-2.2-.5-2.7-1.3M12 6.5v1.5M12 16v1.5"/>'),
  trade: svg('<path d="M4 8h13l-3-3M20 16H7l3 3"/>'),
  fdi: svg('<path d="M4 17l5-5 4 3 7-7"/><path d="M15 8h5v5"/>'),
  hdi: svg('<path d="M12 4l2.4 4.9 5.4.8-3.9 3.8.9 5.4L12 16.4l-4.8 2.5.9-5.4-3.9-3.8 5.4-.8z"/>'),
  gov: svg('<path d="M3 10l9-6 9 6"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18"/>'),
  people: svg('<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c.6-3.2 2.8-5 5.5-5s4.9 1.8 5.5 5"/><circle cx="17" cy="9" r="2.4"/><path d="M15.8 14.2c2.2.2 3.9 1.8 4.4 4.8"/>'),
  port: svg('<circle cx="12" cy="5" r="2"/><path d="M12 7v13M8 11h8"/><path d="M4 14c0 3.5 3.6 6 8 6s8-2.5 8-6"/>'),
  jurong: svg('<path d="M4 20V11l5 3V11l5 3V6h4v14z"/><path d="M15.5 6V3.5"/><path d="M8 17h1M12 17h1"/>'),
  fabs: svg('<rect x="7" y="7" width="10" height="10" rx="1.5"/><rect x="10" y="10" width="4" height="4"/><path d="M9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/>'),
  tuas: svg('<path d="M9 3h6M10 3v6l-5 9a2 2 0 0 0 1.8 3h10.4a2 2 0 0 0 1.8-3l-5-9V3"/><path d="M7.5 15h9"/>'),
  onenorth: svg('<path d="M6 20h12M9 20v-3h6v3"/><path d="M11 17a5 5 0 0 1 4-8.5"/><path d="M13 4l3 1.5-2 4-3-1.5z"/>'),
  cbd: svg('<path d="M3 20h18"/><path d="M5 20V10h4v10M10 20V4h5v16M16 20v-8h4v8"/><path d="M12 7.5h1M12 10.5h1M12 13.5h1"/>'),
  changi: svg('<path d="M10.5 13.5L4 11l1.2-1.6 7.3.8 3.8-4.2c.9-1 2.5-1.1 3.2-.4.7.7.6 2.3-.4 3.2l-4.2 3.8.8 7.3L14.4 21l-2.5-6.5-3.4 3.1.3 2.6-1.3 1.2-1.4-3.3-3.3-1.4 1.2-1.3 2.6.3z"/>'),
  globe: svg('<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.6 2.6 14.4 0 17M12 3.5c-2.6 2.6-2.6 14.4 0 17"/>'),
  close: svg('<path d="M6 6l12 12M18 6L6 18"/>'),
  plus: svg('<path d="M12 5v14M5 12h14"/>'),
  minus: svg('<path d="M5 12h14"/>'),
  reset: svg('<path d="M4 12a8 8 0 1 0 2.4-5.7L4 8.5"/><path d="M4 4v4.5h4.5"/>'),
};
