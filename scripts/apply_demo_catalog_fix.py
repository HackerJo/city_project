#!/usr/bin/env python3
# Demo catalog fix: the viewer uses the catalog stored with the current run.
# Run in the project root:  python apply_demo_catalog_fix.py
# Changes teacher_backend.py, teacher_demo.py and cityviewer/scripts/main.gd.
# Backups are written first; nothing is changed if an anchor is missing.
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path

TAG = "CITYPROJECT_RUN_CATALOG_V1"

BACKEND = [
('''    current = project / "cityviewer/data/buildings.json"
    snapshot = run / "input/output/buildings.json"
    if read_json(current) != read_json(snapshot):
        raise ValueError("Der Gebaeudekatalog wurde seit der Erkennung geaendert. Bitte erneut erkennen.")
''',
'''    # CITYPROJECT_RUN_CATALOG_V1: the viewer reads the catalogue stored with this run.
    snapshot = (run / "input/output/buildings.json").resolve()
    if not snapshot.is_file():
        raise ValueError("Der Gebaeudekatalog dieses Laufs fehlt. Bitte erneut erkennen.")
    catalog_arg = str(snapshot)
'''),
('''        return [str(viewer_exe), "--", str((run / "result/city.json").resolve())]''',
 '''        return [str(viewer_exe), "--", str((run / "result/city.json").resolve()), catalog_arg]'''),
('''            "--", str((run / "result/city.json").resolve())]''',
 '''            "--", str((run / "result/city.json").resolve()), catalog_arg]'''),
]

DEMO = [
('''    if prepared:
        check_viewer_catalog(project, catalog)
    elif''',
'''    if prepared:
        pass  # CITYPROJECT_RUN_CATALOG_V1: the demo is shown with its own catalogue
    elif'''),
]

MAIN = [
('''func _load_json(path: String):''',
'''# CITYPROJECT_RUN_CATALOG_V1: optional 2nd argument = catalogue of this run
func _catalog_path() -> String:
	var args := OS.get_cmdline_user_args()
	if args.size() > 1:
		return args[1]
	return BUILDINGS_PATH


func _load_json(path: String):'''),
('''	var data = _load_json(BUILDINGS_PATH)''',
 '''	var data = _load_json(_catalog_path())'''),
]

def convert(text, pairs):
    if TAG in text:
        return text
    crlf = "\r\n" in text
    for old, new in pairs:
        if crlf:
            old, new = old.replace("\n", "\r\n"), new.replace("\n", "\r\n")
        if text.count(old) != 1:
            raise ValueError("Anker nicht eindeutig gefunden: " + old.strip().splitlines()[0])
        text = text.replace(old, new)
    return text

def apply(root: Path):
    jobs = [(root / "teacher_backend.py", BACKEND),
            (root / "teacher_demo.py", DEMO),
            (root / "cityviewer" / "scripts" / "main.gd", MAIN)]
    prepared = []
    for path, pairs in jobs:
        raw = path.read_bytes().decode("utf-8")
        prepared.append((path, raw, convert(raw, pairs)))
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for path, raw, new in prepared:
        if raw == new:
            print("Bereits angewendet:", path.name)
            continue
        path.with_name(path.name + ".before_run_catalog_" + stamp + ".bak").write_bytes(raw.encode("utf-8"))
        path.write_bytes(new.encode("utf-8"))
        print("Geaendert:", path)
    print("Fertig. Danach: Godot-Export, dann build_lehrerausgabe.ps1.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path.cwd())
    a = p.parse_args()
    try:
        apply(a.root.resolve())
    except (OSError, ValueError, UnicodeError) as exc:
        p.exit(1, "FEHLER: " + str(exc) + "\n")
