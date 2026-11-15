from pathlib import Path
import csv
import io
import json
import shutil
from datetime import datetime

bundle = Path(__file__).resolve().parent
project = bundle.parent
if not (project / "cityviewer/project.godot").is_file():
    raise SystemExit("Den Ordner oeffentliche_gebaeude_update bitte direkt in city_project ablegen.")
json_path = project / "cityviewer/data/buildings.json"
if not json_path.is_file():
    raise SystemExit("buildings.json fehlt. Zuerst python scripts/generate_prints.py ausfuehren.")
try:
    data = json.loads(json_path.read_text(encoding="utf-8-sig"))
    buildings = data["buildings"]
    if not isinstance(buildings, list):
        raise ValueError("buildings ist keine Liste")
    keys = {str(row.get("key", "")) for row in buildings}
    required = {"monastery", "town_hall", "guildhall"}
    if not required.issubset(keys):
        raise ValueError("Katalogeintraege fehlen: " + str(required - keys))
except (ValueError, KeyError, TypeError) as exc:
    raise SystemExit("Ungueltiger Gebaeudekatalog. Nichts geaendert: " + str(exc))
for row in buildings:
    key = row.get("key")
    if key in required:
        row["style"] = "modular"
        row["floors"] = 2 if key == "monastery" else 3
files = ["cityviewer/scripts/building_builder.gd", "cityviewer/scripts/main.gd",
         "cityviewer/data/parts.csv", "settings/buildings.csv"]
for rel in files:
    if not (bundle / "dateien" / rel).is_file():
        raise SystemExit("Paket unvollstaendig: " + rel)
backup = project / ("backup_oeffentliche_gebaeude_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
for rel in files + ["cityviewer/data/buildings.json"]:
    dest = project / rel
    if dest.exists():
        saved = backup / rel
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, saved)
for rel in files:
    dest = project / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bundle / "dateien" / rel, dest)
json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Kloster, Zunfthaus und Rathaus installiert.")
print("CSV und Laufzeit-JSON: modular; Geschosse 2 / 3 / 3.")
print("Sicherung:", backup)
print("Viewer jetzt neu starten. Keine alten Patchskripte erneut ausfuehren.")
