"""Read-only check of shipped demo sources; temporary copies are removed afterwards."""
from pathlib import Path
import tempfile
from PIL import Image
from teacher_demo import load_demos, prepare_demo_run, check_demo_result


def main():
    project = Path(__file__).resolve().parent
    demos, errors = load_demos(project)
    failures = len(errors)
    for error in errors:
        print("FEHLER:", error)
    if not demos and not errors:
        print("Keine Demos eingetragen.")
        return 1
    with tempfile.TemporaryDirectory(prefix="city_demo_check_") as temp:
        for demo in demos:
            try:
                with Image.open(demo["photo"]) as image:
                    image.verify()
                run = prepare_demo_run(project, demo, True, Path(temp))
                city = check_demo_result(run)
                print("OK:", demo["title"], "|", len(city["buildings"]), "Gebaeude |", len(city.get("warnings", [])), "Warnungen")
            except Exception as exc:
                failures += 1
                print("FEHLER:", demo["title"], "|", exc)
    print("Keine Beispieldateien geaendert; keine Erkennung und kein Godot gestartet.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
