"""Source-mode adapter for the existing detector and Godot project. No network access."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import sys
from datetime import datetime
import uuid

VERSION = "0.2.0-dev"


def data_home() -> Path:
    home = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share")) / "CityProject"
    home.mkdir(parents=True, exist_ok=True)
    return home


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def prepare_run(project: Path, image: Path, work_home: Path | None = None) -> Path:
    project, image = project.resolve(), image.resolve()
    if not image.is_file():
        raise ValueError("Das ausgewaehlte Foto ist nicht mehr vorhanden.")
    detector = project / "scripts" / "detect_city.py"
    if not detector.is_file():
        raise ValueError("scripts/detect_city.py fehlt. Bitte im vollstaendigen Projekt starten.")
    layout_path = project / "output" / "layout.json"
    if not layout_path.is_file():
        raise ValueError("output/layout.json fehlt. Die zum gedruckten Blatt passende Datei wiederherstellen; neue Druckvorlagen nur bei Bedarf erzeugen.")
    # Match the catalogue that main.gd actually reads; never overwrite it automatically.
    catalog_path = project / "cityviewer" / "data" / "buildings.json"
    if not catalog_path.is_file():
        raise ValueError("cityviewer/data/buildings.json fehlt. Der Viewer benoetigt diesen Katalog.")
    layout, catalog = read_json(layout_path), read_json(catalog_path)
    if not isinstance(layout, dict) or not isinstance(catalog, dict):
        raise ValueError("Layout oder Gebaeudekatalog ist kein JSON-Objekt.")
    for key in ("paper_mm", "field_mm", "columns", "rows", "grid_origin_mm", "aruco_dict", "corner_markers_mm"):
        if key not in layout:
            raise ValueError("layout.json: Feld fehlt: " + key)
    if not isinstance(catalog.get("buildings"), list) or not catalog["buildings"]:
        raise ValueError("Der Gebaeudekatalog ist leer oder ungueltig.")
    ids = [int(b["id"]) for b in catalog["buildings"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Doppelte Gebaeude-IDs im Katalog.")
    parent = work_home if work_home is not None else data_home()
    run = parent / "runs" / (datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6])
    (run / "input" / "output").mkdir(parents=True)
    (run / "result").mkdir()
    (run / "input/output/layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")
    (run / "input/output/buildings.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata = {"version": VERSION, "image": str(image), "project": str(project),
                "catalog_source": str(catalog_path), "layout_source": str(layout_path)}
    (run / "session.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return run


def detector_command(project: Path, image: Path, run: Path) -> list[str]:
    return [sys.executable, str(project.resolve() / "scripts/detect_city.py"),
            "--image", str(image.resolve()), "--root", str(run / "input"), "--out", str(run / "result")]


def validate_result(run: Path) -> dict:
    city = read_json(run / "result/city.json")
    if not isinstance(city, dict) or not isinstance(city.get("buildings"), list):
        raise ValueError("Die Erkennung lieferte keine gueltigen Stadtdaten.")
    grid = city.get("grid", {})
    columns, rows = int(grid.get("columns", 0)), int(grid.get("rows", 0))
    if columns < 1 or rows < 1:
        raise ValueError("Das erkannte Raster ist ungueltig.")
    if not city["buildings"]:
        raise ValueError("Keine Gebaeude erkannt. Fotoabstand, Schaerfe und Marker pruefen.")
    issues = [str(x) for x in city.get("warnings", [])]
    occupied = {}
    for entry in city["buildings"]:
        for key in ("key", "name", "col", "row", "width_fields", "depth_fields", "door"):
            if key not in entry:
                raise ValueError("Unvollstaendige Gebaeudedaten: " + key)
        if entry["door"] not in ("N", "E", "S", "W"):
            raise ValueError("Ungueltige Tuerausrichtung.")
        c, r = int(entry["col"]), int(entry["row"])
        w, d = int(entry["width_fields"]), int(entry["depth_fields"])
        if w < 1 or d < 1:
            raise ValueError("Ungueltige Gebaeudegroeße.")
        if c < 0 or r < 0 or c+w > columns or r+d > rows:
            issues.append("Ausserhalb des Rasters: " + str(entry["name"]))
        for dc in range(w):
            for dr in range(d):
                cell = (c+dc, r+dr)
                if cell in occupied:
                    issues.append("Ueberlappung: " + str(entry["name"]) + " / " + occupied[cell])
                occupied[cell] = str(entry["name"])
    city["warnings"] = list(dict.fromkeys(issues))
    if not (run / "result/rectified.jpg").is_file():
        raise ValueError("Das Kontrollbild fehlt. Bitte Erkennungsprotokoll pruefen.")
    return city


def find_exported_viewer(project: Path) -> Path | None:
    candidate = project / "cityviewer" / "CityViewer.exe"
    return candidate if candidate.is_file() else None


def viewer_command(project: Path, godot: Path, run: Path,
                   viewer_exe: Path | None = None) -> list[str]:
    current = project / "cityviewer/data/buildings.json"
    snapshot = run / "input/output/buildings.json"
    if read_json(current) != read_json(snapshot):
        raise ValueError("Der Gebaeudekatalog wurde seit der Erkennung geaendert. Bitte erneut erkennen.")
    if viewer_exe is not None:
        viewer_exe = viewer_exe.resolve()
        if not viewer_exe.is_file():
            raise ValueError("Die exportierte CityViewer.exe wurde nicht gefunden: " + str(viewer_exe))
        return [str(viewer_exe), "--", str((run / "result/city.json").resolve())]
    if not godot.is_file():
        raise ValueError("Bitte zuerst die Godot-Programmdatei auswaehlen.")
    if not (project / "cityviewer/project.godot").is_file():
        raise ValueError("cityviewer/project.godot fehlt.")
    return [str(godot.resolve()), "--path", str((project / "cityviewer").resolve()),
            "--", str((run / "result/city.json").resolve())]


def friendly_error(text: str) -> str:
    lower = text.lower()
    if "cv2" in lower and ("no module" in lower or "importerror" in lower):
        return "OpenCV fehlt oder kann nicht geladen werden. Python-Abhaengigkeiten pruefen. Details stehen im Protokoll."
    if "aruco" in lower and "attributeerror" in lower:
        return "Die installierte OpenCV-Version enthaelt keine passende ArUco-Unterstuetzung. Benoetigt wird opencv-contrib-python."
    if "eckmarker" in lower or "corner marker" in lower:
        return "Nicht alle Eckmarker erkannt. Bitte das ganze Blatt mit allen vier Eckmarkern scharf und gleichmaessig beleuchtet fotografieren.\n\n" + text[-1600:]
    return text[-2200:] or "Die Verarbeitung wurde ohne Ergebnis beendet. Bitte das Protokoll oeffnen."
