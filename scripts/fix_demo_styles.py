#!/usr/bin/env python3
# Set style "modular" for the five block buildings in all demo catalogues.
# Run in the project root:  python fix_demo_styles.py
import json
from pathlib import Path

KEYS = {"monastery", "town_hall", "guildhall", "courthouse", "hospital"}

def fix(root: Path) -> None:
    for path in sorted((root / "examples").glob("city*/buildings.json")):
        raw = path.read_bytes().decode("utf-8-sig")
        data = json.loads(raw)
        changed = [b["key"] for b in data.get("buildings", [])
                   if b.get("key") in KEYS and b.get("style") != "modular"]
        if not changed:
            print("Unveraendert:", path.parent.name)
            continue
        for b in data["buildings"]:
            if b.get("key") in changed:
                b["style"] = "modular"
        eol = "\r\n" if "\r\n" in raw else "\n"
        text = json.dumps(data, indent=2, ensure_ascii=False).replace("\n", eol)
        path.with_name("buildings.json.bak_style").write_bytes(raw.encode("utf-8"))
        path.write_bytes(text.encode("utf-8"))
        print("Geaendert:", path.parent.name, changed)

if __name__ == "__main__":
    fix(Path.cwd())
