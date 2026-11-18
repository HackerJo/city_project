# -*- coding: utf-8 -*-
# Korrigiert die Argumentuebergabe an die exportierte CityViewer.exe.
# Ausfuehren im Projektstamm: python fix_exported_viewer_argument.py
# Vorher wird eine Sicherungskopie teacher_backend.py.bak_viewer_argument erstellt.
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "teacher_backend.py"

OLD = """    if viewer_exe is not None:
        viewer_exe = viewer_exe.resolve()
        if not viewer_exe.is_file():
            raise ValueError("Die exportierte CityViewer.exe wurde nicht gefunden: " + str(viewer_exe))
        return [str(viewer_exe), str((run / "result/city.json").resolve())]"""

NEW = """    if viewer_exe is not None:
        viewer_exe = viewer_exe.resolve()
        if not viewer_exe.is_file():
            raise ValueError("Die exportierte CityViewer.exe wurde nicht gefunden: " + str(viewer_exe))
        return [str(viewer_exe), "--", str((run / "result/city.json").resolve())]"""

def main() -> None:
    if not BACKEND.is_file():
        raise SystemExit("Datei fehlt: " + str(BACKEND))
    backup = BACKEND.with_suffix(BACKEND.suffix + ".bak_viewer_argument")
    if not backup.exists():
        shutil.copy2(BACKEND, backup)
        print("Sicherung erstellt: " + backup.name)
    else:
        print("Sicherung bereits vorhanden: " + backup.name)
    text = BACKEND.read_text(encoding="utf-8")
    if OLD not in text:
        if NEW in text:
            print("Die Korrektur ist bereits vorhanden. Es ist keine Aenderung noetig.")
            return
        raise SystemExit("Erwartete Zeile nicht gefunden. Bitte Sicherungskopie pruefen.")
    BACKEND.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    updated = BACKEND.read_text(encoding="utf-8")
    if NEW not in updated:
        raise SystemExit("Patch konnte nicht angewendet werden.")
    print("Patch erfolgreich angewendet.")
    print("Start jetzt mit: python teacher_app.py")
    print('Test: Demo City 03 auswaehlen und "Demo direkt in 3D" druecken.')


if __name__ == "__main__":
    main()
