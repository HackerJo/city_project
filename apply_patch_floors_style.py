#!/usr/bin/env python3
"""Add the columns "floors" and "style" to the Python scripts (run once from the project root).

    python apply_patch_floors_style.py

Patches scripts/settings_loader.py and scripts/generate_prints.py in place (idempotent).
"""
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
if not (root / "scripts").exists():
    root = Path.cwd()

FIELDS = '    floors: int = 1\n    style: str = "block"\n'
PARSE = (
    '        floors = _to_int(r.get("floors", "1") or "1", 1)\n'
    '        if floors is None:\n'
    '            problems.append(t("p_bad_int", field="floors", minimum=1))\n'
    '            floors = 1\n'
    '        style = (r.get("style", "block") or "block").lower()\n'
    '        if style not in ("block", "modular"):\n'
    '            style = "block"\n'
)


def patch(path: Path, edits: list) -> None:
    text = path.read_text(encoding="utf-8")
    if "floors" in text:
        print("already patched:", path.name)
        return
    for pattern, addition, label in edits:
        text, count = re.subn(pattern, lambda m, a=addition: m.group(1) + a, text, count=1)
        if count != 1:
            sys.exit(f"{path.name}: could not apply edit '{label}'. Is the file the expected version?")
    path.write_text(text, encoding="utf-8")
    print("patched:", path.name)


patch(root / "scripts" / "settings_loader.py", [
    (r'(    count: int\n    active: bool\n)', FIELDS, "dataclass fields"),
    (r'(        if count is None: problems\.append\(t\("p_bad_int", field="count", minimum=0\)\)\n)', PARSE, "parse floors and style"),
    (r'(width, depth, r\.get\("model", ""\), color\.lower\(\), height, count, active)(?=\))', ", floors, style", "Building(...) call"),
])

patch(root / "scripts" / "generate_prints.py", [
    (r'("color": b\.color, "height_m": b\.height_m)(?=\})', ', "floors": b.floors, "style": b.style', "buildings.json fields"),
])
