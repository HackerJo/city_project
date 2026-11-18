# -*- coding: utf-8 -*-
# Bereitet die Lehrerausgabe vor: Nutzt eine mitgelieferte Stadt_Erkennung.exe,
# falls vorhanden; behaelt die Python-Entwicklungsfassung als Rueckfalloption.
# Ausfuehren im Projektstamm: python apply_bundled_detector_patch.py
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "teacher_backend.py"

OLD_PREPARE = """    detector = project / "scripts" / "detect_city.py"
    if not detector.is_file():
        raise ValueError("scripts/detect_city.py fehlt. Bitte im vollstaendigen Projekt starten.")"""

NEW_PREPARE = """    detector = project / "scripts" / "detect_city.py"
    if not detector.is_file() and find_bundled_detector(project) is None:
        raise ValueError("scripts/detect_city.py fehlt und keine Stadt_Erkennung.exe gefunden. Bitte im vollstaendigen Projekt starten.")"""

OLD_COMMAND = """def detector_command(project: Path, image: Path, run: Path) -> list[str]:
    return [sys.executable, str(project.resolve() / "scripts/detect_city.py"),
            "--image", str(image.resolve()), "--root", str(run / "input"), "--out", str(run / "result")]"""

NEW_COMMAND = """def find_bundled_detector(project: Path) -> Path | None:
    candidate = project / "Stadt_Erkennung.exe"
    return candidate if candidate.is_file() else None


def detector_command(project: Path, image: Path, run: Path) -> list[str]:
    image, run = image.resolve(), run.resolve()
    detector = find_bundled_detector(project)
    if detector is not None:
        return [str(detector),
                "--image", str(image),
                "--root", str(run / "input"),
                "--out", str(run / "result")]
    return [sys.executable, str(project.resolve() / "scripts/detect_city.py"),
            "--image", str(image),
            "--root", str(run / "input"),
            "--out", str(run / "result")]"""

def replace_exact(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            print("Bereits vorhanden: " + label)
            return
        raise SystemExit("Erwarteter Text nicht gefunden: " + label)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

def main() -> None:
    if not BACKEND.is_file():
        raise SystemExit("Datei fehlt: " + str(BACKEND))
    backup = BACKEND.with_suffix(BACKEND.suffix + ".bak_bundled_detector")
    if not backup.exists():
        shutil.copy2(BACKEND, backup)
        print("Sicherung erstellt: " + backup.name)
    replace_exact(BACKEND, OLD_PREPARE, NEW_PREPARE, "prepare_run in teacher_backend.py")
    replace_exact(BACKEND, OLD_COMMAND, NEW_COMMAND, "detector_command in teacher_backend.py")
    text = BACKEND.read_text(encoding="utf-8")
    checks = (
        "def find_bundled_detector" in text,
        "find_bundled_detector(project) is None" in text,
        "Stadt_Erkennung.exe" in text,
    )
    if not all(checks):
        raise SystemExit("Patch unvollstaendig. Bitte Sicherungskopie pruefen.")
    print("Patch erfolgreich angewendet.")
    print("Die Entwicklungsfassung funktioniert weiterhin mit Python.")
    print("Fuer die Lehrerausgabe wird spaeter eine Stadt_Erkennung.exe neben Lehrer_Stadt.exe erwartet.")


if __name__ == "__main__":
    main()
