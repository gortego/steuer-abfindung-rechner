"""Extract the 1000-EUR overview tax tables (PDF) into the single-file HTML app.

Usage:  py -3 tools/generate_tables.py

Requires pypdf:  py -3 -m pip install pypdf
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent

SOURCES = {
    ("2026", "grund"): "tabelle/grundtabelle-2026-ueberblick-klein.pdf",
    ("2026", "split"): "tabelle/splittingtabelle-2026-ueberblick-klein.pdf",
    ("2027", "grund"): "tabelle/grundtabelle-2027-ueberblick-klein.pdf",
    ("2027", "split"): "tabelle/splittingtabelle-2027-ueberblick-klein.pdf",
}

# A data line contains five numeric tokens (zvE, ESt, SolZu, KiSt 8 %, KiSt 9 %)
# separated by currency symbols, which pypdf may return as a replacement character.
NUMBER = re.compile(r"^-?[\d.,]+$")

START = "/* TABLES_START */"
END = "/* TABLES_END */"


def num(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def extract(path: Path) -> list[list[float]]:
    rows: dict[int, list[float]] = {}
    reader = PdfReader(str(path))
    for page in reader.pages:
        for line in page.extract_text().splitlines():
            tokens = [t for t in line.split() if NUMBER.match(t)]
            if len(tokens) < 5:
                continue
            zve = int(tokens[0].replace(".", ""))
            rows[zve] = [num(t) for t in tokens[1:5]]
    if not rows:
        raise RuntimeError(f"No rows extracted from {path.name}")

    keys = sorted(rows)
    step = 1000
    if any(b - a != step for a, b in zip(keys, keys[1:])):
        raise RuntimeError(f"Non-consecutive 1000-EUR steps in {path.name}: {keys[:5]} ... {keys[-5:]}")

    return [[k, *rows[k]] for k in keys]


def main() -> None:
    tables: dict[str, dict[str, list[list[float]]]] = {}
    for (year, tariff), filename in SOURCES.items():
        rows = extract(ROOT / filename)
        tables.setdefault(year, {})[tariff] = rows
        print(f"{filename}: {len(rows)} rows, zvE {rows[0][0]:,} - {rows[-1][0]:,}")

    payload = json.dumps(tables, separators=(",", ":"), ensure_ascii=False)
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    if START not in html or END not in html:
        raise RuntimeError(f"Markers {START} / {END} missing in index.html")

    before, rest = html.split(START, 1)
    _, after = rest.split(END, 1)
    block = f"{START}\nconst TABLES = {payload};\n{END}"
    html_path.write_text(before + block + after, encoding="utf-8")
    print(f"Written {len(payload):,} bytes of table data into {html_path.name}")


if __name__ == "__main__":
    main()
