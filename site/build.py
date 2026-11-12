"""Build the website from text/*.md and figures/*.png into _site/ (published by GitHub Pages).

Pages, in storyline order. A section with no Markdown file yet shows a "coming soon" note.
"""
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

PAGES = [  # (file stem, nav label)
    ("index", "Home"),
    ("ch01_profile", "1 Country profile"),
    ("ch02_macro", "2 Macro & governance"),
    ("ch03_trade", "3 Trade patterns"),
    ("ch04_rca", "4 Comparative advantage"),
    ("ch05_gvc", "5 Global value chains"),
    ("ch06_fdi", "6 FDI"),
    ("ch07_policy", "7 Trade policy"),
    ("ch09_case", "9 Case study"),
    ("conclusion", "Conclusion"),
]

CSS = """
:root{--ink:#1f1f1d;--muted:#5f5e5a;--line:#e4e3dd;--accent:#2a78d6;--bg:#fbfbf9}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--bg)}
nav{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--line);padding:10px 24px;display:flex;flex-wrap:wrap;gap:4px 16px;font-size:14px;z-index:1}
nav a{color:var(--muted);text-decoration:none}nav a.on{color:var(--accent);font-weight:600}
main{max-width:860px;margin:0 auto;padding:32px 24px 80px}
h1{font-size:30px;line-height:1.25}h2{margin-top:40px;font-size:22px}
img{max-width:100%;border:1px solid var(--line);border-radius:8px;background:#fff}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
.soon{color:var(--muted);font-style:italic}footer{color:var(--muted);font-size:13px;margin-top:48px}
"""


def page(stem, label, body):
    nav = "".join(
        f'<a href="{s}.html"{" class=on" if s == stem else ""}>{l}</a>' for s, l in PAGES
    )
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{label} | Singapore: EC 391</title>
<style>{CSS}</style></head><body><nav>{nav}</nav><main>{body}
<footer>EC 391 Country Team Project: Singapore. Data sources are listed under each figure.</footer></main></body></html>"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "figures", OUT / "figures")
    for stem, label in PAGES:
        src = ROOT / "text" / f"{stem}.md"
        if src.exists():
            md = src.read_text(encoding="utf-8").replace("](../figures/", "](figures/")
            body = markdown.markdown(md, extensions=["tables"])
        else:
            body = f"<h1>{label}</h1><p class=soon>Coming soon.</p>"
        (OUT / f"{stem}.html").write_text(page(stem, label, body), encoding="utf-8")
    print(f"built {len(PAGES)} pages into {OUT}")


if __name__ == "__main__":
    main()
