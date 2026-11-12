"""Build the website from text/*.md and figures/*.png into _site/ (published by GitHub Pages), and the single
Markdown deliverable (all sections concatenated) into report/EC391_Singapore.md.

Pages, in storyline order. A section with no Markdown file yet shows a "coming soon" note.
A line `<!-- include: data/derived/NAME.md -->` in a text file is replaced by that generated table, so tables come
straight from the analysis scripts.
"""
import re
import shutil
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
<a href="EC391_Singapore.md">Download the full text (Markdown)</a>.</footer></main></body></html>"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "figures", OUT / "figures")
    report = []
    for i, (stem, label) in enumerate(PAGES):
        src = ROOT / "text" / f"{stem}.md"
        prev = PAGES[i - 1] if i > 0 else None
        nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
        if src.exists():
            md = expand(src.read_text(encoding="utf-8"))
            report.append(md.replace("](../figures/", "](figures/"))
            body = markdown.markdown(md.replace("](../figures/", "](figures/"), extensions=["tables", "md_in_html"])
        else:
            body = f"<h1>{label}</h1><p class=soon>Coming soon.</p>"
        (OUT / f"{stem}.html").write_text(page(stem, label, body, prev, nxt), encoding="utf-8")
    REPORT.parent.mkdir(exist_ok=True)
    text = "\n\n---\n\n".join(report)
    REPORT.write_text(text.replace("](figures/", "](../figures/") + "\n", encoding="utf-8")
    (OUT / "EC391_Singapore.md").write_text(text + "\n", encoding="utf-8")
    print(f"built {len(PAGES)} pages into {OUT}; report at {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
