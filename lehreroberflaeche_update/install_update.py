from pathlib import Path
from datetime import datetime
import shutil
import hashlib
import json

bundle = Path(__file__).resolve().parent
project = bundle.parent
if not (project / "scripts/detect_city.py").is_file() or not (project / "cityviewer/project.godot").is_file():
    raise SystemExit("Den Ordner lehreroberflaeche_update direkt in city_project ablegen. Nichts geaendert.")
names = ["teacher_app.py", "teacher_backend.py", "test_teacher_backend.py", "requirements-teacher.txt",
         "Start_Lehreroberflaeche.bat", "Readme.Dev.md", "Readme.Teacher.md"]
for name in names:
    if not (bundle / name).is_file():
        raise SystemExit("Updatepaket unvollstaendig: " + name)
backup = project / ("backup_vor_lehreroberflaeche_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
backup.mkdir()
# Save the current code/configuration, not large models, executables or caches.
extensions = {".py", ".gd", ".uid", ".tscn", ".godot", ".json", ".csv", ".cfg", ".md", ".txt", ".bat", ".ps1", ".gdshader"}
files = list(project.glob("*"))
selected = [p for p in files if p.is_file() and p.suffix.lower() in extensions]
for folder in ("scripts", "settings", "cityviewer/scripts", "cityviewer/scenes", "cityviewer/data"):
    path = project / folder
    if path.is_dir():
        selected.extend(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in extensions and "__pycache__" not in p.parts)
if (project / "cityviewer/project.godot").is_file():
    selected.append(project / "cityviewer/project.godot")
for name in ("layout.json", "buildings.json"):
    p = project / "output" / name
    if p.is_file():
        selected.append(p)
manifest = []
for p in sorted(set(selected)):
    rel = p.relative_to(project)
    dest = backup / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    manifest.append({"path": rel.as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
(backup / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
for name in names:
    shutil.copy2(bundle / name, project / name)
print("Lehreroberflaeche als Entwicklungsfassung installiert.")
print("Code-/Konfigurationssicherung (ohne Modelle/Fotos):", backup)
print("Naechster Schritt: python -m pip install -r requirements-teacher.txt")
print("Dann: python teacher_app.py oder Start_Lehreroberflaeche.bat doppelklicken.")
print("Keine vorhandenen Erkennungs-, Godot-, CSV- oder JSON-Dateien ersetzt.")
