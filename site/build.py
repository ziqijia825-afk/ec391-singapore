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
@media (max-width:600px){body{font-size:16px}h1{font-size:26px}main{padding:24px 16px 64px}nav{position:static;padding:8px 16px;font-size:13px}}
"""

INCLUDE = re.compile(r"<!--\s*include:\s*(\S+)\s*-->")


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
BANNER_COLORS = ["#4db6ec", "#5dae4b", "#f28a2e", "#ffc93c", "#2e8fd0", "#e8552f", "#2f7d3a", "#4db6ec", "#f28a2e",
                 "#5dae4b", "#9aa7b0"]  # figures replaced by a richer interactive component
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
                   r'|<ul>.*?</ul>|<ol>.*?</ol>|<blockquote>.*?</blockquote>|<hr\s*/?>', re.S)
WIDE = {"sgmap", "sankey", "treemap", "gvc", "fdi"}  # interactive components drawn across both pages


def strip_tags(h):
    return re.sub(r"<[^>]+>", "", h).strip()


def paginate(stem, html):
    """Split one chapter into book spreads. Text goes on the left page, the figure it discusses on the right;
    interactive components get a two-page spread of their own."""
    blocks = BLOCK.findall(html)
    rest = BLOCK.sub("", html).strip()
    if rest:
        raise SystemExit(f"{stem}: content the book layout does not place: {rest[:120]!r}")
    title = strip_tags(blocks[0]) if blocks and blocks[0].startswith("<h1>") else stem
    sections, cur = [], {"head": None, "blocks": []}
    for b in blocks[1:]:
        if b.startswith("<h2>"):
            sections.append(cur)
            cur = {"head": strip_tags(b), "blocks": []}
        else:
            cur["blocks"].append(b)
    sections.append(cur)
    pre, body = sections[0], sections[1:]
    is_visual = lambda b: b.startswith(("<div data-", '<div class="tablewrap"'))
    special = lambda b: (re.match(r'<div data-special="(\w+)"', b) or [None, None])[1]
    # opener: title page + key finding (or the preamble)
    key = []
    if body and body[0]["head"] == "Key finding" and not any(is_visual(b) for b in body[0]["blocks"]):
        key = ['<h2 class="kf">Key finding</h2>'] + body[0]["blocks"]
        body = body[1:]
    pre_text = [b for b in pre["blocks"] if not is_visual(b)]
    pre_vis = [b for b in pre["blocks"] if is_visual(b)]
    spreads = [{"kind": "opener", "title": title, "left": [], "right": key or pre_text,
                "heads": [x["head"] for x in body if x["head"] != "Sources"]}]
    if key and pre_text:
        body.insert(0, {"head": None, "blocks": pre["blocks"]})
    elif pre_vis:
        body.insert(0, {"head": "Overview", "blocks": pre_vis})
    for sec in body:
        head = f'<h2>{sec["head"]}</h2>' if sec["head"] else ""
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
    # two text-only spreads in a row share one spread (second one on the right page)
    merged = []
    for sp in spreads:
        prev = merged[-1] if merged else None
        if (prev and prev["kind"] == "text" and not prev["right"] and sp["kind"] == "text" and not sp["right"]):
            prev["right"] = sp["left"]
            continue
        merged.append(sp)
    for sp in merged:
        if sp["kind"] == "text" and not sp["right"]:
            sizes = [visible_len(b) for b in sp["left"]]
            if sum(sizes) > 1100 and len(sp["left"]) > 2:  # long text runs on over both pages
                half, acc, cut = sum(sizes) / 2, 0, len(sizes) - 1
                for j, z in enumerate(sizes):
                    acc += z
                    if acc >= half:
                        cut = max(1, min(j + 1, len(sizes) - 1))
                        break
                sp["left"], sp["right"] = sp["left"][:cut], sp["left"][cut:]
            else:
                sp["kind"] = "plate"  # right page becomes an illustration plate
    return title, merged


def visible_len(b):
    """Characters a reader sees before opening anything: a closed <details> shows only its summary."""
    if b.startswith("<details"):
        m = re.search(r"<summary>(.*?)</summary>", b, re.S)
        return 60 + len(strip_tags(m.group(1))) if m else 60
    return len(strip_tags(b))


def page_html(cls, runhead, inner, folio):
    return (f'<section class="page {cls}"><div class="runhead">{runhead}</div><div class="pbody">{inner}</div>'
            f'<div class="folio">{folio}</div></section>')


def build_book(texts):
    chapters, n = [], 0
    for i, (stem, label) in enumerate(NAV):
        md = texts.get("index" if stem == "intro" else stem)
        if md is None:
            continue
        html = interactive_html(markdown.markdown(md, extensions=["tables", "md_in_html"]))
        title, spreads = paginate(stem, html)
        chapters.append((stem, label, BANNER_COLORS[i % len(BANNER_COLORS)], title, spreads))
    # page numbers and anchors first, so tables of contents can point at them
    sid = {}
    for stem, label, color, title, spreads in chapters:
        for k, sp in enumerate(spreads):
            n += 1
            sp["id"], sp["folio"] = n, 2 * n - 1
            if sp.get("section") and (stem, sp["section"]) not in sid:
                sid[(stem, sp["section"])] = sp
    out = []
    for stem, label, color, title, spreads in chapters:
        short = re.sub(r"^\d+\s+", "", label)
        for sp in spreads:
            f = sp["folio"]
            attrs = f'class="spread {sp["kind"]}" id="p{sp["id"]}" data-ch="{stem}" style="--c:{color}"'
            if sp["kind"] == "opener":
                m = re.match(r"(\d+)\s+(.*)", title)
                num, name = (f"Chapter {m.group(1)}", m.group(2)) if m else ("", title)
                toc = "".join(f'<li><a href="#p{sid[(stem, h)]["id"]}">{h}</a><span>{sid[(stem, h)]["folio"]}</span></li>'
                              for h in sp["heads"] if (stem, h) in sid)
                left = (f'<div class="titlepage"><img src="icons/{stem}.svg" alt=""><div class="chnum">{num}</div>'
                        f'<h1 class="lettering">{name}</h1>' + (f'<ol class="toc">{toc}</ol>' if toc else "") + "</div>")
                out.append(f'<article {attrs}>{page_html("left", "", left, f)}'
                           f'{page_html("right", short, "".join(sp["right"]), f + 1)}</article>')
            elif sp["kind"] == "wide":
                out.append(f'<article {attrs}>{page_html("full", f"{short} &middot; {sp["section"]}", sp["left"][0], f"{f} and {f + 1}")}</article>')
            else:
                right = ("".join(sp["right"]) if sp["kind"] == "text"
                         else f'<div class="plate-art"><img src="icons/{stem}.svg" alt=""><p class="lettering">{short}</p></div>')
                out.append(f'<article {attrs}>{page_html("left", short, "".join(sp["left"]), f)}'
                           f'{page_html("right", sp.get("section") or short, right, f + 1)}</article>')
    n += 1
    f = 2 * n - 1
    colophon = ('<div class="colophon"><h2>About this book</h2><p>EC 391 Country Team Project: Singapore, Fall 2026. Every chart '
                'is built by the team from raw data with the scripts in the project repository, and sources are under each '
                'figure and in the appendix.</p><p><a href="EC391_Singapore.md">Full text (Markdown)</a><br>'
                '<a href="article/index.html">Static article version</a><br><a href="#cover" class="to-cover">Back to the cover</a></p></div>')
    back = ('<div class="backcover"><img src="merlion.svg" alt=""><p class="lettering">The End</p>'
            '<p class="hand">From a little red dot to a global hub</p></div>')
    out.append(f'<article class="spread end" id="p{n}" data-ch="appendix" style="--c:#4db6ec">'
               f'{page_html("left", "Colophon", colophon, f)}{page_html("right", "", back, f + 1)}</article>')
    return "\n".join(out), n


def build_interactive(texts):
    book, nspreads = build_book(texts)
    nav = "".join(f'<a href="#{s}">{l}</a>' for s, l in NAV)
    version = str(int(time.time()))  # cache-busting: browsers must not mix old modules or data with new ones
    page = (APP / "index.html").read_text(encoding="utf-8").replace("{{NAV}}", nav).replace("{{SECTIONS}}", book)
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
            texts[stem] = md
            report.append(md)
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
