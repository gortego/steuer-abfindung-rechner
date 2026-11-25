"""Verify the embedded tax tables and interpolation logic against the source PDFs.

Usage:  py -3 tools/verify_calculation.py

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

# A PDF data line has five numeric tokens: zvE, ESt, SolZu, KiSt 8 %, KiSt 9 %.
NUMBER = re.compile(r"^-?[\d.,]+$")
TOL = 1e-9


def num(value: str) -> float:
    return float(value.replace(".", "").replace(",", "."))


def extract_pdf(path: Path) -> dict[int, list[float]]:
    rows: dict[int, list[float]] = {}
    for page in PdfReader(str(path)).pages:
        for line in page.extract_text().splitlines():
            tokens = [t for t in line.split() if NUMBER.match(t)]
            if len(tokens) < 5:
                continue
            zve = int(tokens[0].replace(".", ""))
            rows[zve] = [num(t) for t in tokens[1:5]]
    if not rows:
        raise RuntimeError(f"No rows extracted from {path.name}")
    return rows


def embedded_tables() -> dict[str, dict[str, list[list[float]]]]:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    match = re.search(r"const TABLES = (\{.*?\});\s*/\* TABLES_END \*/", html, re.S)
    if not match:
        raise RuntimeError("Embedded TABLES block not found in index.html")
    return json.loads(match.group(1))


def lookup(rows: list[list[float]], zve: float) -> list[float]:
    """Python mirror of the JavaScript lookup() used by index.html."""
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


def close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    tables = embedded_tables()
    failures = 0

    for (year, tariff), filename in SOURCES.items():
        source = extract_pdf(ROOT / filename)
        embedded_list = tables[year][tariff]
        embedded = {row[0]: row[1:] for row in embedded_list}
        keys = sorted(source)

        label = f"{year} {tariff}"
        if set(source) != set(embedded):
            missing = sorted(set(source) - set(embedded))[:5]
            extra = sorted(set(embedded) - set(source))[:5]
            print(f"FAIL {label}: key mismatch; missing={missing} extra={extra}")
            failures += 1
            continue

        if any(b - a != 1000 for a, b in zip(keys, keys[1:])):
            print(f"FAIL {label}: zvE steps are not 1000 EUR")
            failures += 1

        max_table_diff = 0.0
        max_lookup_diff = 0.0
        kist_failures = 0

        for zve, expected in source.items():
            actual = embedded[zve]
            for e, a in zip(expected, actual):
                max_table_diff = max(max_table_diff, abs(e - a))
            # The PDF's church-tax columns are ESt × 8 % / 9 %.
            if abs(expected[0] * 0.08 - expected[2]) > 1e-8:
                kist_failures += 1
            if abs(expected[0] * 0.09 - expected[3]) > 1e-8:
                kist_failures += 1

            got = lookup(embedded_list, zve)
            for e, g in zip(expected, got):
                max_lookup_diff = max(max_lookup_diff, abs(e - g))

        # Midpoints must equal the mean of the two neighbouring table rows.
        for a_zve, b_zve in zip(keys, keys[1:]):
            expected = [(e + a) / 2 for e, a in zip(embedded[a_zve], embedded[b_zve])]
            got = lookup(embedded_list, (a_zve + b_zve) / 2)
            for e, g in zip(expected, got):
                max_lookup_diff = max(max_lookup_diff, abs(e - g))

        # Above the last row, the same linear slope is continued.
        a_zve, b_zve = keys[-2], keys[-1]
        expected = [e + (e - a) / 2 for e, a in zip(embedded[b_zve], embedded[a_zve])]
        got = lookup(embedded_list, b_zve + 500)
        for e, g in zip(expected, got):
            max_lookup_diff = max(max_lookup_diff, abs(e - g))

        ok = max_table_diff <= TOL and max_lookup_diff <= TOL and kist_failures == 0
        if not ok:
            failures += 1
        print(
            f"{'OK  ' if ok else 'FAIL'} {label}: {len(keys):>4} rows, "
            f"PDF-vs-HTML max diff {max_table_diff:.2e}, "
            f"lookup/interpolation max diff {max_lookup_diff:.2e}, "
            f"KiSt checks {'ok' if kist_failures == 0 else f'{kist_failures} failed'}"
        )

    if failures:
        raise SystemExit(f"{failures} verification group(s) failed")
    print("All embedded tables and interpolation checks match the source PDFs.")


if __name__ == "__main__":
    main()
