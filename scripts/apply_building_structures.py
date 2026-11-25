#!/usr/bin/env python3
"""Local viewer patch. Run: python scripts/apply_building_structures.py"""
from pathlib import Path
from datetime import datetime
import argparse
import ast

ALIASES = {
    "courthouse": "mill", "synagogue": "house", "hospital": "mill",
    "weaving": "house", "dyeing": "house", "pottery": "house",
    "tailoring": "house", "armory": "house", "warehouse": "mill",
    "cemetery": "market", "art_smithy": "smithy",
}
TAG = "# CITYPROJECT_BUILDING_ALIASES_V1"

def transform_builder(text):
    if TAG in text:
        return text
    helper = "\n\n" + TAG + "\nfunc structure_key(key: String) -> String:\n\tmatch key:\n"
    for key, target in ALIASES.items():
        helper += '\t\t"' + key + '":\n\t\t\treturn "' + target + '"\n'
    helper += "\treturn key\n"
    names = ("can_build", "leaves_floor_open", "build_building")
    lines = text.splitlines(keepends=True)
    for name in names:
        matches = [i for i, line in enumerate(lines) if line.startswith("func " + name + "(")]
        if len(matches) != 1:
            raise ValueError("Builder: erwartete Funktion fehlt/mehrfach: " + name)
        i = matches[0]
        if not lines[i].rstrip().endswith(":"):
            raise ValueError("Mehrzeilige Signatur nicht unterstuetzt: " + name)
        lines.insert(i + 1, "\tkey = structure_key(key)\n")
    return "".join(lines) + helper

def transform_main(text):
    if TAG in text:
        return text
    anchor = '\t\tvar info: Dictionary = catalog.get(str(entry["key"]), {})'
    if text.count(anchor) != 1:
        raise ValueError("main.gd: Katalog-Zeile nicht eindeutig gefunden; keine Dateien geaendert.")
    addition = (
        '\n\t\t' + TAG + '\n'
        '\t\tvar structure := builder.structure_key(str(entry["key"]))\n'
        '\t\tif structure != str(entry["key"]):\n'
        '\t\t\tinfo = info.duplicate()\n'
        '\t\t\tinfo["style"] = "modular"\n'
        '\t\t\tvar source_info: Dictionary = catalog.get(structure, {})\n'
        '\t\t\tinfo["floors"] = int(source_info.get("floors", info.get("floors", 1)))'
    )
    return text.replace(anchor, anchor + addition)

def apply(root):
    folder = root / "cityviewer" / "scripts"
    jobs = [(folder / "building_builder.gd", transform_builder),
            (folder / "main.gd", transform_main)]
    prepared = []
    for path, transform in jobs:
        original = path.read_text(encoding="utf-8-sig")
        prepared.append((path, original, transform(original)))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    for path, original, updated in prepared:
        if original == updated:
            print("Bereits angewendet:", path)
            continue
        backup = path.with_name(path.name + ".before_structures_" + stamp + ".bak")
        backup.write_bytes(path.read_bytes())
        path.write_text(updated, encoding="utf-8")
        print("Geaendert:", path, "Backup:", backup.name)
    print("Fertig. Godot-Quellprojekt testen; exportierter Viewer muss neu gebaut werden.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        apply(args.root.resolve())
    except (OSError, ValueError) as exc:
        parser.exit(1, "FEHLER: " + str(exc) + "\n")
