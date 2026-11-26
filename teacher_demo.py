"""Offline demo sessions. Examples are read-only; processing uses separate run folders."""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
import json
import shutil
import uuid
from teacher_backend import (
    read_json,
    data_home,
    validate_result,
    find_bundled_detector,
)

DEMO_VERSION = "0.3.0-dev"
REQUIRED = ("buildings.json", "city.json", "control.jpg", "layout.json", "rectified_raw.jpg", "rectified.jpg")


def inside(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("Demo-Pfad muss relativ sein.")
    root = root.resolve()
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise ValueError("Demo-Pfad verlaesst den Beispielordner.") from None
    return path


def load_demos(project: Path) -> tuple[list[dict], list[str]]:
    root = (project / "examples").resolve()
    manifest = root / "demos.json"
    if not manifest.is_file():
        return [], ["examples/demos.json fehlt."]
    try:
        data = read_json(manifest)
        if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("demos"), list):
            raise ValueError("Ungueltige Demo-Liste (schema_version: 1 erforderlich).")
    except (OSError, ValueError, TypeError) as exc:
        return [], [str(exc)]
    demos, errors, ids = [], [], set()
    for entry in data["demos"]:
        try:
            if not isinstance(entry, dict):
                raise ValueError("Demo-Eintrag ist kein Objekt.")
            ident = entry.get("id")
            if not isinstance(ident, str) or not ident or ident in ids:
                raise ValueError("Demo-ID fehlt oder ist doppelt.")
            ids.add(ident)
            title = entry.get("title")
            if not isinstance(title, str) or not title.strip():
                raise ValueError("Demo-Titel fehlt.")
            folder = inside(root, entry["folder"])
            photo = inside(folder, entry["photo"])
            for file in [photo] + [folder / name for name in REQUIRED]:
                if not file.is_file():
                    raise ValueError("Demo-Datei fehlt: " + str(file))
                inside(root, file.relative_to(root).as_posix())
            demos.append({"id": ident, "title": title, "folder": folder, "photo": photo,
                          "description": str(entry.get("description", ""))})
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
    return demos, errors


def check_inputs(layout: dict, catalog: dict) -> None:
    if not isinstance(layout, dict) or not isinstance(catalog, dict):
        raise ValueError("Demo-Layout oder Katalog ist kein JSON-Objekt.")
    for key in ("paper_mm", "field_mm", "columns", "rows", "grid_origin_mm", "aruco_dict", "corner_markers_mm"):
        if key not in layout:
            raise ValueError("Demo-Layout: Feld fehlt: " + key)
    if int(layout["columns"]) < 1 or int(layout["rows"]) < 1 or float(layout["field_mm"]) <= 0:
        raise ValueError("Ungueltige Rastergroesse im Demo-Layout.")
    buildings = catalog.get("buildings")
    if not isinstance(buildings, list) or not buildings:
        raise ValueError("Demo-Katalog ist leer oder ungueltig.")
    ids, keys = set(), set()
    for b in buildings:
        ident, key = int(b["id"]), str(b["key"])
        if ident in ids or key in keys:
            raise ValueError("Doppelte ID oder Schluessel im Demo-Katalog.")
        ids.add(ident)
        keys.add(key)
        if int(b["width"]) < 1 or int(b["depth"]) < 1:
            raise ValueError("Ungueltige Grundflaeche im Demo-Katalog.")


def check_viewer_catalog(project: Path, catalog: dict) -> None:
    current = project / "cityviewer/data/buildings.json"
    if not current.is_file():
        raise ValueError("cityviewer/data/buildings.json fehlt.")
    if read_json(current) != catalog:
        raise ValueError("Der Demo-Katalog unterscheidet sich vom aktuellen Viewer-Katalog. "
                         "Die Demo kann angesehen und neu erkannt werden, aber nicht mit diesem Katalog in 3D starten. "
                         "Bitte Katalogstaende pruefen; es wurde nichts ueberschrieben.")


def check_demo_result(run: Path) -> dict:
    city = validate_result(run)
    layout = read_json(run / "input/output/layout.json")
    catalog = read_json(run / "input/output/buildings.json")
    if (int(city["grid"]["columns"]), int(city["grid"]["rows"])) != (int(layout["columns"]), int(layout["rows"])):
        raise ValueError("Demo-Stadt und Layout haben unterschiedliche Rastergroessen.")
    by_key = {str(b["key"]): b for b in catalog["buildings"]}
    for e in city["buildings"]:
        b = by_key.get(str(e["key"]))
        if b is None:
            raise ValueError("Unbekanntes Gebaeude in Demo-Stadt: " + str(e["key"]))
        if "id" in e and int(e["id"]) != int(b["id"]):
            raise ValueError("Gebaeude-ID passt nicht zum Demo-Katalog: " + str(e["key"]))
        size = (int(b["width"]), int(b["depth"]))
        if e["door"] in ("E", "W"):
            size = size[::-1]
        if size != (int(e["width_fields"]), int(e["depth_fields"])):
            raise ValueError("Gebaeudegrundflaeche passt nicht zum Demo-Katalog: " + str(e["key"]))
    return city


def prepare_demo_run(project: Path, demo: dict, prepared: bool, work_home: Path | None = None) -> Path:
    project = project.resolve()
    examples = project / "examples"
    folder = demo["folder"].resolve()
    inside(examples, folder.relative_to(examples.resolve()).as_posix())
    photo = demo["photo"].resolve()
    inside(folder, photo.relative_to(folder).as_posix())
    if not photo.is_file():
        raise ValueError("Das Demo-Foto fehlt.")
    layout, catalog = read_json(folder / "layout.json"), read_json(folder / "buildings.json")
    check_inputs(layout, catalog)
    if prepared:
        pass  # CITYPROJECT_RUN_CATALOG_V1: the demo is shown with its own catalogue
    elif not (project / "scripts" / "detect_city.py").is_file() and find_bundled_detector(project) is None:
        raise ValueError("Weder scripts/detect_city.py noch Stadt_Erkennung.exe gefunden.")
    parent = work_home if work_home is not None else data_home()
    run = parent / "runs" / (datetime.now().strftime("%Y%m%d_%H%M%S") + "_demo_" + uuid.uuid4().hex[:6])
    (run / "input/output").mkdir(parents=True)
    (run / "result").mkdir()
    for name, value in (("layout.json", layout), ("buildings.json", catalog)):
        (run / "input/output" / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    metadata = {"version": DEMO_VERSION, "project": str(project), "demo_id": demo["id"],
                "image": str(photo), "demo_folder": str(folder),
                "mode": "prepared_demo" if prepared else "demo_recognition"}
    (run / "session.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (run / "detect.log").write_text("Demo: " + demo["title"] + "\n" +
        ("Vorbereitete Ergebnisse kopiert. KEINE neue Erkennung ausgefuehrt.\n" if prepared else "Neue Erkennung des Demo-Fotos.\n"), encoding="utf-8")
    if prepared:
        # Only write into the new session; never into examples/ or the viewer catalogue.
        city = read_json(folder / "city.json")
        (run / "result/city.json").write_text(json.dumps(city, ensure_ascii=False, indent=2), encoding="utf-8")
        from PIL import Image
        for name in ("control.jpg", "rectified_raw.jpg", "rectified.jpg"):
            source = inside(folder, name)
            with Image.open(source) as img:
                img.verify()
            shutil.copy2(source, run / "result" / name)
        check_demo_result(run)
    return run
