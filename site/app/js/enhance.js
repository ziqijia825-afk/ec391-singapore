// Small UI threaded through every chapter: highlighted numbers, peer colour dots and glossary hints in the text,
// counts on the "More" toggles that hold charts or tables, and a card that leads into the next chapter.
import { ECON } from './chart.js';

// short definitions, the team's own wording
const GLOSSARY = {
  RCA: 'Revealed comparative advantage, the Balassa index. A sector’s share of a country’s exports divided by its share of world exports, so a value above 1 is an advantage.',
  HHI: 'Herfindahl Hirschman index, the sum of squared shares. Close to 0 when trade is spread across many partners, 1 when it goes to one.',
  FDI: 'Foreign direct investment, a lasting stake of at least 10 percent in a firm in another country.',
  GVC: 'Global value chain. Production split across countries, each adding value to inputs made in the others.',
  TiVA: 'The OECD Trade in Value Added database, which traces where the value inside each country’s exports was created.',
  BACI: 'CEPII’s database of world trade, which reconciles what exporters and importers report about the same flow.',
  MFN: 'Most favoured nation. The tariff a WTO member charges every other member unless an agreement says otherwise.',
  PPP: 'Purchasing power parity. Values converted at prices that buy the same basket of goods in every country.',
  WGI: 'The World Bank’s Worldwide Governance Indicators, six dimensions scored from 0 to 100.',
  FTA: 'Free trade agreement. Partners drop most tariffs between themselves and keep their own toward everyone else.',
  BIT: 'Bilateral investment treaty, which protects investors from each party in the other.',
  OLI: 'Dunning’s framework. Firms invest abroad when they combine Ownership, Location and Internalisation advantages.',
  HDI: 'UNDP’s Human Development Index, combining life expectancy, schooling and income.',
  GNI: 'Gross national income. GDP plus income earned abroad, minus income paid to foreign owners.',
  'non-tariff measures': 'Rules other than tariffs that affect imports, such as standards, testing, labelling and licences.',
  'rules of origin': 'Rules that decide which country a product comes from, and so whether it qualifies for a preferential tariff.',
  're-exports': 'Goods imported and shipped out again with little change.',
  'greenfield': 'Investment that builds a new plant or office, as opposed to buying an existing firm.',
  'holding companies': 'Firms whose main business is owning shares in other firms, often operating elsewhere.',
  'backward participation': 'The foreign value added contained in a country’s exports.',
  'forward participation': 'A country’s value added used by other countries in their own exports.',
  'value added': 'The value a producer adds to the inputs it buys, the part of output created at home.',
};
const PEERS = { Malaysia: ECON.MYS, 'Hong Kong SAR': ECON.HKG, Vietnam: ECON.VNM };
const esc = (t) => t.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const rx = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// acronyms match in capitals only (so "BIT" never catches the word "bit"); phrases match with either first letter
const isAcronym = (k) => /^[A-Z][A-Za-z]*$/.test(k) && /[A-Z]{2}|^TiVA$/.test(k);
const TERM_RE = Object.keys(GLOSSARY).map((k) => (isAcronym(k) ? `\\b${k}s?\\b`
  : `\\b[${k[0].toUpperCase()}${k[0]}]${rx(k.slice(1))}\\b`)).join('|');
const NUM_RE = [
  'S?\\$\\s?\\d[\\d,.]*(?:\\s?(?:trillion|billion|million|bn|tn|k))?',
  '[−-]?\\d[\\d,.]*\\s?(?:percent|percentage points|%|times)',
  '\\d+(?:st|nd|rd|th) of \\d+',
  '[−-]?\\d+\\.\\d+',
].join('|');
const PEER_RE = Object.keys(PEERS).map(rx).join('|');
const ALL = new RegExp(`(${TERM_RE})|(${NUM_RE})|(${PEER_RE})`, 'g');

function decorate(root, usedTerms) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => (n.parentElement.closest('a, .tag, .xref, .num, .gloss, .peer, h2, h4, .equation, summary, table, .facts, .timeline, .chains, .footnote')
      ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT),
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach((node) => {
    const text = node.nodeValue;
    ALL.lastIndex = 0;
    if (!ALL.test(text)) return;
    ALL.lastIndex = 0;
    const seenPeer = new Set();
    let out = '', last = 0, m;
    while ((m = ALL.exec(text))) {
      out += esc(text.slice(last, m.index));
      const [hit, term, num, peer] = m;
      if (term) {
        const key = Object.keys(GLOSSARY).find((k) => hit.toLowerCase().replace(/s$/, '') === k.toLowerCase() || hit.toLowerCase() === k.toLowerCase());
        if (key && !usedTerms.has(key)) {
          usedTerms.add(key);
          out += `<span class="gloss" tabindex="0" data-tip="${esc(GLOSSARY[key])}">${esc(hit)}</span>`;
        } else out += esc(hit);
      } else if (num) {
        out += `<span class="num">${esc(hit)}</span>`;
      } else if (peer && !seenPeer.has(hit)) {
        seenPeer.add(hit);
        out += `<span class="peer" style="--k:${PEERS[hit] || '#888'}">${esc(hit)}</span>`;
      } else out += esc(hit);
      last = m.index + hit.length;
    }
    out += esc(text.slice(last));
    const span = document.createElement('span');
    span.innerHTML = out;
    node.replaceWith(...span.childNodes);
  });
}

export function enhance() {
  const spreads = [...document.querySelectorAll('#story .spread')];
  // text: one glossary hint per term per screen, numbers and peers everywhere in running text
  spreads.forEach((sp) => {
    const used = new Set(sp.dataset.ch === 'appendix' ? Object.keys(GLOSSARY) : []);  // the appendix defines the terms itself
    sp.querySelectorAll('.page.left .pbody > p, .page.prose .pbody > p, .page.left details.more p, .page.prose details.more p, .spread.opener .pbody > p')
      .forEach((p) => decorate(p, used));
  });
  // "More" toggles say what they hold
  document.querySelectorAll('#story details.more').forEach((d) => {
    const f = d.querySelectorAll('[data-fig], [data-special]').length, t = d.querySelectorAll('.tablewrap').length;
    const bits = [f ? `${f} chart${f > 1 ? 's' : ''}` : '', t ? `${t} table${t > 1 ? 's' : ''}` : ''].filter(Boolean);
    if (bits.length) d.querySelector('summary')?.insertAdjacentHTML('beforeend', `<span class="dchip">${bits.join(' · ')}</span>`);
  });
  const byCh = new Map();
  spreads.forEach((sp) => { if (!byCh.has(sp.dataset.ch)) byCh.set(sp.dataset.ch, []); byCh.get(sp.dataset.ch).push(sp); });
  // the last screen of each chapter leads into the next one
  const chapters = [...byCh.keys()];
  chapters.forEach((ch, i) => {
    const next = chapters[i + 1];
    if (!next) return;
    const nOpen = byCh.get(next).find((sp) => sp.classList.contains('opener'));
    if (!nOpen) return;
    const title = nOpen.querySelector('.titlepage h1')?.textContent || '';
    const num = nOpen.querySelector('.chnum')?.textContent || 'Next';
    const color = getComputedStyle(nOpen).getPropertyValue('--c').trim();
    const lastSp = byCh.get(ch)[byCh.get(ch).length - 1];
    const col = lastSp.querySelector('.page.left .pbody, .page.prose .pbody');
    col?.insertAdjacentHTML('beforeend', `<a class="nextch" href="#${nOpen.id}" style="--n:${color}"><small>Next · ${num}</small>`
      + `<b>${title}</b><i aria-hidden="true">→</i></a>`);
  });
  // the verdict and the recommendation stand out as a callout box
  document.querySelectorAll('#story .pbody > h2').forEach((h) => {
    if (!/^(The verdict|Investment recommendation)/.test(h.textContent.trim())) return;
    const box = document.createElement('div');
    box.className = 'callout';
    h.before(box);
    let n = h;
    while (n && !(n !== h && (n.tagName === 'H2' || n.classList?.contains('nextch')))) { const next = n.nextElementSibling; box.append(n); n = next; }
  });
}
