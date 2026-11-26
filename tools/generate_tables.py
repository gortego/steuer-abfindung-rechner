"""Extract the 1000-EUR overview tax tables (PDF) into the single-file HTML app.

Also creates clearly labelled projected tables, configured in config.ini under
[table_projection.YEAR], by shifting a base year's table to the right.

Usage:  py -3 tools/generate_tables.py

Requires pypdf:  py -3 -m pip install pypdf
"""

from __future__ import annotations

import configparser
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.ini"

TABLE_YEARS = tuple(range(2021, 2028))
TARIFF_FILES = {"grund": "grundtabelle", "split": "splittingtabelle"}


def discover_sources() -> dict[tuple[str, str], str]:
    """Find every supplied 1,000-EUR overview table for the timeline chart."""
    sources: dict[tuple[str, str], str] = {}
    for year in TABLE_YEARS:
        for tariff, stem in TARIFF_FILES.items():
            path = ROOT / "tabelle" / f"{stem}-{year}-ueberblick-klein.pdf"
            if not path.is_file():
                raise RuntimeError(f"Missing source table: {path.name}")
            sources[(str(year), tariff)] = path.relative_to(ROOT).as_posix()
    return sources


SOURCES = discover_sources()

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


def projection_settings() -> dict[str, dict]:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        parser.read_file(handle)
    settings = {}
    for section in parser.sections():
        if not section.startswith("table_projection."):
            continue
        year = section.split(".", 1)[1]
        options = dict(parser.items(section))
        settings[year] = {
            "base_year": options["base_year"],
            "shifts": {
                "grund": float(options["zve_shift_grund"]),
                "split": float(options["zve_shift_split"]),
            },
        }
    return settings


def row_at(rows: list[list[float]], zve: float) -> list[float]:
    """Mirror of the app's lookup(), used to resample a projected table."""
    first, last = rows[0][0], rows[-1][0]
    if zve <= first:
        return [0.0, 0.0, 0.0, 0.0]
    if zve >= last:
        a, b = rows[-2], rows[-1]
        t = (zve - a[0]) / (b[0] - a[0])
        return [a[i] + (b[i] - a[i]) * t for i in range(1, 5)]
    i = int((zve - first) // 1000)
    a, b = rows[i], rows[i + 1]
    t = (zve - a[0]) / (b[0] - a[0])
    return [a[i] + (b[i] - a[i]) * t for i in range(1, 5)]


def project_table(rows: list[list[float]], shift: float) -> list[list[float]]:
    """Shift the tax schedule right: ESt_new(x) = ESt_base(x - shift)."""
    return [[row[0], *row_at(rows, row[0] - shift)] for row in rows]


def main() -> None:
    tables: dict[str, dict[str, list[list[float]]]] = {}
    for (year, tariff), filename in SOURCES.items():
        rows = extract(ROOT / filename)
        tables.setdefault(year, {})[tariff] = rows
        print(f"{filename}: {len(rows)} rows, zvE {rows[0][0]:,} - {rows[-1][0]:,}")

    for year, settings in projection_settings().items():
        base = settings["base_year"]
        for tariff in ("grund", "split"):
            shift = settings["shifts"][tariff]
            rows = project_table(tables[base][tariff], shift)
            tables.setdefault(year, {})[tariff] = rows
            print(
                f"projection {year} {tariff} from {base} (+{shift:g} EUR zvE): "
                f"{len(rows)} rows, zvE {rows[0][0]:,} - {rows[-1][0]:,}"
            )

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
