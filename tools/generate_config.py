"""Embed config.ini as `const CONFIG` into the single-file HTML app.

Usage:  py -3 tools/generate_config.py

The .ini file is the source of truth. This build step only serialises it to
JSON between the CONFIG_START / CONFIG_END markers in index.html; the browser
never reads config.ini itself.
"""

from __future__ import annotations

import configparser
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.ini"
HTML_PATH = ROOT / "index.html"

START = "/* CONFIG_START */"
END = "/* CONFIG_END */"

INT = re.compile(r"^[+-]?\d+$")
FLOAT = re.compile(r"^[+-]?(?:\d+\.\d*|\.\d+|\d+[eE][+-]?\d+|\d+\.\d*[eE][+-]?\d+)$")
# Do not treat numeric 0/1 as booleans: numeric limits and steps must stay
# numbers (a `false` min becomes NaN in JavaScript and breaks range sliders).
BOOL_TRUE = {"true", "yes", "on"}
BOOL_FALSE = {"false", "no", "off"}


def value(raw: str):
    """Convert an .ini string to a JSON-compatible Python value."""
    text = raw.strip()
    if not text:
        return ""
    if text[0] in "[{":
        return json.loads(text)
    low = text.lower()
    if low in BOOL_TRUE:
        return True
    if low in BOOL_FALSE:
        return False
    if INT.match(text):
        return int(text)
    if FLOAT.match(text):
        return float(text)
    return text


def load_config() -> dict:
    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str  # preserve bbgRV, kindergeldMonth, etc.
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        parser.read_file(handle)

    payload: dict = {}
    for section in parser.sections():
        if section == "states":
            payload["states"] = []
            for code, spec in parser.items(section):
                name, rate, saxony = [part.strip() for part in spec.split("|")]
                payload["states"].append([code, name, int(rate), value(saxony)])
            continue

        target = payload
        for part in section.split("."):
            target = target.setdefault(part, {})
        for key, raw in parser.items(section):
            target[key] = value(raw)

    # Guard against a silent mismatch between the initial zoom domain and its
    # charts. The domain can grow later, but all three must start in sync.
    gross = payload["limits"]["gross"]
    if gross["slider_max"] != payload["charts"]["abfWork"]["x_max"]:
        raise RuntimeError("gross.slider_max must equal charts.abfWork.x_max")
    if gross["slider_max"] != payload["charts"]["netBrutto"]["axis_max"]:
        raise RuntimeError("gross.slider_max must equal charts.netBrutto.axis_max")
    steps = gross.get("zoom_steps")
    if not isinstance(steps, list) or not steps:
        raise RuntimeError("gross.zoom_steps must be a non-empty JSON list")
    if steps != sorted(steps) or gross["slider_max"] not in steps:
        raise RuntimeError("gross.zoom_steps must be sorted and include slider_max")
    if steps[-1] != gross["number_max"]:
        raise RuntimeError("gross.zoom_steps must end at gross.number_max")
    return payload


def main() -> None:
    payload = load_config()
    serialized = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

    html = HTML_PATH.read_text(encoding="utf-8")
    if START not in html or END not in html:
        raise RuntimeError(f"Markers {START} / {END} missing in {HTML_PATH.name}")

    before, rest = html.split(START, 1)
    _, after = rest.split(END, 1)
    block = f"{START}\nconst CONFIG = {serialized};\n{END}"
    HTML_PATH.write_text(before + block + after, encoding="utf-8")
    print(f"Written {len(serialized):,} bytes of config data into {HTML_PATH.name}")


if __name__ == "__main__":
    main()
