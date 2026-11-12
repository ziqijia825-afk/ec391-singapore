"""Regenerate every figure and derived table from the raw data, then build the site and the Markdown report.

Run after any data update: python scripts/run_all.py   (downloads are separate: scripts/fetch_*.py)
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["baci_hhi.py", "ch01_profile.py", "ch02_macro.py", "ch03_trade.py", "ch04_rca.py", "ch05_gvc.py", "ch06_fdi.py",
         "ch07_policy.py", "ch09_case.py", "export_site_data.py"]


def main():
    from sectors import table_markdown  # noqa: PLC0415  (shared sector table for the appendix)
    (HERE.parent / "data" / "derived" / "sector_table.md").write_text(
        table_markdown() + "\n*Mapping between classifications is approximate (for example, HS 84 includes "
        "computers, which ISIC classifies in C26).*\n")
    for step in STEPS:
        print(f"== {step}", flush=True)
        subprocess.run([sys.executable, str(HERE / step)], check=True, cwd=HERE, stdout=subprocess.DEVNULL)
    subprocess.run([sys.executable, str(HERE.parent / "site" / "build.py")], check=True)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
