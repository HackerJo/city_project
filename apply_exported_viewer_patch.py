# -*- coding: utf-8 -*-
# Aktiviert die exportierte CityViewer.exe in der Lehreroberflaeche.
# Ausfuehren im Projektstamm: python apply_exported_viewer_patch.py
# Es werden Sicherungskopien mit der Endung .bak_exported_viewer erstellt.
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "teacher_backend.py"
APP = ROOT / "teacher_app.py"

BACKEND_OLD_VIEWER = """def viewer_command(project: Path, godot: Path, run: Path) -> list[str]:
    if not godot.is_file():
        raise ValueError("Bitte zuerst die Godot-Programmdatei auswaehlen.")
    if not (project / "cityviewer/project.godot").is_file():
        raise ValueError("cityviewer/project.godot fehlt.")
    current = project / "cityviewer/data/buildings.json"
    snapshot = run / "input/output/buildings.json"
    if read_json(current) != read_json(snapshot):
        raise ValueError("Der Gebaeudekatalog wurde seit der Erkennung geaendert. Bitte erneut erkennen.")
    return [str(godot.resolve()), "--path", str((project / "cityviewer").resolve()),
            "--", str((run / "result/city.json").resolve())]
"""

BACKEND_NEW_VIEWER = """def find_exported_viewer(project: Path) -> Path | None:
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
        return [str(viewer_exe), str((run / "result/city.json").resolve())]
    if not godot.is_file():
        raise ValueError("Bitte zuerst die Godot-Programmdatei auswaehlen.")
    if not (project / "cityviewer/project.godot").is_file():
        raise ValueError("cityviewer/project.godot fehlt.")
    return [str(godot.resolve()), "--path", str((project / "cityviewer").resolve()),
            "--", str((run / "result/city.json").resolve())]
"""

APP_IMPORT_OLD = """from teacher_backend import (VERSION, data_home, read_json, prepare_run, detector_command,
                             validate_result, viewer_command, friendly_error)"""

APP_IMPORT_NEW = """from teacher_backend import (VERSION, data_home, read_json, prepare_run, detector_command,
                             validate_result, viewer_command, find_exported_viewer, friendly_error)"""

APP_DETECT_OLD = """        self.godot_path = None
        try:
            value = read_json(self.config_path).get("godot", "")
            if value:
                self.godot_path = Path(value)
        except (OSError, ValueError, AttributeError):
            pass
        if self.godot_path is None:
            found = shutil.which("godot") or shutil.which("godot4")
            candidates = sorted(PROJECT.glob("Godot*.exe"))
            if found:
                self.godot_path = Path(found)
            elif candidates:
                self.godot_path = next((p for p in candidates if "console" not in p.name.lower()), candidates[0])
"""

APP_DETECT_NEW = """        self.godot_path = None
        try:
            value = read_json(self.config_path).get("godot", "")
            if value:
                self.godot_path = Path(value)
        except (OSError, ValueError, AttributeError):
            pass
        if self.godot_path is None:
            found = shutil.which("godot") or shutil.which("godot4")
            candidates = sorted(PROJECT.glob("Godot*.exe"))
            if found:
                self.godot_path = Path(found)
            elif candidates:
                self.godot_path = next((p for p in candidates if "console" not in p.name.lower()), candidates[0])
        self.viewer_exe = find_exported_viewer(PROJECT)
"""

APP_LAUNCH_OLD = """        if not self.godot_path or not self.godot_path.is_file():
            self.choose_godot()
            if not self.godot_path or not self.godot_path.is_file():
                return
"""

APP_LAUNCH_NEW = """        if self.viewer_exe is None:
            if not self.godot_path or not self.godot_path.is_file():
                self.choose_godot()
                if not self.godot_path or not self.godot_path.is_file():
                    return
"""

APP_COMMAND_OLD = """            cmd = viewer_command(PROJECT, self.godot_path, self.run_dir)"""

APP_COMMAND_NEW = """            cmd = viewer_command(PROJECT, self.godot_path, self.run_dir, self.viewer_exe)"""

APP_HELP_OLD = "Godot einmal ueber 'Godot auswaehlen' einrichten."

APP_HELP_NEW = "Bei vorhandener exportierter CityViewer.exe wird diese automatisch verwendet; sonst Godot ueber 'Godot auswaehlen' einrichten."

def replace_exact(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit("Erwarteter Text nicht gefunden: " + label + "\nDatei: " + str(path))
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

def main() -> None:
    for path in (BACKEND, APP):
        if not path.is_file():
            raise SystemExit("Datei fehlt: " + str(path))
        backup = path.with_suffix(path.suffix + ".bak_exported_viewer")
        if not backup.exists():
            shutil.copy2(path, backup)
            print("Sicherung erstellt: " + backup.name)
        else:
            print("Sicherung bereits vorhanden: " + backup.name)

    replace_exact(BACKEND, BACKEND_OLD_VIEWER, BACKEND_NEW_VIEWER, "viewer_command in teacher_backend.py")
    replace_exact(APP, APP_IMPORT_OLD, APP_IMPORT_NEW, "Import in teacher_app.py")
    replace_exact(APP, APP_DETECT_OLD, APP_DETECT_NEW, "Viewer-Erkennung in teacher_app.py")
    replace_exact(APP, APP_LAUNCH_OLD, APP_LAUNCH_NEW, "Godot-Pruefung in teacher_app.py")
    replace_exact(APP, APP_COMMAND_OLD, APP_COMMAND_NEW, "Viewer-Befehl in teacher_app.py")
    replace_exact(APP, APP_HELP_OLD, APP_HELP_NEW, "Hilfetext in teacher_app.py")

    backend = BACKEND.read_text(encoding="utf-8")
    app = APP.read_text(encoding="utf-8")
    checks = (
        "def find_exported_viewer" in backend,
        "viewer_exe: Path | None = None" in backend,
        "find_exported_viewer" in app,
        "self.viewer_exe = find_exported_viewer(PROJECT)" in app,
        "viewer_command(PROJECT, self.godot_path, self.run_dir, self.viewer_exe)" in app,
    )
    if not all(checks):
        raise SystemExit("Patch unvollstaendig. Bitte die Sicherungskopien pruefen.")

    print("Patch erfolgreich angewendet.")
    print("Start jetzt mit: python teacher_app.py")
    print("Die Oberflaeche verwendet automatisch cityviewer/CityViewer.exe, sofern vorhanden.")


if __name__ == "__main__":
    main()
