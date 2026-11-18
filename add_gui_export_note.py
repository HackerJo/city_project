# -*- coding: utf-8 -*-
# Ergaenzt die Readme.Dev.md um den offiziellen Godot-GUI-Exportweg.
# Ausfuehren im Projektstamm: python add_gui_export_note.py
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent
DOC = ROOT / "Readme.Dev.md"
MARKER = "## 3. Datenquellen und erzeugte Dateien"

SECTION = """
## 2a. Offizieller Windows-Export über die Godot-GUI

Der getestete und bevorzugte Weg zur Erzeugung der eigenständigen Viewer-EXE ist der Export über die Godot-GUI. Er ist der verbindliche Buildweg, solange der PowerShell-Skript-Export nicht vollständig mit dem GUI-Export übereinstimmt.

### Ablauf

1. Godot öffnen und das Projekt `cityviewer` öffnen.
2. `Projekt` → `Export ...` wählen.
3. Das Preset `Windows Desktop 2` auswählen.
4. Im Bereich `Ressourcen` prüfen:
   - Export-Modus: `Alle Ressourcen des Projekts exportieren`
   - Filter für Nicht-Ressourcendateien: `*.json, *.csv`
5. Auf `Exportieren` klicken und als Ziel `cityviewer/CityViewer.exe` verwenden bzw. den im Preset gespeicherten Pfad beibehalten.
6. Die erzeugte Datei liegt danach unter `cityviewer/CityViewer.exe`.

### Start der exportierten EXE

Die exportierte EXE enthält das Godot-Projekt eingebettet. Sie unterstützt keinen `--path`-Parameter. Stadtdaten werden als Benutzerargument nach `--` übergeben:

```text
CityViewer.exe -- C:/Pfad/zu/city.json
```

Die Lehreroberfläche erkennt `cityviewer/CityViewer.exe` automatisch, sofern die Patches `apply_exported_viewer_patch.py` und `fix_exported_viewer_argument.py` angewendet wurden. Sie startet die EXE dann ohne Godot-Auswahl und ohne `--path`.

### PowerShell-Skript-Export

`build_viewer_windows.ps1` bleibt als optionaler Automatisierungsversuch bestehen. Im aktuellen Stand erzeugt der Skript-Export eine EXE, in der die rohe `parts.csv` fehlt, obwohl der Include-Filter gesetzt ist. Ursache ist vermutlich die Godot-interne Behandlung der importierten CSV-Datei.

Bis dieser Unterschied geklärt ist, ist der GUI-Export der verbindliche Weg. Das Skript darf nicht als Ersatz für den GUI-Export behandelt werden.

### Test

```powershell
./test_viewer_windows.ps1 -ViewerExe "./cityviewer/CityViewer.exe"
```

Der Godot-Parameter ist für den Start der exportierten EXE nicht erforderlich.

"""

def main() -> None:
    if not DOC.is_file():
        raise SystemExit("Datei fehlt: " + str(DOC))
    text = DOC.read_text(encoding="utf-8")
    if "## 2a. Offizieller Windows-Export über die Godot-GUI" in text:
        print("Der Abschnitt ist bereits vorhanden. Es ist keine Aenderung noetig.")
        return
    if MARKER not in text:
        raise SystemExit("Einfuegemarke nicht gefunden: " + MARKER)
    backup = DOC.with_suffix(DOC.suffix + ".bak_gui_export")
    if not backup.exists():
        shutil.copy2(DOC, backup)
        print("Sicherung erstellt: " + backup.name)
    updated = text.replace(MARKER, SECTION + "\n" + MARKER, 1)
    DOC.write_text(updated, encoding="utf-8")
    print("Readme.Dev.md aktualisiert.")


if __name__ == "__main__":
    main()
