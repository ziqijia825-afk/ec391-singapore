"""Build the website from text/*.md and figures/*.png into _site/ (published by GitHub Pages), and the single
Markdown deliverable (all sections concatenated) into report/EC391_Singapore.md.

Pages, in storyline order. A section with no Markdown file yet shows a "coming soon" note.
A line `<!-- include: data/derived/NAME.md -->` in a text file is replaced by that generated table, so tables come
straight from the analysis scripts.
"""
import re
import shutil
import time
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
REPORT = ROOT / "report" / "EC391_Singapore.md"

PAGES = [  # (file stem, nav label)
    ("index", "Home"),
    ("ch01_profile", "1 Profile"),
    ("ch02_macro", "2 Macro & governance"),
    ("ch03_trade", "3 Trade"),
    ("ch04_rca", "4 Comparative advantage"),
    ("ch05_gvc", "5 Value chains"),
    ("ch06_fdi", "6 FDI"),
    ("ch07_policy", "7 Trade policy"),
    ("ch09_case", "9 Case study"),
    ("conclusion", "Conclusion"),
    ("appendix", "Appendix"),
]

CSS = """
:root{--ink:#1f1f1d;--muted:#5f5e5a;--line:#e4e3dd;--accent:#2a78d6;--bg:#fbfbf9;--card:#ffffff}
*{box-sizing:border-box}
body{margin:0;font:17px/1.65 Georgia,"Iowan Old Style","Times New Roman",serif;color:var(--ink);background:var(--bg)}
nav{position:sticky;top:0;background:rgba(255,255,255,.96);backdrop-filter:blur(6px);border-bottom:1px solid var(--line);
  padding:10px 20px;display:flex;flex-wrap:wrap;gap:4px 16px;font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;z-index:1}
nav a{color:var(--muted);text-decoration:none;white-space:nowrap}nav a:hover{color:var(--ink)}
nav a.on{color:var(--accent);font-weight:600}
main{max-width:900px;margin:0 auto;padding:36px 20px 80px}
h1,h2,h3{font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.25}
h1{font-size:32px;margin:0 0 8px}h2{margin-top:44px;font-size:23px}h3{margin-top:28px;font-size:18px}
p{margin:0 0 1em}
a{color:var(--accent)}
img{display:block;max-width:100%;height:auto;margin:8px 0 6px;border:1px solid var(--line);border-radius:8px;background:#fff}
table{border-collapse:collapse;width:100%;margin:12px 0 6px;font:13.5px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;
  display:block;overflow-x:auto}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;border-bottom:2px solid var(--line)}
table.rca td:not(:first-child),table.rca th:not(:first-child){text-align:center;min-width:92px}
em{color:var(--muted)}
.draft{font:13px/1.5 system-ui,sans-serif;color:var(--muted);background:#f1f0ec;border-radius:6px;padding:8px 12px;margin:0 0 24px}
.soon{color:var(--muted);font-style:italic}
details{border:1px solid var(--line);border-radius:10px;background:#fff;padding:0 16px;margin:14px 0 22px}
details summary{cursor:pointer;font:600 14.5px/1.4 system-ui,sans-serif;color:var(--accent);padding:12px 0;list-style:none}
details summary::before{content:"+ ";font-weight:700}details[open] summary::before{content:"− "}
details[open]{padding-bottom:8px}
.pager{display:flex;justify-content:space-between;gap:12px;margin-top:56px;font:14px system-ui,sans-serif}
footer{color:var(--muted);font:13px/1.5 system-ui,sans-serif;margin-top:28px;border-top:1px solid var(--line);padding-top:14px}
.tag{font:600 12px/1.4 system-ui,sans-serif;background:#e8f2fc;color:#1f5fae;border-radius:999px;padding:2px 9px;margin-left:8px;vertical-align:3px}
.equation{font:600 17px/1.5 Georgia,serif;text-align:center;border:1px solid var(--line);border-left:6px solid #eb6834;border-radius:8px;padding:10px;background:#fff}
.equation span{display:block;font:12.5px system-ui,sans-serif;color:var(--muted)}
.timeline .era,.chains .chain{border-left:4px solid #2a78d6;padding:4px 12px;margin:6px 0;background:#fff}
.timeline .era.brk{border-left-color:#e34948;background:#fdf1ee}.timeline .era b,.timeline .era span{margin-right:8px}
.chains{display:grid;grid-template-columns:1fr 1fr;gap:10px}.chains-src,.timeline-src{grid-column:1/-1;font-size:13px;color:var(--muted)}
.chain h4{margin:4px 0}.chain p{margin:4px 0}.chain b{font-size:22px;display:block}
@media (max-width:600px){body{font-size:16px}h1{font-size:26px}main{padding:24px 16px 64px}nav{position:static;padding:8px 16px;font-size:13px}}
"""

INCLUDE = re.compile(r"<!--\s*include:\s*(\S+)\s*-->")
TAG = re.compile(r"^(#{2,3} .*?)\s*\{([^{}]+)\}\s*$", re.M)  # "## Heading {Course reading}" -> a tag chip


def tags_to_chips(md):
    return TAG.sub(lambda m: f'{m.group(1)} <span class="tag">{m.group(2)}</span>', md)


def tags_strip(md):
    return TAG.sub(lambda m: m.group(1), md)


def expand(md):
    return INCLUDE.sub(lambda m: (ROOT / m.group(1)).read_text(encoding="utf-8").strip(), md)


def page(stem, label, body, prev, nxt):
    nav = "".join(f'<a href="{s}.html"{" class=on" if s == stem else ""}>{l}</a>' for s, l in PAGES)
    pager = '<div class="pager"><span>' + (f'<a href="{prev[0]}.html">← {prev[1]}</a>' if prev else "") + \
            "</span><span>" + (f'<a href="{nxt[0]}.html">{nxt[1]} →</a>' if nxt else "") + "</span></div>"
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{label} | Singapore: EC 391</title>
<style>{CSS}</style></head><body><nav>{nav}</nav><main>{body}{pager}
<footer>EC 391 Country Team Project: Singapore. Every chart is built by the team from raw data with the scripts in
the project repository; sources are under each figure and in the appendix.
<a href="../EC391_Singapore.md">Download the full text (Markdown)</a> · <a href="../index.html">Interactive version</a>.</footer></main></body></html>"""


APP = ROOT / "site" / "app"
NAV = [("intro", "Overview"), ("ch01_profile", "1 Profile"), ("ch02_macro", "2 Macro & governance"),
       ("ch03_trade", "3 Openness & trade"), ("ch04_rca", "4 Comparative advantage"), ("ch05_gvc", "5 Value chains"),
       ("ch06_fdi", "6 FDI"), ("ch07_policy", "7 Trade policy"), ("ch09_case", "9 Case study"),
       ("conclusion", "Conclusion"), ("appendix", "Appendix")]
SPECIAL_FIGS = {"ch02_wgi_radar": "wgi"}
BANNER_COLORS = ["#334e68", "#0f766e", "#4338ca", "#e2562b", "#15803d", "#7c3aed", "#0369a1", "#b45309", "#be123c",
                 "#0b2239", "#475569"]  # one accent per chapter, in NAV order
IMG = re.compile(r'<p>\s*<img alt="([^"]*)" src="figures/([\w-]+)\.png"\s*/?>\s*</p>')
MARK = re.compile(r"<!--\s*interactive:\s*(\w+)\s*-->")


def interactive_html(html):
    def fig(m):
        alt, fid = m.group(1), m.group(2)
        attr = f'data-special="{SPECIAL_FIGS[fid]}"' if fid in SPECIAL_FIGS else f'data-fig="{fid}"'
        return (f'<div {attr}><noscript><img class="fallback" src="figures/{fid}.png" alt="{alt}"></noscript>'
                f'<img class="fallback js-hide" src="figures/{fid}.png" alt="{alt}" loading="lazy" style="display:none"></div>')
    html = IMG.sub(fig, html)
    html = MARK.sub(lambda m: f'<div data-special="{m.group(1)}"></div>', html)
    html = re.sub(r"(<table[\s\S]*?</table>)", r'<div class="tablewrap">\1</div>', html)
    return html


BLOCK = re.compile(r'<h1>.*?</h1>|<h2>.*?</h2>|<h3>.*?</h3>|<details.*?</details>|<p[ >].*?</p>'
                   r'|<div data-(?:fig|special)=[^>]*>.*?</div>|<div class="tablewrap">.*?</div>'
                   r'|<section class="\w+">.*?</section>'
                   r'|<ul>.*?</ul>|<ol>.*?</ol>|<blockquote>.*?</blockquote>|<hr\s*/?>', re.S)
CHIP = re.compile(r'\s*<span class="tag">.*?</span>')
WIDE = {"sgmap", "sankey", "treemap", "gvc", "fdi"}
PAGE_CHARS = 1200  # visible characters that fit on one page beside a figure at the book's type size  # interactive components drawn across both pages


def strip_tags(h):
    return re.sub(r"<[^>]+>", "", h).strip()


def paginate(stem, html):
    """Split one chapter into book spreads. Text goes on the left page, the figure it discusses on the right;
    interactive components get a two-page spread of their own."""
    blocks = []
    for b in BLOCK.findall(html):  # a paragraph longer than a page is split at the sentence nearest its middle
        if b.startswith("<p>") and len(strip_tags(b)) > PAGE_CHARS:
            inner = b[3:-4]
            cuts = [m.end() for m in re.finditer(r"(?<=[a-z0-9%)])\. (?=[A-Z])", inner)]
            if cuts:
                mid = min(cuts, key=lambda c: abs(c - len(inner) / 2))
                blocks += [f"<p>{inner[:mid].rstrip()}</p>", f"<p>{inner[mid:].lstrip()}</p>"]
                continue
        blocks.append(b)
    rest = BLOCK.sub("", html).strip()
    if rest:
        raise SystemExit(f"{stem}: content the book layout does not place: {rest[:120]!r}")
    title = strip_tags(blocks[0]) if blocks and blocks[0].startswith("<h1>") else stem
    sections, cur = [], {"head": None, "blocks": []}
    for b in blocks[1:]:
        if b.startswith("<h2>"):
            sections.append(cur)
            cur = {"head": strip_tags(CHIP.sub("", b)), "h2": b, "blocks": []}
        else:
            cur["blocks"].append(b)
    sections.append(cur)
    pre, body = sections[0], sections[1:]
    is_visual = lambda b: b.startswith(("<div data-", '<div class="tablewrap"', '<section class='))
    special = lambda b: (re.match(r'<div data-special="(\w+)"', b) or [None, None])[1]
    # opener: title page + key finding (or the preamble)
    key = []
    if body and body[0]["head"] == "Key finding" and not any(is_visual(b) for b in body[0]["blocks"]):
        key = ['<h2 class="kf">Key finding</h2>'] + body[0]["blocks"]
        body = body[1:]
    pre_text = [b for b in pre["blocks"] if not is_visual(b)]
    pre_vis = [b for b in pre["blocks"] if is_visual(b)]
    opener_right, pre_rest = (key, pre_text) if key else fill(pre_text, PAGE_CHARS)
    spreads = [{"kind": "opener", "title": title, "left": [], "right": opener_right,
                "heads": [x["head"] for x in body if x["head"] != "Sources"]}]
    if pre_rest or pre_vis:
        body.insert(0, {"head": None if key else "Overview", "blocks": pre_rest + pre_vis})
    for sec in body:
        head = sec.get("h2") or (f'<h2>{sec["head"]}</h2>' if sec["head"] else "")
        cur = None
        for b in sec["blocks"]:
            if special(b) in WIDE:
                if cur:
                    spreads.append(cur)
                spreads.append({"kind": "wide", "section": sec["head"], "left": [b], "right": []})
                cur = None
                continue
            if cur is None:
                cur = {"kind": "text", "section": sec["head"],
                       "left": [head if not any(x.get("section") == sec["head"] for x in spreads[1:])
                                else f'<h2 class="cont">{sec["head"]}</h2>'] if head else [], "right": []}
            if is_visual(b):
                if cur["right"]:
                    spreads.append(cur)
                    cur = {"kind": "text", "section": sec["head"], "left": [f'<h2 class="cont">{sec["head"]}</h2>'] if head else [],
                           "right": []}
                cur["right"].append(b)
            elif cur["right"] and re.fullmatch(r"<p>\s*<em>.*</em>\s*</p>", b, re.S) and is_visual(cur["right"][-1]):
                cur["right"].append(f'<div class="footnote">{b}</div>')  # a table's note stays under the table
            else:
                cur["left"].append(b)
        if cur:
            spreads.append(cur)
    # text that would overflow the page beside a figure runs on to a continuation spread, as in a printed book
    flowed = []
    for sp in spreads:
        flowed.append(sp)
        if sp["kind"] != "text" or not sp["right"]:
            continue
        while sum(visible_len(b) for b in sp["left"]) > PAGE_CHARS and len(sp["left"]) > 2:
            keep, acc = [], 0
            for b in sp["left"]:
                acc += visible_len(b)
                if acc > PAGE_CHARS and len(keep) >= 2:
                    break
                keep.append(b)
            rest = sp["left"][len(keep):]
            if not rest:
                break
            sp["left"] = keep
            cont = (f'<h2 class="cont">{sp["section"]}</h2>' if sp.get("section") else "")
            sp = {"kind": "text", "section": sp.get("section"), "left": ([cont] if cont else []) + rest, "right": []}
            flowed.append(sp)
    spreads = flowed
    # two text-only spreads in a row share one spread (second one on the right page)
    merged = []
    for sp in spreads:
        prev = merged[-1] if merged else None
        if (prev and prev["kind"] == "text" and not prev["right"] and sp["kind"] == "text" and not sp["right"]
                and sum(visible_len(b) for b in prev["left"]) <= PAGE_CHARS and sum(visible_len(b) for b in sp["left"]) <= PAGE_CHARS):
            prev["right"] = sp["left"]
            prev.setdefault("also", []).append(sp.get("section"))
            continue
        merged.append(sp)
    final = []
    for sp in merged:
        while sp["kind"] == "text" and not sp["right"] and len(sp["left"]) > 2 and \
                sum(visible_len(b) for b in sp["left"]) > 1100:  # long text runs on over both pages, then further
            left, rest = fill(sp["left"], PAGE_CHARS)
            right, rest = fill(rest, PAGE_CHARS) if rest else ([], [])
            if not right:  # everything fitted on the left page: balance the two pages instead
                half = sum(visible_len(b) for b in left) / 2
                left, right = fill(left, half)
            sp["left"], sp["right"] = left, right
            final.append(sp)
            if not rest:
                sp = None
                break
            cont = f'<h2 class="cont">{sp["section"]}</h2>' if sp.get("section") else ""
            sp = {"kind": "text", "section": sp.get("section"), "left": ([cont] if cont else []) + rest, "right": []}
        if sp is None:
            continue
        if sp["kind"] == "text" and not sp["right"]:
            if len(sp["left"]) > 2 and sum(visible_len(b) for b in sp["left"]) > 1100:
                left, right = fill(sp["left"], sum(visible_len(b) for b in sp["left"]) / 2)
                sp["left"], sp["right"] = left, right
            else:
                sp["kind"] = "plate"  # right page becomes an illustration plate
        final.append(sp)
    return title, final


def fill(blocks, limit):
    """Take blocks in order while they fit within `limit` visible characters (always at least one)."""
    taken, acc = [], 0
    for j, b in enumerate(blocks):
        size = visible_len(b)
        if taken and acc + size > limit:
            return taken, blocks[j:]
        taken.append(b)
        acc += size
    return taken, []


def visible_len(b):
    """Characters a reader sees before opening anything: a closed <details> shows only its summary."""
    if b.startswith("<details"):
        m = re.search(r"<summary>(.*?)</summary>", b, re.S)
        return 60 + len(strip_tags(m.group(1))) if m else 60
    return len(strip_tags(b))


def page_html(cls, runhead, inner, folio):
    return f'<section class="page {cls}"><div class="pbody">{inner}</div></section>'  # running heads and folios dropped


def number_figures(stem, html):
    """Figure 3.1, 3.2 ... and Table 3.1 ... in reading order within each numbered chapter."""
    m = re.match(r"ch(\d+)_", stem)
    if not m:
        return html
    ch, counts = int(m.group(1)), {"f": 0, "t": 0}

    def fig(mm):
        counts["f"] += 1
        return f'{mm.group(0)[:-1]} data-num="Figure {ch}.{counts["f"]}">'

    def tab(mm):
        counts["t"] += 1
        return f'<div class="tablewrap"><span class="tabnum">Table {ch}.{counts["t"]}</span>'
    html = re.sub(r'<div data-(?:fig|special)="[\w-]+">', fig, html)
    return re.sub(r'<div class="tablewrap">', tab, html)


TILES = ROOT / "data" / "derived" / "tiles.json"


def tiles_html(stem):
    import json
    tiles = json.loads(TILES.read_text()).get(stem, []) if TILES.exists() else []
    if not tiles:
        return ""
    cells = "".join(f'<div class="tile"><b>{t["value"]}</b><span>{t["label"]}</span><small>{t["rank"]}</small></div>' for t in tiles)
    return f'<div class="tiles">{cells}</div>'


def build_book(texts):
    chapters, n = [], 0
    for i, (stem, label) in enumerate(NAV):
        md = texts.get("index" if stem == "intro" else stem)
        if md is None:
            continue
        html = number_figures(stem, interactive_html(markdown.markdown(md, extensions=["tables", "md_in_html"])))
        title, spreads = paginate(stem, html)
        chapters.append((stem, label, BANNER_COLORS[i % len(BANNER_COLORS)], title, spreads))
    # page numbers and anchors first, so tables of contents can point at them
    sid = {}
    for stem, label, color, title, spreads in chapters:
        for k, sp in enumerate(spreads):
            n += 1
            sp["id"], sp["folio"] = n, 2 * n - 1
            for sec in [sp.get("section"), *sp.get("also", [])]:
                if sec and (stem, sec) not in sid:
                    sid[(stem, sec)] = sp
    contents = []
    for stem, label, color, title, spreads in chapters:
        m = re.match(r"ch(\d+)_", stem)
        num = m.group(1) if m else ""
        heads = spreads[0].get("heads", []) if spreads and spreads[0]["kind"] == "opener" else []
        items = "".join(f'<li><a href="#p{sid[(stem, h)]["id"]}">{h}</a></li>' for h in heads if (stem, h) in sid)
        name = re.sub(r"^\d+\s+", "", title)
        contents.append(f'<div class="ct-ch" style="--c:{color}"><a class="ct-head" href="#{stem}"><i>{num or "&middot;"}</i>'
                        f'<span>{name}</span></a>' + (f'<ol>{items}</ol>' if items else "") + "</div>")
    build_book.contents = "".join(contents)
    out = []
    for stem, label, color, title, spreads in chapters:
        short = re.sub(r"^\d+\s+", "", label)
        for sp in spreads:
            f = sp["folio"]
            chn = re.match(r"ch(\d+)_", stem)
            attrs = (f'class="spread {sp["kind"]}" id="p{sp["id"]}" data-ch="{stem}" style="--c:{color}"'
                     + (f' data-chn="{chn.group(1)}"' if chn else ""))
            if sp["kind"] == "opener":
                m = re.match(r"(\d+)\s+(.*)", title)
                num, name = (f"Chapter {m.group(1)}", m.group(2)) if m else ("", title)
                toc = "".join(f'<li><a href="#p{sid[(stem, h)]["id"]}">{h}</a></li>' for h in sp["heads"] if (stem, h) in sid)
                left = (f'<div class="titlepage"><div class="chnum">{num}</div><h1>{name}</h1>'
                        + (f'<ol class="toc">{toc}</ol>' if toc else "") + "</div>")
                out.append(f'<article {attrs}>{page_html("left", "", left, f)}'
                           f'{page_html("right", "", "".join(sp["right"]) + tiles_html(stem), f + 1)}</article>')
            elif sp["kind"] == "wide":
                out.append(f'<article {attrs}>{page_html("full", f"{short} &middot; {sp["section"]}", sp["left"][0], "")}</article>')
            else:
                has_visual = any(b.startswith(('<div data-', '<div class="tablewrap"', '<section', '<div class="footnote"'))
                                 for b in sp["right"])
                if has_visual:
                    out.append(f'<article {attrs}>{page_html("left", short, "".join(sp["left"]), f)}'
                               f'{page_html("right", "", "".join(sp["right"]), f + 1)}</article>')
                else:  # text only: one reading column
                    attrs = attrs.replace(f'class="spread {sp["kind"]}"', 'class="spread prose"')
                    out.append(f'<article {attrs}>{page_html("prose", short, "".join(sp["left"] + sp["right"]), f)}</article>')
    n += 1
    colophon = ('<div class="colophon"><h2>About this site</h2><p>EC 391 Country Team Project: Singapore, Fall 2026. Every chart '
                'is built by the team from raw data with the scripts in the project repository, and sources are under each '
                'figure and in the appendix.</p><p><a href="EC391_Singapore.md">Full text (Markdown)</a> &middot; '
                '<a href="article/index.html">Static article version</a> &middot; <a href="#cover">Back to the top</a></p></div>')
    out.append(f'<article class="spread prose end" id="p{n}" data-ch="appendix">{page_html("prose", "Colophon", colophon, "")}</article>')
    return "\n".join(out), n


def build_interactive(texts):
    book, nspreads = build_book(texts)
    def chip(i, s, l):
        m = re.match(r"(\d+)\s+(.*)", l)
        num, name = (m.group(1).zfill(2), m.group(2)) if m else ("", l)
        return (f'<a href="#{s}" style="--c:{BANNER_COLORS[i % len(BANNER_COLORS)]}">'
                + (f'<i>{num}</i>' if num else "") + f'<span>{name}</span></a>')
    nav = "".join(chip(i, s, l) for i, (s, l) in enumerate(NAV))
    version = str(int(time.time()))  # cache-busting: browsers must not mix old modules or data with new ones
    page = (APP / "index.html").read_text(encoding="utf-8").replace("{{NAV}}", nav).replace("{{SECTIONS}}", book).replace("{{CONTENTS}}", build_book.contents)
    page = page.replace('src="js/main.js"', f'src="js/main.js?v={version}"').replace('href="app.css"', f'href="app.css?v={version}"')
    page = page.replace("</head>", f"<script>window.__V='{version}';</script>\n</head>", 1)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    for f in ("app.css", "merlion.svg", "hero.svg"):
        shutil.copy(APP / f, OUT / f)
    shutil.copytree(APP / "icons", OUT / "icons")
    (OUT / "js").mkdir()
    for js in (APP / "js").glob("*.js"):
        code = re.sub(r"from '(\./[\w]+\.js)'", lambda m: f"from '{m.group(1)}?v={version}'", js.read_text(encoding="utf-8"))
        code = code.replace("import('/js/", f"import('/js/")
        (OUT / "js" / js.name).write_text(code, encoding="utf-8")
    shutil.copytree(APP / "vendor", OUT / "vendor")
    shutil.copytree(ROOT / "site" / "data", OUT / "data")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "article").mkdir(parents=True)
    shutil.copytree(ROOT / "figures", OUT / "figures")
    report, texts = [], {}
    for i, (stem, label) in enumerate(PAGES):
        src = ROOT / "text" / f"{stem}.md"
        prev = PAGES[i - 1] if i > 0 else None
        nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
        if src.exists():
            md = expand(src.read_text(encoding="utf-8")).replace("](../figures/", "](figures/")
            texts[stem] = tags_to_chips(md)
            report.append(tags_strip(md))
            md = texts[stem]
            body = markdown.markdown(md.replace("](figures/", "](../figures/"), extensions=["tables", "md_in_html"])
        else:
            body = f"<h1>{label}</h1><p class=soon>Coming soon.</p>"
        (OUT / "article" / f"{stem}.html").write_text(page(stem, label, body, prev, nxt), encoding="utf-8")
    REPORT.parent.mkdir(exist_ok=True)
    text = MARK.sub("", "\n\n---\n\n".join(report))
    REPORT.write_text(text.replace("](figures/", "](../figures/") + "\n", encoding="utf-8")
    (OUT / "EC391_Singapore.md").write_text(text + "\n", encoding="utf-8")
    build_interactive(texts)
    print(f"built interactive site + {len(PAGES)} article pages into {OUT}; report at {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
