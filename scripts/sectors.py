"""Shared sector table used by Ch. 3 (export structure), Ch. 4 (RCA), Ch. 5 (TiVA) and Ch. 6 (FDI by industry),
so that the chapters talk about the same industries.

Each sector maps to HS 1992 chapters (goods trade, CEPII BACI / UN Comtrade), a World Bank WDI services export
category, OECD TiVA ISIC rev.4 activity codes, and SingStat FDI-by-industry series numbers (table M084831). Mappings are approximate: HS products
and ISIC industries are different classifications (e.g. HS 84 includes computers, which ISIC puts in C26).
"""
import pandas as pd

SECTORS = [
    # name, HS chapters, WDI services indicator, TiVA activities, SingStat FDI series
    ("Electronics & instruments", list(range(85, 86)) + [90, 91, 92], None, ["C26_27"], ["1.1.10", "1.1.11"]),
    ("Machinery incl. computers", [84], None, ["C28"], ["1.1.9"]),
    ("Refined petroleum", [27], None, ["C19"], ["1.1.3"]),
    ("Chemicals & plastics", [28, 29] + list(range(31, 41)), None, ["C20", "C22"], ["1.1.4", "1.1.6"]),
    ("Pharmaceuticals", [30], None, ["C21"], ["1.1.5"]),
    ("Gold & metals", list(range(71, 84)), None, ["C24_25"], ["1.1.7", "1.1.8"]),
    ("Food & agriculture", list(range(1, 25)), None, ["A", "C10T12"], ["1.1.1"]),
    ("Transport equipment", list(range(86, 90)), None, ["C29_30"], ["1.1.12"]),
    ("Other goods", None, None, None, None),  # all remaining HS chapters
    ("Wholesale trade", None, None, ["G"], ["1.3.1"]),
    ("Transport & logistics", None, "BX.GSR.TRAN.ZS", ["H"], ["1.5"]),
    ("Finance & insurance", None, "BX.GSR.INSF.ZS", ["K"], ["1.7"]),
    ("ICT & business services", None, "BX.GSR.CMCP.ZS", ["J", "M_N"], ["1.6", "1.9"]),
    ("Travel & tourism", None, "BX.GSR.TRVL.ZS", ["I"], ["1.4"]),
]

GOODS = [s[0] for s in SECTORS if s[1] is not None] + ["Other goods"]
SERVICES = [s[0] for s in SECTORS if s[2] is not None]


def hs_to_sector():
    """dict HS chapter (int 1-99) -> goods sector name."""
    m = {}
    for name, chapters, *_ in SECTORS:
        for c in chapters or []:
            m[c] = name
    return {c: m.get(c, "Other goods") for c in range(1, 100)}


def services_to_sector():
    return {code: name for name, _, code, *_ in SECTORS if code}


def table_markdown():
    """The sector table as Markdown for the appendix."""
    def chapters(cs):
        if not cs:
            return ""
        cs = sorted(cs)
        runs, start = [], cs[0]
        for a, b in zip(cs, cs[1:] + [None]):
            if b != a + 1:
                runs.append(f"{start:02d}" if start == a else f"{start:02d} to {a:02d}")
                start = b
        return ", ".join(runs)
    lines = ["| Sector | HS 1992 chapters (BACI) | WDI services exports | OECD TiVA (ISIC rev.4) | SingStat FDI series |",
             "| --- | --- | --- | --- | --- |"]
    for name, cs, svc, tiva, fdi in SECTORS:
        lines.append(f"| {name} | {chapters(cs) if cs else ('all other' if name == 'Other goods' else '')} | "
                     f"{svc or ''} | {', '.join(tiva or [])} | {', '.join(fdi or [])} |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(table_markdown())
    print(pd.Series(hs_to_sector()).value_counts())
